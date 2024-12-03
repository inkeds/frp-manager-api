from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Boolean, Index
from datetime import datetime
import enum
from .base import Base

class UserRole(enum.Enum):
    ADMIN = "admin"
    RESELLER = "reseller"
    CLIENT = "client"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(Enum(UserRole))
    whmcs_client_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    
    # 关系
    orders = relationship("Order", back_populates="user")
    
    # 索引
    __table_args__ = (
        Index('idx_user_email_username', 'email', 'username'),
        Index('idx_user_role_active', 'role', 'is_active'),
    )

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    price = Column(Float)
    whmcs_product_id = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    orders = relationship("Order", back_populates="product")
    
    # 索引
    __table_args__ = (
        Index('idx_product_active', 'is_active'),
        Index('idx_product_whmcs', 'whmcs_product_id'),
    )

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    whmcs_order_id = Column(Integer, nullable=True)
    amount = Column(Float)
    status = Column(String)  # pending, active, suspended, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    last_renewed_at = Column(DateTime, nullable=True)
    
    # 关系
    user = relationship("User", back_populates="orders")
    product = relationship("Product", back_populates="orders")
    
    # 索引
    __table_args__ = (
        Index('idx_order_user', 'user_id'),
        Index('idx_order_status', 'status'),
        Index('idx_order_dates', 'created_at', 'expires_at'),
    )
