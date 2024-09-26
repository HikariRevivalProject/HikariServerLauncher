from hsl.core.config import Config
from rich.console import Console
import logging
import requests
import sys
console = Console()
HSL_VERSION = 15
DOWNLOAD_SOURCE = r'https://hsl.hikari.bond/source.json'
SPCONFIGS_SOURCE = r'https://hsl.hikari.bond/spconfigs.json'
VERSION_SOURCE = r'https://hsl.hikari.bond/hsl.json'
logger = logging.getLogger(__name__)
def make_request(url: str, error_message: str) -> dict:
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(response.json())
            return response.json()
        else:
            logger.error(f'{error_message}，状态码：{response.status_code}')
            return {}
    except Exception as e:
        logger.error(f'{error_message}，错误信息：{e}')
        return {}
def check_update(version: int) -> tuple[bool, int]:
        data = make_request(VERSION_SOURCE, error_message='检查更新失败')
        latest: int = data.get('version', 0)
        if version < latest:
            return True, latest
        return False, version
def load_source() -> dict:
    """Load source data from sources
    """
    return make_request(DOWNLOAD_SOURCE, error_message='加载源数据失败')
def get_spconfigs():
    return make_request(SPCONFIGS_SOURCE, error_message='加载特定配置文件失败')

console.rule('加载信息中，请稍后...')
SOURCE = load_source()
SPCONFIGS = get_spconfigs()
VERSIONINFO = check_update(HSL_VERSION)

class HSL:
    """Main class of HSL
    """
    def __init__(self):
        self.version = HSL_VERSION
        self.config = Config().load()
        self.source = SOURCE
        self.spconfigs = SPCONFIGS
        self.flag_outdated, self.latest_version = VERSIONINFO
        if not self.source or not self.spconfigs:
            console.print('加载源数据失败，请检查网络连接.')
            sys.exit(1)
        self.tasks = []