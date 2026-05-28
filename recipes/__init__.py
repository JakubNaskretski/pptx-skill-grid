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
    table_with_callout,
    three_up,
    quote,
    cta_closing,
    team_strip,
    team_grid_2x2,
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
    "table_with_callout": table_with_callout.build,
    "three_up": three_up.build,
    "quote": quote.build,
    "cta_closing": cta_closing.build,
    "team_strip": team_strip.build,
    "team_grid_2x2": team_grid_2x2.build,
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
        "content": {
            "title": "str (required)",
            "table": "{rows, cols, has_header, data: [[...]], style?}",
        },
        "params": {},
        "use_when": "Title + full-width table. table.style: header_accent (default) | zebra_neutral | filled_accent | filled_neutral | minimal.",
    },
    "table_with_callout": {
        "content": {
            "title": "str (required)",
            "callout_heading": "str (optional, left h2)",
            "callout_body": "str|list[str] (optional, left bullets)",
            "table": "{rows, cols, has_header, data: [[...]], style?}",
        },
        "params": {},
        "use_when": "Title + callout text (left half) + branded table (right half). Matches the source deck's branded-table layout.",
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
    "team_strip": {
        "content": {
            "title": "str (optional)",
            "members": "list[{photo, name, role, bio?}] (up to 4, one row)",
        },
        "params": {},
        "use_when": "Up to 4 team members across one row. Photos top, name + role + bio below each. Matches source deck's slide-5 layout.",
    },
    "team_grid_2x2": {
        "content": {
            "title": "str (optional)",
            "members": "list[{photo, name, role, bio?}] (exactly 4)",
        },
        "params": {},
        "use_when": "4 team members in 2x2 grid with photo-left, text-right. More room for bio than team_strip. Matches source deck's slide-6 layout.",
    },
}
