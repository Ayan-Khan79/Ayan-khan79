#!/usr/bin/env python3
import json
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "contributions.json"
OUTPUT = ROOT / "assets" / "contrib-heatmap.svg"

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
CELL = 13
GAP = 4
LEFT = 42
TOP = 62
WEEKS = 53
WIDTH = LEFT + WEEKS * (CELL + GAP) + 24
HEIGHT = TOP + 7 * (CELL + GAP) + 70


def main():
    if not DATA.exists():
        raise FileNotFoundError(f"Missing contribution data: {DATA}")

    payload = json.loads(DATA.read_text(encoding="utf-8"))
    by_date = {
        date.fromisoformat(item["date"]): int(item["level"])
        for item in payload["days"]
    }

    last = max(by_date)
    end = last + timedelta(days=(6 - last.weekday()) % 7)
    start = end - timedelta(days=WEEKS * 7 - 1)

    cells = []
    cursor = start
    index = 0

    while cursor <= end:
        week = (cursor - start).days // 7
        day = cursor.weekday()
        level = max(0, min(4, by_date.get(cursor, 0)))

        x = LEFT + week * (CELL + GAP)
        y = TOP + day * (CELL + GAP)
        delay = 0.35 + index * 0.008

        cells.append(
            f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" '
            f'rx="3" fill="{PALETTE[level]}" class="cell" '
            f'style="animation-delay:{delay:.3f}s">'
            f'<title>{cursor.isoformat()} — contribution level {level}</title>'
            f'</rect>'
        )

        cursor += timedelta(days=1)
        index += 1

    stats = payload.get("stats", {})
    active_days = stats.get("active_days", 0)
    streak = stats.get("current_streak_days", 0)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg"
    width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
    <style>
      .cell {{
        opacity: 0;
        animation: appear .45s ease-out forwards;
      }}
      .title {{
        font: 700 17px ui-monospace,SFMono-Regular,Menlo,monospace;
        fill: #58a6ff;
      }}
      .meta {{
        font: 500 12px ui-monospace,SFMono-Regular,Menlo,monospace;
        fill: #8b949e;
      }}
      @keyframes appear {{
        from {{ opacity: 0; transform: translateY(-6px); }}
        to {{ opacity: 1; transform: translateY(0); }}
      }}
    </style>

    <rect x="1" y="1" rx="12" width="{WIDTH-2}" height="{HEIGHT-2}"
          fill="#0d1117" stroke="#30363d" stroke-width="2"/>

    <text class="title" x="22" y="30">
      ayan@github:~$ ./contributions.sh
    </text>

    <text class="meta" x="22" y="48">
      {active_days} active days · current streak {streak} days
    </text>

    {''.join(cells)}

    <text class="meta" x="{LEFT}" y="{HEIGHT-15}">Less</text>
    {''.join(
        f'<rect x="{LEFT + 32 + i * 19}" y="{HEIGHT-25}" '
        f'width="13" height="13" rx="3" fill="{color}"/>'
        for i, color in enumerate(PALETTE)
    )}
    <text class="meta"
          x="{LEFT + 32 + len(PALETTE) * 19 + 8}"
          y="{HEIGHT-15}">More</text>
    </svg>'''

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
