from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.security import verify_password, create_access_token
from app.models.core import User
from app.models.enums import UserStatus
from app.schemas.auth import Token, UserOut
from app.services.audit import log_action

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


def _display_name(user: User) -> str:
    if user.employee:
        return f"{user.employee.first_name} {user.employee.last_name}"
    if user.customer:
        return f"{user.customer.first_name} {user.customer.last_name}"
    return user.username


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(status_code=403, detail="Your account is not active. Contact an administrator.")

    user.last_login = datetime.utcnow()
    log_action(db, user, "login", details=f"role={user.role.value}")
    db.commit()

    access_token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
    return Token(
        access_token=access_token,
        role=user.role,
        username=user.username,
        display_name=_display_name(user),
    )


@router.get("/me", response_model=UserOut)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user
