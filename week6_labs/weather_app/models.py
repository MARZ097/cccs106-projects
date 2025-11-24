from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class WeatherData:
    """Normalized representation of a city's current weather."""

    city: str
    country: str
    temperature: float
    description: str
    humidity: int
    wind_speed: float
    icon: str
    sunrise: datetime
    sunset: datetime
    timezone_offset: int
    latitude: float
    longitude: float


@dataclass(slots=True)
class AirQualityData:
    """Air quality index with the most relevant pollutants."""

    aqi: int
    co: float
    no2: float
    o3: float
    pm2_5: float
    pm10: float


