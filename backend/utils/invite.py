import secrets
import string
from typing import Dict, Tuple

# 邀请码配置：邀请码 -> (用户名, 是否管理员)
INVITE_CODE_CONFIG = {
    "hc0000": ("HC", True),
    "pk666": ("pk", False),
    "lhc666": ("lhc", False),
    "lyf666": ("lyf", False),
    "ldk666": ("ldk", False),
    "lxt666": ("lxt", False)
}

def validate_invite_code(invite_code: str) -> bool:
    """验证邀请码是否有效"""
    return invite_code in INVITE_CODE_CONFIG

def is_admin_invite_code(invite_code: str) -> bool:
    """检查是否为管理员邀请码"""
    if invite_code not in INVITE_CODE_CONFIG:
        return False
    return INVITE_CODE_CONFIG[invite_code][1]

def get_username_by_invite_code(invite_code: str) -> str:
    """根据邀请码获取对应的用户名"""
    if invite_code not in INVITE_CODE_CONFIG:
        return f"用户_{invite_code[:4]}"  # 默认用户名
    return INVITE_CODE_CONFIG[invite_code][0]

def generate_invite_code(length: int = 8) -> str:
    """生成新的邀请码"""
    characters = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))
def get_all_invite_codes() -> Dict[str, Tuple[str, bool]]:
    """获取所有邀请码配置（用于管理）"""
    return INVITE_CODE_CONFIG.copy()
    return INVITE_CODE_CONFIG.copy()