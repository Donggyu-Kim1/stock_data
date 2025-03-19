from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DECIMAL,
    BigInteger,
    Text,
    TIMESTAMP,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


# 1️⃣ 벤치마크 지수 테이블
class BenchmarkIndex(Base):
    __tablename__ = "benchmark_indices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    index_name = Column(String(50), unique=True, nullable=False)  # 벤치마크 주가지수명
    index_symbol = Column(String(20), unique=True, nullable=False)  # 벤치마크 지수 티커
    country = Column(String(50))  # 국가
    description = Column(Text)  # 설명
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())


# 2️⃣ 벤치마크 가격 데이터 테이블
class BenchmarkPrice(Base):
    __tablename__ = "benchmark_prices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    benchmark_id = Column(
        Integer, nullable=False
    )  # 벤치마크 지수 ID (논리적 관계만 유지)
    date = Column(Date, nullable=False)  # 날짜
    open_price = Column(DECIMAL(10, 2))  # 시가
    high_price = Column(DECIMAL(10, 2))  # 고가
    low_price = Column(DECIMAL(10, 2))  # 저가
    close_price = Column(DECIMAL(10, 2))  # 종가
    adjusted_close_price = Column(DECIMAL(10, 2))  # 수정 종가
    volume = Column(BigInteger)  # 거래량

    # UNIQUE KEY 추가 (benchmark_id + date)
    __table_args__ = (
        UniqueConstraint("benchmark_id", "date", name="uq_benchmark_date"),
    )


# 3️⃣ 기업 정보 테이블
class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), unique=True, nullable=False)  # 종목코드
    name = Column(String(255), nullable=False)  # 기업명
    country = Column(String(50))  # 국가
    sector = Column(String(255))  # 섹터
    benchmark_id = Column(
        Integer, nullable=False
    )  # 벤치마크 지수 ID (논리적 관계만 유지)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())


# 4️⃣ 주가 데이터 테이블
class StockPrice(Base):
    __tablename__ = "stock_prices"

    id = Column(Integer, primary_key=True, autoincrement=True)  # PK 1
    company_id = Column(Integer, primary_key=True, nullable=False)  # PK 2
    date = Column(Date, primary_key=True, nullable=False)  # PK 3
    open_price = Column(DECIMAL(10, 2))  # 시가
    high_price = Column(DECIMAL(10, 2))  # 고가
    low_price = Column(DECIMAL(10, 2))  # 저가
    close_price = Column(DECIMAL(10, 2))  # 종가
    adjusted_close_price = Column(DECIMAL(10, 2))  # 수정 종가
    volume = Column(BigInteger)  # 거래량

    # UNIQUE KEY 추가 (company_id + date)
    __table_args__ = (UniqueConstraint("company_id", "date", name="uq_company_date"),)


# 5️⃣ 재무 데이터 테이블
class FinancialStatement(Base):
    __tablename__ = "financial_statements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, nullable=False)  # 기업 ID (논리적 관계만 유지)
    report_date = Column(Date, nullable=False)  # 보고서 기준일

    # 재무 데이터
    revenue = Column(BigInteger)  # 매출액
    cost_of_sales = Column(BigInteger)  # 매출원가
    gross_profit = Column(BigInteger)  # 매출총이익
    operating_income = Column(BigInteger)  # 영업이익
    net_income = Column(BigInteger)  # 당기순이익
    total_assets = Column(BigInteger)  # 총자산
    total_liabilities = Column(BigInteger)  # 총부채
    current_assets = Column(BigInteger)  # 유동자산
    current_liabilities = Column(BigInteger)  # 유동부채
    total_debt = Column(BigInteger)  # 총차입금
    interest_expense = Column(BigInteger)  # 이자비용

    # 자본 및 현금흐름 관련
    total_equity = Column(BigInteger)  # 자기자본
    retained_earnings = Column(BigInteger)  # 이익잉여금
    cash_equivalents = Column(BigInteger)  # 현금 및 현금성자산
    operating_cash_flow = Column(BigInteger)  # 영업활동 현금흐름
    dividend_payout_ratio = Column(DECIMAL(10, 2))  # 배당성향
    ebitda = Column(BigInteger)  # EBITDA

    # UNIQUE KEY 추가 (company_id + report_date)
    __table_args__ = (
        UniqueConstraint("company_id", "report_date", name="uq_company_report"),
    )


# 6️⃣ 재무 비율 테이블
class FinancialRatio(Base):
    __tablename__ = "financial_ratios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, nullable=False)  # 기업 ID (논리적 관계만 유지)
    fiscal_year = Column(Integer, nullable=False)  # 회계연도

    # 안정성 지표
    current_ratio = Column(DECIMAL(10, 2))  # 유동비율
    cash_ratio = Column(DECIMAL(10, 2))  # 현금비율
    debt_ratio = Column(DECIMAL(10, 2))  # 부채비율
    working_capital_ratio = Column(DECIMAL(10, 2))  # 운전자본비율
    equity_ratio = Column(DECIMAL(10, 2))  # 자기자본비율
    debt_dependency = Column(DECIMAL(10, 2))  # 차입금의존도
    interest_coverage = Column(DECIMAL(10, 2))  # 이자보상배율

    # 수익성 지표
    gross_margin = Column(DECIMAL(10, 2))  # 매출총이익률
    ros = Column(DECIMAL(10, 2))  # 매출액순이익률 (ROS)
    roa = Column(DECIMAL(10, 2))  # 총자산영업이익률 (ROA)
    roe = Column(DECIMAL(10, 2))  # 자기자본순이익률 (ROE)

    # 활동성 지표
    asset_turnover = Column(DECIMAL(10, 2))  # 총자산회전율
    equity_turnover = Column(DECIMAL(10, 2))  # 자기자본회전율
    inventory_turnover = Column(DECIMAL(10, 2))  # 재고자산회전율

    # 성장성 지표
    revenue_growth = Column(DECIMAL(10, 2))  # 매출액 증가율
    asset_growth = Column(DECIMAL(10, 2))  # 총자산 증가율
    equity_growth = Column(DECIMAL(10, 2))  # 자기자본 증가율
    sustainable_growth = Column(DECIMAL(10, 2))  # 지속가능성장률

    # UNIQUE KEY 추가 (company_id + report_date)
    __table_args__ = (
        UniqueConstraint(
            "company_id", "report_date", name="uq_company_financial_ratios"
        ),
    )


# 7️⃣ 기업 가치 평가 테이블
class ValuationMetric(Base):
    __tablename__ = "valuation_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, nullable=False)  # 기업 ID (논리적 관계만 유지)
    date = Column(Date, nullable=False)  # 평가 기준일

    # 기본 밸류에이션 지표
    market_cap = Column(BigInteger)  # 시가총액
    per = Column(DECIMAL(10, 2))  # 주가수익비율 (PER)
    peg_ratio = Column(DECIMAL(10, 2))  # PEG Ratio
    pbr = Column(DECIMAL(10, 2))  # 주가순자산비율 (PBR)
    psr = Column(DECIMAL(10, 2))  # 주가매출비율 (PSR)
    ev_ebitda = Column(DECIMAL(10, 2))  # EV/EBITDA
    fcf = Column(BigInteger)  # Free Cash Flow (FCF)
    beta = Column(DECIMAL(10, 2))  # 베타값

    # 추가적인 밸류에이션 계산 요소
    risk_free_rate = Column(DECIMAL(10, 4))  # 무위험자산수익률
    market_risk_premium = Column(DECIMAL(10, 4))  # 시장 위험 프리미엄
    cost_of_equity = Column(DECIMAL(10, 4))  # 자기자본 비용 (CARM)
    wacc = Column(DECIMAL(10, 4))  # 가중평균자본비용 (WACC)

    # UNIQUE KEY 추가 (company_id + date)
    __table_args__ = (
        UniqueConstraint("company_id", "date", name="uq_company_valuation_date"),
    )
