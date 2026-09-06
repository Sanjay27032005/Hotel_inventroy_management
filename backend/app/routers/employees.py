from datetime import date, datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_admin, require_management
from app.core.security import hash_password
from app.models.core import Employee, Department, User
from app.models.enums import UserRole, UserStatus
from app.services.codes import generate_employee_code
from app.services.audit import log_action

router = APIRouter(prefix="/api/employees", tags=["Employees"])

# Roles a Manager (rather than only Admin) is allowed to create/manage directly (Section 54)
MANAGER_CREATABLE_ROLES = {
    UserRole.BILLING_PERSON, UserRole.ROOM_SERVANT, UserRole.FOOD_SERVANT, UserRole.CHEF,
}


class DepartmentOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class DepartmentCreate(BaseModel):
    name: str
    description: Optional[str] = None


class EmployeeCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    role: UserRole
    department_id: Optional[int] = None
    manager_id: Optional[int] = None
    hire_date: Optional[date] = None
    # Optional: create the login account in the same call
    create_login: bool = False
    username: Optional[str] = None
    password: Optional[str] = None


class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    department_id: Optional[int] = None
    manager_id: Optional[int] = None
    status: Optional[UserStatus] = None


class EmployeeOut(BaseModel):
    id: int
    employee_code: str
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    role: UserRole
    department_id: Optional[int] = None
    manager_id: Optional[int] = None
    hire_date: date
    status: UserStatus
    has_login: bool = False

    class Config:
        from_attributes = True


def _guard_role_creation(current_user: User, target_role: UserRole):
    if current_user.role == UserRole.ADMIN:
        return
    if current_user.role == UserRole.MANAGER and target_role in MANAGER_CREATABLE_ROLES:
        return
    raise HTTPException(status_code=403, detail="You are not permitted to create an employee with this role")


@router.get("/departments", response_model=List[DepartmentOut])
def list_departments(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Department).all()


@router.post("/departments", response_model=DepartmentOut)
def create_department(payload: DepartmentCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    if db.query(Department).filter(Department.name == payload.name).first():
        raise HTTPException(status_code=400, detail="Department already exists")
    dept = Department(**payload.model_dump())
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept


@router.get("", response_model=List[EmployeeOut])
def list_employees(
    role: Optional[UserRole] = None,
    department_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _=Depends(require_management),
):
    query = db.query(Employee)
    if role:
        query = query.filter(Employee.role == role)
    if department_id:
        query = query.filter(Employee.department_id == department_id)
    employees = query.order_by(Employee.id.desc()).all()
    results = []
    for emp in employees:
        out = EmployeeOut.model_validate(emp)
        out.has_login = emp.user_account is not None
        results.append(out)
    return results


@router.get("/{employee_id}", response_model=EmployeeOut)
def get_employee(employee_id: int, db: Session = Depends(get_db), _=Depends(require_management)):
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    out = EmployeeOut.model_validate(emp)
    out.has_login = emp.user_account is not None
    return out


@router.post("", response_model=EmployeeOut)
def create_employee(
    payload: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _guard_role_creation(current_user, payload.role)

    if db.query(Employee).filter(Employee.email == payload.email).first():
        raise HTTPException(status_code=400, detail="An employee with this email already exists")

    emp = Employee(
        employee_code=generate_employee_code(db),
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        phone=payload.phone,
        role=payload.role,
        department_id=payload.department_id,
        manager_id=payload.manager_id,
        hire_date=payload.hire_date or date.today(),
        status=UserStatus.ACTIVE,
    )
    db.add(emp)
    db.flush()

    if payload.create_login:
        if not payload.username or not payload.password:
            raise HTTPException(status_code=400, detail="username and password are required to create a login")
        if db.query(User).filter(User.username == payload.username).first():
            raise HTTPException(status_code=400, detail="Username already taken")
        user = User(
            username=payload.username,
            hashed_password=hash_password(payload.password),
            role=payload.role,
            employee_id=emp.id,
            status=UserStatus.ACTIVE,
        )
        db.add(user)

    log_action(db, current_user, "employee_created", details=f"employee={emp.employee_code} role={emp.role.value}")
    db.commit()
    db.refresh(emp)
    out = EmployeeOut.model_validate(emp)
    out.has_login = payload.create_login
    return out


@router.post("/{employee_id}/create-account", response_model=dict)
def create_login_for_employee(
    employee_id: int,
    username: str,
    password: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    _guard_role_creation(current_user, emp.role)
    if emp.user_account:
        raise HTTPException(status_code=400, detail="This employee already has a login account")
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    user = User(
        username=username,
        hashed_password=hash_password(password),
        role=emp.role,
        employee_id=emp.id,
        status=UserStatus.ACTIVE,
    )
    db.add(user)
    log_action(db, current_user, "employee_login_created", details=f"employee={emp.employee_code}")
    db.commit()
    return {"detail": "Login account created", "username": username}


@router.put("/{employee_id}", response_model=EmployeeOut)
def update_employee(
    employee_id: int, payload: EmployeeUpdate, db: Session = Depends(get_db), _=Depends(require_management)
):
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(emp, field, value)
        if field == "status" and emp.user_account:
            emp.user_account.status = value
    db.commit()
    db.refresh(emp)
    out = EmployeeOut.model_validate(emp)
    out.has_login = emp.user_account is not None
    return out


@router.delete("/{employee_id}")
def deactivate_employee(employee_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    emp.status = UserStatus.INACTIVE
    if emp.user_account:
        emp.user_account.status = UserStatus.INACTIVE
    log_action(db, current_user, "employee_deactivated", details=f"employee={emp.employee_code}")
    db.commit()
    return {"detail": "Employee deactivated"}
