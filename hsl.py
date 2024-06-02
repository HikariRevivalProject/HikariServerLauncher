import requests
from config import Config
def check_update(version: int) -> tuple:
    r = requests.get(VERSION)
    if r.status_code == 200:
        latest: int = r.json()['version']
        if version < latest:
            return True, latest
        else:
            return False, version
    else:
        return False, version

def get_source() -> dict:
    r = requests.get(DOWNLOAD_SOURCE)
    if r.status_code == 200:
        return r.json()
    else:
        return {}

HSL_VERSION = 5
DOWNLOAD_SOURCE = r'http://hsl.hikari.bond/source.json'
VERSION = r'http://hsl.hikari.bond/hsl.json'

SOURCE = get_source()
NEWVERSION_INFO = check_update(HSL_VERSION)
CONFIG = Config().config

class HSL:
    def __init__(self):
        self.source = SOURCE
        self.version = 4
        self.newVersionInfo = NEWVERSION_INFO
        self.config = CONFIG

