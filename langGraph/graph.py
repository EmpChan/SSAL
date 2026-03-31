# graph.py
from langgraph.graph import StateGraph, END
from langGraph.models import NoticeState
from langGraph.nodes import (
    refine_text_node,
    remind_check_node,
    extract_title_node,
    extract_dates_node,
    save_to_db_node,
)

def route_after_remind(state: NoticeState):
    if state["is_deadline"]:
        return "save_db"      # true → 바로 저장
    return "extract_title"    # false → 추출 시작

def build_graph():
    workflow = StateGraph(NoticeState)

    # 노드 등록
    workflow.add_node("refine_text", refine_text_node)
    workflow.add_node("remind_check", remind_check_node)
    workflow.add_node("extract_title", extract_title_node)
    workflow.add_node("extract_dates", extract_dates_node)
    workflow.add_node("save_db", save_to_db_node)

    # 흐름 연결
    workflow.set_entry_point("refine_text")
    workflow.add_edge("refine_text", "remind_check")

    workflow.add_conditional_edges(
        "remind_check",
        route_after_remind,
        {
            "save_db": "save_db",
            "extract_title": "extract_title",
        }
    )

    workflow.add_edge("extract_title", "extract_dates")
    workflow.add_edge("extract_dates", "save_db")
    workflow.add_edge("save_db", END)

    return workflow.compile()

app = build_graph()