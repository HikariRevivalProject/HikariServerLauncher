import asyncio
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
                    await asyncio.sleep(0.5)
                    await websocket.send_json({"init": self.flag_init, "timestamp": time.time()})
            except WebSocketDisconnect:
                logger.info(f"WebSocket Disconnected")
            finally:
                await websocket.close()
        except RuntimeError:
            pass

    def __init__(self, host, port):
        super().__init__()
        routes = [
            Route("/", endpoint=self.firstpage),
            Route("/home", endpoint=self.homepage),
            WebSocketRoute("/ws/init", endpoint=self.websocket_init),
            WebSocketRoute("/ws/status", endpoint=self.websocket_status),
        ]
        self.app = Starlette(debug=True, routes=routes)
        self.app.mount("/static", StaticFiles(directory="hsl/webui/templates/static"), name="static")
        self.app.mount("/", StaticFiles(directory="hsl/webui/templates/"), name="templates")
        uvicorn.run(self.app, host=host, port=port, log_level="info")
        
if __name__ == "__main__":
    HSL_WEBUI('0.0.0.0', 15432)