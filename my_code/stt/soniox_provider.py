import asyncio
import json
import os
from dotenv import load_dotenv
import websockets
from .parts import make_part


class SonioxProvider:
    def __init__(self, config):
        self.config = config
        self.websocket = None
        self._send_queue = asyncio.Queue()
        self._receive_queue = asyncio.Queue()
        self._connected = False
        self._send_task = None
        self._receive_task = None

    # Cnnects to websocket, sends initial message with config info
    async def connect(self) -> None:
        if self._connected:
            return
        self.websocket = await websockets.connect(self.config.websocket_url)
        init_msg = {
            "api_key": self.config.api_key,
            "audio_format": self.config.audio_format,
            "sample_rate": self.config.sample_rate,
            "num_channels": self.config.num_channels,
            "model": self.config.model,
            "language_hints": self.config.language_hints,
        }
        await self.websocket.send(json.dumps(init_msg))
        self._connected = True
        self._send_task = asyncio.create_task(self._send_loop())
        self._receive_task = asyncio.create_task(self._receive_loop())

    # Disconnects from websocket
    async def disconnect(self) -> None:
        self._connected = False
        if self._send_task:
            self._send_task.cancel()
        if self._receive_task:
            self._receive_task.cancel()
        if self.websocket:
            await self.websocket.close()

    # Sends audio  chunks (bytes) into the internal send queue (_send_queue) asynchronously.
    async def send_audio(self, audio_bytes: bytes) -> None:
        if not self._connected:
            raise RuntimeError("Soniox provider: Not Connected.")
        await self._send_queue.put(audio_bytes)

    async def receive_parts(self) -> list[dict]:
        all_parts = []
        while not self._receive_queue.empty():
            parts = await self._receive_queue.get()
            all_parts.extend(parts)
        return all_parts

    # Sends audio through websocket
    async def _send_loop(self) -> None:
        try:
            while self._connected:
                audio_chunk = await self._send_queue.get()
                await self.websocket.send(audio_chunk)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"SonioxProvider send loop error: {e}")

    async def get_transcripts(self) -> list[str]:
        transcripts = []
        while not self._receive_queue.empty():
            transcript = await self._receive_queue.get()
            transcripts.append(transcript)
        return transcripts

    async def _receive_loop(self):
        try:
            async for resp in self.websocket:
                data = json.loads(resp)
                if "error_message" in data:
                    await self._handle_error(data["error_message"])
                    break
                parts = []
                if "tokens" in data:
                    for t in data["tokens"]:
                        text = t.get("text")
                        if isinstance(text, list):
                            text = "".join(text)
                        is_final = t.get("is_final", False)
                        parts.append(make_part(text=text, is_final=is_final))
                if parts:
                    await self._receive_queue.put(parts)
        except Exception as ex:
            await self._handle_error(ex)
