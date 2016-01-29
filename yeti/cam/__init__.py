__author__ = 'chris'
from yeti.common import constants
from yeti.common import config
from yeti.common import statuses

import sensors
import service
import camera

temp = sensors.Temperature()
server = service.YetiService(config.get(constants.CONFIG_SERVER))
cam = camera.YetiCam()

cam.Start()
