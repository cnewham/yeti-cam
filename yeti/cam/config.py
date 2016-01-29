__author__ = 'chris'
import pickledb
from yeti.common import constants

db = pickledb.load('db/config.db', True)

if not db.get(constants.CONFIG_VERSION):
    db.set(constants.CONFIG_VERSION, 1)
if not db.get(constants.CONFIG_SERVER):
    db.set(constants.CONFIG_SERVER, "http://localhost:5000/api/")

def get(key = None):
    if key is None:
        return db.getall()
    else:
        return db.get(key)

def update(configs):
    print "update configs: " + configs
