"""
get_locations_lat_lon.py
Module for fetching geographic coordinates (latitude and longitude) for specified locations.
Uses the OpenWeather Geocoding API to convert location names to coordinates and stores results in CSV.
"""

# Import necessery libraries for the script
import requests
import pandas as pd
import os
from dotenv import load_dotenv
from include.logger import setup_logger, get_logger

# Load environment variables from .env file
load_dotenv()
setup_logger()
logger = get_logger()

# Retrieve OpenWeather API key from environment variables for authentication
api_key = os.getenv("WEATHER_API_KEY")
# Define list of location names to fetch coordinates for (Jakarta districts)
locations = ["Jakarta Barat", "Jakarta Pusat", "Jakarta Selatan", "Jakarta Timur", "Jakarta Utara"]
# Set the base URL for OpenWeather Geocoding API endpoint
base_url = "https://api.openweathermap.org/geo/1.0/direct"
# path save file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
FILE_SAVE = os.path.join(DATA_DIR, "weather_locations.csv")

def get_coordinates(locations):
    """
    Fetches geographic coordinates (latitude and longitude) for given location names.
    Calls the OpenWeather Geocoding API for each location and saves results to CSV file.
    
    Parameters:
        locations (list): List of location names to fetch coordinates for
    
    Returns:
        list: List of dictionaries containing location name, latitude, and longitude
              Each dictionary has keys: 'name', 'latitude', 'longitude'
    """
    logger.info("Starting fetch locations informations...")
    # Initialize empty list to store location data with coordinates
    weather_locations = []
    # Iterate through each location name
    for location in locations:
        # Build API request parameters for geocoding query
        params = {
            "q": location,  # Location name to search for
            "limit": 1,  # Limit results to single best match
            "appid": api_key  # OpenWeather API authentication key
        }
        # Make HTTP GET request to geocoding API
        response = requests.get(base_url, params=params)
        try:
            # Check if the API request was successful (status code 200)
            if response.status_code == 200:
                # Parse JSON response from the API
                data = response.json()
                # Verify that response contains location data
                if data:
                    # Extract latitude coordinate from first result
                    lat = data[0]['lat']
                    # Extract longitude coordinate from first result
                    lon = data[0]['lon']
                    # Extract local name in Indonesian language
                    loc = data[0]['local_names']['id']
                    # Add extracted location data to the list
                    weather_locations.append({
                        'name': loc,  # Store location name
                        'latitude': lat,  # Store latitude
                        'longitude': lon  # Store longitude
                    })
            # Catch HTTP errors that might occur during API calls
        except requests.HTTPError as http_err:
            # Print error message if API call fails for a location
            logger.error(f"HTTP error occurred for {location}: {http_err}")
    
    # Create pandas DataFrame from the collected location data
    df = pd.DataFrame(weather_locations)
    # Export the location data to CSV file for later use
    df.to_csv(FILE_SAVE, index=False)
    logger.info("Process complete. Location to get {} cities".format(len(df)))