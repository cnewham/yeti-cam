import os
import argparse
import errno

parser = argparse.ArgumentParser()
parser.add_argument("--name", help="The unique name of the yeti-cam camera", default="primary")

options = parser.parse_args()


def createcamdir(path=None):
    temp = "%s/cams/%s" % (os.getcwd(), options.name)

    if path:
        temp += "/%s" % path

    try:
        os.makedirs(temp)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

    return temp


def camdirexists(name):
    return os.path.exists("%s/cams/%s" % (os.getcwd(), name))


def getcamdir(name=None):
    if name and not camdirexists(name):
        raise NameError('%s cam does not exist' % name)

    if name:
        return "%s/cams/%s" % (os.getcwd(), name)
    else:
        return "%s/cams/%s" % (os.getcwd(), options.name)


def getnames():
    directory = "%s/cams" % os.getcwd()

    return next(os.walk(directory))[1]


print createcamdir()
