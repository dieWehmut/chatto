#!/usr/bin/env python3
"""
数据库迁移脚本：为Message表添加文件支持字段
"""

import sqlite3
import os

def migrate_database():
    db_path = 'chat.db'
    
    if not os.path.exists(db_path):
        print(f"数据库文件 {db_path} 不存在")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 检查是否已经有新字段
        cursor.execute("PRAGMA table_info(messages)")
        columns = [column[1] for column in cursor.fetchall()]
        
        new_columns = ['message_type', 'file_path', 'file_name', 'file_size']
        for column in new_columns:
            if column not in columns:
                print(f"添加字段: {column}")
                if column == 'message_type':
                    cursor.execute(f"ALTER TABLE messages ADD COLUMN {column} TEXT DEFAULT 'text'")
                elif column == 'file_path':
                    cursor.execute(f"ALTER TABLE messages ADD COLUMN {column} TEXT")
                elif column == 'file_name':
                    cursor.execute(f"ALTER TABLE messages ADD COLUMN {column} TEXT")
                elif column == 'file_size':
                    cursor.execute(f"ALTER TABLE messages ADD COLUMN {column} INTEGER")
            else:
                print(f"字段 {column} 已存在")
        
        # 确保现有消息的message_type为'text'
        cursor.execute("UPDATE messages SET message_type = 'text' WHERE message_type IS NULL")
        
        conn.commit()
        print("数据库迁移完成！")
        
    except Exception as e:
        print(f"迁移失败: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
