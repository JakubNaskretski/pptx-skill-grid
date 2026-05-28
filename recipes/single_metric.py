"""single_metric — one hero KPI with supporting copy.

Matches "Big Data", "Big Data 2", "Text and Large Stat" patterns.

content:
  title    (str, optional)        — page title h1
  value    (str, required)        — the big number/word (uses hero_metric)
  caption  (str, optional)        — short attribution / context, rendered in
                                    the footer strip so it doesn't crowd the
                                    big number
  body     (str|list, optional)   — supporting paragraph/bullets to the right

Layout:
  title    rows 1-2   cols 1-12
  value    rows 3-10  cols 1-8    (accent_primary, hero_metric @ 160pt)
  body     rows 3-10  cols 9-12   (right column)
  caption  footer strip (full width, secondary text)
"""

from __future__ import annotations


def build(content: dict, **params) -> list[dict]:
    title = content.get("title")
    value = content.get("value", "")
    caption = content.get("caption")
    body = content.get("body")

    placements = []
    if title:
        placements.append({
            "type": "heading",
            "level": "h1",
            "grid": {"row": 1, "col": 1, "row_span": 2, "col_span": 12},
            "content": title,
        })

    placements.append({
        "type": "heading",
        "level": "hero_metric",
        "color_key": "accent_primary",
        "vertical_anchor": "middle",
        "grid": {"row": 3, "col": 1, "row_span": 8, "col_span": 8},
        "content": str(value),
    })

    if body:
        placements.append({
            "type": "text",
            "level": "body",
            "vertical_anchor": "middle",
            "grid": {"row": 3, "col": 9, "row_span": 8, "col_span": 4},
            "content": body,
        })

    if caption:
        placements.append({
            "type": "text",
            "level": "caption",
            "color_key": "text_secondary",
            "alignment": "left",
            "grid": {"strip": "footer"},
            "content": caption,
        })

    return placements
