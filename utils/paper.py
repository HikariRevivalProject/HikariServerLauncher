from utils.download import downloadFile
async def downloadLatest(source,path) -> bool:
    sources = source["mc"]["paper"]['list']
    for source in sources:
        if source['type'] == "official":
            if downloadFile(source['latest'],path):
                return True
    return False
async def getLatestVersionName(source) -> str:
    return source["mc"]["paper"]['latestVersionName']
    