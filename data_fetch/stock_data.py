from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from config.db_config import get_db_connection
from database.models import Company, StockPrice  # 모델 불러오기

# 주식 데이터 불러오기
import yfinance as yf
from pykrx import stock
from datetime import datetime, timedelta

engine = create_engine(get_db_connection())
Session = sessionmaker(bind=engine)


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
                    "open_price": row["Open"],
                    "high_price": row["High"],
                    "low_price": row["Low"],
                    "close_price": row["Close"],
                    "adjusted_close_price": row["Adj Close"],
                    "volume": row["Volume"],
                }
            )

        return stock_data
    except Exception as e:
        print(f"❌ {symbol} 데이터 수집 실패: {e}")
        return None


def fetch_kr_stock_data(symbol):
    """pykrx를 사용하여 한국 주식 데이터를 가져옴"""
    try:
        today = datetime.today().strftime("%Y%m%d")
        start_date = (datetime.today() - timedelta(days=5 * 365)).strftime("%Y%m%d")

        data = stock.get_market_ohlcv(start_date, today, symbol)

        if data.empty:
            print(f"⚠️ {symbol} 주가 데이터 없음")
            return None

        stock_data = []
        for date, row in data.iterrows():
            stock_data.append(
                {
                    "date": datetime.strptime(str(date), "%Y%m%d").date(),
                    "open_price": row["시가"],
                    "high_price": row["고가"],
                    "low_price": row["저가"],
                    "close_price": row["종가"],
                    "adjusted_close_price": row["종가"],  # pykrx에는 수정 종가 없음
                    "volume": row["거래량"],
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
    """수집한 주가 데이터를 stock_prices 테이블에 저장"""
    session = Session()
    try:
        # company_id 검증
        if not company_exists(session, company_id):
            print(f"❌ 유효하지 않은 company_id: {company_id}")
            return

        for data in stock_data:
            # 중복 데이터 검증
            if is_stock_data_already_stored(session, company_id, data["date"]):
                print(f"⚠️ {company_id} {data['date']} 데이터 이미 존재, 저장 건너뜀")
                continue

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
