"""big_statement — large declarative text, optional sub-line.

Smaller than section_number (240pt), bigger than h1 (36pt). Uses the
'statement' type level (60pt). Use for hero/cover-style proclamations:
"We're not slowing down." / "$1B in pipeline." / "Three things matter."

content:
  statement   (str, required)
  sub         (str, optional)               — smaller line below
  alignment   ('left' default | 'center')

Layout:
  statement rows 4-7 cols 1-10 (if left) or 1-12 (if center)
  sub       rows 8-9 cols 1-10 (if left) or 1-12 (if center)
"""

from __future__ import annotations


def build(content: dict, **params) -> list[dict]:
    statement = content.get("statement", "")
    sub = content.get("sub")
    alignment = content.get("alignment", "left")

    if alignment == "center":
        col_start, col_span = 1, 12
    else:
        col_start, col_span = 1, 10

    placements = [
        {
            "type": "heading",
            "level": "statement",
            "alignment": alignment,
            "grid": {"row": 4, "col": col_start, "row_span": 4, "col_span": col_span},
            "content": statement,
        }
    ]
    if sub:
        placements.append({
            "type": "text",
            "level": "body",
            "alignment": alignment,
            "color_key": "text_secondary",
            "grid": {"row": 9, "col": col_start, "row_span": 2, "col_span": col_span},
            "content": sub,
        })
    return placements
