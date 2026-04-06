from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, utils
from ..database import get_db
from ..api.auth import oauth2_scheme, verify_token

router = APIRouter(prefix="/api/users", tags=["users"])

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

@router.get("/me", response_model=schemas.UserResponse)
async def get_my_profile(current_user_data: tuple = Depends(get_current_user_role)):
    """Получение профиля текущего пользователя"""
    user, token_data = current_user_data
    return user

@router.put("/me", response_model=schemas.UserResponse)
async def update_my_profile(
    user_update: schemas.UserUpdate,
    current_user_data: tuple = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    """Обновление профиля текущего пользователя"""
    user, token_data = current_user_data
    
    # Обновляем только разрешенные поля
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field in ["full_name"]:  # Разрешенные для изменения поля
            setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    return user