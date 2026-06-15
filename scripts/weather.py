"""
weather.py
Module for fetching weather data from the OpenWeather API.
Retrieves current weather information for specified locations and returns structured data.
"""

# Import necessary libraries for API requests, environment variables, data manipulation, and logging
import requests
import os  
from dotenv import load_dotenv 
import pandas as pd  
from datetime import datetime  
from logger import setup_logger, get_logger  

# Initialize logging system for tracking activity and debugging
setup_logger()
logger = get_logger()


def get_weather_data(locations: pd.DataFrame, api_key: str, base_url: str) -> list: 
    """
    Fetches current weather data from the OpenWeather API for multiple locations.
    Iterates through provided locations, makes API requests, and extracts weather information.

    Parameters:
        locations (pd.DataFrame): DataFrame containing location data with 'latitude', 'longitude', and 'name' columns
        api_key (str): OpenWeather API authentication key
        base_url (str): Base URL for the OpenWeather API endpoint

    Returns:
        list: List of dictionaries containing weather data with keys: location, description, temperature, 
            humidity, wind_speed, weather_conditions, date, and time
    """

    # Log the start of weather data fetching process
    logger.info("Starting to fetch weather data for locations.")
    # Record the start time for performance measurement
    start_time = datetime.now()

    # list initilization for the fetch data
    weather_data = []

    for _, coords in locations.iterrows():
        # Build API request parameters with location coordinates and authentication
        params = {
            "lat": coords['latitude'], 
            "lon": coords['longitude'],  
            "appid": api_key,  
            "units": "metric",  
        }
        # Attempt to fetch weather data from the API
        try:
            response = requests.get(base_url, params=params)
            # Checking API response
            if response.status_code == 200:
                # Parsing the json from API
                data = response.json()
                if data:
                    # Extract weather description from the API response
                    weather_desc = data["weather"][0]["description"]
                    # Extract temperature value in Celsius
                    temp = data["main"]["temp"]
                    # Extract humidity percentage
                    humidity = data["main"]["humidity"]
                    # Extract wind speed in m/s
                    wind_speed = data["wind"]["speed"]
                    # Extract main weather condition
                    weather_conditions = data["weather"][0]["main"]
                    # Add all extracted weather data to the list
                    weather_data.append({
                        "location": coords['name'],  # Store location name
                        "description": weather_desc,  # Store weather description
                        "temperature": temp,  # Store temperature in Celsius
                        "humidity": humidity,  # Store humidity percentage
                        "wind_speed": wind_speed,  # Store wind speed
                        "weather_conditions": weather_conditions,  # Store main weather condition
                        "date": datetime.fromtimestamp(data["dt"]).date(),  # Convert Unix timestamp to date
                        "time": datetime.fromtimestamp(data["dt"]).time()  # Convert Unix timestamp to time
                    })
                else:
                    # Log warning if no data was returned for a location
                    logger.warning(f"No weather data found for {coords['name']}")
        except requests.RequestException as http_err:
            # Catch and log any HTTP or connection errors
            logger.error(f"HTTP error occurred for {coords['name']}: {http_err}")
    
    # Record the end time and calculate total execution time
    end_time = datetime.now()
    # Log completion message with performance metrics
    logger.info("Finished fetching weather data. Time taken: {}".format(end_time - start_time))
    
    return weather_data
        
