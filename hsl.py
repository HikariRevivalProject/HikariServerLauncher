import requests
from config import Config
from rich.console import Console

console = Console()

HSL_VERSION = 12
DOWNLOAD_SOURCE = r'http://hsl.hikari.bond/source.json'
CONFIGS_SOURCE = r'http://hsl.hikari.bond/configs.json'
VERSION = r'http://hsl.hikari.bond/hsl.json'

def make_request(url: str, error_message: str, timeout: int = 3) -> dict:
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        return response.json()
    except requests.RequestException:
        console.print(error_message)
        return {}

def check_update(version: int) -> tuple:
    data = make_request(VERSION, '检查更新失败')
    if data:
        latest = data['version']
        if version < latest:
            return True, latest
        else:
            return False, version
    return False, version

def get_source() -> dict:
    data = make_request(DOWNLOAD_SOURCE, '无法获取下载源信息')
    if data:
        return data
    raise Exception('无法连接到服务器，请检查网络连接，软件将关闭...')

def get_configs() -> list:
    data = list(make_request(CONFIGS_SOURCE, '无法获取特定配置信息'))
    if data:
        return data
    return []

try:
    SOURCE = get_source()
except Exception as e:
    console.print(e)
    exit()

NEWVERSION_INFO = check_update(HSL_VERSION)
CONFIG = Config()

class HSL:
    def __init__(self):
        self.source = SOURCE
        self.version = HSL_VERSION
        self.newVersionInfo = NEWVERSION_INFO
        self.config = CONFIG
