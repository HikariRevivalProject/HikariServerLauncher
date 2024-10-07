import logging
import requests
from hsl.source.source import Source
logger = logging.getLogger(__name__)
DOWNLOAD_SOURCE = r'https://hsl.hikari.bond/source.json'
SPCONFIGS_SOURCE = r'https://hsl.hikari.bond/spconfigs.json'
VERSION_SOURCE = r'https://hsl.hikari.bond/hsl.json'

def make_request(url: str, error_message: str) -> dict:
    try:
        response = requests.get(url,timeout=5)
        if response.status_code == 200:
            return response.json()
        logger.error(f'{error_message}，状态码：{response.status_code}')
        return {}
    except Exception as e:
        logger.error(f'{error_message}，错误信息：{e}')
        return {}
def check_update(version: int) -> tuple[bool, int]:
    data = make_request(VERSION_SOURCE, error_message='检查更新失败')
    latest: int = data.get('version', 0)
    return (True, latest) if version < latest else (False, version)
def load_source() -> Source:
    """Load source data from sources
    """
    _source = make_request(DOWNLOAD_SOURCE, error_message='加载源数据失败')
    return Source(**_source)
def get_spconfigs():
    return make_request(SPCONFIGS_SOURCE, error_message='加载特定配置文件失败')