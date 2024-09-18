import asyncio
import webbrowser
from starlette.requests import Request
from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.routing import Route, WebSocketRoute
from starlette.staticfiles import StaticFiles
from starlette.websockets import WebSocket, WebSocketDisconnect

import uvicorn
import os
import logging
import sys
import psutil
import time
from hsl.core.main import HSL
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger('hsl')
def load_page(path) -> str:
    with open(os.path.join("hsl", "webui", "templates", path + ".html"), "r", encoding="utf-8") as f:
        return f.read()
class HSL_WEBUI(HSL):
    async def firstpage(self, request: Request):
        return HTMLResponse(
            #load_page("home")
            load_page("first")
        )
    async def homepage(self, request: Request):
        return HTMLResponse(
            load_page("home")
        )

    async def websocket_init(self, websocket: WebSocket):
        await websocket.accept()
        logger.info(f"HSL Init accepted")
        await websocket.close()
        await self.init()

    async def websocket_status(self, websocket: WebSocket):
        await websocket.accept()
        logger.info(f"HSL Status accepted, init: {self.flag_init}")
        try:
            try:
                while True:
                    await asyncio.sleep(1)
                    #get cpu percent
                    cpu_percent = int(psutil.cpu_percent(None))
                    #get memory percent
                    memory = int(psutil.virtual_memory().total / (1024.0 ** 2))
                    memory_used = int(psutil.virtual_memory().used / (1024.0 ** 2))
                    #get disk percent
                    disk = int(psutil.disk_usage('/').total / (1024.0 ** 3))
                    disk_used = int(psutil.disk_usage('/').used / (1024.0 ** 3))
                    await websocket.send_json({"init": self.flag_init, "timestamp": int(time.time()), "cpu_percent": cpu_percent, "memory": memory, "memory_used": memory_used, "disk": disk, "disk_used": disk_used, "outdated": self.flag_outdated})
            except WebSocketDisconnect:
                logger.info(f"WebSocket Disconnected")
            finally:
                await websocket.close()
        except RuntimeError:
            pass

    def __init__(self):
        super().__init__()

    def run(self):
        host = self.config.host
        port = self.config.port
        routes = [
            Route("/", endpoint=self.firstpage),
            Route("/home", endpoint=self.homepage),
            WebSocketRoute("/ws/status", endpoint=self.websocket_status),
            WebSocketRoute("/ws/init", endpoint=self.websocket_init),
        ]
        self.app = Starlette(debug=True, routes=routes)
        self.app.mount("/static", StaticFiles(directory="hsl/webui/templates/static"), name="static")
        self.app.mount("/", StaticFiles(directory="hsl/webui/templates/"), name="templates")
        webbrowser.open(f"http://localhost:{port}/", autoraise=True)
        uvicorn.run(self.app, host=host, port=port, log_level="info")