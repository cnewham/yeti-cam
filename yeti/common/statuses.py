__author__ = 'chris'
import pickledb
from yeti.common import constants

db = pickledb.load('db/status.db', True)

def get(key):
    return db.get(key)

def getall():
    return db.dump()

def set(key, value):
    db.set(key, value)