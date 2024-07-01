import os
import subprocess
from rich.console import Console
from threading import Thread
import psutil
from queue import Queue
from hsl import HSL

console = Console()

class Server(HSL):
    """
    Server Class
    """
    def readLine(self, process, output_queue: Queue):
        for line in iter(process.stdout.readline, b''):
            try:
                output_queue.put(line.decode('utf-8').strip())
            except UnicodeDecodeError:
                output_queue.put(line.decode('gbk').strip())
            if process.poll() is not None:
                output_queue.put(None)
                break
                
    def input(self, process, input_queue: Queue):
        while True:
            try:
                command_input = input(f'({self.name}) >>> ')
            except KeyboardInterrupt:
                console.log("已退出输入")
                process.kill()
                break
            except EOFError:
                console.log("已退出输入")
                process.kill()
                break
            input_queue.put(command_input)
            if input_queue.get() is None:
                break
            try:
                process.stdin.write(command_input.encode('utf-8') + b'\n')
                process.stdin.flush()
            except OSError:
                os._exit(0)

    def check_process(self, process):
        return psutil.pid_exists(process.pid)
    def __init__(self, *, name: str, type: str, path: str, javaPath: str, maxRam: str, data={}):
        super().__init__()
        self.name = name
        self.type = type
        self.path = path
        self.javaPath = javaPath
        self.maxRam = maxRam
        self.data = data
    def run(self):
        if 'startup_cmd' in self.data:
            subprocess.Popen(self.data['startup_cmd'],cwd=self.path)
        jvm_setting: str = ''
        if 'jvm_setting' in self.data:
            jvm_setting: str = ' ' + self.data['jvm_setting']
        match self.type:
            case 'vanilla':
                run_command = f'{self.javaPath} -Dfile.encoding=utf-8 -Xmx{self.maxRam} -jar server.jar'
            case 'paper':
                run_command = f'{self.javaPath} -Dfile.encoding=utf-8 -Xmx{self.maxRam} -jar server.jar'
            case 'fabric':
                run_command = f'{self.javaPath} -Dfile.encoding=utf-8 -Xmx{self.maxRam} -jar server.jar'
            case 'forge':
                mcVersion = self.data['mcVersion']
                forgeVersion = self.data['forgeVersion']
                mcMajorVersion = int(mcVersion.split('.')[1])
                if mcMajorVersion >= 17:
                    if os.name == 'nt':
                        run_command = f'{self.javaPath}{jvm_setting} -Dfile.encoding=utf-8 -Xmx{self.maxRam} @user_jvm_args.txt @libraries/net/minecraftforge/forge/{mcVersion}-{forgeVersion}/win_args.txt %*'
                    else:
                        run_command = f'{self.javaPath}{jvm_setting} -Dfile.encoding=utf-8 -Xmx{self.maxRam} @user_jvm_args.txt @libraries/net/minecraftforge/forge/{mcVersion}-{forgeVersion}/unix_args.txt %*'
                if mcMajorVersion < 17:
                    run_command = f'{self.javaPath} -Dfile.encoding=utf-8 -Xmx{self.maxRam} -jar forge-{mcVersion}-{forgeVersion}.jar'
        console.log(f'Run Command: {run_command}')

        output_queue = Queue()
        input_queue = Queue()

        process = subprocess.Popen(
            run_command.split(" "),
            cwd=self.path,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        
        t2 = Thread(target=self.input, args=(process, input_queue))
        t1 = Thread(target=self.readLine, args=(process, output_queue))

        t1.start()
        t2.start()

        while self.check_process(process):
            line = output_queue.get()
            if line is None:
                break
            console.print(line)

        #t1.join()
        #t2.join()


