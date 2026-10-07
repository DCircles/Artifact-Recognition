# memory.py
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import hashlib

DB_PATH = Path("artifact_memory.db")


def init_db():
    """初始化数据库表结构"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            role TEXT NOT NULL, -- 'user' or 'assistant'
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS image_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            image_hash TEXT NOT NULL, -- 图像hash值，唯一键
            question TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            UNIQUE(user_id, image_hash, question)
        )
    """)
    conn.commit()
    conn.close()

def calc_img_hash(image_bytes: bytes) -> str:
    """ 计算图片的哈希值 """
    return hashlib.md5(image_bytes).hexdigest()

def get_history_hash(user_id: str, image_hash:str, question: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT content FROM image_cache WHERE user_id = ? AND image_hash = ? AND question = ?",
                   (user_id, image_hash, question))
    result = cursor.fetchone()
    conn.close()
    return result

def save_message(user_id: str, role: str, content: str):
    """保存单条消息"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT OR IGNORE INTO messages (user_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
            (user_id,role, content, datetime.now().isoformat(timespec="seconds"))
        )
        conn.commit()
    except sqlite3.Error as e:
        print(str(e))
    finally:
        conn.close()

def save_assistant_messages(user_id: str, image_hash: str, question: str, content:str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT OR IGNORE INTO image_cache (user_id, image_hash, question, content, timestamp) VALUES (?, ?, ?, ?, ?)",
                       (user_id, image_hash, question, content, datetime.now().isoformat(timespec="seconds")))
        conn.commit()
    except sqlite3.Error as e:
        print(str(e))
    finally:
        conn.close()

def get_history(user_id: str, limit: int = 6) -> List[Dict[str, Any]]:
    """
    获取指定会话的历史记录
    返回格式适配 LangChain 的 MessagesPlaceholder
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # 获取最近的 limit 条记录，并按时间正序排列
    cursor.execute(
        "SELECT role, content FROM messages WHERE user_id = ? ORDER BY id DESC LIMIT ?",
        (user_id, limit)
    )
    rows = cursor.fetchall()
    conn.close()

    # 转换为 LangChain 兼容的字典列表
    # 注意：数据库取出是倒序，这里需要反转回正序
    history = [{"role": row[0], "content": row[1]} for row in reversed(rows)]
    return history


# 模块加载时自动初始化数据库
init_db()