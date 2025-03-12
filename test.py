import pandas as pd
import os


def fix_sector_column(file_path):
    """중복된 Sector_x, Sector_y 컬럼을 정리하여 하나의 Sector 컬럼으로 유지"""
    if not os.path.exists(file_path):
        print(f"❌ 파일이 존재하지 않습니다: {file_path}")
        return

    df = pd.read_csv(file_path)

    # ✅ Sector_x, Sector_y가 존재하는 경우 정리
    if "Sector_x" in df.columns and "Sector_y" in df.columns:
        df["Sector"] = df["Sector_x"].combine_first(df["Sector_y"])  # 우선순위 적용
        df.drop(columns=["Sector_x", "Sector_y"], inplace=True)  # 불필요한 컬럼 제거

    # ✅ 정리된 CSV 저장
    df.to_csv(file_path, index=False)
    print(f"✅ {file_path} 중복 Sector 컬럼 정리 완료! ({len(df)}개)")


if __name__ == "__main__":
    # ✅ CSV 파일 경로
    DATA_PATH = "data/"
    KOSPI_FILE = os.path.join(DATA_PATH, "kospi_tickers.csv")
    KOSDAQ_FILE = os.path.join(DATA_PATH, "kosdaq_tickers.csv")

    # ✅ KOSPI & KOSDAQ 중복 Sector 정리 실행
    fix_sector_column(KOSPI_FILE)
    fix_sector_column(KOSDAQ_FILE)

    print("🎉 KOSPI & KOSDAQ 중복 Sector 컬럼 정리 완료!")
