from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
import json

from models import Base, User, Product, Order, UserRole
from database import engine, get_db
from whmcs import WHMCSClient

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(title="FRP Management API")

# 安全配置
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WHMCS客户端
whmcs_client = WHMCSClient()

# 辅助函数
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

# API路由
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/")
async def create_user(
    username: str,
    password: str,
    email: str,
    role: UserRole,
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user, scopes=["admin"])
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db_user = User(
        username=username,
        email=email,
        hashed_password=get_password_hash(password),
        role=role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/products/")
async def list_products(db: Session = Depends(get_db)):
    return db.query(Product).filter(Product.is_active == True).all()

@app.post("/orders/")
async def create_order(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # 创建WHMCS订单
    whmcs_response = await whmcs_client.create_order(
        client_id=current_user.whmcs_client_id,
        product_id=product.whmcs_product_id
    )
    
    if whmcs_response.get("result") != "success":
        raise HTTPException(status_code=400, detail="Failed to create WHMCS order")
    
    order = Order(
        user_id=current_user.id,
        product_id=product_id,
        whmcs_order_id=whmcs_response.get("orderid"),
        amount=product.price,
        status="pending"
    )
    
    db.add(order)
    db.commit()
    db.refresh(order)
    return order

@app.get("/orders/")
async def list_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == UserRole.ADMIN:
        return db.query(Order).all()
    return db.query(Order).filter(Order.user_id == current_user.id).all()

@app.get("/orders/{order_id}")
async def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if current_user.role != UserRole.ADMIN and order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return order

@app.put("/orders/{order_id}/status")
async def update_order_status(
    order_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user, scopes=["admin"])
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.status = status
    db.commit()
    return order

# FRP配置相关路由
@app.get("/configs")
async def list_configs(current_user: User = Depends(get_current_user)):
    configs = []
    try:
        for filename in os.listdir(CONFIG_DIR):
            if filename.endswith('.json'):
                with open(os.path.join(CONFIG_DIR, filename), 'r') as f:
                    config = json.load(f)
                    configs.append(config)
        return configs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/configs/{name}")
async def get_config(
    name: str,
    current_user: User = Depends(get_current_user)
):
    try:
        with open(os.path.join(CONFIG_DIR, f"{name}.json"), 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Config not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/configs")
async def create_config(
    config: dict,
    current_user: User = Security(get_current_user, scopes=["admin"])
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        config_path = os.path.join(CONFIG_DIR, f"{config['name']}.json")
        if os.path.exists(config_path):
            raise HTTPException(status_code=400, detail="Config already exists")
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        return config
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
