import asyncio
import os
import re
import webbrowser
import math
import random
from rich.console import Console

#import tkintertools as tkt
#import tkintertools.animation as animation
#import tkintertools.color as color
#import tkintertools.constants as constants
#import tkintertools.standard.dialogs as dialogs  # Customied
#import tkintertools.standard.features as features  # Customied
#import tkintertools.standard.shapes as shapes  # Customied
#import tkintertools.standard.texts as texts  # Customied
#import tkintertools.style as style
#import tkintertools.three as three


from prompt import promptSelect, promptInput, promptConfirm
from utils import vanilla, paper, forge, fabric, osfunc
from hsl import HSL
from server import Server
from config import Config
from workspace import Workspace
from java import Java

OPTIONS_YN = ['是', '否']
OPTIONS_GAMETYPE = ['原版','Paper','Forge','Fabric','取消']
OPTIONS_MENU = ['创建服务器', '管理服务器', '删除服务器','退出']
OPTIONS_MANAGE = ['启动服务器','打开服务器目录',]

MAXRAM_PATTERN = re.compile(r'^\d+(\.\d+)?(M|G)$')
HSL_NAME = f'Hikari Server Launcher'
OS_MAXRAM = osfunc.getOSMaxRam()
WIDTH = 1280
HEIGHT = 720

console = Console()
#style.use_theme('system')
#constants.SYSTEM = "Windows10"
'''
root = tkt.Tk((WIDTH,HEIGHT), title=HSL_NAME)
#root.iconbitmap('HSL.ico')
root.center()
canvas = tkt.Canvas(
    root, zoom_item=True, keep_ratio="full",free_anchor=True, 
    highlightthickness=1, highlightbackground="grey"
)
canvas.place(width=1280, height=720, x=640, y=360, anchor="center")
canvas.create_line(1000, 0, 1000, 800, fill="grey")
_l = tkt.Label(canvas, (0, 0), (1280, 60), name="")
_l.shapes[0].styles = {"normal": {"fill": "#C286FF", "outline": "#C286FF"}}
_l.update()
_textName = canvas.create_text(200,30,text=HSL_NAME,font=('Arial',30))
_textRelease = canvas.create_text(500,30,text='Pre-release',font=('Arial',30))
canvas.itemconfigure(_textName,fill='#FFFFFF')
canvas.itemconfigure(_textRelease,fill='#FFFFFF')

tkt.UnderlineButton(canvas, (1200, 640), text="加入QQ群", through=True, command=lambda: webbrowser.open_new_tab("https://qm.qq.com/q/S1HInZBv22"))
tkt.UnderlineButton(canvas, (1200, 680), text="项目主页", through=True, command=lambda: webbrowser.open_new_tab("https://github.com/Hikari16665/HikariServerLauncher"))

root.mainloop()
'''
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
        option = await promptSelect(OPTIONS_YN,'是否使用镜像源优先?')
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
        global Server
        serverName: str = await promptInput('请输入服务器名称:')
        while (not serverName.strip()) or (serverName in ['con','aux','nul','prn'] and os.name == 'nt'):
            serverName = await promptInput('[bold magenta]名称非法，请重新输入:')
        servers = self.Workspace.workspaces
        if any(servers[i]['name'] == serverName for i in range(len(servers))):
            console.print('[bold magenta]服务器已存在。')
            return
        console.print('服务器不存在，进入安装阶段。')
        serverPath = await self.Workspace.create(server_name=serverName)
        server_setting = await self.install(
            serverName=serverName,
            serverPath=serverPath
        )
        if server_setting == False:
            console.print('[bold magenta]未安装服务器。')
            return
        serverName, serverType, serverPath, javaPath = server_setting
        maxRam = await promptInput(f'你的主机最大内存为：{OS_MAXRAM}MB 请输入服务器最大内存(示例：1024M 或 1G):')
        #check regex
        while not MAXRAM_PATTERN.match(maxRam):
            maxRam = await promptInput('输入错误，请重新输入:')
        server = None
        server = Server(
            name=serverName,
            type=serverType,
            path=serverPath,
            javaPath=javaPath,
            maxRam=maxRam
        )
        await self.Workspace.add(server)
    async def install(self,*,serverName: str,serverPath: str):
        serverJarPath = os.path.join(serverPath,'server.jar')
        gameType = await promptSelect(OPTIONS_GAMETYPE,'请选择服务器类型:')
        match gameType:
            case 0:
                #vanilla
                serverType = 'vanilla'
                mcVersions = await vanilla.get_versions(self.source)
                mcVersions = [x['id'] for x in mcVersions if x['type'] == 'release']
                index = await promptSelect(mcVersions,'请选择Minecraft服务器版本:')
                mcVersion = mcVersions[index]
                #check java
                javaPath = await self.Java.getJavaByGameVersion(mcVersion, path=self.Config.config['workspace'])
                console.print(f'正在下载 Vanilla 服务端: {mcVersion}')
                #download vanilla server
                status = await vanilla.downloadServer(self.source,mcVersion,serverJarPath,self.Config.config['use_mirror'])
                if not status:
                    console.print('[bold magenta]Vanilla 服务端下载失败。')
                    return False
                console.print('Vanilla 服务端下载完成。')

            case 1:
                #paper
                serverType = 'paper'
                mcVersion = await paper.getLatestVersionName(self.source)
                javaPath = await self.Java.getJavaByGameVersion(mcVersion, path=self.Config.config['workspace'])
                status = await paper.downloadLatest(self.source,serverJarPath)
                if not status:
                    console.print('Paper 服务端下载失败。')
                    return False
                console.print('Paper 服务端下载完成。')
            case 2:
                #forge
                serverType = 'forge'
                raise NotImplementedError('Forge 服务端暂未实现。')
                mcVersions = await vanilla.get_versions(self.source)
                mcVersions = [x['id'] for x in mcVersions if x['type'] == 'release']
                index = await promptSelect(mcVersions,'请选择Minecraft服务器版本:')
            case 3:
                #fabric
                serverType = 'fabric'
                mcVersions = await vanilla.get_versions(self.source)
                mcVersions = [x['id'] for x in mcVersions if x['type'] == 'release']
                index = await promptSelect(mcVersions,'请选择Minecraft服务器版本:')
                mcVersion = mcVersions[index]
                javaPath = await self.Java.getJavaByGameVersion(mcVersion, path=self.Config.config['workspace'])
                loaderVersion = await fabric.getLoaderVersion(self.source)
                status = await fabric.downloadServer(self.source,os.path.join(serverPath,'server.jar'),mcVersion,loaderVersion)
                if not status:
                    console.print('Fabric 服务端下载失败。')
                    return False
                console.print('Fabric 服务端下载完成。')
            case 4:
                return False
        return serverName, serverType, serverPath, javaPath
    async def manage(self):
        workspaces = self.Workspace.workspaces
        if not workspaces:
            await self.create()
        console.rule('服务器管理')
        index = await promptSelect([x['name'] for x in workspaces],'选择服务器:')
        serverName = workspaces[index]['name']
        choice = await promptSelect(OPTIONS_MANAGE,f'{serverName} - 请选择操作:')
        server = await self.Workspace.get(index)
        match choice:
            case 0:
                server.run()
            case 1:
                try:
                    os.startfile(server.path)
                except:
                    console.print('[bold magenta]无法打开服务器目录。')
    async def delete(self):
        console.rule('服务器删除')
        if not self.Workspace.workspaces:
            console.print('没有服务器。')
            await self.mainMenu()
        index = await promptSelect([x['name'] for x in self.Workspace.workspaces],'请选择要删除的服务器:')
        if await promptConfirm('确定要删除吗?'):
            await self.Workspace.delete(index)
        await self.mainMenu()
    async def mainMenu(self):
        console.rule('Hikari Server Launcher')
        console.print('[bold gold]欢迎使用 Hikari Server Launcher.')
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