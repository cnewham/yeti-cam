__author__ = 'chris'
import pickledb

db = pickledb.load('db/cam.db', True)

if not db.get('config-version'):
    db.set('config-version', 1)