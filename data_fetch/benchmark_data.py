import os
import sys
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from database.models import Base, BenchmarkIndex
from config.db_config import get_db_url

# 데이터베이스 연결 설정
db_url = get_db_url()
engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
session = Session()

# 벤치마크 지수 정보 정의
benchmark_indices = [
    {
        "index_name": "KOSPI",
        "index_symbol": "KOSPI",
        "country": "KR",
        "description": "한국 종합주가지수",
    },
    {
        "index_name": "KOSDAQ",
        "index_symbol": "KOSDAQ",
        "country": "KR",
        "description": "한국 코스닥지수",
    },
    {
        "index_name": "S&P 500",
        "index_symbol": "^GSPC",
        "country": "US",
        "description": "미국 S&P 500 지수",
    },
    {
        "index_name": "NASDAQ",
        "index_symbol": "^IXIC",
        "country": "US",
        "description": "미국 NASDAQ 종합지수",
    },
    {
        "index_name": "DOW JONES",
        "index_symbol": "^DJI",
        "country": "US",
        "description": "미국 다우존스 산업평균지수",
    },
]

# 데이터베이스에 지수 정보 추가 또는 업데이트
for index_data in benchmark_indices:
    index = (
        session.query(BenchmarkIndex)
        .filter_by(index_symbol=index_data["index_symbol"])
        .first()
    )
    if index:
        # 기존 지수 정보 업데이트
        index.index_name = index_data["index_name"]
        index.country = index_data["country"]
        index.description = index_data["description"]
        print(f"기존 지수 정보 업데이트: {index.index_name}")
    else:
        # 새로운 지수 정보 추가
        new_index = BenchmarkIndex(
            index_name=index_data["index_name"],
            index_symbol=index_data["index_symbol"],
            country=index_data["country"],
            description=index_data["description"],
        )
        session.add(new_index)
        print(f"새로운 지수 정보 추가: {index_data['index_name']}")

# 변경 사항 커밋
session.commit()
print("벤치마크 지수 정보가 성공적으로 데이터베이스에 저장되었습니다.")
