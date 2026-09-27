#!/usr/bin/env python3
"""Sync chapter 4 BOM fallback table rows from docs/data/parts-list.json."""
import html
import json
from pathlib import Path
from urllib.parse import urlparse


def safe_text(value: str) -> str:
    return html.escape(value or "", quote=True)


def safe_url(value: str) -> str:
    parsed = urlparse(value or "")
    if parsed.scheme in ("http", "https"):
        return html.escape(value, quote=True)
    return "#"


repo = Path(__file__).resolve().parents[1]
chapter = repo / "docs/chapters/04-parts-list.html"
source = repo / "docs/data/parts-list.json"

data = json.loads(source.read_text(encoding="utf-8"))
rows = []
for r in data:
    item = safe_text(r.get("item", ""))
    category = safe_text(r.get("category", ""))
    spec = safe_text(r.get("recommended_spec", ""))
    price = safe_text(r.get("approx_price_usd_estimate", ""))
    notes = safe_text(r.get("notes", ""))
    url = safe_url(r.get("example_purchase_link", ""))

    rows.append(
        f'<tr><td>{item}</td><td>{category}</td><td>{spec}</td><td>{price}</td><td><a href="{url}" aria-label="Example purchase link for {item}">Example link for {item}</a></td><td>{notes}</td></tr>'
    )

text = chapter.read_text(encoding="utf-8")
start = text.index('<tbody id="bom-table-body" data-source="../data/parts-list.json">')
end = text.index('</tbody>', start) + len('</tbody>')
text = text[:start] + '<tbody id="bom-table-body" data-source="../data/parts-list.json">\n' + '\n'.join(rows) + '\n</tbody>' + text[end:]
chapter.write_text(text, encoding="utf-8")
print("Synced BOM fallback table from docs/data/parts-list.json")
