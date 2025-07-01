import asyncio
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from .stt.stt_handler import SpeechInputHandler
from .stt.parts import make_part

load_dotenv()
API_KEY = os.getenv("SONIOX_API_KEY")
WEBSOCKET_URL = "wss://stt-rt.soniox.com/transcribe-websocket"

app = FastAPI()

app.mount("/static", StaticFiles(directory="my_code/static"), name="static")


@app.get("/")
async def index():
    return FileResponse("my_code/static/index.html")

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.remove(websocket)
    
    async def send_json(self, websocket: WebSocket, data) -> None:
        await websocket.send_json(data)
    
    async def broadcast_json(self, data) -> None:
        for connection in self.active_connections:
            await connection.send_json(data)
    
manager = ConnectionManager()

@app.websocket("/ws/transcribe")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    handler = SpeechInputHandler(api_key=API_KEY, websocket_url=WEBSOCKET_URL)
    await handler.start()

    try:
        while True:
            parts = handler.get_parts()  # This returns a list of parts (each: {text, is_final})

            for part in parts:
                # Send each part immediately to frontend
                await manager.send_json(websocket, part)

            await asyncio.sleep(0.01)

    except WebSocketDisconnect:
        print("Client disconnected")
    finally:
        await handler.stop()
        manager.disconnect(websocket)
