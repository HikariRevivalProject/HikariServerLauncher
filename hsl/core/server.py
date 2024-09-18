import os
import psutil
# import asyncio
# import subprocess

from hsl.core.main import HSL
# from queue import Queue
# from rich.live import Live
# from rich.table import Table
# from rich.panel import Panel
# from rich.layout import Layout
# from threading import Thread
# from aioconsole import ainput
from rich.console import Console


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
            
    #         cpu_percent = p.cpu_percent()
            
    #         mem_info = p.memory_info()
    #         rss = int(mem_info.rss / (1024 * 1024))
            
    #         memory_percent = int(p.memory_percent())
            
    #         return {
    #             'pid': pid,
    #             'cpu_percent': cpu_percent,
    #             'memory_percent': memory_percent,
    #             'memory': rss,
    #         }
    #     except psutil.NoSuchProcess:
    #         return None
    # async def create_panel(self, table):
        
    #     return Panel(table, title=self.name, expand=True)
    #async def monitor_process(self, process, output_queue: Queue):
    def pathJoin(self, path: str) -> str:
        return os.path.join(os.getcwd(), self.path, path)

    # async def Output(self, process):
    #     output_text = ''
        
    #     layout = Layout()
    #     layout.split_column(Layout(name='monitor',ratio=3), Layout(name='output',ratio=6))
    #     with Live(layout) as live:
    #         for line in iter(process.stdout.readline, b''):
    #             table = Table(
    #             "PID", "CPU %", "Memory %", "Memory", show_header=True, show_edge=True, header_style="bold magenta"
    #             )
    #             try:
    #                 output_text += line.decode('utf-8').strip() + '\n'
    #             except UnicodeDecodeError:
    #                 output_text += line.decode('gbk').strip() + '\n'                   
    #             process_info = await self.get_process_info(process.pid)
    #             if process_info:
    #                 table.add_row(
    #                     str(process_info['pid']),
    #                     f"{process_info['cpu_percent']}%",
    #                     f"{process_info['memory_percent']}%",
    #                     f"{process_info['memory']} MB",
    #                 )
    #             text = '\n'.join(output_text.split('\n')[::-1])
    #             layout['monitor'].update(Panel(table, title='System Info'))
    #             layout['output'].update(Panel(text, title='Output'))
    #             live.update(layout)
    #             del table
                
    #             if process.poll() is not None:
    #                 break
    #     return
    # def consoleOutput(self, process):
    #     loop = asyncio.new_event_loop()
    #     asyncio.set_event_loop(loop)
    #     loop.run_until_complete(self.Output(process))
    # async def get_input(self, process, input_queue: Queue):
    #     while True:
    #         try:
    #             command_input = await ainput(f'({self.name}) >>> ')
    #         except (KeyboardInterrupt, EOFError):
    #             console.log("已退出输入")
    #             process.kill()
    #             break
    #         input_queue.put(command_input)
    #         if input_queue.get() is None:
    #             break
    #         try:
    #             process.stdin.write(command_input.encode('utf-8') + b'\n')
    #             process.stdin.flush()
    #         except OSError:
    #             os._exit(0)
    #     return
    # def consoleInput(self, process, input_queue: Queue):
    #     loop = asyncio.new_event_loop()
    #     asyncio.set_event_loop(loop)
    #     loop.run_until_complete(self.get_input(process, input_queue))

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

    # async def run(self):
    #     if 'startup_cmd' in self.data:
    #         subprocess.Popen(self.data['startup_cmd'], cwd=self.path)

    #     run_command = self.gen_run_command()

    #     if self.config.debug:
    #         console.log(f'[Debug]: Run Command: {run_command}')
        
    #     workdir = self.path if not self.config.direct_mode else None

    #     process = subprocess.Popen(
    #         run_command.split(" "),
    #         cwd=workdir,
    #         stdin=subprocess.PIPE,
    #         stdout=subprocess.PIPE,
    #         stderr=subprocess.STDOUT,
    #     )
    #     input_queue = Queue()
        
    #     #t1 = Thread(target=self.consoleOutput, args=(table, process, output_queue))
    #     t1 = Thread(target=self.consoleOutput, args=(process,))
    #     t2 = Thread(target=self.consoleInput, args=(process, input_queue))

    #     t1.start()
    #     t2.start()

    #     t1.join()
    #     console.print('[bold green]请输入任意内容以退出控制台')
    #     t2.join()
    #     return
