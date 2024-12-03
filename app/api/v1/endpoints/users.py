from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta
from app.core.config import get_settings
from app.core.security import create_access_token, validate_password
from app.db.base import get_db
from app.db.models import User, UserRole
from app.services.user_service import UserService
from pydantic import BaseModel, EmailStr
from fastapi_limiter.depends import RateLimiter

settings = get_settings()
router = APIRouter()

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.CLIENT
    whmcs_client_id: int = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: UserRole
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    _: str = Depends(RateLimiter(times=5, minutes=5))  # 5次/5分钟的限制
):
    user = await UserService.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=400,
            detail="Inactive user"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id,
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/users", response_model=UserResponse)
async def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user, scopes=["admin"])
):
    if not validate_password(user_in.password):
        raise HTTPException(
            status_code=400,
            detail="Password does not meet security requirements"
        )
    
    user = await UserService.create_user(
        db=db,
        username=user_in.username,
        email=user_in.email,
        password=user_in.password,
        role=user_in.role,
        whmcs_client_id=user_in.whmcs_client_id
    )
    return user

@router.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/users/{user_id}", response_model=UserResponse)
async def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user, scopes=["admin"])
):
    user = await UserService.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user, scopes=["admin"])
):
    if user_update.password and not validate_password(user_update.password):
        raise HTTPException(
            status_code=400,
            detail="Password does not meet security requirements"
        )
    
    user = await UserService.update_user(
        db=db,
        user_id=user_id,
        username=user_update.username,
        email=user_update.email,
        password=user_update.password if user_update.password else None,
        role=user_update.role
    )
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user, scopes=["admin"])
):
    success = await UserService.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": "success"}
