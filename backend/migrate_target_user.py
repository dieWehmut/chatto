#!/usr/bin/env python3
"""
数据库迁移脚本：添加 target_user_id 字段到 messages 表
"""

import sqlite3
from pathlib import Path
import sys

def migrate_database():
    """添加 target_user_id 字段到 messages 表"""
    
    # 数据库路径
    db_path = Path(__file__).parent / "chat.db"
    
    if not db_path.exists():
        print(f"数据库文件不存在: {db_path}")
        return False
    
    conn = None
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查字段是否已存在
        cursor.execute("PRAGMA table_info(messages)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'target_user_id' in column_names:
            print("target_user_id 字段已存在，无需迁移")
            return True
        
        print("开始迁移数据库...")
        
        # 添加 target_user_id 字段
        cursor.execute("""
            ALTER TABLE messages 
            ADD COLUMN target_user_id INTEGER REFERENCES users(id)
        """)
        
        # 提交更改
        conn.commit()
        
        print("数据库迁移完成！")
        print("已添加 target_user_id 字段到 messages 表")
        
        return True
        
    except sqlite3.Error as e:
        print(f"数据库迁移失败: {e}")
        return False
    
    finally:
        if conn:
            conn.close()

def verify_migration():
    """验证迁移是否成功"""
    
    db_path = Path(__file__).parent / "chat.db"
    
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查表结构
        cursor.execute("PRAGMA table_info(messages)")
        columns = cursor.fetchall()
        
        print("\n当前 messages 表结构:")
        for col in columns:
            print(f"  {col[1]} - {col[2]} (可空: {not col[3]})")
        
        # 检查是否包含 target_user_id
        column_names = [col[1] for col in columns]
        if 'target_user_id' in column_names:
            print("\n✅ target_user_id 字段已成功添加")
            return True
        else:
            print("\n❌ target_user_id 字段未找到")
            return False
        
    except sqlite3.Error as e:
        print(f"验证失败: {e}")
        return False
    
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("=" * 50)
    print("开始数据库迁移：添加消息目标用户字段")
    print("=" * 50)
    
    # 执行迁移
    if migrate_database():
        # 验证迁移
        if verify_migration():
            print("\n🎉 数据库迁移成功完成！")
            sys.exit(0)
        else:
            print("\n❌ 数据库迁移验证失败！")
            sys.exit(1)
    else:
        print("\n❌ 数据库迁移失败！")
        sys.exit(1)
