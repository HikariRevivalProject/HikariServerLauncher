from utils.download import downloadFile
from rich.console import Console
console = Console()
async def downloadLatest(source,path) -> bool:
    sources = source["mc"]["paper"]['list']
    for source in sources:
        if source['type'] == "official":
            if downloadFile(source['latest'],path):
                return True
    return False
async def getLatestVersionName(source) -> str:
    return source["mc"]["paper"]['latestVersionName']

async def install(self, serverName: str, serverPath: str, serverJarPath: str, data: dict):
    serverType = 'paper'
    mcVersion = await getLatestVersionName(self.source)
    javaPath = await self.Java.getJavaByGameVersion(mcVersion, path=self.config.workspace_dir)
    if not await downloadLatest(self.source, serverJarPath):
        console.print('Paper 服务端下载失败。')
        return False
    console.print('Paper 服务端下载完成。')
    return serverName, serverType, serverPath, javaPath, data