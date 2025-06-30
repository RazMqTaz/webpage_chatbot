import asyncio
import os
from dotenv import load_dotenv
from stt.stt_handler import SpeechInputHandler

load_dotenv()


async def user_input(prompt: str) -> str:
    # Run blocking input() in a thread so it doesn't block the event loop
    return await asyncio.to_thread(input, prompt)


async def live_stt_session() -> None:
    api_key = os.getenv("SONIOX_API_KEY")
    if not api_key:
        print("Error: SONIOX_API_KEY not found in environment variables.")
        return

    handler = SpeechInputHandler(
        api_key=api_key, websocket_url="wss://stt-rt.soniox.com/transcribe-websocket"
    )

    await handler.start()
    print("Start speaking! Type 'stop' and press Enter to end.\n")

    try:
        while True:
            transcript = handler.get_transcript()
            if transcript:
                print(f"\rTranscription so far: {transcript}", end="", flush=True)

            cmd = await user_input("\n> ")
            if cmd.strip().lower() == "stop":
                print("\nStopping transcription...")
                break

            await asyncio.sleep(0.1)
    finally:
        await handler.stop()
        print("\nFinal transcription:")
        print(handler.get_transcript())


if __name__ == "__main__":
    asyncio.run(live_stt_session())
