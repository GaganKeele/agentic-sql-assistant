from typing import TypedDict, Optional, List

class GraphState(TypedDict):
    question: str
    session_id: str
    conversation_history: List[dict]
    language: Optional[str]
    rephrased_question: Optional[str]
    decomposed_questions: Optional[List[str]]
    question_types: Optional[List[dict]]
    sql_results: Optional[list]
    answer: Optional[str]
    final_answer: Optional[str]
    error: Optional[str]


    