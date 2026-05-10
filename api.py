import os
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Ensure the project source is importable
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "src"))

from chatbot import GLAChatbot
from embedder import index_exists
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(
    title="GLA Admission Chatbot API",
    description="REST API for the GLA University chatbot frontend.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    retrieval_mode: str = "faiss"
    show_sources: bool = False

class ChatResponse(BaseModel):
    answer: str
    sources: list[str] = []

chatbots: dict[str, GLAChatbot] = {}


def get_chatbot(retrieval_mode: str = "faiss") -> GLAChatbot:
    normalized_mode = retrieval_mode.lower() if retrieval_mode else "faiss"
    if normalized_mode not in chatbots:
        chatbots[normalized_mode] = GLAChatbot(
            retrieval_mode=normalized_mode,
            supermemory_api_key=os.getenv("SUPERMEMORY_API_KEY"),
        )
    return chatbots[normalized_mode]


@app.on_event("startup")
def startup_event():
    if not index_exists("vector_store"):
        raise RuntimeError(
            "Vector store not found. Run `python scripts/ingest.py` before using the API."
        )


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "GLA Admission Chatbot API is running."}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="The message may not be empty.")

    if not index_exists("vector_store"):
        raise HTTPException(
            status_code=503,
            detail="Vector store not found. Run `python scripts/ingest.py` first.",
        )

    bot = get_chatbot(request.retrieval_mode)

    if request.show_sources:
        result = bot.ask_with_sources(request.message)
        return ChatResponse(answer=result["answer"], sources=result["sources"])

    answer = bot.ask(request.message)
    return ChatResponse(answer=answer, sources=[])
