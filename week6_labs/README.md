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

### Core Weather Features
- **Search Dashboard**
  - Enter a city name (supports `City`, `City, Country Code`, or coordinates).
  - Async fetching with graceful messages for invalid locations or network issues.
  - Displays weather icon, temperature (metric units), humidity, wind speed, and "feels like" temperature.
  - Current location detection using IP geolocation.
  - Local time display for the searched city.
  - **Professional loading spinner** - Centered modal with blue card design and white spinner.

- **Sunrise/Sunset Countdown**
  - Shows local sunrise and sunset times based on the provided timezone offset.
  - Live countdown that automatically switches between "Sunrise in…", "Sunset in…", and "Next sunrise in…".
  - Updates every 30 seconds for real-time accuracy.

- **Air Quality Summary**
  - Uses the retrieved latitude/longitude to call the Air Pollution API.
  - Provides AQI bucket with color-coded chip (Good/Fair/Moderate/Poor/Very Poor).
  - Detailed pollutant concentration display (PM2.5, PM10, O₃, NO₂, CO).

### Advanced Features
- **Multiple Cities Comparison**
  - "Add to comparison" button stores the current city inside a persistent JSON watchlist.
  - Comparison cards display icon, temperature, humidity, wind, and local time.
  - Remove city via the delete icon; list refreshes automatically and survives restarts.
  - Data persists across app sessions.

- **Hourly Forecast**
  - Displays next 36 hours of weather forecast in 3-hour intervals.
  - Shows temperature, weather icon, and humidity for each time slot.
  - Horizontal scrolling for easy navigation.
  - Clean card-based design with icons.

- **Weather Recommendations**
  - Smart recommendations based on current weather conditions.
  - Temperature-based advice (stay hydrated, dress warmly, etc.).
  - Condition-specific tips (umbrella for rain, indoor warnings for storms, etc.).
  - Dynamic emoji icons for visual appeal.

### UI/UX Enhancements
- **Modern Design**: Minimalist blue/gray color scheme with gradient header.
- **Loading States**: Professional centered loading spinner with semi-transparent overlay.
- **Responsive Layout**: Adapts to different screen sizes with responsive rows.
- **Visual Feedback**: Color-coded status messages, smooth transitions, and hover effects.
- **Accessibility**: Clear typography, good contrast ratios, and descriptive tooltips.

## Testing Checklist

### Basic Functionality
1. ✅ Search a valid city (e.g., `Manila`, `Tokyo`, `Paris`) and confirm base weather fields.
2. ✅ Verify the **loading spinner** appears centered with blue card design while fetching data.
3. ✅ Click "My Location" button to detect your current location automatically.
4. ✅ Try an invalid city (e.g., `asdfghjkl`) to see error handling.

### Feature Verification
5. ✅ Check sunrise/sunset times and countdown updates (wait 30 seconds to see refresh).
6. ✅ Verify air quality displays with color-coded AQI chip and pollutant details.
7. ✅ Confirm hourly forecast displays correctly with temperature, humidity, and weather icons.
8. ✅ Check that weather recommendations appear based on current conditions.
9. ✅ Verify "feels like" temperature is displayed below main temperature.
10. ✅ Confirm local time is shown for the searched city.

### Data Persistence
11. ✅ Add at least two cities to the comparison list and verify cards render.
12. ✅ Remove a city from the watchlist using the close button.
13. ✅ Close and reopen the app—watchlist should persist.

### UI/UX
14. ✅ Verify loading spinner appears centered with dark overlay.
15. ✅ Check that all buttons are disabled during loading.
16. ✅ Confirm status messages appear with appropriate colors.
17. ✅ Test horizontal scrolling on hourly forecast.

## Troubleshooting

### Common Issues

- **Missing API key**: The app will raise a clear error if `OPENWEATHER_API_KEY` is not defined in `.env`.
  - **Solution**: Edit `.env` file and add your API key from https://openweathermap.org/api

- **Rate limit or connectivity issues**: Error messages appear in the header section.
  - **Solution**: Wait a few moments and retry. Free API keys have rate limits.

- **Location detection fails**: "Unable to detect your location" message appears.
  - **Solution**: Manually enter your city name in the search box.

- **Stale watchlist**: Old cities remain in comparison list.
  - **Solution**: Delete `weather_app/data/watchlist.json` to reset the saved list.

- **Loading spinner stuck**: Spinner doesn't disappear after searching.
  - **Solution**: Check your internet connection and API key validity.

- **Import errors**: `ModuleNotFoundError` when running the app.
  - **Solution**: Ensure virtual environment is activated and run `pip install -r requirements.txt`

### Performance Tips

- The app fetches data for all watchlist cities on startup, which may take a few seconds.
- Hourly forecast data is cached per search to minimize API calls.
- Countdown updates every 30 seconds to balance accuracy and performance.

---

## Recent Updates

### Version 1.1 (November 26, 2025)
- ✨ **New**: Professional centered loading spinner with blue card design
- ✨ **New**: Semi-transparent overlay during loading for better focus
- ✨ **New**: Disabled inputs during data fetching to prevent multiple requests
- 🎨 **Improved**: Loading experience with larger spinner and clear messaging
- 📝 **Updated**: Comprehensive documentation and testing checklist

### Version 1.0 (November 25, 2025)
- 🎉 Initial release with all Module 6 requirements
- ✅ Beginner features: Search, weather display, async handling
- ✅ Advanced features: Multiple cities, sunrise/sunset, air quality
- 🌟 Bonus features: Current location, hourly forecast, recommendations

---

## Credits

- **Weather Data**: [OpenWeatherMap API](https://openweathermap.org/api)
- **Geolocation**: [IP-API](https://ip-api.com/)
- **UI Framework**: [Flet](https://flet.dev/)
- **Icons**: Material Design Icons

---
