import asyncio

from .audio_capture import AudioCapture
from .soniox_provider import SonioxProvider
from .parts import make_part


class SpeechInputHandler:
    def __init__(self, api_key: str, websocket_url: str):
        self.soniox = SonioxProvider(api_key, websocket_url)
        self.audio_capture = AudioCapture()
        self._running = False
        self._task_audio = None
        self._task_receive = None
        self.final_transcripts = []
        self.partial_transcript = ""
        self.parts: list[dict] = []

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
                incoming = await self.soniox.get_transcripts()
                for item in incoming:
                    tokens = item.get("tokens", [])
                    is_final = item.get("is_final", False)

                    text = "".join(token["text"] for token in tokens)
                    # Finalized text is permaently added to self.transcript
                    if is_final:
                        if text:
                            self.final_transcripts.append(text)
                        self.partial_transcript = ""
                    else:
                        self.partial_transcript = text
                    
                    # Save all parts (final and non-final)
                    self.parts.append(make_part(text=text, is_final=is_final))
                
                await asyncio.sleep(0.01)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Error in receive loop: {e}")
            self._running = False

    def get_transcript(self) -> str:
        """Return concatenated transcripts collected so far."""
        return " ".join(self.final_transcripts) + " " + self.partial_transcript
    
    def get_parts(self) -> list[dict]:
        parts, self.parts = self.parts, []
        return parts
