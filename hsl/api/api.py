from starlette.requests import Request
from starlette.applications import Starlette
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Route, WebSocketRoute
from starlette.staticfiles import StaticFiles
from starlette.websockets import WebSocket, WebSocketDisconnect
from hsl.core.main import HSL
from starlette.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
class HSL_API(HSL):
    def __init__(self):
        super().__init__()
    def run(self):
        routes = [
            #Route("/api/run_init", endpoint=self.run_init),
        ]
        app = Starlette(debug=True, routes=routes)
        app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
        uvicorn.run(app, host="0.0.0.0", port=23451)
hsl_api = HSL_API()
