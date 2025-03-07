from typing import Optional, Literal
from pydantic import BaseModel
import json

from hsl.core.exceptions import RequestFailedException
from hsl.openfrp.apireq import openfrp_api_request
from hsl.source.source import get_source
class OpenFrpTunnel(BaseModel):
    autoTls: str
    connectAddress: str
    custom: Optional[str]
    domain: Optional[str]
    forceHttps: bool
    friendlyNode: str
    id: int
    lastLogin: Optional[int]
    lastUpdate: int
    localIp: str
    localPort: int
    nid: int
    online: bool
    proxyName: str
    proxyType: Literal['tcp','udp','http','https','stcp','xtcp']
    proxyProtocolVersion: str
    status: bool
    uid: int
    useEncryption: bool
    useCompression: bool
class OpenFrpTunnelShort(BaseModel):
    autoTls: str
    custom: str
    dataEncrypt: bool
    dataGzip: bool
    domain_bind: str
    forceHttps: bool
    local_addr: str
    local_port: int
    name: str
    node_id: int
    proxyProtocolVersion: bool
    remote_port: int
    type: Literal['tcp']
class OpenFrpTunnelList(BaseModel):
    total: int
    list: list[OpenFrpTunnel]
async def getUserProxies(auth: str) -> Optional[list[OpenFrpTunnel]]:
    """获取用户隧道列表

    Args:
        auth (str): Authorization

    Returns:
        Optional[list[OpenFrpTunnel]]: 隧道列表，可空
    """
    source = get_source()
    _resp = await openfrp_api_request(source.openfrp.getUserProxies, authorization=auth)
    try:
        tunnelList = OpenFrpTunnelList(**_resp.json()['data'])
    except RequestFailedException:
        return None
    return tunnelList.list
async def newTunnel(auth: str, tunnel: OpenFrpTunnelShort) -> bool:
    """新建隧道

    Args:
        auth (str): Authorizaton
        tunnel (OpenFrpTunnelShort): 短隧道信息

    Returns:
        bool: 是否成功
    """
    source = get_source()
    _resp = await openfrp_api_request(source.openfrp.newProxy, data=tunnel.dict(), authorization=auth)
    return _resp.status_code == 200
async def delTunnel(auth: str, tunnelId: int) -> bool:
    """删除隧道

    Args:
        auth (str): Authorization
        tunnelId (int): 隧道Id

    Returns:
        bool: 是否成功
    """
    source = get_source()
    _resp = await openfrp_api_request(source.openfrp.removeProxy, data={'proxy_id': tunnelId}, authorization=auth)
    return _resp.status_code == 200
async def editTunnel(auth: str, tunnelId: int, tunnel: OpenFrpTunnelShort) -> bool:
    """编辑隧道

    Args:
        auth (str): Authorization
        tunnelId (int): 隧道Id
        tunnel (OpenFrpTunnelShort): 短隧道信息

    Returns:
        bool: 是否成功
    """
    source = get_source()
    data = tunnel.dict()
    data['proxy_id'] = tunnelId
    _resp = await openfrp_api_request(source.openfrp.editProxy, data=data, authorization=auth)
    return _resp.status_code == 200