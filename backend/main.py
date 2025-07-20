from fastapi import FastAPI, File, UploadFile, Form, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from .agent import generate_response, score_call, generate_session_title
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv
import assemblyai as aai
import uuid
import requests
from fastapi.responses import StreamingResponse
import asyncio
import websockets
import base64
import time
import json
from supabase import create_client, Client

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AssemblyAI client
AUDIO_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
aai.settings.api_key = AUDIO_API_KEY

# In-memory session store (replace with DB like Supabase for production)
sessions = {}

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_PUBLIC_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class CallRequest(BaseModel):
    user_input: str
    history: str
    persona: str
    offer: str

@app.post("/generate-response")
async def call_response(req: CallRequest):
    reply = generate_response(req.user_input, req.history, req.persona, req.offer)
    return {"reply": reply}

class ScoreRequest(BaseModel):
    user_input: str
    history: str
    persona: str
    offer: str

@app.post("/score-call")
async def score_call_endpoint(req: ScoreRequest):
    result = score_call(req.history, req.persona, req.offer)
    return result

@app.post("/transcribe-audio")
async def transcribe_audio(file: UploadFile = File(...)):
    # Read the uploaded audio file
    audio_bytes = await file.read()
    # Save to a temporary file
    with open("temp_audio.wav", "wb") as f:
        f.write(audio_bytes)
    # Transcribe with AssemblyAI
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe("temp_audio.wav")
    return {"transcript": transcript.text}

@app.post("/start-session")
def start_session(persona: str = Form(...), offer: str = Form(...), history: str = Form("") ):
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "persona": persona,
        "offer": offer,
        "history": history,
        "active": True
    }
    return {"session_id": session_id}

@app.post("/transcribe-and-respond")
async def transcribe_and_respond(
    session_id: str = Form(...),
    file: UploadFile = File(...)
):
    # Check session
    if session_id not in sessions or not sessions[session_id]["active"]:
        return {"error": "Invalid or inactive session_id"}
    # Transcribe audio
    audio_bytes = await file.read()
    with open("temp_audio.wav", "wb") as f:
        f.write(audio_bytes)
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe("temp_audio.wav")
    user_input = transcript.text
    # Update history
    sessions[session_id]["history"] += f"\nUser: {user_input}\n"
    # Get AI response
    persona = sessions[session_id]["persona"]
    offer = sessions[session_id]["offer"]
    history = sessions[session_id]["history"]
    ai_reply = generate_response(user_input, history, persona, offer)
    sessions[session_id]["history"] += f"AI: {ai_reply}\n"
    return {"transcript": user_input, "ai_reply": ai_reply}

@app.post("/end-session")
def end_session(session_id: str = Form(...)):
    if session_id not in sessions:
        return {"error": "Invalid session_id"}
    session = sessions[session_id]
    persona = session["persona"]
    offer = session["offer"]
    history = session["history"]
    session["active"] = False
    result = score_call(history, persona, offer)
    title = generate_session_title(history, persona, offer)
    # Save to Supabase
    supabase.table("sessions").insert({
        "session_id": session_id,
        "persona": persona,
        "offer": offer,
        "history": history,
        "score": result.get("score"),
        "feedback": result.get("feedback"),
        "title": title,
        "created_at": int(time.time())
    }).execute()
    return {"score": result.get("score"), "feedback": result.get("feedback"), "title": title}

@app.get("/sessions")
def list_sessions():
    res = supabase.table("sessions").select("session_id, title, created_at, score").order("created_at", desc=True).execute()
    return res.data

@app.get("/session/{session_id}")
def get_session(session_id: str):
    res = supabase.table("sessions").select("*").eq("session_id", session_id).single().execute()
    return res.data

@app.post("/upload-call")
async def upload_call(
    file: UploadFile = File(...),
    persona: str = Form(...),
    offer: str = Form(...),
    history: str = Form("")
):
    import os
    filename = f"full_call{os.path.splitext(file.filename)[1]}"
    audio_bytes = await file.read()
    with open(filename, "wb") as f:
        f.write(audio_bytes)
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(filename)
    print("AssemblyAI transcript object:", transcript)
    print("Transcript text:", transcript.text)
    full_convo = f"{history}\n{transcript.text}"
    result = score_call(full_convo, persona, offer)
    return {
        "transcript": transcript.text,
        "score": result.get("score"),
        "feedback": result.get("feedback")
    }

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

@app.post("/tts")
def tts(text: str = Form(...)):
    url = "https://api.deepgram.com/v1/speak"
    headers = {
        "Authorization": f"Token {DEEPGRAM_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "model": "aura-asteria-en"  # You can change the model as needed
    }
    response = requests.post(url, headers=headers, json=payload, stream=True)
    if response.status_code != 200:
        return {"error": response.text}
    return StreamingResponse(response.raw, media_type="audio/mpeg")

ASSEMBLYAI_REALTIME_URL = "wss://api.assemblyai.com/v2/realtime/ws?sample_rate=16000"

sessions_ws = {}  # session_id: {"history": str, "persona": str, "offer": str}

@app.websocket("/ws/salescall")
async def salescall_ws(websocket: WebSocket):
    await websocket.accept()
    session_id = None
    assembly_ws = None
    try:
        # Receive initial session info
        init_data = await websocket.receive_json()
        session_id = init_data.get("session_id")
        persona = init_data.get("persona")
        offer = init_data.get("offer")
        sessions_ws[session_id] = {"history": "", "persona": persona, "offer": offer}

        # Connect to AssemblyAI real-time
        assembly_ws = await websockets.connect(
            ASSEMBLYAI_REALTIME_URL,
            extra_headers={"Authorization": AUDIO_API_KEY},
            ping_interval=5,
            ping_timeout=20
        )

        last_transcript = ""
        last_transcript_time = time.time()
        silence_threshold = 2.5  # seconds
        buffer = b""
        user_turn = b""

        async def send_audio():
            while True:
                data = await websocket.receive_bytes()
                await assembly_ws.send(base64.b64encode(data).decode("utf-8"))

        send_audio_task = asyncio.create_task(send_audio())

        while True:
            result = await assembly_ws.recv()
            msg = json.loads(result)
            if "text" in msg and msg["message_type"] == "FinalTranscript":
                transcript = msg["text"].strip()
                if transcript:
                    last_transcript = transcript
                    last_transcript_time = time.time()
                    # Append to history
                    sessions_ws[session_id]["history"] += f"\nUser: {transcript}\n"
                    await websocket.send_json({"transcript": transcript})
            # Detect silence
            if time.time() - last_transcript_time > silence_threshold and last_transcript:
                # User stopped speaking, get AI response
                persona = sessions_ws[session_id]["persona"]
                offer = sessions_ws[session_id]["offer"]
                history = sessions_ws[session_id]["history"]
                ai_reply = generate_response(last_transcript, history, persona, offer)
                sessions_ws[session_id]["history"] += f"AI: {ai_reply}\n"
                # Call TTS
                tts_response = requests.post(
                    "http://localhost:8000/tts",
                    data={"text": ai_reply},
                    stream=True
                )
                audio_bytes = tts_response.content if tts_response.status_code == 200 else None
                await websocket.send_json({
                    "ai_reply": ai_reply,
                    "ai_audio": base64.b64encode(audio_bytes).decode("utf-8") if audio_bytes else None
                })
                last_transcript = ""
                last_transcript_time = time.time()
            await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        pass
    finally:
        if assembly_ws:
            await assembly_ws.close()
        if session_id in sessions_ws:
            del sessions_ws[session_id]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
