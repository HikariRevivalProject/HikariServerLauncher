import json
import logging
logger = logging.getLogger('hsl')
CONFIG_FILE = 'hsl-config.json'
class Config():
    def __init__(self):
        self.first_run: bool = True
        self.use_mirror: bool = False
        self.workspace_dir: str = 'workspace'
        self.workspace_file: str = 'workspace.json'
        self.autorun: str = ''
        self.debug: bool = False
    def load(self):
        try:
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                self.__dict__.update(data)
        except FileNotFoundError:
            pass
        except json.JSONDecodeError:
            logger.error('Invalid config file')
        return self
    def save(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.__dict__, f, indent=4)
            logger.info(f'Config saved to {CONFIG_FILE} with data {self.__dict__}')