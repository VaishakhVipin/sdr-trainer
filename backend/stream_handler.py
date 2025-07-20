import asyncio
import websockets
import base64
import json
import requests
import sounddevice as sd
import os
from dotenv import load_dotenv

load_dotenv()

ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
BACKEND_API = "http://localhost:8000/generate-response"  # Your FastAPI endpoint

TRANSCRIPT_URL = "wss://api.assemblyai.com/v2/realtime/ws?sample_rate=16000"

# Customize this with your current sales persona
PERSONA = ""
HISTORY = ""
OFFER = ""

# Store convo history
conversation = ""

async def send_receive():
    global conversation
    async with websockets.connect(
        TRANSCRIPT_URL,
        extra_headers={"Authorization": ASSEMBLYAI_API_KEY},
        ping_interval=5,
        ping_timeout=20
    ) as ws:
        print("🎙️ Connected to AssemblyAI. Start speaking...")

        def callback(indata, frames, time, status):
            if status:
                print(status)
            data = base64.b64encode(indata).decode("utf-8")
            asyncio.create_task(ws.send(json.dumps({"audio_data": data})))

        with sd.InputStream(callback=callback, channels=1, samplerate=16000, dtype='int16'):
            while True:
                result = await ws.recv()
                msg = json.loads(result)

                if "text" in msg and msg['message_type'] == 'FinalTranscript':
                    user_input = msg['text'].strip()
                    print(f"🧠 You said: {user_input}")

                    # Send to your FastAPI Gemini agent
                    payload = {
                        "user_input": user_input,
                        "history": conversation,
                        "persona": PERSONA,
                        "offer": OFFER
                    }

                    try:
                        r = requests.post(BACKEND_API, json=payload)
                        ai_reply = r.json()["reply"]
                        print(f"🤖 Gemini replied: {ai_reply}")

                        # Update conversation history
                        conversation += f"\nUser: {user_input}\nAI: {ai_reply}\n"

                    except Exception as e:
                        print("❌ Error hitting backend:", e)

if __name__ == "__main__":
    asyncio.run(send_receive())
