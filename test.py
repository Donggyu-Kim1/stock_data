import os
import pandas as pd

# ✅ 저장된 파일 경로 설정
data_folder = "data"
is_cleaned_path = os.path.join(data_folder, "손익계산서_정리.csv")
bs_cleaned_path = os.path.join(data_folder, "재무상태표_정리.csv")
cf_cleaned_path = os.path.join(data_folder, "현금흐름표_정리.csv")

# ✅ CSV 파일 불러오기
df_is = pd.read_csv(is_cleaned_path)
df_bs = pd.read_csv(bs_cleaned_path)
df_cf = pd.read_csv(cf_cleaned_path)

# ✅ `label_ko` 데이터만 추출하여 고유 값 리스트 생성
is_labels = df_is["label_ko"].unique().tolist()
bs_labels = df_bs["label_ko"].unique().tolist()
cf_labels = df_cf["label_ko"].unique().tolist()

# ✅ 파일로 저장 (각 재무제표의 `label_ko` 목록)
is_labels_path = os.path.join(data_folder, "손익계산서_항목목록.txt")
bs_labels_path = os.path.join(data_folder, "재무상태표_항목목록.txt")
cf_labels_path = os.path.join(data_folder, "현금흐름표_항목목록.txt")

with open(is_labels_path, "w", encoding="utf-8") as f:
    f.write("\n".join(is_labels))

with open(bs_labels_path, "w", encoding="utf-8") as f:
    f.write("\n".join(bs_labels))

with open(cf_labels_path, "w", encoding="utf-8") as f:
    f.write("\n".join(cf_labels))

print(
    f"✅ `label_ko` 데이터 추출 완료! \n - {is_labels_path} \n - {bs_labels_path} \n - {cf_labels_path}"
)
