from __future__ import annotations

import asyncio
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import flet as ft

try:
    from .models import AirQualityData, WeatherData
    from .services import WeatherService, WeatherServiceError
except ImportError:
    # Allow running as a script directly
    from models import AirQualityData, WeatherData
    from services import WeatherService, WeatherServiceError


class WeatherApp:
    """Flet-based weather dashboard with multiple enhancements."""

    def __init__(self, page: ft.Page) -> None:
        self.page = page
        self.service = WeatherService()
        self.current_weather: WeatherData | None = None
        self.current_air: AirQualityData | None = None
        self.hourly_forecast: list[dict] = []

        self.storage_dir = Path(__file__).parent / "data"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.watchlist_file = self.storage_dir / "watchlist.json"
        self.watchlist: list[str] = self._load_watchlist()
        self.units = "metric"

        self._build_ui()
        self.page.run_task(self._refresh_watchlist)
        self.page.run_task(self._countdown_loop)
        self.page.run_task(self._fetch_current_location)

    # ------------------------------------------------------------------ UI setup
    def _build_ui(self) -> None:
        page = self.page
        page.title = "Weather Dashboard"
        page.padding = 0
        page.bgcolor = "#F5F7FA"
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.scroll = ft.ScrollMode.AUTO

        self.status_text = ft.Text("", color="#FFFFFF", size=14, weight=ft.FontWeight.W_500)
        self.city_field = ft.TextField(
            label="Search location",
            hint_text="e.g., Manila, Tokyo, Paris",
            autofocus=True,
            on_submit=self._handle_search,
            expand=True,
            border_color="#CBD5E0",
            focused_border_color="#4299E1",
            text_size=15,
        )
        self.search_button = ft.ElevatedButton(
            text="Search",
            icon=ft.Icons.SEARCH,
            on_click=self._handle_search,
            bgcolor="#4299E1",
            color="#FFFFFF",
        )
        self.location_button = ft.ElevatedButton(
            text="My Location",
            icon=ft.Icons.MY_LOCATION,
            on_click=self._handle_current_location,
            bgcolor="#667EEA",
            color="#FFFFFF",
        )
        self.add_watch_button = ft.OutlinedButton(
            text="Add to comparison",
            icon=ft.Icons.ADD,
            disabled=True,
            on_click=self._handle_add_watchlist,
        )

        self.main_icon = ft.Image(src="", width=120, height=120, fit=ft.ImageFit.CONTAIN, visible=False)
        self.temp_text = ft.Text(size=56, weight=ft.FontWeight.BOLD, color="#2D3748")
        self.feels_like_text = ft.Text(size=16, color="#718096", italic=True)
        self.description_text = ft.Text(size=18, color="#4A5568")
        self.current_time_text = ft.Text(size=15, color="#718096", italic=True)
        self.details_column = ft.Column(spacing=8)
        self.recommendations_column = ft.Column(spacing=8)
        self.sunrise_text = ft.Text(size=14, color="#4A5568")
        self.sunset_text = ft.Text(size=14, color="#4A5568")
        self.countdown_text = ft.Text(size=14, weight=ft.FontWeight.BOLD, color="#2D3748")

        self.air_chip_label = ft.Text("AQI", weight=ft.FontWeight.BOLD, size=12, color="#FFFFFF")
        self.air_chip_container = ft.Container(
            content=self.air_chip_label,
            padding=ft.padding.symmetric(horizontal=14, vertical=8),
            bgcolor="#718096",
            border_radius=20,
        )
        self.air_details = ft.Column(spacing=6)

        self.watchlist_column = ft.Column(spacing=12, expand=True)
        self.hourly_scroll = ft.Row(scroll=ft.ScrollMode.AUTO, spacing=10)

        # Create centered loading spinner overlay
        self.loading_overlay = ft.Container(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.ProgressRing(width=70, height=70, stroke_width=5, color="#FFFFFF"),
                        ft.Container(height=20),
                        ft.Text(
                            "Loading weather data...", 
                            size=18, 
                            color="#FFFFFF", 
                            weight=ft.FontWeight.W_600,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=0,
                ),
                padding=40,
                bgcolor="#4299E1",
                border_radius=20,
                shadow=ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=30,
                    color="#00000040",
                    offset=ft.Offset(0, 10),
                ),
            ),
            alignment=ft.alignment.center,
            bgcolor="#00000050",  # Dark semi-transparent overlay
            visible=False,
        )

        # Main content container
        self.main_content = ft.Container(
            content=ft.Column(
                controls=[
                    # Header section with gradient
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(
                                    "Weather Dashboard",
                                    size=28,
                                    weight=ft.FontWeight.BOLD,
                                    color="#FFFFFF",
                                ),
                                ft.Container(height=20),
                                ft.Row(
                                    [self.city_field, self.search_button, self.location_button],
                                    spacing=10,
                                ),
                                ft.Container(
                                    content=self.status_text,
                                    padding=ft.padding.only(top=5),
                                ),
                            ],
                            spacing=10,
                        ),
                        padding=30,
                        gradient=ft.LinearGradient(
                            begin=ft.alignment.top_left,
                            end=ft.alignment.bottom_right,
                            colors=["#4299E1", "#667EEA"],
                        ),
                    ),
                    # Main content
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Row(
                                    [
                                        self.add_watch_button,
                                    ],
                                    alignment=ft.MainAxisAlignment.END,
                                    spacing=10,
                                ),
                                self._build_main_card(),
                                self._build_hourly_forecast_card(),
                                self._build_air_quality_card(),
                                ft.Container(height=10),
                                ft.Text(
                                    "City Comparison",
                                    size=22,
                                    weight=ft.FontWeight.BOLD,
                                    color="#2D3748",
                                ),
                                ft.Text(
                                    "Compare weather across multiple cities",
                                    size=14,
                                    color="#718096",
                                ),
                                ft.Container(height=5),
                                self.watchlist_column,
                            ],
                            spacing=15,
                        ),
                        padding=ft.padding.symmetric(horizontal=30, vertical=20),
                    ),
                ],
                spacing=0,
            ),
            width=1000,
        )

        # Use Stack to overlay loading spinner on top of content
        page.add(
            ft.Stack(
                [
                    self.main_content,
                    self.loading_overlay,
                ],
                expand=True,
            )
        )

    def _build_main_card(self) -> ft.Control:
        """Card displaying the currently searched city's weather."""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Column(
                                [
                                    self.temp_text,
                                    self.feels_like_text,
                                    self.description_text,
                                    self.current_time_text,
                                    ft.Container(height=10),
                                    self.details_column,
                                ],
                                alignment=ft.MainAxisAlignment.START,
                                expand=True,
                            ),
                            self.main_icon,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Container(height=10),
                    self.recommendations_column,
                    ft.Container(height=10),
                    ft.Divider(height=1, color="#E2E8F0"),
                    ft.Container(height=10),
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Row(
                                            [
                                                ft.Icon(ft.Icons.WB_SUNNY, size=20, color="#F6AD55"),
                                                ft.Text("Sunrise", size=13, weight=ft.FontWeight.BOLD, color="#4A5568"),
                                            ],
                                            spacing=5,
                                        ),
                                        self.sunrise_text,
                                    ],
                                    spacing=5,
                                ),
                                padding=15,
                                bgcolor="#FFF5F0",
                                border_radius=10,
                                expand=True,
                            ),
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Row(
                                            [
                                                ft.Icon(ft.Icons.WB_TWILIGHT, size=20, color="#FC8181"),
                                                ft.Text("Sunset", size=13, weight=ft.FontWeight.BOLD, color="#4A5568"),
                                            ],
                                            spacing=5,
                                        ),
                                        self.sunset_text,
                                    ],
                                    spacing=5,
                                ),
                                padding=15,
                                bgcolor="#FFF0F0",
                                border_radius=10,
                                expand=True,
                            ),
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Row(
                                            [
                                                ft.Icon(ft.Icons.TIMER, size=20, color="#4299E1"),
                                                ft.Text("Countdown", size=13, weight=ft.FontWeight.BOLD, color="#4A5568"),
                                            ],
                                            spacing=5,
                                        ),
                                        self.countdown_text,
                                    ],
                                    spacing=5,
                                ),
                                padding=15,
                                bgcolor="#EBF8FF",
                                border_radius=10,
                                expand=True,
                            ),
                        ],
                        spacing=10,
                    ),
                ],
                spacing=15,
            ),
            padding=25,
            bgcolor="#FFFFFF",
            border_radius=15,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=10,
                color="#00000010",
                offset=ft.Offset(0, 2),
            ),
        )

    def _build_hourly_forecast_card(self) -> ft.Control:
        """Card containing hourly forecast."""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.ACCESS_TIME, size=24, color="#667EEA"),
                            ft.Text("Hourly Forecast", size=20, weight=ft.FontWeight.BOLD, color="#2D3748"),
                        ],
                        spacing=10,
                    ),
                    ft.Container(height=10),
                    self.hourly_scroll,
                ],
                spacing=12,
            ),
            padding=25,
            bgcolor="#FFFFFF",
            border_radius=15,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=10,
                color="#00000010",
                offset=ft.Offset(0, 2),
            ),
        )

    def _build_air_quality_card(self) -> ft.Control:
        """Card containing air quality metrics."""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Row(
                                [
                                    ft.Icon(ft.Icons.AIR, size=24, color="#4299E1"),
                                    ft.Text("Air Quality", size=20, weight=ft.FontWeight.BOLD, color="#2D3748"),
                                ],
                                spacing=10,
                            ),
                            self.air_chip_container,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Container(height=5),
                    self.air_details,
                ],
                spacing=12,
            ),
            padding=25,
            bgcolor="#FFFFFF",
            border_radius=15,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=10,
                color="#00000010",
                offset=ft.Offset(0, 2),
            ),
        )

    # ------------------------------------------------------------------ Event handlers
    def _handle_search(self, e: ft.ControlEvent) -> None:
        city = self.city_field.value.strip()
        if not city:
            self._show_status("Please enter a city name.")
            return
        self.page.run_task(self._fetch_weather, city)

    def _handle_current_location(self, e: ft.ControlEvent) -> None:
        self.page.run_task(self._fetch_current_location_weather)

        self.page.run_task(self._refresh_watchlist)

    def _handle_add_watchlist(self, e: ft.ControlEvent) -> None:
        if not self.current_weather:
            return
        city = self.current_weather.city
        if city in self.watchlist:
            self._show_status(f"{city} is already on your list.", success=True)
            return
        self.watchlist.append(city)
        self._save_watchlist()
        self._show_status(f"Added {city} to comparison.", success=True)
        self.page.run_task(self._refresh_watchlist)

    def _handle_remove_city(self, city: str) -> None:
        if city not in self.watchlist:
            return
        self.watchlist.remove(city)
        self._save_watchlist()
        self._show_status(f"Removed {city} from comparison.", success=True)
        self.page.run_task(self._refresh_watchlist)

    # ------------------------------------------------------------------ Async helpers
    async def _fetch_weather(self, city: str) -> None:
        self._set_loading(True)
        try:
            weather = await self.service.fetch_weather(city, units=self.units)
            air = await self.service.fetch_air_quality(weather.latitude, weather.longitude)
            hourly = await self.service.fetch_hourly_forecast(weather.latitude, weather.longitude, units=self.units)
        except WeatherServiceError as exc:
            self._show_status(str(exc))
            self._set_loading(False)
            return

        self.current_weather = weather
        self.current_air = air
        self.hourly_forecast = hourly
        self._update_weather_display()
        self._update_air_quality()
        self._update_hourly_forecast()
        self._set_loading(False)

    async def _fetch_current_location(self) -> None:
        """Fetch weather for current location on app start."""
        try:
            city = await self.service.get_current_location()
            if city:
                await self._fetch_weather(city)
        except WeatherServiceError:
            # Silently fail on app start if location detection fails
            pass

    async def _fetch_current_location_weather(self) -> None:
        """Fetch weather for current location when button is clicked."""
        self._set_loading(True)
        try:
            city = await self.service.get_current_location()
            if city:
                self.city_field.value = city
                await self._fetch_weather(city)
            else:
                self._show_status("Unable to detect your location")
        except WeatherServiceError as exc:
            self._show_status(str(exc))
        finally:
            self._set_loading(False)

    async def _refresh_watchlist(self) -> None:
        if not self.watchlist:
            self.watchlist_column.controls = [
                ft.Text("No cities yet. Search for a city and tap 'Add to comparison'.")
            ]
            self.page.update()
            return

        cards: list[ft.Control] = []
        
        for city in self.watchlist:
            try:
                weather = await self.service.fetch_weather(city, units=self.units)
            except WeatherServiceError as exc:
                self._show_status(f"{city}: {exc}")
                continue
            
            cards.append(self._build_watch_card(weather))

        self.watchlist_column.controls = cards or [
            ft.Text("Unable to load watchlist. Check your API key or network.")
        ]
        
        self.page.update()

    # ------------------------------------------------------------------ UI updates
    def _update_weather_display(self) -> None:
        if not self.current_weather:
            return
        weather = self.current_weather
        unit_symbol = "°C" if self.units == "metric" else "°F"
        wind_unit = "m/s" if self.units == "metric" else "mph"

        self.temp_text.value = f"{weather.temperature:.1f}{unit_symbol}"
        self.feels_like_text.value = f"Feels like {weather.feels_like:.1f}{unit_symbol}"
        self.description_text.value = f"{weather.city}, {weather.country} · {weather.description}"
        
        # Display current time in the city's timezone
        tz = timezone(timedelta(seconds=weather.timezone_offset))
        current_time = datetime.now(tz)
        self.current_time_text.value = f"Local time: {current_time.strftime('%I:%M %p, %B %d, %Y')}"
        
        self.main_icon.src = f"https://openweathermap.org/img/wn/{weather.icon}@4x.png"
        self.main_icon.visible = True
        
        # Update recommendations
        self._update_recommendations(weather)

        self.details_column.controls = [
            ft.Row(
                [
                    ft.Icon(ft.Icons.WATER_DROP, size=18, color="#4299E1"),
                    ft.Text(f"Humidity: {weather.humidity}%", size=15, color="#4A5568"),
                ],
                spacing=8,
            ),
            ft.Row(
                [
                    ft.Icon(ft.Icons.AIR, size=18, color="#48BB78"),
                    ft.Text(f"Wind: {weather.wind_speed:.1f} {wind_unit}", size=15, color="#4A5568"),
                ],
                spacing=8,
            ),
        ]

        self._update_solar_section()

        self.add_watch_button.disabled = False
        self._show_status(f"Updated weather for {weather.city}.", success=True)
        self.page.update()

    def _update_air_quality(self) -> None:
        if not self.current_air:
            self.air_chip_label.value = "No data"
            self.air_chip_label.color = "#FFFFFF"
            self.air_chip_container.bgcolor = "#A0AEC0"
            self.air_details.controls = []
            self.page.update()
            return

        air = self.current_air
        label, color = self._aqi_label_color(air.aqi)
        self.air_chip_label.value = f"AQI {air.aqi} · {label}"
        self.air_chip_label.color = "#FFFFFF"
        self.air_chip_container.bgcolor = color

        self.air_details.controls = [
            ft.Row(
                [
                    ft.Container(
                        content=ft.Text("PM2.5", size=12, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        bgcolor="#667EEA",
                        border_radius=5,
                    ),
                    ft.Text("{:.1f} µg/m³".format(air.pm2_5), size=14, color="#4A5568"),
                ],
                spacing=10,
            ),
            ft.Row(
                [
                    ft.Container(
                        content=ft.Text("PM10", size=12, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        bgcolor="#5A67D8",
                        border_radius=5,
                    ),
                    ft.Text("{:.1f} µg/m³".format(air.pm10), size=14, color="#4A5568"),
                ],
                spacing=10,
            ),
            ft.Row(
                [
                    ft.Container(
                        content=ft.Text("O₃", size=12, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        bgcolor="#48BB78",
                        border_radius=5,
                    ),
                    ft.Text("{:.1f} µg/m³".format(air.o3), size=14, color="#4A5568"),
                ],
                spacing=10,
            ),
            ft.Row(
                [
                    ft.Container(
                        content=ft.Text("NO₂", size=12, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        bgcolor="#ED8936",
                        border_radius=5,
                    ),
                    ft.Text("{:.1f} µg/m³".format(air.no2), size=14, color="#4A5568"),
                ],
                spacing=10,
            ),
            ft.Row(
                [
                    ft.Container(
                        content=ft.Text("CO", size=12, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        bgcolor="#E53E3E",
                        border_radius=5,
                    ),
                    ft.Text("{:.1f} µg/m³".format(air.co), size=14, color="#4A5568"),
                ],
                spacing=10,
            ),
        ]
        self.page.update()

    def _build_watch_card(self, weather: WeatherData) -> ft.Control:
        unit_symbol = "°C" if self.units == "metric" else "°F"
        wind_unit = "m/s" if self.units == "metric" else "mph"
        
        # Calculate current time for this city
        tz = timezone(timedelta(seconds=weather.timezone_offset))
        current_time = datetime.now(tz)
        time_str = current_time.strftime('%I:%M %p')
        
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text(
                                        f"{weather.city}, {weather.country}",
                                        size=18,
                                        weight=ft.FontWeight.BOLD,
                                        color="#2D3748",
                                    ),
                                    ft.Text(
                                        f"🕐 {time_str}",
                                        size=13,
                                        color="#718096",
                                    ),
                                ],
                                spacing=2,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.CLOSE,
                                tooltip="Remove city",
                                icon_size=20,
                                on_click=lambda e, city=weather.city: self._handle_remove_city(city),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text(
                                        f"{weather.temperature:.1f}{unit_symbol}",
                                        size=36,
                                        weight=ft.FontWeight.BOLD,
                                        color="#2D3748",
                                    ),
                                    ft.Text(
                                        weather.description,
                                        size=14,
                                        color="#718096",
                                    ),
                                ],
                                spacing=5,
                            ),
                            ft.Image(
                                src=f"https://openweathermap.org/img/wn/{weather.icon}@2x.png",
                                width=64,
                                height=64,
                            ),
                            ft.Column(
                                [
                                    ft.Row(
                                        [
                                            ft.Icon(ft.Icons.WATER_DROP, size=16, color="#4299E1"),
                                            ft.Text(f"{weather.humidity}%", size=13, color="#4A5568"),
                                        ],
                                        spacing=5,
                                    ),
                                    ft.Row(
                                        [
                                            ft.Icon(ft.Icons.AIR, size=16, color="#48BB78"),
                                            ft.Text(f"{weather.wind_speed:.1f} {wind_unit}", size=13, color="#4A5568"),
                                        ],
                                        spacing=5,
                                    ),
                                ],
                                spacing=8,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        spacing=15,
                    ),
                ],
                spacing=10,
            ),
            padding=20,
            bgcolor="#FFFFFF",
            border_radius=12,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=8,
                color="#00000008",
                offset=ft.Offset(0, 2),
            ),
        )

    # ------------------------------------------------------------------ Misc helpers
    def _show_status(self, message: str, success: bool = False) -> None:
        self.status_text.value = message
        self.status_text.color = "#FFFFFF" if success else "#FFF5F5"
        self.page.update()

    def _set_loading(self, is_loading: bool) -> None:
        self.loading_overlay.visible = is_loading
        self.search_button.disabled = is_loading
        self.city_field.disabled = is_loading
        self.page.update()

    def _format_countdown(
        self, sunrise: datetime, sunset: datetime, tz: timezone
    ) -> str:
        now = datetime.now(tz)
        if now < sunrise:
            delta = sunrise - now
            label = "Sunrise in"
        elif now < sunset:
            delta = sunset - now
            label = "Sunset in"
        else:
            next_sunrise = sunrise + timedelta(days=1)
            delta = next_sunrise - now
            label = "Next sunrise in"
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes = remainder // 60
        return f"{label} {hours}h {minutes}m"

    def _update_solar_section(self) -> None:
        if not self.current_weather:
            self.sunrise_text.value = "--:--"
            self.sunset_text.value = "--:--"
            self.countdown_text.value = "Search for a city to start the countdown."
            return

        weather = self.current_weather
        tz = timezone(timedelta(seconds=weather.timezone_offset))
        sunrise_local = weather.sunrise.astimezone(tz)
        sunset_local = weather.sunset.astimezone(tz)
        self.sunrise_text.value = sunrise_local.strftime("%I:%M %p")
        self.sunset_text.value = sunset_local.strftime("%I:%M %p")
        self.countdown_text.value = self._format_countdown(sunrise_local, sunset_local, tz)

    async def _countdown_loop(self) -> None:
        while True:
            await asyncio.sleep(30)
            previous = self.countdown_text.value
            self._update_solar_section()
            if self.countdown_text.value != previous:
                self.page.update()

    def _aqi_label_color(self, aqi: int) -> tuple[str, str]:
        scale = {
            1: ("Good", "#48BB78"),
            2: ("Fair", "#68D391"),
            3: ("Moderate", "#ECC94B"),
            4: ("Poor", "#F6AD55"),
            5: ("Very Poor", "#FC8181"),
        }
        return scale.get(aqi, ("Unknown", "#A0AEC0"))

    def _load_watchlist(self) -> list[str]:
        if not self.watchlist_file.exists():
            return []
        try:
            return json.loads(self.watchlist_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []

    def _save_watchlist(self) -> None:
        self.watchlist_file.write_text(json.dumps(self.watchlist, indent=2), encoding="utf-8")

    def _update_hourly_forecast(self) -> None:
        """Update hourly forecast display."""
        if not self.hourly_forecast:
            self.hourly_scroll.controls = [
                ft.Text("Search for a city to see hourly forecast", color="#718096")
            ]
            self.page.update()
            return

        unit_symbol = "°C" if self.units == "metric" else "°F"
        cards = []
        
        for hour_data in self.hourly_forecast[:12]:  # Show next 12 hours
            cards.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                hour_data["time"],
                                size=13,
                                weight=ft.FontWeight.BOLD,
                                color="#4A5568",
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Image(
                                src=f"https://openweathermap.org/img/wn/{hour_data['icon']}@2x.png",
                                width=50,
                                height=50,
                            ),
                            ft.Text(
                                f"{hour_data['temp']:.0f}{unit_symbol}",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color="#2D3748",
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Row(
                                [
                                    ft.Icon(ft.Icons.WATER_DROP, size=14, color="#4299E1"),
                                    ft.Text(f"{hour_data['humidity']}%", size=12, color="#718096"),
                                ],
                                spacing=3,
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                        ],
                        spacing=5,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=15,
                    bgcolor="#F7FAFC",
                    border_radius=12,
                    border=ft.border.all(1, "#E2E8F0"),
                    width=100,
                )
            )
        
        self.hourly_scroll.controls = cards
        self.page.update()

    def _update_recommendations(self, weather: WeatherData) -> None:
        """Generate smart weather recommendations."""
        recommendations = []
        
        # Temperature-based recommendations
        temp = weather.temperature
        feels = weather.feels_like
        
        if temp > 30:
            recommendations.append(
                self._create_recommendation_chip(
                    "🌡️ Hot day ahead",
                    "Stay hydrated and seek shade",
                    "#FED7D7"
                )
            )
        elif temp < 10:
            recommendations.append(
                self._create_recommendation_chip(
                    "🧥 Bundle up",
                    "Wear warm clothing",
                    "#BEE3F8"
                )
            )
        
        # Feels like difference
        if abs(feels - temp) > 5:
            if feels > temp:
                recommendations.append(
                    self._create_recommendation_chip(
                        "🌡️ Feels warmer",
                        f"Humidity makes it feel like {feels:.0f}°",
                        "#FED7D7"
                    )
                )
            else:
                recommendations.append(
                    self._create_recommendation_chip(
                        "❄️ Feels colder",
                        f"Wind chill makes it feel like {feels:.0f}°",
                        "#BEE3F8"
                    )
                )
        
        # Weather condition recommendations
        condition = weather.description.lower()
        icon_code = weather.icon
        
        if "rain" in condition or "drizzle" in condition:
            recommendations.append(
                self._create_recommendation_chip(
                    "☔ Bring an umbrella",
                    "Rain expected today",
                    "#BEE3F8"
                )
            )
        elif "clear" in condition and "d" in icon_code:  # Daytime clear
            recommendations.append(
                self._create_recommendation_chip(
                    "☀️ Sunny day",
                    "Don't forget sunscreen",
                    "#FEF5E7"
                )
            )
        elif "cloud" in condition:
            recommendations.append(
                self._create_recommendation_chip(
                    "☁️ Cloudy skies",
                    "Good day for outdoor activities",
                    "#E6FFFA"
                )
            )
        elif "snow" in condition:
            recommendations.append(
                self._create_recommendation_chip(
                    "❄️ Snowy weather",
                    "Drive carefully and dress warmly",
                    "#E6F7FF"
                )
            )
        elif "storm" in condition or "thunder" in condition:
            recommendations.append(
                self._create_recommendation_chip(
                    "⚡ Thunderstorm alert",
                    "Stay indoors if possible",
                    "#FED7D7"
                )
            )
        
        # Humidity recommendations
        if weather.humidity > 80:
            recommendations.append(
                self._create_recommendation_chip(
                    "💧 High humidity",
                    "May feel muggy outside",
                    "#E6FFFA"
                )
            )
        elif weather.humidity < 30:
            recommendations.append(
                self._create_recommendation_chip(
                    "🏜️ Low humidity",
                    "Use moisturizer for dry skin",
                    "#FEF5E7"
                )
            )
        
        # Wind recommendations
        if weather.wind_speed > 10:  # m/s or mph depending on units
            recommendations.append(
                self._create_recommendation_chip(
                    "💨 Windy conditions",
                    "Secure loose objects",
                    "#E6F7FF"
                )
            )
        
        # Time-based recommendations
        tz = timezone(timedelta(seconds=weather.timezone_offset))
        current_time = datetime.now(tz)
        hour = current_time.hour
        
        if 20 <= hour or hour < 6:  # Night time
            recommendations.append(
                self._create_recommendation_chip(
                    "🌙 Evening/Night",
                    "Good time for stargazing" if "clear" in condition else "Stay cozy indoors",
                    "#E6E6FA"
                )
            )
        
        # If pleasant weather
        if 18 <= temp <= 26 and weather.humidity < 70 and "clear" in condition:
            recommendations.append(
                self._create_recommendation_chip(
                    "✨ Perfect weather",
                    "Great day for outdoor activities!",
                    "#C6F6D5"
                )
            )
        
        self.recommendations_column.controls = recommendations[:4]  # Show max 4
        self.page.update()

    def _create_recommendation_chip(self, title: str, subtitle: str, bg_color: str) -> ft.Control:
        """Create a recommendation chip with icon and text."""
        return ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(title, size=14, weight=ft.FontWeight.BOLD, color="#2D3748"),
                            ft.Text(subtitle, size=13, color="#4A5568"),
                        ],
                        spacing=2,
                    ),
                ],
                spacing=10,
            ),
            padding=12,
            bgcolor=bg_color,
            border_radius=10,
            border=ft.border.all(1, "#E2E8F0"),
        )


def main(page: ft.Page) -> None:
    WeatherApp(page)


if __name__ == "__main__":
    ft.app(target=main)


