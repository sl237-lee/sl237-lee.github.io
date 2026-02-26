"""
Database initialization and table creation
"""
import os
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

class Transaction(Base):
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    transaction_id = Column(String, unique=True, index=True)
    user_id = Column(String, index=True)
    amount = Column(Float)
    merchant = Column(String)
    category = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_fraud = Column(Boolean, nullable=True)
    fraud_score = Column(Float, nullable=True)
    
    # Location
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Device info
    device_id = Column(String)
    ip_address = Column(String)

class Prediction(Base):
    __tablename__ = 'predictions'
    
    id = Column(Integer, primary_key=True)
    transaction_id = Column(String, index=True)
    fraud_probability = Column(Float)
    is_fraud_predicted = Column(Boolean)
    model_version = Column(String)
    inference_time_ms = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

def init_db():
    """Initialize database and create tables"""
    db_url = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
    
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    print("✅ Database tables created successfully!")
    
    return engine

if __name__ == "__main__":
    init_db()
