import os
from typing import List, Dict
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from google import genai
from pydantic import BaseModel

# Load variables from .env file
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY is missing in the .env file!")

# Initialize FastAPI app and Google GenAI client
app = FastAPI(title="Gemini AI Chatbot API")
client = genai.Client(api_key=API_KEY)


# Data structures for handling API requests
class ChatMessage(BaseModel):
    role: str  # "user" or "model"
    content: str


class ChatRequest(BaseModel):
    user_message: str
    history: List[ChatMessage] = []


@app.get("/")
def health_check():
    return {"status": "ok", "message": "Gemini Chatbot API is running online!"}


@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        # Convert incoming conversation history into Gemini SDK format
        gemini_history = []
        for msg in request.history:
            # Gemini SDK expects "user" and "model" as roles
            gemini_role = "user" if msg.role == "user" else "model"
            gemini_history.append({
                "role": gemini_role,
                "parts": [{"text": msg.content}]
            })

        # Initialize chat session with past context using gemini-2.5-flash
        chat_session = client.chats.create(
            model="gemini-3.5-flash",
            history=gemini_history
        )

        # Send the latest message
        response = chat_session.send_message(request.user_message)

        return {"response": response.text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))