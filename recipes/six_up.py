"""six_up — title + 6 cells in a 3×2 grid (icon + label + body each).

For "Six Content" patterns where each item has equal weight and similar
shape. If items also need prominent numbers, use numbered_list_6up.

content:
  title  (str, optional)
  items  (list[{icon_asset_id?, label, body}], 6)

Layout:
  title rows 1-2 cols 1-12
  6 cells in 3 cols × 2 rows. Each cell 4 col_span × 5 row_span:
    top row of items: rows 3-7   cols 1-4 / 5-8 / 9-12
    bot row of items: rows 8-12  cols 1-4 / 5-8 / 9-12
  Per cell: icon_label rows R..R+1 (2 rows) + body rows R+2..R+4 (3 rows)
"""

from __future__ import annotations


def build(content: dict, **params) -> list[dict]:
    title = content.get("title")
    items = list(content.get("items", []))[:6]
    while len(items) < 6:
        items.append({"label": "", "body": "", "icon_asset_id": None})

    placements = []
    if title:
        placements.append({
            "type": "heading",
            "level": "h1",
            "grid": {"row": 1, "col": 1, "row_span": 2, "col_span": 12},
            "content": title,
        })

    cell_positions = [
        (3, 1), (3, 5), (3, 9),
        (8, 1), (8, 5), (8, 9),
    ]
    # icon_label rows R-R+1 (2 rows), body rows R+2..R+4 (3 rows). No
    # explicit gap row — icon_label's MIDDLE anchor already provides
    # visual breathing room between label and body.
    for (row, col), item in zip(cell_positions, items):
        placements.append({
            "type": "icon_label",
            "grid": {"row": row, "col": col, "row_span": 2, "col_span": 4},
            "content": {
                "icon_asset_id": item.get("icon_asset_id"),
                "label": item.get("label", ""),
            },
        })
        body = item.get("body")
        if body:
            placements.append({
                "type": "text",
                "level": "body",
                "grid": {"row": row + 2, "col": col, "row_span": 3, "col_span": 4},
                "content": body,
            })

    return placements
