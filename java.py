import os
import zipfile
from utils.download import downloadFile
from hsl import HSL


if os.name == 'nt':
    JAVA_EXEC = 'java.exe'
elif os.name == 'posix':
    JAVA_EXEC = 'java'
class Java(HSL):
    def __init__(self):
        super().__init__()
    async def getJavaVersion(self,mcVersion) -> str:
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
    async def checkJavaExist(self,javaVersion,path) -> bool:
        if not os.path.exists(os.path.join(path,'java',javaVersion,'bin')):
            return False
        return True
    async def downloadJava(self,javaVersion,path):
        sources = self.source['java']['list']
        if self.config['use_mirror']:
            sources = sources[::-1]
        path = os.path.join(path,'java',javaVersion)
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
                break
        #unzip java.zip
        with zipfile.ZipFile(filename,'r') as file:
            file.extractall(path)
        os.remove(filename)
    async def getJavaByGameVersion(self, mcVersion: str, path: str):
        javaVersion = await self.getJavaVersion(mcVersion)
        javaPath = os.path.join(path,'java',javaVersion)
        if not await self.checkJavaExist(javaVersion, path):
            print(f'Java版本 {javaVersion} 不存在。正在下载Java...')
            await self.downloadJava(javaVersion, path)
        return os.path.join(javaPath, 'bin', JAVA_EXEC)

    async def getJavaByJavaVersion(self, javaVersion:str, path:str) -> str:
        javaPath = os.path.join(path,'java',javaVersion)
        if not await self.checkJavaExist(javaVersion, path):
            print(f'Java版本 {javaVersion} 不存在。正在下载Java...')
            await self.downloadJava(javaVersion, path)
        return os.path.join(javaPath,'bin',JAVA_EXEC)