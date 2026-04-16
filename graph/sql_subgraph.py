from langgraph.graph import StateGraph, END
from graph.state import GraphState
from mcp_server.tools import date_context, agentic_rag, sql_generation, sql_execution
from app.llm import call_llm

MAX_RETRIES = 3

def get_schema_context_node(state: GraphState) -> GraphState:
    """Load schema if not already in state"""
    if not state.get("schema_context"):
        from memory.database import get_schema
        state["schema_context"] = get_schema()
    return state

def react_node(state: GraphState) -> GraphState:
    """ReAct loop: Supervisor plans, Executor runs tools"""
    question = state["rephrased_question"]
    retries = 0

    # Step 1: Get date context
    date_info = date_context(question)
    state["date_context"] = date_info

    # Step 2: Find relevant tables (RAG)
    relevant_tables = agentic_rag(question)
    state["relevant_tables"] = relevant_tables

    # Step 3: Generate + Execute SQL with retries
    last_error = None
    while retries < MAX_RETRIES:
        # Generate SQL
        sql = sql_generation(question, relevant_tables, date_info, call_llm)
        sql = sql.strip().strip("```sql").strip("```").strip()
        state["generated_sql"] = sql

        # Execute SQL
        result = sql_execution(sql)

        if result["error"]:
            last_error = result["error"]
            retries += 1

            # Re-plan: ask LLM to fix the SQL
            fix_prompt = f"""The SQL query failed with error: {result['error']}
            
Original question: {question}
Failed SQL: {sql}

Fix the SQL query. Return ONLY the corrected SQL."""

            sql = call_llm(
                "You are a SQL expert. Fix the broken SQL query. Return only valid SQLite SQL.",
                fix_prompt
            )
            continue

        # Success — format the answer
        state["sql_results"] = result["results"]
        state["final_answer"] = format_sql_answer(
            question, result["results"], sql
        )
        state["error"] = None
        return state

    # All retries failed → ask for clarification
    state["error"] = last_error
    state["final_answer"] = f"I couldn't retrieve that data. Could you clarify your question? (Error: {last_error})"
    return state

def format_sql_answer(question: str, results: list, sql: str) -> str:
    """Use LLM to format results as natural language"""
    if not results:
        return "No data found for your query."

    results_text = str(results[:10])  # Limit to 10 rows

    return call_llm(
        system_prompt="You are a helpful data analyst. Format query results as a clear, concise answer.",
        user_message=f"""Question: {question}
        
Query results: {results_text}

Write a clear, natural language answer based on these results:"""
    )

def create_sql_subgraph():
    builder = StateGraph(GraphState)

    builder.add_node("get_schema_context", get_schema_context_node)
    builder.add_node("to_react", react_node)

    builder.set_entry_point("get_schema_context")
    builder.add_edge("get_schema_context", "to_react")
    builder.add_edge("to_react", END)

    return builder.compile()

sql_subgraph = create_sql_subgraph()