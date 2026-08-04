# owreplays

Shareable turn-by-turn Old World replays, reconstructed from per-turn
cloud-save archives by [owdeepanalysis](../owdeepanalysis/). Each game is a
single self-contained HTML file (map + fog + units + per-turn reports for
both POVs, icons and data inlined) — works from GitHub Pages, a file share,
or a Discord attachment.

## Adding a game

```sh
cd ../owdeepanalysis
python3 viewer_export.py "/path/to/owsaves/mp-archive/<game>" --out viewer
python3 package_viewer.py --viewer viewer --out "../owreplays/games/<slug>.html"
cd ../owreplays && python3 build_index.py
```

Then commit + push; Pages serves `index.html` with a card per game.
