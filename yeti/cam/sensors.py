__author__ = 'chris'
from yeti.common import constants
from yeti.cam import db

class Temperature:
    def read(self):
        return db.dgetall(constants.CONFIG_SENSORS)
