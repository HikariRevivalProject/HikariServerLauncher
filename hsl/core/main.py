from hsl.core.config import Config
from hsl.core.checks import load_source, get_spconfigs, check_update
from rich.console import Console
import sys
import platform
console = Console()
HSL_VERSION = 15

OS_ARCH = platform.machine()
if OS_ARCH != 'AMD64':
    console.print(f'当前系统架构{OS_ARCH}不支持，请使用AMD64架构的设备/系统运行.')
    sys.exit(1)

console.rule('加载信息中，请稍后...')
SOURCE = load_source()
SPCONFIGS = get_spconfigs()
VERSION_INFO = check_update(HSL_VERSION)

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