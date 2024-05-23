import requests
import os
import json
import shutil
import asyncio
import subprocess
import zipfile

from utils.download import downloadFile
from config import Config

if os.name == 'nt':
    JAVA_EXEC = 'java.exe'
elif os.name == 'posix':
    JAVA_EXEC = 'java'

VERSION = r'http://hsl.hikari.bond/hsl.json'
DOWNLOAD_SOURCE = r'http://hsl.hikari.bond/source.json'
class HSL:
    def __init__(self):
        self.source = self.get_source()
    def check_update(self,version: int) -> tuple:
        r = requests.get(VERSION)
        if r.status_code == 200:
            latest: int = r.json()['version']
            if version < latest:
                return True, latest
            else:
                return False, version
        else:
            return False, version
    def get_source(self) -> dict:
        r = requests.get(DOWNLOAD_SOURCE)
        if r.status_code == 200:
            return r.json()
        else:
            return {}

class Workspace(HSL):
    def __init__(self):
        super().__init__()
        self.workspaces = []
        self.path = Config().config["workspace"]
        self.file_path = Config().config["workspace_path"]

        self.initialize()
    def initialize(self):
        try:
            self.load()
        except FileNotFoundError:
            if not os.path.exists(self.path):
                os.makedirs(self.path)
            self.save()
    def save(self):
        with open(self.file_path, 'w') as f:
            json.dump(self.workspaces, f)
    def load(self):
        with open(self.file_path, 'r') as f:
            self.workspaces = json.load(f)
    async def create(self, *, server_name: str):
        serverPath = os.path.join(self.path,server_name)
        if not os.path.exists(serverPath):
            os.makedirs(serverPath)
            with open(os.path.join(serverPath,"eula.txt"), 'w') as f:
                f.write("eula=true")
        return serverPath
    async def add(self, Server):
        self.workspaces.append({
            "name": Server.name,
            "type": Server.type,
            "path": Server.path,
            "javaVersion": Server.javaVersion,
            "maxRam": Server.maxRam
        })
        self.save()
    async def get(self, index: int):
        server = self.workspaces[index]
        return Server(
            name = server["name"],
            type = server["type"],
            path = server["path"],
            javaVersion = server["javaVersion"],
            maxRam = server["maxRam"]
        )
    async def delete(self, index: int):
        shutil.rmtree(self.workspaces[index]["path"])
        del self.workspaces[index]
        self.save()

class Server(HSL):
    def __init__(self,*,name: str,type: str,path: str,javaVersion: str,maxRam: str):
        super().__init__()
        self.name = name #name
        self.type = type
        self.path = path #path
        self.javaVersion = javaVersion #6 8 11 16 17 21
        self.maxRam = maxRam #in MB

    async def run(self):
        javaPath = await Java().getJavaByJavaVersion(self.javaVersion)
        if self.type == 'vanilla':
            run_command = f'{javaPath} -Xmx{self.maxRam} -jar server.jar nogui'
        if self.type == 'paper':
            run_command = f'{javaPath} -Xmx{self.maxRam} -jar server.jar nogui'
        Server = subprocess.Popen(
            run_command.split(" "),
            cwd=self.path, 
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )

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
    async def checkJavaExist(self,javaVersion) -> bool:
        if not os.path.exists(os.path.join(Workspace().path,'java',javaVersion,'bin',JAVA_EXEC)):
            return False
        return True
    async def downloadJava(self,javaVersion):
        sources = self.source['java']['list']
        path = os.path.join(Workspace().path,'java',javaVersion)
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
    async def getJavaByGameVersion(self,mcVersion: str):
        javaVersion = await self.getJavaVersion(mcVersion)
        javaPath = os.path.join(Workspace().path,'java',javaVersion)
        if not await self.checkJavaExist(javaVersion):
            print(f'Java版本 {javaVersion} 不存在。正在下载Java...')
            await self.downloadJava(javaVersion)
        return (
            javaVersion,
            os.path.join(javaPath,'bin',JAVA_EXEC)
            )
    async def getJavaByJavaVersion(self,javaVersion) -> str:
        javaPath = os.path.join(Workspace().path,'java',javaVersion)
        if not await self.checkJavaExist(javaVersion):
            print(f'Java版本 {javaVersion} 不存在。正在下载Java...')
            await self.downloadJava(javaVersion)
        return os.path.join(javaPath,'bin',JAVA_EXEC)