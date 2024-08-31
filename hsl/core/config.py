#config
import os
import json

CONFIG_FILE = 'hsl-config.json'
class Config:
    first_run: bool = True
    use_mirror: bool = False
    workspace_dir: str = 'workspace'
    workspace_file: str = 'workspace.json'
    autorun: str = ''
    debug: bool = False
    direct_mode: bool = False
    
    @classmethod
    def load(cls):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                cls.first_run = config['first_run']
                cls.use_mirror = config['use_mirror']
                cls.workspace_dir = config['workspace_dir']
                cls.workspace_file = config['workspace_file']
                cls.autorun = config['autorun']
                cls.debug = config['debug']
                cls.direct_mode = config['direct_mode']
        except (FileNotFoundError, KeyError):
            cls.save()
    @classmethod
    def save(cls):
        with open(CONFIG_FILE, 'w') as f:
            json.dump({
                'first_run': cls.first_run,
                'use_mirror': cls.use_mirror,
                'autorun': cls.autorun,
                'debug': cls.debug,
                'direct_mode': cls.direct_mode
            }, f)
# class Config:
#     def __init__(self):
#         self.first_run: bool = True
#         self.use_mirror: bool = False
#         self.workspace_dir: str = 'workspace'
#         self.config_dir: str = 'hsl-config'
#         self.config_file: str = 'config.json'
#         self.workspace_file: str = 'workspace.json'
#         self.config_path: str = os.path.join(self.config_dir, self.config_file)
#         self.workspace_path: str = os.path.join(self.workspace_dir, self.workspace_file)
#         self.autorun: str = ''
#         self.debug: bool = False
#         self.direct_mode: bool = False
#         self.initialize()

#     def initialize(self):
#         try:
#             self.load_config()
#         except FileNotFoundError:
#             #not found, create
#             if not os.path.exists(self.config_path):
#                 os.makedirs(self.config_dir)
#             self.save_config()
#         except KeyError:
#             #delete config
#             os.remove(self.config_path)
#             self.save_config()
#     def save_config(self):
#         with open(self.config_path, 'w') as f:
#             json.dump({
#                 'first_run': self.first_run,
#                 'use_mirror': self.use_mirror,
#                 'autorun': self.autorun,
#                 'debug': self.debug,
#                 'direct_mode': self.direct_mode
#             }, f)
#         self.load_config()
#     def load_config(self):
#         with open(self.config_path, 'r') as f:
#             config = json.load(f)
#             self.first_run = config['first_run']
#             self.use_mirror = config['use_mirror']
#             self.autorun = config['autorun']
#             self.debug = config['debug']
#             self.direct_mode = config['direct_mode']