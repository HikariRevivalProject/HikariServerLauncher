import os
import zipfile
import shutil
from config import Config
from workspace import Workspace
from utils.download import downloadFile

Config = Config()
Workspace = Workspace()
if os.name == 'nt':
    JAVA_EXEC = 'java.exe'
elif os.name == 'posix':
    JAVA_EXEC = 'java'
else:
    raise Exception('Unsupported OS')
async def getJavaVersion(mcVersion):
    parts = mcVersion.split('.')
    version = int(parts[1])
    if version <= 6:
        return '6'
    elif version == 7:
        return '8'
    elif 7 < version <= 16:
        return '11'
    elif 16 < version < 20:
        return '17'
    elif version >= 20:
        return '21'
    else:
        return '0'
async def checkJavaExist(javaVersion):
    if not os.path.exists(os.path.join(Workspace.path,'java',javaVersion,'bin',JAVA_EXEC)):
        return False
    return True
async def downloadJava(javaVersion,source):
    sources = source['java']['list']
    path = os.path.join(Workspace.path,'java',javaVersion)
    filename = os.path.join(path,'java.zip')
    #make dir
    if not os.path.exists(path):
        os.makedirs(path)
    #get source
    for i in sources:
        if os.name == 'nt':
            url = i['windows'][javaVersion]
        if os.name == 'posix':
            url = i['linux'][javaVersion]
        if downloadFile(url,filename):
            #if downloaded successfully break
            break
    #unzip java.zip
    with zipfile.ZipFile(filename,'r') as file:
        file.extractall(path)
    os.remove(filename)
async def getJava(mcVersion,source):
    javaVersion = await getJavaVersion(mcVersion)
    javaPath = os.path.join(Workspace.path,'java',javaVersion)
    if not await checkJavaExist(javaVersion):
        print(f'Java版本 {javaVersion} 不存在。正在下载Java...')
        await downloadJava(javaVersion,source)
    return os.path.join(javaPath,'bin',JAVA_EXEC)