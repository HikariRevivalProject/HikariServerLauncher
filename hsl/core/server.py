import os
from typing import Dict, Callable
import regex
import signal
import psutil
import asyncio
import subprocess
from hsl.core.java import Java
from hsl.core.main import HSL
from hsl.utils.prompt import promptSelect
from queue import Queue
from threading import Thread
from aioconsole import ainput
from rich.console import Console
from rich.style import Style
START_SERVER = regex.compile(r'.*Starting minecraft server version.*')
START_PORT = regex.compile(r'.*Starting Minecraft server on.*')
PREPARE_LEVEL = regex.compile(r'.*Preparing level ".*"')
PREPARE_SPAWN = regex.compile(r'.*Preparing start region for dimension.*')
DONE_SERVER = regex.compile(r'.*Done \([^\)]+\)! For help, type "help"')
OFFLINE_SERVER = regex.compile(r'.*The server will make no attempt to authenticate usernames.*')
STOP_SERVER = regex.compile(r'.*Stopping server.*')
ASSIST_LOG_ANALYSIS_KEY = {
    START_SERVER: 'server-starting',
    START_PORT: 'server-bind-port',
    PREPARE_LEVEL: 'server-preparing-level',
    PREPARE_SPAWN: 'server-preparing-spawn',
    DONE_SERVER: 'server-start-done',
    OFFLINE_SERVER: 'server-offline-mode-enabled',
    STOP_SERVER:'server-stopping'
}
FLAG_OUTPUT_ENABLE = True
console = Console(style='dim')
output_counter = 0
class Server(HSL):
    """
    Server Class
    """
    def __init__(self, *, name: str, type: str, path: str, javaversion: str, maxRam: str, data=None):
        if data is None:
            data = {}
        super().__init__()
        self.name = name
        self.type = type
        self.path = path
        self.javaversion = javaversion
        self.maxRam = maxRam
        self.data = data
        self.constants_init()
    def constants_init(self):
        global HSL_FUNCTION_MENU, PROCESS_FUNCTIONS
        HSL_FUNCTION_MENU = self.locale.trans_key(['process-functions', 'cancel'])
        PROCESS_FUNCTIONS = self.locale.trans_key(['process-functions-kill','process-functions-sigstop','process-functions-sigcont', 'cancel'])
    def pathJoin(self, path: str) -> str:
        return os.path.join(os.getcwd(), self.path, path)
    async def analysis_output(self, output_text: str):
        global output_counter
        if output_counter == 0:
            console.print(self.locale.trans_key('hsl-assist-log-analyzer-text-prefix') + self.locale.trans_key('hsl-assist-log-analyzer-text-server-log-found'))
        output_counter += 1
        for key, value in ASSIST_LOG_ANALYSIS_KEY.items():
            if key.match(output_text) and FLAG_OUTPUT_ENABLE:
                console.print(self.locale.trans_key('hsl-assist-log-analyzer-text-prefix') + self.locale.trans_key(f'hsl-assist-log-analyzer-text-{value}'))
                return
    async def Output(self, process: subprocess.Popen):
        global FLAG_OUTPUT_ENABLE
        linetext = ''
        processed_lines = set()
        console.print('[bold magenta][HSL][yellow]开始启动服务器...')
        while True:
            for line in iter(process.stdout.readline, b''): # type: ignore
                try:
                    linetext = line.decode('utf-8').strip()
                except UnicodeDecodeError:
                    linetext = line.decode('gbk').strip()
                if not linetext:
                    continue
                if linetext not in processed_lines:
                    processed_lines.add(linetext)
                    if FLAG_OUTPUT_ENABLE:
                        console.print(linetext,markup=False,style=Style(bgcolor='#2c2c2c',color='white'))
                    await self.analysis_output(linetext)
            if process.poll() is not None:
                break
        return
    def consoleOutput(self, process: subprocess.Popen):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.Output(process))
    async def process_write_input(self, process: subprocess.Popen, input: str):
        process.stdin.write(input.encode('utf-8') + b'\n') # type: ignore
        process.stdin.flush() # type: ignore
    async def get_input(self, process: subprocess.Popen, input_queue: Queue):
        while True:
            try:
                command_input = await ainput(f'({self.name}) >>> ')
            except (KeyboardInterrupt, EOFError):
                console.log("已退出输入")
                process.kill()
                break
            except Exception as e:
                console.log(f'输入错误: {e}')
                continue
            if command_input.strip().lower() == 'hsl':
                global FLAG_OUTPUT_ENABLE
                FLAG_OUTPUT_ENABLE = False
                await self.hsl_function_menu(process)
                FLAG_OUTPUT_ENABLE = True
                continue
            input_queue.put(command_input)
            if input_queue.get() is None:
                break
            try:
                await self.process_write_input(process, command_input)
            except OSError:
                pass
        return
    async def hsl_function_menu(self, process: subprocess.Popen):
        _index = await promptSelect(HSL_FUNCTION_MENU, self.locale.trans_key('hsl-shell-functions-text'))
        hsl_functions:Dict[int,Callable] = {
            0: lambda: self.process_functions(process),
            len(HSL_FUNCTION_MENU) - 1: lambda: asyncio.sleep(0)
        }
        await hsl_functions[_index]()
    async def process_functions(self,process: subprocess.Popen):
        _index = await promptSelect(PROCESS_FUNCTIONS, self.locale.trans_key('process-functions'))
        process_functions:Dict[int,Callable] = {
            0: lambda: self.process_kill(process),
            1: lambda: self.process_sigstop(process),
            2: lambda: self.process_sigcont(process),
            len(PROCESS_FUNCTIONS) - 1: lambda: asyncio.sleep(0)
        }
        await process_functions[_index]()
    async def process_kill(self, process: subprocess.Popen):
        process.kill()
        console.print(self.locale.trans_key('process-functions-kill-success'))
    async def process_sigstop(self, process: subprocess.Popen):
        if os.name == 'nt':
            _process = psutil.Process(process.pid)
            _process.suspend()
        else:
            os.kill(process.pid, signal.SIGSTOP)
        console.print(self.locale.trans_key('process-functions-sigstop-success'))
    async def process_sigcont(self, process: subprocess.Popen):
        if os.name == 'nt':
            _process = psutil.Process(process.pid)
            _process.resume()
        else:
            os.kill(process.pid, signal.SIGCONT)
        console.print(self.locale.trans_key('process-functions-sigcont-success'))
    def consoleInput(self, process: subprocess.Popen, input_queue: Queue):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.get_input(process, input_queue))

    def check_process_exists(self, process):
        return psutil.pid_exists(process.pid)

    async def gen_run_command(self, path, export: bool = False) -> str:
        javaexecPath = await Java().getJavaByJavaVersion(self.javaversion, path)

        if export:
            run_dir = os.getcwd()
            javaexecPath = os.path.join(run_dir, javaexecPath)
            run_command = self._build_run_command(javaexecPath, export=True)
            return "\n".join([
                "cd " + os.path.join(os.getcwd(), self.path),
                run_command
            ])

        return self._build_run_command(javaexecPath)

    def _build_run_command(self, javaexecPath, export=False):
        jvm_setting = self.data.get('jvm_setting', '')
        console.print('[bold green]生成启动命令...')
        if self.type in ['vanilla', 'paper', 'fabric']:
            return " ".join([
                javaexecPath,
                "-Dfile.encoding=utf-8",
                "-Xmx" + self.maxRam,
                "-jar",
                self.pathJoin("server.jar") if export else "server.jar"
            ])

        mcVersion = self.data['mcVersion']
        forgeVersion = self.data['forgeVersion']
        mcMajorVersion = int(mcVersion.split('.')[1])

        if mcMajorVersion >= 17:
            args_path = (
                "@" + self.pathJoin(f"libraries/net/minecraftforge/forge/{mcVersion}-{forgeVersion}/unix_args.txt")
                if os.name == 'posix' 
                else "@" + self.pathJoin(f"libraries/net/minecraftforge/forge/{mcVersion}-{forgeVersion}/win_args.txt")
            )

            if jvm_setting:
                return " ".join([
                    javaexecPath + jvm_setting,
                    "-Dfile.encoding=utf-8",
                    "-Xmx" + self.maxRam,
                    "@user_jvm_args.txt",
                    args_path,
                    "%*"
                ])

            return " ".join([
                javaexecPath,
                "-Dfile.encoding=utf-8",
                "-Xmx" + self.maxRam,
                "@user_jvm_args.txt",
                args_path
            ])

        return " ".join([
            javaexecPath,
            "-Dfile.encoding=utf-8",
            "-Xmx" + self.maxRam,
            "-jar",
            self.pathJoin(f"forge-{mcVersion}-{forgeVersion}.jar")
            if export else f"forge-{mcVersion}-{forgeVersion}.jar"
        ])
    async def run(self, path: str):
        if not self.config.shell_introduction_read:
            console.print(self.locale.trans_key('hsl-shell-introduction'))
            await promptSelect(self.locale.trans_key(['yes']), self.locale.trans_key('hsl-shell-introduction-prompt-select'))
            self.config.shell_introduction_read = True
            self.config.save()
        startup_cmd = self.data.get('startup_cmd', '')
        if not startup_cmd:
            console.log('[bold red]启动命令为空')
        else:
            try:
                subprocess.Popen(startup_cmd, cwd=self.path)
            except Exception as e:
                console.log(f'[bold red]启动命令执行失败: {e}')
        startup_cmd = self.data.get('startup_cmd', '')
        if not startup_cmd:
            console.log('[bold red]启动前执行命令为空')
        else:
            os.system(startup_cmd)
            console.log(self.locale.trans_key('command-execute-before-server-ran'))
            await asyncio.sleep(1)

        run_command = await self.gen_run_command(path)

        if self.config.debug:
            console.log(f'[Debug]: Run Command: {run_command}')
        
        workdir = self.path

        process = subprocess.Popen(
            run_command.split(" "),
            cwd=workdir,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        input_queue = Queue()
        #t1 = Thread(target=self.consoleOutput, args=(table, process, output_queue))
        t1 = Thread(target=self.consoleOutput, args=(process,))
        t2 = Thread(target=self.consoleInput, args=(process, input_queue))

        
        t1.start()
        t2.start()
        
        try:
            t1.join()
            console.print('[bold green]键入Ctrl+C以退出控制台')
            t2.join()
            console.print('[bold green]控制台已退出')
        except KeyboardInterrupt:
            console.print('[bold red]已退出控制台')
            process.kill()
        return