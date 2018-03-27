import os
import argparse
import errno

parser = argparse.ArgumentParser()
parser.add_argument("--name", help="The unique name of the yeti-cam camera")
parser.add_argument("--server", help="The server to download initial config")

options = parser.parse_args()

if options.name is None and "YETICAM" in os.environ:
    options.name = os.environ["YETICAM"]
else:
    options.name = "primary"


def get_resource(path=None, dir_only=False):
    resource = "%s/cams" % os.getcwd()

    if path is not None:
        if path[:1] == "/":
            resource += path
        else:
            resource += "/%s" % path

        try:
            if dir_only:
                os.makedirs(resource)
            else:
                os.makedirs(os.path.dirname(resource))
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

    return resource


def get_cam_resource(name=options.name, path=None, dir_only=False):
    resource = "%s/cams/%s" % (os.getcwd(), name)

    if path is not None:
        if path[:1] == "/":
            resource += path
        else:
            resource += "/%s" % path

        try:
            if dir_only:
                os.makedirs(resource)
            else:
                os.makedirs(os.path.dirname(resource))
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

    return resource


def resource_exists(path):
    return os.path.exists(path)


def get_registered_cams():
    directory = "%s/cams" % os.getcwd()

    return next(os.walk(directory))[1]


def cam_is_registered(name):
    return os.path.exists("%s/cams/%s" % (os.getcwd(), name))
