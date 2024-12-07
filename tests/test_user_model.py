from contextlib import contextmanager
import re
import sqlite3
import hashlib

import pytest

from models.user_model import (
    create_account,
    login,
    update_password
)

######################################################
#
#    Fixtures
#
######################################################

def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()

@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  
    mock_cursor.fetchall.return_value = []
    mock_conn.commit.return_value = None

    @contextmanager
    def mock_get_db_connection():
        yield mock_conn  

    mocker.patch("models.user_model.get_db_connection", mock_get_db_connection)

    return mock_cursor 

######################################################
#
#    Create Account
#
######################################################

def test_create_account(mock_cursor):
    """Test creating a new account in the database."""

    create_account(username="testuser", password="password123")

    expected_query = normalize_whitespace("""
        INSERT INTO users (username, password)
        VALUES (?, ?)
    """)

    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args[0][1]

    expected_arguments = ("testuser", hashlib.sha256("password123".encode()).hexdigest())
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_create_account_duplicate(mock_cursor):
    """Test creating an account with a duplicate username, raising an IntegrityError."""

    mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: users.username")

    with pytest.raises(ValueError, match="Username 'testuser' already exists"):
        create_account(username="testuser", password="password123")

######################################################
#
#    Login
#
######################################################

def test_login_success(mock_cursor):
    """Test successful login with correct username and password."""

    mock_cursor.fetchone.return_value = {"password": hashlib.sha256("password123".encode()).hexdigest()}

    result = login(username="testuser", password="password123")
    assert result is True, "Expected login to succeed, but it failed."

def test_login_invalid_password(mock_cursor):
    """Test login with an invalid password."""

    mock_cursor.fetchone.return_value = {"password": hashlib.sha256("wrongpassword".encode()).hexdigest()}

    result = login(username="testuser", password="password123")
    assert result is False, "Expected login to fail, but it succeeded."

def test_login_nonexistent_user(mock_cursor):
    """Test login with a non-existent username."""

    mock_cursor.fetchone.return_value = None

    result = login(username="nonexistentuser", password="password123")
    assert result is False, "Expected login to fail, but it succeeded."

######################################################
#
#    Update Password
#
######################################################

def test_update_password_success(mock_cursor):
    """Test successful password update."""

    mock_cursor.fetchone.return_value = {"password": hashlib.sha256("oldpassword".encode()).hexdigest()}

    update_password(username="testuser", old_password="oldpassword", new_password="newpassword123")

    expected_query = normalize_whitespace("""
        UPDATE users SET password = ? WHERE username = ?
    """)

    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args_list[1][0][1]

    expected_arguments = (hashlib.sha256("newpassword123".encode()).hexdigest(), "testuser")
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_update_password_invalid_old_password(mock_cursor):
    """Test password update with an invalid old password."""

    mock_cursor.fetchone.return_value = {"password": hashlib.sha256("wrongoldpassword".encode()).hexdigest()}

    with pytest.raises(ValueError, match="Invalid username or old password"):
        update_password(username="testuser", old_password="oldpassword", new_password="newpassword123")

def test_update_password_nonexistent_user(mock_cursor):
    """Test password update with a non-existent username."""

    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Invalid username or old password"):
        update_password(username="nonexistentuser", old_password="oldpassword", new_password="newpassword123")