#!/bin/bash

# Load the environment variables from .env file
if [ -f .env ]; then
    export $(cat .env | xargs)
fi

# Debug: Print environment variables
echo "CREATE_DB=$CREATE_DB"
echo "DB_PATH=$DB_PATH"
echo "SQL_CREATE__USER_TABLE_PATH=$SQL_CREATE__USER_TABLE_PATH"
echo "SQL_CREATE__LOCATION_TABLE_PATH=$SQL_CREATE__LOCATION_TABLE_PATH"

# Check if CREATE_DB is true, and run the database creation script if so
if [ "$CREATE_DB" = "true" ]; then
    echo "Creating the database..."
    /app/sql/create_db.sh
else
    echo "Skipping database creation."
fi

# Start the Python application
exec python app.py