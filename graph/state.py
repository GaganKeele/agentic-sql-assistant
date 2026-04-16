from typing import TypedDict, Optional, List

class GraphState(TypedDict):
    question: str
    session_id: str
    conversation_history: List[dict]
    language: Optional[str]
    rephrased_question: Optional[str]
    decomposed_questions: Optional[List[str]]
    question_types: Optional[List[dict]]
    schema_context: Optional[dict]
    relevant_tables: Optional[list]
    generated_sql: Optional[str]
    sql_results: Optional[list]
    date_context: Optional[dict]
    final_answer: Optional[str]
    error: Optional[str]