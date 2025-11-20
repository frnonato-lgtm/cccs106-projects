# weather_service.py
"""Weather API service layer."""

import httpx
from typing import Dict, Optional
from config import Config


class WeatherServiceError(Exception):
    """Custom exception for weather service errors."""
    pass


class WeatherService:
    """Service for fetching weather data from OpenWeatherMap API."""
    
    def __init__(self):
        self.api_key = Config.API_KEY
        self.base_url = Config.BASE_URL
        self.timeout = Config.TIMEOUT
    
    async def _fetch_data(self, url: str, params: Dict) -> Dict:
        """Internal helper to handle HTTP request and error handling."""
        try:
            # Make async HTTP request
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                
                # Check for HTTP errors
                if response.status_code == 404:
                    city_name = params.get("q", "location")
                    raise WeatherServiceError(
                        f"City or {city_name} not found. Please check the spelling."
                    )
                elif response.status_code == 401:
                    raise WeatherServiceError(
                        "Invalid API key. Please check your configuration."
                    )
                elif response.status_code >= 500:
                    raise WeatherServiceError(
                        "Weather service is currently unavailable. "
                        "Please try again later."
                    )
                elif response.status_code != 200:
                    raise WeatherServiceError(
                        f"Error fetching data: {response.status_code}"
                    )
                
                # Parse JSON response
                return response.json()
                
        except httpx.TimeoutException:
            raise WeatherServiceError(
                "Request timed out. Please check your internet connection."
            )
        except httpx.NetworkError:
            raise WeatherServiceError(
                "Network error. Please check your internet connection."
            )
        except httpx.HTTPError as e:
            raise WeatherServiceError(f"HTTP error occurred: {str(e)}")
        except Exception as e:
            raise WeatherServiceError(f"An unexpected error occurred: {str(e)}")

    async def get_weather(self, city: str, unit: str) -> Dict:
        """
        Fetch weather data for a given city.
        
        Args:
            city: Name of the city
            
        Returns:
            Dictionary containing weather data
            
        Raises:
            WeatherServiceError: If the request fails
        """
        if not city:
            raise WeatherServiceError("City name cannot be empty")
        
        # Build request parameters
        params = {
            "q": city,
            "appid": self.api_key,
            "units": unit,
        }
        
        # Use the unified fetcher
        return await self._fetch_data(self.base_url, params)
        
    async def get_weather_by_coordinates(
        self, 
        lat: float, 
        lon: float,
        unit: str = Config.UNITS
    ) -> Dict:
        """
        Fetch weather data by coordinates.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Dictionary containing weather data
        """
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": unit,
        }
        
        # Use the unified fetcher
        return await self._fetch_data(self.base_url, params)

    async def get_forecast(self, city: str, unit: str) -> Dict:
        """Get 5-day forecast."""
        forecast_url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {
            "q": city,
            "appid": self.api_key,
            "units": unit,
        }
        
        # Use the unified fetcher
        return await self._fetch_data(forecast_url, params)