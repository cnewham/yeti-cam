__author__ = 'chris'
import datetime

def Log(module, level, message):
    print "%s: [%s] [%s] %s" % (datetime.datetime.now().strftime("%x %X.%f"), level, module, message)

def LogVerbose(module, message):
    Log(module, "VERBOSE", message)

def LogInfo(module, message):
    Log(module, "INFO", message)

def LogWarn(module, message):
    Log(module, "WARN", message)

def LogError(module, message, ex = None):
    Log(module, "ERROR", message)

    if ex is not None:
        details = "%s %s" % (type(ex), ex)
        Log(module, "EXCEPTION", details)

