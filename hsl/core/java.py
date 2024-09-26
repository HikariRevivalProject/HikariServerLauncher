import os
import zipfile
from rich.console import Console
from hsl.core.main import HSL
from hsl.utils.download import downloadfile

console = Console()
if os.name == 'nt':
    JAVA_EXEC = 'java.exe'
    # Windows
elif os.name == 'posix':
    JAVA_EXEC = 'java'
    # Linux
async def recursive_chmod(directory, mode):
    """
        Recursively change the permissions of a directory and its contents.
        Args: 
            directory(str):  directory path
            mode(int):  permission mode
    """

    for root, dirs, files in os.walk(directory):
        for d in dirs:
            os.chmod(os.path.join(root, d), mode)
        for f in files:
            os.chmod(os.path.join(root, f), mode)

class Java(HSL):

    def __init__(self):
        super().__init__()
    
    async def getJavaVersion(self,mcVersion: str) -> str:
        """
            Get java version by game version.

            Args: 
                mcVersion(int):  mc version
        
            Returns: 
                str: java version should be used
        """
        parts = mcVersion.split('.')
        version = int(parts[1])
        if version <= 6:
            return '6'
        elif version == 7:
            return '8'
        elif 7 < version <= 16:
            return '8'
        elif 16 < version < 20:
            return '17'
        elif version >= 20:
            return '21'
        else:
            return '0'
    async def checkJavaExist(self,javaVersion,path) -> bool:
        """
            Check if Java exists.
            Args: 
                javaVersion(int):  Java version
                path(str):  workspace path
        
            Returns: 
                bool: True if the java exists, False otherwise.
        """

        if not os.path.exists(os.path.join(path, 'java', javaVersion, 'bin', JAVA_EXEC)):
            return False
        return True
    async def downloadJava(self, javaVersion, path) -> bool:
        """
            Download Java and return the status.

            Args: 
                javaVersion(int):  Java version
                path(str):  workspace path
        
            Returns: 
                bool: True if the java is downloaded and extracted successfully, False otherwise.
        """
        sources = self.source['java']['list']
        if self.config.use_mirror:
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
            if await downloadfile(url,filename):
                with zipfile.ZipFile(filename,'r') as file:
                    file.extractall(path)
                #change permission for linux
                await recursive_chmod(path, 0o755)
                os.remove(filename)
                return True
        return False
        
    async def getJavaByGameVersion(self, mcVersion: str, path: str) -> str:
        """
            get java path by game version(if not exist, will call downloadJava)

            Args: 
                mcVersion(int):  mc version
                path(str):  workspace path
        
            Returns: 
                str: java executeable file path
        """
        javaVersion = await self.getJavaVersion(mcVersion)
        javaPath = os.path.join(path,'java',javaVersion)
        if not await self.checkJavaExist(javaVersion, path):
            console.print(f'[red] Java版本 {javaVersion} 不存在。正在下载Java...')
            await self.downloadJava(javaVersion, path)
        return os.path.join(javaPath, 'bin', JAVA_EXEC)

    async def getJavaByJavaVersion(self, javaVersion:str, path:str) -> str:
        """
            get java path by java version(if not exist, will call downloadJava)

            Args: 
                javaVersion(int):  java version
                path(str):  workspace path
        
            Returns: 
                str: java executeable file path
        """
        javaPath = os.path.join(path,'java',javaVersion)
        if not await self.checkJavaExist(javaVersion, path):
            console.print(f'[red] Java版本 {javaVersion} 不存在。正在下载Java...')
            await self.downloadJava(javaVersion, path)
        return os.path.join(javaPath,'bin',JAVA_EXEC)