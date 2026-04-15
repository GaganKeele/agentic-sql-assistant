from fastapi import FastAPI
from contextlib import asynccontextmanager
from pydantic import BaseModel

@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP — this runs before the app accepts requests
    print("Starting up...")
    print("App ready")
    yield
    # SHUTDOWN — this runs when app stops
    print("Shutting down...")

app = FastAPI(
    title="Agentic SQL Assistant",
    description="Natural language to SQL using LangGraph + ReAct",
    lifespan=lifespan
)

class ChatRequest(BaseModel):
    session_id: str
    question: str

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/chat")
async def chat(request: ChatRequest):
    # Placeholder — we'll wire LangGraph here on Day 2
    return {
        "session_id": request.session_id,
        "answer": f"Echo: {request.question}"
    }