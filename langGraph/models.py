from typing import TypedDict

# State 정의 - 노드 간 공유되는 데이터
class NoticeState(TypedDict):
    raw_text: str           # 원본 텍스트
    refined_text: str       # 이모지 제거된 텍스트
    is_deadline: bool       # 마감 공지 여부
    emoji_dict: dict        # 이모지 매핑
    title: str              # 추출된 제목
    start_date: str         # 시작일
    end_date: str           # 종료일