import subprocess
from hsl import HSL
class Server(HSL):
    def __init__(self,*,name: str,type: str,path: str,javaVersion: str,maxRam: str):
        super().__init__()
        self.name = name #name
        self.type = type
        self.path = path #path
        self.javaVersion = javaVersion #6 8 11 16 17 21
        self.maxRam = maxRam #in MB

    def run(self):
        javaPath = self.Java.getJavaByJavaVersion(self.javaVersion)
        if self.type == 'vanilla':
            run_command = f'{javaPath} -Xmx{self.maxRam} -jar server.jar nogui'
        subprocess.Popen(run_command.split(" "),cwd=self.path)