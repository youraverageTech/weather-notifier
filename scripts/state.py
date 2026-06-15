import json
import os
from logger import setup_logger, get_logger
from datetime import datetime

setup_logger()
logger = get_logger()

state_dir = "data"
file_state = os.path.join(state_dir, "state.json")

def load_state():
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
    try:
        with open(file_state, 'w') as f:
            json.dump(state, f, indent= 4)
            logger.info("State saved successfully")
    except OSError as e:
        logger.error(f"Failed to save state: {e}")

def get_city_state(state, city):
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
    city_state = get_city_state(state, city)
    city_state['is_raining'] = is_raining
    city_state['last_checked'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    state[city] = city_state
    logger.info(f"State updated for {city} - is_raining: {is_raining}")

    return state

def should_send_rain_alert(city_state, is_raining):
    return is_raining and not city_state["is_raining"]

def has_rain_stopped(city_state, is_raining):
    return not is_raining and city_state["is_raining"]

