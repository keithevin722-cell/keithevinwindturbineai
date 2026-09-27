#!/usr/bin/env python3
"""Sync chapter 4 BOM fallback table rows from docs/data/parts-list.json."""
import json
from pathlib import Path

repo = Path(__file__).resolve().parents[1]
chapter = repo / "docs/chapters/04-parts-list.html"
source = repo / "docs/data/parts-list.json"

data = json.loads(source.read_text())
rows = []
for r in data:
    rows.append(
        f'<tr><td>{r["item"]}</td><td>{r["category"]}</td><td>{r["recommended_spec"]}</td><td>{r["approx_price_usd_estimate"]}</td><td><a href="{r["example_purchase_link"]}">Example link</a></td><td>{r["notes"]}</td></tr>'
    )

text = chapter.read_text()
start = text.index('<tbody id="bom-table-body" data-source="../data/parts-list.json">')
end = text.index('</tbody>', start) + len('</tbody>')
text = text[:start] + '<tbody id="bom-table-body" data-source="../data/parts-list.json">\n' + '\n'.join(rows) + '\n</tbody>' + text[end:]
chapter.write_text(text)
print('Synced BOM fallback table from docs/data/parts-list.json')
