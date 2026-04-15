from graph.state import GraphState
from graph.nodes import (
    detect_language_node,
    question_type_router,
    update_history_node,
    classify_questions_node
)

def make_state(**kwargs) -> GraphState:
    """Helper to make a minimal valid state"""
    base = {
        "question": "test question",
        "session_id": "test_session",
        "conversation_history": [],
        "language": None,
        "rephrased_question": "test question",
        "decomposed_questions": ["test question"],
        "question_types": None,
        "sql_results": None,
        "answer": None,
        "final_answer": None,
        "error": None,
    }
    base.update(kwargs)
    return base

# ── Tests that need NO API key ──────────────────────

def test_detect_language_english():
    state = make_state(question="What are the total sales?")
    result = detect_language_node(state)
    assert result["language"] == "en"

def test_detect_language_sets_field():
    state = make_state(question="hello")
    result = detect_language_node(state)
    assert "language" in result
    assert result["language"] is not None

def test_router_returns_sql():
    state = make_state(question_types=[{"question": "sales?", "type": "sql"}])
    assert question_type_router(state) == "sql"

def test_router_returns_general():
    state = make_state(question_types=[{"question": "hi", "type": "general"}])
    assert question_type_router(state) == "general"

def test_router_defaults_to_general_when_empty():
    state = make_state(question_types=[])
    assert question_type_router(state) == "general"

def test_update_history_appends_turns():
    state = make_state(
        question="What is revenue?",
        conversation_history=[],
        final_answer="Revenue is $100"
    )
    result = update_history_node(state)
    assert len(result["conversation_history"]) == 2
    assert result["conversation_history"][0]["role"] == "user"
    assert result["conversation_history"][1]["role"] == "assistant"

def test_update_history_max_10_turns():
    # Start with 10 existing messages
    existing = [{"role": "user", "content": f"msg{i}"} for i in range(10)]
    state = make_state(
        question="new question",
        conversation_history=existing,
        final_answer="new answer"
    )
    result = update_history_node(state)
    assert len(result["conversation_history"]) <= 10

def test_graph_state_has_required_keys():
    required = ["question", "session_id", "conversation_history",
                "language", "rephrased_question", "final_answer"]
    for key in required:
        assert key in GraphState.__annotations__