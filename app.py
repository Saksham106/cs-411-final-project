"""Simple Flask weather API.

This module provides a Flask application that fetches and serves weather data
using the Visual Crossing API.

Example:
    Run the server:
        build the docker image: $ docker build -t flask-weather-api .
        run the docker container: $ docker run -p <ports> flask-weather-api

    Then call:
        $ then you can call it at http://127.0.0.1:5002/api/<city>

Attributes:
    module_level_variable1 (str): The weather API key from environment vars.

"""

from flask import Flask, jsonify, make_response, Response, request
import os
import hashlib
import sqlite3
import json
from dotenv import load_dotenv

from models.user_model import create_account, login, update_password
from models.weather_model import (
    fetch_weather_data,
    get_current_conditions,
    get_week_average_temp,
    get_max_temp_day,
    get_min_temp_day,
    get_highest_precip_day
)

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

@app.route('/')
def home():
    """Example function with types documented in the docstring.

    Returns:
        str: A simple greeting message.
    """
    return "Hello, Flask!"

@app.route('/api/<city>', methods=['GET'])
def call_api(city):
    """Example function with types documented in the docstring.

    Args:
        city (str): The city name for which to fetch weather data.

    Returns:
        dict: A dictionary containing weather data for the specified city,
        or a JSON error response.
    """
    try:
        response_data = fetch_weather_data(city)
        return jsonify(response_data)
    except ValueError as err:
        return jsonify({"error": str(err)}), 500

@app.route('/api/<city>/current-conditions', methods=['GET'])
def current_conditions(city):
    """Get the current weather conditions for a given city."""
    try:
        current_conditions = get_current_conditions(city)
        return jsonify(current_conditions)
    except ValueError as err:
        return jsonify({"error": str(err)}), 500

@app.route('/api/<city>/week-average-temp', methods=['GET'])
def week_average_temp(city):
    """Calculate the weekly average temperature for a given city."""
    try:
        average_temp = get_week_average_temp(city)
        return jsonify({"week_average_temp": average_temp})
    except ValueError as err:
        return jsonify({"error": str(err)}), 500

@app.route('/api/<city>/max-temp-day', methods=['GET'])
def max_temp_day(city):
    """Determine the day with the highest maximum temperature for a given city."""
    try:
        max_day = get_max_temp_day(city)
        return jsonify(max_day)
    except ValueError as err:
        return jsonify({"error": str(err)}), 500

@app.route('/api/<city>/min-temp-day', methods=['GET'])
def min_temp_day(city):
    """Determine the day with the lowest minimum temperature for a given city."""
    try:
        min_day = get_min_temp_day(city)
        return jsonify(min_day)
    except ValueError as err:
        return jsonify({"error": str(err)}), 500

@app.route('/api/<city>/highest-precip-day', methods=['GET'])
def highest_precip_day(city):
    """Determine the day with the highest precipitation probability for a given city."""
    try:
        highest_precip_day = get_highest_precip_day(city)
        return jsonify(highest_precip_day)
    except ValueError as err:
        return jsonify({"error": str(err)}), 500

@app.route('/api/health', methods=['GET'])
def healthcheck() -> Response:
    """
    Health check route to verify the service is running.

    Returns:
        JSON response indicating the health status of the service.
    """
    app.logger.info('Health check')
    response = make_response(jsonify({"status": "healthy"}), 200)
    app.logger.debug(f"Health Check Response: {response.get_data(as_text=True)}") 
    return response  

@app.route('/api/create-account', methods=['POST'])
def create_account_route() -> Response:
    """
    Create a new account.

    Returns:
        JSON response indicating the account was created.
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    try:
        create_account(username, password)
        return jsonify({"message": "Account created successfully"}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login_route() -> Response:
    """
    Login to an existing account.

    Returns:
        JSON response indicating whether the login was successful or not.
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    try:
        if login(username, password):
            return jsonify({"message": "Login successful"}), 200
        else:
            return jsonify({"error": "Invalid username or password"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/update-password', methods=['POST'])
def update_password_route() -> Response:
    """
    Update the password for an existing account.

    Returns:
        JSON response indicating whether the password update was successful or not.
    """
    data = request.get_json()
    username = data.get('username')
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not username or not old_password or not new_password:
        return jsonify({"error": "Username, old password, and new password are required"}), 400

    try:
        update_password(username, old_password, new_password)
        return jsonify({"message": "Password updated successfully"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)