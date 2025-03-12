import os
import io
import pandas as pd
import requests


def fetch_krx_sector_data(market: str):
    """
    KRX 한국거래소에서 특정 시장(KOSPI/KOSDAQ)의 업종(Sector) 정보 크롤링
    """
    headers = {"User-Agent": "Mozilla/5.0"}

    # ✅ OTP 요청 URL
    otp_url = "http://data.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd"
    otp_data = {
        "locale": "ko_KR",
        "mktId": "STK" if market == "KOSPI" else "KSQ",  # KOSPI: STK, KOSDAQ: KSQ
        "trdDd": pd.to_datetime("today").strftime("%Y%m%d"),
        "share": "1",
        "money": "1",
        "csvxls_isNo": "false",
        "name": "fileDown",
        "url": "dbms/MDC/STAT/standard/MDCSTAT03901",
    }

    # ✅ OTP 요청
    otp_response = requests.post(otp_url, data=otp_data, headers=headers)
    otp_code = otp_response.text.strip()

    # ✅ KRX 데이터 다운로드 URL
    download_url = "http://data.krx.co.kr/comm/fileDn/download_csv/download.cmd"
    download_response = requests.post(
        download_url, data={"code": otp_code}, headers=headers
    )

    # ✅ 📌 인코딩 변환 (한글 깨짐 방지)
    decoded_content = download_response.content.decode(
        "EUC-KR", errors="replace"
    )  # 🔹 인코딩 변환
    df = pd.read_csv(io.StringIO(decoded_content))

    # ✅ 컬럼명 변경
    df = df.rename(
        columns={
            "종목코드": "Symbol",
            "종목명": "Name",
            "업종명": "Sector",  # ✅ 업종명 → Sector로 매핑
        }
    )

    return df[["Symbol", "Name", "Sector"]]


# ✅ CSV 파일 업데이트 함수
def update_ticker_csv(market: str, file_path: str):
    """기존 CSV 파일을 읽고 업종(Sector) 정보를 추가하여 업데이트"""
    if not os.path.exists(file_path):
        print(f"❌ 파일이 존재하지 않습니다: {file_path}")
        return

    # ✅ 기존 종목 리스트 불러오기
    df = pd.read_csv(file_path)

    # ✅ 기존 Sector, Industry 컬럼 제거 (중복 방지)
    if "Sector" in df.columns and "Industry" in df.columns:
        df.drop(columns=["Sector", "Industry"], inplace=True)

    # ✅ KRX에서 최신 업종(Sector) 정보 가져오기
    krx_data = fetch_krx_sector_data(market)

    # ✅ Symbol 기준으로 병합 (업종 추가)
    df = df.merge(krx_data, on=["Symbol", "Name"], how="left")

    # ✅ 업데이트된 데이터 저장
    df.to_csv(file_path, index=False)
    print(f"✅ {file_path} 업데이트 완료! ({len(df)}개)")


if __name__ == "__main__":
    # ✅ CSV 파일 경로
    DATA_PATH = "data/"
    KOSPI_FILE = os.path.join(DATA_PATH, "kospi_tickers.csv")
    KOSDAQ_FILE = os.path.join(DATA_PATH, "kosdaq_tickers.csv")

    # ✅ KOSPI & KOSDAQ 티커 리스트 업데이트
    update_ticker_csv("KOSPI", KOSPI_FILE)
    update_ticker_csv("KOSDAQ", KOSDAQ_FILE)

    print("🎉 KOSPI & KOSDAQ 업종/산업 정보 업데이트 완료!")
