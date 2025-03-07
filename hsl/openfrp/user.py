from typing import Optional, Literal, Dict
from rich.console import Console
from httpx import Cookies
from hsl.source.source import get_source
from hsl.openfrp.tunnel import OpenFrpTunnelShort
from hsl.openfrp.tunnel import OpenFrpTunnel, getUserProxies, newTunnel, delTunnel, editTunnel
from hsl.openfrp.node import OpenFrpNodeInfo, getOpenFrpNodeList
from hsl.openfrp.apireq import openfrp_api_request
from pydantic import BaseModel
from hsl.source.source import get_source
from hsl.core.exceptions import RequestFailedException
from hsl.core.locale import Locale
from hsl.core.config import Config
import time
import os
from rich.console import Console
console = Console()
locale = Locale()
config = Config().load()
userGroups = {
    'normal': 1,
    'vip': 2,
    'svip': 3,
    'admin': 4,
    'dev': 4
}
class OpenFrpUserInfo(BaseModel):
    """
        OpenFrp用户信息
    """
    outLimit: int # 上行带宽 in Kbps
    used: int # 已用隧道数量
    token: str # 授权码
    realname: bool # 是否实名认证
    regTime: str # 注册时间
    inLimit: int # 下行带宽 in Kbps
    friendlyGroup: str # 用户组可读名
    proxies: int # 可用隧道数量
    id: int # 用户ID
    email: str # 邮箱
    username: str # 用户名 
    group: Literal['normal','vip','svip','admin','dev'] # 用户组标识符
    traffic: int # 剩余流量 in MB
    def __str__(self) -> str:
        """
            可读用户信息
        """
        return locale.trans_key('openfrp-user-info',username=self.username,email=self.email,group=self.friendlyGroup,registertime=self.regTime,traffic=str(self.traffic),realname='是' if self.realname else '否',proxies=str(self.proxies),used=str(self.used),outLimit=str(self.outLimit),inLimit=str(self.inLimit))
    def getGroupLevel(self) -> int:
        """获取用户组级别

        Returns:
            int: 用户组级别
        """
        return userGroups[self.group]
async def pwdLogin(*, username: str, password: str) -> Optional[Cookies]:
    """请求OpenFrp账密登录

    Args:
        username (str): 用户名/邮箱
        password (str): 密码

    Returns:
        Optional[Cookies]: 返回Cookies，可空
    """
    source = get_source()
    if config.openfrp_username and config.openfrp_password:
        console.print(locale.trans_key('openfrp-using-cache'))
        username = config.openfrp_username
        password = config.openfrp_password
    _resp = await openfrp_api_request(source.openfrp.pwdLogin, data={
        "user": username,
        "password": password
    })
    config.openfrp_password = password
    config.openfrp_username = username
    config.save()
    return _resp.cookies

async def getApiCode(cookie: str) -> Optional[str]:
    """使用17a Cookie 取得API Code

    Args:
        cookie (str): 17a Cookie

    Returns:
        Optional[str]: Api Code，可空
    """
    source = get_source()
    _resp = await openfrp_api_request(source.openfrp.authCode, data={}, cookie=cookie)
    return _resp.json()["data"]['code']
async def codeLogin(code: str) -> Optional[str]:
    """通过API Code登录OpenFrp，返回Authorization

    Args:
        code (str): API Code

    Returns:
        Optional[str]: Authorization，可空
    """
    source = get_source()
    _resp = await openfrp_api_request(source.openfrp.codeLogin.replace(r'{code}', code), data={})
    authorization = _resp.headers.get("Authorization")
    console.print(locale.trans_key('openfrp-get-authorization', auth=authorization))
    return authorization
async def getUserInfo(authToken: str) -> Optional[OpenFrpUserInfo]:
    """
        获取OpenFrp用户信息
    """
    source = get_source()
    _resp = await openfrp_api_request(source.openfrp.getUserInfo, data={}, authorization=authToken)
    return OpenFrpUserInfo(**_resp.json()["data"])
async def runLogin(username: str, password: str) -> Optional[tuple[OpenFrpUserInfo, str]]:
    """执行OpenFrp登录

    Args:
        username (str): 用户名/邮箱
        password (str): 密码

    Returns:
        Optional[tuple[OpenFrpUserInfo, str]]: 用户信息和Authorization，可空
    """
    console.print(locale.trans_key('openfrp-running-login', username=username))
    pwdlogincookie = await pwdLogin(username=username, password=password)
    code = await getApiCode(pwdlogincookie['17a']) # type: ignore
    authToken = await codeLogin(code) # type: ignore
    userInfo = await getUserInfo(authToken) # type: ignore
    return userInfo, authToken # type: ignore

class OpenFrpUser():
    def __init__(self, username: str, password: str) -> None:
        self.username: str = username
        self.password: str = password
        self.authorization: str = ''
        self.userInfo: Optional[OpenFrpUserInfo] = None
        self.lastLoginTime: int = 0
    async def getUserInfo(self) -> Optional[OpenFrpUserInfo]:
        """获取OpenFrp用户信息

        Returns:
            Optional[OpenFrpUserInfo]: 用户信息，可空
        """
        console.print(locale.trans_key('openfrp-getting-user-info', username=self.username))
        await self.check_and_update_authorization()
        if self.userInfo is None:
            console.print(locale.trans_key('openfrp-failed-get-user-info'))
        return self.userInfo
    async def check_and_update_authorization(self) -> bool:
        """检查并更新Authorization

        Returns:
            bool: 是否有更新
        """
        if time.time() - self.lastLoginTime < 3600:
            console.print(locale.trans_key('openfrp-authorization-may-not-expired'))
            return False
        try:
            self.userInfo, self.authorization = await runLogin(self.username, self.password) # type: ignore
        except RequestFailedException:
            console.print(locale.trans_key('openfrp-login-failed'))
            return False
        self.lastLoginTime = int(time.time())
        return True
    async def getOpenFrpNodeList(self) -> Optional[list[OpenFrpNodeInfo]]:
        """获取OpenFrp节点列表

        Returns:
            Optional[list[OpenFrpNodeInfo]]: 节点列表，可空
        """
        console.print("[bold green]正在获取OpenFrp节点列表...[/bold green]")
        await self.check_and_update_authorization()
        return await getOpenFrpNodeList(self.authorization) # type: ignore
    async def getOpenFrpTunnelList(self) -> Optional[list[OpenFrpTunnel]]:
        """获取OpenFrp隧道列表

        Returns:
            Optional[list[OpenFrpTunnel]]: 隧道列表，可空
        """
        console.print("[bold green]正在获取OpenFrp隧道列表...[/bold green]")
        await self.check_and_update_authorization()
        return await getUserProxies(self.authorization) # type: ignore
    async def newTunnel(self, tunnel: OpenFrpTunnelShort) -> bool:
        """新建隧道

        Args:
            tunnel (OpenFrpTunnelShort): 短隧道信息

        Returns:
            bool: 是否成功
        """
        console.print("[bold green]正在新建隧道...[/bold green]")
        await self.check_and_update_authorization()
        return await newTunnel(self.authorization, tunnel) # type: ignore
    async def delTunnel(self, tunnelId: int) -> bool:
        """删除隧道

        Args:
            tunnelId (int): 隧道Id

        Returns:
            bool: 是否成功
        """
        console.print("[bold green]正在删除隧道...[/bold green]")
        await self.check_and_update_authorization()
        return await delTunnel(self.authorization, tunnelId)
    async def editTunnel(self, tunnelId: int, tunnel: OpenFrpTunnelShort) -> bool:
        """编辑隧道

        Args:
            tunnelId (int): 隧道Id
            tunnel (OpenFrpTunnelShort): 短隧道信息

        Returns:
            bool: 是否成功
        """
        console.print("[bold green]正在编辑隧道...[/bold green]")
        await self.check_and_update_authorization()
        return await editTunnel(self.authorization, tunnelId, tunnel) # type: ignore