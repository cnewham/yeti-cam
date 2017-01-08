import logging
import yeti
import pickledb
from datetime import datetime, timedelta
import requests, json
from yeti.common import constants

logger = logging.getLogger(__name__)

db = pickledb.load(yeti.createcamdir('db') + '/weather.db', True)

wu = {}

if not db.get(constants.WEATHER_WU_KEY):
    db.set(constants.WEATHER_WU_KEY, "NA")

if not db.get(constants.WEATHER_STATION):
    db.set(constants.WEATHER_STATION, "KPACLEAR5")

if not db.get(constants.WEATHER_EXPIRE_MIN):
    db.set(constants.WEATHER_EXPIRE_MIN, 10)


def build_url(feature):
    url = "http://api.wunderground.com/api/%s/%s/q/pws:%s.json" % (db.get(constants.WEATHER_WU_KEY), feature, db.get(constants.WEATHER_STATION))
    logger.debug("URL: " + url)
    return url


def refresh():
    logger.info("Refreshing data from WeatherUnderground")

    try:
        logger.debug("Requesting conditions")
        response = requests.get(build_url("conditions"))
        conditions = json.loads(response.text)
        wu["conditions"] = conditions["current_observation"]

        logger.debug("Request alerts")
        response = requests.get(build_url("alerts"))
        alerts = json.loads(response.text)
        wu["alerts"] = alerts["alerts"]

        logger.debug("Request forecast")
        response = requests.get(build_url("forecast"))
        forecast = json.loads(response.text)
        wu["forecast"] = forecast["forecast"]["simpleforecast"]["forecastday"]

        wu["expire"] = datetime.now() + timedelta(minutes=db.get(constants.WEATHER_EXPIRE_MIN))
    except:
        logger.exception("An error occurred while attempting to access WeatherUndergound API")
        raise


def get(force=False):
    logger.info("Getting weather data")

    # Refresh data if it's the first time, it's expired or the force flag is set
    if not wu or wu["expire"] <= datetime.now() or force:
        refresh()

    return wu


if __name__ == "__main__":
    refresh()
