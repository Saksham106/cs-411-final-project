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
    """Represents a user in the system.

    Attributes:
        id (int): The unique identifier for the user.
        username (str): The username chosen by the user.
        password (str): The user's hashed password.
    """
    id: int
    username: str
    password: str


def get_db_connection():
    """Create and return a connection to the SQLite database.

    Uses the `DB_PATH` environment variable to determine the database location. 
    The connection returned has its `row_factory` set to `sqlite3.Row` to allow 
    accessing columns by name.

    Returns:
        sqlite3.Connection: A connection to the SQLite database.
    """
    conn = sqlite3.connect(os.getenv('DB_PATH'))
    conn.row_factory = sqlite3.Row
    return conn


def create_account(username: str, password: str) -> None:
    """Create a new user account with the given username and password.

    The password is hashed using SHA-256 before storing it in the database.

    Args:
        username (str): The desired username for the new account.
        password (str): The plaintext password for the new account.

    Raises:
        ValueError: If the username already exists.
        sqlite3.Error: If a database error occurs.
    """
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
    """Attempt to log in a user with the provided credentials.

    The provided password is hashed and compared against the stored hash.

    Args:
        username (str): The username of the account.
        password (str): The plaintext password for the account.

    Returns:
        bool: True if the login is successful, False otherwise.

    Raises:
        sqlite3.Error: If a database error occurs.
    """
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
    """Update the password for a given user if the old password is correct.

    Args:
        username (str): The username of the account.
        old_password (str): The user's current plaintext password.
        new_password (str): The user's desired new plaintext password.

    Raises:
        ValueError: If the provided old password is invalid or the username does not exist.
        sqlite3.Error: If a database error occurs.
    """
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
