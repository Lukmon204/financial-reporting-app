from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional
from datetime import timedelta
from .. import models, schemas, utils
from ..database import get_db
from ..utils.security import (
    verify_password, 
    create_access_token, 
    create_refresh_token, 
    verify_token
)
from ..config import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="/api/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def authenticate_user(db: Session, username: str, password: str):
    """Аутентифицирует пользователя"""
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

@router.post("/register", response_model=schemas.Token)
async def register(user_data: schemas.RegisterRequest, db: Session = Depends(get_db)):
    """Регистрация нового пользователя"""
    # Проверяем, что пользователь с таким именем не существует
    existing_user = db.query(models.User).filter(
        (models.User.username == user_data.username) | 
        (models.User.email == user_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким именем или email уже существует"
        )
    
    # Хешируем пароль и создаем пользователя
    hashed_password = utils.security.get_password_hash(user_data.password)
    user = models.User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        role="employee",
        status="pending"  # Ждет одобрения администратора
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Создаем токены
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username": user.id, "role": user.role},
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role}
    )
    
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/login", response_model=schemas.Token)
async def login(request: Request, form_ OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Вход пользователя в систему"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Аккаунт не активирован. Обратитесь к администратору."
        )
    
    # Логируем попытку входа
    audit_log = models.AuditLog(
        user_id=user.id,
        action="login",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", "")
    )
    db.add(audit_log)
    db.commit()
    
    # Создаем токены
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role},
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role}
    )
    
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer("/refresh")
async def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    """Обновление токена доступа"""
    token_data = verify_token(refresh_token)
    if token_data is None or token_data.get("token_type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный токен обновления"
        )
    
    user = db.query(models.User).filter(models.User.id == token_data["user_id"]).first()
    if not user or user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден или заблокирован"
        )
    
    # Создаем новый токен доступа
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Выход из системы"""
    token_data = verify_token(token)
    if token_
        # Логируем выход
        audit_log = models.AuditLog(
            user_id=token_data["user_id"],
            action="logout"
        )
        db.add(audit_log)
        db.commit()
    
    return {"message": "Вы успешно вышли из системы"}

@router.get("/me", response_model=schemas.UserResponse)
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Получение информации о текущем пользователе"""
    token_data = verify_token(token)
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не удалось проверить учетные данные",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(models.User).filter(models.User.id == token_data["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    return user