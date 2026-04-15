def test_health_check():
    """Sanity check — always passes, confirms test setup works"""
    assert True

def test_graph_state_keys():
    """Verify GraphState has the fields we need"""
    from graph.state import GraphState
    required_keys = [
        "question", "session_id", "conversation_history",
        "language", "rephrased_question", "final_answer"
    ]
    # GraphState is a TypedDict — check its annotations
    state_keys = GraphState.__annotations__.keys()
    for key in required_keys:
        assert key in state_keys, f"Missing key: {key}"