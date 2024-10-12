from hsl.core.config import Config
from hsl.core.checks import get_version
from hsl.source.source import get_source
from hsl.spconfigs.spconfigs import get_spconfigs
from rich.console import Console
import sys
import platform
console = Console()

OS_ARCH = platform.machine()
if OS_ARCH != 'AMD64':
    console.print(f'当前系统架构{OS_ARCH}不支持，请使用AMD64架构的设备/系统运行.')
    sys.exit(1)
with console.status('[bold purple]正在启动 Hikari Server Launcher...',spinner='material'):
    console.print('[bold green]加载信息中，请稍后...')
    SOURCE = get_source()
    console.print('[bold green]加载源数据成功.')
    SPCONFIGS = get_spconfigs()
    console.print('[bold green]加载特定配置成功.')

class HSL:
    """Main class of HSL
    """
    def __init__(self):
        self.version, self.minor_version = get_version()
        self.config = Config().load()
        self.source = SOURCE
        self.spconfigs = SPCONFIGS
        if not self.source or not self.spconfigs:
            console.print('加载源数据失败，请检查网络连接.')
            sys.exit(1)
        # self.tasks = []