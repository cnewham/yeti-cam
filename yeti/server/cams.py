import json
import pickledb
import yeti

import logging
logger = logging.getLogger(__name__)

db = pickledb.load(yeti.get_resource("cams.db"), True)
order = 0

for registered_cam in yeti.get_registered_cams():
    if not db.get(registered_cam):
        db.dcreate(registered_cam)
        db.dadd(registered_cam, ("hidden", False))
        db.dadd(registered_cam, ("order", order))

    order += 1


def get(cam=None):
    if cam:
        return db.get(cam)

    with open(yeti.get_resource("cams.db"), 'r+') as camsdb:
        cams = camsdb.read()

    return json.loads(cams)


def update(cams):
    if not cams or cams is None:
        raise ValueError("No values have been supplied")

    for cam, properties in cams.iteritems():
        for key, value in properties.iteritems():
            db.dadd(cam, (key, value))

