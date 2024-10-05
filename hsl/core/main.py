from hsl.core.config import Config
from hsl.core.checks import load_source, get_spconfigs, check_update
from rich.console import Console
import sys
import platform
console = Console()
HSL_VERSION = 16

OS_ARCH = platform.machine()
if OS_ARCH != 'AMD64':
    console.print(f'当前系统架构{OS_ARCH}不支持，请使用AMD64架构的设备/系统运行.')
    sys.exit(1)
with console.status('[bold purple]正在启动 Hikari Server Launcher...',spinner='material'):
    console.print('[bold green]加载信息中，请稍后...')
    SOURCE = load_source()
    console.print('[bold green]加载源数据成功.')
    SPCONFIGS = get_spconfigs()
    console.print('[bold green]加载特定配置文件成功.')
    VERSION_INFO = check_update(HSL_VERSION)
    console.print('[bold green]检查更新完成.')

class HSL:
    """Main class of HSL
    """
    def __init__(self):
        self.version = HSL_VERSION
        self.config = Config().load()
        self.source = SOURCE
        self.spconfigs = SPCONFIGS
        self.flag_outdated, self.latest_version = VERSION_INFO
        if not self.source or not self.spconfigs:
            console.print('加载源数据失败，请检查网络连接.')
            sys.exit(1)
        self.tasks = []