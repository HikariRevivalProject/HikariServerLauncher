from pydantic import BaseModel
from typing import List, Optional, Dict
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

class Source(BaseModel):
    mc: MC
    forge: Forge
    neoforge: NeoForge
    fabric: Fabric
    java: Java

source = {
    "version": 1,
    "mc": {
        "vanilla": {
            "list": [{
                "type": "bmclapi",
                "versionList": "https://bmclapi2.bangbang93.com/mc/game/version_manifest_v2.json",
                "server": "https://bmclapi2.bangbang93.com/version/{version}/server"
            }
        ]},
        "paper":{
            "latestVersionName": "1.21.1",
            "experimentalVersionName": "1.21.1",
            "list":[
                {
                    "type":"stable",
                    "latest":"https://api.papermc.io/v2/projects/paper/versions/1.21.1/builds/122/downloads/paper-1.21.1-122.jar"
                },
                {
                    "type":"experimental",
                    "latest":"https://api.papermc.io/v2/projects/paper/versions/1.21.1/builds/122/downloads/paper-1.21.1-122.jar"
                }
            ]
        }
    },
    "forge": {
        "list": [{
            "type": "official",
            "metadata": "https://files.minecraftforge.net/maven/net/minecraftforge/forge/maven-metadata.json",
            "download": "https://files.minecraftforge.net/maven/net/minecraftforge/forge/"
        },
        {
            "type": "bmclapi",
            "supportList": "https://bmclapi2.bangbang93.com/forge/minecraft",
            "getByVersion": "https://bmclapi2.bangbang93.com/forge/minecraft/{version}",
            "download": "https://bmclapi2.bangbang93.com/forge/download"
        }
    ]},
    "neoforge": {
        "list": [
        {
            "type": "official",
            "getByVersion": "https://bmclapi2.bangbang93.com/neoforge/list/{version}",
            "download": "https://bmclapi2.bangbang93.com/neoforge/version/{version}/download/installer.jar"
        }
    ]},
    "fabric": {
        "list": [{
            "type": "official",
            "supportList": "https://meta.fabricmc.net/v2/versions/game",
            "loaderList": "https://meta.fabricmc.net/v2/versions/loader",
            "installer": "https://meta.fabricmc.net/v2/versions/loader/{version}/{loader}/1.0.1/server/jar"
    }]},
    "java": {
        "list": [
            {
                "type": "GloryGods",
                "windows": {
                    "6": "https://jdk.114914.xyz/jdk-6.zip",
                    "8": "https://jdk.114914.xyz/jre1.8.0_341.zip",
                    "11": "https://jdk.114914.xyz/jdk-11.zip",
                    "16": "https://jdk.114914.xyz/jdk-16.zip",
                    "17": "https://jdk.114914.xyz/jdk-17.zip",
                    "21": "https://jdk.114914.xyz/jdk-21.zip"
                },
                "linux": {
                    "6": "https://jdk.114914.xyz/jdk-6-linux.zip",
                    "8": "https://jdk.114914.xyz/jdk8-linux.zip",
                    "11": "https://jdk.114914.xyz/jdk11-linux.zip",
                    "16": "https://jdk.114914.xyz/jdk-16-linux.zip",
                    "17": "https://jdk.114914.xyz/jdk-17-linux.zip",
                    "21": "https://jdk.114914.xyz/jdk-21-linux.zip"
                }
            },
            {
                "type": "lingyi",
                "windows": {
                    "6": "https://vip.123pan.cn/1821558579/Lingyi/java/6/jdk6-win-mcres.cn.zip",
                    "8": "https://vip.123pan.cn/1821558579/Lingyi/java/8/jre8_win-mcres.cn.zip",
                    "11": "https://vip.123pan.cn/1821558579/Lingyi/java/11/jdk11-win-mcres.cn.zip",
                    "16": "https://vip.123pan.cn/1821558579/Lingyi/java/16/jdk16-win-mcres.cn.zip",
                    "17": "https://vip.123pan.cn/1821558579/Lingyi/java/17/jdk17-win-mcres.cn.zip",
                    "21": "https://vip.123pan.cn/1821558579/Lingyi/java/21/jdk21-win-mcres.cn.zip"
                },
                "linux": {
                    "6": "https://vip.123pan.cn/1821558579/Lingyi/java/6/jdk6-lin.mcres.cn.zip",
                    "8": "https://vip.123pan.cn/1821558579/Lingyi/java/8/jdk8-lin-mcres.cn.zip",
                    "11": "https://vip.123pan.cn/1821558579/Lingyi/java/11/jdk11-lin-mcres.cn.zip",
                    "16": "https://vip.123pan.cn/1821558579/Lingyi/java/16/jdk16-lin-mcres.cn.zip",
                    "17": "https://vip.123pan.cn/1821558579/Lingyi/java/17/jdk17-lin-mcres.cn.zip",
                    "21": "https://vip.123pan.cn/1821558579/Lingyi/java/21/jdk21-lin-mcres.cn.zip"
                }
            }
    ]}
}
def get_source() -> Source:
    return Source(**source)