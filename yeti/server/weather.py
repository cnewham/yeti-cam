import logging
import yeti
import pickledb
from datetime import datetime, timedelta
import requests, json
from yeti.common import constants
import astro

logger = logging.getLogger(__name__)

db = pickledb.load(yeti.get_resource("weather.db"), True)

try:
    with open(yeti.get_resource("wu.json"), 'r') as data_file:
        wu = json.load(data_file)
except IOError:
    wu = {}

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


def build_weather_underground_url(feature):
    return "http://api.wunderground.com/api/%s/%s/q/pws:%s.json" % (
        db.get(constants.WEATHER_WU_KEY), feature, db.get(constants.WEATHER_STATION))


def build_ambient_weather_url():
    return "https://api.ambientweather.net/v1/devices?applicationKey=%s&apiKey=%s" % (
        db.get(constants.WEATHER_AMBIENT_APP_KEY), db.get(constants.WEATHER_AMBIENT_API_KEY))


def refresh():
    """
    Refreshes data from WeatherUndergound
    API Documentation: https://www.wunderground.com/weather/api/d/docs?d=index
    :return:
    """
    try:
        wu_icon_set = "i"

        logger.debug("Requesting conditions")
        response = requests.get(build_weather_underground_url("conditions"))

        if not response.text:
            raise ValueError("response was empty when attempting to access WU API: %s" % api)

        conditions = json.loads(response.text)
        wu["conditions"] = conditions["current_observation"]

        latitude = wu["conditions"]["observation_location"]["latitude"]
        longitude = wu["conditions"]["observation_location"]["longitude"]

        wu["conditions"]["astrology"] = astro.tojson(latitude, longitude)

        # Change icon set
        wu["conditions"]["icon_url"] = wu["conditions"]["icon_url"].replace("/k/", "/%s/" % wu_icon_set)

        logger.debug("Requesting forecast")
        response = requests.get(build_weather_underground_url("forecast"))
        forecast = json.loads(response.text)
        wu["forecast"] = forecast["forecast"]["simpleforecast"]["forecastday"]

        for day in wu["forecast"]:
            astrodate = datetime(day["date"]["year"], day["date"]["month"], day["date"]["day"])
            day["astrology"] = astro.tojson(latitude, longitude, astrodate)
            day["icon_url"] = day["icon_url"].replace("/k/", "/%s/" % wu_icon_set)

        response = requests.get(build_ambient_weather_url())
        ambient = json.loads(response.text)

        if len(ambient) > 0:
            wu["conditions"]["indoor_temp_f"] = ambient[0]["lastData"]["tempinf"]

        wu["expire"] = (datetime.now() + timedelta(minutes=db.get(constants.WEATHER_EXPIRE_MIN))).isoformat()

        with open('wu.json', 'w') as data_file:
            json.dump(wu, data_file)
    except:
        logger.exception("An error occurred while attempting to access WeatherUndergound API")
        raise


def get(force=False):
    logger.info("Getting weather data")

    # Refresh data if it's the first time, it's expired or the force flag is set
    if not wu or datetime.strptime(wu["expire"], "%Y-%m-%dT%H:%M:%S.%f") <= datetime.now() or force:
        logger.info("Refreshing weather data from WU")
        refresh()

    return wu


if __name__ == "__main__":
    refresh()
