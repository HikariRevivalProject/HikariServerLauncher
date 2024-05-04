import subprocess
class Server:
    def __init__(self,name,path,run_command):
        self.name = name
        self.path = path
        self.run_command = run_command
    def run(self):
        run_command = self.run_command.split(" ")
        subprocess.Popen(run_command,cwd=self.path)