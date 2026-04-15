from langdetect import detect
from app.llm import call_llm
from graph.state import GraphState

# ─────────────────────────────────────────
# NODE 1: detect_language
# ─────────────────────────────────────────
def detect_language_node(state: GraphState) -> GraphState:
    try:
        lang = detect(state["question"])
    except:
        lang = "en"
    state["language"] = lang
    return state

# ─────────────────────────────────────────
# NODE 2: rephrase_qtn
# ─────────────────────────────────────────
def rephrase_qtn_node(state: GraphState) -> GraphState:
    history = state.get("conversation_history", [])
    history_text = "\n".join(
        [f"{m['role']}: {m['content']}" for m in history[-4:]]
    ) or "No previous conversation."

    system = """You are a query clarification assistant.
Given conversation history and a user question, rewrite the question to be:
- Clear and unambiguous
- Self-contained (no pronouns like 'it', 'that', 'those')
- Specific about time periods if mentioned
Return ONLY the rewritten question, nothing else."""

    user = f"""Conversation history:
{history_text}

User question: {state['question']}

Rewritten question:"""

    state["rephrased_question"] = call_llm(system, user)
    return state

# ─────────────────────────────────────────
# NODE 3: question_decomposer
# ─────────────────────────────────────────
def question_decomposer_node(state: GraphState) -> GraphState:
    system = """You are a question decomposition assistant.
If the question has multiple parts, split into independent sub-questions.
If it's a single question, return it as-is.
Return ONLY a Python list of strings like: ["question 1", "question 2"]
No explanation, no markdown, just the list."""

    user = f"Question: {state['rephrased_question']}"

    result = call_llm(system, user)

    try:
        import ast
        questions = ast.literal_eval(result)
        if not isinstance(questions, list):
            questions = [state["rephrased_question"]]
    except:
        questions = [state["rephrased_question"]]

    state["decomposed_questions"] = questions
    return state

# ─────────────────────────────────────────
# NODE 4: classify_questions
# ─────────────────────────────────────────
def classify_questions_node(state: GraphState) -> GraphState:
    system = """Classify each question as one of: sql, general
- sql: needs database data (sales, products, revenue, counts, analytics)
- general: conversational, greetings, explanations

Return ONLY a Python list of dicts like:
[{"question": "...", "type": "sql"}, {"question": "...", "type": "general"}]
No explanation, no markdown."""

    user = f"Questions: {state['decomposed_questions']}"

    result = call_llm(system, user)

    try:
        import ast
        classified = ast.literal_eval(result)
    except:
        classified = [
            {"question": q, "type": "general"}
            for q in state["decomposed_questions"]
        ]

    state["question_types"] = classified
    return state

# ─────────────────────────────────────────
# NODE 5: narrative_ans
# ─────────────────────────────────────────
def narrative_ans_node(state: GraphState) -> GraphState:
    system = """You are a helpful data assistant.
Answer the user's question in a friendly, concise way.
If it's a greeting, respond warmly.
If it's a general knowledge question, answer directly."""

    user = state["rephrased_question"]
    state["final_answer"] = call_llm(system, user)
    return state

# ─────────────────────────────────────────
# NODE 6: update_conversation_history
# ─────────────────────────────────────────
def update_history_node(state: GraphState) -> GraphState:
    history = state.get("conversation_history", [])
    history.append({"role": "user", "content": state["question"]})
    history.append({"role": "assistant", "content": state.get("final_answer", "")})
    # Keep last 10 turns only
    state["conversation_history"] = history[-10:]
    return state

# ─────────────────────────────────────────
# ROUTER: decides which path after classify
# ─────────────────────────────────────────
def question_type_router(state: GraphState) -> str:
    types = state.get("question_types", [])
    if types and types[0]["type"] == "sql":
        return "sql"
    return "general"