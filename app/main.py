from fastapi import FastAPI
from contextlib import asynccontextmanager
from pydantic import BaseModel
from graph.main_graph import main_graph
from memory.database import init_database, get_schema
from mcp_server.tools import setup_schema_embeddings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    print("Initializing database...")
    init_database()

    print("Setting up Qdrant embeddings...")
    schema = get_schema()
    setup_schema_embeddings(schema)

    print("✅ All systems ready")
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
        "schema_context": None,
        "relevant_tables": None,
        "generated_sql": None,
        "sql_results": None,
        "date_context": None,
        "final_answer": None,
        "error": None,
    }

    result = await main_graph.ainvoke(initial_state)

    return {
        "session_id": request.session_id,
        "answer": result["final_answer"],
        "sql_used": result.get("generated_sql"),
        "language_detected": result["language"],
    }