class LottoFilter:

  def __init__(self, df_history):
    self.history_records = []
    for _, row in df_history.iterrows():
      self.history_records.append({
          "round": int(row["회차"]),
          "main": set([int(row[f"n{i}"]) for i in range(1, 7)]),
          "bonus": int(row["bonus"]),
      })

  def is_clean_history(self, combo: list[int]):
    c_set = set(combo)
    for h in self.history_records:
      inter = c_set.intersection(h["main"])
      if len(inter) == 6:
        return False, f"역대 {h['round']}회 1등 기출"
      if len(inter) == 5 and h["bonus"] in c_set:
        return False, f"역대 {h['round']}회 2등 기출"
    return True, "신규 조합"