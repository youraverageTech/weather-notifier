# Weather Notifier Project

A sophisticated Apache Airflow-based weather monitoring system that fetches real-time weather data from the OpenWeather API, detects adverse weather conditions, and sends email notifications to alert users about rain, drizzle, and thunderstorms.

## Features

- **Real-time Weather Monitoring**: Fetches current weather data for multiple locations using the OpenWeather API
- **Adverse Weather Detection**: Automatically detects and alerts on rain, drizzle, and thunderstorm conditions
- **Smart Alerting**: Sends email notifications only when weather conditions transition to adverse states (avoiding duplicate alerts)
- **State Management**: Tracks weather state changes per location to differentiate between new alerts and continued conditions
- **Multi-location Support**: Monitor multiple cities or coordinates simultaneously
- **Email Notifications**: Sends formatted HTML emails with detailed weather information
- **Containerized**: Runs in Docker for consistent deployment across environments
- **Airflow Orchestration**: Uses Apache Airflow for scheduling and orchestrating weather checks

## Project Structure

```
weather-notifier/
├── dags/
│   ├── main.py              # Entry point for weather monitoring logic
│   └── weather_notifier.py  # Airflow DAG definition
├── include/
│   ├── weather.py           # OpenWeather API integration
│   ├── email_notifier.py    # Email sending functionality
│   ├── state.py             # Weather state management
│   ├── logger.py            # Logging setup
│   ├── weather_history.py   # Historical weather data tracking
│   ├── get_locations_lat_lon.py  # Location coordinate fetcher
│   └── data/
│       ├── state.json       # Persisted weather state
│       └── weather_locations.csv  # Monitored locations list
├── tests/                   # Test suite
├── logs/                    # Application logs
├── Dockerfile              # Docker container configuration
├── docker-compose.override.yml  # Compose overrides
├── airflow_settings.yaml    # Airflow configuration
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Prerequisites

- Python 3.8 or higher
- Docker and Docker Compose (for containerized deployment)
- OpenWeather API key (free tier available at https://openweathermap.org/api)
- Gmail account with App Password (for email notifications)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd weather-notifier
```

### 2. Set Up Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# OpenWeather API Configuration
WEATHER_API_KEY=your_openweather_api_key_here

# Email Configuration
SENDER_EMAIL=your_gmail_address@gmail.com
APP_PASSWORD=your_gmail_app_password_here
RECEIVER_EMAIL=recipient_email@example.com

# Optional: Logging and other settings
LOG_LEVEL=INFO
```

**Note**: For Gmail, you need to:
1. Enable 2-Factor Authentication on your Google Account
2. Generate an App Password at https://myaccount.google.com/apppasswords
3. Use the generated 16-character password in `APP_PASSWORD`

### 3. Set Up Location Data

Create a CSV file at `include/data/weather_locations.csv` with the following format:

```csv
name,latitude,longitude
New York,40.7128,-74.0060
London,51.5074,-0.1278
Tokyo,35.6762,139.7674
```

Or run the location fetcher:

```bash
python include/get_locations_lat_lon.py
```

### 4. Install Dependencies (Local Development)

```bash
# Create a virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 5. Docker Setup

Build and run the application using Docker Compose:

```bash
# Build the container
docker-compose build

# Start the Airflow environment
docker-compose up -d

# Access the Airflow UI at http://localhost:8080
```

## Usage

### Running Locally

```bash
# Make sure your virtual environment is activated and .env is configured
python dags/main.py
```

### Running with Airflow

The DAG `weather_notifier` is automatically available in Airflow once deployed:

1. Navigate to the Airflow Web UI (http://localhost:8080)
2. Find the `weather_notifier` DAG
3. Enable the DAG using the toggle
4. Trigger it manually or let it run on schedule

### Configuration

**Monitoring Frequency**: Edit the schedule in [dags/weather_notifier.py](dags/weather_notifier.py)

**Adverse Weather Conditions**: Modify the `ADVERSE_CONDITIONS` list in [dags/main.py](dags/main.py):

```python
ADVERSE_CONDITIONS = ["Rain", "Drizzle", "Thunderstorm"]
```

## Key Components

### Weather Fetching ([include/weather.py](include/weather.py))
Handles all API requests to OpenWeather, manages parameters, and parses responses.

### State Management ([include/state.py](include/state.py))
Tracks weather conditions per location to determine if an alert should be sent (transitions from clear to adverse conditions).

### Email Notifications ([include/email_notifier.py](include/email_notifier.py))
Formats weather data into HTML emails and sends via Gmail SMTP.

### Logging ([include/logger.py](include/logger.py))
Provides centralized logging for debugging and monitoring.

## Development

### Running Tests

```bash
python -m pytest tests/
```

### Debugging

Enable debug logging by setting in `.env`:

```env
LOG_LEVEL=DEBUG
```

## Dependencies

- **apache-airflow-providers-postgres**: PostgreSQL integration for Airflow
- **pandas**: Data manipulation and analysis
- **requests**: HTTP library for API calls
- **python-dotenv**: Environment variable management
- **pyarrow**: Data serialization

See [requirements.txt](requirements.txt) for complete dependency list.

## Troubleshooting

### Email Not Sending
- Verify Gmail App Password is correct
- Check that 2FA is enabled on Gmail account
- Ensure sender/receiver email addresses are correct in `.env`

### API Rate Limiting
- Free tier allows 60 calls per minute
- Increase interval between checks if hitting limits

### State File Issues
- If state tracking behaves unexpectedly, delete `include/data/state.json` to reset
- A new state file will be created on next run

## Future Enhancements

- [ ] Database integration for historical data storage
- [ ] Web dashboard for weather visualization
- [ ] SMS notifications in addition to email
- [ ] Customizable alert thresholds (temperature, wind speed)
- [ ] Multiple recipient support
- [ ] Weather prediction-based alerts

## License

[Add your license information here]

## Contact

For questions or issues, please open a GitHub issue or contact the project maintainers.

## Changelog

### v1.0.0
- Initial release with basic weather monitoring and email alerts

