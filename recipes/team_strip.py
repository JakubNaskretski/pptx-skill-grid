"""team_strip — title + 4 team cards in a single horizontal row.

Matches the source deck's slide-5 layout. Each card: photo at top, name +
role + optional bio below.

content:
  {
    "title": "Our team",
    "members": [
      {"photo": "asset_id" | {"placeholder": true}, "name": "...",
       "role": "...", "bio": "..."?},
      ... up to 4
    ]
  }

If `members` < 4, only that many cards are drawn (no padding).
If `members` > 4, extras are ignored (use team_grid_2x2 for 4 / a different
layout for >4).
"""

from __future__ import annotations


def build(content: dict, **params) -> list[dict]:
    title = content.get("title", "")
    members = content.get("members", [])[:4]

    placements = []
    if title:
        placements.append({
            "type": "heading",
            "level": "h1",
            "grid": {"row": 1, "col": 1, "row_span": 2, "col_span": 12},
            "content": title,
        })

    # 4 columns evenly distributed: starts 1, 4, 7, 10, span 3 each.
    col_starts = [1, 4, 7, 10]
    for col, member in zip(col_starts, members):
        photo = member.get("photo") or {"placeholder": True, "label": "team photo"}
        if isinstance(photo, str):
            photo_content = {"asset_id": photo, "fit": "fill"}
        elif isinstance(photo, dict) and "asset_id" not in photo and "placeholder" not in photo:
            photo_content = {"placeholder": True, "label": "team photo"}
        else:
            photo_content = photo

        # Photo: rows 3-7 (5 rows), col_span 3 → aspect ~0.81
        placements.append({
            "type": "image",
            "grid": {"row": 3, "col": col, "row_span": 5, "col_span": 3},
            "content": photo_content,
        })
        # Name (row 8): h3
        placements.append({
            "type": "heading",
            "level": "h3",
            "grid": {"row": 8, "col": col, "row_span": 1, "col_span": 3},
            "content": member.get("name", ""),
        })
        # Role (row 9): caption, secondary color
        placements.append({
            "type": "text",
            "level": "caption",
            "color_key": "text_secondary",
            "grid": {"row": 9, "col": col, "row_span": 1, "col_span": 3},
            "content": member.get("role", ""),
        })
        # Bio (rows 10-12): body
        bio = member.get("bio")
        if bio:
            placements.append({
                "type": "text",
                "level": "body",
                "grid": {"row": 10, "col": col, "row_span": 3, "col_span": 3},
                "content": bio,
            })

    return placements
