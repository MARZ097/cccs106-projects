# Module 6 Weather Application

Interactive weather dashboard built with **Python 3.12** and **Flet 0.28.3** for the Module 6 learning task. The app follows the provided tutorial for the base features and adds the required enhancements:

- Beginner baseline: search any city, show current temperature, description, humidity, wind speed, OpenWeather icon, async network handling, and friendly error states.
- Multiple Cities Comparison: maintain a persistent watchlist and view side-by-side cards for several cities.
- Sunrise/Sunset Countdown: display local sunrise and sunset plus a live countdown to the next event.
- Air Quality Integration: pull real-time AQI data (OpenWeather Air Pollution API) and highlight key pollutants.

## Project Structure

```
week6_labs/
├── .env.example          # Template for environment variables
├── .gitignore           # Git ignore rules
├── README.md            # This file
├── requirements.txt     # Python dependencies
├── setup.bat            # Automated setup script (Windows)
├── run_app.bat          # Quick run script (Windows)
└── weather_app/
    ├── __init__.py      # Package initialization
    ├── main.py          # Main application and UI
    ├── models.py        # Data models (WeatherData, AirQualityData)
    ├── services.py      # API service layer
    └── data/            # Created automatically - stores watchlist.json
```

The app stores the comparison watchlist JSON inside `weather_app/data/` (created automatically on first run).

## Prerequisites

- Python 3.11+ (tested on 3.12)
- OpenWeatherMap API key with access to the weather and air pollution endpoints

## Setup

### Quick Setup (Windows)

Run the automated setup script:

```bash
cd week6_labs
setup.bat
```

This will:
- Create a virtual environment
- Install all dependencies
- Create a `.env` file from `.env.example`

Then edit `.env` and add your OpenWeatherMap API key from https://openweathermap.org/api.

### Manual Setup

```bash
cd week6_labs
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

Create your environment file:

```bash
copy .env.example .env       # Windows
# cp .env.example .env       # macOS/Linux
```

Edit `.env` and replace the placeholder key with the one from https://openweathermap.org/api.

## Running the App

### Quick Run (Windows)

After setup, simply run:

```bash
run_app.bat
```

Or manually:

```bash
cd week6_labs
venv\Scripts\activate
cd weather_app
python main.py
```

**Note:** When running manually, make sure to `cd` into the `weather_app` directory first, or use the module approach:

```bash
cd week6_labs
venv\Scripts\activate
python -m weather_app.main
```

Flet opens a desktop window by default. Use `--web` if you prefer running it in the browser.

## Feature Highlights

- **Search Dashboard**
  - Enter a city name (supports `City`, `City, Country Code`, or coordinates).
  - Async fetching with graceful messages for invalid locations or network issues.
  - Displays weather icon, temperature (metric units), humidity, wind speed, and "feels like" temperature.
  - Current location detection using IP geolocation.
  - Local time display for the searched city.
- **Sunrise/Sunset Countdown**
  - Shows local sunrise and sunset times based on the provided timezone offset.
  - Countdown automatically switches between “Sunrise in…”, “Sunset in…”, and “Next sunrise in…”.
- **Air Quality Summary**
  - Uses the retrieved latitude/longitude to call the Air Pollution API.
  - Provides AQI bucket, color-coded chip, and pollutant concentration details (PM2.5, PM10, O₃, NO₂, CO).
- **Multiple Cities Comparison**
  - "Add to comparison" button stores the current city inside a persistent JSON watchlist.
  - Comparison cards display icon, temperature, humidity, wind, and local time.
  - Remove city via the delete icon; list refreshes automatically and survives restarts.
- **Hourly Forecast**
  - Displays next 36 hours of weather forecast in 3-hour intervals.
  - Shows temperature, weather icon, and humidity for each time slot.
  - Horizontal scrolling for easy navigation.
- **Weather Recommendations**
  - Smart recommendations based on current weather conditions.
  - Temperature-based advice (stay hydrated, dress warmly, etc.).
  - Condition-specific tips (umbrella for rain, indoor warnings for storms, etc.).

## Testing Checklist

1. Search a valid city (e.g., `Manila`) and confirm base weather fields, sunrise/sunset countdown, and air quality.
2. Click "My Location" button to detect your current location automatically.
3. Verify hourly forecast displays correctly with temperature, humidity, and weather icons.
4. Check that weather recommendations appear based on current conditions.
5. Add at least two cities to the comparison list and verify cards render.
6. Close/reopen the app—watchlist should persist.
7. Try an invalid city to see error handling.

## Troubleshooting

- **Missing API key**: The app will raise a clear error if `OPENWEATHER_API_KEY` is not defined.
- **Rate limit or connectivity issues**: Messages appear near the search bar; retry after a short wait.
- **Stale watchlist**: Delete `weather_app/data/watchlist.json` if you need to reset the saved list.

Happy coding!


