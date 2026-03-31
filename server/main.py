from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.pool import StaticPool
from pydantic import BaseModel, ConfigDict
from datetime import datetime, timezone
from typing import Optional

# ==========================================
# 1. 데이터베이스 설정 (In-Memory SQLite)
# ==========================================
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==========================================
# 2. SQLAlchemy ORM 모델 (DB 테이블 구조)
# ==========================================
class Notice(Base):
    __tablename__ = "notices"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)

    # 💡 수정: 서버 구동 시간이 아닌, 데이터가 들어가는 시점의 시간을 계산하도록 lambda 사용
    createdAt = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    startTime = Column(DateTime, nullable=False, index=True)
    endTime = Column(DateTime, nullable=False, index=True)

Base.metadata.create_all(bind=engine)

# ==========================================
# 3. Pydantic 스키마 (데이터 검증 및 직렬화)
# ==========================================
class NoticeCreate(BaseModel):
    title: str
    content: str
    # 💡 수정: 프론트엔드에서 createdAt을 보내지 않아도 DB가 알아서 생성함
    startTime: datetime
    endTime: datetime

class NoticeResponse(BaseModel):
    id: int
    title: str
    content: str
    createdAt: datetime
    startTime: datetime
    endTime: datetime

    # 💡 수정: SQLAlchemy 모델을 Pydantic으로 변환하기 위한 필수 설정!
    model_config = ConfigDict(from_attributes=True)

# ==========================================
# 4. FastAPI 애플리케이션 및 의존성 주입
# ==========================================
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==========================================
# 5. API 엔드포인트 (라우터)
# ==========================================
@app.post("/notices/", response_model=NoticeResponse)
def create_notice(notice: NoticeCreate, db: Session = Depends(get_db)):
    new_notice = Notice(
        title=notice.title,
        content=notice.content,
        # createdAt은 제외 (DB가 자동 생성)
        startTime=notice.startTime,
        endTime=notice.endTime,
    )

    db.add(new_notice)
    db.commit()
    db.refresh(new_notice)
    return new_notice

@app.get("/notices/", response_model=list[NoticeResponse])
def read_notices(
    year: Optional[int] = None, 
    month: Optional[int] = None, 
    skip: int = 0, 
    limit: int = 500, 
    db: Session = Depends(get_db)
):
    query = db.query(Notice)

    if year is not None and month is not None:
        calendar_start = datetime(year, month, 1)
        
        if month == 12:
            next_year = year + 1
            next_month = 1
        else:
            next_year = year
            next_month = month + 1
            
        calendar_end = datetime(next_year, next_month, 1)

        query = query.filter(
            Notice.endTime >= calendar_start,
            Notice.startTime < calendar_end
        )

    notices = query.offset(skip).limit(limit).all()
    return notices

# 터미널에서 `python 파일명.py`로 바로 실행하기 위한 코드
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)