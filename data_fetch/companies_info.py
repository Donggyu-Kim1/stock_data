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


# ✅ NaN 값을 None으로 변환하는 함수 + 불필요한 Symbol 필터링 추가
def clean_value(value, check_symbol=False):
    """NaN, 'nan', None, 빈 문자열을 None으로 변환하고, 심볼에 '.' 또는 '$'가 포함되면 제외"""
    if pd.isna(value) or value in ["nan", "None", "", None]:
        return None

    # ✅ Symbol에 '.', '$' 포함된 경우 제거
    if check_symbol and any(char in value for char in [".", "$"]):
        print(f"⏭️ {value} (특수 문자 포함: 스킵)")
        return None

    return value


# ✅ 벤치마크별 티커 리스트 로드
def load_ticker_list(filename, symbol_col="Symbol"):
    """각 벤치마크별 티커 리스트를 로드하여 {Symbol: Sector} 형태로 반환"""
    filepath = f"data/{filename}"
    if os.path.exists(filepath):
        df = pd.read_csv(filepath)

        # ✅ NYSE의 경우, "ACT Symbol" 컬럼을 사용
        if "ACT Symbol" in df.columns:
            symbol_col = "ACT Symbol"

        # ✅ 필요한 컬럼이 없으면 오류 출력 후 빈 딕셔너리 반환
        if symbol_col not in df.columns:
            print(f"⚠️ {filename} 파일에서 '{symbol_col}' 컬럼을 찾을 수 없음.")
            return {}

        # ✅ NaN 값 제거 후 Symbol & Sector 추출
        df = df.dropna(subset=[symbol_col])  # ✅ NaN이 있는 행 제거
        return {
            clean_value(row[symbol_col], check_symbol=True): clean_value(
                row.get("Sector", "")
            )
            for _, row in df.iterrows()
            if clean_value(row[symbol_col], check_symbol=True)
        }
    return {}


# ✅ 티커 리스트 로드
sp500_tickers = load_ticker_list("sp500_tickers.csv")
nasdaq_tickers = load_ticker_list("nasdaq_tickers.csv")
nyse_tickers = load_ticker_list("nyse_tickers.csv", symbol_col="ACT Symbol")
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
    symbol = clean_value(symbol, check_symbol=True)
    if symbol is None:
        return None  # ✅ symbol이 없거나 필터링 대상이면 건너뜀

    try:
        stock_data = yf.Ticker(symbol).info
        return {
            "symbol": symbol,
            "name": clean_value(
                stock_data.get("longName", stock_data.get("shortName", ""))
            ),
            "sector": clean_value(stock_data.get("sector", "")),  # ✅ NaN 처리
            "country": "US",
            "benchmark_id": get_benchmark_id(symbol),
        }
    except Exception as e:
        print(f"⚠️ {symbol} 정보 조회 실패: {e}")
        return None


# ✅ 한국 주식 정보 수집 (pykrx)
def fetch_korean_stock_info(symbol):
    """pykrx를 활용하여 한국 주식 정보를 가져오기"""
    symbol = clean_value(symbol, check_symbol=True)
    if symbol is None:
        return None  # ✅ symbol이 없거나 필터링 대상이면 건너뜀

    try:
        name = stock.get_market_ticker_name(symbol)
        sector = clean_value(
            kospi_tickers.get(symbol, "") or kosdaq_tickers.get(symbol, "")
        )  # ✅ CSV에서 업종 가져오기
        return {
            "symbol": symbol,
            "name": clean_value(name),
            "sector": sector,
            "country": "KR",
            "benchmark_id": get_benchmark_id(symbol),
        }
    except Exception as e:
        print(f"⚠️ {symbol} 정보 조회 실패: {e}")
        return None


# ✅ 기업 정보를 DB에 저장
def save_company_info(company_data):
    """기업 정보를 `companies` 테이블에 저장"""
    if (
        not company_data
        or not company_data["symbol"]
        or not company_data["benchmark_id"]
    ):
        print(f"⚠️ 벤치마크 ID가 없어 저장하지 않음: {company_data}")
        return

    # ✅ 기존 데이터 확인
    existing_company = (
        session.query(Company).filter_by(symbol=company_data["symbol"]).first()
    )
    if existing_company:
        # ✅ 기존 데이터 업데이트
        existing_company.name = company_data["name"]
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
    us_tickers = (
        set(sp500_tickers.keys())
        | set(nasdaq_tickers.keys())
        | set(nyse_tickers.keys())
    )
    for symbol in us_tickers:
        if session.query(Company).filter_by(symbol=symbol).first():
            print(f"⏭️ {symbol} 이미 존재: 스킵")
            continue  # ✅ 이미 존재하는 경우 스킵
        company_data = fetch_us_stock_info(symbol)
        if company_data:
            save_company_info(company_data)

    # ✅ 한국 주식 처리 (KOSPI, KOSDAQ)
    kr_tickers = set(kospi_tickers.keys()) | set(kosdaq_tickers.keys())
    for symbol in kr_tickers:
        if session.query(Company).filter_by(symbol=symbol).first():
            print(f"⏭️ {symbol} 이미 존재: 스킵")
            continue  # ✅ 이미 존재하는 경우 스킵
        company_data = fetch_korean_stock_info(symbol)
        if company_data:
            save_company_info(company_data)


if __name__ == "__main__":
    process_all_companies()
    print("🎉 모든 기업 정보 저장 완료!")
