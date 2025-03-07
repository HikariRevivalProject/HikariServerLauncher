from pydantic import BaseModel
from typing import List, Optional, Dict
import httpx
class VanillaSource(BaseModel):
    type: str
    versionList: str
    server: str

class Vanilla(BaseModel):
    list: List[VanillaSource]

class PaperSource(BaseModel):
    type: str
    latest: str

class Paper(BaseModel):
    latestVersionName: str
    experimentalVersionName: str
    list: List[PaperSource]

class MC(BaseModel):
    vanilla: Vanilla
    paper: Paper

class ForgeSource(BaseModel):
    type: str
    metadata: Optional[str]
    download: Optional[str]
    supportList: Optional[str]
    getByVersion: Optional[str]

class Forge(BaseModel):
    list: List[ForgeSource]

class NeoForgeSource(BaseModel):
    type: str
    getByVersion: str
    download: str

class NeoForge(BaseModel):
    list: List[NeoForgeSource]

class FabricSource(BaseModel):
    type: str
    supportList: str
    loaderList: str
    installer: str

class Fabric(BaseModel):
    list: List[FabricSource]

class JavaSource(BaseModel):
    type: str
    windows: Dict[str, str]
    linux: Dict[str, str]

class Java(BaseModel):
    list: List[JavaSource]

class OpenFrp(BaseModel):
    pwdLogin: str
    authCode: str
    codeLogin: str
    getUserInfo: str
    getUserProxies: str
    newProxy: str
    removeProxy: str
    getNodeList: str
    editProxy: str

class Source(BaseModel):
    mc: MC
    forge: Forge
    neoforge: NeoForge
    fabric: Fabric
    java: Java
    openfrp: OpenFrp
SOURCE_URL = "https://hsl-config.oss-cn-beijing.aliyuncs.com/source.json"
def get_source() -> Source:
    return Source(**httpx.get(SOURCE_URL).json())