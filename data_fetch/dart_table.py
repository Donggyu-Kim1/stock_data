import os
import pandas as pd

# ✅ 저장할 폴더 생성
data_folder = "data"
os.makedirs(data_folder, exist_ok=True)

# ✅ 파일 경로
income_statement_path = os.path.join(data_folder, "손익계산서.csv")
balance_sheet_path = os.path.join(data_folder, "재무상태표.csv")
cash_flow_path = os.path.join(data_folder, "현금흐름표.csv")

# ✅ CSV 파일 불러오기
df_is = pd.read_csv(income_statement_path)
df_bs = pd.read_csv(balance_sheet_path)
df_cf = pd.read_csv(cash_flow_path)

# ✅ MultiIndex 컬럼명 단순화
df_is.columns = [
    "index",
    "concept_id",
    "label_ko",
    "label_en",
    "class0",
    "class1",
    "class2",
] + list(df_is.columns[7:])
df_bs.columns = [
    "index",
    "concept_id",
    "label_ko",
    "label_en",
    "class0",
    "class1",
    "class2",
    "class3",
    "class4",
] + list(df_bs.columns[9:])
df_cf.columns = [
    "index",
    "concept_id",
    "label_ko",
    "label_en",
    "class0",
    "class1",
    "class2",
] + list(
    df_cf.columns[7:]
)  # ✅ 현금흐름표도 동일하게 처리

# ✅ 불필요한 컬럼 제거 (index 컬럼 제거)
df_is.drop(columns=["index"], inplace=True)
df_bs.drop(columns=["index"], inplace=True)
df_cf.drop(columns=["index"], inplace=True)

# ✅ 데이터를 정규화 (Melt 변환)
df_is_melted = df_is.melt(
    id_vars=["concept_id", "label_ko", "label_en"],
    var_name="report_date",
    value_name="value",
)
df_bs_melted = df_bs.melt(
    id_vars=["concept_id", "label_ko", "label_en"],
    var_name="report_date",
    value_name="value",
)
df_cf_melted = df_cf.melt(
    id_vars=["concept_id", "label_ko", "label_en"],
    var_name="report_date",
    value_name="value",
)

# ✅ 🔹 첫 번째 행 제거 (컬럼명이 중복된 데이터 삭제)
df_is_melted_cleaned = df_is_melted.iloc[1:].reset_index(drop=True)
df_bs_melted_cleaned = df_bs_melted.iloc[1:].reset_index(drop=True)
df_cf_melted_cleaned = df_cf_melted.iloc[1:].reset_index(drop=True)

# ✅ 🔹 report_date 값이 잘못된 경우 필터링 (ex: "class0" 같은 값 제거)
df_is_melted_cleaned = df_is_melted_cleaned[
    df_is_melted_cleaned["report_date"].str.contains(r"\d{8}-\d{8}", na=False)
]
df_bs_melted_cleaned = df_bs_melted_cleaned[
    df_bs_melted_cleaned["report_date"].str.contains(r"\d{8}", na=False)
]
df_cf_melted_cleaned = df_cf_melted_cleaned[
    df_cf_melted_cleaned["report_date"].str.contains(r"\d{8}", na=False)
]

# ✅ 정리된 CSV 파일 저장 (data 폴더 내부)
is_cleaned_path = os.path.join(data_folder, "손익계산서_정리.csv")
bs_cleaned_path = os.path.join(data_folder, "재무상태표_정리.csv")
cf_cleaned_path = os.path.join(data_folder, "현금흐름표_정리.csv")

df_is_melted_cleaned.to_csv(is_cleaned_path, index=False, encoding="utf-8-sig")
df_bs_melted_cleaned.to_csv(bs_cleaned_path, index=False, encoding="utf-8-sig")
df_cf_melted_cleaned.to_csv(cf_cleaned_path, index=False, encoding="utf-8-sig")

print(
    f"✅ CSV 파일로 저장 완료! \n - {is_cleaned_path} \n - {bs_cleaned_path} \n - {cf_cleaned_path}"
)
