import subprocess
from rich.console import Console
from threading import Thread
import sys
from queue import Queue
from hsl import HSL

console = Console()

class Server(HSL):
    """
    Server Class
    """
    def readLine(self, process, output_queue):
        for line in iter(process.stdout.readline, b''):
            output_queue.put(line.decode('utf-8').strip())
            if process.poll() is not None:
                output_queue.put(None)
                break
                
    def input(self, process, input_queue):
        while True:
            command_input = input(f'({self.name}) >>> ')
            input_queue.put(command_input)
            if input_queue.get() is None:
                break
            process.stdin.write(command_input.encode('utf-8') + b'\n')
            process.stdin.flush()

    def __init__(self, *, name: str, type: str, path: str, javaPath: str, maxRam: str):
        super().__init__()
        self.name = name
        self.type = type
        self.path = path
        self.javaPath = javaPath
        self.maxRam = maxRam

    def run(self):
        match self.type:
            case 'vanilla'|'paper'|'fabric':
                run_command = f'{self.javaPath} -Xmx{self.maxRam} -jar server.jar'
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

        t1 = Thread(target=self.readLine, args=(process, output_queue))
        t2 = Thread(target=self.input, args=(process, input_queue))

        t1.start()
        t2.start()

        while True:
            line = output_queue.get()
            if line is None:
                break
            console.print(line)

        t1.join()
        t2.join()

        process.terminate()
        process.wait()

