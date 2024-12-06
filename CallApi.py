from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, Flask!"

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