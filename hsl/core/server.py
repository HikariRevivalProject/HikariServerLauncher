import os
from xml.dom.pulldom import START_DOCUMENT
import regex
import psutil
import asyncio
import subprocess
from hsl.core.java import Java
from hsl.core.main import HSL
from queue import Queue
from threading import Thread
from aioconsole import ainput
from rich.console import Console
START_SERVER = regex.compile(r'.*Starting minecraft server version.*')
START_PORT = regex.compile(r'.*Starting Minecraft server on.*')
PREPARE_LEVEL = regex.compile(r'.*Preparing level ".*"')
PREPARE_SPAWN = regex.compile(r'.*Preparing start region for dimension.*')
DONE_SERVER = regex.compile(r'.*Done \([^\)]+\)! For help, type "help"')
OFFLINE_SERVER = regex.compile(r'.*The server will make no attempt to authenticate usernames.*')
console = Console()
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

    def pathJoin(self, path: str) -> str:
        return os.path.join(os.getcwd(), self.path, path)
    async def analysis_output(self, output_text: str):
        global output_counter
        if output_counter == 0:
            console.print('[bold magenta][HSL辅助日志分析][yellow]出现服务器日志输出...')
        output_counter += 1
        if regex.match(DONE_SERVER, output_text):
            console.print('[bold magenta][HSL辅助日志分析][yellow]服务器启动完成.')
        if regex.match(START_SERVER, output_text):
            console.print('[bold magenta][HSL辅助日志分析][yellow]服务器启动中...')
        if regex.match(START_PORT, output_text):
            console.print('[bold magenta][HSL辅助日志分析][yellow]服务器已启动, 正在监听端口.')
        if regex.match(PREPARE_LEVEL, output_text):
            console.print('[bold magenta][HSL辅助日志分析][yellow]正在准备地图...')
        if regex.match(PREPARE_SPAWN, output_text):
            console.print('[bold magenta][HSL辅助日志分析][yellow]正在准备出生点...')
        if regex.match(OFFLINE_SERVER, output_text):
            console.print('[bold magenta][HSL辅助日志分析][yellow]服务器未启用正版验证，请注意安全性.')
    async def Output(self, process):
        linetext = ''
        processed_lines = set()
        console.print('[bold magenta][HSL辅助日志分析][yellow]开始启动服务器...')
        while True:
            for line in iter(process.stdout.readline, b''):
                try:
                    linetext = line.decode('utf-8').strip()
                except UnicodeDecodeError:
                    linetext = line.decode('gbk').strip()
                if not linetext:
                    continue
                if linetext not in processed_lines:
                    processed_lines.add(linetext)
                    await self.analysis_output(linetext)
                    console.print(linetext)
            if process.poll() is not None:
                break
        return
    def consoleOutput(self, process):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.Output(process))
    async def get_input(self, process, input_queue: Queue):
        while True:
            try:
                command_input = await ainput(f'{self.name} >>> ')
            except (KeyboardInterrupt,asyncio.exceptions.CancelledError):
                console.log("已退出输入")
                process.kill()
                break
            except EOFError:
                console.log("已退出输入")
                process.kill()
                break
            except Exception as e:
                console.log(f'输入错误: {e}')
                continue
            input_queue.put(command_input)
            if input_queue.get() is None:
                break
            try:
                process.stdin.write(command_input.encode('utf-8') + b'\n')
                process.stdin.flush()
            except OSError:
                pass
        return
    def consoleInput(self, process, input_queue: Queue):
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
        startup_cmd = self.data.get('startup_cmd', '')
        if not startup_cmd:
            console.log('[bold red]启动命令为空')
        else:
            try:
                subprocess.Popen(startup_cmd, cwd=self.path)
            except Exception as e:
                console.log(f'[bold red]启动命令执行失败: {e}')
        # if 'startup_cmd' in self.data:
        #     if not self.data.get('startup_cmd', ''):
        #         console.log('[bold red]启动命令为空')
        #     else:
        #         subprocess.Popen(self.data['startup_cmd'], cwd=self.path)

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
        

        t1.join()
        console.print('[bold green]键入Ctrl+C以退出控制台')
        t2.join()
        console.print('[bold green]控制台已退出')
        return