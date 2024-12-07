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

# Mocking the database connection for tests
@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Mock the connection's cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Default return for queries
    mock_cursor.fetchall.return_value = []
    mock_conn.commit.return_value = None

    # Mock the get_db_connection context manager from user_model
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn  # Yield the mocked connection object

    mocker.patch("models.user_model.get_db_connection", mock_get_db_connection)

    return mock_cursor  # Return the mock cursor so we can set expectations per test

######################################################
#
#    Create Account
#
######################################################

def test_create_account(mock_cursor):
    """Test creating a new account in the database."""

    # Call the function to create a new account
    create_account(username="testuser", password="password123")

    expected_query = normalize_whitespace("""
        INSERT INTO users (username, password)
        VALUES (?, ?)
    """)

    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call (second element of call_args)
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = ("testuser", hashlib.sha256("password123".encode()).hexdigest())
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_create_account_duplicate(mock_cursor):
    """Test creating an account with a duplicate username, raising an IntegrityError."""

    # Simulate IntegrityError due to a duplicate entry
    mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: users.username")

    # Expect ValueError when handling IntegrityError
    with pytest.raises(ValueError, match="Username 'testuser' already exists"):
        create_account(username="testuser", password="password123")

######################################################
#
#    Login
#
######################################################

def test_login_success(mock_cursor):
    """Test successful login with correct username and password."""

    # Simulate that the user exists with the given username and password
    mock_cursor.fetchone.return_value = {"password": hashlib.sha256("password123".encode()).hexdigest()}

    # Call the login function and check the result
    result = login(username="testuser", password="password123")
    assert result is True, "Expected login to succeed, but it failed."

def test_login_invalid_password(mock_cursor):
    """Test login with an invalid password."""

    # Simulate that the user exists with the given username but different password
    mock_cursor.fetchone.return_value = {"password": hashlib.sha256("wrongpassword".encode()).hexdigest()}

    # Call the login function and check the result
    result = login(username="testuser", password="password123")
    assert result is False, "Expected login to fail, but it succeeded."

def test_login_nonexistent_user(mock_cursor):
    """Test login with a non-existent username."""

    # Simulate that no user exists with the given username
    mock_cursor.fetchone.return_value = None

    # Call the login function and check the result
    result = login(username="nonexistentuser", password="password123")
    assert result is False, "Expected login to fail, but it succeeded."

######################################################
#
#    Update Password
#
######################################################

def test_update_password_success(mock_cursor):
    """Test successful password update."""

    # Simulate that the user exists with the given username and old password
    mock_cursor.fetchone.return_value = {"password": hashlib.sha256("oldpassword".encode()).hexdigest()}

    # Call the update_password function
    update_password(username="testuser", old_password="oldpassword", new_password="newpassword123")

    expected_query = normalize_whitespace("""
        UPDATE users SET password = ? WHERE username = ?
    """)

    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call (second element of call_args)
    actual_arguments = mock_cursor.execute.call_args_list[1][0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = (hashlib.sha256("newpassword123".encode()).hexdigest(), "testuser")
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_update_password_invalid_old_password(mock_cursor):
    """Test password update with an invalid old password."""

    # Simulate that the user exists with the given username but different old password
    mock_cursor.fetchone.return_value = {"password": hashlib.sha256("wrongoldpassword".encode()).hexdigest()}

    # Expect ValueError when handling invalid old password
    with pytest.raises(ValueError, match="Invalid username or old password"):
        update_password(username="testuser", old_password="oldpassword", new_password="newpassword123")

def test_update_password_nonexistent_user(mock_cursor):
    """Test password update with a non-existent username."""

    # Simulate that no user exists with the given username
    mock_cursor.fetchone.return_value = None

    # Expect ValueError when handling non-existent username
    with pytest.raises(ValueError, match="Invalid username or old password"):
        update_password(username="nonexistentuser", old_password="oldpassword", new_password="newpassword123")