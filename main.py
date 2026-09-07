import argparse
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from src.filter import LottoFilter
from src.generator import LottoGenerator
from src.parser import load_lotto_data
from src.stats import LottoStats
from src.updater import update_lotto_excel

console = Console()


def run_update():
  console.print(
      Panel(
          "[bold cyan]📥 새로운 회차 당첨 번호 엑셀 업데이트[/bold cyan]",
          expand=False,
      )
  )
  try:
    r_num = int(input("• 회차 (예: 1241): ").strip())
    raw_nums = input(
        "• 당첨 번호 6개 (공백 구분, 예: 3 7 11 24 33 42): "
    ).strip()
    nums = [int(x) for x in raw_nums.split()]
    bonus = int(input("• 보너스 번호 1개 (예: 18): ").strip())
    date_input = input(
        "• 추첨 일자 (엔터 시 오늘 날짜 자동, 예: 2026-09-12): "
    ).strip()

    if len(nums) != 6:
      console.print("[bold red]❌ 번호는 정확히 6개여야 합니다.[/bold red]")
      return

    update_lotto_excel(
        round_num=r_num,
        nums=nums,
        bonus=bonus,
        date_str=date_input if date_input else None,
    )
  except Exception as e:
    console.print(f"[bold red]❌ 입력 처리 중 오류 발생:[/bold red] {e}")


def run_generation(num_sets: int, file_path: str):
  df_history, loaded_path = load_lotto_data(file_path)
  stats = LottoStats(df_history)
  lotto_filter = LottoFilter(df_history)
  generator = LottoGenerator(stats, lotto_filter)

  # 1. 통계 요약 브리핑
  stat_table = Table(
      title=f"📊 로또 6/45 역대 통계 브리핑 (1회 ~ {stats.latest_round}회)",
      style="bold green",
  )
  stat_table.add_column("분류", style="cyan", width=18)
  stat_table.add_column("데이터 및 반영 비율", style="yellow")

  top10_str = ", ".join(f"{n:02d}" for n in stats.top10_list)
  recent_str = ", ".join(f"{n:02d}" for n in stats.recent_numbers)

  stat_table.add_row("누적 분석 회차", f"{stats.total_draws:,} 회")
  stat_table.add_row(
      f"직전 {stats.latest_round}회 당첨번호",
      f"[bold white]{recent_str}[/bold white] (보너스: {stats.recent_bonus:02d})",
  )
  stat_table.add_row(
      "누적 출현 Top 10", f"[bold magenta]{top10_str}[/bold magenta]"
  )
  stat_table.add_row(
      "십의자리 가중치", "4개 구간 (63%) | 3개 구간 (37%)"
  )
  stat_table.add_row(
      "일의자리 동끝수 가중치", "동끝 1쌍 (70%) | 동끝 2쌍 (30%)"
  )
  stat_table.add_row(
      "직전 회차 이월수 가중치", "1개 이월 (71%) | 2개 이월 (29%)"
  )
  console.print(stat_table)

  # 2. 번호 생성
  combos = generator.generate(n_sets=num_sets)

  # 3. 추천 결과 테이블
  res_table = Table(
      title=(
          f"\n🎯 제 {stats.latest_round + 1}회 대비 최적 가중치 추천 번호"
          f" ({len(combos)}세트)"
      ),
      style="bold blue",
  )
  res_table.add_column("No", style="dim", width=4, justify="center")
  res_table.add_column("추천 번호 (6개)", style="bold yellow", justify="center")
  res_table.add_column("이월수", style="cyan", justify="center")
  res_table.add_column("구간", style="magenta", justify="center")
  res_table.add_column("동끝", style="green", justify="center")
  res_table.add_column("Top 10 포함", style="white", justify="center")

  for i, r in enumerate(combos, 1):
    combo_str = "  ".join(f"{x:02d}" for x in r["combo"])
    carry_str = ", ".join(f"{x:02d}" for x in r["carry"])
    top_str = ", ".join(f"{x:02d}" for x in r["top10"])
    res_table.add_row(
        f"{i:02d}",
        combo_str,
        carry_str,
        f"{r['sections']}구간",
        f"{r['dup_pairs']}쌍",
        top_str,
    )

  console.print(res_table)

  # 4. 복사용 출력
  console.print("\n[bold white on blue] 📋 복사용 텍스트 [/bold white on blue]")
  for i, r in enumerate(combos, 1):
    print(f"[{i:02d}] " + ", ".join(f"{x:02d}" for x in r["combo"]))


def main():
  parser = argparse.ArgumentParser(
      description="Lotto Weighted Pattern Generator CLI"
  )
  parser.add_argument(
      "-n", "--num", type=int, default=5, help="생성할 세트 개수 (기본값: 5)"
  )
  parser.add_argument(
      "-f",
      "--file",
      type=str,
      default="data/복권_모음집.xlsx",
      help="엑셀 파일 경로",
  )
  parser.add_argument(
      "--add",
      action="store_true",
      help="새로운 당첨 번호를 엑셀에 업데이트",
  )
  args = parser.parse_args()

  if args.add:
    run_update()
  else:
    run_generation(num_sets=args.num, file_path=args.file)


if __name__ == "__main__":
  main()