from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from config.db_config import get_db_url
from database.models import Company, StockPrice  # 모델 불러오기

import numpy as np
import yfinance as yf
from pykrx import stock
from datetime import datetime, timedelta

engine = create_engine(get_db_url())
Session = sessionmaker(bind=engine)


def convert_nan_to_none(value):
    """NaN 값을 None으로 변환 (MySQL DECIMAL 타입 대응)"""
    if isinstance(value, float) and np.isnan(value):
        return None
    return value


def get_companies():
    """기업 정보를 가져옴"""
    session = Session()
    try:
        return session.query(Company.id, Company.symbol, Company.country).all()
    except Exception as e:
        print(f"❌ 기업 목록 불러오기 실패: {e}")
        return []
    finally:
        session.close()


def fetch_us_stock_data(symbol):
    """yfinance를 사용하여 미국 주식 데이터를 가져옴"""
    try:
        end_date = datetime.today().strftime("%Y-%m-%d")
        start_date = (datetime.today() - timedelta(days=5 * 365)).strftime("%Y-%m-%d")

        stock = yf.Ticker(symbol)
        data = stock.history(start=start_date, end=end_date)  # 5년치 데이터 가져오기

        if data.empty:
            print(f"⚠️ {symbol} 주가 데이터 없음")
            return None

        stock_data = []
        for date, row in data.iterrows():
            stock_data.append(
                {
                    "date": date.date(),
                    "open_price": convert_nan_to_none(row["Open"]),
                    "high_price": convert_nan_to_none(row["High"]),
                    "low_price": convert_nan_to_none(row["Low"]),
                    "close_price": convert_nan_to_none(row["Close"]),
                    "adjusted_close_price": convert_nan_to_none(row["Close"]),
                    "volume": convert_nan_to_none(row["Volume"]),
                }
            )

        return stock_data
    except Exception as e:
        print(f"❌ {symbol} 데이터 수집 실패: {e}")
        return None


def fetch_kr_stock_data(symbol):
    """pykrx를 사용하여 한국 주식 데이터를 가져옴 (날짜 변환 처리)"""
    try:
        today = datetime.today().strftime("%Y%m%d")
        start_date = (datetime.today() - timedelta(days=5 * 365)).strftime("%Y%m%d")

        data = stock.get_market_ohlcv(start_date, today, symbol)

        if data.empty:
            print(f"⚠️ {symbol} 주가 데이터 없음")
            return None

        stock_data = []
        for date, row in data.iterrows():
            # ✅ 날짜 형식이 YYYY-MM-DD HH:MM:SS인 경우 자동 변환
            if isinstance(date, str):
                try:
                    date_obj = datetime.strptime(date, "%Y%m%d").date()
                except ValueError:
                    date_obj = datetime.strptime(date, "%Y-%m-%d %H:%M:%S").date()
            else:
                date_obj = date.date()  # Timestamp 객체라면 변환

            stock_data.append(
                {
                    "date": date_obj,
                    "open_price": convert_nan_to_none(row["시가"]),
                    "high_price": convert_nan_to_none(row["고가"]),
                    "low_price": convert_nan_to_none(row["저가"]),
                    "close_price": convert_nan_to_none(row["종가"]),
                    "adjusted_close_price": convert_nan_to_none(row["종가"]),
                    "volume": convert_nan_to_none(row["거래량"]),
                }
            )

        return stock_data
    except Exception as e:
        print(f"❌ {symbol} 데이터 수집 실패: {e}")
        return None


def company_exists(session, company_id):
    """company_id가 유효한지 검증"""
    return session.query(Company.id).filter_by(id=company_id).first() is not None


def is_stock_data_already_stored(session, company_id, date):
    """이미 해당 날짜의 주가 데이터가 저장되어 있는지 확인"""
    return (
        session.query(StockPrice.id).filter_by(company_id=company_id, date=date).first()
        is not None
    )


def save_stock_data(company_id, stock_data):
    """주가 데이터를 저장하며, 기존 데이터와 비교하여 다르면 업데이트"""
    session = Session()
    try:
        # company_id 검증
        if not company_exists(session, company_id):
            print(f"❌ 유효하지 않은 company_id: {company_id}")
            return

        today = datetime.today().date()  # 오늘 날짜

        for data in stock_data:
            existing_entry = (
                session.query(StockPrice)
                .filter_by(company_id=company_id, date=data["date"])
                .first()
            )

            if existing_entry:
                # ✅ 과거 데이터의 종가(close_price) 또는 거래량(volume)이 다르면 업데이트 수행
                if (
                    existing_entry.close_price != data["close_price"]
                    or existing_entry.volume != data["volume"]
                ):
                    existing_entry.open_price = data["open_price"]
                    existing_entry.high_price = data["high_price"]
                    existing_entry.low_price = data["low_price"]
                    existing_entry.close_price = data["close_price"]
                    existing_entry.adjusted_close_price = data["adjusted_close_price"]
                    existing_entry.volume = data["volume"]
                    print(
                        f"🔄 {company_id} {data['date']} 주가 데이터 업데이트 (변경 감지)"
                    )

                else:
                    print(
                        f"⚠️ {company_id} {data['date']} 기존 데이터와 동일, 업데이트 건너뜀"
                    )

            else:
                # ✅ 새로운 데이터라면 INSERT 수행
                new_price = StockPrice(
                    company_id=company_id,
                    date=data["date"],
                    open_price=data["open_price"],
                    high_price=data["high_price"],
                    low_price=data["low_price"],
                    close_price=data["close_price"],
                    adjusted_close_price=data["adjusted_close_price"],
                    volume=data["volume"],
                )
                session.add(new_price)

        session.commit()
        print(f"✅ {company_id} 주가 데이터 저장 완료")
    except Exception as e:
        session.rollback()
        print(f"❌ 데이터 저장 실패: {e}")
    finally:
        session.close()


def update_stock_data():
    """기업 리스트를 불러와 주가 데이터를 수집하고 저장"""
    companies = get_companies()

    for company in companies:
        company_id, symbol, country = company

        if country == "US":
            stock_data = fetch_us_stock_data(symbol)
        elif country == "KR":
            stock_data = fetch_kr_stock_data(symbol)
        else:
            print(f"⚠️ 지원되지 않는 국가: {country}")
            continue

        if stock_data:
            save_stock_data(company_id, stock_data)
        else:
            print(f"⚠️ {symbol} 주가 데이터 없음, 저장 건너뜀")


if __name__ == "__main__":
    update_stock_data()
