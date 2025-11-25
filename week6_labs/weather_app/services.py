from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Final

import httpx
from dotenv import load_dotenv

try:
    from .models import AirQualityData, WeatherData
except ImportError:
    # Allow running as a script directly
    from models import AirQualityData, WeatherData

load_dotenv()


class WeatherServiceError(Exception):
    """Raised when the weather service fails."""


class WeatherService:
    """Wrapper around the OpenWeatherMap REST endpoints."""

    WEATHER_URL: Final[str] = "https://api.openweathermap.org/data/2.5/weather"
    AIR_URL: Final[str] = "https://api.openweathermap.org/data/2.5/air_pollution"
    FORECAST_URL: Final[str] = "https://api.openweathermap.org/data/2.5/forecast"
    IPAPI_URL: Final[str] = "http://ip-api.com/json/"

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.getenv("OPENWEATHER_API_KEY")
        if not self.api_key:
            raise WeatherServiceError(
                "Missing API key. Define OPENWEATHER_API_KEY in .env or environment."
            )

    async def fetch_weather(self, city: str, units: str = "metric") -> WeatherData:
        """Return normalized weather data for a given city."""
        params = {"q": city, "appid": self.api_key, "units": units}

        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
            try:
                resp = await client.get(self.WEATHER_URL, params=params)
                resp.raise_for_status()
            except httpx.HTTPStatusError as exc:
                message = exc.response.json().get("message", "Request failed")
                raise WeatherServiceError(message.title()) from exc
            except httpx.HTTPError as exc:
                raise WeatherServiceError("Network error while fetching weather") from exc

        payload = resp.json()
        sys_data = payload.get("sys", {})
        coord = payload.get("coord", {})

        return WeatherData(
            city=payload.get("name", city).strip(),
            country=sys_data.get("country", ""),
            temperature=payload["main"]["temp"],
            feels_like=payload["main"]["feels_like"],
            description=payload["weather"][0]["description"].title(),
            humidity=payload["main"]["humidity"],
            wind_speed=payload["wind"]["speed"],
            icon=payload["weather"][0]["icon"],
            sunrise=datetime.fromtimestamp(sys_data["sunrise"], tz=timezone.utc),
            sunset=datetime.fromtimestamp(sys_data["sunset"], tz=timezone.utc),
            timezone_offset=payload.get("timezone", 0),
            latitude=coord.get("lat", 0.0),
            longitude=coord.get("lon", 0.0),
        )

    async def fetch_air_quality(self, lat: float, lon: float) -> AirQualityData:
        """Return air quality data for a coordinate pair."""
        params = {"lat": lat, "lon": lon, "appid": self.api_key}

        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
            try:
                resp = await client.get(self.AIR_URL, params=params)
                resp.raise_for_status()
            except httpx.HTTPStatusError as exc:
                message = exc.response.json().get("message", "Request failed")
                raise WeatherServiceError(message.title()) from exc
            except httpx.HTTPError as exc:
                raise WeatherServiceError("Network error while fetching air quality") from exc

        payload = resp.json()
        record = payload["list"][0]
        components = record["components"]

        return AirQualityData(
            aqi=record["main"]["aqi"],
            co=components.get("co", 0.0),
            no2=components.get("no2", 0.0),
            o3=components.get("o3", 0.0),
            pm2_5=components.get("pm2_5", 0.0),
            pm10=components.get("pm10", 0.0),
        )

    async def fetch_hourly_forecast(self, lat: float, lon: float, units: str = "metric") -> list[dict]:
        """Return hourly forecast for next 24 hours."""
        params = {"lat": lat, "lon": lon, "appid": self.api_key, "units": units}

        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
            try:
                resp = await client.get(self.FORECAST_URL, params=params)
                resp.raise_for_status()
            except httpx.HTTPStatusError as exc:
                message = exc.response.json().get("message", "Request failed")
                raise WeatherServiceError(message.title()) from exc
            except httpx.HTTPError as exc:
                raise WeatherServiceError("Network error while fetching forecast") from exc

        payload = resp.json()
        hourly_data = []
        
        # OpenWeatherMap 5-day forecast returns data in 3-hour intervals
        for item in payload["list"][:16]:  # Get next 48 hours (16 * 3 hours)
            dt = datetime.fromtimestamp(item["dt"], tz=timezone.utc)
            hourly_data.append({
                "time": dt.strftime("%I %p"),  # e.g., "03 PM"
                "temp": item["main"]["temp"],
                "icon": item["weather"][0]["icon"],
                "humidity": item["main"]["humidity"],
                "description": item["weather"][0]["description"].title(),
            })
        
        return hourly_data

    async def get_current_location(self) -> str:
        """Get current location city name using IP geolocation."""
        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
            try:
                resp = await client.get(self.IPAPI_URL)
                resp.raise_for_status()
                data = resp.json()
                if data.get("status") == "success":
                    return data.get("city", "")
                raise WeatherServiceError("Unable to detect location")
            except httpx.HTTPError as exc:
                raise WeatherServiceError("Network error while detecting location") from exc


