
import csv
from collections import Counter, defaultdict
from pathlib import Path

INPUT = Path("data/results.csv")
OUTPUT = Path("data/analysis.txt")

def analyze():
    if not INPUT.exists():
        print("結果データがありません")
        return

    with INPUT.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    valid = []
    for r in rows:
        try:
            nums = [int(r[k]) for k in ("first", "second", "third")]
            if all(1 <= n <= 6 for n in nums) and len(set(nums)) == 3:
                valid.append(r)
        except (ValueError, KeyError, TypeError):
            continue

    if not valid:
        print("分析できるレースがありません")
        return

    venues = defaultdict(list)
    for r in valid:
        venues[r["venue"]].append(r)

    lines = []
    def report(s=""):
        print(s)
        lines.append(s)

    report(f"分析レース数: {len(valid)}")
    report()

    for venue, races in sorted(venues.items()):
        total = len(races)
        wins = sum(r["first"] == "1" for r in races)
        losses = total - wins
        rate = wins / total * 100

        report(f"【{venue}】")
        report(f"レース数: {total}")
        report(f"1号艇勝率: {rate:.1f}%")
        report(f"1号艇敗退率: {losses / total * 100:.1f}%")

        patterns = Counter(
            f'{r["first"]}-{r["second"]}-{r["third"]}'
            for r in races
        )
        report("3連単出目ランキング:")
        for pattern, count in patterns.most_common(10):
            report(f"  {pattern}: {count}回")
        report()

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"保存完了: {OUTPUT}")

if __name__ == "__main__":
    analyze()
