from dataclasses import dataclass
import logging
import os
import sqlite3
from typing import Any
import hashlib

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@dataclass
class User:
    id: int
    username: str
    password: str

def get_db_connection():
    conn = sqlite3.connect(os.getenv('DB_PATH'))
    conn.row_factory = sqlite3.Row
    return conn

def create_account(username: str, password: str) -> None:
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (username, password)
                VALUES (?, ?)
            """, (username, hashed_password))
            conn.commit()
            logger.info("Account successfully created for username: %s", username)
    except sqlite3.IntegrityError:
        logger.error("Username already exists: %s", username)
        raise ValueError(f"Username '{username}' already exists")
    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e

def login(username: str, password: str) -> bool:
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            if row and row['password'] == hashed_password:
                logger.info("Login successful for username: %s", username)
                return True
            else:
                logger.warning("Invalid username or password for username: %s", username)
                return False
    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e

def update_password(username: str, old_password: str, new_password: str) -> None:
    hashed_old_password = hashlib.sha256(old_password.encode()).hexdigest()
    hashed_new_password = hashlib.sha256(new_password.encode()).hexdigest()
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            if row and row['password'] == hashed_old_password:
                cursor.execute("UPDATE users SET password = ? WHERE username = ?", (hashed_new_password, username))
                conn.commit()
                logger.info("Password updated successfully for username: %s", username)
            else:
                logger.warning("Invalid old password for username: %s", username)
                raise ValueError("Invalid username or old password")
    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e