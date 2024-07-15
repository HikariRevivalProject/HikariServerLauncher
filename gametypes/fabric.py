import requests
from rich.console import Console
from utils.prompt import promptSelect
from utils.download import downloadFile
console = Console()
async def getMcVersions(source: dict) -> list:
    sources = source["fabric"]['list']
    for source in sources:
        if source['type'] == "official":
            try:
                response = requests.get(source['supportList'])
                if response.status_code == 200:
                    fabVersions = response.json()
                    return [i['version'] for i in fabVersions if i['stable'] == True]
            except:
                pass
    return []
async def getLoaderVersion(source: dict) -> str:
    sources = source["fabric"]['list']
    for source in sources:
        if source['type'] == "official":
            try:
                response = requests.get(source['loaderList'])
                if response.status_code == 200:
                    loaderList = response.json()
                    return loaderList[0]['version']
            except:
               pass
    return ''
async def downloadServer(
        source: dict,
        path: str,
        mcVersion: str,
        loaderVersion: str
    ) -> bool:
    sources = source["fabric"]['list']
    for source in sources:
        if source['type'] == "official":
            url = source['installer'].replace(r'{version}',mcVersion).replace(r'{loader}',loaderVersion)
            if downloadFile(url,path):
                return True
               
    return False
async def install(self, serverName: str, serverPath: str, serverJarPath: str, data: str):
    serverType = 'fabric'
    fabVersion = await getMcVersions(self.source)
    mcVersion = fabVersion[await promptSelect(fabVersion, '请选择 Fabric 服务器版本:')]
    javaPath = await self.Java.getJavaByGameVersion(mcVersion, path=self.config.workspace_dir)
    loaderVersion = await getLoaderVersion(self.source)
    if not await downloadServer(self.source, serverJarPath, mcVersion, loaderVersion):
        print('Fabric 服务端下载失败。')
        return False
    console.print('Fabric 服务端下载完成。')
    return serverName, serverType, serverPath, javaPath, data