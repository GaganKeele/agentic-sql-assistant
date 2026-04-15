from fastapi import FastAPI
from contextlib import asynccontextmanager
from pydantic import BaseModel
from graph.main_graph import main_graph

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("✅ LangGraph loaded")
    yield
    print("Shutting down...")

app = FastAPI(title="Agentic SQL Assistant", lifespan=lifespan)

class ChatRequest(BaseModel):
    session_id: str
    question: str

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/chat")
async def chat(request: ChatRequest):
    initial_state = {
        "question": request.question,
        "session_id": request.session_id,
        "conversation_history": [],
        "language": None,
        "rephrased_question": None,
        "decomposed_questions": None,
        "question_types": None,
        "final_answer": None,
    }

    result = await main_graph.ainvoke(initial_state)

    return {
        "session_id": request.session_id,
        "answer": result["final_answer"],
        "language_detected": result["language"],
        "rephrased_as": result["rephrased_question"]
    }