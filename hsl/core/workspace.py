from hsl.core.main import HSL
import json
import os
import shutil
from hsl.core.server import Server
class Workspace(HSL):
    def __init__(self):
        super().__init__()
        self.workspaces = []
        self.dir = self.config.workspace_dir
        self.file = self.config.workspace_file
        self.path = os.path.join(self.dir, self.file)

        self.workspace_init()
    def workspace_init(self):
        try:
            self.load()
        except FileNotFoundError:
            if not os.path.exists(self.dir):
                os.makedirs(self.dir)
            self.save()
    def save(self):
        with open(self.path, 'w') as f:
            json.dump(self.workspaces, f)
    def load(self):
        with open(self.path, 'r') as f:
            self.workspaces = json.load(f)
    async def create(self, *, server_name: str):
        serverPath = os.path.join(self.dir,server_name)
        if not os.path.exists(serverPath):
            os.makedirs(serverPath)
        with open(os.path.join(serverPath,'eula.txt'), 'w') as f:
            f.write('eula=true')
        return serverPath
    async def add(self, Server: Server):
        self.workspaces.append({
            "name": Server.name,
            "type": Server.type,
            "path": Server.path,
            "javaPath": Server.javaPath,
            "maxRam": Server.maxRam,
            "data": Server.data
        })
        self.save()
    async def get(self, index: int) -> Server:
        server = self.workspaces[index]
        return Server(
            name = server["name"],
            type = server["type"],
            path = server["path"],
            javaPath = server["javaPath"],
            maxRam = server["maxRam"],
            data = server["data"]
        )
    async def getFromName(self, name: str) -> Server:
        for server in self.workspaces:
            if server["name"] == name:
                return Server(
                    name = server["name"],
                    type = server["type"],
                    path = server["path"],
                    javaPath = server["javaPath"],
                    maxRam = server["maxRam"],
                    data = server["data"]
                )
        raise Exception("Server not found")
    async def delete(self, index: int):
        try:
            shutil.rmtree(self.workspaces[index]["path"])
        except:
            pass
        del self.workspaces[index]
        self.save()

    async def modify(self, index: int, key: str, value: str):
        self.workspaces[index][key] = value
        self.save()
        self.load()
    async def modifyData(self, index: int, key: str, value: str):
        self.workspaces[index]['data'][key] = value
        self.save()
        self.load()