#!/usr/bin/env python3
"""
数据库迁移脚本：清理非管理员用户，只保留管理员账户
"""

import sqlite3
from pathlib import Path

def clean_users():
    """清理数据库中的非管理员用户"""
    db_path = Path(__file__).parent / "chat.db"
    
    if not db_path.exists():
        print(f"数据库文件不存在: {db_path}")
        return False
    
    conn = None
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("开始清理用户数据...")
        
        # 查看当前用户
        cursor.execute("SELECT id, username, invite_code, is_admin FROM users")
        users = cursor.fetchall()
        
        print(f"\n当前用户列表 ({len(users)} 个用户):")
        for user in users:
            admin_status = "管理员" if user[3] else "普通用户"
            print(f"  ID: {user[0]}, 用户名: {user[1]}, 邀请码: {user[2]}, 类型: {admin_status}")
        
        # 删除非管理员用户
        cursor.execute("DELETE FROM users WHERE is_admin = 0 OR is_admin IS NULL")
        deleted_count = cursor.rowcount
        
        # 注意：消息表不需要更新，因为它通过外键关联用户
        # 消息会保留，但用户信息会通过 JOIN 查询获取
        
        # 提交更改
        conn.commit()
        
        print(f"\n✅ 清理完成!")
        print(f"   删除了 {deleted_count} 个非管理员用户")
        print("   相关消息已保留，将显示为历史消息")
        
        # 显示剩余用户
        cursor.execute("SELECT id, username, invite_code, is_admin FROM users")
        remaining_users = cursor.fetchall()
        
        print(f"\n保留的用户 ({len(remaining_users)} 个):")
        for user in remaining_users:
            admin_status = "管理员" if user[3] else "普通用户"
            print(f"  ID: {user[0]}, 用户名: {user[1]}, 邀请码: {user[2]}, 类型: {admin_status}")
        
        return True
        
    except sqlite3.Error as e:
        print(f"数据库操作失败: {e}")
        return False
    
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("数据库用户清理脚本")
    print("此脚本将删除所有非管理员用户，只保留管理员账户")
    print("=" * 60)
    
    # 确认操作
    confirm = input("\n确定要继续吗？(y/N): ")
    if confirm.lower() != 'y':
        print("操作已取消")
        exit(0)
    
    # 执行清理
    if clean_users():
        print("\n🎉 用户数据清理完成！")
        print("现在管理员可以通过管理界面重新添加用户")
    else:
        print("\n❌ 清理失败！")
        exit(1)
