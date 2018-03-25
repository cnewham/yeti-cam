#!/usr/bin/env python
from astral import Location
import math, decimal, datetime

dec = decimal.Decimal


def moonphase(now=None):
    if now is None:
        now = datetime.datetime.now()

    diff = now - datetime.datetime(2001, 1, 1)
    days = dec(diff.days) + (dec(diff.seconds) / dec(86400))
    lunations = dec("0.20439731") + (days * dec("0.03386319269"))

    pos = lunations % dec(1)

    quarter = dec(round(pos * 4) / 4)
    isphase = False

    if round(abs(quarter - pos), 2) <= .01:
        isphase = True
        pos = quarter

    index = (pos * dec(4))

    index = math.floor(index)

    index = int(index) & 3

    phases = {
        0: ("New Moon", "new"),
        1: ("First Quarter", "firstqtr"),
        2: ("Full Moon", "full"),
        3: ("Last Quarter", "lastqtr"),
    }

    interm = {
       0: ("Waxing Crescent", "waxingcrescent"),
       1: ("Waxing Gibbous", "waxinggibbous"),
       2: ("Waning Gibbous", "waninggibbous"),
       3: ("Waning Crescent", "waningcrescent")
    }

    if isphase:
        return phases[index], pos
    else:
        return interm[index], pos


def suntimes(latitude, longitude, now=None):
    if now is None:
        now = datetime.datetime.now()

    l = Location()
    l.latitude = latitude
    l.longitude = longitude
    l.timezone = "US/Eastern"

    sun = l.sun(datetime.date(now.year, now.month, now.day), local=True)

    return sun['sunrise'], sun['sunset']


def tojson(latitude, longitude, now=None):
    if now is None:
        now = datetime.datetime.now()

    now = datetime.datetime.combine(now, datetime.time(21, 00, 00))

    moon = moonphase(now)
    sun = suntimes(float(latitude), float(longitude), now)

    astrology = {
        "datetime": now.isoformat(),
        "moonphase": {"name": moon[0][0], "code": moon[0][1], "value": round(float(moon[1]), 3)},
        "sun": {"sunrise": sun[0].isoformat(), "sunset": sun[1].isoformat()}
    }

    return astrology


if __name__ == "__main__":
    for i in range(-5,20):
        print tojson(u'41.186668', -78.460136, datetime.datetime.now() + datetime.timedelta(days=i))
