import subprocess
import asyncio
from hsl import HSL
class Server(HSL):
    """
    Server Class
    """
    async def readLine(self,process):
        while True:
            line = process.stdout.readline()
            if line == b'':
                break
            print(line.decode('utf-8').strip())
            #yield line.decode('utf-8').strip()
    async def input(self,process):
        while True:
            command_input = input()
            process.stdin.write(command_input.encode('utf-8'))
            process.stdin.flush()
    def __init__(self,*,name: str,type: str,path: str,javaPath: str,maxRam: str):
        super().__init__()
        self.name = name
        self.type = type
        self.path = path
        self.javaPath = javaPath
        self.maxRam = maxRam

    async def run(self):
        if self.type == 'vanilla':
            run_command = f'{self.javaPath} -Xmx{self.maxRam} -jar server.jar'
        if self.type == 'paper':
            run_command = f'{self.javaPath} -Xmx{self.maxRam} -jar server.jar'
        ServerProcess = subprocess.Popen(
            run_command.split(" "),
            cwd=self.path, 
            stdin = subprocess.PIPE, 
            stdout = subprocess.PIPE, 
            stderr = subprocess.PIPE
        )
        outputTask = asyncio.create_task(self.readLine(ServerProcess))
        #inputTask = asyncio.create_task(self.input(ServerProcess))
        await asyncio.gather(outputTask)#,inputTask)
