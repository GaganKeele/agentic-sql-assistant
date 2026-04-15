from langgraph.graph import StateGraph, END
from graph.state import GraphState
from graph.nodes import (
    detect_language_node,
    rephrase_qtn_node,
    question_decomposer_node,
    classify_questions_node,
    narrative_ans_node,
    update_history_node,
    question_type_router
)

def create_main_graph():
    builder = StateGraph(GraphState)

    # Add all nodes
    builder.add_node("detect_language", detect_language_node)
    builder.add_node("rephrase_qtn", rephrase_qtn_node)
    builder.add_node("question_decomposer", question_decomposer_node)
    builder.add_node("classify_questions", classify_questions_node)
    builder.add_node("narrative_ans", narrative_ans_node)
    builder.add_node("update_history", update_history_node)

    # Entry point
    builder.set_entry_point("detect_language")

    # Linear edges
    builder.add_edge("detect_language", "rephrase_qtn")
    builder.add_edge("rephrase_qtn", "question_decomposer")
    builder.add_edge("question_decomposer", "classify_questions")

    # Conditional routing after classify
    builder.add_conditional_edges(
        "classify_questions",
        question_type_router,
        {
            "sql": "narrative_ans",      # Day 3: replace with sql_subgraph
            "general": "narrative_ans"
        }
    )

    builder.add_edge("narrative_ans", "update_history")
    builder.add_edge("update_history", END)

    return builder.compile()

# Compile once at module level
main_graph = create_main_graph()