#!/usr/bin/env python3
"""
清理脚本：只保留 hc0000 管理员账户
"""

import sqlite3
from pathlib import Path

def clean_admin_users():
    """只保留 hc0000 管理员账户"""
    db_path = Path(__file__).parent / "chat.db"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("清理多余的管理员账户...")
        
        # 只保留 hc0000 账户，删除其他所有用户
        cursor.execute("DELETE FROM users WHERE invite_code != 'hc0000'")
        deleted_count = cursor.rowcount
        
        conn.commit()
        
        print(f"删除了 {deleted_count} 个多余用户")
        
        # 显示剩余用户
        cursor.execute("SELECT id, username, invite_code, is_admin FROM users")
        users = cursor.fetchall()
        
        print(f"\n剩余用户 ({len(users)} 个):")
        for user in users:
            admin_status = "管理员" if user[3] else "普通用户"
            print(f"  ID: {user[0]}, 用户名: {user[1]}, 邀请码: {user[2]}, 类型: {admin_status}")
            
    finally:
        conn.close()

if __name__ == "__main__":
    clean_admin_users()
