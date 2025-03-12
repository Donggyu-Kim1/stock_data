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
    """PyMySQL을 사용하여 MySQL 데이터베이스 연결을 반환"""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        print("✅ MySQL 데이터베이스 연결 성공!")
        return conn
    except pymysql.MySQLError as err:
        print(f"❌ MySQL 연결 실패: {err}")
        return None


def get_db_url():
    """SQLAlchemy에서 사용할 수 있는 MySQL 데이터베이스 URL을 반환"""
    return f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"


if __name__ == "__main__":
    # 테스트: PyMySQL DB 연결 확인
    connection = get_db_connection()
    if connection:
        connection.close()

    # 테스트: SQLAlchemy DB URL 출력
    print("✅ SQLAlchemy DB URL:", get_db_url())
