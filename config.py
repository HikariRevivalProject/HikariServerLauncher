#config
import os
import json

class Config:
    def __init__(self):
        self.first_run = True
        self.use_mirror = False
        self.workspace_dir = 'workspace'
        self.config_dir = 'hsl-config'
        self.config_file = 'config.json'
        self.workspace_file = 'workspace.json'
        self.config_path = os.path.join(self.config_dir, self.config_file)
        self.workspace_path = os.path.join(self.workspace_dir, self.workspace_file)
        self.autorun = ''
        self.initialize()

    def initialize(self):
        try:
            self.load_config()
        except FileNotFoundError:
            #not found, create
            if not os.path.exists(self.config_path):
                os.makedirs(self.config_dir)
            self.save_config()
        except KeyError:
            #delete config
            os.remove(self.config_path)
            self.save_config()
    def save_config(self):
        with open(self.config_path, 'w') as f:
            json.dump({
                'first_run': self.first_run,
                'use_mirror': self.use_mirror,
                'autorun': self.autorun,
            }, f)
        self.load_config()
    def load_config(self):
        with open(self.config_path, 'r') as f:
            config = json.load(f)
            self.first_run = config['first_run']
            self.use_mirror = config['use_mirror']
            self.autorun = config['autorun']