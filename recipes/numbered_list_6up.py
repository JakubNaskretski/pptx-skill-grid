"""numbered_list_6up — title + 6 numbered items in a 3x2 grid.

Each item has a prominent number, a label, and supporting body text. Use
for "principles", "priorities", "steps" — anything where 6 items have
equal weight and the numbers themselves carry meaning.

content:
  title  (str, optional)
  items  (list[{number?, label, body}], 1-6)
         number defaults to the 1-indexed position; pass 'number' to override
         (e.g. "01", "02" zero-padded).

Layout:
  title  rows 1-2 cols 1-12
  6 cells in 3x2 grid: 4 cols wide x 5 rows tall each.
    top row of items: rows 3-7,   cols 1-4 / 5-8 / 9-12
    bot row of items: rows 8-12,  cols 1-4 / 5-8 / 9-12
  Per cell: number rows X-X+1 (metric_value 48pt accent), label row X+2 (h3),
            body rows X+3 to X+4 (body).
"""

from __future__ import annotations


def build(content: dict, **params) -> list[dict]:
    title = content.get("title")
    items = list(content.get("items", []))[:6]

    placements = []
    if title:
        placements.append({
            "type": "heading",
            "level": "h1",
            "grid": {"row": 1, "col": 1, "row_span": 2, "col_span": 12},
            "content": title,
        })

    cell_positions = [
        # (row_start, col_start) for the 6 cells (3 across × 2 down)
        (3, 1), (3, 5), (3, 9),
        (8, 1), (8, 5), (8, 9),
    ]
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            item = {"label": str(item), "body": ""}
        row, col = cell_positions[i]
        number = item.get("number") or f"{i + 1:02d}"
        # Number — uses metric_value (48pt heading) in accent for impact
        placements.append({
            "type": "heading",
            "level": "metric_value",
            "color_key": "accent_primary",
            "grid": {"row": row, "col": col, "row_span": 2, "col_span": 4},
            "content": str(number),
        })
        # Label — h3 bold
        placements.append({
            "type": "heading",
            "level": "h3",
            "grid": {"row": row + 2, "col": col, "row_span": 1, "col_span": 4},
            "content": item.get("label", ""),
        })
        # Body — 2 rows of body text
        body = item.get("body")
        if body:
            placements.append({
                "type": "text",
                "level": "body",
                "grid": {"row": row + 3, "col": col, "row_span": 2, "col_span": 4},
                "content": body,
            })

    return placements
