import requests
from rich.console import Console
from hsl.utils.download import downloadfile
from hsl.utils.prompt import promptSelect
from hsl.source.source import Source
console = Console()
async def get_versions(source: Source,mirror_first=False) -> list:
    sources = source.mc.vanilla.list
    if mirror_first:
        sources = sources[::-1]
    for vanilla_source in sources:
        if vanilla_source.type == 'bmclapi':
            try:
                response = requests.get(vanilla_source.versionList)
                if response.status_code == 200:
                    return response.json().get('versions')
            except Exception:
                pass
    return []
async def downloadServer(source: Source,gameVersion,path,mirror_first=False) -> bool:
    # sourcery skip: remove-redundant-pass, swap-nested-ifs
    sources = source.mc.vanilla.list
    if mirror_first:
        sources = sources[::-1]
    for vanilla_source in sources:
        if vanilla_source.type == 'bmclapi':
            if await downloadfile(vanilla_source.server.replace('{version}',gameVersion), path):
                return True
        else:
            pass
    return False
async def install(self, serverName: str, serverPath: str, serverJarPath: str, data: dict):
    serverType = 'vanilla'
    mcVersions = [x['id'] for x in await get_versions(self.source) if x['type'] == 'release']
    if not mcVersions:
        console.print('[bold magenta]没有找到可用的 Minecraft 版本。')
        return False
    mcVersion = mcVersions[await promptSelect(mcVersions, '请选择Minecraft服务器版本:')]
    javaVersion = await self.Java.getJavaVersion(mcVersion)
    console.print(f'正在下载 Vanilla 服务端: {mcVersion}')
    if not await downloadServer(self.source, mcVersion, serverJarPath, self.config.use_mirror):
        console.print('[bold magenta]Vanilla 服务端下载失败。')
        return False
    console.print('Vanilla 服务端下载完成。')
    return serverName, serverType, serverPath, javaVersion, data