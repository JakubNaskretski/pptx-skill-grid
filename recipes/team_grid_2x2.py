"""team_grid_2x2 — title + 2x2 grid of team cards. Each card: photo left,
name+role+bio right.

Matches the source deck's slide-6 layout. Use this when 4 members need
more textual space per card than team_strip allows.

content:
  {
    "title": "Leadership team",
    "members": [
      {"photo": "asset_id" | {"placeholder": true}, "name": "...",
       "role": "...", "bio": "..."?},
      ... exactly 4 expected (positions: top-left, bottom-left, top-right,
      bottom-right)
    ]
  }

Empty member slots render their photo as a placeholder and other text
fields empty — keeps the grid balanced.
"""

from __future__ import annotations


def build(content: dict, **params) -> list[dict]:
    title = content.get("title", "")
    members = list(content.get("members", []))[:4]
    while len(members) < 4:
        members.append({})

    placements = []
    if title:
        placements.append({
            "type": "heading",
            "level": "h1",
            "grid": {"row": 1, "col": 1, "row_span": 2, "col_span": 12},
            "content": title,
        })

    # 4 cards: top-left, bottom-left, top-right, bottom-right
    # Each card: photo col_span 3, content col_span 3, total 6
    # Top row of cards: rows 3-7 (5 rows)
    # Bottom row of cards: rows 8-12 (5 rows)
    card_positions = [
        {"row": 3,  "img_col": 1, "txt_col": 4},   # top-left
        {"row": 8,  "img_col": 1, "txt_col": 4},   # bottom-left
        {"row": 3,  "img_col": 7, "txt_col": 10},  # top-right
        {"row": 8,  "img_col": 7, "txt_col": 10},  # bottom-right
    ]

    for pos, member in zip(card_positions, members):
        photo = member.get("photo") or {"placeholder": True, "label": "team photo"}
        if isinstance(photo, str):
            photo_content = {"asset_id": photo, "fit": "fill"}
        elif isinstance(photo, dict) and "asset_id" not in photo and "placeholder" not in photo:
            photo_content = {"placeholder": True, "label": "team photo"}
        else:
            photo_content = photo

        # Photo: rows pos.row .. pos.row+4 (5 rows), 3 cols wide → ~0.81 aspect
        placements.append({
            "type": "image",
            "grid": {"row": pos["row"], "col": pos["img_col"],
                     "row_span": 5, "col_span": 3},
            "content": photo_content,
        })
        # Name on the first row of the card (h3)
        placements.append({
            "type": "heading",
            "level": "h3",
            "grid": {"row": pos["row"], "col": pos["txt_col"],
                     "row_span": 1, "col_span": 3},
            "content": member.get("name", ""),
        })
        # Role on the second row (caption)
        placements.append({
            "type": "text",
            "level": "caption",
            "color_key": "text_secondary",
            "grid": {"row": pos["row"] + 1, "col": pos["txt_col"],
                     "row_span": 1, "col_span": 3},
            "content": member.get("role", ""),
        })
        # Bio fills rows 3-4 (3 rows)
        bio = member.get("bio")
        if bio:
            placements.append({
                "type": "text",
                "level": "body",
                "grid": {"row": pos["row"] + 2, "col": pos["txt_col"],
                         "row_span": 3, "col_span": 3},
                "content": bio,
            })

    return placements
