import requests
import re
import os
import subprocess
import psutil
from rich.console import Console
from hsl.gametypes import vanilla
from hsl.utils.download import downloadfile
from hsl.utils.prompt import promptSelect
FORGE_REGEX = re.compile(r'(\w+)-(\w+)')
console = Console()
async def nameJoin(baseurl: str,mcVersion:str, forgeversion: str,category: str,format: str):
    return f'{baseurl}{mcVersion}-{forgeversion}/forge-{mcVersion}-{forgeversion}-{category}.{format}'
    #return baseurl + forgeversion + '/forge-' + forgeversion + '-' + category + '.' + format
async def get_mcversions(source: dict,use_bmclapi: bool=False) -> list:
    sources = source["forge"]['list']
    if use_bmclapi:
        sources = sources[::-1]
    for source in sources:
        if source['type'] == 'bmclapi':
            try:
                response = requests.get(source['supportList'])
                if response.status_code == 200:
                    versions = response.json()
                    return versions
            except:
                pass
        if source['type'] == 'official':
            try:
                response = requests.get(source['metadata'])
                if response.status_code == 200:
                    versions = list(response.json().keys())
                    return versions
            except:
                pass
    return []
async def get_forgeversions(source: dict,mcVersion: str,use_bmclapi: bool=False) -> list:
    sources = source["forge"]['list']
    if use_bmclapi:
        sources = sources[::-1]
    for source in sources:
        if source['type'] == 'bmclapi':
            try:
                response = requests.get(source['getByVersion'].replace('{version}',mcVersion))
                if response.status_code == 200:
                    versions = response.json()
                    sorted_versions = sorted(versions,key=lambda i: i['build'],reverse=True)
                    installer_versions = [i for i in sorted_versions if 'files' in i and any(j.get('format') == 'jar' and j.get('category') == 'installer' for j in i.get('files', []))]
                    return [i['version'] for i in installer_versions]
            except:
                pass
        if source['type'] == 'official':
            try:
                response = requests.get(source['metadata'])
                if response.status_code == 200:
                    versions = list(response.json()[mcVersion])[::-1]
                    return versions
            except:
                pass
    return []
async def download_installer(source: dict,mcVersion: str,version: str,path: str,use_bmclapi: bool=False) -> bool:
    sources = source["forge"]['list']
    if use_bmclapi:
        sources = sources[::-1]
    for source in sources:
        if source['type'] == 'bmclapi':
            if '-' in version:
                mcVersion,version = re.findall(FORGE_REGEX,version)
            params = {
                'mcversion': mcVersion,
                'version': version,
                'category': 'installer',
                'format': 'jar'
            }
            status = await downloadfile(source['download'],path,params=params)
            return status
        if source['type'] == 'official':
            url = await nameJoin(source['download'],mcVersion,version,'installer','jar')
            status = await downloadfile(url, path)
            return status
    return False
async def run_install(javaPath: str,path: str):
    cmd = f'{javaPath} -jar forge-installer.jar --installServer'
    console.log(f'Run Forge Install Args: {cmd}')
    Process = subprocess.Popen(args=cmd.split(" "),cwd=path)
    while psutil.pid_exists(Process.pid):
        pass
    return True
async def install(self, serverName: str, serverPath: str, serverJarPath: str, data: dict):
        serverType = 'forge'
        mcVersions = await vanilla.get_versions(self.source)
        _mcVersions = await get_mcversions(self.source, self.config.use_mirror)
        mcVersions = [x['id'] for x in mcVersions if x['type'] == 'release' and x['id'] in _mcVersions]
        index = await promptSelect(mcVersions, '请选择 Minecraft 版本:')
        mcVersion = mcVersions[index]

        javaPath = await self.Java.getJavaByGameVersion(mcVersion, path=self.config.workspace_dir)
        forgeVersions = await get_forgeversions(self.source, mcVersion, self.config.use_mirror)
        index = await promptSelect(forgeVersions, '请选择 Forge 版本:')
        forgeVersion = forgeVersions[index]
        #1.21-51.0.21
        if '-' in forgeVersion:
            forgeVersion = forgeVersion.split('-')[1]
            #51.0.21
        data['mcVersion'] = mcVersion
        data['forgeVersion'] = forgeVersion

        installerPath = os.path.join(serverPath, 'forge-installer.jar')
        if not await download_installer(self.source, mcVersion, forgeVersion, installerPath, self.config.use_mirror):
            console.print('Forge 安装器下载失败。')
            return False
        console.print('Forge 安装器下载完成，尝试执行安装...')

        if not await run_install(javaPath, serverPath):
            console.print('Forge 安装失败。')
            return False
        console.print('Forge 安装完成。')

        return serverName, serverType, serverPath, javaPath, data