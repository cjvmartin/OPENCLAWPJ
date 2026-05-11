# 檔案路徑：backend/database/db_manager.py
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from backend.config import settings
import json

Base = declarative_base()

# 定義訂單表格
class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String(50))
    items_json = Column(Text)  # 儲存餐點 JSON 字串
    total_fee = Column(Float)
    status = Column(String(20), default="pending") 
    created_at = Column(DateTime, default=datetime.now)

# 🌟 修正處：將 create_all 改為 create_engine
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    """建立所有表格"""
    # 這裡才是使用 create_all 的地方
    Base.metadata.create_all(bind=engine)

def save_new_order(user_name, items_list):
    """將解析後的訂單存入資料庫"""
    db = SessionLocal()
    try:
        new_order = Order(
            user_name=user_name,
            items_json=json.dumps(items_list, ensure_ascii=False),
            total_fee=settings.DEFAULT_DELIVERY_FEE
        )
        db.add(new_order)
        db.commit()
        db.refresh(new_order)
        return new_order.id
    except Exception as e:
        print(f"❌ 資料庫寫入失敗：{e}")
        db.rollback()
        return None
    finally:
        db.close()

def get_all_orders():
    """讀取所有訂單"""
    db = SessionLocal()
    try:
        orders = db.query(Order).order_by(Order.created_at.desc()).all()
        return orders
    finally:
        db.close()