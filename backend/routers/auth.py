from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
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
    if not validate_invite_code(request.invite_code, db):
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
    
    # 检查是否为静态配置中的邀请码（可以自动创建用户）
    from utils.invite import INVITE_CODE_CONFIG
    if request.invite_code not in INVITE_CODE_CONFIG:
        raise HTTPException(status_code=400, detail="邀请码不存在，请联系管理员添加用户")
    
    # 新用户，使用邀请码对应的固定用户名（只适用于静态配置的邀请码）
    is_admin = is_admin_invite_code(request.invite_code, db)
    username = get_username_by_invite_code(request.invite_code, db)
    
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

class OnlineStatusRequest(BaseModel):
    user_id: int
    is_online: bool

# 用户管理相关模型
class CreateUserRequest(BaseModel):
    admin_user_id: int
    invite_code: str
    username: str
    is_admin: bool = False

class UpdateUserRequest(BaseModel):
    admin_user_id: int
    target_user_id: int
    new_username: Optional[str] = None
    new_invite_code: Optional[str] = None
    is_admin: Optional[bool] = None

class UserManagementResponse(BaseModel):
    id: int
    username: str
    invite_code: str
    is_admin: bool
    is_online: bool
    created_at: datetime
    last_active: Optional[datetime]

    class Config:
        from_attributes = True

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

def verify_admin(user_id: int, db: Session) -> User:
    """验证用户是否为管理员"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if not getattr(user, "is_admin"):
        raise HTTPException(status_code=403, detail="权限不足，需要管理员权限")
    return user

@router.post("/admin/create_user", response_model=UserManagementResponse)
async def create_user(request: CreateUserRequest, db: Session = Depends(get_db)):
    """管理员创建新用户"""
    # 验证管理员权限
    verify_admin(request.admin_user_id, db)
    
    # 检查邀请码是否已存在
    existing_user = db.query(User).filter(User.invite_code == request.invite_code).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="邀请码已存在")
    
    # 创建新用户
    new_user = User(
        invite_code=request.invite_code,
        username=request.username,
        is_admin=request.is_admin,
        is_online=False,
        created_at=datetime.now(timezone.utc),
        last_active=None
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@router.put("/admin/update_user", response_model=UserManagementResponse)
async def update_user(request: UpdateUserRequest, db: Session = Depends(get_db)):
    """管理员更新用户信息"""
    # 验证管理员权限
    verify_admin(request.admin_user_id, db)
    
    # 查找目标用户
    target_user = db.query(User).filter(User.id == request.target_user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="目标用户不存在")
    
    # 更新用户信息
    if request.new_username is not None:
        setattr(target_user, "username", request.new_username)
    
    if request.new_invite_code is not None:
        # 检查新邀请码是否已被其他用户使用
        existing_code_user = db.query(User).filter(
            User.invite_code == request.new_invite_code,
            User.id != request.target_user_id
        ).first()
        if existing_code_user:
            raise HTTPException(status_code=400, detail="新邀请码已被其他用户使用")
        setattr(target_user, "invite_code", request.new_invite_code)
    
    if request.is_admin is not None:
        setattr(target_user, "is_admin", request.is_admin)
    
    db.commit()
    db.refresh(target_user)
    
    return target_user

@router.get("/admin/users", response_model=List[UserManagementResponse])
async def get_all_users(admin_user_id: int, db: Session = Depends(get_db)):
    """管理员获取所有用户列表"""
    # 验证管理员权限
    verify_admin(admin_user_id, db)
    
    users = db.query(User).order_by(User.created_at.desc()).all()
    return users

@router.get("/admin/delete_user")
async def delete_user(admin_user_id: int, target_user_id: int, db: Session = Depends(get_db)):
    """管理员删除用户"""
    # 验证管理员权限
    admin = verify_admin(admin_user_id, db)
    
    # 查找目标用户
    target_user = db.query(User).filter(User.id == target_user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="目标用户不存在")
    
    # 不能删除自己
    if getattr(admin, "id") == getattr(target_user, "id"):
        raise HTTPException(status_code=400, detail="不能删除自己")
    
    try:
        # 导入 Message 模型
        from app.models import Message
        
        # 删除该用户的所有消息
        db.query(Message).filter(Message.user_id == target_user_id).delete()
        
        # 清理该用户作为目标用户的消息关联
        db.query(Message).filter(Message.target_user_id == target_user_id).update({Message.target_user_id: None})
        
        # 清理该用户作为删除者的消息关联
        db.query(Message).filter(Message.deleted_by == target_user_id).update({Message.deleted_by: None})
        
        # 删除用户
        db.delete(target_user)
        db.commit()
        
        return {"message": f"用户 {getattr(target_user, 'username')} 已被删除"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除用户失败: {str(e)}")

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