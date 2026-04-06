from sqlalchemy import Column, Integer, DateTime, Float, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    base_id = Column(Integer, ForeignKey("bases.id"), nullable=False)
    date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    cash_sales = Column(Float, nullable=False)
    realization = Column(Float, nullable=False)
    incoming = Column(Float, nullable=False)
   , nullable=False)
    income = Column(Float, nullable=False)
    payment = Column(Float, nullable=False)
    expenses = Column(Float, nullable=False)
    balance = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Связи
    author = relationship("User", back_populates="reports")
    base_info = relationship("BaseInfo", back_populates="reports")

    # Ограничение: один отчет в день на одного пользователя
    __table_args__ = (UniqueConstraint('user_id', 'date', name='_user_date_uc'),)