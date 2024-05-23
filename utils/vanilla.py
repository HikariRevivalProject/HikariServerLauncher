import requests
from utils.download import downloadFile
async def get_versions(source,use_bmclapi=False) -> list:
    sources = source["mc"]["vanilla"]['list']
    if use_bmclapi:
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
async def downloadServer(source,gameVersion,path,use_bmclapi=False) -> bool:
    sources = source["mc"]["vanilla"]['list']
    if use_bmclapi:
        sources = sources[::-1]
    for source in sources:
        if source['type'] == 'bmclapi':
            if downloadFile(source['server'].replace('{version}',gameVersion),path):
                return True
    return False