import os
import argparse
import errno

parser = argparse.ArgumentParser()
parser.add_argument("--name", help="The unique name of the yeti-cam camera", default="primary")

options = parser.parse_args()


def getcamdir(path=None):
    temp = "%s/cams/%s" % (os.path.dirname(os.getcwd()), options.name)

    if path:
        temp += "/%s" % path

    try:
        os.makedirs(temp)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

    return temp


print getcamdir()
