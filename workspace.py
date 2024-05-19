import os
import json
import shutil
from config import Config
from server import Server
class Workspace:
    global Server, Config
    def __init__(self):
        self.config = Config().config
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
    def create(self,Server: Server):
        self.workspaces.append({"name":Server.name,"path":Server.path,"run_command":Server.run_command})
        if not os.path.exists(Server.path):
            os.makedirs(Server.path)
            with open(os.path.join(Server.path,"eula.txt"), 'w') as f:
                f.write("eula=true")
        self.save()
    def delete(self,index):
        shutil.rmtree(self.workspaces[index]["path"])
        del self.workspaces[index]
        self.save()