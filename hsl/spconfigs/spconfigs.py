spconfigs = [
    {
        "name": "server.properties",
        "?name": "! 配置文件显示在特定配置编辑预览处的名字",
        "path": "server.properties",
        "?path": "! 配置文件的路径，子路径使用单个左斜线(/)分割",
        "description": "Minecraft服务器基本配置文件 包含端口，人数，正版等",
        "?description": "! 关于配置文件的介绍",
        "type": "properties",
        "?type": "! 配置文件类型，目前支持properties和yml两种",
        "keys": [
            {
                "name": "服务器端口",
                "key": "server-port",
                "?key": "！配置键的名称，如果有嵌套用单个点号(.)分割",
                "description": "服务器将监听的端口（默认：25565）",
                "tips": "只有你确定才要更改...",
                "?tips": "！提示，若设置将会在用户编辑时显示",
                "type": "int",
                "?type": "! 可以为int str bool",
                "danger": False,
                "?danger": "是否为危险配置，如果是将会额外提示用户"
            },
            {
                "name": "正版状态",
                "key": "online-mode",
                "description": "服务器是否进行正版验证（默认：是）",
                "tips": "不建议经常修改，因为正版和离线uuid互不兼容，容易导致玩家存档丢失",
                "type": "bool",
                "danger": True
            },
            {
                "name": "MOTD",
                "key": "motd",
                "description": "服务器展示在外部的预览文本",
                "tips": "支持中文",
                "type": "str",
                "danger": False
            },
            {
                "name": "PVP",
                "key": "pvp",
                "description": "服务器是否允许玩家互相攻击（默认：是）",
                "tips": "",
                "type": "bool",
                "danger": False
            },
            {
                "name": "最大玩家数",
                "key": "max-players",
                "description": "服务器可容纳最多玩家数量（默认:20）",
                "tips": "仅仅是上限，具体容纳人数取决于服务器配置",
                "type": "int",
                "danger": False
            },
            {
                "name": "出生点保护范围",
                "key": "spawn-protection",
                "description": "距离世界出生点2x+1范围内格数无法破坏（x为该项的值，默认：16）",
                "tips": "可以适当调小",
                "type": "int",
                "danger": False
            },
            {
                "name": "允许飞行",
                "key": "allow-flight",
                "description": "生存模式玩家悬空过久将被踢出，如果你被误杀，请打开此项允许悬空（默认：否）",
                "tips": "极其建议打开，太能误杀了",
                "type": "bool",
                "danger": False
            },
            {
                "name": "启用命令方块",
                "key": "enable-command-block",
                "description": "命令方块可否在本服务器工作？",
                "tips": "原版服若需要命令方块，可开启此项，插件服推荐使用插件而非指令",
                "type": "bool",
                "danger": False
            },
            {
                "name": "极限模式",
                "key": "hardcore",
                "description": "启用后服务器将进入极限模式，若死亡将被服务器封禁",
                "tips": "你很勇啊？",
                "type": "bool",
                "danger": True
            },
            {
                "name": "地图名称",
                "key": "level-name",
                "description": "服务器将尝试读取该目录下的地图作为世界（默认：world）",
                "tips": "",
                "type": "str",
                "danger": False
            },
            {
                "name": "地图种子",
                "key": "level-seed",
                "description": "服务器将使用该种子生成地图（默认：随机）",
                "tips": "若开服后修改，则新生成的地图会出现地形断层",
                "type": "int",
                "danger": True
            },
            {
                "name": "启用白名单",
                "key": "white-list",
                "description": "服务器是否启用白名单，启用后只有白名单中的玩家可以进入服务器（正版服独占，默认：否）",
                "tips": "设置白名单可使用白名单相关指令，值得注意的是如果未设置入白名单，服主也无法进入服务器",
                "type": "bool",
                "danger": False
            },
            {
                "name": "允许下界",
                "key": "allow-nether",
                "description": "服务器是否允许进入下界？（默认：是）",
                "tips": "没有下界需求的小游戏服可以关闭此项",
                "type": "bool",
                "danger": False
            },
            {
                "name": "游戏模式",
                "key": "gamemode",
                "description": "服务器默认游戏模式（默认：survival）",
                "tips": "服务器会默认进入服务器玩家的模式。",
                "type": "choice",
                "choices": [
                    "survival",
                    "creative",
                    "adventure"
                ],
                "danger": True
            },
            {
                "name": "难度",
                "key": "difficulty",
                "description": "服务器默认难度（默认：easy）",
                "tips": "服务器的难度。",
                "type": "choice",
                "choices": [
                    "peaceful",
                    "easy",
                    "normal",
                    "hard"
                ],
                "danger": False
            }
        ]
    },
    {
        "name": "bukkit.yml",
        "path": "bukkit.yml",
        "description": "Bukkit架构插件服 根本配置文件",
        "type": "yml",
        "keys": [
            {
                "name": "允许末地",
                "key": "settings.allow-end",
                "?key": "！配置键的名称，如果有嵌套用单个点号(.)分割",
                "description": "服务器是否允许进入末地？（默认：是）",
                "tips": "没有末地需求的小游戏服可以关闭此项",
                "type": "bool",
                "danger": False
            },
            {
                "name": "过载警告",
                "key": "settings.warn-on-overload",
                "description": "服务器过载时是否警告？（默认：是）",
                "tips": "眼不见心不烦",
                "type": "bool",
                "danger": False
            },
            {
                "name": "关服文本",
                "key": "settings.shutdown-message",
                "description": "服务器关服的提示文本",
                "tips": "服又无了？",
                "type": "str",
                "danger": False
            }
        ]
    },
    {
        "name": "Paper 世界设置",
        "path": "config/paper-world-defaults.yml",
        "?path":"! 配置文件的路径，子路径使用单个左斜线(/)分割",
        "description": "Paper世界设置",
        "type": "yml",
        "keys": [
            {
                "name": "反矿透",
                "key": "anticheat.anti-xray.enabled",
                "description": "是否启用反矿透？",
                "tips": "较为消耗服务器内存资源",
                "type": "bool",
                "danger": False
            },
            {
                "name": "反矿透引擎模式",
                "key": "anticheat.anti-xray.engine-mode",
                "description": "反矿透引擎模式（1,2：减少可见量，3：暴力填充混淆）",
                "tips": "较为消耗服务器内存资源",
                "type": "int",
                "danger": False
            }
        ]
    },
    {
        "name": "Paper 总设置",
        "path": "config/paper-global.yml",
        "description": "Paper总设置",
        "type": "yml",
        "keys": [
            {
                "name": "启用玩家碰撞",
                "key": "collisions.enable-player-collisions",
                "description": "玩家是否碰撞？",
                "tips": "当你被别人挤下悬崖时...",
                "type": "bool",
                "danger": False
            },
            {
                "name": "区块系统IO线程数",
                "key": "chunk-system.io-threads",
                "description": "区块系统IO线程数（-1自动）",
                "tips": "取决于核心数",
                "type": "int",
                "danger": True
            },
            {
                "name": "区块系统工作线程数",
                "key": "chunk-system.worker-threads",
                "description": "区块系统工作线程数（-1自动）",
                "tips": "取决于核心数",
                "type": "int",
                "danger": True
            }
        ]
    }
]
def get_spconfigs() -> list[dict]:
    return spconfigs