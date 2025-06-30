import asyncio
import json
import websockets


class SonioxProvider:
    def __init__(
        self,
        api_key: str,
        websocket_url: str,
        audio_format: str = "pcm_s16le",
        sample_rate: int = 16000,
        num_channels: int = 1,
        model: str = "stt-rt-preview",
    ):
        self.api_key = api_key
        self.websocket_url = websocket_url
        self.audio_format = audio_format
        self.sample_rate = sample_rate
        self.num_channels = num_channels
        self.model = model

        self.websocket: websockets.WebSocketClientProtocol | None = None
        self._send_queue: asyncio.Queue[bytes] = asyncio.Queue()
        self._receive_queue: asyncio.Queue[str] = asyncio.Queue()
        self._connected = False
        self._send_task: asyncio.Task | None = None
        self._receive_task: asyncio.Task | None = None

    # Cnnects to websocket, sends initial message with config info
    async def connect(self) -> None:
        self.websocket = await websockets.connect(self.websocket_url)
        init_msg = {
            "api_key": self.api_key,
            "audio_format": self.audio_format,
            "sample_rate": self.sample_rate,
            "num_channels": self.num_channels,
            "model": self.model,
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

    # Will be used later for more frontend-y stuff
    async def get_transcripts(self) -> list[str]:
        transcripts = []
        while not self._receive_queue.empty():
            transcript = await self._receive_queue.get()
            transcripts.append(transcript)
        return transcripts


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

    async def _receive_loop(self) -> None:
        try:
            async for message in self.websocket:
                data = json.loads(message)
                if "error_message" in data:
                    print(f"SonioxProvider error: {data['error_message']}")
                    await self.disconnect()
                    break

                if "tokens" in data:
                    texts = [
                        token.get("text", "")
                        for token in data["tokens"]
                        if token.get("text")
                    ]
                    transcript_text = "".join(texts)
                    if transcript_text:
                        await self._receive_queue.put(transcript_text)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"SonioxProvider receive loop error: {e}")
            await self.disconnect()
