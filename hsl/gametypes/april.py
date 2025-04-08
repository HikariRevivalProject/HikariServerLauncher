import requests
from rich.console import Console
from hsl.utils.download import downloadfile
from hsl.utils.prompt import promptSelect
from hsl.source.source import Source
console = Console()
async def downloadServer(source: Source,gameVersion,path) -> bool:
    # sourcery skip: remove-redundant-pass, swap-nested-ifs
    sources = source.mc.april.list
    for april_source in sources:
        if april_source.version == gameVersion:
            if await downloadfile(april_source.link, path):
                return True
        else:
            pass
    return False
async def install(self, serverName: str, serverPath: str, serverJarPath: str, data: dict):# -> tuple[str, Literal['vanilla'], str, Any, dict[Any, Any]] | ...:# -> tuple[str, Literal['vanilla'], str, Any, dict[Any, Any]] | ...:# -> tuple[str, Literal['vanilla'], str, Any, dict[Any, Any]] | ...:# -> tuple[str, Literal['vanilla'], str, Any, dict[Any, Any]] | ...:
    serverType = 'vanilla'
    mcVersions = [x.name for x in self.source.mc.april.list]
    if not mcVersions:
        console.print('[bold magenta]没有找到可用的 Minecraft 版本。')
        return False
    index = await promptSelect(mcVersions, '请选择Minecraft服务器版本:')
    _serverName = self.source.mc.april.list[index].name
    mcVersion = self.source.mc.april.list[index].version
    javaVersion = await self.Java.getJavaVersion(mcVersion)
    console.print(f'正在下载 愚人节 服务端: {_serverName}')
    if not await downloadServer(self.source, mcVersion, serverJarPath):
        console.print('[bold magenta]愚人节 服务端下载失败。')
        return False
    console.print('愚人节 服务端下载完成。')
    return serverName, serverType, serverPath, javaVersion, data