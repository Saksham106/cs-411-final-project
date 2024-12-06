#!/bin/bash

# Debug: Print environment variables
echo "DB_PATH=$DB_PATH"
echo "SQL_CREATE__USER_TABLE_PATH=$SQL_CREATE__USER_TABLE_PATH"
echo "SQL_CREATE__LOCATION_TABLE_PATH=$SQL_CREATE__LOCATION_TABLE_PATH"

# Ensure the directory for the database exists
DB_DIR=$(dirname "$DB_PATH")
if [ ! -d "$DB_DIR" ]; then
    echo "Creating directory $DB_DIR"
    mkdir -p "$DB_DIR"
fi

# Check if the database file already exists
if [ -f "$DB_PATH" ]; then
    echo "Recreating database at $DB_PATH."
    # Drop and recreate the tables
    sqlite3 "$DB_PATH" < "$SQL_CREATE__USER_TABLE_PATH"
    sqlite3 "$DB_PATH" < "$SQL_CREATE__LOCATION_TABLE_PATH"
    echo "Database recreated successfully."
else
    echo "Creating database at $DB_PATH."
    # Create the database for the first time
    sqlite3 "$DB_PATH" < "$SQL_CREATE__USER_TABLE_PATH"
    sqlite3 "$DB_PATH" < "$SQL_CREATE__LOCATION_TABLE_PATH"
    echo "Database created successfully."
fi