from pydantic import BaseModel
from hsl.openfrp.apireq import openfrp_api_request
from typing import Optional, Union, Literal, List
from hsl.source.source import get_source
from hsl.core.exceptions import RequestFailedException
userGroups = {
    'normal': 1,
    'vip': 2,
    'svip': 3,
    'admin': 4,
    'dev': 4
}
class protocolSupport(BaseModel):
    """
        协议支持
    """
    tcp: bool
    udp: bool
    http: bool
    https: bool
class OpenFrpNodeInfo(BaseModel):
    """
        OpenFrp节点信息
    """
    allowEc: bool
    bandwidth: int
    bandwithMagnification: Optional[float]
    classify: Literal[1, 2, 3]
    comments: str
    enableDefaultTls: Optional[bool]
    group: str
    hostname: str
    id: int
    maxOnlineMagnification: float
    name: str
    needRealname: bool
    port: Union[int, str]
    status: int
    unitcostEc: int
    description: str
    protocolSupport: protocolSupport
    fullyLoaded: bool
    
    def getNodeUrl(self) -> str:
        """
            获取节点URL
        """
        return f'{self.hostname}:{self.port}'
    def getGroupLevels(self) -> list[int]:
        """
            获取节点组等级
        """
        return [userGroups[group] for group in self.group.split(';')]

class OpenFrpNodeList(BaseModel):
    """
        OpenFrp节点列表
    """
    total: int
    list: List[OpenFrpNodeInfo]
async def getOpenFrpNodeList(auth: str, filter: bool = False, userGroup: int = 1) -> Optional[list[OpenFrpNodeInfo]]:
    """
        获取OpenFrp节点列表
        
        filter: 是否过滤
    """
    source = get_source()
    _resp = await openfrp_api_request(source.openfrp.getNodeList, authorization=auth)
    try:
        nodeList = OpenFrpNodeList(**_resp.json()['data'])
    except RequestFailedException:
        return None
    if filter:
        return [node for node in nodeList.list 
                if isinstance(node.port, int) 
                and node.status == 200 
                and not node.fullyLoaded # overloaded (why use this shit name)
                and node.protocolSupport.tcp 
                and userGroup in node.getGroupLevels()
                ]
    return nodeList.list