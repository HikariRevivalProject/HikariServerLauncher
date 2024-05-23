
import psutil
def getOSMaxRam():
    totalMemory = psutil.virtual_memory().total
    return int(round(totalMemory / (1024.0 * 1024.0), 2))
