import os
import pandas as pd
import dart_fss as fss

# ✅ DART API 키 설정
DART_API_KEY = os.getenv("DART_API_KEY", "")  # 환경변수에서 API 키 가져오기
fss.set_api_key(api_key=DART_API_KEY)  # ✅ API 키 등록

# ✅ 기업 목록 가져오기
corp_list = fss.get_corp_list()

# ✅ 삼성전자 찾기
samsung = corp_list.find_by_corp_name("삼성전자", exactly=True)[0]

# ✅ 2024년부터 연간 연결재무제표 불러오기
fs = samsung.extract_fs(bgn_de="20240101")

# ✅ 손익계산서(IS) & 재무상태표(BS) 데이터 추출
df_is = fs["is"]
df_bs = fs["bs"]
df_cf = fs["cf"]

# ✅ MultiIndex를 해제하고 CSV로 저장
data_folder = "data"
os.makedirs(data_folder, exist_ok=True)  # 폴더 생성

df_is_reset = df_is.reset_index()  # MultiIndex 해제
df_bs_reset = df_bs.reset_index()  # MultiIndex 해제
df_cf_reset = df_cf.reset_index()  # MultiIndex 해제

# ✅ CSV 파일로 저장
is_filepath = os.path.join(data_folder, "손익계산서.csv")
bs_filepath = os.path.join(data_folder, "재무상태표.csv")
cf_filepath = os.path.join(data_folder, "현금흐름표.csv")

df_is_reset.to_csv(is_filepath, index=False, encoding="utf-8-sig")
df_bs_reset.to_csv(bs_filepath, index=False, encoding="utf-8-sig")
df_cf_reset.to_csv(cf_filepath, index=False, encoding="utf-8-sig")

print(f"\n✅ 손익계산서 저장 완료: {is_filepath}")
print(f"✅ 재무상태표 저장 완료: {bs_filepath}")
print(f"✅ 현금흐름표 저장 완료: {cf_filepath}")
