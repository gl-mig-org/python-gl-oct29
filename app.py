from flask import Flask, render_template, request, jsonify
from config import Config
from weather_service import get_weather, WeatherError

app = Flask(__name__)
app.config.from_object(Config)


@app.route("/", methods=["GET", "POST"])
def index():
    weather, error = None, None
    if request.method == "POST":
        city = request.form.get("city", "").strip()
        if not city:
            error = "Please enter a city name."
        else:
            try:
                weather = get_weather(city)
            except WeatherError as exc:
                error = str(exc)
    return render_template("index.html", weather=weather, error=error)


@app.route("/api/weather/<city>")
def api_weather(city):
    """JSON endpoint, e.g. /api/weather/Chennai"""
    try:
        return jsonify(get_weather(city))
    except WeatherError as exc:
        return jsonify({"error": str(exc)}), 404


if __name__ == "__main__":
    app.run(debug=True)