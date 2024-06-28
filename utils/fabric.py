import requests
from utils.download import downloadFile

async def getMcVersions(source) -> list:
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
async def getLoaderVersion(source) -> str:
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
async def downloadServer(source,path,mcVersion,loaderVersion) -> bool:
    sources = source["fabric"]['list']
    for source in sources:
        if source['type'] == "official":
            url = source['installer'].replace(r'{version}',mcVersion).replace(r'{loader}',loaderVersion)
            if downloadFile(url,path):
                return True
               
    return False