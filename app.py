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
import requests
from dotenv import load_dotenv
import os
import hashlib
import sqlite3
import json

from models.user_model import create_account, login, update_password

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
    weather_api_key = os.getenv('WEATHER_API_KEY')
    api_url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}/next7days?unitGroup=us&include=days%2Ccurrent%2Cevents&key={weather_api_key}&contentType=json"
    try:
        response = requests.get(api_url)
        response.raise_for_status()

        response_data = response.json()
        write_data_to_json_file(response_data, 'weather_data.json')
        return response_data
    except requests.exceptions.HTTPError as http_err:
        return jsonify({"error": str(http_err)}), response.status_code
    except Exception as err:
        return jsonify({"error": str(err)}), 500

def write_data_to_json_file(data, filename):
    """Example function with types documented in the docstring.

    Args:
        data (dict): The data to write to a file.
        filename (str): The name of the file where data will be written.

    Returns:
        None
    """
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def load_weather_data(city):
    """Example function with types documented in the docstring.

    Args:
        city (str): The city for which to load weather data.

    Returns:
        dict: The weather data dictionary loaded from file or retrieved from API.
    """
    filename = 'weather_data.json'
    if not os.path.exists(filename) or os.path.getsize(filename) == 0:
        call_api(city)
    with open(filename, 'r') as f:
        data = json.load(f)
    return data

@app.route('/api/<city>/current-conditions', methods=['GET'])
def get_current_conditions(city):
    """Example function with types documented in the docstring.

    Args:
        city (str): The city for which to retrieve current weather conditions.

    Returns:
        dict: A dictionary containing the current weather conditions.
    """
    data = load_weather_data(city)
    current_conditions = data.get('currentConditions', {})
    return jsonify(current_conditions)

@app.route('/api/<city>/week-average-temp', methods=['GET'])
def get_week_average_temp(city):
    """Example function with types documented in the docstring.

    Args:
        city (str): The city for which to calculate the weekly average temperature.

    Returns:
        dict: A dictionary with the key 'week_average_temp' containing the average temperature.
    """
    data = load_weather_data(city)
    days = data.get('days', [])
    if not days:
        return jsonify({"error": "No day data available"}), 404

    temps = [day.get('temp', 0) for day in days if 'temp' in day]
    if not temps:
        return jsonify({"error": "No temperature data available"}), 404

    avg_temp = sum(temps) / len(temps)
    return jsonify({"week_average_temp": avg_temp})

@app.route('/api/<city>/max-temp-day', methods=['GET'])
def get_max_temp_day(city):
    """Example function with types documented in the docstring.

    Args:
        city (str): The city for which to determine the day with the highest maximum temperature.

    Returns:
        dict: A dictionary representing the day with the highest max temperature.
    """
    data = load_weather_data(city)
    days = data.get('days', [])
    if not days:
        return jsonify({"error": "No day data available"}), 404

    max_day = max(days, key=lambda d: d.get('tempmax', float('-inf')))
    return jsonify(max_day)

@app.route('/api/<city>/min-temp-day', methods=['GET'])
def get_min_temp_day(city):
    """Example function with types documented in the docstring.

    Args:
        city (str): The city for which to determine the day with the lowest minimum temperature.

    Returns:
        dict: A dictionary representing the day with the lowest min temperature.
    """
    data = load_weather_data(city)
    days = data.get('days', [])
    if not days:
        return jsonify({"error": "No day data available"}), 404

    min_day = min(days, key=lambda d: d.get('tempmin', float('inf')))
    return jsonify(min_day)

@app.route('/api/<city>/highest-precip-day', methods=['GET'])
def get_highest_precip_day(city):
    """Example function with types documented in the docstring.

    Args:
        city (str): The city for which to determine the day with the highest precipitation probability.

    Returns:
        dict: A dictionary representing the day with the highest precipitation probability.
    """
    data = load_weather_data(city)
    days = data.get('days', [])
    if not days:
        return jsonify({"error": "No day data available"}), 404

    highest_precip_day = max(days, key=lambda d: d.get('precipprob', 0))
    return jsonify(highest_precip_day)


@app.route('/api/health', methods=['GET'])
def healthcheck() -> Response:
    """
    Health check route to verify the service is running.

    Returns:
        JSON response indicating the health status of the service.
    """
    app.logger.info('Health check')
    return make_response(jsonify({'status': 'healthy'}), 200)


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