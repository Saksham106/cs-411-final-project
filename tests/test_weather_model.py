import pytest
import json
import requests
from unittest.mock import patch, mock_open
from models.weather_model import (
    fetch_weather_data, 
    write_data_to_json_file,
    load_weather_data,
    get_current_conditions,
    get_week_average_temp,
    get_max_temp_day,
    get_min_temp_day,
    get_highest_precip_day
)




# Mocking requests.get for fetch_weather_data
@patch("weather_model.requests.get")
def test_fetch_weather_data_success(mock_get):
    """Test successful fetching of weather data."""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"city": "TestCity", "currentConditions": {"temp": 70}}

    result = fetch_weather_data("TestCity")
    assert result == {"city": "TestCity", "currentConditions": {"temp": 70}}

@patch("weather_model.requests.get")
def test_fetch_weather_data_http_error(mock_get):
    """Test fetching weather data with an HTTP error."""
    mock_get.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Client Error")

    with pytest.raises(ValueError, match="HTTP error occurred:"):
        fetch_weather_data("InvalidCity")

@patch("weather_model.requests.get")
def test_fetch_weather_data_generic_error(mock_get):
    """Test fetching weather data with a generic error."""
    mock_get.side_effect = Exception("Network issue")

    with pytest.raises(ValueError, match="An error occurred:"):
        fetch_weather_data("TestCity")

# Mocking file handling for write_data_to_json_file
@patch("builtins.open", new_callable=mock_open)
def test_write_data_to_json_file(mock_file):
    """Test writing weather data to a JSON file."""
    data = {"city": "TestCity", "currentConditions": {"temp": 70}}
    write_data_to_json_file(data, "weather_data.json")

    # Ensure the file was opened and written to
    mock_file.assert_called_once_with("weather_data.json", "w")
    mock_file().write.assert_called_once_with(json.dumps(data, indent=4))

# Mocking file reading and existence for load_weather_data
@patch("os.path.exists", return_value=True)
@patch("builtins.open", new_callable=mock_open, read_data='{"city": "TestCity", "currentConditions": {"temp": 70}}')
def test_load_weather_data_from_file(mock_file, mock_exists):
    """Test loading weather data from an existing JSON file."""
    result = load_weather_data("TestCity")
    assert result == {"city": "TestCity", "currentConditions": {"temp": 70}}

@patch("os.path.exists", return_value=False)
@patch("weather_model.fetch_weather_data", return_value={"city": "TestCity", "currentConditions": {"temp": 70}})
@patch("weather_model.write_data_to_json_file")
def test_load_weather_data_fallback_to_api(mock_write, mock_fetch, mock_exists):
    """Test loading weather data by falling back to the API."""
    result = load_weather_data("TestCity")
    assert result == {"city": "TestCity", "currentConditions": {"temp": 70}}
    mock_fetch.assert_called_once_with("TestCity")
    mock_write.assert_called_once()

@patch("os.path.exists", return_value=True)
@patch("builtins.open", new_callable=mock_open, read_data="Invalid JSON")
def test_load_weather_data_invalid_file(mock_file, mock_exists):
    """Test handling of invalid JSON data in the file."""
    with pytest.raises(json.JSONDecodeError):
        load_weather_data("TestCity")

@patch("weather_model.load_weather_data", return_value={"currentConditions": {"temp": 70, "humidity": 50}})
def test_get_current_conditions(mock_load):
    """Test getting current weather conditions for a city."""
    result = get_current_conditions("TestCity")
    assert result == {"temp": 70, "humidity": 50}

@patch("weather_model.load_weather_data", return_value={})
def test_get_current_conditions_missing(mock_load):
    """Test handling missing currentConditions in weather data."""
    result = get_current_conditions("TestCity")
    assert result == {}  # Function should return an empty dictionary

# Mock data for weather days
mock_weather_data = {
    "days": [
        {"temp": 70, "tempmax": 75, "tempmin": 65, "precipprob": 10},
        {"temp": 68, "tempmax": 72, "tempmin": 64, "precipprob": 20},
        {"temp": 73, "tempmax": 80, "tempmin": 70, "precipprob": 30},
    ]
}

@patch("weather_model.load_weather_data", return_value=mock_weather_data)
def test_get_week_average_temp(mock_load):
    """Test calculating the weekly average temperature."""
    result = get_week_average_temp("TestCity")
    assert result == (70 + 68 + 73) / 3  # Average temperature

@patch("weather_model.load_weather_data", return_value={"days": []})
def test_get_week_average_temp_no_days(mock_load):
    """Test calculating the weekly average temperature when no days data is available."""
    with pytest.raises(ValueError, match="No day data available"):
        get_week_average_temp("TestCity")

@patch("weather_model.load_weather_data", return_value=mock_weather_data)
def test_get_max_temp_day(mock_load):
    """Test determining the day with the highest maximum temperature."""
    result = get_max_temp_day("TestCity")
    assert result == {"temp": 73, "tempmax": 80, "tempmin": 70, "precipprob": 30}

@patch("weather_model.load_weather_data", return_value={"days": []})
def test_get_max_temp_day_no_days(mock_load):
    """Test determining the day with the highest max temperature when no days data is available."""
    with pytest.raises(ValueError, match="No day data available"):
        get_max_temp_day("TestCity")

@patch("weather_model.load_weather_data", return_value=mock_weather_data)
def test_get_min_temp_day(mock_load):
    """Test determining the day with the lowest minimum temperature."""
    result = get_min_temp_day("TestCity")
    assert result == {"temp": 70, "tempmax": 75, "tempmin": 65, "precipprob": 10}

@patch("weather_model.load_weather_data", return_value={"days": []})
def test_get_min_temp_day_no_days(mock_load):
    """Test determining the day with the lowest min temperature when no days data is available."""
    with pytest.raises(ValueError, match="No day data available"):
        get_min_temp_day("TestCity")

@patch("weather_model.load_weather_data", return_value=mock_weather_data)
def test_get_highest_precip_day(mock_load):
    """Test determining the day with the highest precipitation probability."""
    result = get_highest_precip_day("TestCity")
    assert result == {"temp": 73, "temp
