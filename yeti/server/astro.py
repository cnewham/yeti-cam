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

   #print round(pos * 4) / 4

   index = int(math.floor(pos * 8))

   #print index

   return {
      0: ("New Moon", "new"),
      1: ("Waxing Crescent", "waxingcrescent"),
      2: ("First Quarter", "firstqtr"),
      3: ("Waxing Gibbous", "waxinggibbous"),
      4: ("Full Moon", "full"),
      5: ("Waning Gibbous", "waninggibbous"),
      6: ("Last Quarter", "lastqtr"),
      7: ("Waning Crescent", "waningcrescent")
   }[index], pos


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

   now = datetime.datetime.combine(now, datetime.time(23, 59, 59))

   moon = moonphase(now)
   sun = suntimes(float(latitude), float(longitude), now)

   astrology = {
      "datetime" : now.isoformat(),
      "moonphase": {"name": moon[0][0], "code": moon[0][1], "value": round(float(moon[1]), 2)},
      "sun": {"sunrise": sun[0].strftime("%I:%M %p"), "sunset": sun[1].strftime("%I:%M %p")}
      }

   return astrology

def main():
   phase = moonphase()
   roundedpos = round(float(phase[1]), 3)
   print "%s (%s)" % (phase[0], roundedpos)

   sun = suntimes(41.186668, -78.460136)
   print "Sunrise: %s  Sunset: %s" % sun

   print tojson(u'41.186668', -78.460136, datetime.datetime.now() + datetime.timedelta(days=14))

if __name__=="__main__":
   main()
