from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel
import secrets

# 資料庫配置
# DATABASE_URL = (
#     "mssql+pyodbc://username:password@server/database"
#     "?driver=ODBC+Driver+17+for+SQL+Server"
# )

# 使用 SQLite 進行開發
DATABASE_URL = "sqlite:///./shopping_cart.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 導入密碼處理
from passlib.context import CryptContext

# 密碼加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 資料庫模型
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 關聯
    cart_items = relationship("CartItem", back_populates="user")

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    image_url = Column(String(200))
    category = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 關聯
    cart_items = relationship("CartItem", back_populates="product")

class CartItem(Base):
    __tablename__ = "cart_items"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 關聯
    user = relationship("User", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")

# 建立資料表
Base.metadata.create_all(bind=engine)

app = FastAPI(title="購物車系統", version="1.0.0")

# 配置 Session 中間件
app.add_middleware(SessionMiddleware, secret_key=secrets.token_urlsafe(32))

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 輔助函數
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def get_current_user(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登入"
        )
    
    # 獲取資料庫會話
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用戶不存在"
            )
        return user
    finally:
        db.close()

# Pydantic 模型
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    image_url: Optional[str] = None
    category: Optional[str] = None

class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    stock: int
    image_url: Optional[str]
    category: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = 1

class CartItemResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int
    created_at: datetime
    product: ProductResponse

    class Config:
        from_attributes = True

# 資料庫依賴
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



# 初始化測試資料
def init_test_data(db: Session):
    # 檢查是否已有資料
    if db.query(Product).first():
        return
    
    # 建立測試商品
    test_products = [
        Product(name="iPhone 15", description="最新款iPhone，配備強大的A17 Pro晶片", price=35900, stock=10, category="手機", 
                image_url="https://picsum.photos/250/200?random=1"),
        Product(name="MacBook Pro", description="高效能筆記型電腦，適合專業工作", price=89900, stock=5, category="電腦",
                image_url="https://picsum.photos/250/200?random=2"),
        Product(name="AirPods Pro", description="主動降噪耳機，絕佳音質體驗", price=7490, stock=20, category="耳機",
                image_url="https://picsum.photos/250/200?random=3"),
        Product(name="iPad Air", description="輕薄平板電腦，工作娛樂兩相宜", price=21900, stock=15, category="平板",
                image_url="https://picsum.photos/250/200?random=4"),
        Product(name="Apple Watch", description="智慧手錶，健康生活好夥伴", price=12900, stock=8, category="穿戴裝置",
                image_url="https://picsum.photos/250/200?random=5"),
    ]
    
    for product in test_products:
        db.add(product)
    
    # 建立測試用戶
    test_user = User(
        username="testuser", 
        email="test@example.com",
        hashed_password=get_password_hash("123456")
    )
    db.add(test_user)
    
    db.commit()

# 應用啟動時初始化測試資料
@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    try:
        init_test_data(db)
    finally:
        db.close()

# API 路由
@app.get("/api/products", response_model=List[ProductResponse])
async def get_products(db: Session = Depends(get_db)):
    products = db.query(Product).filter(Product.is_active == True).all()
    return products

@app.get("/api/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id, Product.is_active == True).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    return product

@app.post("/api/products", response_model=ProductResponse)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.get("/api/users", response_model=List[UserResponse])
async def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

# 認證路由
@app.post("/api/register", response_model=UserResponse)
async def register(user: UserCreate, request: Request, db: Session = Depends(get_db)):
    # 檢查用戶名是否已存在
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="用戶名已存在")
    
    # 檢查郵箱是否已存在
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="郵箱已存在")
    
    # 創建新用戶
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # 設置 Session
    request.session["user_id"] = db_user.id
    request.session["username"] = db_user.username
    
    return db_user

@app.post("/api/login", response_model=UserResponse)
async def login(user_data: UserLogin, request: Request, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用戶名或密碼錯誤"
        )
    
    # 設置 Session
    request.session["user_id"] = user.id
    request.session["username"] = user.username
    
    return user

@app.post("/api/logout")
async def logout(request: Request):
    request.session.clear()
    return {"message": "登出成功"}

@app.get("/api/me", response_model=UserResponse)
async def read_users_me(request: Request):
    current_user = get_current_user(request)
    return current_user

@app.post("/api/users", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # 檢查用戶名是否已存在
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="用戶名已存在")
    
    # 檢查郵箱是否已存在
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="郵箱已存在")
    
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/api/cart", response_model=List[CartItemResponse])
async def get_cart(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request)
    cart_items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    return cart_items

@app.post("/api/cart", response_model=CartItemResponse)
async def add_to_cart(cart_item: CartItemCreate, request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request)
    
    # 檢查商品是否存在
    product = db.query(Product).filter(Product.id == cart_item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    
    # 檢查庫存
    if product.stock < cart_item.quantity:
        raise HTTPException(status_code=400, detail="庫存不足")
    
    # 檢查是否已經在購物車中
    existing_item = db.query(CartItem).filter(
        CartItem.user_id == current_user.id,
        CartItem.product_id == cart_item.product_id
    ).first()
    
    if existing_item:
        # 更新數量
        existing_item.quantity += cart_item.quantity
        db.commit()
        db.refresh(existing_item)
        return existing_item
    else:
        # 新增購物車項目
        db_cart_item = CartItem(
            user_id=current_user.id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity
        )
        db.add(db_cart_item)
        db.commit()
        db.refresh(db_cart_item)
        return db_cart_item

@app.put("/api/cart/{cart_item_id}")
async def update_cart_item(cart_item_id: int, quantity: int, request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request)
    
    cart_item = db.query(CartItem).filter(
        CartItem.id == cart_item_id,
        CartItem.user_id == current_user.id
    ).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="購物車項目不存在")
    
    cart_item.quantity = quantity
    db.commit()
    return {"message": "更新成功"}

@app.delete("/api/cart/{cart_item_id}")
async def remove_from_cart(cart_item_id: int, request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request)
    
    cart_item = db.query(CartItem).filter(
        CartItem.id == cart_item_id,
        CartItem.user_id == current_user.id
    ).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="購物車項目不存在")
    
    db.delete(cart_item)
    db.commit()
    return {"message": "移除成功"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 