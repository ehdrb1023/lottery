# migrate_db.py
import os
import tomllib
from pathlib import Path

import pandas as pd
from supabase import create_client, Client

ROOT = Path(__file__).resolve().parents[2]


def load_credentials():
    """앱과 같은 출처를 쓴다 — .streamlit/secrets.toml, 없으면 환경변수."""
    secrets_path = ROOT / ".streamlit" / "secrets.toml"
    if secrets_path.exists():
        with secrets_path.open("rb") as f:
            secrets = tomllib.load(f)
        url, key = secrets.get("SUPABASE_URL"), secrets.get("SUPABASE_KEY")
        if url and key:
            return url, key

    url, key = os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY")
    if url and key:
        return url, key

    raise SystemExit(
        f"자격증명을 찾을 수 없다.\n"
        f"  1) {secrets_path} 에 SUPABASE_URL / SUPABASE_KEY 를 넣거나\n"
        f"  2) 환경변수로 전달해라"
    )


url, key = load_credentials()
supabase: Client = create_client(url, key)

print("엑셀 데이터 로딩 중...")
df_raw = pd.read_excel(ROOT / "data" / "복권_모음집.xlsx", sheet_name="Sheet1", skiprows=2)
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