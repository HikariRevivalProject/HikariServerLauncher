import os
import re
import sys
import yaml
import random
import asyncio
import noneprompt
try:
    import winreg as reg
except Exception:
    pass
import webbrowser
import javaproperties
from hsl.utils import osfunc
from hsl.core.server import Server
from hsl.core.java import Java
from hsl.core.checks import check_update, send_counter
from typing import Any, Callable, Optional
from rich.table import Table
from hsl.core.workspace import Workspace
from hsl.core.main import HSL
from hsl.core.backup import Backup
from hsl.core.sponsor import get_sponsor_list
from rich.console import Console
from hsl.gametypes import fabric, forge, paper, vanilla
from hsl.utils.prompt import promptSelect, promptInput, promptConfirm, promptSelectRed
console = Console()
HELP_URL = r'https://docs.qq.com/doc/DY3pnS1hFVm1uYWlp'
QQGROUP_URL = r'https://qm.qq.com/q/bUTqWXnwje'
OPTIONS_LANGUAGE = ["简体中文", "English"]
OPTIONS_LANGUAGE_CODE = ["zh", "en"]
OS_MAXRAM = osfunc.getOSMaxRam() #max ram in MB
HSL_NAME = 'Hikari Server Launcher'
MAXRAM_PATTERN = re.compile(r'^\d+(\.\d+)?(M|G)$') # like 4G or 4096M
try:
    AUTORUN_REG_HKEY = reg.HKEY_CURRENT_USER # type: ignore
    AUTORUN_REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
except NameError:
    pass
class HSL_MAIN(HSL):
    def constants_init(self) -> None:
        global OPTIONS_MENU, OPTIONS_MANAGE, OPTIONS_BACKUPS, OPTIONS_SETTINGS, OPTIONS_ADVANCED, OPTIONS_GAMETYPE, OPTIONS_JAVA, OPTIONS_JAVA_VERSION, OPTIONS_ABOUT, OPTIONS_JOKE
        OPTIONS_ADVANCED = self.locale.trans_key(['cancel'])
        OPTIONS_SETTINGS = self.locale.trans_key(
            ['set-language', 'debug', 'mirror-first', 'run-on-system-startup', 'cancel']
        )
        OPTIONS_GAMETYPE = self.locale.trans_key(
            ['vanilla', 'paper', 'forge', 'fabric', 'cancel']
        )
        OPTIONS_BACKUPS = self.locale.trans_key(
            ['backup-server', 'restore-server', 'delete-backup', 'cancel']
        )
        OPTIONS_MENU = self.locale.trans_key(
            ['create-server', 'manage-server', 'delete-server', 'backup-center', 'settings', 'advanced-options', 'about', 'exit']
        )
        OPTIONS_MANAGE = self.locale.trans_key(['start-server','open-server-folder','specific-configs','command-execute-before-server-start','custom-jvm-args','set-to-auto-run','export-start-script','edit-java-version','edit-max-ram','cancel'])
        OPTIONS_JAVA = self.locale.trans_key(
            ['java-6', 'java-8', 'java-11', 'java-17', 'java-21', 'cancel']
        )
        OPTIONS_JAVA_VERSION = ['6', '8', '11', '16', '17', '21']
        OPTIONS_ABOUT = self.locale.trans_key(['sponsor-list'])
    def __init__(self):
        super().__init__()
        self.Workspace = Workspace()
        self.Java = Java()
        self.Backup = Backup()
        self.constants_init()
    async def welcome(self) -> None:
        """
            Welcome
        """
        try:
            webbrowser.open(QQGROUP_URL, new=1)
            webbrowser.open(HELP_URL, new=1)
        except webbrowser.Error:
            console.print(self.locale.trans_key('cannot-open-web-browser', help = HELP_URL, qqgroup = QQGROUP_URL))
        await self.set_language()
        console.rule(self.locale.trans_key('customize-on-first-run'))
        console.print(self.locale.trans_key('set-mirror-priority-suggest-text'))
        self.config.use_mirror = await promptConfirm(self.locale.trans_key('set-mirror-priority-prompt-select'))
        self.config.first_run = False
        self.config.save()
        console.print(self.locale.trans_key('settings-applied'))
        console.rule(self.locale.trans_key('finished-customizing'))
        return
    async def exit(self) -> None:
        sys.exit(0)
    async def do_nothing(self) -> None:
        pass
    async def create(self) -> None:
        """
            Create server
        """
        serverName = await self.get_valid_server_name()
        if not serverName:
            console.print(self.locale.trans_key('server-exist'))
            return

        console.print(self.locale.trans_key('no-such-server'))
        serverPath = await self.Workspace.create(server_name=serverName)
        server_setting = await self.install(serverName=serverName, serverPath=serverPath)
        if not server_setting:
            console.print(self.locale.trans_key('install-server-failed'))
            return

        serverName, serverType, serverPath, javaversion, data = server_setting # type: ignore
        maxRam = await self.get_valid_max_ram()
        await self.Workspace.add(
            Server(name=serverName, type=serverType, path=serverPath, javaversion=javaversion, maxRam=maxRam, data=data)
        )
        console.print(self.locale.trans_key('server-install-success', serverName = serverName))

    async def get_valid_server_name(self) -> Optional[str]:
        """
            Get valid server name
            Return: str | None
        """
        serverName = await promptInput(self.locale.trans_key('server-name-input'))
        while (not serverName.strip()) or (serverName in ['con','aux','nul','prn'] and os.name == 'nt'):
            serverName = await promptInput(self.locale.trans_key('illegal-name-input'))

        servers = self.Workspace.workspaces
        return None if any(s['name'] == serverName for s in servers) else serverName
    
    async def get_valid_max_ram(self) -> str:
        maxRam = await promptInput(self.locale.trans_key('maximum-memory-prompt-input',OS_MAXRAM = str(OS_MAXRAM)))
        while not MAXRAM_PATTERN.match(maxRam):
            maxRam = await promptInput(self.locale.trans_key('maximum-memory-input-illegal'))
        return maxRam

    async def install(self, *, serverName: str, serverPath: str) -> tuple[str, str, str, str, dict] | bool:
        if self.config.use_mirror:
            console.print(self.locale.trans_key("mirror-first-enabled-prompt-text"))
        serverJarPath = os.path.join(serverPath, 'server.jar')
        
        gameType = await promptSelect(OPTIONS_GAMETYPE, self.locale.trans_key("server-type-prompt-select"))
        if gameType == 0:
            return await vanilla.install(self, serverName, serverPath, serverJarPath, {})
        elif gameType == 1:
            data = {
                'experimental': await promptConfirm(self.locale.trans_key('paper-experimental-prompt-select'))
            }
            return await paper.install(self, serverName, serverPath, serverJarPath, data)
        elif gameType == 2:
            return await forge.install(self, serverName, serverPath, serverJarPath, {})
        elif gameType == 3:
            return await fabric.install(self, serverName, serverPath, serverJarPath, {})
        else:
            return False
        # install_methods: dict[int, Callable] = {
        #     0: vanilla.install,
        #     1: paper.install,
        #     2: forge.install,
        #     3: fabric.install
        # }
        # if gameType == 4:
        #     return False
        # data = {}
        # return await install_methods[gameType](self, serverName, serverPath, serverJarPath, data)
    async def manage(self) -> None:
        if not self.Workspace.workspaces:
            console.print(self.locale.trans_key('no-server-available'))
            await asyncio.sleep(1)
            return
        
        console.rule(self.locale.trans_key('server-management'))
        index = await promptSelect([x['name'] for x in self.Workspace.workspaces], self.locale.trans_key('select-server'))
        server = await self.Workspace.get(index)
        _index = await promptSelect(OPTIONS_MANAGE, self.locale.trans_key('server-manage-prompt-select', servername = server.name))
        
        manage_methods: dict[int, Callable] = {
            0: lambda: server.run(self.Workspace.dir),
            1: lambda: self.open_server_directory(server),
            2: lambda: self.editConfig(server),
            3: lambda: self.set_startup_command(index),
            4: lambda: self.set_jvm_settings(index),
            5: lambda: self.set_autorun(server),
            6: lambda: self.export_start_script(server),
            7: lambda: self.change_java_version(index),
            8: lambda: self.change_max_ram(index),
            len(OPTIONS_MANAGE)-1: lambda: self.do_nothing()
        }
        await manage_methods[_index]()
        return
    async def change_max_ram(self, index: int) -> None:
        maxRam = await self.get_valid_max_ram()
        await self.Workspace.modify(index,'maxRam', maxRam)
        console.print(self.locale.trans_key('maximum-memory-setting-success'))
    async def change_java_version(self, index: int):
        console.print(self.locale.trans_key('prompt-select-java-automatically'))
        _index_java = await promptSelect(OPTIONS_JAVA, self.locale.trans_key('java-select'))
        if _index_java == len(OPTIONS_JAVA)-1:
            return
        await self.Workspace.modify(index, 'javaversion', OPTIONS_JAVA_VERSION[_index_java])
        console.print(self.locale.trans_key('java-select-success'))
        return
    async def open_server_directory(self, server: Server) -> None:
        try:
            os.startfile(server.path) # type: ignore
        except Exception:
            console.print(self.locale.trans_key('cannot-open-server-directory'))

    async def set_startup_command(self, index: int) -> None:
        cmd = await promptInput(self.locale.trans_key('command-execute-before-server-start-prompt-input'))
        await self.Workspace.modifyData(index, 'startup_cmd', cmd)
        console.print(self.locale.trans_key('startup-cmd-set'))

    async def set_jvm_settings(self, index: int) -> None:
        console.print(self.locale.trans_key('jvm-setting'))
        jvm_setting = await promptInput(self.locale.trans_key('jvm-setting-prompt'))
        await self.Workspace.modifyData(index, 'jvm_setting', jvm_setting)
        console.print(self.locale.trans_key('jvm-setting-success'))

    async def set_autorun(self, server: Server) -> None:
        if not await promptConfirm(self.locale.trans_key('set-to-auto-run-ask', servername = server.name)): return
        self.config.autorun = server.name
        self.config.save()
        console.print(self.locale.trans_key('set-to-auto-run-2'))

    async def export_start_script(self, server: Server) -> None:
        script_name = f'{server.name}.run.bat' if os.name == 'nt' else f'{server.name}.run.sh'
        with open(script_name, 'w') as f:
            f.write(await server.gen_run_command(self.Workspace.dir, export=True))
        console.print(self.locale.trans_key('exported-start-script', script_name = script_name))
        await asyncio.sleep(3)

    async def editConfig(self, server: Server) -> None:
        configs = self.spconfigs
        
        editableConfigs = await self.get_editable_configs(configs, server)
        if not editableConfigs:
            console.print(self.locale.trans_key('no-specific-config-available'))
            return
        await self.edit_selected_configs(editableConfigs, server)
        return
    async def get_editable_configs(self, configs, server: Server) -> list:
        editableConfigs = []
        for config_info in configs:
            config_path = os.path.join(server.path, *config_info['path'].split('/'))
            
            if not os.path.exists(config_path):
                continue
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = self.load_config_file(config_info, f)
            if any(self.get_nested_value(config, key_info['key'].split('.')) is not None for key_info in config_info['keys']):
                editableConfigs.append((config_info,config))
        return editableConfigs

    def load_config_file(self, config_info: dict, f) -> dict:
        if config_info['type'] == 'properties':
            return javaproperties.load(f)
        elif config_info['type'] == 'yml':
            return yaml.safe_load(f)
        return {}

    def get_nested_value(self, config: dict, keys: list) -> Any:
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
                [f"{x[0]['name']} - {x[0]['description']}" for x in editableConfigs] + self.locale.trans_key(['return']), 
                self.locale.trans_key('specific-config-file-edit-select')
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
                [x[1] for x in editableKeys] + self.locale.trans_key(['return']), 
                self.locale.trans_key('specific-config-edit-select')
            )
            if editKeyIndex == len(editableKeys):
                break
            
            key, _ = editableKeys[editKeyIndex]
            key_info: dict  = editConfig['keys'][editKeyIndex]
            value = self.get_nested_value(config, key.split('.'))
            if not value:
                return
            console.print(self.locale.trans_key('specific-config-current-value',name=key_info['name'], value = value))
            console.print(f'[bold white]Tips: {key_info["tips"]}')
            if key_info.get('danger', False):
                console.print(self.locale.trans_key('danger-config-warn'))
            editValue = await self.input_new_value(editConfig, key_info)
            self.set_nested_value(config, key.split('.'), editValue)
            self.save_config_file(editConfig, config, server.path)
        return

    async def input_new_value(self, editConfig, key_info) -> str | int | bool | None:
        if key_info['type'] == "int":
            key = await promptInput(self.locale.trans_key('enter-new-value-int'))
            return key if editConfig['type'] == 'properties' else int(key)
        elif key_info['type'] == "str":
            return await promptInput(self.locale.trans_key('enter-new-value-str'))

        elif key_info['type'] == "bool":
            if editConfig['type'] == 'properties':
                return 'true' if await promptConfirm(self.locale.trans_key('enter-new-value-bool')) else 'false'
            return await promptConfirm(self.locale.trans_key('enter-new-value-bool'))
        elif key_info['type'] == "choice":
            choice_index = await promptSelect(key_info['choices'], self.locale.trans_key('enter-new-value-select'))
            return key_info['choices'][choice_index]
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
        except Exception:
            return False
    async def delete(self) -> None:
        console.rule(self.locale.trans_key('delete-server'))
        if not self.Workspace.workspaces:
            console.print(self.locale.trans_key('no-such-server'))
            return
        
        index = await promptSelect([x['name'] for x in self.Workspace.workspaces], self.locale.trans_key('delete-server-prompt-select'))
        if await promptConfirm(self.locale.trans_key('delete-server-prompt-confirm')):
            await self.Workspace.delete(index)
        return

    async def setting(self):
        console.rule(self.locale.trans_key('settings'))
        index = await promptSelect(OPTIONS_SETTINGS, self.locale.trans_key('settings'))
        
        settings_methods = {
            0: lambda: self.set_language(),
            1: lambda: self.set_debug_mode(),
            2: lambda: self.set_mirror_priority(),
            3: lambda: self.set_run_on_startup(),
            len(OPTIONS_SETTINGS) - 1: lambda: self.do_nothing()
        }
        await settings_methods[index]()
        self.config.save()
    async def set_language(self):
        lang = await promptSelect(OPTIONS_LANGUAGE, self.locale.trans_key('select-language'))
        self.locale.set_language(OPTIONS_LANGUAGE_CODE[lang])
        self.constants_init()
        self.config.language = OPTIONS_LANGUAGE_CODE[lang]
        self.config.save()
        console.print(self.locale.trans_key('language-changed'))
    async def set_run_on_startup(self):
        if os.name == 'nt':
            #new feature: add to registry
            reg_key = reg.OpenKey(AUTORUN_REG_HKEY, AUTORUN_REG_PATH, 0, reg.KEY_SET_VALUE) # type: ignore
            query_reg_key = reg.OpenKey(AUTORUN_REG_HKEY, AUTORUN_REG_PATH, 0, reg.KEY_QUERY_VALUE) # type: ignore
            #check if HSL is already in the registry
            try:
                reg.QueryValueEx(query_reg_key, HSL_NAME) # type: ignore
                console.print(self.locale.trans_key('already-in-autorun-registry'))
                if await promptConfirm(self.locale.trans_key('autorun-registry-remove-prompt-confirm')):
                    reg.DeleteValue(reg_key, HSL_NAME) # type: ignore
                return
            except FileNotFoundError:
                pass
            if not await promptConfirm(
                self.locale.trans_key('autorun-registry-add-prompt-confirm')
            ):
                return
            exec_path = os.path.abspath(sys.argv[0])
            reg.SetValueEx(reg_key, HSL_NAME, 0, reg.REG_SZ, exec_path) # type: ignore
        else:
            console.print(self.locale.trans_key('autorun-not-supported-os'))
            return
    async def set_debug_mode(self):
        self.config.debug = await promptConfirm(self.locale.trans_key('debug-mode-prompt-select'))
    async def set_mirror_priority(self):
        self.config.use_mirror = await promptConfirm(self.locale.trans_key('set-mirror-priority-prompt-select'))
    async def advanced_options(self):
        index = await promptSelect(OPTIONS_ADVANCED, self.locale.trans_key('advanced-settings'))
        
        advanced_methods = {
            len(OPTIONS_ADVANCED) - 1: lambda: self.do_nothing()
        }
        await advanced_methods[index]()
    
    async def mainMenu(self):
        while True:
            title = self.locale.trans_key('title', version = str(self.version/10)) + (self.locale.trans_key('title-debug') if self.config.debug else '')
            console.rule(title)
            window_title = self.locale.trans_key('window-title', version = str(self.version/10)) + (self.locale.trans_key('window-title-debug') if self.config.debug else '')
            console.set_window_title(window_title)
            console.print(self.locale.trans_key('version', HSL_NAME = HSL_NAME, version = str(self.version/10), minor_version = str(self.minor_version)))
            
            try:
                _index = await promptSelect(OPTIONS_MENU, self.locale.trans_key('menu'))
            except (asyncio.CancelledError, KeyboardInterrupt):
                continue
            menu_methods: dict[int, Callable] = {
                0: lambda: self.create(),
                1: lambda: self.manage(),
                2: lambda: self.delete(),
                3: lambda: self.backups(),
                4: lambda: self.setting(),
                5: lambda: self.advanced_options(),
                6: lambda: self.about(),
                7: lambda: self.exit()
            }
            await menu_methods[_index]()
    async def about(self):
        console.rule(self.locale.trans_key('about'))
        console.print(self.locale.trans_key('about-text'))
        _index = await promptSelect(OPTIONS_ABOUT, self.locale.trans_key('about'))
        about_methods: dict[int, Callable] = {
            0: lambda:self.get_sponsor_list()
        }
        return await about_methods[_index]()
    async def get_sponsor_list(self):
        table = Table(title=self.locale.trans_key('sponsor'),show_header=False)
        sponsor_list = get_sponsor_list()
        for sponsor in sponsor_list:
            table.add_row(f'[bold green]{sponsor}[/bold green]')
        table.add_section()
        table.add_row(self.locale.trans_key('sponsor-thanks'))
        console.print(table)
        
    async def autorun(self):
        server = await self.Workspace.getFromName(self.config.autorun)
        console.print(self.locale.trans_key('server-auto-run-prompt',servername=server.name))
        await asyncio.sleep(3)
        await server.run(self.Workspace.dir)
        exit()
    async def backups(self):
        console.rule(self.locale.trans_key('backup-management'))
        backup_methods: dict[int, Callable] = {
            0: lambda: self.create_backup(),
            1: lambda: self.restore_backup(),
            2: lambda: self.delete_backup(),
            len(OPTIONS_BACKUPS) - 1: lambda: self.do_nothing()
        }
        index = await promptSelect(OPTIONS_BACKUPS, self.locale.trans_key('backup-management'))
        await backup_methods[index]()
    async def create_backup(self):
        servers = await self.Workspace.getAll()
        if not servers:
            console.print(self.locale.trans_key('no-server-available'))
            return
        server_index = await promptSelect([x.name for x in servers], self.locale.trans_key('backup-server-prompt-select'))
        server = servers[server_index]
        with console.status(self.locale.trans_key('backup-creating', servername=server.name)):
            backup_file = await self.Backup.backup_server(server)
        console.print(self.locale.trans_key('backup-create-success', servername=server.name, backupname=backup_file))
        return True
    async def restore_backup(self):
        servers = await self.Workspace.getAll()
        server_index = await promptSelect([x.name for x in servers], self.locale.trans_key('backup-restore-server-prompt-select'))
        server = servers[server_index]

        backups = await self.Backup.get_backup_list()
        if not backups:
            console.print(self.locale.trans_key('no-backup-available'))
            return
        backup_index = await promptSelect(list(backups), self.locale.trans_key('backup-restore-select'))
        backup_file = backups[backup_index]
        with console.status(self.locale.trans_key('backup-restoring',backupname = backup_file)):
            await self.Backup.restore_backup(server, backup_file)
        console.print(self.locale.trans_key('backup-restore-success', servername=server.name, backupname=backup_file))
        return True
    async def delete_backup(self):
        backups = await self.Backup.get_backup_list()
        if not backups:
            console.print(self.locale.trans_key('no-backup-available'))
            return
        backup_index = await promptSelect(list(backups), self.locale.trans_key('delete-backup-prompt-select'))
        backup_file = backups[backup_index]
        if await promptConfirm(self.locale.trans_key('delete-backup-prompt-confirm', backupname=backup_file)):
            await self.Backup.delete_backup(backup_file)
        return True

mainProgram = HSL_MAIN()
async def main():
    task = asyncio.create_task(check_update())
    counter_task = asyncio.create_task(send_counter())
    # isOutdated, new = mainProgram.flag_outdated, mainProgram.latest_version
    if mainProgram.config.first_run:
        await mainProgram.welcome()
    if mainProgram.config.autorun:
        try:
            loop = asyncio.get_event_loop()
            task = loop.create_task(mainProgram.autorun())
            await asyncio.wait_for(task, None)

        except (KeyboardInterrupt, asyncio.CancelledError):
            mainProgram.config.autorun = ''
            mainProgram.config.save()
            console.print(mainProgram.locale.trans_key('autorun-canceled'))
    await mainProgram.mainMenu()
    await task
    await counter_task
    

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except SystemExit:
        pass
    except noneprompt.CancelledError:
        console.print(mainProgram.locale.trans_key('user-cancel-operate'))
    except Exception as e:
        console.print(mainProgram.locale.trans_key('unknown-error-occur', e = str(e)))
        if mainProgram.config.debug:
            console.print_exception()