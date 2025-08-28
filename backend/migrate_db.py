#!/usr/bin/env python3
"""
数据库迁移脚本 - 添加消息删除相关字段
"""

import sqlite3

def migrate_database():
    """添加消息删除相关字段到现有数据库"""
    conn = sqlite3.connect('chat.db')
    cursor = conn.cursor()
    
    try:
        # 检查是否已存在新字段
        cursor.execute("PRAGMA table_info(messages)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # 添加 is_deleted 字段
        if 'is_deleted' not in columns:
            cursor.execute('ALTER TABLE messages ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE')
            print("Added is_deleted column")
        
        # 添加 deleted_at 字段
        if 'deleted_at' not in columns:
            cursor.execute('ALTER TABLE messages ADD COLUMN deleted_at DATETIME')
            print("Added deleted_at column")
        
        # 添加 deleted_by 字段
        if 'deleted_by' not in columns:
            cursor.execute('ALTER TABLE messages ADD COLUMN deleted_by INTEGER')
            print("Added deleted_by column")
        
        conn.commit()
        print("Database migration completed successfully!")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
