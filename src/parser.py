import os
import pandas as pd


def load_lotto_data(file_path: str = "data/복권_모음집.xlsx"):
  candidates = [
      file_path,
      os.path.join(os.getcwd(), file_path),
      "data/복권_모음집.xlsx",
      "data/복권_모음집_최신판.xlsx",
      "data/복권_모음집_최신판_2.xlsx",
  ]

  found_path = None
  for cand in candidates:
    if os.path.exists(cand):
      found_path = cand
      break

  if not found_path:
    raise FileNotFoundError(f"엑셀 데이터를 찾을 수 없습니다: {file_path}")

  # Sheet1의 3번째 행(인덱스 2)부터 헤더 파싱
  df_raw = pd.read_excel(found_path, sheet_name="Sheet1", skiprows=2)
  df = df_raw.iloc[1:].dropna(subset=[df_raw.columns[5]]).iloc[:, 4:13]
  df.columns = [
      "날짜",
      "회차",
      "n1",
      "n2",
      "n3",
      "n4",
      "n5",
      "n6",
      "bonus",
  ]

  for c in ["회차", "n1", "n2", "n3", "n4", "n5", "n6", "bonus"]:
    df[c] = pd.to_numeric(df[c], errors="coerce").astype(int)

  df_sorted = df.sort_values("회차").reset_index(drop=True)
  return df_sorted, found_path