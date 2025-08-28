from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from datetime import datetime, timezone
from utils.invite import (
    validate_invite_code, 
    is_admin_invite_code, 
    get_username_by_invite_code
)

router = APIRouter()

class LoginRequest(BaseModel):
    invite_code: str

class LoginResponse(BaseModel):
    message: str
    user_id: int
    username: str
    is_admin: bool
    invite_code: str

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    if not validate_invite_code(request.invite_code):
        raise HTTPException(status_code=400, detail="无效的邀请码")
    
    # 检查用户是否已存在
    existing_user = db.query(User).filter(User.invite_code == request.invite_code).first()
    if existing_user:
        # 更新在线状态
        setattr(existing_user, "is_online", True)
        setattr(existing_user, "last_active", datetime.now(timezone.utc))
        db.commit()
        
        return LoginResponse(
            message="登录成功",
            user_id=getattr(existing_user, "id"),
            username=getattr(existing_user, "username"),
            is_admin=getattr(existing_user, "is_admin"),
            invite_code=getattr(existing_user, "invite_code")
        )
    
    # 新用户，使用邀请码对应的固定用户名
    is_admin = is_admin_invite_code(request.invite_code)
    username = get_username_by_invite_code(request.invite_code)
    
    new_user = User(
        invite_code=request.invite_code,
        username=username,
        is_admin=is_admin,
        is_online=True,
        last_active=datetime.now(timezone.utc)
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return LoginResponse(
        message="账户创建成功",
        user_id=getattr(new_user, "id"),
        username=getattr(new_user, "username"),
        is_admin=getattr(new_user, "is_admin"),
        invite_code=getattr(new_user, "invite_code")
    )

from typing import Dict, List, Any

class OnlineStatusRequest(BaseModel):
    user_id: int
    is_online: bool

@router.post("/update_online_status")
async def update_online_status(request: OnlineStatusRequest, db: Session = Depends(get_db)):
    """更新用户在线状态"""
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # SQLAlchemy实例属性赋值
    setattr(user, "is_online", request.is_online)
    setattr(user, "last_active", datetime.now(timezone.utc))
    db.commit()
    
    return {"message": "在线状态更新成功"}

@router.get("/invite_codes")
async def get_invite_codes() -> Dict[str, List[Dict[str, Any]]]:
    """获取所有可用的邀请码（仅用于开发/测试）"""
    from utils.invite import get_all_invite_codes
    codes = get_all_invite_codes()
    return {
        "invite_codes": [
            {
                "code": code,
                "username": config[0],
                "is_admin": config[1]
            }
            for code, config in codes.items()
        ]
    }