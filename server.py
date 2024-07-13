import os
import psutil
import subprocess
import asyncio
from aioconsole import ainput
from threading import Thread
from queue import Queue
from rich import box
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from hsl import HSL

console = Console()

class Server(HSL):
    """
    Server Class
    """
    def __init__(self, *, name: str, type: str, path: str, javaPath: str, maxRam: str, data={}):
        super().__init__()
        self.name = name
        self.type = type
        self.path = path
        self.javaPath = javaPath
        self.maxRam = maxRam
        self.data = data
    
    # async def get_process_info(self, pid: int):
    #     try:
    #         p = psutil.Process(pid)
            
    #         cpu_percent = p.cpu_percent(interval=1)
            
    #         mem_info = p.memory_info()
    #         rss = mem_info.rss / (1024 * 1024)
    #         vms = mem_info.vms / (1024 * 1024)
            
    #         memory_percent = p.memory_percent()
            
    #         return {
    #             'pid': pid,
    #             'name': p.name(),
    #             'cpu_percent': cpu_percent,
    #             'memory_percent': memory_percent,
    #             'rss': rss,
    #             'vms': vms
    #         }
    #     except psutil.NoSuchProcess:
    #         return None
    # def create_panel(self, table, process_info):
    #     if process_info:
    #         table.add_row(
    #             str(process_info['pid']),
    #             f"{process_info['cpu_percent']}%",
    #             f"{process_info['memory']} MB",
    #             f"{process_info['memory_percent']}%",
    #             f"{process_info['rss']} MB",
    #             f"{process_info['vms']} MB"
    #         )
    #     return Panel(table, title=self.name, expand=True)

    # def create_layout(self, table, process_info, output: str):
    #     os_panel = self.create_panel(table, process_info)
    #     layout = Panel.fit(f'[panel]\n{os_panel}\n[/]\n{output}', title=self.name)
    #     return layout
    def pathJoin(self, path: str) -> str:
        return os.path.join(os.getcwd(), self.path, path)

    async def Output(self, process, output_queue: Queue):
        for line in iter(process.stdout.readline, b''):
            try:
                output_queue.put(line.decode('utf-8').strip())
            except UnicodeDecodeError:
                output_queue.put(line.decode('gbk').strip())
            if process.poll() is not None:
                output_queue.put(None)
                break
            if self.check_process(process):
                line = output_queue.get()
                console.log(line)
        return
    def consoleOutput(self, process, output_queue: Queue):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.Output(process, output_queue))
    async def get_input(self, process, input_queue: Queue):
        while True:
            try:
                command_input = await ainput(f'({self.name}) >>> ')
            except (KeyboardInterrupt, EOFError):
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
        return
    def consoleInput(self, process, input_queue: Queue):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.get_input(process, input_queue))

    def check_process(self, process):
        return psutil.pid_exists(process.pid)

    def gen_run_command(self, export: bool = False) -> str:
        javaexecPath = self.javaPath if os.name != 'posix' else (r'./../../' + self.javaPath if not self.config.direct_mode else r'./' + self.javaPath)
        
        if export:
            run_dir = os.getcwd()
            javaexecPath = os.path.join(run_dir, javaexecPath)
            run_command = self._build_run_command(javaexecPath, export=True)
            return f'cd {os.path.join(os.getcwd(), self.path)}\n{run_command}'

        return self._build_run_command(javaexecPath)

    def _build_run_command(self, javaexecPath, export=False):
        jvm_setting = self.data.get('jvm_setting', '')

        if self.type in ['vanilla', 'paper', 'fabric']:
            return f'{javaexecPath} -Dfile.encoding=utf-8 -Xmx{self.maxRam} -jar {self.pathJoin("server.jar")}' if export else f'{javaexecPath} -Dfile.encoding=utf-8 -Xmx{self.maxRam} -jar server.jar'
        
        mcVersion = self.data['mcVersion']
        forgeVersion = self.data['forgeVersion']
        mcMajorVersion = int(mcVersion.split('.')[1])
        
        if mcMajorVersion >= 17:
            args_path = f"@{self.pathJoin(f'libraries/net/minecraftforge/forge/{mcVersion}-{forgeVersion}/unix_args.txt')}" if os.name == 'posix' else f"@{self.pathJoin(f'libraries/net/minecraftforge/forge/{mcVersion}-{forgeVersion}/win_args.txt')}"
            if jvm_setting:
                console.log(f'[Debug]: Jvm Setting: {jvm_setting}')
                return f'{javaexecPath}{jvm_setting} -Dfile.encoding=utf-8 -Xmx{self.maxRam} @user_jvm_args.txt {args_path} %*'
            return f'{javaexecPath} -Dfile.encoding=utf-8 -Xmx{self.maxRam} @user_jvm_args.txt {args_path} '
        
        return f'{javaexecPath} -Dfile.encoding=utf-8 -Xmx{self.maxRam} -jar {self.pathJoin(f"forge-{mcVersion}-{forgeVersion}.jar")}' if export else f'{javaexecPath} -Dfile.encoding=utf-8 -Xmx{self.maxRam} -jar forge-{mcVersion}-{forgeVersion}.jar'

    async def run(self):
        if 'startup_cmd' in self.data:
            subprocess.Popen(self.data['startup_cmd'], cwd=self.path)

        run_command = self.gen_run_command()

        if self.config.debug:
            console.log(f'[Debug]: Run Command: {run_command}')
        # table = Table(
        #     "PID", "CPU %", "Memory", "Memory %", "RSS", "VMS", box=box.SIMPLE, title=self.name
        # )
        workdir = self.path if not self.config.direct_mode else None

        process = subprocess.Popen(
            run_command.split(" "),
            cwd=workdir,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        output_queue = Queue()
        input_queue = Queue()
        
        #t1 = Thread(target=self.consoleOutput, args=(table, process, output_queue))
        t1 = Thread(target=self.consoleOutput, args=(process, output_queue))
        t2 = Thread(target=self.consoleInput, args=(process, input_queue))

        t1.start()
        t2.start()

        t1.join()
