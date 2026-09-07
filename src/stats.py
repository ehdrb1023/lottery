from collections import Counter
import pandas as pd


class LottoStats:

  def __init__(self, df_history: pd.DataFrame):
    self.df_history = df_history
    self.total_draws = len(df_history)
    self.latest_round = int(df_history.iloc[-1]["회차"])
    self.recent_numbers = [
        int(df_history.iloc[-1][f"n{i}"]) for i in range(1, 7)
    ]
    self.recent_bonus = int(df_history.iloc[-1]["bonus"])

    # 누적 최다 빈도 Top 10 산출
    all_main = []
    for _, row in df_history.iterrows():
      all_main.extend([int(row[f"n{i}"]) for i in range(1, 7)])
    self.freq_counter = Counter(all_main)
    self.top10_list = [
        num
        for num, _ in sorted(
            self.freq_counter.items(), key=lambda x: (-x[1], x[0])
        )[:10]
    ]
    self.top10_set = set(self.top10_list)

  @staticmethod
  def get_decade_sec(n: int) -> int:
    if 1 <= n <= 9:
      return 0  # 단번대
    elif 10 <= n <= 19:
      return 1  # 10번대
    elif 20 <= n <= 29:
      return 2  # 20번대
    elif 30 <= n <= 39:
      return 3  # 30번대
    else:
      return 4  # 40번대