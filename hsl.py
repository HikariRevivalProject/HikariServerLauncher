import httpx
import asyncio

from rich.console import Console

from config import Config


console = Console()

HSL_VERSION = 13
DOWNLOAD_SOURCE = r'https://hsl.hikari.bond/source.json'
CONFIGS_SOURCE = r'https://hsl.hikari.bond/configs.json'
VERSION_SOURCE = r'https://hsl.hikari.bond/hsl.json'

async def make_request(url: str, error_message: str, timeout: int = 3) -> dict:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=timeout)
            response.raise_for_status()  # Will raise an HTTPError for bad status codes
            return response.json()
        except httpx.RequestError:
            console.print(error_message)
            return {}

async def check_update(version: int) -> tuple[bool, int]:
    data = await make_request(VERSION_SOURCE, '检查更新失败')
    if data:
        latest: int = data['version']
        if version < latest:
            return True, latest
        else:
            return False, version
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
async def init() -> tuple:
    tasks = [
        get_source(), 
        check_update(HSL_VERSION)
    ]
    try:
        SOURCE, NEWVERSION_INFO = await asyncio.gather(*tasks, return_exceptions=True)
    except Exception as e:
        console.print(e)
        exit()
    return SOURCE, NEWVERSION_INFO
CONFIG = Config()
SOURCE, NEWVERSION_INFO = asyncio.run(init())
class HSL:
    def __init__(self):
        self.source = SOURCE
        self.version = HSL_VERSION
        self.newVersionInfo = NEWVERSION_INFO
        self.config = CONFIG
