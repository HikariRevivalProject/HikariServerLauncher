import asyncio
import os
import re

from prompt import promptSelect, promptInput, promptConfirm
from utils import vanilla, paper, forge, fabric, osfunc
from hsl import HSL, Server, Workspace, Java
from config import Config

OPTIONS_YN = ['是', '否']
OPTIONS_GAMETYPE = ['原版','Paper(1.20.4)','Forge','Fabric']
OPTIONS_MENU = ['创建服务器', '管理服务器', '删除服务器','退出']
OPTIONS_MANAGE = ['启动服务器']

MAXRAM_PATTERN = re.compile(r'^\d+(\.\d+)?(M|G)$')
HSL_VERSION = 4
OS_MAXRAM = osfunc.getOSMaxRam()
class Main(HSL):
    def __init__(self):
        super().__init__()
        self.Config = Config()
        self.Workspace = Workspace()
        self.Java = Java()
        try:
            isOutdated, new = self.check_update(HSL_VERSION)
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
        serverName: str = await promptInput('请输入服务器名称:')
        while (not serverName.strip()) or serverName in ['con','aux','nul','prn']:
            serverName = await promptInput('名称非法，请重新输入:')
        servers = self.Workspace.workspaces
        for i in range(len(servers)):
            if servers[i]['name'] == serverName:
                print('服务器已存在。')
                return self.Workspace.get(index=i)
        print('服务器不存在，进入安装阶段。')
        serverPath = await self.Workspace.create(server_name=serverName)
        Server = await self.install(
            serverName=serverName,
            serverPath=serverPath
        )
        await self.Workspace.add(Server)
    async def install(self,*,serverName: str,serverPath: str):
        serverJarPath = os.path.join(serverPath,'server.jar')
        gameType = await promptSelect(OPTIONS_GAMETYPE,'请选择服务器类型:')
        if gameType == 0:
            #vanilla
            #version selection
            serverType = 'vanilla'
            mcVersions = await vanilla.get_versions(self.source)
            mcVersions = [x['id'] for x in mcVersions if x['type'] == 'release']
            index = await promptSelect(mcVersions,'请选择Minecraft服务器版本:')
            mcVersion = mcVersions[index]
            #check java
            javaVersion, javaPath = await self.Java.getJavaByGameVersion(mcVersion)
            print(f'正在下载Vanilla 服务端: {mcVersion}')
            #download vanilla server
            status = await vanilla.downloadServer(self.source,mcVersion,serverJarPath)
            if not status:
                print('Vanilla 服务端下载失败。')
                return
            print('Vanilla 服务端下载完成。')
            maxRam = await promptInput(f'你的主机最大内存为：{OS_MAXRAM}MB 请输入服务器最大内存(示例：1024M 或 1G):')
            #check regex
            while not MAXRAM_PATTERN.match(maxRam):
                maxRam = await promptInput('输入错误，请重新输入:')
            return Server(
                name=serverName,
                type=serverType,
                path=serverPath,
                javaVersion=javaVersion,
                maxRam=maxRam
            )

        elif gameType == 1:
            #papers
            #paper version 1.20.4
            serverType = 'paper'
            mcVersion = '1.20.4'
            javaVersion = await self.Java.getJavaVersion(mcVersion)
            status = await paper.downloadLatest(self.source,serverJarPath)
            if not status:
                print('Paper 服务端下载失败。')
                return
            print('Paper 服务端下载完成。')
            maxRam = await promptInput(f'你的主机最大内存为：{OS_MAXRAM}MB 请输入服务器最大内存(示例：1024M 或 1G):')
            #check regex
            while not MAXRAM_PATTERN.match(maxRam):
                maxRam = await promptInput('输入错误，请重新输入:')
            return Server(
                name = serverName,
                type = serverType,
                path=serverPath,
                javaVersion=javaVersion,
                maxRam = maxRam
            )
        else:
            raise NotImplementedError('哥们还没写到这块...')
        await self.mainMenu()
    async def manage(self):
        workspaces = self.Workspace.workspaces
        if not workspaces:
            await self.create()
        print('----- 服务器管理 -----')
        index = await promptSelect([x['name'] for x in workspaces],'选择服务器:')
        serverName = workspaces[index]['name']
        choice = await promptSelect(OPTIONS_MANAGE,f'{serverName} - 请选择操作:')
        if choice == 0:
            Server = await self.Workspace.get(index)
            await Server.run()
    async def delete(self):
        print('----- 服务器删除 -----')
        if not self.Workspace.workspaces:
            print('没有服务器。')
            await self.mainMenu()
        index = await promptSelect([x['name'] for x in self.Workspace.workspaces],'请选择要删除的服务器:')
        if await promptConfirm('确定要删除吗?'):
            await self.Workspace.delete(index)
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