import pandas as pd
import os


dir = "data"
file_data = os.path.join(dir, "weather_history")

def weather_history(weather_data: list):
    if not weather_data:
        print("No weather data to save.")

        return
    df = pd.DataFrame(weather_data)
    if not os.path.exists(file_data):
        df.to_csv(file_data, index=False)
    else:
        df.to_csv(file_data, mode='a', header=False, index=False)