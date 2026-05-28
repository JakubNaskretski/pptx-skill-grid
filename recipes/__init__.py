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
    single_metric,
    big_statement,
    agenda,
    numbered_list_6up,
    chart_with_takeaway,
    table_full,
    table_with_callout,
    three_up,
    four_up,
    six_up,
    matrix_2x2,
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
    "single_metric": single_metric.build,
    "big_statement": big_statement.build,
    "agenda": agenda.build,
    "numbered_list_6up": numbered_list_6up.build,
    "chart_with_takeaway": chart_with_takeaway.build,
    "table_full": table_full.build,
    "table_with_callout": table_with_callout.build,
    "three_up": three_up.build,
    "four_up": four_up.build,
    "six_up": six_up.build,
    "matrix_2x2": matrix_2x2.build,
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
        "content": {
            "number": "str|int (required)",
            "label": "str (required)",
            "alignment": "'right' (default) | 'left' | 'center'",
        },
        "params": {},
        "use_when": "Visual break between major sections. Big orange numeral + section label. Position varies by alignment.",
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
    "single_metric": {
        "content": {
            "title": "str (optional)",
            "value": "str (required)",
            "sub_value": "str (optional, 66pt secondary stat directly below)",
            "caption": "str (optional, footer)",
            "body": "str|list (optional, supporting copy on the right)",
            "size": "'hero' (default, 150pt) | 'mega' (200pt — dominates slide)",
        },
        "params": {},
        "use_when": "One hero KPI dominates the slide. For 2-4 KPIs use metric_strip instead. Use size='mega' when the stat alone is the headline.",
    },
    "big_statement": {
        "content": {
            "statement": "str (required)",
            "sub": "str (optional, smaller line below)",
            "alignment": "'left' (default) | 'center'",
        },
        "params": {},
        "use_when": "Big declarative text statement. Smaller than section_divider, bigger than h1 (~60pt).",
    },
    "agenda": {
        "content": {
            "title": "str (optional)",
            "items": "list[str] (1-10)",
        },
        "params": {},
        "use_when": "Numbered TOC / agenda list. 1-5 items get generous spacing; 6+ get compressed.",
    },
    "numbered_list_6up": {
        "content": {
            "title": "str (optional)",
            "items": "list[{number?, label, body}] (1-6)",
        },
        "params": {},
        "use_when": "6 items each with a prominent numeral, label, and body. Use when the numbers themselves carry meaning (steps, principles, priorities).",
    },
    "four_up": {
        "content": {
            "title": "str (optional)",
            "items": "list[{icon_asset_id?, label, body}] (4)",
        },
        "params": {},
        "use_when": "4 parallel columns each with icon, label, body. Same pattern as three_up.",
    },
    "six_up": {
        "content": {
            "title": "str (optional)",
            "items": "list[{icon_asset_id?, label, body}] (6)",
        },
        "params": {},
        "use_when": "6 cells in a 3x2 grid each with icon, label, body. For numbered emphasis use numbered_list_6up.",
    },
    "matrix_2x2": {
        "content": {
            "title": "str (optional)",
            "items": "list[{image, label, body?}] (4)",
        },
        "params": {},
        "use_when": "Generic 2x2 grid of image+text cards. team_grid_2x2 is the team-specific specialization.",
    },
}
