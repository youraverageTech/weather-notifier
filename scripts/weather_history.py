"""
Weather history module for the weather notifier application.

This module handles storing and managing historical weather data by appending
weather records to a CSV file. It provides functionality to save weather data
in a persistent format for later analysis and tracking.
"""

import pandas as pd
import os

# Directory where weather history data is stored
dir = "data"
# Full path to the weather history CSV file
file_data = os.path.join(dir, "weather_history")

def weather_history(weather_data: list):
    """
    Save weather data to a CSV file.
    
    Appends weather records to the weather_history CSV file. Creates the file
    if it doesn't exist, otherwise appends new records to the existing file.
    
    Args:
        weather_data (list): A list of dictionaries containing weather data.
                           Each dictionary should contain weather information
                           (e.g., city, temperature, rain status, timestamp).
    
    Returns:
        None
        
    Note:
        - Does nothing if weather_data is empty.
        - Creates CSV file with headers on first write.
        - Appends data without headers on subsequent writes.
    """
    if not weather_data:
        print("No weather data to save.")

        return
    df = pd.DataFrame(weather_data)
    if not os.path.exists(file_data):
        df.to_csv(file_data, index=False)
    else:
        df.to_csv(file_data, mode='a', header=False, index=False)