# migrate_db.py
import os
import pandas as pd
from supabase import create_client, Client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
if not url or not key:
    raise SystemExit("SUPABASE_URL / SUPABASE_KEY 환경변수가 필요하다")

supabase: Client = create_client(url, key)

print("엑셀 데이터 로딩 중...")
df_raw = pd.read_excel("data/복권_모음집.xlsx", sheet_name="Sheet1", skiprows=2)
df = df_raw.iloc[1:].dropna(subset=[df_raw.columns[5]]).iloc[:, 4:13]
df.columns = ["날짜", "회차", "n1", "n2", "n3", "n4", "n5", "n6", "bonus"]

records = []
for _, row in df.iterrows():
    records.append({
        "round": int(row["회차"]),
        "draw_date": str(row["날짜"])[:10],
        "n1": int(row["n1"]), "n2": int(row["n2"]), "n3": int(row["n3"]),
        "n4": int(row["n4"]), "n5": int(row["n5"]), "n6": int(row["n6"]),
        "bonus": int(row["bonus"])
    })

print(f"총 {len(records)}건의 데이터 DB 업로드 시작...")
# Supabase 일괄 Insert (1천여 건은 1초면 들어갑니다)
supabase.table("lotto_history").insert(records).execute()
print("✅ Supabase 마이그레이션 완료!")