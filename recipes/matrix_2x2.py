"""matrix_2x2 — title + 2×2 grid of cards (image + label + body).

Generic 2×2 layout for any image-and-content matrix. team_grid_2x2 is the
team-specific specialization of this pattern.

content:
  title  (str, optional)
  items  (list[{image, label, body?}], 4)
         image can be 'asset_id' string OR {asset_id, fit} OR {placeholder, label}

Layout:
  title rows 1-2 cols 1-12
  4 cells in 2 rows × 2 cols. Each cell 6 col_span × 5 row_span; inside the
  cell, image is left half (3 cols) and content is right half (3 cols).
    top-left:     rows 3-7  cols 1-6
    top-right:    rows 3-7  cols 7-12
    bottom-left:  rows 8-12 cols 1-6
    bottom-right: rows 8-12 cols 7-12
"""

from __future__ import annotations


def build(content: dict, **params) -> list[dict]:
    title = content.get("title")
    items = list(content.get("items", []))[:4]
    while len(items) < 4:
        items.append({})

    placements = []
    if title:
        placements.append({
            "type": "heading",
            "level": "h1",
            "grid": {"row": 1, "col": 1, "row_span": 2, "col_span": 12},
            "content": title,
        })

    card_positions = [
        {"row": 3, "img_col": 1, "txt_col": 4},
        {"row": 3, "img_col": 7, "txt_col": 10},
        {"row": 8, "img_col": 1, "txt_col": 4},
        {"row": 8, "img_col": 7, "txt_col": 10},
    ]
    for pos, item in zip(card_positions, items):
        image = item.get("image") or {"placeholder": True, "label": "image"}
        if isinstance(image, str):
            image_content = {"asset_id": image, "fit": "fill"}
        elif isinstance(image, dict) and "asset_id" not in image and "placeholder" not in image:
            image_content = {"placeholder": True, "label": "image"}
        else:
            image_content = image

        placements.append({
            "type": "image",
            "grid": {"row": pos["row"], "col": pos["img_col"],
                     "row_span": 5, "col_span": 3},
            "content": image_content,
        })
        # Label
        placements.append({
            "type": "heading",
            "level": "h3",
            "grid": {"row": pos["row"], "col": pos["txt_col"],
                     "row_span": 1, "col_span": 3},
            "content": item.get("label", ""),
        })
        # Body
        body = item.get("body")
        if body:
            placements.append({
                "type": "text",
                "level": "body",
                "grid": {"row": pos["row"] + 1, "col": pos["txt_col"],
                         "row_span": 4, "col_span": 3},
                "content": body,
            })

    return placements
