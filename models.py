from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from pydantic import BaseSettings, Field


# ✅ Load settings from environment or default
class Settings(BaseSettings):
    DATABASE_URL: str = Field("sqlite:///./smarttopup.db", env="DATABASE_URL")

    class Config:
        env_file = ".env"


settings = Settings()

# ✅ Database setup
engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ✅ User model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    whatsapp_id = Column(String, unique=True, index=True)
    name = Column(String, nullable=True)
    wallet = Column(Float, default=0.0)
    referral_code = Column(String, nullable=True)


# ✅ Transaction model
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_whatsapp = Column(String, index=True)
    tx_type = Column(String)  # airtime, data, bill, pin, fund
    provider = Column(String, nullable=True)
    amount = Column(Float, default=0.0)
    charge = Column(Float, default=0.0)
    status = Column(String, default="pending")  # pending, success, failed
    provider_ref = Column(String, nullable=True)
    meta = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
