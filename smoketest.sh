#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5002/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done


###############################################
#
# Health checks
#
###############################################

check_health() {
  echo "Checking health status..."
  response=$(curl -s -X GET "$BASE_URL/health")
  echo "Response: $response"
  if echo "$response" | jq -e '.status == "healthy"' > /dev/null 2>&1; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}


##########################################################
#
# Weather Data Management
#
##########################################################

fetch_weather() {
  city=$1
  echo "Fetching weather data for city ($city)..."
  response=$(curl -s -X GET "$BASE_URL/$city")
  echo "Response: $response"
  echo "$response" | grep -q '"error"' && {
    echo "Failed to fetch weather data for $city."
    exit 1
  }
}

get_current_conditions() {
  city=$1
  echo "Fetching current weather conditions for city ($city)..."
  response=$(curl -s -X GET "$BASE_URL/$city/current-conditions")
  echo "Response: $response"
  echo "$response" | grep -q '"temp"' || {
    echo "Failed to fetch current conditions for $city."
    exit 1
  }
}

get_weekly_average() {
  city=$1
  echo "Fetching weekly average temperature for city ($city)..."
  response=$(curl -s -X GET "$BASE_URL/$city/week-average-temp")
  echo "Response: $response"
  echo "$response" | grep -q '"week_average_temp"' || {
    echo "Failed to fetch weekly average temperature for $city."
    exit 1
  }
}

get_max_temp_day() {
  city=$1
  echo "Fetching the day with the highest temperature for city ($city)..."
  response=$(curl -s -X GET "$BASE_URL/$city/max-temp-day")
  echo "Response: $response"
  echo "$response" | grep -q '"tempmax"' || {
    echo "Failed to fetch max temperature day for $city."
    exit 1
  }
}

get_min_temp_day() {
  city=$1
  echo "Fetching the day with the lowest temperature for city ($city)..."
  response=$(curl -s -X GET "$BASE_URL/$city/min-temp-day")
  echo "Response: $response"
  echo "$response" | grep -q '"tempmin"' || {
    echo "Failed to fetch min temperature day for $city."
    exit 1
  }
}

get_highest_precip_day() {
  city=$1
  echo "Fetching the day with the highest precipitation for city ($city)..."
  response=$(curl -s -X GET "$BASE_URL/$city/highest-precip-day")
  echo "Response: $response"
  echo "$response" | grep -q '"precipprob"' || {
    echo "Failed to fetch highest precipitation day for $city."
    exit 1
  }
}


##########################################################
#
# User Account Management
#
##########################################################

create_account() {
  username=$1
  password=$2
  echo "Creating user account ($username)..."
  response=$(curl -s -X POST "$BASE_URL/create-account" -H "Content-Type: application/json" \
    -d "{\"username\": \"$username\", \"password\": \"$password\"}")
  echo "Response: $response"
  message=$(echo "$response" | jq -r '.message')
  error=$(echo "$response" | jq -r '.error')
  if [ "$message" == "Account created successfully" ]; then
    echo "Account created successfully for $username."
  elif [ "$error" == "Username '$username' already exists" ]; then
    echo "Username '$username' already exists. Skipping account creation."
  else
    echo "Failed to create account for $username."
    exit 1
  fi
}

login_user() {
  username=$1
  password=$2
  echo "Logging in user ($username)..."
  response=$(curl -s -X POST "$BASE_URL/login" -H "Content-Type: application/json" \
    -d "{\"username\": \"$username\", \"password\": \"$password\"}")
  echo "Response: $response"
  message=$(echo "$response" | jq -r '.message')
  if [ "$message" == "Login successful" ]; then
    echo "Login successful for $username."
  else
    echo "Failed to log in user $username."
    exit 1
  fi
}

update_password() {
  username=$1
  old_password=$2
  new_password=$3
  echo "Updating password for user ($username)..."
  response=$(curl -s -X POST "$BASE_URL/update-password" -H "Content-Type: application/json" \
    -d "{\"username\": \"$username\", \"old_password\": \"$old_password\", \"new_password\": \"$new_password\"}")
  echo "Response: $response"
  message=$(echo "$response" | jq -r '.message')
  if [ "$message" == "Password updated successfully" ]; then
    echo "Password updated successfully for $username."
  else
    echo "Failed to update password for $username."
    exit 1
  fi
}


############################################################
#
# Test Sequence
#
############################################################

CITY="boston"

# Health checks
check_health

# Weather data tests
fetch_weather "$CITY"
get_current_conditions "$CITY"
get_weekly_average "$CITY"
get_max_temp_day "$CITY"
get_min_temp_day "$CITY"
get_highest_precip_day "$CITY"

# User account tests
create_account "testuser" "password123"
login_user "testuser" "password123"
update_password "testuser" "password123" "newpassword123"

echo "All tests passed successfully!"