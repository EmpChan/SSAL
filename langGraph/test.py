# test.py
from graph import app

# 테스트 케이스 1 - 일반 공지 (title, date 추출)
test_normal = {
    "raw_text": "📢 2024 동계 프로젝트 참가자 모집!\n신청 기간: 2024-12-01 ~ 2024-12-15\n관심 있는 분들은 구글폼 작성 바랍니다.",
    "refined_text": "",
    "is_deadline": False,
    "title": None,
    "start_date": None,
    "end_date": None,
}

# 테스트 케이스 2 - 마감 공지 (바로 save_db)
test_deadline = {
    "raw_text": "⚠️ 오늘 오후 6시 최종 제출 마감입니다. 서두르세요!",
    "refined_text": "",
    "is_deadline": False,
    "title": None,
    "start_date": None,
    "end_date": None,
}

print("=" * 50)
print("📌 테스트 1: 일반 공지")
print("=" * 50)
result1 = app.invoke(test_normal)
print(f"제목: {result1['title']}")
print(f"시작일: {result1['start_date']}")
print(f"종료일: {result1['end_date']}")

print("\n" + "=" * 50)
print("📌 테스트 2: 마감 공지")
print("=" * 50)
result2 = app.invoke(test_deadline)
print(f"마감공지 여부: {result2['is_deadline']}")