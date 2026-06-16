"""
checker.py
Module for analyzing weather data from the OpenWeather API and identifying adverse weather conditions.
Filters weather data to detect rainy, drizzly, or thunderstorm conditions for notification purposes.
"""

# Import logging utilities for tracking application activity and debugging
from scripts.logger import setup_logger, get_logger

# Initialize and configure the logging system for activity tracking
setup_logger()
# Get a logger instance for this module
logger = get_logger()

# Define list of weather conditions that trigger notifications to the user
# These conditions indicate adverse weather that may require user notification
ADVERSE_CONDITIONS = ["Rain", "Drizzle", "Thunderstorm"]

def check_weather_conditions(weather_data):
    """
    Analyzes weather data to identify adverse weather conditions.
    
    Parameters:
        weather_data (list): List of dictionaries containing weather information with 'weather_conditions' key
    
    Returns:
        tuple: (bool, list) - Boolean indicating if adverse conditions found, and list of matching weather records
    """
    
    # log the start of the checking process
    logger.info("Starting checking data process.")
    
    # Checking weather data
    if not weather_data:
        logger.warning("No weather data provided.")
        return False, []

    # Create list of data that matching the condition
    matched = [
        data for data in weather_data
        if data.get("weather_conditions") in ADVERSE_CONDITIONS
    ]

    if matched:
        logger.info(f"{len(matched)} adverse weather condition(s) found.")
    else:
        logger.info("No adverse weather conditions found.")

    return bool(matched), matched

def is_adverse_condition(data):
    return 