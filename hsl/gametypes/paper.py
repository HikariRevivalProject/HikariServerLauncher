from hsl.utils.download import downloadfile
from hsl.source.source import Source
from rich.console import Console
console = Console()
async def downloadLatest(source: Source, path: str, experiemental=False) -> bool:
    channel = 'experimental' if experiemental else 'stable'
    sources = source.mc.paper.list
    for paper_source in sources:
        if paper_source.type == channel:
            return await downloadfile(paper_source.latest,path)
    return False
async def getLatestVersionName(source: Source) -> str:
    return source.mc.paper.latestVersionName

async def install(self, serverName: str, serverPath: str, serverJarPath: str, data: dict):
    experimental = data.get('experimental', False)
    serverType = 'paper'
    mcVersion = await getLatestVersionName(self.source)
    javaPath = await self.Java.getJavaVersion(mcVersion)
    if not await downloadLatest(self.source, serverJarPath, experiemental=experimental):
        console.print('Paper 服务端下载失败。')
        return False
    console.print('Paper 服务端下载完成。')
    return serverName, serverType, serverPath, javaPath, data