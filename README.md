# 🤖 Agentic SQL Assistant

> **Ask questions in plain English. Get SQL-powered answers instantly.**
> Zero SQL knowledge required.

[![CI/CD Pipeline](https://github.com/GaganKeele/agentic-sql-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/GaganKeele/agentic-sql-assistant/actions)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-multi--node-green.svg)](https://langchain-ai.github.io/langgraph/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://hub.docker.com/r/gagankeele/agentic-sql-assistant)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🎯 What It Does

| User asks | System does | User gets |
|---|---|---|
| *"What were total sales last month?"* | Detects dates → finds schema → generates SQL → executes | *"Total sales in March 2026: ₹1,24,975"* |
| *"Which product earns the most?"* | RAG retrieves relevant tables → builds JOIN query | *"ML Model Training Kit — ₹87,989 total revenue"* |
| *"How are you?"* | Routes to narrative node (no SQL needed) | *"I'm great! Ask me about your sales data."* |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                   User (Streamlit UI)                │
└─────────────────────────┬───────────────────────────┘
                          │ HTTP POST /chat
┌─────────────────────────▼───────────────────────────┐
│              FastAPI Route Handler                   │
│         (guardrails → context → state)               │
└─────────────────────────┬───────────────────────────┘
                          │ graph.ainvoke(state)
┌─────────────────────────▼───────────────────────────┐
│               LangGraph Main Graph                   │
│                                                      │
│  detect_language → rephrase_qtn → decompose          │
│                                       │              │
│                              classify_questions      │
│                             ↙                ↘       │
│                    SQL Subgraph          narrative   │
│                    (ReAct Agent)           _ans      │
│                         │                    │       │
│                    to_indic ←────────────────┘       │
│                         │                            │
│               update_conversation_history            │
└─────────────────────────┬───────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────┐
│              SQL Subgraph (ReAct Loop)               │
│                                                      │
│  get_schema_context → schema_embedding → to_ReAct    │
│                                                      │
│  ┌─────────────────────────────────────────────┐     │
│  │           SUPERVISOR                        │     │
│  │  Plan → Monitor → Re-plan on error          │     │
│  └──────────────────┬──────────────────────────┘     │
│                     │ Commands                        │
│  ┌──────────────────▼──────────────────────────┐     │
│  │           EXECUTOR (MCP Tools)              │     │
│  │  📅 date_context  → resolve "last month"    │     │
│  │  🔍 agentic_rag   → find relevant tables    │     │
│  │  ✏️  sql_generation → write SQL query        │     │
│  │  ⚡ sql_execution  → run on SQLite           │     │
│  └─────────────────────────────────────────────┘     │
│                                                      │
│         ↓ success          ↓ fail (max 3 retries)    │
│        END             human_assistance              │
└──────────────────────────────────────────────────────┘
```

---

## ⚡ Tech Stack

| Layer | Technology |
|---|---|
| **Orchestration** | LangGraph (StateGraph, multi-node, subgraphs) |
| **LLM** | Groq API (`llama-3.3-70b-versatile`) |
| **Vector Search** | Qdrant (hybrid dense + sparse embeddings) |
| **Embeddings** | `sentence-transformers/all-MiniLM-L6-v2` |
| **Tool Protocol** | MCP (Model Context Protocol) |
| **Backend** | FastAPI + Uvicorn |
| **Database** | SQLite (via `memory/database.py`) |
| **UI** | Streamlit |
| **CI/CD** | GitHub Actions → Docker Hub |
| **Containerization** | Docker + Docker Compose |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker Desktop
- Groq API key (free at [console.groq.com](https://console.groq.com))

### 1. Clone & Setup
```bash
git clone https://github.com/GaganKeele/agentic-sql-assistant.git
cd agentic-sql-assistant

python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Environment Variables
```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

### 3. Start Qdrant
```bash
docker-compose up -d
```

### 4. (Optional) Populate Rich Sample Data
```bash
python database_update.py
# Loads 100 sales records, 15 customers, 10 products
```

### 5. Run the API
```bash
uvicorn app.main:app --reload
```
API docs available at: `http://localhost:8000/docs`

### 6. Run the UI
```bash
# In a new terminal
streamlit run streamlit_app.py
```
Chat UI at: `http://localhost:8501`

---

## 💬 Example Questions to Try

```
"What are the total sales for last month?"
"Which product has the highest revenue?"
"Show me sales by customer segment"
"How many completed orders do we have?"
"Who are our top 5 customers by sales amount?"
"What is the monthly revenue trend for 2025?"
"Show pending orders"
"Which city has the most customers?"
```

---

## 📁 Project Structure

```
agentic-sql-assistant/
│
├── app/
│   ├── main.py           # FastAPI app + lifespan (DB + Qdrant init)
│   └── llm.py            # Groq LLM client (module-level, loaded once)
│
├── graph/
│   ├── state.py          # GraphState TypedDict definition
│   ├── nodes.py          # All 6 main graph nodes
│   ├── main_graph.py     # LangGraph main workflow
│   └── sql_subgraph.py   # ReAct SQL agent subgraph
│
├── mcp_server/
│   └── tools.py          # MCP tools: date_context, agentic_rag,
│                         #            sql_generation, sql_execution
│
├── memory/
│   └── database.py       # SQLite init, schema fetch, query execution
│
├── tests/
│   ├── test_nodes.py     # 8 node tests (no API key needed)
│   └── test_tools.py     # 5 tool tests (SQLite only)
│
├── .github/
│   └── workflows/
│       └── ci.yml        # CI: pytest → Docker build → Docker Hub push
│
├── streamlit_app.py      # Chat UI with SQL transparency
├── docker-compose.yml    # Qdrant vector database
├── Dockerfile            # App containerization
├── database_update.py    # Rich sample data loader
└── requirements.txt
```

---

## 🔄 CI/CD Pipeline

```
Push to main branch
        │
        ▼
┌───────────────────┐
│  Run Tests (CI)   │  ← pytest 13 tests, no API key needed
│  ubuntu-latest    │
└────────┬──────────┘
         │ ✅ All pass
         ▼
┌───────────────────┐
│  Build Docker     │  ← Only runs if tests pass
│  Image (CD)       │  ← Only runs on main branch
└────────┬──────────┘
         │
         ▼
  Docker Hub Push
  gagankeele/agentic-sql-assistant:latest
  gagankeele/agentic-sql-assistant:<commit-sha>
```

---

## 🧠 Key Design Decisions

**1. MCP Tools in Separate Process**
MCP servers require their own event loop. Running in a separate process prevents conflicts with FastAPI's async runtime and allows independent restarts.

**2. LLM at Module Level**
The Groq client is loaded once at startup (`app/llm.py`), not per-request. This eliminates repeated initialization latency across all graph nodes.

**3. Hybrid Qdrant Search**
Schema embeddings use both dense vectors (semantic similarity) and sparse vectors (keyword matching) for more accurate table retrieval than either approach alone.

**4. Fresh Embeddings on Startup**
Qdrant indices are deleted and rebuilt on every startup. This ensures schema changes are always reflected without manual cache invalidation.

**5. ReAct with Auto-Recovery**
The SQL agent retries up to 3 times on failure, with the supervisor LLM analyzing the error and replanning before each retry.

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

```
tests/test_nodes.py::test_detect_language_english          PASSED
tests/test_nodes.py::test_detect_language_sets_field       PASSED
tests/test_nodes.py::test_router_returns_sql               PASSED
tests/test_nodes.py::test_router_returns_general           PASSED
tests/test_nodes.py::test_router_defaults_to_general       PASSED
tests/test_nodes.py::test_update_history_appends_turns     PASSED
tests/test_nodes.py::test_update_history_max_10_turns      PASSED
tests/test_nodes.py::test_graph_state_has_required_keys    PASSED
tests/test_tools.py::test_date_context_has_required_keys   PASSED
tests/test_tools.py::test_date_context_last_month_format   PASSED
tests/test_tools.py::test_sql_execution_blocks_dangerous   PASSED
tests/test_tools.py::test_sql_execution_select_works       PASSED
tests/test_tools.py::test_get_schema_returns_tables        PASSED

13 passed in 0.73s
```

---

## 🛡️ Security

- Only `SELECT` queries are permitted — `DROP`, `DELETE`, `INSERT`, `UPDATE` are blocked at execution level
- API keys stored in `.env` (never committed — see `.gitignore`)
- Input validation via Pydantic models on all endpoints

---

## 📈 Planned Improvements

- [ ] Counter subgraph (sales scenario follow-up questions)
- [ ] Indic language support (IndicTrans2 translation nodes)
- [ ] PostgreSQL support (production database)
- [ ] Conversation memory persistence across sessions
- [ ] NVIDIA Nemo guardrails integration
- [ ] Multi-tenant session management

---

## 👤 Author

**Gagan K** — AI Engineer  
[GitHub](https://github.com/GaganKeele) · [LinkedIn](https://linkedin.com/in/gagan-ka282b7232) · gagankeele99@gmail.com

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.