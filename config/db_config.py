import pymysql
import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수 불러오기
load_dotenv()

# MySQL 연결 설정
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "financial_db"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "cursorclass": pymysql.cursors.DictCursor,  # 결과를 딕셔너리 형태로 반환
}


def get_db_connection():
    """MySQL 데이터베이스 연결을 반환하는 함수 (PyMySQL)"""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        print("✅ MySQL 데이터베이스 연결 성공!")
        return conn
    except pymysql.MySQLError as err:
        print(f"❌ MySQL 연결 실패: {err}")
        return None


if __name__ == "__main__":
    # 테스트: DB 연결 확인
    connection = get_db_connection()
    if connection:
        connection.close()
