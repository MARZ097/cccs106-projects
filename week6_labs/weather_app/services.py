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


