#!/usr/bin/env python3
"""Regenerate index.html from games/*.html — run after adding a game.

A game is `games/<slug>.html` (the replay); an optional companion
`games/<slug>-report.html` (the written analysis) joins the same card.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).parent

CARD = """    <div class=card>
      <div class=title>{title}</div>
      <div class=meta>{meta}</div>
      <div class=links><a href="games/{fn}">▶ replay</a>{report}</div>
    </div>"""

PAGE = """<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Old World Replays</title>
<style>
 body{{margin:0;background:#0b0c0f;color:#dfe2e6;font:15px/1.5 system-ui}}
 header{{background:#15171c;border-bottom:1px solid #2a2d34;padding:18px 22px}}
 header b{{color:#ffd27a;font-size:20px}}
 header .sub{{color:#9aa1ab;font-size:13px;margin-top:4px;max-width:80ch}}
 header a{{color:#6a9bb5}}
 #grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));
   gap:12px;padding:18px 22px;max-width:1100px}}
 .card{{background:#15171c;border:1px solid #2a2d34;border-radius:10px;padding:14px 16px}}
 .card .title{{font-weight:700;color:#ffd27a;font-size:16px}}
 .card .meta{{color:#9aa1ab;font-size:12px;margin-top:4px}}
 .card .links{{margin-top:10px;display:flex;gap:14px}}
 .card .links a{{color:#dfe2e6;text-decoration:none;background:#1b1e24;
   border:1px solid #3a3d44;border-radius:6px;padding:5px 12px;font-size:13px}}
 .card .links a:hover{{border-color:#ffd27a}}
 .card .links a.rep{{color:#e8c9a0;border-color:#6b4a1f}}
 .note{{max-width:1100px;margin:0 auto;padding:0 22px 18px;color:#9aa1ab;font-size:12.5px}}
 .note b{{color:#e8c9a0}}
</style></head><body>
<header><b>Old World Replays</b>
<div class=sub>experimental replay viewer for Old World games — turn-by-turn dual-POV
replays reconstructed from cloud-save archives · bright = visible, dim = explored,
dark = unexplored · built with
<a href="https://github.com/alcaras/ow-replay-analyzer">ow-replay-analyzer</a></div></header>
<div id=grid>
{cards}
</div>
<div class=note><b>⚠ About the analysis reports:</b> they're written by Claude (an AI)
from data extracted out of the save files. The extraction is validated against the game's
own recorded numbers, but the interpretation is a machine's, not a strong player's —
causal claims are inference and mistakes are likely. Read them as prompts for your own
analysis.</div>
</body></html>
"""


def main():
    # optional manual metadata for games whose final save isn't archived
    meta_path = ROOT / "games.json"
    manual = json.loads(meta_path.read_text()) if meta_path.exists() else {}
    cards = []
    for p in sorted((ROOT / "games").glob("*.html")):
        if p.stem.endswith("-report"):
            continue
        html = p.read_text()
        m = re.search(r'"game":"([^"]*)"', html)
        game = m.group(1) if m else p.stem
        go = re.search(r'"gameOver":\{"team":\d+,"winner":"([^"]*)","victory":"([^"]*)","turn":(\d+)\}', html)
        if go:
            game += f" — 🏆 {go.group(1)} by {go.group(2)} T{go.group(3)}"
        elif p.stem in manual and manual[p.stem].get("result"):
            game += f" — {manual[p.stem]['result']}"
        meta = f"{p.stat().st_size // 1024 // 1024} MB"
        tmax = re.findall(r'\{"t":(\d+),"tiles"', html)
        if tmax:
            meta = f"turns {tmax[0]}–{tmax[-1]} · " + meta
        players = re.search(r'"players":({.*?}})', html)
        if players:
            try:
                pl = json.loads(players.group(1))
                meta = " vs ".join(f"{v['name']} ({v['nation']})" for v in pl.values()) + " · " + meta
            except Exception:
                pass
        rp = p.with_name(p.stem + "-report.html")
        report = (f'<a class=rep href="games/{rp.name}">📊 AI analysis</a>'
                  if rp.exists() else "")
        if p.stem in manual and manual[p.stem].get("note"):
            meta += " · " + manual[p.stem]["note"]
        cards.append(CARD.format(fn=p.name, title=game, meta=meta, report=report))
    (ROOT / "index.html").write_text(PAGE.format(cards="\n".join(cards)))
    print(f"index.html: {len(cards)} game(s)")


if __name__ == "__main__":
    main()
