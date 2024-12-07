from flask import Flask, jsonify, make_response, Response, request
import requests
from dotenv import load_dotenv
import os
import hashlib
import sqlite3

from user_model import create_account, login, update_password

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, Flask!"


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
    

@app.route('/api/<city>', methods=['GET'])
def call_api(city):
    weather_api_key = os.getenv('WEATHER_API_KEY')
    api_url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}/next7days?unitGroup=us&include=days%2Ccurrent%2Cevents&key={weather_api_key}&contentType=json"
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        return jsonify({"error": str(http_err)}), response.status_code
    except Exception as err:
        return jsonify({"error": str(err)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)