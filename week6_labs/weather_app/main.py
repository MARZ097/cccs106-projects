from __future__ import annotations

import asyncio
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import flet as ft

from .models import AirQualityData, WeatherData
from .services import WeatherService, WeatherServiceError


class WeatherApp:
    """Flet-based weather dashboard with multiple enhancements."""

    def __init__(self, page: ft.Page) -> None:
        self.page = page
        self.service = WeatherService()
        self.units = "metric"
        self.current_weather: WeatherData | None = None
        self.current_air: AirQualityData | None = None

        self.storage_dir = Path(__file__).parent / "data"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.watchlist_file = self.storage_dir / "watchlist.json"
        self.watchlist: list[str] = self._load_watchlist()

        self._build_ui()
        self.page.run_task(self._refresh_watchlist)
        self.page.run_task(self._countdown_loop)

    # ------------------------------------------------------------------ UI setup
    def _build_ui(self) -> None:
        page = self.page
        page.title = "Module 6 Weather Application"
        page.padding = 20
        page.bgcolor = ft.colors.BLUE_GREY_50
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.scroll = ft.ScrollMode.AUTO

        self.status_text = ft.Text("", color=ft.colors.RED_400)
        self.city_field = ft.TextField(
            label="Enter city",
            hint_text="e.g., Manila, Tokyo, Paris",
            autofocus=True,
            on_submit=self._handle_search,
            expand=True,
        )
        self.search_button = ft.FilledButton(
            text="Search", icon=ft.icons.SEARCH, on_click=self._handle_search
        )
        self.add_watch_button = ft.OutlinedButton(
            text="Add to comparison",
            icon=ft.icons.LIST,
            disabled=True,
            on_click=self._handle_add_watchlist,
        )

        self.main_icon = ft.Image(width=160, height=160, fit=ft.ImageFit.CONTAIN)
        self.temp_text = ft.Text(size=48, weight=ft.FontWeight.BOLD)
        self.description_text = ft.Text(size=20)
        self.details_column = ft.Column(spacing=4)
        self.sunrise_text = ft.Text()
        self.sunset_text = ft.Text()
        self.countdown_text = ft.Text(weight=ft.FontWeight.BOLD)

        self.air_chip = ft.Chip(label="AQI", bgcolor=ft.colors.BLUE_GREY_100)
        self.air_details = ft.Column(spacing=2)

        self.watchlist_column = ft.Column(spacing=10, expand=True)

        self.loading_overlay = ft.ProgressBar(width=page.width or 400, visible=False)

        page.add(
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.ResponsiveRow(
                            [
                                ft.Column(
                                    [
                                        ft.Row([self.city_field, self.search_button], expand=True),
                                        self.status_text,
                                    ],
                                    col={"sm": 12, "md": 8},
                                ),
                                ft.Column(
                                    [
                                        self.add_watch_button,
                                        ft.TextButton(
                                            "Toggle °C / °F",
                                            icon=ft.icons.SYNC_ALT,
                                            on_click=self._handle_unit_toggle,
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.START,
                                    col={"sm": 12, "md": 4},
                                ),
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.START,
                        ),
                        ft.Divider(),
                        self._build_main_card(),
                        ft.Divider(),
                        self._build_air_quality_card(),
                        ft.Divider(),
                        ft.Text("Multiple Cities Comparison", size=20, weight=ft.FontWeight.BOLD),
                        ft.Text(
                            "Keep a watchlist of other locations and compare them side by side.",
                            color=ft.colors.BLUE_GREY_600,
                        ),
                        ft.Container(
                            content=self.watchlist_column,
                            padding=10,
                            bgcolor=ft.colors.WHITE,
                            border_radius=10,
                            ink=False,
                        ),
                        self.loading_overlay,
                    ],
                    tight=True,
                    spacing=20,
                ),
                width=900,
            )
        )

    def _build_main_card(self) -> ft.Control:
        """Card displaying the currently searched city's weather."""
        return ft.Card(
            content=ft.Container(
                padding=20,
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Column(
                                    [self.temp_text, self.description_text, self.details_column],
                                    alignment=ft.MainAxisAlignment.START,
                                    expand=True,
                                ),
                                self.main_icon,
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.Row(
                            [
                                ft.Column(
                                    [
                                        ft.Text("Sunrise", weight=ft.FontWeight.BOLD),
                                        self.sunrise_text,
                                    ]
                                ),
                                ft.Column(
                                    [
                                        ft.Text("Sunset", weight=ft.FontWeight.BOLD),
                                        self.sunset_text,
                                    ]
                                ),
                                ft.Column(
                                    [
                                        ft.Text("Countdown", weight=ft.FontWeight.BOLD),
                                        self.countdown_text,
                                    ]
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_AROUND,
                        ),
                    ],
                    spacing=20,
                ),
            )
        )

    def _build_air_quality_card(self) -> ft.Control:
        """Card containing air quality metrics."""
        return ft.Card(
            content=ft.Container(
                padding=20,
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text("Air Quality", size=20, weight=ft.FontWeight.BOLD),
                                self.air_chip,
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        self.air_details,
                    ],
                    spacing=10,
                ),
            )
        )

    # ------------------------------------------------------------------ Event handlers
    def _handle_search(self, e: ft.ControlEvent) -> None:
        city = self.city_field.value.strip()
        if not city:
            self._show_status("Please enter a city name.")
            return
        self.page.run_task(self._fetch_weather, city)

    def _handle_unit_toggle(self, e: ft.ControlEvent) -> None:
        self.units = "imperial" if self.units == "metric" else "metric"
        if self.current_weather:
            self.page.run_task(self._fetch_weather, self.current_weather.city)
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
        except WeatherServiceError as exc:
            self._show_status(str(exc))
            self._set_loading(False)
            return

        self.current_weather = weather
        self.current_air = air
        self._update_weather_display()
        self._update_air_quality()
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
        self.description_text.value = f"{weather.city}, {weather.country} · {weather.description}"
        self.main_icon.src = f"https://openweathermap.org/img/wn/{weather.icon}@4x.png"

        self.details_column.controls = [
            ft.Text(f"Humidity: {weather.humidity}%"),
            ft.Text(f"Wind: {weather.wind_speed:.1f} {wind_unit}"),
        ]

        self._update_solar_section()

        self.add_watch_button.disabled = False
        self._show_status(f"Updated weather for {weather.city}.", success=True)
        self.page.update()

    def _update_air_quality(self) -> None:
        if not self.current_air:
            self.air_chip.label = "AQI — unavailable"
            self.air_details.controls = []
            self.page.update()
            return

        air = self.current_air
        label, color = self._aqi_label_color(air.aqi)
        self.air_chip.label = f"AQI {air.aqi} · {label}"
        self.air_chip.bgcolor = color

        self.air_details.controls = [
            ft.Text("Fine particulates (PM2.5): {:.1f} µg/m³".format(air.pm2_5)),
            ft.Text("Coarse particulates (PM10): {:.1f} µg/m³".format(air.pm10)),
            ft.Text("Ozone (O₃): {:.1f} µg/m³".format(air.o3)),
            ft.Text("Nitrogen dioxide (NO₂): {:.1f} µg/m³".format(air.no2)),
            ft.Text("Carbon monoxide (CO): {:.1f} µg/m³".format(air.co)),
        ]
        self.page.update()

    def _build_watch_card(self, weather: WeatherData) -> ft.Control:
        unit_symbol = "°C" if self.units == "metric" else "°F"
        return ft.Card(
            content=ft.Container(
                padding=15,
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text(
                                    f"{weather.city}, {weather.country}",
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.IconButton(
                                    icon=ft.icons.DELETE,
                                    tooltip="Remove city",
                                    on_click=lambda e, city=weather.city: self._handle_remove_city(
                                        city
                                    ),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.Row(
                            [
                                ft.Text(f"{weather.temperature:.1f}{unit_symbol}", size=32),
                                ft.Image(
                                    src=f"https://openweathermap.org/img/wn/{weather.icon}@2x.png",
                                    width=72,
                                    height=72,
                                ),
                                ft.Column(
                                    [
                                        ft.Text(weather.description),
                                        ft.Text(f"Humidity: {weather.humidity}%"),
                                        ft.Text(f"Wind: {weather.wind_speed:.1f}"),
                                    ]
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            spacing=20,
                        ),
                    ]
                ),
            )
        )

    # ------------------------------------------------------------------ Misc helpers
    def _show_status(self, message: str, success: bool = False) -> None:
        self.status_text.value = message
        self.status_text.color = ft.colors.GREEN_600 if success else ft.colors.RED_400
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
            1: ("Good", ft.colors.GREEN_200),
            2: ("Fair", ft.colors.LIGHT_GREEN_300),
            3: ("Moderate", ft.colors.AMBER_200),
            4: ("Poor", ft.colors.ORANGE_200),
            5: ("Very Poor", ft.colors.RED_200),
        }
        return scale.get(aqi, ("Unknown", ft.colors.BLUE_GREY_100))

    def _load_watchlist(self) -> list[str]:
        if not self.watchlist_file.exists():
            return []
        try:
            return json.loads(self.watchlist_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []

    def _save_watchlist(self) -> None:
        self.watchlist_file.write_text(json.dumps(self.watchlist, indent=2), encoding="utf-8")


def main(page: ft.Page) -> None:
    WeatherApp(page)


if __name__ == "__main__":
    ft.app(target=main)


