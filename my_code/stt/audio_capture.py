import asyncio
import sounddevice as sd


class AudioCapture:
    def __init__(self, sample_rate=16000, channels=1, block_duration_ms=20):
        self.sample_rate = sample_rate
        self.channels = channels
        self.block_duration_ms = block_duration_ms
        self.block_size = int(self.sample_rate * self.block_duration_ms / 1000)
        self._queue = asyncio.Queue()
        self._stream = None
        self._loop = asyncio.get_event_loop()

    def _audio_callback(self, indata, frames, time, status) -> None:
        if status:
            print(f"Audio input status: {status}")
        # Convert numpy array to bytes
        self._loop.call_soon_threadsafe(self._queue.put_nowait, indata.tobytes())

    async def start(self) -> None:
        loop = asyncio.get_running_loop()
        self._queue = asyncio.Queue()
        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            blocksize=self.block_size,
            dtype="int16",
            callback=self._audio_callback,
        )

        self._stream.start()

    async def read_chunk(self) -> bytes:
        return await self._queue.get()

    async def stop(self) -> None:
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None
