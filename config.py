#config
import os
import json

class Config:
    def __init__(self):
        self.config = {}
        self.config['first_run'] = True
        self.config['use_bmclapi'] = False
        self.config['workspace'] = 'workspace'
        self.config['config'] = 'config'
        self.config['config_file'] = 'config.json'
        self.config['workspace_file'] = 'workspace.json'
        self.config['config_path'] = os.path.join(self.config['config'], self.config['config_file'])
        self.config['workspace_path'] = os.path.join(self.config['workspace'], self.config['workspace_file'])
        self.initialize()

    def initialize(self):
        try:
            self.load_config()
        except FileNotFoundError:
            if not os.path.exists(self.config['config']):
                os.makedirs(self.config['config'])
            self.save_config()
    def save_config(self):
        with open(self.config['config_path'], 'w') as f:
            json.dump(self.config, f)
    def load_config(self):
        with open(self.config['config_path'], 'r') as f:
            self.config = json.load(f)
    def get_config(self):
        return self.config