def nameJoin(baseurl,forgeversion,category,format):
    return f'{baseurl}{forgeversion}/forge-{forgeversion}-{category}.{format}'
    #return baseurl + forgeversion + '/forge-' + forgeversion + '-' + category + '.' + format