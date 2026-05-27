"""section_divider — big orange numeral on the right, section label bottom-left.

Number: rows 4-9 (6 rows = half height), cols 10-12 (3 cols), right-aligned.
Label:  rows 10-12 (3 rows), cols 1-8.
"""

from __future__ import annotations



def build(content: dict, **params) -> list[dict]:
    number = content.get("number", "")
    label = content.get("label", "")

    return [
        {
            "type": "heading",
            "level": "section_number",
            "alignment": "right",
            "color_key": "accent_secondary",
            "grid": {"row": 4, "col": 10, "row_span": 6, "col_span": 3},
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
