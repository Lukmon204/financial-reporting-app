from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
from .. import models, schemas, utils
from ..database import get_db
from ..api.auth import oauth2_scheme, verify_token
from ..config import TIMEZONE

router = APIRouter(prefix="/api/reports", tags=["reports"])

def get_current_user_role(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Получает информацию о текущем пользователе и проверяет его роль"""
    token_data = utils.security.verify_token(token)
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не удалось проверить учетные данные",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(models.User).filter(models.User.id == token_data["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    return user, token_data

@router.post("/", response_model=schemas.ReportResponse)
async def create_report(
    report_data: schemas.ReportCreate,
    current_user_data: tuple = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    """Создание нового отчета"""
    user, token_data = current_user_data
    
    # Проверяем статус пользователя
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ваш аккаунт не активирован"
        )
    
    # Проверяем, не отправлял ли пользователь отчет сегодня
    today_start = datetime.now(TIMEZONE).replace(hour=0, minute=0, second=0, microsecond=0)
    existing_report = db.query(models.Report).filter(
        models.Report.user_id == user.id,
        models.Report.date >= today_start
    ).first()
    
    if existing_report:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Вы уже отправили отчет сегодня"
        )
    
    # Создаем отчет
    report = models.Report(
        user_id=user.id,
        base_id=user.base_id,
        cash_sales=report_data.cash_sales,
        realization=report_data.realization,
        incoming=report_data.incoming,
        purchases=report_data.purchases,
        income=report_data.income,
        payment=report_data.payment,
        expenses=report_data.expenses,
        balance=report_data.balance
    )
    
    db.add(report)
    db.commit()
    db.refresh(report)
    
    # Создаем уведомление для менеджера
    if user.base_id:
        manager = db.query(models.User).filter(
            models.User.base_id == user.base_id,
            models.User.role == "manager"
        ).first()
        
        if manager:
            notification = models.Notification(
                user_id=manager.id,
                title="Новый отчет",
                message=f"Пользователь {user.full_name} отправил новый отчет за сегодня"
            )
            db.add(notification)
            db.commit()
    
    return report

@router.get("/{report_id}", response_model=schemas.ReportResponse)
async def get_report(
    report_id: int,
    current_user_data: tuple = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    """Получение конкретного отчета"""
    user, token_data = current_user_data
    
    report = db.query(models.Report).filter(models.Report.id == report_id).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Отчет не найден")
    
    # Проверяем права доступа
    if user.role != "admin" and user.role != "manager" and report.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для просмотра отчета"
        )
    
    # Для менеджеров и админов - проверяем, принадлежит ли отчет их базе
    if user.role in ["manager"]:
        if user.base_id and report.base_id != user.base_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для просмотра отчета"
            )
    
    return report

@router.put("/{report_id}", response_model=schemas.ReportResponse)
async def update_report(
    report_id: int,
    report_data: schemas.ReportUpdate,
    current_user_data: tuple = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    """Обновление отчета (в течение 1 часа после создания)"""
    user, token_data = current_user_data
    
    report = db.query(models.Report).filter(models.Report.id == report_id).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Отчет не найден")
    
    # Проверяем права доступа - только владелец может редактировать
    if report.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для редактирования отчета"
        )
    
    # Проверяем, прошло ли менее 1 часа с момента создания
    one_hour_ago = datetime.now(TIMEZONE) - timedelta(hours=1)
    if report.created_at.replace(tzinfo=None) < one_hour_ago.replace(tzinfo=None):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Редактирование отчета возможно только в течение 1 часа после отправки"
        )
    
    # Обновляем поля отчета
    for field, value in report_data.model_dump().items():
        setattr(report, field, value)
    
    db.commit()
    db.refresh(report)
    
    return report

@router.delete("/{report_id}")
async def delete_report(
    report_id: int,
    current_user_data: tuple = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    """Удаление отчета (в течение 1 часа после создания)"""
    user, token_data = current_user_data
    
    report = db.query(models.Report).filter(models.Report.id == report_id).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Отчет не найден")
    
    # Только администратор может удалять отчеты
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только администратор может удалять отчеты"
        )
    
    db.delete(report)
    db.commit()
    
    return {"message": "Отчет успешно удален"}

@router.get("/", response_model=List[schemas.ReportResponse])
async def get_reports(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    base_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user_data: tuple = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    """Получение списка отчетов с фильтрами"""
    user, token_data = current_user_data
    
    query = db.query(models.Report).order_by(models.Report.created_at.desc())
    
    # Фильтры в зависимости от роли пользователя
    if user.role == "employee":
        # Сотрудник видит только свои отчеты
        query = query.filter(models.Report.user_id == user.id)
    elif user.role == "manager":
        # Менеджер видит отчеты своей базы
        if user.base_id:
            query = query.join(models.User).filter(models.User.base_id == user.base_id)
    # Администратор видит все отчеты
    
    # Дополнительные фильтры
    if user_id and (user.role == "admin" or user.role == "manager"):
        query = query.filter(models.Report.user_id == user_id)
    
    if base_id and user.role == "admin":
        query = query.filter(models.Report.base_id == base_id)
    
    if start_date:
        query = query.filter(models.Report.date >= start_date)
    
    if end_date:
        query = query.filter(models.Report.date <= end_date)
    
    reports = query.offset(skip).limit(limit).all()
    return reports

@router.get("/today/summary", response_model=schemas.ReportSummary)
async def get_today_summary(
    current_user_data: tuple = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    """Сводка по отчетам за сегодня"""
    user, token_data = current_user_data
    
    today_start = datetime.now(TIMEZONE).replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = datetime.now(TIMEZONE).replace(hour=23, minute=59, second=59, microsecond=999999)
    
    query = db.query(models.Report).filter(
        models.Report.date >= today_start,
        models.Report.date <= today_end
    )
    
    # Фильтрация в зависимости от роли
    if user.role == "employee":
        query = query.filter(models.Report.user_id == user.id)
    elif user.role == "manager":
        if user.base_id:
            query = query.join(models.User).filter(models.User.base_id == user.base_id)
    
    reports = query.all()
    
    if not reports:
        return schemas.ReportSummary(
            total_cash_sales=0,
            total_realization=0,
            total_incoming=0,
            total_purchases=0,
            total_income=0,
            total_payment=0,
            total_expenses=0,
            total_balance=0,
            report_count=0
        )
    
    summary = schemas.ReportSummary(
        total_cash_sales=sum(r.cash_sales for r in reports),
        total_realization=sum(r.realization for r in reports),
        total_incoming=sum(r.incoming for r in reports),
        total_purchases=sum(r.purchases for r in reports),
        total_income=sum(r.income for r in reports),
        total_payment=sum(r.payment for r in reports),
        total_expenses=sum(r.expenses for r in reports),
        total_balance=sum(r.balance for r in reports),
        report_count=len(reports)
    )
    
    return summary