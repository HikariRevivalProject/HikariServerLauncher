def nameJoin(baseurl: str,forgeversion: str,category: str,format: str):
    return f'{baseurl}{forgeversion}/forge-{forgeversion}-{category}.{format}'
    #return baseurl + forgeversion + '/forge-' + forgeversion + '-' + category + '.' + format