import asyncio
import os
from dotenv import load_dotenv

from stt.stt_handler import SpeechInputHandler
from stt.parts import make_part

# Load .env
load_dotenv()
API_KEY = os.getenv("SONIOX_API_KEY")
WEBSOCKET_URL="wss://stt-rt.soniox.com/transcribe-websocket"

async def user_input(prompt: str) -> str:
    # Run blocking input() in a thread so it doesn't block the event loop
    return await asyncio.to_thread(input, prompt)


async def live_stt_session() -> None:
    if not API_KEY:
        print("Error: SONIOX_API_KEY not found in environment variables.")
        return

    handler = SpeechInputHandler(
        api_key=API_KEY, websocket_url=WEBSOCKET_URL
    )

    await handler.start()
    print("Start speaking! Type 'stop' and press Enter to end.\n")

    final_text = ""
    partial_text = ""

    async def input_monitor():
        while True:
            cmd = await user_input("\n>")
            if cmd.strip().lower() == "stop":
                raise KeyboardInterrupt
    
    monitor_task = asyncio.create_task(input_monitor())

    try:
        while True:
            parts = handler.get_parts()

            for part in parts:
                if part["is_final"]:
                    final_text += part["text"]
                    partial_text = ""
                else:
                    partial_text = part["text"]

            full_line = final_text + partial_text
            print("\r" + full_line + "|", end="", flush=True)

            await asyncio.sleep(0.05)
    except KeyboardInterrupt:
        pass
    finally:
        await handler.stop()
        print("\nFinal transcription:")
        print(handler.get_transcript())


if __name__ == "__main__":
    asyncio.run(live_stt_session())
