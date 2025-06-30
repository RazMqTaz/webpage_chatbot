import asyncio
from .audio_capture import AudioCapture
from .soniox_provider import SonioxProvider


class SpeechInputHandler:
    def __init__(self, api_key: str, websocket_url: str):
        self.soniox = SonioxProvider(api_key, websocket_url)
        self.audio_capture = AudioCapture()
        self._running = False
        self._task_audio = None
        self._task_receive = None
        self.transcripts = []

    async def start(self) -> None:
        """Start audio capture and connect to Soniox for streaming."""
        await self.soniox.connect()
        await self.audio_capture.start()
        self._running = True
        # Launch background tasks for sending audio and receiving transcripts
        self._task_audio = asyncio.create_task(self._send_audio_loop())
        self._task_receive = asyncio.create_task(self._receive_loop())

    async def stop(self) -> None:
        """Stop streaming and disconnect cleanly."""
        self._running = False

        # Cancel background tasks
        if self._task_audio:
            self._task_audio.cancel()
            try:
                await self._task_audio
            except asyncio.CancelledError:
                pass

        if self._task_receive:
            self._task_receive.cancel()
            try:
                await self._task_receive
            except asyncio.CancelledError:
                pass

        # Stop audio capture and disconnect from Soniox
        await self.audio_capture.stop()
        await self.soniox.disconnect()

    async def _send_audio_loop(self) -> None:
        """Continuously read audio chunks and send to Soniox."""
        try:
            while self._running:
                chunk = await self.audio_capture.read_chunk()
                await self.soniox.send_audio(chunk)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Error in audio sending loop: {e}")
            self._running = False

    async def _receive_loop(self) -> None:
        """Continuously poll Soniox for transcripts and buffer them."""
        try:
            while self._running:
                new_transcripts = await self.soniox.get_transcripts()
                if new_transcripts:
                    self.transcripts.extend(new_transcripts)
                await asyncio.sleep(0.1)  # Poll interval, adjust as needed
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Error in receive loop: {e}")
            self._running = False

    def get_transcript(self) -> str:
        """Return concatenated transcripts collected so far."""
        return " ".join(self.transcripts)
