from utils.download import downloadFile
async def downloadLatest(source,path):
    sources = source["mc"]["paper"]['list']
    for source in sources:
        if source['type'] == "official":
            if downloadFile(source['latest'],path):
                return