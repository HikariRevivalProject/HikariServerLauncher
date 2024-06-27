import requests
import json
from config import Config
from rich.console import Console
console = Console()
def check_update(version: int) -> tuple:
    console.print('正在检查更新...')
    try:
        r = requests.get(VERSION,timeout=1)
        if r.status_code == 200:
            latest: int = r.json()['version']
            if version < latest:
                return True, latest
            else:
                return False, version
        else:
            console.print('检查更新失败')
            return False, version
    except:
        console.print('检查更新失败')
        return False, version
def get_source() -> dict:
    console.print('正在获取下载源信息...')
    with open('source.json','r',encoding='utf-8') as f:
        return json.loads(f.read())
    r = requests.get(DOWNLOAD_SOURCE,timeout=3)
    if r.status_code == 200:
        return r.json()
    else:
        return {}

HSL_VERSION = 6
DOWNLOAD_SOURCE = r'http://mirror.hikari.bond:12345/source.json'
VERSION = r'http://mirror.hikari.bond:12345/hsl.json'
try:
    SOURCE = get_source()
except:
    print('无法连接到服务器，请检查网络连接，软件将关闭...')
    exit()
NEWVERSION_INFO = check_update(HSL_VERSION)
CONFIG = Config().config
class HSL:
    def __init__(self):
        self.source = SOURCE
        self.version = HSL_VERSION
        self.newVersionInfo = NEWVERSION_INFO
        self.config = CONFIG

