import requests
import re
import subprocess
import psutil
from rich.console import Console
from utils.download import downloadFile
FORGE_REGEX = re.compile(r'(\w+)-(\w+)')
console = Console()
async def nameJoin(baseurl: str,mcVersion:str, forgeversion: str,category: str,format: str):
    return f'{baseurl}{mcVersion}/{forgeversion}/forge-{mcVersion}-{forgeversion}-{category}.{format}'
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
            status = downloadFile(source['download'],path,params=params)
            if status:
                return True
        if source['type'] == 'official':
            url = await nameJoin(source['download'],mcVersion,version,'installer','jar')
            status = downloadFile(url, path)
    return False
async def run_install(javaPath: str,path: str):
    cmd = f'{javaPath} -jar forge-installer.jar --installServer'
    console.log(f'Run Forge Install Args: {cmd}')
    Process = subprocess.Popen(args=cmd.split(" "),cwd=path)
    while psutil.pid_exists(Process.pid):
        pass
    return True