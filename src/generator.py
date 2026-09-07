from collections import Counter
import random
import numpy as np
from src.filter import LottoFilter
from src.stats import LottoStats


class LottoGenerator:

  def __init__(self, stats: LottoStats, lotto_filter: LottoFilter):
    self.stats = stats
    self.filter = lotto_filter

  def generate(self, n_sets: int = 5, seed: int = None):
    if seed:
      random.seed(seed)
      np.random.seed(seed)

    results = []
    attempts = 0

    while len(results) < n_sets and attempts < 100000:
      attempts += 1

      # 1. 실제 출현 비율 기반 가중치 타겟 샘플링
      n_carry = int(np.random.choice([1, 2], p=[0.71, 0.29]))
      target_secs = int(np.random.choice([3, 4], p=[0.37, 0.63]))
      target_pairs = int(np.random.choice([1, 2], p=[0.70, 0.30]))

      # 2. 이월수 추출
      carries = random.sample(self.stats.recent_numbers, n_carry)

      # 3. 비이월 번호 무작위 추출
      pool = [x for x in range(1, 46) if x not in carries]
      others = random.sample(pool, 6 - n_carry)
      combo = sorted(carries + others)

      # [검증 1] 누적 Top 10 번호 1개 이상 포함
      if not any(x in self.stats.top10_set for x in combo):
        continue

      # [검증 2] 십의자리 구간 수 검증
      secs = set(self.stats.get_decade_sec(x) for x in combo)
      if len(secs) != target_secs:
        continue

      # [검증 3] 일의자리 동끝수 패턴 검증
      ends = [x % 10 for x in combo]
      counts = sorted(list(Counter(ends).values()), reverse=True)
      if target_pairs == 1 and counts != [2, 1, 1, 1, 1]:
        continue
      if target_pairs == 2 and counts != [2, 2, 1, 1]:
        continue

      # [검증 4] 역대 1·2등 기출 필터링
      is_clean, _ = self.filter.is_clean_history(combo)
      if not is_clean:
        continue

      if combo not in [r["combo"] for r in results]:
        results.append({
            "combo": combo,
            "carry": carries,
            "sections": target_secs,
            "dup_pairs": target_pairs,
            "top10": [x for x in combo if x in self.stats.top10_set],
        })

    return results