import os
import pandas as pd
import yfinance as yf
from pykrx import stock
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from database.models import Base, Company, BenchmarkIndex
from config.db_config import get_db_url

# ✅ 데이터베이스 연결
db_url = get_db_url()
engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
session = Session()

# ✅ `data/` 폴더 확인 및 생성
os.makedirs("data", exist_ok=True)

# ✅ 벤치마크 ID 가져오기
benchmark_map = {b.index_symbol: b.id for b in session.query(BenchmarkIndex).all()}


# ✅ 벤치마크별 티커 리스트 로드
def load_ticker_list(filename):
    filepath = f"data/{filename}"
    if os.path.exists(filepath):
        return set(pd.read_csv(filepath)["Symbol"].tolist())
    return set()


sp500_tickers = load_ticker_list("sp500_tickers.csv")
nasdaq_tickers = load_ticker_list("nasdaq_tickers.csv")
nyse_tickers = load_ticker_list("nyse_tickers.csv")
kospi_tickers = load_ticker_list("kospi_tickers.csv")
kosdaq_tickers = load_ticker_list("kosdaq_tickers.csv")


# ✅ 벤치마크 매핑 함수
def get_benchmark_id(symbol):
    """기업의 벤치마크 ID를 반환 (우선순위: S&P 500 > NASDAQ > NYSE > KOSPI > KOSDAQ)"""
    if symbol in sp500_tickers:
        return benchmark_map.get("^GSPC")
    elif symbol in nasdaq_tickers:
        return benchmark_map.get("^IXIC")
    elif symbol in nyse_tickers:
        return benchmark_map.get("^NYA")
    elif symbol in kospi_tickers:
        return benchmark_map.get("1001")  # KOSPI
    elif symbol in kosdaq_tickers:
        return benchmark_map.get("2001")  # KOSDAQ
    return None


# ✅ 미국 주식 정보 수집 (yfinance)
def fetch_us_stock_info(symbol):
    """yfinance를 활용하여 미국 주식 정보를 가져오기"""
    try:
        stock_data = yf.Ticker(symbol).info
        return {
            "symbol": symbol,
            "name": stock_data.get("longName", stock_data.get("shortName", "")),
            "industry": stock_data.get("industry", ""),
            "sector": stock_data.get("sector", ""),
            "country": "US",
            "benchmark_id": get_benchmark_id(symbol),
        }
    except Exception as e:
        print(f"⚠️ {symbol} 정보 조회 실패: {e}")
        return None


# ✅ 한국 주식 정보 수집 (pykrx)
def fetch_korean_stock_info(symbol):
    """pykrx를 활용하여 한국 주식 정보를 가져오기"""
    try:
        name = stock.get_market_ticker_name(symbol)
        return {
            "symbol": symbol,
            "name": name,
            "industry": "",  # KRX에서는 업종 정보를 제공하지 않음
            "sector": "",
            "country": "KR",
            "benchmark_id": get_benchmark_id(symbol),
        }
    except Exception as e:
        print(f"⚠️ {symbol} 정보 조회 실패: {e}")
        return None


# ✅ 기업 정보를 DB에 저장
def save_company_info(company_data):
    """기업 정보를 `companies` 테이블에 저장"""
    if not company_data or not company_data["benchmark_id"]:
        print(f"⚠️ 벤치마크 ID가 없어 저장하지 않음: {company_data}")
        return

    existing_company = (
        session.query(Company).filter_by(symbol=company_data["symbol"]).first()
    )
    if existing_company:
        # ✅ 기존 데이터 업데이트
        existing_company.name = company_data["name"]
        existing_company.industry = company_data["industry"]
        existing_company.sector = company_data["sector"]
        existing_company.benchmark_id = company_data["benchmark_id"]
    else:
        # ✅ 새로운 데이터 삽입
        new_company = Company(**company_data)
        session.add(new_company)

    session.commit()
    print(f"✅ {company_data['symbol']} ({company_data['name']}) 저장 완료!")


# ✅ 전체 주식 리스트 가져오기
def process_all_companies():
    """미국 & 한국 주식 데이터를 모두 가져와서 DB에 저장"""
    # ✅ 미국 주식 처리 (S&P 500, NASDAQ, NYSE)
    us_tickers = sp500_tickers | nasdaq_tickers | nyse_tickers
    for symbol in us_tickers:
        company_data = fetch_us_stock_info(symbol)
        save_company_info(company_data)

    # ✅ 한국 주식 처리 (KOSPI, KOSDAQ)
    kr_tickers = kospi_tickers | kosdaq_tickers
    for symbol in kr_tickers:
        company_data = fetch_korean_stock_info(symbol)
        save_company_info(company_data)


if __name__ == "__main__":
    process_all_companies()
    print("🎉 모든 기업 정보 저장 완료!")
