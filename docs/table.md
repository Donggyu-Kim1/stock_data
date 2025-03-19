# 1. 기업 정보 테이블 (companies)

```sql
-- 기업의 기본 정보를 저장하는 테이블.
CREATE TABLE companies (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    symbol         VARCHAR(20) NOT NULL UNIQUE,  -- 종목코드 (Ticker, 종목코드)
    name           VARCHAR(255) NOT NULL,       -- 기업명
    country        VARCHAR(50),                 -- 국가 (KR, US)
    sector         VARCHAR(255),                -- 섹터
    benchmark_id   INT NOT NULL,                -- 벤치마크 주가지수 ID (논리적 관계만 유지)
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

# 2. 주가 데이터 테이블 (stock_prices)

```sql
-- 기업의 일별 주가 데이터를 저장하는 테이블.
CREATE TABLE stock_prices (
    id            INT AUTO_INCREMENT,  -- AUTO_INCREMENT 유지
    company_id    INT NOT NULL,        -- 기업 ID (논리적 관계만 유지)
    date          DATE NOT NULL,       -- 날짜
    open_price    DECIMAL(10,2),       -- 시가
    high_price    DECIMAL(10,2),       -- 고가
    low_price     DECIMAL(10,2),       -- 저가
    close_price   DECIMAL(10,2),       -- 종가
    adjusted_close_price DECIMAL(10,2), -- 수정 종가
    volume        BIGINT,              -- 거래량

    -- 복합 PRIMARY KEY 적용 (파티션을 위해 필요)
    PRIMARY KEY (id, company_id, date),

    -- 중복 방지
    UNIQUE (company_id, date)
);
```

# 3. 재무 데이터 테이블 (financial_statements)

```sql
-- 기업의 분기별 재무제표 데이터를 저장하는 테이블.
CREATE TABLE financial_statements (
    id                   INT AUTO_INCREMENT PRIMARY KEY,
    company_id           INT NOT NULL,  -- 기업 ID (논리적 관계만 유지)
    report_date          DATE NOT NULL, -- 보고서 기준일 (분기별)

    -- 기본 재무 데이터
    revenue              BIGINT,        -- 매출액
    operating_income     BIGINT,        -- 영업이익
    net_income           BIGINT,        -- 당기순이익
    total_assets         BIGINT,        -- 총자산
    total_liabilities    BIGINT,        -- 총부채
    current_assets       BIGINT,        -- 유동자산
    current_liabilities  BIGINT,        -- 유동부채
    total_debt           BIGINT,        -- 총차입금
    interest_expense     BIGINT,        -- 이자비용

    -- 자본 및 현금흐름 관련
    total_equity         BIGINT,        -- 자기자본
    retained_earnings    BIGINT,        -- 이익잉여금
    cash_equivalents     BIGINT,        -- 현금 및 현금성자산
    operating_cash_flow  BIGINT,        -- 영업활동 현금흐름
    dividend_payout_ratio DECIMAL(10,2), -- 배당성향
    ebitda              BIGINT,         -- EBITDA

    -- 중복 방지
    UNIQUE (company_id, report_date)
);
```

# 4. 재무 비율 테이블 (financial_ratios)

```sql
-- 안정성, 수익성, 활동성, 성장성 지표를 저장하는 테이블.
CREATE TABLE financial_ratios (
    id                   INT AUTO_INCREMENT PRIMARY KEY,
    company_id           INT NOT NULL,  
    fiscal_year          DATE NOT NULL,  -- 회계연도

    -- 안정성 (Liquidity & Solvency)
    current_ratio        DECIMAL(10,2), -- 유동비율
    cash_ratio           DECIMAL(10,2), -- 현금비율
    debt_ratio           DECIMAL(10,2), -- 부채비율
    working_capital_ratio DECIMAL(10,2), -- 운전자본비율
    equity_ratio         DECIMAL(10,2), -- 자기자본비율
    debt_dependency      DECIMAL(10,2), -- 차입금 의존도
    interest_coverage    DECIMAL(10,2), -- 이자보상배율

    -- 수익성 (Profitability)
    gross_margin         DECIMAL(10,2), -- 매출총이익률
    ros                 DECIMAL(10,2), -- 매출액순이익률 (ROS)
    roa                 DECIMAL(10,2), -- 총자산영업이익률 (ROA)
    roe                 DECIMAL(10,2), -- 자기자본순이익률 (ROE)

    -- 활동성 (Efficiency)
    asset_turnover       DECIMAL(10,2), -- 총자산회전율
    equity_turnover      DECIMAL(10,2), -- 자기자본회전율
    inventory_turnover   DECIMAL(10,2), -- 재고자산회전율

    -- 성장성 (Growth)
    revenue_growth       DECIMAL(10,2), -- 매출액 증가율
    asset_growth         DECIMAL(10,2), -- 총자산 증가율
    equity_growth        DECIMAL(10,2), -- 자기자본 증가율
    sustainable_growth   DECIMAL(10,2), -- 지속가능성장률

    -- 중복 방지
    UNIQUE (company_id, report_date)
);
```

# 5. 벤치마크 지수 테이블 (benchmark_indices)

```sql
-- 미국, 한국 벤치마크 지수 관련 테이블
CREATE TABLE benchmark_indices (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    index_name      VARCHAR(50) NOT NULL UNIQUE,  -- 벤치마크 주가지수명(티커)
    index_symbol    VARCHAR(20) NOT NULL UNIQUE, -- 벤치마크 지수 티커
    country        VARCHAR(50),                  -- 국가 (KR, US 등)
    description     TEXT,                         -- 설명 (예: S&P 500은 미국 대형주 500개 포함)
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

# 6. 벤치마크 지수 가격 테이블 (benchmark_prices)

```sql
-- 벤치마크 지수 가격 테이블
CREATE TABLE benchmark_prices (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    benchmark_id  INT NOT NULL,  -- 벤치마크 지수 ID (논리적 관계만 유지)
    date          DATE NOT NULL, -- 날짜
    open_price    DECIMAL(10,2), -- 시가
    high_price    DECIMAL(10,2), -- 고가
    low_price     DECIMAL(10,2), -- 저가
    close_price   DECIMAL(10,2), -- 종가
    adjusted_close_price DECIMAL(10,2), -- 수정 종가
    volume        BIGINT,        -- 거래량

    -- 중복 방지
    UNIQUE (benchmark_id, date)
);
```

# 7. 기업 가치 평가 테이블 (valuation_metrics)

```sql
-- 기업의 가치 평가 관련 데이터를 저장하는 테이블.
CREATE TABLE valuation_metrics (
    id                     INT AUTO_INCREMENT PRIMARY KEY,
    company_id             INT NOT NULL,  -- 기업 ID (논리적 관계만 유지)
    date                   DATE NOT NULL,  -- 평가 기준일

    -- 기본 밸류에이션 지표
    market_cap             BIGINT,        -- 시가총액
    per                    DECIMAL(10,2), -- 주가수익비율 (PER)
    peg_ratio              DECIMAL(10,2), -- PEG Ratio
    pbr                    DECIMAL(10,2), -- 주가순자산비율 (PBR)
    psr                    DECIMAL(10,2), -- 주가매출비율 (PSR)
    ev_ebitda              DECIMAL(10,2), -- EV/EBITDA
    fcf                    BIGINT,        -- Free Cash Flow (FCF)
    beta                   DECIMAL(10,2), -- 베타값

    -- 추가적인 밸류에이션 계산 요소
    risk_free_rate         DECIMAL(10,4), -- 무위험자산수익률
    market_risk_premium    DECIMAL(10,4), -- 시장 위험 프리미엄
    cost_of_equity         DECIMAL(10,4), -- 자기자본 비용 (CARM)
    wacc                   DECIMAL(10,4), -- 가중평균자본비용 (WACC)

    -- 중복 방지
    UNIQUE (company_id, date)
);
```