from os import error
import httpx
import logging
import asyncio

from hsl.core.config import Config
logger = logging.getLogger('root')

DOWNLOAD_SOURCE = r'https://hsl.hikari.bond/source.json'
CONFIGS_SOURCE = r'https://hsl.hikari.bond/configs.json'
VERSION_SOURCE = r'https://hsl.hikari.bond/hsl.json'

async def make_request(url: str, error_message: str, timeout: int = 3) -> dict:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=timeout)
            return response.json()
        except httpx.RequestError as e:
            logger.error(error_message+f':{e}')
            return {}

async def check_update(version: int) -> tuple[bool, int]:
    data = await make_request(VERSION_SOURCE, error_message='检查更新失败')
    latest: int = data.get('version', 0)
    if version < latest:
        return True, latest
    return False, version

async def get_source() -> dict:
    data = await make_request(DOWNLOAD_SOURCE, error_message='无法获取下载源信息')
    return data

async def get_configs() -> list:
    data = list(await make_request(CONFIGS_SOURCE, error_message='无法获取特定配置信息'))
    if data:
        return data
    return []
# async def init() -> tuple:
#     tasks = [
#         get_source(), 
#         check_update(HSL_VERSION)
#     ]
#     try:
#         SOURCE, NEWVERSION_INFO = await asyncio.gather(*tasks, return_exceptions=True)
#     except Exception as e:
#         logger.error(f'初始化失败：{e}')
#         sys.exit(0)
#     return SOURCE, NEWVERSION_INFO
VERSION: int = 14
class HSL:
    def __init__(self):
        self.config = Config
        self.config.load()
        self.flag_init: int = 3
        self.flag_outdated = False
        self.newVersion = (False, 0)
    async def init(self):
        self.flag_init = 2
        self.source = await get_source()
        if not self.source:
            self.flag_init = 10
            return
        self.flag_init = 1
        self.newVersion = await check_update(VERSION)
        self.flag_outdated = self.newVersion[0]
        self.flag_init = 0
        return