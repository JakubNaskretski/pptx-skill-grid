"""matrix_2x2 — title + 2×2 grid of cards (image + label + body).

Generic 2×2 layout for any image-and-content matrix. team_grid_2x2 is the
team-specific specialization of this pattern.

content:
  title  (str, optional)
  items  (list[{image, label, body?}], 4)
         image can be 'asset_id' string OR {asset_id, fit} OR {placeholder, label}

Layout:
  title rows 1-2 cols 1-12
  Each card is 5 cols wide × 4 rows tall, with a 2-col gap between
  left/right cards (cols 6-7) and a 1-row gap between top/bottom (row 7).
    top-left:     rows 3-6  cols 1-5
    top-right:    rows 3-6  cols 8-12
    bottom-left:  rows 8-11 cols 1-5
    bottom-right: rows 8-11 cols 8-12

  Inside each card: image (2 cols) + text (3 cols). Text sits at rows
  row_start+1 to row_start+2 so it visually centers against the 4-row image.
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

    # Each card: 4 rows × 5 cols. Image: 2 cols (img_col, +1). Text: 3 cols.
    card_positions = [
        {"row": 3,  "img_col": 1, "txt_col": 3},   # top-left, card cols 1-5
        {"row": 3,  "img_col": 8, "txt_col": 10},  # top-right, card cols 8-12
        {"row": 8,  "img_col": 1, "txt_col": 3},   # bottom-left
        {"row": 8,  "img_col": 8, "txt_col": 10},  # bottom-right
    ]
    for pos, item in zip(card_positions, items):
        image = item.get("image") or {"placeholder": True, "label": "image"}
        if isinstance(image, str):
            image_content = {"asset_id": image, "fit": "fill"}
        elif isinstance(image, dict) and "asset_id" not in image and "placeholder" not in image:
            image_content = {"placeholder": True, "label": "image"}
        else:
            image_content = image

        # Image: 4 rows tall × 2 cols wide
        placements.append({
            "type": "image",
            "grid": {"row": pos["row"], "col": pos["img_col"],
                     "row_span": 4, "col_span": 2},
            "content": image_content,
        })
        # Label: 1 row tall, positioned at row+1 of the card (visual middle).
        # vertical_anchor=bottom so the label sits right above the body.
        placements.append({
            "type": "heading",
            "level": "h3",
            "vertical_anchor": "bottom",
            "grid": {"row": pos["row"], "col": pos["txt_col"],
                     "row_span": 2, "col_span": 3},
            "content": item.get("label", ""),
        })
        # Body: 2 rows below label.
        body = item.get("body")
        if body:
            placements.append({
                "type": "text",
                "level": "body",
                "vertical_anchor": "top",
                "grid": {"row": pos["row"] + 2, "col": pos["txt_col"],
                         "row_span": 2, "col_span": 3},
                "content": body,
            })

    return placements
