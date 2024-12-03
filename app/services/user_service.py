from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db.models import User, UserRole
from app.core.security import get_password_hash, verify_password
from fastapi import HTTPException

class UserService:
    @staticmethod
    async def create_user(
        db: Session,
        username: str,
        email: str,
        password: str,
        role: UserRole,
        whmcs_client_id: Optional[int] = None
    ) -> User:
        try:
            hashed_password = get_password_hash(password)
            user = User(
                username=username,
                email=email,
                hashed_password=hashed_password,
                role=role,
                whmcs_client_id=whmcs_client_id
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail="Username or email already exists"
            )

    @staticmethod
    async def authenticate_user(
        db: Session,
        username: str,
        password: str
    ) -> Optional[User]:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            # 增加失败登录计数
            user.failed_login_attempts += 1
            db.commit()
            return None
        
        # 登录成功，重置失败计数并更新最后登录时间
        user.failed_login_attempts = 0
        user.last_login = datetime.utcnow()
        db.commit()
        return user

    @staticmethod
    async def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    async def get_user_by_username(db: Session, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    async def update_user(
        db: Session,
        user_id: int,
        **kwargs
    ) -> Optional[User]:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        for key, value in kwargs.items():
            if hasattr(user, key):
                if key == "password":
                    value = get_password_hash(value)
                setattr(user, key, value)
        
        try:
            db.commit()
            db.refresh(user)
            return user
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail="Update failed due to constraint violation"
            )

    @staticmethod
    async def delete_user(db: Session, user_id: int) -> bool:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        try:
            db.delete(user)
            db.commit()
            return True
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail="Cannot delete user due to existing dependencies"
            )
