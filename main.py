import os
import re
import sys
import yaml
import json
import asyncio
import noneprompt
import javaproperties
from hsl.core.java import Java
from hsl.utils import osfunc
from hsl.core.server import Server
from typing import Callable
from hsl.core.workspace import Workspace
from hsl.core.main import HSL
from rich.console import Console
from hsl.gametypes import fabric, forge, paper, vanilla
from hsl.utils.prompt import promptSelect, promptInput, promptConfirm

OPTIONS_YN = ['是', '否']
OPTIONS_ADVANCED = ['GUI测试', '取消']
OPTIONS_SETTINGS = ['调试模式', '镜像源优先', '取消']
OPTIONS_GAMETYPE = ['原版','Paper','Forge','Fabric','取消']
OPTIONS_MENU = ['创建服务器', '管理服务器', '删除服务器', '设置', '高级选项', '退出']
OPTIONS_MANAGE = ['启动服务器','打开服务器目录','特定配置',"启动前执行命令",'自定义JVM设置','设定为自动启动', '导出启动脚本' ,'取消']

OS_MAXRAM = osfunc.getOSMaxRam() #max ram in MB
HSL_NAME = 'Hikari Server Launcher'
MAXRAM_PATTERN = re.compile(r'^\d+(\.\d+)?(M|G)$') # like 4G or 4096M

console = Console()

class Main(HSL):
    def __init__(self):
        super().__init__()
        self.Workspace = Workspace()
        self.Java = Java()
        
    async def welcome(self) -> None:
        """
            Welcome
        """
        console.rule('配置设置')
        console.print('如果你的服务器环境在国内, 推荐使用镜像源源以获得更好的速度。\n是否使用镜像源优先? (默认: 否)\n')
        self.config.use_mirror = await promptConfirm('是否使用镜像源优先?')
        self.config.first_run = False
        self.config.save()
        console.print('设置已应用。')
        console.rule('配置完成')
        return
    
    async def exit(self) -> None:
        #exit the program
        sys.exit(0)

    async def create(self) -> None:
        """
            Create server
        """
        serverName = await self.get_valid_server_name()
        if not serverName:
            console.print('[bold magenta]服务器已存在。')
            return
        
        console.print('服务器不存在，进入安装阶段。')
        serverPath = await self.Workspace.create(server_name=serverName)
        server_setting = await self.install(serverName=serverName, serverPath=serverPath)
        if not server_setting:
            console.print('[bold magenta]未安装服务器。')
            return
        
        serverName, serverType, serverPath, javaPath, data = server_setting # type: ignore
        maxRam = await self.get_valid_max_ram()
        if maxRam is None:
            maxRam = str(OS_MAXRAM) + 'M'
        server = Server(name=serverName, type=serverType, path=serverPath, javaPath=javaPath, maxRam=maxRam, data=data)
        await self.Workspace.add(server)

    async def get_valid_server_name(self) -> str | None:
        """
            Get valid server name
            Return: str | None
        """
        serverName = await promptInput('请输入服务器名称:')
        while (not serverName.strip()) or (serverName in ['con','aux','nul','prn'] and os.name == 'nt'):
            serverName = await promptInput('名称非法，请重新输入:')
        
        servers = self.Workspace.workspaces
        if any(s['name'] == serverName for s in servers):
            return None
        return serverName
    
    async def get_valid_max_ram(self) -> str | None:
        """
            Get valid max ram
            Return: str | None
        """
        maxRam = await promptInput(f'你的主机最大内存为：{OS_MAXRAM}MB 请输入服务器最大内存(示例：1024M 或 1G):')
        while not MAXRAM_PATTERN.match(maxRam):
            maxRam = await promptInput('输入错误，请重新输入:')
        return maxRam

    async def install(self, *, serverName: str, serverPath: str) -> tuple | bool:
        """
            Install the server
            Args: 
                serverName: str
                serverPath: str
        
            Returns: 
                serverName, 
                serverPath, 
                serverJarPath, 
                data
        """

        serverJarPath = os.path.join(serverPath, 'server.jar')
        
        gameType = await promptSelect(OPTIONS_GAMETYPE, '请选择服务器类型:')

        install_methods: dict[int, Callable] = {
            0: vanilla.install,
            1: paper.install,
            2: forge.install,
            3: fabric.install
        }
        if gameType == 4:
            return False
        data = {}
        return await install_methods[gameType](self, serverName, serverPath, serverJarPath, data)

    async def manage(self) -> None:
        if not self.Workspace.workspaces:
            console.print('[bold magenta]没有可用的服务器。')
            await asyncio.sleep(1)
            return
        
        console.rule('服务器管理')
        index = await promptSelect([x['name'] for x in self.Workspace.workspaces], '选择服务器:')
        server = await self.Workspace.get(index)
        index = await promptSelect(OPTIONS_MANAGE, f'{server.name} - 请选择操作:')
        
        manage_methods: dict[int, Callable] = {
            0: server.run,
            1: lambda: self.open_server_directory(server),
            2: lambda: self.editConfig(server),
            3: lambda: self.set_startup_command(index),
            4: lambda: self.set_jvm_settings(index),
            5: lambda: self.set_autorun(server),
            6: lambda: self.export_start_script(server)
        }
        await manage_methods[index]()
        return

    async def open_server_directory(self, server: Server) -> None:
        try:
            os.startfile(server.path)
        except:
            console.print('[bold magenta]无法打开服务器目录。')

    async def set_startup_command(self, index: int) -> None:
        cmd = await promptInput('请输入命令，将在服务器启动前在服务器目录执行:')
        await self.Workspace.modifyData(index, 'startup_cmd', cmd)
        console.print('[bold green]命令设置成功。')

    async def set_jvm_settings(self, index: int) -> None:
        console.print('[white bold]请输入JVM参数（包含横杠，例如-Xms1G，可多个），将在服务器启动时添加至启动参数内\n默认已设置-Dfile.encoding=utf-8以及-Xmx')
        jvm_setting = await promptInput('此为高级设置，若您不了解请勿随意填写:')
        await self.Workspace.modifyData(index, 'jvm_setting', jvm_setting)
        console.print('[bold green]JVM参数设置成功。')

    async def set_autorun(self, server: Server) -> None:
        if not await promptConfirm(f'!!! 确定要将 {server.name} 设为自动启动吗？'): return
        self.config.autorun = server.name
        self.config.save()
        console.print('[bold green]自动启动设置成功，将在下次运行此软件时自动打开该服务器。')

    async def export_start_script(self, server: Server) -> None:
        script_name = f'{server.name}.run.bat' if os.name == 'nt' else f'{server.name}.run.sh'
        with open(script_name, 'w') as f:
            f.write(server.gen_run_command(export=True))
        console.print(f'[green]生成启动脚本成功({script_name})')
        await asyncio.sleep(2)

    async def editConfig(self, server: Server) -> None:
        console.print('[blue bold]读取特定配置索引:')
        configs = self.spconfigs
        if not configs:
            console.print('[bold magenta]特定配置索引读取失败，请检查网络连接。')
            return
        
        editableConfigs = await self.get_editable_configs(configs, server)
        if not editableConfigs:
            console.print('[bold magenta]没有可编辑的配置文件。')
            return
        
        await self.edit_selected_configs(editableConfigs, server)
        return
    async def get_editable_configs(self, configs, server: Server) -> list:
        editableConfigs = []
        for config_info in configs:
            console.print(f'[bold green]尝试读取配置文件：{config_info["name"]}')
            config_path = os.path.join(server.path, *config_info['path'].split('/'))
            
            if not os.path.exists(config_path):
                console.print(f'[bold magenta]{config_info["name"]} - 配置文件不存在。')
                continue
            
            with open(config_path, 'r') as f:
                config = self.load_config_file(config_info, f)
            console.print(f'[bold green]{config_info["name"]} - 读取成功。')
            if any(self.get_nested_value(config, key_info['key'].split('.')) is not None for key_info in config_info['keys']):
                editableConfigs.append((config_info,config))
        return editableConfigs

    def load_config_file(self, config_info: dict, f) -> dict:
        if config_info['type'] == 'properties':
            return javaproperties.load(f)
        elif config_info['type'] == 'yml':
            return yaml.safe_load(f)
        return {}

    def get_nested_value(self, config: dict, keys: list) -> dict | None:
        for key in keys:
            config = config.get(key, None)
            if config is None:
                return None
        return config

    def set_nested_value(self, config, keys, value):
        for key in keys[:-1]:
            config = config.setdefault(key, {})
        config[keys[-1]] = value

    async def edit_selected_configs(self, editableConfigs, server) -> None:
        while True:
            selected_index = await promptSelect(
                [f"{x[0]['name']} - {x[0]['description']}" for x in editableConfigs] + ['返回'], 
                '请选择要修改的配置文件:'
            )
            if selected_index == len(editableConfigs):
                break

            editConfig, config = editableConfigs[selected_index]
            await self.edit_config_items(editConfig, config, server)
        return

    async def edit_config_items(self, editConfig, config, server) -> None:
        editableKeys = [(key_info['key'], f"{key_info['name']} - {key_info['description']}") for key_info in editConfig['keys']]
        while True:
            editKeyIndex = await promptSelect(
                [x[1] for x in editableKeys] + ['返回'], 
                '请选择要修改的配置项:'
            )
            if editKeyIndex == len(editableKeys):
                break
            
            key, _ = editableKeys[editKeyIndex]
            key_info: dict  = editConfig['keys'][editKeyIndex]
            console.print(f'[bold white]Tips: {key_info["tips"]}')
            if key_info.get('danger', False):
                console.print(f'[bold red]这是一个危险配置！修改前请三思！')
            editValue = await self.input_new_value(editConfig, key_info)
            self.set_nested_value(config, key.split('.'), editValue)
            self.save_config_file(editConfig, config, server.path)
        return

    async def input_new_value(self, editConfig, key_info) -> str | int | bool | None:
        if key_info['type'] == "int":
            key = await promptInput('请输入新值(整数):')
            if editConfig['type'] == 'properties':
                return key
            return int(key)

        elif key_info['type'] == "str":
            return await promptInput('请输入新值(字符串):')

        elif key_info['type'] == "bool":
            if editConfig['type'] == 'properties':
                return 'true' if await promptConfirm('请选择新值:') else 'false'
            return await promptConfirm('请选择新值:')
        return None

    def save_config_file(self, editConfig, config, server_path) -> bool:
        config_path = os.path.join(server_path, *editConfig['path'].split('/'))
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                if editConfig['type'] == 'properties':
                    javaproperties.dump(config, f)
                    return True
                elif editConfig['type'] == 'yml':
                    yaml.dump(config, f)
                    return True
                else:
                    return False
        except:
            return False
    async def delete(self) -> None:
        console.rule('服务器删除')
        if not self.Workspace.workspaces:
            console.print('没有服务器。')
            return
        
        index = await promptSelect([x['name'] for x in self.Workspace.workspaces], '请选择要删除的服务器:')
        if await promptConfirm('确定要删除吗?'):
            await self.Workspace.delete(index)
        return

    async def setting(self):
        console.rule('设置')
        index = await promptSelect(OPTIONS_SETTINGS, '设置：')
        
        settings_methods = {
            0: lambda: self.set_debug_mode(),
            1: lambda: self.set_mirror_priority(),
            len(OPTIONS_SETTINGS) - 1: lambda: None
        }
        await settings_methods.get(index, lambda: None)()
        self.config.save()

    async def set_debug_mode(self):
        self.config.debug = await promptConfirm('开启调试模式？')
    async def set_mirror_priority(self):
        self.config.use_mirror = await promptConfirm('是否使用镜像源优先？')
    async def advanced_options(self):
        index = await promptSelect(OPTIONS_ADVANCED, '高级选项：')
        
        advanced_methods = {
            0: lambda: (),
            1: lambda: self.exit()
        }
        await advanced_methods[index]()
    
    async def mainMenu(self):
        console.clear()
        console.rule(f'{HSL_NAME} v{str(self.version/10)}')
        console.set_window_title(f'{HSL_NAME} v{str(self.version/10)}')
        console.print(f'[bold blue]信息：当前工作目录：[u]{self.Workspace.path}[/u], 最大内存：[u]{OS_MAXRAM}[/u]MB, 调试模式：[u]{self.config.debug}[/u], 镜像源优先：[u]{self.config.use_mirror}[/u], 自动启动：[u]{self.config.autorun}[/u]')
        while True:
            console.print(f'[bold gold]欢迎使用 {HSL_NAME}.')
            index = await promptSelect(OPTIONS_MENU, '菜单：')
            
            menu_methods: dict[int, Callable] = {
                0: lambda: self.create(),
                1: lambda: self.manage(),
                2: lambda: self.delete(),
                3: lambda: self.setting(),
                4: lambda: self.advanced_options(),
                5: lambda: self.exit()
            }
            await menu_methods[index]()

    async def autorun(self):
        server = await self.Workspace.getFromName(self.config.autorun)
        console.print(f'[bold blue]将于三秒后启动 {server.name}。键入Ctrl+C(^C)可取消.')
        await asyncio.sleep(3)
        await server.run()
        exit()

mainProgram = Main()
async def main():
    isOutdated, new = mainProgram.flag_outdated, mainProgram.latest_version
    if isOutdated:
        console.print(f'[bold magenta]发现新版本，版本号：[u]{new/10}[/u]，建议及时更新')
        await asyncio.sleep(3)
    if mainProgram.config.first_run:
        await mainProgram.welcome()
        await mainProgram.mainMenu()
    else:
        if mainProgram.config.autorun:
            try:
                loop = asyncio.get_event_loop()
                task = loop.create_task(mainProgram.autorun())
                await asyncio.wait_for(task, None)
            except (KeyboardInterrupt, asyncio.CancelledError):
                mainProgram.config.autorun = ''
                mainProgram.config.save()
                console.print('自动启动已取消并重置，如需再次启用请重新设置。')
                await asyncio.sleep(1)
        await mainProgram.mainMenu()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except SystemExit:
        pass
    except noneprompt.CancelledError:
        console.print('[bold green]用户取消操作，已退出。')
    except Exception as e:
        if mainProgram.config.debug:
            console.print_exception()
        else:
            console.print(f'[bold red]发生未知错误: {e}')
            console.print_exception()