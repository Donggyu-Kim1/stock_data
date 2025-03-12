import os
import pandas as pd
import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from database.models import BenchmarkIndex, BenchmarkPrice, Base
from config.db_config import get_db_url

# 데이터 수집 라이브러리
from pykrx import stock  # 한국 지수
import yfinance as yf  # 미국 지수

# 데이터베이스 연결 설정
db_url = get_db_url()
engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
session = Session()

# 📌 1️⃣ 벤치마크 지수 목록 조회
benchmark_indices = session.query(BenchmarkIndex).all()
if not benchmark_indices:
    print(
        "❌ 벤치마크 지수 데이터가 존재하지 않습니다. benchmark_data.py를 먼저 실행하세요."
    )
    exit()

# 📌 2️⃣ 벤치마크 지수별 데이터 수집
for benchmark in benchmark_indices:
    index_symbol = benchmark.index_symbol
    country = benchmark.country

    # 📌 3️⃣ 데이터 수집 기간 설정 (5년치)
    end_date = datetime.datetime.today().strftime("%Y-%m-%d")
    start_date = (
        datetime.datetime.today() - datetime.timedelta(days=5 * 365)
    ).strftime("%Y-%m-%d")

    print(f"📊 {benchmark.index_name} ({index_symbol}) 데이터 수집 중...")

    # 📌 4️⃣ 한국 지수 (KOSPI, KOSDAQ) - pykrx 사용
    if country == "KR":
        df = stock.get_index_ohlcv_by_date(
            start_date.replace("-", ""), end_date.replace("-", ""), index_symbol
        )
        if df.empty:
            print(f"⚠️ {benchmark.index_name} 데이터가 없습니다.")
            continue

        df.reset_index(inplace=True)
        df.rename(
            columns={
                "날짜": "date",
                "시가": "open",
                "고가": "high",
                "저가": "low",
                "종가": "close",
                "거래량": "volume",
            },
            inplace=True,
        )

    # 📌 5️⃣ 미국 지수 (S&P 500, NASDAQ, DOW JONES) - yfinance 사용
    elif country == "US":
        df = yf.download(
            index_symbol, start=start_date, end=end_date, auto_adjust=False
        )

        if df.empty:
            print(f"⚠️ {benchmark.index_name} 데이터가 없습니다.")
            continue

        # ✅ MultiIndex 해제 (첫 번째 레벨만 남김)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # ✅ 컬럼명을 소문자로 변환
        df.columns = df.columns.str.lower()

        # ✅ 인덱스를 date 컬럼으로 변환
        df["date"] = df.index.date

        # ✅ 컬럼명 변경
        df.rename(
            columns={
                "open": "open",
                "high": "high",
                "low": "low",
                "close": "close",
                "adj close": "adjusted_close",
                "volume": "volume",
            },
            inplace=True,
        )

        # ✅ "adjusted_close"가 없으면 "close" 값 사용
        if "adjusted_close" not in df.columns:
            df["adjusted_close"] = df["close"]

    else:
        print(f"❌ 지원하지 않는 국가 코드: {country}")
        continue

    # 📌 6️⃣ 데이터베이스에 저장 (중복 확인 후 삽입)
    for _, row in df.iterrows():
        existing_data = (
            session.query(BenchmarkPrice)
            .filter_by(benchmark_id=benchmark.id, date=row["date"])
            .first()
        )
        if existing_data:
            # 기존 데이터 업데이트
            existing_data.open_price = row["open"]
            existing_data.high_price = row["high"]
            existing_data.low_price = row["low"]
            existing_data.close_price = row["close"]
            existing_data.adjusted_close_price = row.get(
                "adjusted_close", row["close"]
            )  # 수정 종가가 없으면 종가 사용
            existing_data.volume = row["volume"]
        else:
            # 새 데이터 삽입
            new_price = BenchmarkPrice(
                benchmark_id=benchmark.id,
                date=row["date"],
                open_price=row["open"],
                high_price=row["high"],
                low_price=row["low"],
                close_price=row["close"],
                adjusted_close_price=row.get("adjusted_close", row["close"]),
                volume=row["volume"],
            )
            session.add(new_price)

    session.commit()
    print(f"✅ {benchmark.index_name} ({index_symbol}) 데이터 저장 완료!")

print("🎉 모든 벤치마크 지수 데이터 수집 및 저장 완료!")
