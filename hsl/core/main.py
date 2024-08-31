import httpx
import logging

from hsl.core.config import Config
logging.basicConfig(level=logging.INFO, format='[%(asctime)s][%(levelname)s] %(message)s')
logger = logging.getLogger('hsl')

DOWNLOAD_SOURCE = r'https://hsl.hikari.bond/source.json'
CONFIGS_SOURCE = r'https://hsl.hikari.bond/configs.json'
VERSION_SOURCE = r'https://hsl.hikari.bond/hsl.json'

async def make_request(url: str, error_message: str, timeout: int = 3) -> dict:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            logger.error(error_message)
            return {}

async def check_update(version: int) -> tuple[bool, int]:
    data = await make_request(VERSION_SOURCE, '检查更新失败')
    if data:
        latest: int = data['version']
        if version < latest:
            return True, latest
    return False, version

async def get_source() -> dict:
    data = await make_request(DOWNLOAD_SOURCE, '无法获取下载源信息')
    if data:
        return data
    raise Exception('无法连接到服务器，请检查网络连接，软件将关闭...')

async def get_configs() -> list:
    data = list(await make_request(CONFIGS_SOURCE, '无法获取特定配置信息'))
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
class HSL:
    def __init__(self):
        self.version: int = 14
        self.config = Config
        self.flag_init: int = 3
    async def init(self):
        self.flag_init = 2
        self.source = await get_source()
        self.flag_init = 1
        self.newVersion = await check_update(self.version)
        self.flag_init = 0