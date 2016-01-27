__author__ = 'chris'
import pickledb
from yeti.common import constants

db = pickledb.load('db/cam.db', True)

if not db.get(constants.CONFIG_VERSION):
    db.set(constants.CONFIG_VERSION, 1)