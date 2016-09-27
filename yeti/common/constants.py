__author__ = 'chris'

#CONVERSION CONSTANTS

SECONDS2MIN = 60

#EVENT CONSTANTS

EVENT_TIMER = 'timer'
EVENT_MOTION = 'motion'
EVENT_MANUAL = 'manual'
EVENT_TYPE_IMAGE = 'image'
EVENT_TYPE_VIDEO = 'video'

#STATUS CONSTANTS

STATUS = 'status'
STATUS_CAM = 'cam'
STATUS_BATTERY = 'battery'
STATUS_EVENT = 'event'
STATUS_TIME = 'time'
STATUS_INDOOR_TEMP = 'indoor_temp'
STATUS_OUTDOOR_TEMP = 'outdoor_temp'
STATUS_TEMP = 'temp'
STATUS_HUMIDITY = 'humidity'
STATUS_MOTION_EVENTS_24H = 'motion_events_24h'

#CONFIG CONSTANTS

CONFIG_VERSION = 'version'
CONFIG_STATUS = 'status'
CONFIG_STATUS_NEW = "NEW"
CONFIG_STATUS_MODIFIED = "MODIFIED"
CONFIG_STATUS_UPDATED = "UPDATED"
CONFIG_CHECK_INTERVAL_MIN = 'config_check_interval'
CONFIG_SERVER = 'server'
CONFIG_IMAGE_QUALITY = "image_quality"
CONFIG_IMAGE_DIR = "image_dir"
CONFIG_IMAGE_PREFIX = 'image_prefix'
CONFIG_IMAGE_WIDTH = 'image_width'
CONFIG_IMAGE_HEIGHT = 'image_height'
CONFIG_IMAGE_VFLIP = 'image_vflip'
CONFIG_IMAGE_HFLIP = 'image_hflip'
CONFIG_IMAGE_EXPOSURE_MODE = "image_exposure_mode"
CONFIG_IMAGE_AWB_MODE = "image_awb_mode"
CONFIG_MOTION_ENABLED = 'motion_enabled'
CONFIG_MOTION_RECORD_ENABLED = 'motion_record_enabled'
CONFIG_MOTION_THRESHOLD = 'motion_threshold'
CONFIG_MOTION_SENSITIVITY = 'motion_sensitivity'
CONFIG_MOTION_DELAY_SEC = 'motion_delay'
CONFIG_MOTION_CAPTURE_THRESHOLD = 'motion_capture_threshold'
CONFIG_MOTION_EVENT_CAPTURE_TYPE = 'motion_event_capture_type'
CONFIG_MOTION_PERCENT_CHANGE_MAX = 'motion_percent_change_max'
CONFIG_TIMER_INTERVAL_MIN = 'timer_interval'
CONFIG_SOCKET_HOST = 'config_socket_host'
CONFIG_SOCKET_PORT = 'config_socket_port'

#SENSOR CONSTANTS

SENSORS_TEMP = 'temp'
SENSORS_MOTION = 'motion'
SENSORS_SOUND = 'sound'
SENSORS_READ_INTERVAL_SEC = 'read_interval_sec'

#OTHER CONSTANTS

MOTION_LOG = 'motion_log'
GDRIVE_FOLDER = 'gdrive_folder'
ENABLE_GDRIVE = 'enable_gdrive'
LAST_CAM_UPDATE = 'last_cam_update'