from hsl import HSL
import json
import os
import shutil
from server import Server
class Workspace(HSL):
    def __init__(self):
        super().__init__()
        self.workspaces = []
        self.path = self.config["workspace"]
        self.file_path = self.config["workspace_path"]

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
    async def add(self, Server: Server):
        self.workspaces.append({
            "name": Server.name,
            "type": Server.type,
            "path": Server.path,
            "javaPath": Server.javaPath,
            "maxRam": Server.maxRam
        })
        self.save()
    async def get(self, index: int):
        server = self.workspaces[index]
        return Server(
            name = server["name"],
            type = server["type"],
            path = server["path"],
            javaPath = server["javaPath"],
            maxRam = server["maxRam"]
        )
    async def delete(self, index: int):
        shutil.rmtree(self.workspaces[index]["path"])
        del self.workspaces[index]
        self.save()
