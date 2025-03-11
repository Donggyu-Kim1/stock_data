from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# MySQL 연결 URL 생성 (PyMySQL 사용)
DATABASE_URL = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

# SQLAlchemy 엔진 생성
engine = create_engine(DATABASE_URL, echo=True)


# 데이터베이스 테이블 생성 함수
def create_tables():
    Base.metadata.create_all(engine)
    print("✅ 모든 테이블이 성공적으로 생성되었습니다!")


if __name__ == "__main__":
    create_tables()
