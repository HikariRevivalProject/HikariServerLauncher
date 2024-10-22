import httpx
from rich.console import Console
# DOWNLOAD_SOURCE = r'https://hsl.hikari.bond/source.json'
# SPCONFIGS_SOURCE = r'https://hsl.hikari.bond/spconfigs.json'
VERSION_SOURCE = r'https://hsl.hikari.bond/hsl.json'
SEND_COUNTER = r'http://a.hikari.bond:40654/count'
HSL_VERSION = 17
HSL_VERSION_MINOR = 3

console = Console()
async def make_request(url: str, error_message: str) -> dict:
    #console.print(f'Requesting: {url}')
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code == 200:
                return response.json()
            console.print(f'[bold red]{error_message}[/bold red]')
            return {}
    except httpx.ConnectError:
        console.print(f'[bold red]{error_message}[/bold red]')
        return {}
async def check_update():
    data = await make_request(VERSION_SOURCE, error_message='检查更新失败')
    latest: int = data.get('version', 0)
    minor: int = data.get('minor', 0)
    #console.log(f'Version data fetched: {latest}-{minor}')
    if (HSL_VERSION < latest):
        console.print(f'[bold magenta]发现主要版本更新，版本号：[u]{latest/10}[/u]，建议及时更新')
        return
    if (HSL_VERSION_MINOR < minor and HSL_VERSION == latest):
        console.print(f'[bold magenta]发现次要版本更新，版本号：[u]{latest/10}.{minor}[/u]，建议及时更新')
        return
def get_version() -> tuple:
    return HSL_VERSION, HSL_VERSION_MINOR
async def send_counter():
    await make_request(SEND_COUNTER, error_message='发送计数失败')