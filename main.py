from prompt import promptSelect, promptInput, promptConfirm
from source import getSource
from config import Config
from workspace import Workspace
from server import Server
import asyncio
import utils
import os
OPTIONS_YN = ['是', '否']
OPTIONS_GAMETYPE = ['原版','Paper','Forge','Fabric']
OPTIONS_MENU = ['创建服务器', '管理服务器', '删除服务器','退出']
OPTIONS_MANAGE = ['启动服务器']
HSL_VERSION = 2
class Main:
    def __init__(self):
        global Config, Workspace
        self.Config = Config()
        self.Workspace = Workspace()
        self.source = getSource()
        try:
            isOutdated, new = utils.hsl.checkUpdate(HSL_VERSION)
            if isOutdated:
                print(f'发现新版本，版本号：{new}，建议及时更新')
        except:
            pass
    async def welcome(self):
        print('----- HSL -----')
        print('欢迎使用 Hikari Server Launcher.')
        print('这是一个Minecraft服务器的安装器/启动器.')
        print('----- 配置设置 -----')
        print('如果你的服务器环境在国内, 推荐使用BMCLAPI源以获得更好的速度。\n是否使用BMCLAPI源优先? (默认: 否)\n')
        option = await promptSelect(OPTIONS_YN,'是否使用BMCLAPI源优先?')
        if option == 0:
            self.Config.config['use_bmclapi'] = True
            print('设置已应用。')
        print('----- 配置完成 -----')
        self.Config.config['first_run'] = False
        self.Config.save_config()
        print('----- 服务器创建 -----')
        await self.create()

    async def create(self):
        serverName = await promptInput('请输入服务器名称:')
        for server in self.Workspace.workspaces:
            if server['name'] == serverName:
                print('服务器已存在。')
                return Server(serverName,server['path'],server['run_command'])
        self.Workspace.create(Server(serverName,os.path.join(self.Workspace.path,serverName),''))
        print('服务器已创建。')
        await self.install(Server(serverName,os.path.join(self.Workspace.path,serverName),''))
    async def install(self,Server:Server):
        gameType = await promptSelect(OPTIONS_GAMETYPE,'请选择服务器类型:')
        if gameType == 0:
            #vanilla
            #version selection
            mcVersions = await utils.vanilla.get_versions(self.source)
            mcVersions = [x['id'] for x in mcVersions if x['type'] == 'release']
            index = await promptSelect(mcVersions,'请选择Minecraft服务器版本:')
            mcVersion = mcVersions[index]
            #check(download) java
            javaPath = await utils.java.getJava(mcVersion,self.source)
            print('正在下载Vanilla 服务端: ' + mcVersion)
            #download vanilla server
            await utils.vanilla.downloadServer(self.source,mcVersion,os.path.join(Server.path,'server.jar'))
            print('Vanilla 服务端下载完成。')
            #find and save run command
            for i in range(len(self.Workspace.workspaces)):
                if self.Workspace.workspaces[i]['name'] == Server.name:
                    self.Workspace.workspaces[i]['run_command'] = f'{javaPath} -jar server.jar'
                    self.Workspace.save()
                    break
        else:
            raise NotImplementedError('哥们还没写到这块...')
        await self.mainMenu()
    async def manage(self):
        workspaces = self.Workspace.workspaces
        if not workspaces:
            await self.create()
        print('----- 服务器管理 -----')
        index = await promptSelect([x['name'] for x in workspaces],'选择服务器:')
        server = workspaces[index]['name']
        choice = await promptSelect(OPTIONS_MANAGE,f'{server} - 请选择操作:')
        if choice == 0:
            name = workspaces[index]['name']
            path = workspaces[index]['path']
            run_command = workspaces[index]['run_command']
            server = Server(name,path,run_command)
            server.run()
    async def delete(self):
        print('----- 服务器删除 -----')
        if not self.Workspace.workspaces:
            print('没有服务器。')
            await self.mainMenu()
        index = await promptSelect([x['name'] for x in self.Workspace.workspaces],'请选择要删除的服务器:')
        if await promptConfirm('确定要删除吗?'):
            self.Workspace.delete(index)
        await self.mainMenu()
    async def mainMenu(self):
        print('----- HSL -----')
        print('欢迎使用 Hikari Server Launcher.')
        choice = await promptSelect(OPTIONS_MENU,'菜单：')
        if choice == 0:
            await self.create()
            await self.mainMenu()
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
        await MainProgram.mainMenu()
if __name__ == '__main__':
    asyncio.run(main())