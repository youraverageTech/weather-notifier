"""
State management module for the weather notifier application.

This module handles loading, saving, and updating weather state conditions 
for different cities. It maintains state information such as current rain status,
last check time, and when alerts were sent.
"""

import json
import os
from scripts.logger import setup_logger, get_logger
from datetime import datetime

setup_logger()
logger = get_logger()

# Directory and file path for storing state data
state_dir = "data"
file_state = os.path.join(state_dir, "state.json")

def load_state():
    """
    Load weather state from the state.json file.
    
    Returns:
        dict: A dictionary containing the state data for all cities.
              Returns an empty dict if file doesn't exist or is corrupt.
    """
    if not os.path.exists(file_state):
        logger.info("State file not found, starting with empty state.")
        return {}
    try:
        with open(file_state, 'r') as f:
            state = json.load(f)
            logger.info("State conditions loaded successfully!")

            return state
        
    except json.JSONDecodeError:
        logger.warning("State file is corrupt, starting with empty state.")

        return {}

def save_state(state):
    """
    Save the current state to the state.json file.
    
    Args:
        state (dict): The state dictionary to save to disk.
        
    Returns:
        None
        
    Note:
        Logs error if save operation fails due to OS errors.
    """
    try:
        with open(file_state, 'w') as f:
            json.dump(state, f, indent= 4)
            logger.info("State saved successfully")
    except OSError as e:
        logger.error(f"Failed to save state: {e}")

def get_city_state(state, city):
    """
    Retrieve the weather state for a specific city.
    
    Args:
        state (dict): The overall state dictionary.
        city (str): The city name to retrieve state for.
        
    Returns:
        dict: A dictionary containing:
              - is_raining (bool): Whether it's currently raining in the city.
              - last_checked (str): Timestamp of last weather check.
              - alert_sent_at (str): Timestamp of when the last alert was sent.
              
    Note:
        Returns default state with all values set to False/None if city doesn't exist.
    """
    if city not in state:
        logger.info(f"There are no state weather condition for the {city}")
        return {
            "is_raining": False,
            "last_checked": None,
            "alert_sent_at": None
        }
    logger.info("State found for {}".format(city))

    return state[city]

def update_city_state(state, city, is_raining):
    """
    Update the weather state for a specific city.
    
    Args:
        state (dict): The overall state dictionary.
        city (str): The city name to update.
        is_raining (bool): Current rain status for the city.
        
    Returns:
        dict: The updated state dictionary.
        
    Note:
        Updates the is_raining flag and sets last_checked to current timestamp.
    """
    city_state = get_city_state(state, city)
    city_state['is_raining'] = is_raining
    city_state['last_checked'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    state[city] = city_state
    logger.info(f"State updated for {city} - is_raining: {is_raining}")

    return state

def should_send_rain_alert(city_state, is_raining):
    """
    Determine if a rain alert should be sent.
    
    Args:
        city_state (dict): The current state for a city.
        is_raining (bool): Whether it's currently raining.
        
    Returns:
        bool: True if it just started raining (rain detected but wasn't before).
        
    Note:
        Returns True only when transitioning from dry to rainy conditions.
    """
    return is_raining and not city_state["is_raining"]

def has_rain_stopped(city_state, is_raining):
    """
    Determine if rain has stopped in a city.
    
    Args:
        city_state (dict): The current state for a city.
        is_raining (bool): Whether it's currently raining.
        
    Returns:
        bool: True if it was raining but isn't anymore (rain stopped).
        
    Note:
        Returns True only when transitioning from rainy to dry conditions.
    """
    return not is_raining and city_state["is_raining"]

