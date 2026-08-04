#!/usr/bin/env python3
"""Regenerate index.html from games/*.html — run after adding a game."""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent

CARD = """    <a class=card href="games/{fn}">
      <div class=title>{title}</div>
      <div class=meta>{meta}</div>
    </a>"""

PAGE = """<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Old World Replays</title>
<style>
 body{{margin:0;background:#0b0c0f;color:#dfe2e6;font:15px/1.5 system-ui}}
 header{{background:#15171c;border-bottom:1px solid #2a2d34;padding:18px 22px}}
 header b{{color:#ffd27a;font-size:20px}}
 header .sub{{color:#9aa1ab;font-size:13px;margin-top:4px}}
 #grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));
   gap:12px;padding:18px 22px;max-width:1100px}}
 .card{{display:block;background:#15171c;border:1px solid #2a2d34;border-radius:10px;
   padding:14px 16px;text-decoration:none;color:inherit}}
 .card:hover{{border-color:#ffd27a}}
 .card .title{{font-weight:700;color:#ffd27a;font-size:16px}}
 .card .meta{{color:#9aa1ab;font-size:12px;margin-top:4px}}
</style></head><body>
<header><b>Old World Replays</b>
<div class=sub>experimental replay viewer for Old World games — turn-by-turn dual-POV
replays reconstructed from cloud-save archives · bright = visible, dim = explored,
dark = unexplored · vision is a geometric approximation</div></header>
<div id=grid>
{cards}
</div></body></html>
"""


def main():
    cards = []
    for p in sorted((ROOT / "games").glob("*.html")):
        html = p.read_text()
        m = re.search(r'"game":"([^"]*)"', html)
        game = m.group(1) if m else p.stem
        players = re.search(r'"players":({.*?}})', html)
        meta = f"{p.stat().st_size // 1024 // 1024} MB"
        tm = re.search(r'"turns":\[{"t":(\d+)', html)
        tmax = re.findall(r'\{"t":(\d+),"tiles"', html)
        if tmax:
            meta = f"turns {tmax[0]}–{tmax[-1]} · " + meta
        if players:
            try:
                pl = json.loads(players.group(1))
                names = " vs ".join(f"{v['name']} ({v['nation']})" for v in pl.values())
                meta = names + " · " + meta
            except Exception:
                pass
        cards.append(CARD.format(fn=p.name, title=game, meta=meta))
    (ROOT / "index.html").write_text(PAGE.format(cards="\n".join(cards)))
    print(f"index.html: {len(cards)} game(s)")


if __name__ == "__main__":
    main()
