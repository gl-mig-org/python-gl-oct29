import requests
from config import Config

WEATHER_CODES = {
    0: ("Clear sky", "☀️"), 1: ("Mainly clear", "🌤️"), 2: ("Partly cloudy", "⛅"),
    3: ("Overcast", "☁️"), 45: ("Fog", "🌫️"), 48: ("Rime fog", "🌫️"),
    51: ("Light drizzle", "🌦️"), 53: ("Drizzle", "🌦️"), 55: ("Heavy drizzle", "🌧️"),
    61: ("Light rain", "🌦️"), 63: ("Rain", "🌧️"), 65: ("Heavy rain", "🌧️"),
    71: ("Light snow", "🌨️"), 73: ("Snow", "🌨️"), 75: ("Heavy snow", "❄️"),
    80: ("Rain showers", "🌦️"), 81: ("Rain showers", "🌧️"), 82: ("Violent showers", "⛈️"),
    95: ("Thunderstorm", "⛈️"), 96: ("Thunderstorm with hail", "⛈️"), 99: ("Severe thunderstorm", "⛈️"),
}


class WeatherError(Exception):
    """Raised when weather data can't be retrieved."""


def get_coordinates(city: str) -> dict:
    """Convert a city name into latitude and longitude."""
    resp = requests.get(
        Config.GEOCODING_URL,
        params={"name": city, "count": 1, "language": "en", "format": "json"},
        timeout=Config.REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    results = resp.json().get("results")
    if not results:
        raise WeatherError(f"City '{city}' not found.")
    r = results[0]
    return {
        "name": r["name"],
        "country": r.get("country", ""),
        "latitude": r["latitude"],
        "longitude": r["longitude"],
    }


def get_weather(city: str) -> dict:
    """Return the current weather for a city."""
    try:
        loc = get_coordinates(city)
        resp = requests.get(
            Config.FORECAST_URL,
            params={
                "latitude": loc["latitude"],
                "longitude": loc["longitude"],
                "current": "temperature_2m,apparent_temperature,relative_humidity_2m,"
                           "wind_speed_10m,weather_code",
                "timezone": "auto",
            },
            timeout=Config.REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
    except requests.RequestException as exc:
        raise WeatherError("Weather service is unavailable. Please try again.") from exc

    current = resp.json()["current"]
    description, icon = WEATHER_CODES.get(current["weather_code"], ("Unknown", "❔"))

    return {
        "city": loc["name"],
        "country": loc["country"],
        "temperature": current["temperature_2m"],
        "feels_like": current["apparent_temperature"],
        "humidity": current["relative_humidity_2m"],
        "wind_speed": current["wind_speed_10m"],
        "description": description,
        "icon": icon,
        "time": current["time"],
    }