from functools import cache
import logging
import requests
import os
from rich.console import Console
logger = logging.getLogger(__name__)
DOWNLOAD_SOURCE = r'https://hsl.hikari.bond/source.json'
SPCONFIGS_SOURCE = r'https://hsl.hikari.bond/spconfigs.json'
VERSION_SOURCE = r'https://hsl.hikari.bond/hsl.json'
HSL_VERSION = 16
HSL_VERSION_MINOR = 4

console = Console()
async def make_request(url: str, error_message: str) -> dict:
    console.print(f'Requesting: {url}')
    try:
        response = requests.get(url,timeout=3)
        if response.status_code == 200:
            return response.json()
        console.log(f'{error_message}，状态码：{response.status_code}')
        return {}
    except Exception as e:
        console.log(f'{error_message}，错误信息：{e}')
        return {}
async def check_update():
    data = await make_request(VERSION_SOURCE, error_message='检查更新失败')
    latest: int = data.get('version', 0)
    minor: int = data.get('minor', 0)
    console.log(f'Version data fetched: {latest}-{minor}')
    if (HSL_VERSION < latest):
        console.print(f'[bold magenta]发现主要版本更新，版本号：[u]{latest/10}[/u]，建议及时更新')
        return
    if (HSL_VERSION_MINOR < minor):
        console.print(f'[bold magenta]发现次要版本更新，版本号：[u]{minor/10}[/u]，建议及时更新')
        return
def get_version() -> tuple:
    return HSL_VERSION, HSL_VERSION_MINOR
# async def get_cache_update() -> bool:
#     data = await make_request(VERSION_SOURCE, error_message='检查更新失败')
#     remote_spconfig = data.get('spconfig', 0)
#     remote_source = data.get('source', 0)
#     if os.path.exists(SPCONFIG_CACHE_FILE):
#         with open(SPCONFIG_CACHE_FILE, 'r', encoding='utf-8') as f:
#             cached_spconfig_version = json.load(f).get('version', 0)
#             console.print(f'Cached SPConfig version: {cached_spconfig_version}')
#     else:
#         cached_spconfig_version = 0
#     if os.path.exists(SOURCE_CACHE_FILE):
#         with open(SOURCE_CACHE_FILE, 'r', encoding='utf-8') as f:
#             cached_source_version = json.load(f)[0].get('version', 0)
#             console.print(f'Cached Source version: {cached_source_version}')
#     else:
#         cached_source_version = 0
#     if (
#         remote_spconfig > cached_spconfig_version or
#         remote_source > cached_source_version
#     ):
#         console.print('Cache outdated, updating...')
#         return await update_cache()
#     return True
    
# async def update_cache() -> bool:
#     """Update cache
#     """
#     spconfig_data = await make_request(SPCONFIGS_SOURCE, error_message='更新特定配置缓存失败')
#     with open(SPCONFIG_CACHE_FILE, 'w', encoding='utf-8') as f:
#         json.dump(spconfig_data, f, ensure_ascii=False, indent=4)
#     source_data = await make_request(DOWNLOAD_SOURCE, error_message='更新下载源缓存失败')
#     with open(SOURCE_CACHE_FILE, 'w', encoding='utf-8') as f:
#         json.dump(source_data, f, ensure_ascii=False, indent=4)
#     return bool((spconfig_data and source_data))
# async def load_source() -> Source:
#     """Load source data from sources
#     """
#     if os.path.exists(SOURCE_CACHE_FILE):
#         with open(SOURCE_CACHE_FILE, 'r', encoding='utf-8') as f:
#             return Source(**json.load(f))
#     await get_cache_update()
#     return await load_source()
#     # _source = make_request(DOWNLOAD_SOURCE, error_message='加载源数据失败')
#     # return Source(**_source)
# async def get_spconfigs() -> dict:
#     if os.path.exists(SPCONFIG_CACHE_FILE):
#         with open(SPCONFIG_CACHE_FILE, 'r', encoding='utf-8') as f:
#             return json.load(f)
#     await get_cache_update()
#     return await get_spconfigs()
# async def get_version_data() -> tuple:
#     return HSL_VERSION, HSL_VERSION_MINOR, *await check_update()