from hsl.api import HSL_API
from hsl.core.main import HSL
from hsl.webui import HSL_WEBUI
import threading
if __name__ == '__main__':
    thread1 = threading.Thread(target=HSL_API().run)
    thread2 = threading.Thread(target=HSL_WEBUI().run)
    thread1.start()
    thread2.start()
