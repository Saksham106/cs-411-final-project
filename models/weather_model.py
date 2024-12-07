import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def fetch_weather_data(city: str) -> dict:
    """
    Fetch weather data for a given city from the Visual Crossing API.

    Args:
        city (str): The city name for which to fetch weather data.

    Returns:
        dict: A dictionary containing weather data for the specified city.
    """
    weather_api_key = os.getenv('WEATHER_API_KEY')
    api_url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}/next7days?unitGroup=us&include=days%2Ccurrent%2Cevents&key={weather_api_key}&contentType=json"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        raise ValueError(f"HTTP error occurred: {http_err}")
    except Exception as err:
        raise ValueError(f"An error occurred: {err}")

def write_data_to_json_file(data: dict, filename: str) -> None:
    """
    Write data to a JSON file.

    Args:
        data (dict): The data to write to a file.
        filename (str): The name of the file where data will be written.

    Returns:
        None
    """
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def load_weather_data(city: str) -> dict:
    """
    Load weather data from a file or fetch it from the API if the file does not exist.

    Args:
        city (str): The city for which to load weather data.

    Returns:
        dict: The weather data dictionary loaded from file or retrieved from API.
    """
    filename = 'weather_data.json'
    if not os.path.exists(filename) or os.path.getsize(filename) == 0:
        data = fetch_weather_data(city)
        write_data_to_json_file(data, filename)
    else:
        with open(filename, 'r') as f:
            data = json.load(f)
    return data

def get_current_conditions(city: str) -> dict:
    """
    Get the current weather conditions for a given city.

    Args:
        city (str): The city name for which to fetch current weather conditions.

    Returns:
        dict: A dictionary containing the current weather conditions.
    """
    data = load_weather_data(city)
    return data.get('currentConditions', {})

def get_week_average_temp(city: str) -> float:
    """
    Calculate the weekly average temperature for a given city.

    Args:
        city (str): The city name for which to calculate the weekly average temperature.

    Returns:
        float: The weekly average temperature.
    """
    data = load_weather_data(city)
    days = data.get('days', [])
    if not days:
        raise ValueError("No day data available")

    total_temp = sum(day.get('temp', 0) for day in days)
    return total_temp / len(days)

def get_max_temp_day(city: str) -> dict:
    """
    Determine the day with the highest maximum temperature for a given city.

    Args:
        city (str): The city name for which to determine the day with the highest maximum temperature.

    Returns:
        dict: A dictionary representing the day with the highest max temperature.
    """
    data = load_weather_data(city)
    days = data.get('days', [])
    if not days:
        raise ValueError("No day data available")

    return max(days, key=lambda d: d.get('tempmax', float('-inf')))

def get_min_temp_day(city: str) -> dict:
    """
    Determine the day with the lowest minimum temperature for a given city.

    Args:
        city (str): The city name for which to determine the day with the lowest minimum temperature.

    Returns:
        dict: A dictionary representing the day with the lowest min temperature.
    """
    data = load_weather_data(city)
    days = data.get('days', [])
    if not days:
        raise ValueError("No day data available")

    return min(days, key=lambda d: d.get('tempmin', float('inf')))

def get_highest_precip_day(city: str) -> dict:
    """
    Determine the day with the highest precipitation probability for a given city.

    Args:
        city (str): The city name for which to determine the day with the highest precipitation probability.

    Returns:
        dict: A dictionary representing the day with the highest precipitation probability.
    """
    data = load_weather_data(city)
    days = data.get('days', [])
    if not days:
        raise ValueError("No day data available")

    return max(days, key=lambda d: d.get('precipprob', 0))