# main.py
"""Weather Application using Flet v0.28.3"""

import flet as ft
from weather_service import WeatherService
from config import Config
import asyncio
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict


class WeatherApp:
    """Main Weather Application class."""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.weather_service = WeatherService()
        self.history_file = Path("search_history.json")
        self.settings_file = Path("settings.json")
        self.search_history = self.load_history()
        self.settings = self.load_settings()
        self.current_unit = self.settings.get("unit", "metric")
        
        # UI controls for dynamic updates
        self.current_temp = None
        self.feels_like = None
        self.wind_speed = None
        self.current_city = None
        
        # Flet controls need to be explicitly managed for color and updates
        self.temp_text = ft.Text("", size=48, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900)
        self.feels_like_text = ft.Text("", size=16, color=ft.Colors.GREY_700)
        self.wind_value_text = ft.Text("", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900)
        self.desc_text = ft.Text("", size=20, italic=True)
        self.icon_image = ft.Image(width=100, height=100)
        self.city_text = ft.Text("", size=24, weight=ft.FontWeight.BOLD)

        self.setup_page()
        self.build_ui()
    
    def load_history(self):
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []

    def save_history(self):
        with open(self.history_file, 'w') as f:
            json.dump(self.search_history, f)

    def load_settings(self):
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                pass
        return {"unit": "metric"}

    def save_settings(self):
        with open(self.settings_file, "w") as f:
            json.dump({"unit": self.current_unit}, f)

    def add_to_history(self, city: str):
        if city in self.search_history:
            self.search_history.remove(city)
            
        self.search_history.insert(0, city)
        self.search_history = self.search_history[:10]
        self.save_history()
        self.update_history_dropdown()
        
    def setup_page(self):
        """Configure page settings."""
        self.page.title = Config.APP_TITLE
        
        # Add theme switcher
        self.page.theme_mode = ft.ThemeMode.LIGHT

        # Custom theme Colors
        self.page.theme = ft.Theme(
            color_scheme_seed=ft.Colors.BLUE,
        )
        
        self.page.padding = 20
        self.page.window.width = Config.APP_WIDTH
        self.page.window.height = Config.APP_HEIGHT
        self.page.window.resizable = False
        
        # Center the window on desktop
        self.page.window.center()
        
    def build_ui(self):
        """Build the user interface."""
        # Title
        self.title = ft.Text(
            "Weather App",
            size=32,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLUE_700,
        )
        
        # Theme toggle button
        self.theme_button = ft.IconButton(
            icon=ft.Icons.DARK_MODE,
            tooltip="Toggle theme",
            icon_size=28,
            icon_color=ft.Colors.GREY_400,
            on_click=self.toggle_theme,
        )
        
        initial_switch_color = ft.Colors.BLUE_700 if self.page.theme_mode == ft.ThemeMode.LIGHT else ft.Colors.GREY_400

        self.unit_switch = ft.Switch(
            value=(self.current_unit == "imperial"),
            on_change=self.toggle_units,
            active_color=initial_switch_color,
            width=50,
            height=30,
        )
        
        self.unit_toggle = ft.Row(
            [
                ft.Text("°C", size=16, weight=ft.FontWeight.BOLD),
                self.unit_switch,
                ft.Text("°F", size=16, weight=ft.FontWeight.BOLD),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=5,
        )

        title_row = ft.Row(
            [
                self.title,
                ft.Row([self.unit_toggle, self.theme_button]),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        
        self.city_input = ft.TextField(
            label="Enter city name",
            expand=True,
            hint_text="e.g., London, Tokyo, New York",
            border_color=ft.Colors.BLUE_400,
            prefix_icon=ft.Icons.LOCATION_CITY,
            autofocus=True,
            on_submit=self.on_search,
        )
        
        self.search_button = ft.ElevatedButton(
            "Get Weather",
            icon=ft.Icons.SEARCH,
            on_click=self.on_search,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE_700,
            ),
        )

        self.history_dropdown = ft.Dropdown(
            label="Search History",
            width=120,
            text_style=ft.TextStyle(size=14),
            label_style=ft.TextStyle(size=12),
            border_color=ft.Colors.BLUE_400,
            options=[ft.dropdown.Option(city) for city in self.search_history],
            on_change=self.on_history_select,
        )

        self.weather_container = ft.Container(
            visible=False,
            bgcolor=ft.Colors.BLUE_50,
            border_radius=10,
            padding=20,
        )

        self.forecast_container = ft.Container(
            visible=False,
            bgcolor=ft.Colors.BLUE_50,
            border_radius=10,
            padding=20,
        )
        
        self.weather_container.content = self._build_weather_content()
        self.forecast_container.content = ft.Column([])
        
        self.error_message = ft.Text(
            "",
            color=ft.Colors.RED_700,
            visible=False,
        )
        
        self.loading = ft.ProgressRing(visible=False)
        
        self.page.add(
            ft.Container(
                expand=True,
                # Add horizontal padding to create space for the scrollbar inside the window edge
                padding=ft.padding.only(left=5, right=5), 
                content=ft.Column(
                    [
                        title_row,
                        ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                        ft.Row(
                            [
                                self.city_input,
                                self.history_dropdown,
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        self.search_button,
                        ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                        self.loading,
                        self.error_message,
                        ft.Column(
                            [
                                self.weather_container,
                                self.forecast_container,
                            ],
                            scroll=ft.ScrollMode.AUTO,
                            expand=True,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10,
                ),
            )
        )

    def _build_weather_content(self):
        """Builds the content for the main weather display."""
        # Info card controls
        humidity_card = self.create_info_card(
            ft.Icons.WATER_DROP,
            "Humidity",
            ft.Text(f"0%", 
                    size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900)
        )
        wind_card = self.create_info_card(
            ft.Icons.AIR,
            "Wind Speed",
            self.wind_value_text 
        )

        return ft.Column(
            [
                self.city_text,
                
                ft.Row(
                    [
                        self.icon_image,
                        self.desc_text,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                
                self.temp_text, 
                self.feels_like_text, 
                
                ft.Divider(),
                
                ft.Row(
                    [
                        humidity_card,
                        wind_card,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )
    
    def update_history_dropdown(self):
        self.history_dropdown.options = [ft.dropdown.Option(c) for c in self.search_history]
        self.page.update()

    def on_history_select(self, e):
        self.city_input.value = self.history_dropdown.value
        self.page.update()
        self.on_search(None)
    
    def on_search(self, e):
        """Handle search button click or enter key press."""
        self.page.run_task(self.get_weather)
    
    async def get_weather(self):
        """Fetch and display weather data."""
        city = self.city_input.value.strip()
        
        if not city:
            self.show_error("Please enter a city name")
            return
        
        self.loading.visible = True
        self.error_message.visible = False
        self.weather_container.visible = False
        self.forecast_container.visible = False
        self.page.update()
        
        try:
            weather_data = await self.weather_service.get_weather(city, self.current_unit)
            
            self.current_city = city 
            
            forecast_data = await self.weather_service.get_forecast(city, self.current_unit)
            self.add_to_history(city)
            await self.display_weather(weather_data)
            await self.display_forecast(forecast_data)
            
        except Exception as e:
            self.show_error(str(e))
        
        finally:
            self.loading.visible = False
            self.page.update()

    async def display_weather(self, data: dict):
        """Display weather information."""
        city_name = data.get("name", "Unknown")
        country = data.get("sys", {}).get("country", "")
        temp = data.get("main", {}).get("temp", 0)
        feels_like = data.get("main", {}).get("feels_like", 0)
        humidity = data.get("main", {}).get("humidity", 0)
        description = data.get("weather", [{}])[0].get("description", "").title()
        icon_code = data.get("weather", [{}])[0].get("icon", "01d")
        wind_speed = data.get("wind", {}).get("speed", 0)
        
        # Store raw values for unit conversion
        self.current_temp = temp
        self.feels_like = feels_like
        self.wind_speed = wind_speed
        self.humidity = humidity

        unit_symbol = "°C" if self.current_unit == "metric" else "°F"
        wind_unit = "m/s" if self.current_unit == "metric" else "mph"
        
        # Update text controls directly.
        self.city_text.value = f"{city_name}, {country}"
        self.city_text.color = ft.Colors.BLACK 
        
        self.icon_image.src = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"
        
        self.desc_text.value = description
        self.desc_text.color = ft.Colors.BLACK

        self.temp_text.value = f"{temp:.1f}{unit_symbol}"
        self.feels_like_text.value = f"Feels like {feels_like:.1f}{unit_symbol}"
        self.feels_like_text.color = ft.Colors.GREY_700

        self.wind_value_text.value = f"{wind_speed:.1f} {wind_unit}"
        self.wind_value_text.color = ft.Colors.BLUE_900

        # Update Humidity Text Control
        humidity_card = self.weather_container.content.controls[5].controls[0]
        humidity_value_control = humidity_card.content.controls[2]
        if isinstance(humidity_value_control, ft.Text):
             humidity_value_control.value = f"{humidity}%"

        self.weather_container.animate_opacity = 300
        self.weather_container.opacity = 0
        self.weather_container.visible = True
        self.page.update()

        await asyncio.sleep(0.1)
        self.weather_container.opacity = 1
        self.page.update()

    async def display_forecast(self, data: dict):
        """Display 5-day forecast."""
        unit_symbol = "°C" if self.current_unit == "metric" else "°F"

        # Aggregate by date
        daily_forecast = defaultdict(list)
        for item in data.get("list", []):
            dt_txt = item.get("dt_txt", "")
            date_str = dt_txt.split(" ")[0]
            daily_forecast[date_str].append(item)

        forecast_cards = []

        for date_str, items in list(daily_forecast.items())[:5]:
            temps = [i.get("main", {}).get("temp", 0) for i in items]
            
            first_item = items[0]
            icon = first_item.get("weather", [{}])[0].get("icon", "01d")
            description = first_item.get("weather", [{}])[0].get("description", "").title()
            
            high_temp = max(temps)
            low_temp = min(temps)
            
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            date_label = date_obj.strftime("%a, %b %d")

            # Fixed text colors for dark mode readability
            card = ft.Container(
                content=ft.Row(
                    [
                        ft.Text(date_label, size=16, weight=ft.FontWeight.BOLD, width=80, color=ft.Colors.BLACK),
                        ft.Image(
                            src=f"https://openweathermap.org/img/wn/{icon}@2x.png",
                            width=30,
                            height=30,
                        ),
                        ft.Text(description, size=14, italic=True, expand=True, color=ft.Colors.BLACK),
                        ft.Text(f"H: {high_temp:.1f}{unit_symbol}", size=14, color=ft.Colors.BLACK),
                        ft.Text(f"L: {low_temp:.1f}{unit_symbol}", size=14, color=ft.Colors.BLACK),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    spacing=10,
                ),
                bgcolor=ft.Colors.WHITE,
                padding=10,
                border_radius=10,
                margin=ft.margin.only(bottom=5),
            )
            forecast_cards.append(card)

        self.forecast_container.content.controls.clear()
        self.forecast_container.content.controls.extend(
            [ft.Text("5-Day Forecast", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900), ft.Divider()] + forecast_cards
        )
        self.forecast_container.visible = True
        self.page.update()

    def create_info_card(self, icon, label, value):
        """Create an info card for weather details."""
        # Value is passed as a control or a string. If string, it's converted to a control.
        value_control = value if isinstance(value, ft.Control) else ft.Text(
            value,
            size=16,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLUE_900,
        )
        
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(icon, size=30, color=ft.Colors.BLUE_700),
                    ft.Text(label, size=12, color=ft.Colors.GREY_600),
                    value_control,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            ),
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            padding=15,
            width=150,
        )
    
    def show_error(self, message: str):
        """Display error message."""
        self.error_message.value = f"❌ {message}"
        self.error_message.visible = True
        self.weather_container.visible = False
        self.forecast_container.visible = False
        self.page.update()

    def toggle_theme(self, e):
        """Toggle between light and dark theme."""
        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.theme_button.icon = ft.Icons.LIGHT_MODE
            self.theme_button.icon_color = ft.Colors.BLUE_700
            self.unit_switch.active_color = ft.Colors.BLUE_700
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.theme_button.icon = ft.Icons.DARK_MODE
            self.theme_button.icon_color = ft.Colors.GREY_400
            self.unit_switch.active_color = ft.Colors.GREY_400
        self.page.update()

    async def update_forecast_display(self):
        """Fetches and displays new forecast data based on the current unit."""
        if self.current_city and self.forecast_container.visible:
            try:
                # Re-fetch forecast data with the new unit
                forecast_data = await self.weather_service.get_forecast(self.current_city, self.current_unit)
                await self.display_forecast(forecast_data)
            except Exception as e:
                # Show an error but don't hide the current weather
                self.show_error("Could not refresh forecast units.")
                self.page.update()


    def toggle_units(self, e):
        if not self.weather_container.visible or self.current_temp is None:
            return
    
        old_unit = self.current_unit
        self.current_unit = "imperial" if e.control.value else "metric"
        self.save_settings()

        # Animate current weather temperature conversion
        self.weather_container.animate_opacity = 200
        self.weather_container.opacity = 0
        self.page.update()

        # Perform the conversion math
        if old_unit == "metric":
            self.current_temp = (self.current_temp * 9/5) + 32
            self.feels_like = (self.feels_like * 9/5) + 32
            self.wind_speed = self.wind_speed * 2.237
        else:
            self.current_temp = (self.current_temp - 32) * 5/9
            self.feels_like = (self.feels_like - 32) * 5/9
            self.wind_speed = self.wind_speed / 2.237

        unit_symbol = "°C" if self.current_unit == "metric" else "°F"
        wind_unit = "m/s" if self.current_unit == "metric" else "mph"

        # Update displayed values for current weather
        self.temp_text.value = f"{self.current_temp:.1f}{unit_symbol}"
        self.feels_like_text.value = f"Feels like {self.feels_like:.1f}{unit_symbol}"
        self.wind_value_text.value = f"{self.wind_speed:.1f} {wind_unit}"

        # Animate current weather back in
        self.weather_container.opacity = 1
        self.page.update()
        
        # Update the 5-day forecast unit by re-fetching data
        self.page.run_task(self.update_forecast_display)


def main(page: ft.Page):
    """Main entry point."""
    WeatherApp(page)


if __name__ == "__main__":
    ft.app(target=main)