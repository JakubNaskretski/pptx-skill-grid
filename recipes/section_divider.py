"""section_divider — big orange numeral + section label.

Layout varies by alignment:
  right (default): number rows 4-9 cols 9-11 (right-aligned, inset 1 col from
                   right edge), label rows 10-12 cols 1-8 bottom-left
  left:            number rows 4-9 cols 2-4  (left-aligned, inset 1 col from
                   left edge),  label rows 10-12 cols 5-12 bottom-right
  center:          number rows 3-8 cols 5-8 (centered), label rows 9-11 cols 1-12

content:
  number      (str|int, required)
  label       (str, required)
  alignment   ('right' default | 'left' | 'center')

This inset position (1 col from each edge) was tuned from the reference
branded deck — flush-edge feels cramped at 240pt.
"""

from __future__ import annotations


def build(content: dict, **params) -> list[dict]:
    number = content.get("number", "")
    label = content.get("label", "")
    alignment = content.get("alignment", "right")

    if alignment == "left":
        return [
            {
                "type": "heading",
                "level": "section_number",
                "alignment": "left",
                "color_key": "accent_secondary",
                "grid": {"row": 4, "col": 2, "row_span": 6, "col_span": 3},
                "content": str(number),
            },
            {
                "type": "heading",
                "level": "h1",
                "alignment": "right",
                "grid": {"row": 10, "col": 5, "row_span": 3, "col_span": 8},
                "content": label,
            },
        ]
    if alignment == "center":
        return [
            {
                "type": "heading",
                "level": "section_number",
                "alignment": "center",
                "color_key": "accent_secondary",
                "grid": {"row": 3, "col": 5, "row_span": 6, "col_span": 4},
                "content": str(number),
            },
            {
                "type": "heading",
                "level": "h1",
                "alignment": "center",
                "grid": {"row": 9, "col": 1, "row_span": 3, "col_span": 12},
                "content": label,
            },
        ]
    # Default: right
    return [
        {
            "type": "heading",
            "level": "section_number",
            "alignment": "right",
            "color_key": "accent_secondary",
            "grid": {"row": 4, "col": 9, "row_span": 6, "col_span": 3},
            "content": str(number),
        },
        {
            "type": "heading",
            "level": "h1",
            "alignment": "left",
            "grid": {"row": 10, "col": 1, "row_span": 3, "col_span": 8},
            "content": label,
        },
    ]
