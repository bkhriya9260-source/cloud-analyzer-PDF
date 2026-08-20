from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from config import settings

engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- 1. User & Auth Data ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user") # user, admin
    created_at = Column(DateTime, default=datetime.utcnow)
    
    subscription = relationship("UserSubscription", back_populates="user", uselist=False)
    searches = relationship("SearchHistory", back_populates="user")
    monitored_items = relationship("Monitoring", back_populates="user")

# --- 2. Store & Competitor Data ---
class Store(Base):
    __tablename__ = "stores"
    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    platform = Column(String, default="Shopify")
    niche = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    products = relationship("Product", back_populates="store")

# --- 3. Product Catalog Data ---
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"))
    title = Column(String, index=True, nullable=False)
    url = Column(Text, nullable=False)
    image_url = Column(Text, nullable=True)
    selling_price = Column(Float, default=0.0)
    cogs = Column(Float, default=0.0)
    is_best_seller = Column(Boolean, default=False)
    first_seen = Column(DateTime, default=datetime.utcnow)

    store = relationship("Store", back_populates="products")
    price_history = relationship("PriceHistory", back_populates="product")
    ad_history = relationship("AdHistory", back_populates="product")

# --- 4. Price & Trend History ---
class PriceHistory(Base):
    __tablename__ = "price_history"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    price = Column(Float, nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="price_history")

# --- 5. Ad History Data ---
class AdHistory(Base):
    __tablename__ = "ad_history"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    platform = Column(String, nullable=False) # Meta, TikTok, Google
    ad_id = Column(String, nullable=True)
    ad_copy = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    detected_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="ad_history")

# --- 6. Search History Data ---
class SearchHistory(Base):
    __tablename__ = "search_history"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    query = Column(String, nullable=False)
    filters_used = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="searches")

# --- 7. Monitoring & Alerts Data ---
class Monitoring(Base):
    __tablename__ = "monitoring"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    target_type = Column(String, nullable=False) # 'STORE' or 'PRODUCT'
    target_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="monitored_items")

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    alert_type = Column(String, nullable=False) # 'PRICE_DROP', 'NEW_AD', 'NEW_BESTSELLER'
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()