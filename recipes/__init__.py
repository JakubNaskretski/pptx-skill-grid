"""Recipe registry.

A recipe is a parametric function that takes content (and optional params)
and returns a list of component placements. The render engine resolves
placements to absolute coordinates via grid.py and dispatches each one to
its component renderer.

To add a recipe: create `recipes/<name>.py` exporting `build(content, **params)`
and add it to RECIPES below.
"""

from . import (
    title_only,
    section_divider,
    title_bullets,
    title_hero_image,
    text_image_split,
    two_col_text,
    comparison,
    metric_strip,
    chart_with_takeaway,
    table_full,
    three_up,
    quote,
    cta_closing,
)


RECIPES = {
    "title_only": title_only.build,
    "section_divider": section_divider.build,
    "title_bullets": title_bullets.build,
    "title_hero_image": title_hero_image.build,
    "text_image_split": text_image_split.build,
    "two_col_text": two_col_text.build,
    "comparison": comparison.build,
    "metric_strip": metric_strip.build,
    "chart_with_takeaway": chart_with_takeaway.build,
    "table_full": table_full.build,
    "three_up": three_up.build,
    "quote": quote.build,
    "cta_closing": cta_closing.build,
}


RECIPE_SIGNATURES = {
    "title_only": {
        "content": {"title": "str (required)", "subtitle": "str (optional)"},
        "params": {},
        "use_when": "Cover / opener slide.",
    },
    "section_divider": {
        "content": {"number": "str|int (required)", "label": "str (required)"},
        "params": {},
        "use_when": "Visual break between major sections. Big orange numeral right; section label bottom-left.",
    },
    "title_bullets": {
        "content": {"title": "str (required)", "bullets": "list[str] (required, max 6)"},
        "params": {},
        "use_when": "Bread-and-butter content slide. Title + bullets.",
    },
    "title_hero_image": {
        "content": {"title": "str (required)", "image": "image content (required)"},
        "params": {},
        "use_when": "Single big visual under a title.",
    },
    "text_image_split": {
        "content": {"title": "str (required)", "text": "str or list[str]", "image": "image content"},
        "params": {"image_side": "'left'|'right' (default 'right')"},
        "use_when": "Text on one side, image on the other.",
    },
    "two_col_text": {
        "content": {"title": "str (required)", "left": "str or list[str]", "right": "str or list[str]"},
        "params": {},
        "use_when": "Two parallel columns of text without labels.",
    },
    "comparison": {
        "content": {
            "title": "str (required)",
            "left_label": "str (required)",
            "right_label": "str (required)",
            "left_body": "str or list[str]",
            "right_body": "str or list[str]",
        },
        "params": {},
        "use_when": "Labeled vs / before-after comparison.",
    },
    "metric_strip": {
        "content": {
            "title": "str (optional)",
            "metrics": "list[{value, label, delta?, delta_status?}] (2-4 items)",
        },
        "params": {},
        "use_when": "2-4 KPIs displayed side-by-side. Count derived from len(metrics).",
    },
    "chart_with_takeaway": {
        "content": {
            "title": "str (required)",
            "chart": "chart content (required)",
            "takeaway": "str or list[str]",
        },
        "params": {},
        "use_when": "A chart plus a sentence/list of takeaways in a sidebar.",
    },
    "table_full": {
        "content": {"title": "str (required)", "table": "table content (required)"},
        "params": {},
        "use_when": "Title + full-width table.",
    },
    "three_up": {
        "content": {
            "title": "str (optional)",
            "items": "list[{icon_asset_id?, label, body}] (3 items)",
        },
        "params": {},
        "use_when": "Three parallel columns each with icon, label, supporting body.",
    },
    "quote": {
        "content": {"text": "str (required)", "attribution": "str (optional)"},
        "params": {},
        "use_when": "Pull-quote or testimonial.",
    },
    "cta_closing": {
        "content": {
            "title": "str (required)",
            "cta": "{label: str}",
            "contact": "str (optional)",
        },
        "params": {},
        "use_when": "Closing / next-steps / thank-you slide.",
    },
}
