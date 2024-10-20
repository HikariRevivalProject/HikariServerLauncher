import json
import logging
import os
from rich.console import Console
logger = logging.getLogger('hsl')
CONFIG_FILE = 'hsl-config.json'
console = Console()
class Config():
    def __init__(self):
        self.first_run: bool = True
        self.use_mirror: bool = False
        self.workspace_dir: str = 'workspace'
        self.workspace_file: str = 'workspace.json'
        self.backup_dir: str = 'backup'
        self.autorun: str = ''
        self.debug: bool = False
        self.language: str = 'zh'
    def load(self):
        try:
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                self.__dict__.update(data)
        except FileNotFoundError:
            pass
        except KeyError:
            os.remove(CONFIG_FILE)
            console.log('Invalid config file, removed and created a new one')
            self.save()
        except json.JSONDecodeError:
            console.log('Invalid config file')
        return self
    def save(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.__dict__, f, indent=4)
            #console.log(f'Config saved to {CONFIG_FILE} with data {self.__dict__}')