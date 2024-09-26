import requests
from rich.console import Console
from hsl.utils.download import downloadfile
from hsl.utils.prompt import promptSelect
console = Console()
async def get_versions(source,mirror_first=False) -> list:
    sources = source["mc"]["vanilla"]['list']
    if mirror_first:
        sources = sources[::-1]
    for source in sources:
        if source['type'] == 'bmclapi':
            try:
                response = requests.get(source['versionList'])
                if response.status_code == 200:
                    versions = response.json().get('versions')
                    return versions
            except:
                pass
    return []
async def downloadServer(source,gameVersion,path,mirror_first=False) -> bool:
    sources = source["mc"]["vanilla"]['list']
    if mirror_first:
        sources = sources[::-1]
    for source in sources:
        if source['type'] == 'bmclapi':
            if await downloadfile(source['server'].replace('{version}',gameVersion),path):
                return True
    return False
async def install(self, serverName: str, serverPath: str, serverJarPath: str, data: dict):
        serverType = 'vanilla'
        mcVersions = [x['id'] for x in await get_versions(self.source) if x['type'] == 'release']
        mcVersion = mcVersions[await promptSelect(mcVersions, '请选择Minecraft服务器版本:')]
        javaPath = await self.Java.getJavaByGameVersion(mcVersion, path=self.config.workspace_dir)
        console.print(f'正在下载 Vanilla 服务端: {mcVersion}')
        if not await downloadServer(self.source, mcVersion, serverJarPath, self.config.use_mirror):
            console.print('[bold magenta]Vanilla 服务端下载失败。')
            return False
        console.print('Vanilla 服务端下载完成。')
        return serverName, serverType, serverPath, javaPath, data