import logging
import json
import pickledb
import yeti
import yeti.common
import requests
from requests.exceptions import HTTPError

logger = logging.getLogger(__name__)

db = pickledb.load(yeti.get_resource("moultrie.db"), True)
TOKEN = "token"
LOGIN = "login"

if not db.get(TOKEN):
    db.set(TOKEN, None)

if not db.get(LOGIN):
    db.set(LOGIN, None)


def login():
    logger.debug("Logging into Moultrie API")

    url = "https://consumerservice2.moultriemobile.com/oauth2/token"

    if db.get(LOGIN) is None:
        raise EnvironmentError("Login information not configured")

    r = requests.post(url, data=db.get(LOGIN))
    r.raise_for_status()

    token = r.json()["access_token"]

    db.set(TOKEN, token)


def retrieve():
    logger.debug("Retrieving image URLs")

    url = "https://consumerservice2.moultriemobile.com/api/Image/ImageSearch"

    headers = {
        "content-type": "application/json",
        "Authorization": "Bearer %s" % db.get(TOKEN)
    }

    r = requests.post(url=url, headers=headers, json={"Order": "TakenOnDescending"})
    r.raise_for_status()

    response = r.json()
    return response["Results"]


def get_latest_pics():
    logger.info("Getting latest Moultrie data")

    if db.get(TOKEN) is None:
        login()

    try:
        return retrieve()
    except HTTPError as e:
        if e.response.status_code == 401:
            logger.warn("Token expired")
            login()
            return retrieve()
        else:
            raise
    except Exception:
        logger.exception("Error retrieving Moultrie data")
        raise


if __name__ == "__main__":
    print json.dumps(get_latest_pics())
