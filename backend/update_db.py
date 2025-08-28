#!/usr/bin/env python3
"""
数据库更新脚本 - 为现有用户添加新字段
"""
import sqlite3

def update_database():
    """更新数据库结构和现有数据"""
    print("正在更新数据库结构...")
    
    # 连接到SQLite数据库
    conn = sqlite3.connect('chat.db')
    cursor = conn.cursor()
    
    try:
        # 检查是否已存在is_online列
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'is_online' not in columns:
            print("添加is_online列...")
            cursor.execute("ALTER TABLE users ADD COLUMN is_online BOOLEAN DEFAULT 0")
        else:
            print("is_online列已存在")
            
        if 'last_active' not in columns:
            print("添加last_active列...")
            cursor.execute("ALTER TABLE users ADD COLUMN last_active DATETIME")
        else:
            print("last_active列已存在")
        
        # 更新所有现有用户的在线状态为False
        cursor.execute("UPDATE users SET is_online = 0 WHERE is_online IS NULL")
        cursor.execute("UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE last_active IS NULL")
        
        conn.commit()
        print("数据库更新完成！")
        
    except Exception as e:
        print(f"更新失败: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    update_database()
