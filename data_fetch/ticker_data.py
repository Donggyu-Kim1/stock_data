import pandas as pd
from pykrx import stock


def get_sp500_tickers():
    """S&P 500 티커 리스트 가져오기"""
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    tables = pd.read_html(url)
    df = tables[0]
    df.to_csv("data/sp500_tickers.csv", index=False)
    print(f"✅ S&P 500 티커 리스트 저장 완료! ({len(df)}개)")


def get_nasdaq_tickers():
    """NASDAQ 전체 티커 리스트 가져오기"""
    url = "ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqlisted.txt"
    df = pd.read_csv(url, sep="|")
    df.to_csv("data/nasdaq_tickers.csv", index=False)
    print(f"✅ NASDAQ 티커 리스트 저장 완료! ({len(df)}개)")


def get_nyse_tickers():
    """NYSE 전체 티커 리스트 가져오기"""
    url = "ftp://ftp.nasdaqtrader.com/SymbolDirectory/otherlisted.txt"
    df = pd.read_csv(url, sep="|")
    df.to_csv("data/nyse_tickers.csv", index=False)
    print(f"✅ NYSE 티커 리스트 저장 완료! ({len(df)}개)")


def get_kospi_tickers():
    """KOSPI 종목 리스트 가져오기"""
    tickers = stock.get_market_ticker_list(market="KOSPI")
    df = pd.DataFrame({"Symbol": tickers})

    # ✅ 기업명 추가 (KRX에서 제공)
    df["Name"] = df["Symbol"].apply(lambda x: stock.get_market_ticker_name(x))

    # ✅ CSV 저장
    df.to_csv("data/kospi_tickers.csv", index=False)
    print(f"✅ KOSPI 티커 리스트 저장 완료! ({len(df)}개)")


def get_kosdaq_tickers():
    """KOSDAQ 종목 리스트 가져오기"""
    tickers = stock.get_market_ticker_list(market="KOSDAQ")
    df = pd.DataFrame({"Symbol": tickers})

    # ✅ 기업명 추가 (KRX에서 제공)
    df["Name"] = df["Symbol"].apply(lambda x: stock.get_market_ticker_name(x))

    # ✅ CSV 저장
    df.to_csv("data/kosdaq_tickers.csv", index=False)
    print(f"✅ KOSDAQ 티커 리스트 저장 완료! ({len(df)}개)")


if __name__ == "__main__":
    get_kospi_tickers()
    get_kosdaq_tickers()
    get_sp500_tickers()
    get_nasdaq_tickers()
    get_nyse_tickers()
    print("🎉 모든 티커 리스트 저장 완료!")
