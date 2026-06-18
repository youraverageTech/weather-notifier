# Automated Weather Notifier Pipeline

Automated weather monitoring pipeline that checks real-time weather conditions for multiple cities, detects adverse weather (rain, drizzle, thunderstorm), avoids duplicate alerts through state-based transition detection, and sends email notifications. Built with Apache Airflow (via Astro CLI), PostgreSQL, and the OpenWeatherMap API.

## Overview

Weather Notifier solves a simple but common automation problem: instead of manually checking the weather, this pipeline periodically polls the OpenWeatherMap API for a list of cities, compares the result against the last known state, and only sends an email when a condition actually *changes* — rain starting or rain stopping. Every observation is also archived to a PostgreSQL database for later analysis.

The project evolved from a single Python script into an orchestrated Airflow DAG, reflecting a typical path from automation script to data pipeline.

## Features

- **Multi-city monitoring** — checks weather for any number of locations defined in a CSV file
- **Adverse condition detection** — flags rain, drizzle, and thunderstorm conditions
- **Alert deduplication** — uses persisted state to notify only on transitions (clear → rain, rain → clear), not on every run
- **Email notifications** — HTML-formatted alerts sent via Gmail SMTP, with separate messages for "rain started" and "rain stopped"
- **Historical data storage** — every weather check is logged to a PostgreSQL table for trend analysis
- **Orchestrated scheduling** — runs on a fixed interval via Apache Airflow, with retries and branching logic
- **Centralized logging** — all modules log to a single file through a shared logger instance

## Architecture

```
                    ┌────────────────────-─┐
                    │  weather_locations   │
                    │       .csv           │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌───────────────────-──┐
                    │   load_locations     │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌────────────────────-─┐
                    │  fetch_weather_data  │──── OpenWeatherMap API
                    └──────────┬───────────┘
                               │
                ┌──────────────┴──────────────-┐
                ▼                              ▼
    ┌────────────────────--─┐        ┌────────────────────---──┐
    │  load_weather_history │        │ check_and_notify_alerts │
    │   (→ PostgreSQL)      │        │   (state comparison)    │
    └────────────────────--─┘        └──────────┬──────────---─┘
                                                │
                                                ▼
                                    ┌───────────────────-──┐
                                    │   check_conditions   │
                                    │     (branch task)    │
                                    └──────────-┬──────────┘
                                  ┌─────────────┴───────────-──┐
                                  ▼                            ▼
                        ┌────────────────--─┐          ┌─────────────────┐
                        │  sending_alerts   │          │   end_pipeline  │
                        │  (email via SMTP) │          │   (no-op log)   │
                        └────────────────--─┘          └─────────────────┘
```

## Tech Stack

| Component | Technology |
|---|---|
| Orchestration | Apache Airflow (TaskFlow API) via Astro CLI |
| Language | Python 3.13 |
| Weather data | OpenWeatherMap API (current weather + geocoding) |
| History storage & State | PostgreSQL (Docker) |
| Notifications | Gmail SMTP (`smtplib`) |
| Database admin | pgAdmin (Docker) |
| Containerization | Docker Compose (via Astro CLI) |

## Project Structure

```
weather-notifier/
├── dags/
│   └── weather_notifier.py        # Airflow DAG main workflow (TaskFlow API)
│   └── get_lat_lon_locations.py   # Airflow DAG to get lat lon location (TaskFlow API)
├── include/
│   ├── data/
│   │   └── weather_locations.csv  # List of cities with lat/lon
|   ├── logs/
│   │   └── logger.log             # Log process
│   ├── weather.py                 # OpenWeatherMap API calls
│   ├── checker.py                 # Adverse weather condition detection
│   ├── state.py                   # State persistence & transition detection
│   ├── weather_history.py         # PostgreSQL history logging
│   ├── email_notifier.py          # HTML email composition & sending
│   └── logger.py                  # Centralized logging setup
├── plugins/
├── tests/
├── docker-compose.override.yml    # Custom postgres + pgAdmin services
├── Dockerfile
├── packages.txt
├── requirements.txt
├── .env                            # Secrets (not committed)
├── .env.example                    # Template for required variables
└── .gitignore
```

## Module Responsibilities

| Module | Responsibility |
|---|---|
| `weather.py` | Fetches coordinates and current weather data from OpenWeatherMap |
| `state.py` | Loads/saves city state, detects transitions (rain started / rain stopped) to prevent duplicate alerts |
| `weather_history.py` | Initializes the history table and appends each weather observation to PostgreSQL |
| `email_notifier.py` | Builds and sends HTML email alerts via Gmail SMTP |
| `logger.py` | Provides a single shared logger (`weather_notifier`) used across all modules |

## How Alert Deduplication Works

Running the pipeline every few minutes means the same rain event would otherwise trigger a new email on every run. To avoid this, each city's last known condition is persisted and compared against the current reading:

| Previous state | Current state | Action |
|---|---|---|
| Not raining | Raining | Send "rain started" alert |
| Raining | Raining | No alert (already notified) |
| Raining | Not raining | Send "rain stopped" alert |
| Not raining | Not raining | No alert |

This is a simplified version of the transition-detection pattern used in production monitoring systems (e.g. Prometheus Alertmanager, PagerDuty).

## Database Schema

**`weather_history`** — append-only log of every observation

| Column | Type | Description |
|---|---|---|
| `id` | `BIGINT` (identity) | Primary key |
| `location` | `TEXT` | City name |
| `weather_conditions` | `TEXT` | Main condition (e.g. `Rain`, `Clear`) |
| `description` | `TEXT` | Detailed description |
| `temperature` | `FLOAT` | Temperature in °C |
| `humidity` | `INTEGER` | Humidity percentage |
| `wind_speed` | `FLOAT` | Wind speed in m/s |
| `date` / `time` | `DATE` / `TIME` | Observation timestamp |

**`weather_state`** — one row per city, current condition only

| Column | Type | Description |
|---|---|---|
| `city` | `TEXT` (Primary key) | City name |
| `is_raining` | `BOOLEAN` | Current rain status |
| `last_checked` | `TIMESTAMP` | Last time this city was checked |
| `alert_sent_at` | `TIMESTAMP` | Last time an alert was sent |


## Setup

### Prerequisites

- [Astro CLI](https://www.astronomer.io/docs/astro/cli/install-cli)
- Docker Desktop
- An [OpenWeatherMap API key](https://openweathermap.org/api)
- A Gmail account with an [App Password](https://support.google.com/accounts/answer/185833) generated

### 1. Clone and configure environment variables

```bash
git clone <repo-url>
cd weather-notifier
cp .env.example .env
```

Fill in `.env`:

```env
WEATHER_API_KEY=your_openweathermap_key
SENDER_EMAIL=you@gmail.com
APP_PASSWORD=your_gmail_app_password
RECEIVER_EMAIL=recipient@gmail.com

AIRFLOW_CONN_WEATHER_DB_CONN=postgresql://postgres:postgres@weather_db:5432/weather_db
```

### 2. Define your locations

Edit `include/data/weather_locations.csv` with the cities you want to monitor (name, latitude, longitude).

### 3. Start the environment

```bash
astro dev start
```

This builds the Airflow containers plus the custom `weather_db` (PostgreSQL) and `pgadmin` services defined in `docker-compose.override.yml`.

### 4. Access the services

| Service | URL | Credentials |
|---|---|---|
| Airflow UI | http://localhost:8080 | `admin` / `admin` |
| pgAdmin | http://localhost:5050 | as set in `.env` |
| PostgreSQL (from host) | `localhost:5435` | as set in `.env` |

### 5. Run the pipeline

In the Airflow UI, unpause `weather_notifier_pipeline`. It runs automatically every 10 minutes, or trigger it manually for testing.

## Local Development Notes

- The `include/` folder is automatically mounted into all Airflow containers by Astro CLI — no manual volume configuration is needed for it.
- The custom `weather_db` and `pgadmin` services must be explicitly attached to Astro's internal Docker network (`<project>_airflow`) to be reachable from Airflow tasks; this is already configured in `docker-compose.override.yml`.
- Avoid naming custom services `postgres`, `webserver`, `scheduler`, or other names Astro already uses internally — Docker Compose will merge configurations rather than create separate containers.
- Database credentials for `weather_db` and `pgadmin` are intended for local development only and are not security-sensitive in the way the OpenWeatherMap or email credentials are.

## Possible Extensions

- Migrate state and history storage from local PostgreSQL to a managed service (e.g. Supabase) for persistence outside local Docker volumes
- Add a transformation/aggregation layer (daily average temperature per city, rain frequency per week) to strengthen this as a data engineering portfolio piece
- Add a lightweight dashboard (Metabase or Grafana) on top of `weather_history` for visual trend analysis
- Extend alert conditions beyond rain to extreme temperature, high wind, and high humidity
- Add forecast-based alerts (next 3–12 hours) in addition to current-condition alerts

## License

This project is for educational and portfolio purposes.