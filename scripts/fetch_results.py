
import csv
import io
import re
import urllib.request
from datetime import date, timedelta
from pathlib import Path

VENUES = {
    "桐生": 1, "戸田": 2, "江戸川": 3, "平和島": 4,
    "多摩川": 5, "浜名湖": 6, "蒲郡": 7, "常滑": 8,
    "津": 9, "三国": 10, "びわこ": 11, "住之江": 12,
    "尼崎": 13, "鳴門": 14, "丸亀": 15, "児島": 16,
    "宮島": 17, "徳山": 18, "下関": 19, "若松": 20,
    "芦屋": 21, "福岡": 22, "唐津": 23, "大村": 24
}

OUTPUT = Path("data/results.csv")
URL = "https://www.boatrace.jp/owpc/pc/race/resultlist"

def fetch_day(day, venue, code):
    params = f"?hd={day:%Y%m%d}&jcd={code:02d}"
    request = urllib.request.Request(
        URL + params,
        headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        html = response.read().decode("utf-8", errors="replace")

    # Extract the trifecta section, before the next results table.
    section = html.split("3連勝単式", 1)
    if len(section) < 2:
        return []

    section = section[1].split("着順", 1)[0]
    section = re.sub(r"<[^>]+>", " ", section)
    section = re.sub(r"\s+", " ", section)

    pattern = r"(\d{1,2})R\s+([1-6])\s*-\s*([1-6])\s*-\s*([1-6])"
    rows = []
    for match in re.finditer(pattern, section):
        race, first, second, third = map(int, match.groups())
        if 1 <= race <= 12 and len({first, second, third}) == 3:
            rows.append([day.isoformat(), venue, race,
                         first, second, third])
    return rows

def main():
    today = date.today()
    rows = []
    for offset in range(1, 2):
        day = today - timedelta(days=offset)
        for venue, code in VENUES.items():
            try:
                rows.extend(fetch_day(day, venue, code))
            except Exception as exc:
                print(f"取得失敗: {day} {venue}: {exc}")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "venue", "race",
                         "first", "second", "third"])
        writer.writerows(rows)

    print(f"保存完了: {len(rows)}レース -> {OUTPUT}")

if __name__ == "__main__":
    main()
