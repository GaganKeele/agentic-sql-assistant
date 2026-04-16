from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
import os, json
from dotenv import load_dotenv

load_dotenv()

# Module-level clients (loaded once)
qdrant = QdrantClient(
    host=os.getenv("QDRANT_HOST", "localhost"),
    port=int(os.getenv("QDRANT_PORT", 6333))
)
embedder = SentenceTransformer("all-MiniLM-L6-v2")

COLLECTION = "schema_info"

# ─────────────────────────────────────────
# TOOL 1: date_context
# ─────────────────────────────────────────
def date_context(question: str) -> dict:
    """Resolves relative dates in questions"""
    today = date.today()
    last_month = today - relativedelta(months=1)

    return {
        "today": str(today),
        "current_month": today.strftime("%B %Y"),
        "last_month": last_month.strftime("%B %Y"),
        "last_month_start": str(last_month.replace(day=1)),
        "last_month_end": str(today.replace(day=1) - relativedelta(days=1)),
        "current_year": today.year,
        "last_year": today.year - 1,
    }

# ─────────────────────────────────────────
# TOOL 2: setup_schema_embeddings
# ─────────────────────────────────────────
def setup_schema_embeddings(schema: dict):
    """Store schema embeddings in Qdrant on startup"""
    # Create collection if not exists
    collections = [c.name for c in qdrant.get_collections().collections]

    if COLLECTION in collections:
        qdrant.delete_collection(COLLECTION)

    qdrant.create_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE)
    )

    # Embed each table
    points = []
    for i, (table_name, columns) in enumerate(schema.items()):
        col_text = ", ".join([f"{c['name']} ({c['type']})" for c in columns])
        text = f"Table: {table_name}. Columns: {col_text}"
        vector = embedder.encode(text).tolist()

        points.append(PointStruct(
            id=i,
            vector=vector,
            payload={
                "table": table_name,
                "columns": columns,
                "description": text
            }
        ))

    qdrant.upsert(collection_name=COLLECTION, points=points)
    print(f"✅ Embedded {len(points)} tables into Qdrant")

# ─────────────────────────────────────────
# TOOL 3: agentic_rag
# ─────────────────────────────────────────
def agentic_rag(query: str, limit: int = 3) -> list:
    """Find relevant tables using semantic search"""
    query_vector = embedder.encode(query).tolist()

    results = qdrant.query_points(          # ← changed from .search()
        collection_name=COLLECTION,
        query=query_vector,                 # ← changed from query_vector=
        limit=limit
    ).points                                # ← add .points at the end

    return [
        {
            "table": r.payload["table"],
            "columns": r.payload["columns"],
            "score": r.score
        }
        for r in results
    ]
# ─────────────────────────────────────────
# TOOL 4: sql_generation
# ─────────────────────────────────────────
def sql_generation(question: str, relevant_tables: list, date_info: dict, llm_fn) -> str:
    """Generate SQL from question using schema context"""
    schema_text = ""
    for t in relevant_tables:
        cols = ", ".join([f"{c['name']} {c['type']}" for c in t["columns"]])
        schema_text += f"Table {t['table']}({cols})\n"

    prompt = f"""You are a SQL expert. Generate a SQLite SQL query.

Schema:
{schema_text}

Date context:
- Today: {date_info['today']}
- Last month: {date_info['last_month']} ({date_info['last_month_start']} to {date_info['last_month_end']})
- Current year: {date_info['current_year']}

Question: {question}

Rules:
- Return ONLY the SQL query, no explanation
- Use proper SQLite syntax
- For "last month" use dates: {date_info['last_month_start']} to {date_info['last_month_end']}
- Always use table aliases for clarity

SQL:"""

    return llm_fn(
        system_prompt="You are a SQL expert. Return only valid SQLite SQL, nothing else.",
        user_message=prompt
    )

# ─────────────────────────────────────────
# TOOL 5: sql_execution
# ─────────────────────────────────────────
def sql_execution(sql: str) -> dict:
    """Execute SQL safely and return results"""
    from memory.database import execute_query

    # Basic safety check
    sql_upper = sql.upper().strip()
    if any(word in sql_upper for word in ["DROP", "DELETE", "INSERT", "UPDATE", "ALTER"]):
        return {"error": "Only SELECT queries are allowed", "results": []}

    try:
        results = execute_query(sql)
        return {"results": results, "row_count": len(results), "error": None}
    except Exception as e:
        return {"error": str(e), "results": []}