import secrets
import string
from typing import Dict, Tuple, Optional
from sqlalchemy.orm import Session

# 邀请码配置：邀请码 -> (用户名, 是否管理员)
# 只保留初始管理员用户，其他用户由管理员界面添加
INVITE_CODE_CONFIG = {
    "hc0000": ("HC", True)
}

def validate_invite_code(invite_code: str, db: Optional[Session] = None) -> bool:
    """验证邀请码是否有效 - 检查静态配置和数据库"""
    # 首先检查静态配置
    if invite_code in INVITE_CODE_CONFIG:
        return True
    
    # 如果提供了数据库会话，检查数据库中的用户
    if db:
        from app.models import User
        existing_user = db.query(User).filter(User.invite_code == invite_code).first()
        return existing_user is not None
    
    return False

def is_admin_invite_code(invite_code: str, db: Optional[Session] = None) -> bool:
    """检查是否为管理员邀请码 - 检查静态配置和数据库"""
    # 首先检查静态配置
    if invite_code in INVITE_CODE_CONFIG:
        return INVITE_CODE_CONFIG[invite_code][1]
    
    # 如果提供了数据库会话，检查数据库中的用户
    if db:
        from app.models import User
        existing_user = db.query(User).filter(User.invite_code == invite_code).first()
        if existing_user:
            return getattr(existing_user, "is_admin")
    
    return False

def get_username_by_invite_code(invite_code: str, db: Optional[Session] = None) -> str:
    """根据邀请码获取对应的用户名 - 检查静态配置和数据库"""
    # 首先检查静态配置
    if invite_code in INVITE_CODE_CONFIG:
        return INVITE_CODE_CONFIG[invite_code][0]
    
    # 如果提供了数据库会话，检查数据库中的用户
    if db:
        from app.models import User
        existing_user = db.query(User).filter(User.invite_code == invite_code).first()
        if existing_user:
            return getattr(existing_user, "username")
    
    return f"用户_{invite_code[:4]}"  # 默认用户名

def generate_invite_code(length: int = 8) -> str:
    """生成新的邀请码"""
    characters = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))
def get_all_invite_codes() -> Dict[str, Tuple[str, bool]]:
    """获取所有邀请码配置（用于管理）"""
    return INVITE_CODE_CONFIG.copy()
    return INVITE_CODE_CONFIG.copy()