import asyncio
import tkintertools as tkt
import tkintertools.animation as animation
import tkintertools.color as color
import tkintertools.core.constants as constants
import tkintertools.standard.dialogs as dialogs  # Customied
import tkintertools.standard.features as features  # Customied
import tkintertools.standard.shapes as shapes  # Customied
import tkintertools.standard.texts as texts  # Customied
import tkintertools.style as style
import tkintertools.toolbox as toolbox

WIDTH = 1280
HEIGHT = 720
HSL_NAME = 'Hikari Server Launcher'

async def init():
    root = tkt.Tk((WIDTH,HEIGHT),title=f"{HSL_NAME} - GUI DEMO")
    root.alpha(1)
    root.center()
    canvas = tkt.Canvas(root, zoom_item=True, keep_ratio="min", free_anchor=True)
    canvas.place(width=1280, height=720, anchor="center")