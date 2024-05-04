import os
import zipfile
import shutil
from config import Config
from workspace import Workspace
from utils.download import downloadFile

Config = Config()
Workspace = Workspace()
async def getJavaVersion(mcVersion):
    parts = mcVersion.split('.')
    version = int(parts[1])
    if version <= 6:
        return '6'
    elif version == 7:
        return '8'
    elif 7 < version <= 16:
        return '11'
    elif 16 < version < 20:
        return '17'
    elif version >= 20:
        return '21'
    else:
        return '0'
async def checkJavaExist(javaVersion):
    if not os.path.exists(os.path.join(Workspace.path,'java',javaVersion)):
        return False
    return True
async def getJava(javaVersion,source):
    sources = source['java']['list']
    url = ''
    path = os.path.join(Workspace.path,'java',javaVersion)
    filename = os.path.join(path,'java.zip')
    if not os.path.exists(path):
        os.makedirs(path)
    for i in sources:
        if os.name == 'nt':
            url = i['windows'][javaVersion]
        if os.name == 'posix':
            url = i['linux'][javaVersion]
        if downloadFile(url,filename):
            break
    with zipfile.ZipFile(filename,'r') as file:
        for member in file.namelist():
            is_directory = member.endswith('/')
            full_output_path = os.path.join(path, member[:-1] if is_directory else member)
            os.makedirs(full_output_path, exist_ok=True) if is_directory else None
            if not is_directory:
                file.extract(member, path)
    os.remove(filename)
    subdirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
    
    if len(subdirs) == 1:
        subdir_path = os.path.join(path, subdirs[0])
        for item in os.listdir(subdir_path):
            src = os.path.join(subdir_path, item)
            dst = os.path.join(path, item)
            if os.path.isfile(src):
                shutil.move(src, dst)
            elif os.path.isdir(src):
                shutil.move(src, dst)
        os.rmdir(subdir_path)
