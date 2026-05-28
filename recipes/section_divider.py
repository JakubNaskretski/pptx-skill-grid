"""section_divider — big orange numeral + section label.

Layout varies by alignment:
  right (default): number rows 3-9 cols 9-11 (right-aligned, inset 1 col from
                   right edge), label rows 11-12 cols 1-8 bottom-left
  left:            number rows 3-9 cols 2-4  (left-aligned, inset 1 col from
                   left edge),  label rows 11-12 cols 5-12 bottom-right
  center:          number rows 3-9 cols 5-8  (centered), label rows 11-12 cols 1-12

content:
  number      (str|int, required)
  label       (str, required)
  alignment   ('right' default | 'left' | 'center')

Number cell is 7 rows tall (3-9) so 240pt text fits with vertical headroom
(no overlap into label). Row 10 is an explicit gap. word_wrap is disabled
on section_number in the heading renderer so e.g. "01" stays on one line.
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
                "grid": {"row": 3, "col": 2, "row_span": 7, "col_span": 3},
                "content": str(number),
            },
            {
                "type": "heading",
                "level": "h1",
                "alignment": "right",
                "grid": {"row": 11, "col": 5, "row_span": 2, "col_span": 8},
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
                "grid": {"row": 3, "col": 5, "row_span": 7, "col_span": 4},
                "content": str(number),
            },
            {
                "type": "heading",
                "level": "h1",
                "alignment": "center",
                "grid": {"row": 11, "col": 1, "row_span": 2, "col_span": 12},
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
            "grid": {"row": 3, "col": 9, "row_span": 7, "col_span": 3},
            "content": str(number),
        },
        {
            "type": "heading",
            "level": "h1",
            "alignment": "left",
            "grid": {"row": 11, "col": 1, "row_span": 2, "col_span": 8},
            "content": label,
        },
    ]
