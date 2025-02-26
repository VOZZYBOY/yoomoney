
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
import json
from config import DATABASE_URL 

Base = declarative_base()

class Payment(Base):
    __tablename__ = 'payments'

    id = Column(Integer, primary_key=True)
    amount = Column(Float, nullable=False)
    description = Column(String)
    status = Column(String, default='pending')
    user_id = Column(Integer) 
    payment_id = Column(String, unique=True)  
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_recurrent = Column(Boolean, default=False)
    payment_method_id = Column(String)  
    retries = Column(Integer, default=0)
    metadata = Column(Text)

    def __repr__(self):
        return f"<Payment(id={self.id}, amount={self.amount}, status='{self.status}')>"

    def to_dict(self):
        """Конвертирует объект Payment в словарь."""
        return {
            'id': self.id,
            'amount': self.amount,
            'description': self.description,
            'status': self.status,
            'user_id': self.user_id,
            'payment_id': self.payment_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_recurrent': self.is_recurrent,
            'payment_method_id': self.payment_method_id,
            'retries': self.retries,
            'metadata': json.loads(self.metadata) if self.metadata else {}
        }

engine = create_engine(DATABASE_URL) 
Base.metadata.create_all(engine) 
Session = sessionmaker(bind=engine)
session = Session()
