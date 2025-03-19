import os
import pandas as pd
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from database.models import FinancialStatement, Company
from config.db_config import get_db_url

# 재무 데이터 수집 api
import yfinance as yf
from pykrx import stock
from dart_fss import get_corp_list

# ✅ 데이터베이스 연결 설정
engine = create_engine(get_db_url())
Session = sessionmaker(bind=engine)
session = Session()

# ✅ DART API 키 설정
DART_API_KEY = os.getenv("DART_API_KEY", "")
corp_list = get_corp_list(api_key=DART_API_KEY)


def fetch_us_financials(symbol):
    """미국 주식의 5년 치 연간 재무 데이터(yfinance 사용)"""
    try:
        stock = yf.Ticker(symbol)
        financials = stock.financials.T  # 연간 손익계산서
        balance_sheet = stock.balance_sheet.T  # 연간 대차대조표
        cashflow = stock.cashflow.T  # 연간 현금흐름표

        # ✅ 5년치 연간 데이터만 선택
        report_dates = financials.index.astype(str)[-5:]  # 최신 5개 연도 선택

        # ✅ 배당성향 (payoutRatio) 가져오기
        dividend_payout_ratio = stock.info.get("payoutRatio", None)
        if dividend_payout_ratio is not None:
            dividend_payout_ratio = round(
                float(dividend_payout_ratio) * 100, 2
            )  # 퍼센트 변환

        data = []
        for report_date in report_dates:
            year = int(report_date[:4])  # 연도 추출

            # ✅ 데이터가 NaN인 경우 None으로 변환하는 함수
            def clean_value(value):
                return None if pd.isna(value) else float(value)

            # ✅ 총자산 (Total Assets)
            total_assets = clean_value(
                balance_sheet.get("Total Assets", {}).get(report_date)
            )

            # ✅ 총부채 (Total Liabilities)
            total_liabilities = clean_value(
                balance_sheet.get("Total Liabilities Net Minority Interest", {}).get(
                    report_date
                )
            )

            # ✅ 총 자기자본 (Total Equity) 계산 (총자산 - 총부채)
            total_equity = None
            if total_assets is not None and total_liabilities is not None:
                total_equity = total_assets - total_liabilities

            # ✅ 영업활동 현금흐름 (Operating Cash Flow) 가져오기
            operating_cash_flow = clean_value(
                cashflow.get("Operating Cash Flow", {}).get(report_date)
            )

            net_income = clean_value(financials.get("Net Income", {}).get(report_date))
            operating_income = clean_value(
                financials.get("Operating Income", {}).get(report_date)
            )
            depreciation = clean_value(
                cashflow.get("Depreciation And Amortization", {}).get(report_date)
            )

            # ✅ EBITDA 계산 (운영이익 + 감가상각비)
            ebitda = (
                operating_income + depreciation
                if operating_income and depreciation
                else None
            )

            # ✅ 데이터가 NaN이면 건너뛰기
            if net_income is not None:
                data.append(
                    {
                        "report_date": report_date,
                        "revenue": clean_value(
                            financials.get("Total Revenue", {}).get(report_date)
                        ),
                        "operating_income": operating_income,
                        "net_income": net_income,
                        "total_assets": total_assets,
                        "total_liabilities": total_liabilities,
                        "current_assets": clean_value(
                            balance_sheet.get("Current Assets", {}).get(report_date)
                        ),
                        "current_liabilities": clean_value(
                            balance_sheet.get("Current Liabilities", {}).get(
                                report_date
                            )
                        ),
                        "total_debt": clean_value(
                            balance_sheet.get("Total Debt", {}).get(report_date)
                        ),
                        "interest_expense": clean_value(
                            financials.get("Interest Expense", {}).get(report_date)
                        ),
                        "total_equity": total_equity,  # ✅ 계산된 값 적용
                        "retained_earnings": clean_value(
                            balance_sheet.get("Retained Earnings", {}).get(report_date)
                        ),
                        "cash_equivalents": clean_value(
                            balance_sheet.get("Cash And Cash Equivalents", {}).get(
                                report_date
                            )
                        ),
                        "operating_cash_flow": operating_cash_flow,
                        "dividend_payout_ratio": dividend_payout_ratio,
                        "ebitda": ebitda,
                    }
                )
        return data
    except Exception as e:
        print(f"❌ {symbol} 재무 데이터 수집 실패: {e}")
        return None


def fetch_kr_net_income(symbol, report_date):
    """
    DART에서 한국 주식의 당기순이익 데이터를 가져오기
    :param symbol: 종목 코드
    :param report_date: 기준일 (예: "2023-12-31")
    :return: 당기순이익 (Net Income) or None
    """
    try:
        corp = corp_list.find_by_stock_code(symbol)
        if corp is None:
            print(f"⚠️ {symbol} 기업을 찾을 수 없음")
            return None

        fs = corp.extract_fs(report_tp="annual", year=5)  # 5년치 데이터

        if report_date in fs.index:
            return fs.loc[report_date, "당기순이익"] if "당기순이익" in fs else None
        else:
            return None
    except Exception as e:
        print(f"❌ {symbol} 당기순이익 조회 실패: {e}")
        return None


def fetch_kr_dividend_payout_ratio(symbol, report_date):
    """한국 주식의 배당성향을 pykrx와 DART 데이터를 활용하여 계산"""
    try:
        year = report_date[:4]
        start_date = f"{year}0101"
        end_date = f"{year}1231"

        # 📌 배당금 데이터 조회 (연간 기준)
        df = stock.get_market_dividend_by_date(start_date, end_date, symbol)
        if df.empty:
            return None

        total_dividends = df["현금배당액"].sum()

        # 📌 당기순이익 (DART API 활용)
        net_income = fetch_kr_net_income(symbol, report_date)
        if not net_income or net_income <= 0:
            return None

        return round((total_dividends / net_income) * 100, 2)
    except Exception as e:
        print(f"❌ {symbol} 배당성향 계산 실패: {e}")
        return None


def fetch_kr_financials(symbol):
    """한국 주식의 5년 치 재무 데이터(DART API + pykrx 활용)"""
    try:
        corp = corp_list.find_by_stock_code(symbol)
        if corp is None:
            print(f"⚠️ {symbol} 기업을 찾을 수 없음")
            return None

        fs = corp.extract_fs(report_tp="annual", year=5)

        data = []
        for report_date in fs.index.astype(str):
            net_income = (
                fs.loc[report_date, "당기순이익"] if "당기순이익" in fs else None
            )
            operating_income = (
                fs.loc[report_date, "영업이익"] if "영업이익" in fs else None
            )
            depreciation = (
                fs.loc[report_date, "감가상각비"] if "감가상각비" in fs else None
            )

            # ✅ EBITDA 계산
            ebitda = None
            if operating_income is not None and depreciation is not None:
                ebitda = operating_income + depreciation

            # ✅ 배당성향 계산 (pykrx 활용)
            dividend_payout_ratio = fetch_kr_dividend_payout_ratio(symbol, report_date)

            data.append(
                {
                    "report_date": report_date,
                    "revenue": (
                        fs.loc[report_date, "매출액"] if "매출액" in fs else None
                    ),
                    "operating_income": operating_income,
                    "net_income": net_income,
                    "total_assets": (
                        fs.loc[report_date, "자산총계"] if "자산총계" in fs else None
                    ),
                    "total_liabilities": (
                        fs.loc[report_date, "부채총계"] if "부채총계" in fs else None
                    ),
                    "current_assets": (
                        fs.loc[report_date, "유동자산"] if "유동자산" in fs else None
                    ),
                    "current_liabilities": (
                        fs.loc[report_date, "유동부채"] if "유동부채" in fs else None
                    ),
                    "total_debt": (
                        fs.loc[report_date, "총차입금"] if "총차입금" in fs else None
                    ),
                    "interest_expense": (
                        fs.loc[report_date, "이자비용"] if "이자비용" in fs else None
                    ),
                    "total_equity": (
                        fs.loc[report_date, "자본총계"] if "자본총계" in fs else None
                    ),
                    "retained_earnings": (
                        fs.loc[report_date, "이익잉여금"]
                        if "이익잉여금" in fs
                        else None
                    ),
                    "cash_equivalents": (
                        fs.loc[report_date, "현금및현금성자산"]
                        if "현금및현금성자산" in fs
                        else None
                    ),
                    "operating_cash_flow": (
                        fs.loc[report_date, "영업활동현금흐름"]
                        if "영업활동현금흐름" in fs
                        else None
                    ),
                    "dividend_payout_ratio": dividend_payout_ratio,
                    "ebitda": ebitda,
                }
            )
        return data
    except Exception as e:
        print(f"❌ {symbol} 재무 데이터 수집 실패: {e}")
        return None


def save_financial_data(company_id, financial_data):
    """재무 데이터를 저장"""
    session = Session()
    try:
        for data in financial_data:
            existing_entry = (
                session.query(FinancialStatement)
                .filter_by(company_id=company_id, report_date=data["report_date"])
                .first()
            )

            if existing_entry:
                print(
                    f"⚠️ {company_id} {data['report_date']} 기존 데이터 존재, 업데이트 안함"
                )
            else:
                new_entry = FinancialStatement(company_id=company_id, **data)
                session.add(new_entry)

        session.commit()
        print(f"✅ {company_id} 재무 데이터 저장 완료")
    except Exception as e:
        session.rollback()
        print(f"❌ 데이터 저장 실패: {e}")
    finally:
        session.close()


def update_financial_data():
    """모든 기업의 재무 데이터를 수집 및 저장"""
    companies = session.query(Company.id, Company.symbol, Company.country).all()

    for company in companies:
        company_id, symbol, country = company

        if country == "US":
            financial_data = fetch_us_financials(symbol)
        elif country == "KR":
            financial_data = fetch_kr_financials(symbol)
        else:
            print(f"⚠️ 지원되지 않는 국가: {country}")
            continue

        if financial_data:
            save_financial_data(company_id, financial_data)
        else:
            print(f"⚠️ {symbol} 재무 데이터 없음, 저장 건너뜀")


if __name__ == "__main__":
    update_financial_data()
