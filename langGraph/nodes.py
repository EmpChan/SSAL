# nodes.py
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from models import NoticeState
import json, re

llm = ChatOllama(
    model="qwen2.5:7b",
    temperature=0,
    num_ctx=2048,
    num_predict=256,
)

# ① 텍스트 정제 (이모지 제거)
def refine_text_node(state: NoticeState):
    text = state["raw_text"]
    refined = re.sub(r'[^\w\s\.\,\!\?\:\-\(\)가-힣]', '', text)
    return {"refined_text": refined}

# nodes.py - remind_check_node 수정

def remind_check_node(state: NoticeState):
    prompt = ChatPromptTemplate.from_template(
        "아래 공지를 읽고 '마감 임박 알림' 인지 판단해.\n"
        "마감 임박 알림이란: 제출 마감, 신청 마감, 오늘까지, 오늘 마감, D-day 등 긴박한 마감을 강조하는 공지야.\n"
        "일반 모집 공고, 행사 안내, 일정 공유는 해당 안 돼.\n\n"
        "반드시 true 또는 false 만 출력해. 다른 말 절대 하지마.\n\n"
        "공지: {text}"
    )
    chain = prompt | llm
    result = chain.invoke({"text": state["refined_text"]})
    raw = result.content.strip().lower()
    print(f"  [remind_check 원본 응답]: '{raw}'")  # 디버깅용
    is_deadline = raw == "true"  # 정확히 "true"일 때만
    return {"is_deadline": is_deadline}

# ③ 대제목 추출 노드
def extract_title_node(state: NoticeState):
    prompt = ChatPromptTemplate.from_template(
        "공지사항의 핵심 제목을 한 줄로만 출력해. 다른 말 하지마.\n\n"
        "공지: {text}"
    )
    chain = prompt | llm
    result = chain.invoke({"text": state["refined_text"]})
    return {"title": result.content.strip()}

# ④ 기간 추출 노드
def extract_dates_node(state: NoticeState):
    prompt = ChatPromptTemplate.from_template(
        "공지에서 시작일과 종료일을 추출해.\n"
        "반드시 JSON만 출력해: {{\"start_date\": \"YYYY-MM-DD\", \"end_date\": \"YYYY-MM-DD\"}}\n"
        "날짜가 없으면 null로 해.\n\n"
        "공지: {text}"
    )
    chain = prompt | llm
    result = chain.invoke({"text": state["refined_text"]})
    clean = re.sub(r"```json|```", "", result.content).strip()
    dates = json.loads(clean)
    return {
        "start_date": dates.get("start_date"),
        "end_date": dates.get("end_date")
    }

# ⑤ DB 저장
def save_to_db_node(state: NoticeState):
    print(f"\n✅ DB 저장: {state}")
    return {}