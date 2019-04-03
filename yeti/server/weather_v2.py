import logging
from datetime import datetime, timedelta

import json
import pickledb
import requests

import yeti
from yeti.common import constants, astro

logger = logging.getLogger(__name__)

db = pickledb.load(yeti.get_resource("weather.db"), True)

try:
    with open(yeti.get_resource("weather.json"), 'r') as input:
        cached = json.load(input)
except Exception:
    cached = {}

if not db.get(constants.WEATHER_LOCATION):
    db.set(constants.WEATHER_LOCATION, "NA")

if not db.get(constants.WEATHER_WU_KEY):
    db.set(constants.WEATHER_WU_KEY, "NA")

if not db.get(constants.WEATHER_AMBIENT_APP_KEY):
    db.set(constants.WEATHER_AMBIENT_APP_KEY, "NA")

if not db.get(constants.WEATHER_AMBIENT_API_KEY):
    db.set(constants.WEATHER_AMBIENT_API_KEY, "NA")

if not db.get(constants.WEATHER_STATION):
    db.set(constants.WEATHER_STATION, "KPACLEAR5")

if not db.get(constants.WEATHER_EXPIRE_MIN):
    db.set(constants.WEATHER_EXPIRE_MIN, 10)

if not db.get(constants.WEATHER_DARKSKY_API_KEY):
    db.set(constants.WEATHER_DARKSKY_API_KEY, "NA")


def build_darksky_url():
    return "https://api.darksky.net/forecast/%s/%s?exclude=minutely,hourly,currently" % (
        db.get(constants.WEATHER_DARKSKY_API_KEY), db.get(constants.WEATHER_LOCATION))


def build_ambient_weather_url():
    return "https://api.ambientweather.net/v1/devices?applicationKey=%s&apiKey=%s" % (
        db.get(constants.WEATHER_AMBIENT_APP_KEY), db.get(constants.WEATHER_AMBIENT_API_KEY))


def refresh():
    try:
        with requests.get(build_ambient_weather_url()) as response:
            logger.info("Retrieving weather data from Ambient Weather")
            result = json.loads(response.text)
            ambient = result[0]["lastData"]

        with requests.get(build_darksky_url()) as response:
            logger.info("Retrieving weather data from DarkSky")
            darksky = json.loads(response.text)

        if "alerts" in darksky:
            cached["alerts"] = []

            for item in darksky["alerts"]:
                alert = {
                    "title": item["title"],
                    "severity": item["severity"],
                    "time": datetime.fromtimestamp(item["time"]).isoformat(),
                    "expires": datetime.fromtimestamp(item["expires"]).isoformat(),
                    "uri": item["uri"]
                }

                cached["alerts"].append(alert)

        cached["longitude"] = darksky["longitude"]
        cached["latitude"] = darksky["latitude"]

        current_date = datetime.fromtimestamp(ambient["dateutc"]/1000)

        cached["current"] = {
            "date": current_date.isoformat(),
            "temp": ambient["tempf"],
            "apparentTemp": ambient["feelsLike"],
            "humidity": ambient["humidity"],
            "indoor": {
                "temp": ambient["tempinf"],
                "humidity": ambient["humidityin"]
            },
            "wind": {
                "speed": ambient["windspeedmph"],
                "direction": ambient["winddir"],
                "gust": ambient["windgustmph"]
            },
            "precipitation": {
                "hourly": ambient["hourlyrainin"],
                "daily": ambient["dailyrainin"],
                "weekly": ambient["weeklyrainin"]
            },
            "astrology": astro.tojson(darksky["latitude"], darksky["longitude"])
        }

        cached["forecast"] = []
        for day in darksky["daily"]["data"]:
            forecast = {
                "summary": day["summary"],
                "date": datetime.fromtimestamp(day["time"]).isoformat(),
                "icon": day["icon"],
                "humidity": day["humidity"],
                "dewPoint": day["dewPoint"],
                "cloudCover": day["cloudCover"],
                "visibility": day["visibility"],
                "pressure": day["pressure"],
                "ozone": day["ozone"],
                "temp": {
                    "high": day["temperatureHigh"],
                    "low": day["temperatureLow"],
                    "apparentHigh": day["apparentTemperatureHigh"],
                    "apparentLow": day["apparentTemperatureLow"],
                },
                "wind": {
                    "speed": day["windSpeed"],
                    "direction": day["windBearing"],
                    "gust": day["windGust"],
                    "gustTime": datetime.fromtimestamp(day["windGustTime"]).isoformat()
                },
                "precipitation": {
                    "type": day["precipType"] if "precipType" in day else "",
                    "accumulation": day["precipAccumulation"] if "precipAccumulation" in day else 0,
                    "probability": day["precipProbability"],
                    "intensity": day["precipIntensity"]
                },
                "astrology": astro.tojson(darksky["latitude"], darksky["longitude"],
                                          datetime.fromtimestamp(day["time"]))
            }

            cached["forecast"].append(forecast)
            cached["current"]["icon"] = cached["forecast"][0]["icon"]

        cached["expire"] = (datetime.now() + timedelta(minutes=db.get(constants.WEATHER_EXPIRE_MIN))).isoformat()

        with open(yeti.get_resource("weather.json"), 'w') as output:
            json.dump(cached, output)
    except:
        logger.exception("An error occurred while attempting to gather weather data")
        raise


def get(force=False):
    logger.info("Getting weather data")

    # Refresh data if it's the first time, it's expired or the force flag is set
    if not cached or datetime.strptime(cached["expire"], "%Y-%m-%dT%H:%M:%S.%f") <= datetime.now() or force:
        refresh()

    return cached


if __name__ == "__main__":
    refresh()
