from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, utils
from ..database import get_db
from ..api.auth import oauth2_scheme, verify_token

router = APIRouter(prefix="/api/notifications", tags=["notifications"])

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

@router.get("/", response_model=List[schemas.NotificationResponse])
async def get_notifications(
    current_user_data: tuple = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    """Получение уведомлений текущего пользователя"""
    user, token_data = current_user_data
    
    notifications = db.query(models.Notification)\
        .filter(models.Notification.user_id == user.id)\
        .order_by(models.Notification.created_at.desc())\
        .all()
    
    return notifications

@router.put("/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: int,
    current_user_data: tuple = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    """Отметить уведомление как прочитанное"""
    user, token_data = current_user_data
    
    notification = db.query(models.Notification)\
        .filter(models.Notification.id == notification_id)\
        .filter(models.Notification.user_id == user.id)\
        .first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Уведомление не найдено")
    
    notification.is_read = True
    db.commit()
    
    return {"message": "Уведомление отмечено как прочитанное"}

@router.put("/read-all")
async def mark_all_notifications_as_read(
    current_user_data: tuple = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    """Отметить все уведомления как прочитанные"""
    user, token_data = current_user_data
    
    db.query(models.Notification)\
        .filter(models.Notification.user_id == user.id)\
        .update({models.Notification.is_read: True})
    
    db.commit()
    
    return {"message": "Все уведомления отмечены как прочитанные"}