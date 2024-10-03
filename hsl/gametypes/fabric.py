from re import S
import requests
from rich.console import Console
from hsl.source.source import Source
from hsl.utils.prompt import promptSelect
from hsl.utils.download import downloadfile
console = Console()
async def getMcVersions(source: Source) -> list[str]:
    sources = source.fabric.list
    for fabric_source in sources:
        if fabric_source.type == "official":
            try:
                response = requests.get(fabric_source.supportList)
                if response.status_code == 200:
                    fabVersions = response.json()
                    return [i['version'] for i in fabVersions if i['stable'] == True]
            except Exception:
                pass
    return []
async def getLoaderVersion(source: Source) -> str:
    sources = source.fabric.list
    for fabric_source in sources:
        if fabric_source.type == "official":
            try:
                response = requests.get(fabric_source.loaderList)
                if response.status_code == 200:
                    loaderList = response.json()
                    return loaderList[0]['version']
            except Exception:
                pass
    return ''
async def downloadServer(
        source: Source,
        path: str,
        mcVersion: str,
        loaderVersion: str
    ) -> bool:
    sources = source.fabric.list
    for fabric_source in sources:
        if fabric_source.type == "official":
            url = fabric_source.installer.replace(r'{version}',mcVersion).replace(r'{loader}',loaderVersion)
            if await downloadfile(url,path):
                return True
    return False
async def install(self, serverName: str, serverPath: str, serverJarPath: str, data: dict):
    serverType = 'fabric'
    fabVersion = await getMcVersions(self.source)
    fabVersion_index = await promptSelect(fabVersion, '请选择 Fabric 服务器版本:')
    mcVersion = fabVersion[fabVersion_index]
    javaPath = await self.Java.getJavaVersion(mcVersion)
    loaderVersion = await getLoaderVersion(self.source)
    if not await downloadServer(self.source, serverJarPath, mcVersion, loaderVersion):
        print('Fabric 服务端下载失败。')
        return False
    console.print('Fabric 服务端下载完成。')
    return serverName, serverType, serverPath, javaPath, data