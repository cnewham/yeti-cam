__author__ = 'chris'
import pickledb
import constants

db = pickledb.load('db/config.db', True)

if not db.get(constants.CONFIG_VERSION):
    db.set(constants.CONFIG_VERSION, 1)
if not db.get(constants.CONFIG_SERVER):
    db.set(constants.CONFIG_SERVER, "http://localhost:5000/api/")

def get(key):
    return db.get(key)

def getall():
    return db.dump()

def set(key, value):
    db.set(key, value)