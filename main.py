import asyncio
import os
import re
import javaproperties
from rich.console import Console

from prompt import promptSelect, promptInput, promptConfirm
from utils import vanilla, paper, forge, fabric, osfunc
from hsl import HSL, get_configs
from server import Server
from config import Config
from workspace import Workspace
from java import Java

OPTIONS_YN = ['是', '否']
OPTIONS_GAMETYPE = ['原版','Paper','Forge','Fabric','取消']
OPTIONS_MENU = ['创建服务器', '管理服务器', '删除服务器','退出']
OPTIONS_MANAGE = ['启动服务器','打开服务器目录','特定配置',"启动前执行命令","自定义JVM设置","取消"]

MAXRAM_PATTERN = re.compile(r'^\d+(\.\d+)?(M|G)$')
HSL_NAME = 'Hikari Server Launcher'
OS_MAXRAM = osfunc.getOSMaxRam()
WIDTH = 1280
HEIGHT = 720

console = Console()

class Main(HSL):
    def __init__(self):
        super().__init__()
        self.Config = Config()
        self.Workspace = Workspace()
        self.Java = Java()
        try:
            isOutdated, new = self.newVersionInfo
            if isOutdated:
                console.print(f'[bold magenta]发现新版本，版本号：[u]{new}[/u]，建议及时更新')
        except:
            pass
    
    async def welcome(self):
        console.rule('配置设置')
        console.print('如果你的服务器环境在国内, 推荐使用镜像源源以获得更好的速度。\n是否使用镜像源优先? (默认: 否)\n')
        option = await promptSelect(OPTIONS_YN, '是否使用镜像源优先?')
        if option == 0:
            self.Config.config['use_mirror'] = True
            console.print('设置已应用。')
        console.rule('配置完成')
        self.Config.config['first_run'] = False
        self.Config.save_config()
        console.rule('服务器创建')
        await self.create()
        await self.mainMenu()

    async def create(self):
        serverName = await promptInput('请输入服务器名称:')
        while not serverName.strip() or (serverName in ['con','aux','nul','prn'] and os.name == 'nt'):
            serverName = await promptInput('[bold magenta]名称非法，请重新输入:')
        
        servers = self.Workspace.workspaces
        if any(s['name'] == serverName for s in servers):
            console.print('[bold magenta]服务器已存在。')
            return
        
        console.print('服务器不存在，进入安装阶段。')
        serverPath = await self.Workspace.create(server_name=serverName)
        server_setting = await self.install(serverName=serverName, serverPath=serverPath)
        if not server_setting:
            console.print('[bold magenta]未安装服务器。')
            return
        
        serverName, serverType, serverPath, javaPath, data = server_setting
        maxRam = await promptInput(f'你的主机最大内存为：{OS_MAXRAM}MB 请输入服务器最大内存(示例：1024M 或 1G):')
        while not MAXRAM_PATTERN.match(maxRam):
            maxRam = await promptInput('输入错误，请重新输入:')
        
        server = Server(name=serverName, type=serverType, path=serverPath, javaPath=javaPath, maxRam=maxRam, data=data)
        await self.Workspace.add(server)
    
    async def install(self, *, serverName: str, serverPath: str):
        serverJarPath = os.path.join(serverPath, 'server.jar')
        data = {}
        gameType = await promptSelect(OPTIONS_GAMETYPE, '请选择服务器类型:')
        if gameType == 4:
            return False
        
        if gameType == 0:  # vanilla
            serverType = 'vanilla'
            mcVersions = [x['id'] for x in await vanilla.get_versions(self.source) if x['type'] == 'release']
            mcVersion = mcVersions[await promptSelect(mcVersions, '请选择Minecraft服务器版本:')]
            javaPath = await self.Java.getJavaByGameVersion(mcVersion, path=self.Config.config['workspace'])
            console.print(f'正在下载 Vanilla 服务端: {mcVersion}')
            if not await vanilla.downloadServer(self.source, mcVersion, serverJarPath, self.Config.config['use_mirror']):
                console.print('[bold magenta]Vanilla 服务端下载失败。')
                return False
            console.print('Vanilla 服务端下载完成。')
        
        elif gameType == 1:  # paper
            serverType = 'paper'
            mcVersion = await paper.getLatestVersionName(self.source)
            javaPath = await self.Java.getJavaByGameVersion(mcVersion, path=self.Config.config['workspace'])
            if not await paper.downloadLatest(self.source, serverJarPath):
                console.print('Paper 服务端下载失败。')
                return False
            console.print('Paper 服务端下载完成。')
        
        elif gameType == 2:  # forge
            #forge
            serverType = 'forge'
            mcVersions = await vanilla.get_versions(self.source)
            _mcVersions = await forge.get_mcversions(self.source,self.Config.config['use_mirror'])
            mcVersions = [x['id'] for x in mcVersions if x['type'] == 'release' and x['id'] in _mcVersions]
            index = await promptSelect(mcVersions,'请选择 Minecraft 版本:')
            mcVersion = mcVersions[index]
            javaPath = await self.Java.getJavaByGameVersion(mcVersion, path=self.Config.config['workspace'])
            forgeVersions: list = await forge.get_forgeversions(self.source,mcVersion,self.Config.config['use_mirror'])
            index: int = await promptSelect(forgeVersions,'请选择 Forge 版本:')
            forgeVersion: str = forgeVersions[index]
            print(forgeVersion)
            if '-' in forgeVersion:
                forgeVersion = forgeVersion.split('-')[1]
            data['mcVersion'] = mcVersion
            data['forgeVersion'] = forgeVersion
            installerPath = os.path.join(serverPath,'forge-installer.jar')
            status = await forge.download_installer(self.source,mcVersion,forgeVersion,installerPath,self.Config.config['use_mirror'])
            if not status:
                console.print('Forge 安装器下载失败。')
                return False
            console.print('Forge 安装器下载完成，尝试执行安装...')
            status = await forge.run_install(javaPath,serverPath)
            if not status:
                console.print('Forge 安装失败。')
                return False
            console.print('Forge 安装完成。')
        
        elif gameType == 3:  # fabric
            serverType = 'fabric'
            fabVersion = await fabric.getMcVersions(self.source)
            mcVersion = fabVersion[await promptSelect(fabVersion, '请选择 Fabric 服务器版本:')]
            javaPath = await self.Java.getJavaByGameVersion(mcVersion, path=self.Config.config['workspace'])
            loaderVersion = await fabric.getLoaderVersion(self.source)
            if not await fabric.downloadServer(self.source, os.path.join(serverPath, 'server.jar'), mcVersion, loaderVersion):
                console.print('Fabric 服务端下载失败。')
                return False
            console.print('Fabric 服务端下载完成。')
        
        return serverName, serverType, serverPath, javaPath, data
    
    async def manage(self):
        if not self.Workspace.workspaces:
            await self.create()
            return
        
        console.rule('服务器管理')
        index = await promptSelect([x['name'] for x in self.Workspace.workspaces], '选择服务器:')
        server = await self.Workspace.get(index)
        choice = await promptSelect(OPTIONS_MANAGE, f'{server.name} - 请选择操作:')
        if choice == 0:
            server.run()
        elif choice == 1:
            try:
                os.startfile(server.path)
            except:
                console.print('[bold magenta]无法打开服务器目录。')
        elif choice == 2:
            await self.editConfig(server)
        elif choice == 3:
            cmd = await promptInput('请输入命令，将在服务器启动前在服务器目录执行:')
            await self.Workspace.modifyData(index, 'startup_cmd', cmd)
            console.print('[bold green]命令设置成功。')
        elif choice == 4:
            console.print('[white bold]请输入JVM参数（包含横杠，例如-Xms1G，可多个），将在服务器启动时添加至启动参数内\n默认已设置-Dfile.encoding=utf-8以及-Xmx')
            jvm_setting = await promptInput('此为高级设置，若您不了解请勿随意填写:')
            await self.Workspace.modifyData(index, 'jvm_setting', jvm_setting)
            console.print('[bold green]JVM参数设置成功。')
        
        await self.mainMenu()

    async def editConfig(self, server: Server):
        console.print('[blue bold]读取特定配置索引:')
        configs = get_configs()
        if not configs:
            console.print('[bold magenta]特定配置索引读取失败，请检查网络连接。')
            return
        
        editableConfigs = []
        for config_info in configs:
            console.print(f'[bold green]尝试读取配置文件：{config_info["name"]}')
            config_path = os.path.join(server.path, config_info['path'])
            
            if not os.path.exists(config_path):
                console.print(f'[bold magenta]{config_info["name"]} - 配置文件不存在。')
                continue
            
            if config_info['type'] == 'properties':
                with open(config_path, 'r') as f:
                    config = javaproperties.load(f)
                
                console.print(f'[bold green]{config_info["name"]} - 读取成功。')
                
                if any(key_info['key'] in config for key_info in config_info['keys']):
                    editableConfigs.append((config_info, config))
        
        if not editableConfigs:
            console.print('[bold magenta]没有可编辑的配置文件。')
            return
        
        while True:
            selected_index = await promptSelect(
                [f"{x[0]['name']} - {x[0]['description']}" for x in editableConfigs] + ['返回'], 
                '请选择要修改的配置文件:'
            )
            if selected_index == len(editableConfigs):
                break

            editConfig, config = editableConfigs[selected_index]
            editableKeys = [(key_info['key'], f"{key_info['name']} - {key_info['description']}") for key_info in editConfig['keys']]
            
            while True:
                editKeyIndex = await promptSelect(
                    [x[1] for x in editableKeys] + ['返回'], 
                    '请选择要修改的配置项:'
                )
                if editKeyIndex == len(editableKeys):
                    break
                
                key, _ = editableKeys[editKeyIndex]
                key_info = editConfig['keys'][editKeyIndex]
                
                if key_info['type'] == "int":
                    editValue = await promptInput('请输入新值(整数):')
                elif key_info['type'] == "str":
                    editValue = await promptInput('请输入新值(字符串):')
                elif key_info['type'] == "bool":
                    editValue = 'true' if await promptConfirm('请选择新值:') else 'false'
                
                config[key] = editValue
                if editConfig['type'] == 'properties':
                    with open(os.path.join(server.path, editConfig['path']), 'w', encoding='utf-8') as f:
                        javaproperties.dump(config, f)

    
    async def delete(self):
        console.rule('服务器删除')
        if not self.Workspace.workspaces:
            console.print('没有服务器。')
            await self.mainMenu()
        
        index = await promptSelect([x['name'] for x in self.Workspace.workspaces], '请选择要删除的服务器:')
        if await promptConfirm('确定要删除吗?'):
            await self.Workspace.delete(index)
        
        await self.mainMenu()
    
    async def mainMenu(self):
        console.clear()
        console.rule(f'Hikari Server Launcher v{str(self.version/10)}')
        console.print('[bold gold]欢迎使用 Hikari Server Launcher.')
        choice = await promptSelect(OPTIONS_MENU, '菜单：')
        if choice == 0:
            await self.create()
        elif choice == 1:
            await self.manage()
        elif choice == 2:
            await self.delete()
        elif choice == 3:
            exit(0)
        else:
            raise NotImplementedError('你怎么会选择到这里呢？')

async def main():
    MainProgram = Main()
    if MainProgram.Config.config['first_run']:
        await MainProgram.welcome()
    else:
        #try:
        await MainProgram.mainMenu()
        #except Exception as e:
        #    console.print('出现未知异常', e)

if __name__ == '__main__':
    asyncio.run(main())
