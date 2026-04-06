from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional

class ReportBase(BaseModel):
    cash_sales: float
    realization: float
    incoming: float
    purchases: float
    income: float
    payment: float
    expenses: float
    balance: float

    @field_validator('*', mode='before')
    def validate_non_negative(cls, v):
        if v is not None and v < 0:
            raise ValueError('Значения должны быть неотрицательными')
        return v

class ReportCreate(ReportBase):
    pass

class ReportUpdate(ReportBase):
    pass

class ReportResponse(BaseModel):
    id: int
    user_id: int
    base_id: int
    date: datetime
    cash_sales: float
    realization: float
    incoming: float
    purchases: float
    income: float
    payment: float
    expenses: float
    balance: float
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ReportSummary(BaseModel):
    total_cash_sales: float
    total_realization: float
    total_incoming: float
    total_purchases: float
    total_income: float
    total_payment: float
    total_expenses: float
    total_balance: float
    report_count: int