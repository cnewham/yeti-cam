__author__ = 'chris'
import datetime

def LogVerbose(module, message):
    print "%s: [VERBOSE] %s: %s" % (datetime.datetime.now().strftime("%x %X.%f"), module, message)

def LogInfo(module, message):
    print "%s: [INFO] %s: %s" % (datetime.datetime.now().strftime("%x %X.%f"), module, message)

def LogWarn(module, message):
    print "%s: [WARN] %s: %s" % (datetime.datetime.now().strftime("%x %X.%f"), module, message)

def LogError(module, message, ex = None):
    print "%s: [ERROR] %s: %s" % (datetime.datetime.now().strftime("%x %X.%f"), module, message)

    if ex is not None:
        print "%s: [EXCEPTION] %s: %s %s" % (datetime.datetime.now().strftime("%x %X.%f"), module, type(ex), ex)

