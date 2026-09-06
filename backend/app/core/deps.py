from typing import Iterable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.core import User
from app.models.enums import UserRole, UserStatus

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(status_code=403, detail="Account is not active")
    return user


def require_roles(*roles: Iterable[UserRole]):
    """Dependency factory: restrict an endpoint to a set of roles.
    Admin is always implicitly allowed since it has full system access.
    """
    allowed = set(roles)
    allowed.add(UserRole.ADMIN)

    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )
        return current_user

    return dependency


# Convenience role groups per the requirement doc's Role-Based Access Control table
require_admin = require_roles(UserRole.ADMIN)
require_management = require_roles(UserRole.ADMIN, UserRole.GENERAL_MANAGER, UserRole.MANAGER)
require_billing = require_roles(UserRole.BILLING_PERSON, UserRole.MANAGER, UserRole.GENERAL_MANAGER)
require_room_staff = require_roles(UserRole.ROOM_SERVANT, UserRole.MANAGER)
require_food_staff = require_roles(UserRole.FOOD_SERVANT, UserRole.MANAGER)
require_kitchen_staff = require_roles(UserRole.CHEF, UserRole.MANAGER)
require_reports_access = require_roles(UserRole.ADMIN, UserRole.GENERAL_MANAGER)
require_staff_any = require_roles(
    UserRole.GENERAL_MANAGER, UserRole.MANAGER, UserRole.BILLING_PERSON,
    UserRole.ROOM_SERVANT, UserRole.FOOD_SERVANT, UserRole.CHEF,
)
