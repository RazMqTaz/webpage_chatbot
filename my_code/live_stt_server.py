import asyncio
import os
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from starlette.responses import FileResponse
from .stt.soniox_provider import SonioxProvider  
from .stt.audio_capture import AudioCapture

app = FastAPI()

load_dotenv()
SONIOX_API_KEY = os.getenv("SONIOX_API_KEY")
WEBSOCKET =  "wss://stt-rt.soniox.com/transcribe-websocket"

@app.get("/")
async def index():
    return FileResponse("my_code/static/index.html")

@app.websocket("/ws/transcribe")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    class Config:
        websocket_url=WEBSOCKET
        api_key=SONIOX_API_KEY
        audio_format = "pcm_s16le"
        sample_rate = 16000
        num_channels = 1
        model = "stt-rt-preview"
        language_hints = ["en"]
    
    # Setup your provider and audio capture
    config = Config()
    provider = SonioxProvider(config)
    audio_capture = AudioCapture()
    await provider.connect()
    await audio_capture.start()

    async def send_audio():
        try:
            while True:
                chunk = await audio_capture.read_chunk()
                await provider.send_audio(chunk)
        except asyncio.CancelledError:
            pass

    send_audio_task = asyncio.create_task(send_audio())

    try:
        while True:
            parts = await provider.receive_parts()
            if parts:
                # Send entire list as one JSON message
                await websocket.send_json(parts)
            await asyncio.sleep(0.01)
    except WebSocketDisconnect:
        print("Client disconnected")
    finally:
        send_audio_task.cancel()
        await audio_capture.stop()
        await provider.disconnect()
