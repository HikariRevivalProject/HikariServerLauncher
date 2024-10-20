import os
import shutil
import regex
import zipfile
import datetime
from hsl.core.config import Config
from hsl.core.server import Server
config = Config()
REGEX_BACKUP_FILE = r"^.*_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.zip$"
class Backup():
    async def backup_server(self, server: Server):
        backup_dir = config.backup_dir
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        backup_file = os.path.join(backup_dir, server.name + "_" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".zip")
        with zipfile.ZipFile(backup_file, "w",compresslevel=9,compression=zipfile.ZIP_DEFLATED) as zip_file:
            for root, dirs, files in os.walk(server.path):
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, start=config.workspace_dir)
                    zip_file.write(file_path, arcname=relative_path)
        return backup_file
    async def get_backup_list(self) -> list[str]:
        backup_dir = config.backup_dir
        backup_list = []
        if os.path.exists(backup_dir):
            backup_list.extend(
                file
                for file in os.listdir(backup_dir)
                if regex.match(REGEX_BACKUP_FILE, file)
            )
        return backup_list
    async def restore_backup(self, server: Server, backup_file: str):
        backup_dir = config.backup_dir
        #remove old server files
        try:
            shutil.rmtree(server.path)
        except FileNotFoundError:
            pass
        os.makedirs(server.path)
        #extract backup files
        with zipfile.ZipFile(os.path.join(backup_dir, backup_file), "r") as zip_file:
            zip_file.extractall(config.workspace_dir)
    async def delete_backup(self, backup_file: str):
        backup_dir = config.backup_dir
        os.remove(os.path.join(backup_dir, backup_file))