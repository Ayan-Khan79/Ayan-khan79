#!/usr/bin/env python3
import json
from datetime import date, datetime, timezone, timedelta
from pathlib import Path
import requests
from bs4 import BeautifulSoup

USERNAME = "Ayan-Khan79"
URL = f"https://github.com/users/{USERNAME}/contributions"
ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "contributions.json"

def main():
    response = requests.get(URL, headers={"User-Agent": "Ayan-Khan79-profile-readme"}, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    days = {}
    for cell in soup.select("[data-date][data-level]"):
        raw_date = cell.get("data-date")
        raw_level = cell.get("data-level")
        try:
            date.fromisoformat(raw_date)
            level = max(0, min(int(raw_level), 4))
        except (TypeError, ValueError):
            continue
        days[raw_date] = level
    if not days:
        raise RuntimeError("No contribution cells found. GitHub markup may have changed.")
    ordered = [{"date": d, "level": days[d]} for d in sorted(days)]
    by_date = {date.fromisoformat(x["date"]): x["level"] for x in ordered}
    cursor = date.fromisoformat(ordered[-1]["date"])
    streak = 0
    while by_date.get(cursor, 0) > 0:
        streak += 1
        cursor -= timedelta(days=1)
    payload = {
        "username": USERNAME,
        "source": URL,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "days": ordered,
        "stats": {
            "active_days": sum(1 for x in ordered if x["level"] > 0),
            "max_level": max((x["level"] for x in ordered), default=0),
            "current_streak_days": streak,
        },
    }
    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {len(ordered)} days to {OUTPUT}")

if __name__ == "__main__":
    main()
