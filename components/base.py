"""Component renderers.

A component is one piece of a slide (heading, text, image, metric, …) drawn at
a fractional rect. Each renderer is theme-aware via Context.

For image components, the renderer emits a PLACEHOLDER shape (dashed grey
rect labeled with the asset_id). splice_assets.py walks the final .pptx,
finds shapes whose name starts with `ASSET_PLACEHOLDER:`, and swaps in the
binary from the asset folder.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt


PLACEHOLDER_PREFIX = "ASSET_PLACEHOLDER"  # splice_assets.py looks for this


# ---------- Context + helpers ----------


@dataclass
class Context:
    """Render-time context passed to every component renderer."""

    theme: dict
    canvas_w_in: float
    canvas_h_in: float

    @classmethod
    def from_theme(cls, theme: dict) -> "Context":
        canvas = theme.get("canvas", {})
        return cls(
            theme=theme,
            canvas_w_in=canvas.get("width_in", 13.333),
            canvas_h_in=canvas.get("height_in", 7.5),
        )

    def to_emu(self, rect: dict) -> tuple[int, int, int, int]:
        """Fractional rect → (left, top, width, height) in EMU."""
        return (
            Inches(rect["x"] * self.canvas_w_in),
            Inches(rect["y"] * self.canvas_h_in),
            Inches(rect["w"] * self.canvas_w_in),
            Inches(rect["h"] * self.canvas_h_in),
        )

    def hex(self, color_key: str) -> str:
        """Resolve a color key to a hex string.

        Accepts:
          - direct hex: '#FFFFFF'
          - dotted: 'status.positive', 'tints.orange_30'
          - bare (searches palette → tints → status, first hit wins):
            'accent_primary', 'grey_90'
        """
        if color_key.startswith("#"):
            return color_key
        if "." in color_key:
            section, key = color_key.split(".", 1)
            return self.theme[section][key]
        for section in ("palette", "tints", "status"):
            if color_key in self.theme.get(section, {}):
                return self.theme[section][color_key]
        raise KeyError(f"color key not found in palette/tints/status: {color_key}")

    def rgb(self, color_key: str) -> RGBColor:
        return _hex_to_rgb(self.hex(color_key))

    def type_style(self, level: str) -> dict:
        return self.theme["type_scale"][level]

    def font_name(self, font_key: str) -> str:
        return self.theme["fonts"][font_key]


def _hex_to_rgb(hex_str: str) -> RGBColor:
    h = hex_str.lstrip("#")
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def _apply_style_overrides(base: dict, overrides: dict | None) -> dict:
    if not overrides:
        return base
    out = dict(base)
    out.update(overrides)
    return out


def _set_run(run, *, text=None, font=None, size_pt=None, bold=None, italic=None,
             color_hex=None):
    if text is not None:
        run.text = text
    f = run.font
    if font is not None:
        f.name = font
    if size_pt is not None:
        f.size = Pt(size_pt)
    if bold is not None:
        f.bold = bold
    if italic is not None:
        f.italic = italic
    if color_hex is not None:
        f.color.rgb = _hex_to_rgb(color_hex)


def _add_textbox(slide, rect_emu, *, anchor=MSO_ANCHOR.TOP, word_wrap=True):
    left, top, w, h = rect_emu
    box = slide.shapes.add_textbox(left, top, w, h)
    tf = box.text_frame
    tf.word_wrap = word_wrap
    tf.vertical_anchor = anchor
    # Clear default paragraph so we control insertion
    tf.margin_left = Emu(0)
    tf.margin_right = Emu(0)
    tf.margin_top = Emu(0)
    tf.margin_bottom = Emu(0)
    return box, tf


_ALIGN = {
    "left": PP_ALIGN.LEFT,
    "center": PP_ALIGN.CENTER,
    "right": PP_ALIGN.RIGHT,
    "justify": PP_ALIGN.JUSTIFY,
}


# ---------- Component renderers ----------


def render_heading(slide, ctx: Context, rect: dict, content: Any,
                   style_overrides: dict | None = None,
                   level: str = "h1", alignment: str = "left",
                   color_key: str = "text_primary"):
    """heading — content is a string. `level` keys into theme.type_scale."""
    text = str(content) if content is not None else ""
    base = ctx.type_style(level)
    style = _apply_style_overrides(base, style_overrides)

    anchor = MSO_ANCHOR.MIDDLE if level == "section_number" else MSO_ANCHOR.TOP
    rect_emu = ctx.to_emu(rect)
    _, tf = _add_textbox(slide, rect_emu, anchor=anchor)

    p = tf.paragraphs[0]
    p.alignment = _ALIGN.get(alignment, PP_ALIGN.LEFT)
    run = p.add_run()
    _set_run(
        run,
        text=text,
        font=ctx.font_name(style["font"]),
        size_pt=style["size_pt"],
        bold=(style["weight"] >= 700),
        color_hex=style.get("color_hex") or ctx.hex(color_key),
    )


def render_text(slide, ctx: Context, rect: dict, content: Any,
                style_overrides: dict | None = None,
                level: str = "body", alignment: str = "left",
                color_key: str = "text_primary"):
    """text — content is a string (paragraph) or list of strings (bullets)."""
    base = ctx.type_style(level)
    style = _apply_style_overrides(base, style_overrides)
    rect_emu = ctx.to_emu(rect)
    _, tf = _add_textbox(slide, rect_emu)

    font = ctx.font_name(style["font"])
    size_pt = style["size_pt"]
    bold = style["weight"] >= 700
    color = style.get("color_hex") or ctx.hex(color_key)

    if isinstance(content, list):
        # Bullets — each item is a paragraph
        for i, item in enumerate(content):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.alignment = _ALIGN.get(alignment, PP_ALIGN.LEFT)
            run = p.add_run()
            _set_run(
                run,
                text=f"•  {item}",
                font=font, size_pt=size_pt, bold=bold, color_hex=color,
            )
            p.space_after = Pt(4)
    else:
        text = str(content) if content is not None else ""
        p = tf.paragraphs[0]
        p.alignment = _ALIGN.get(alignment, PP_ALIGN.LEFT)
        run = p.add_run()
        _set_run(run, text=text, font=font, size_pt=size_pt, bold=bold,
                 color_hex=color)


def render_image(slide, ctx: Context, rect: dict, content: Any,
                 style_overrides: dict | None = None):
    """image — content is {"asset_id": "...", "fit": "fill"|"contain"}
    or {"placeholder": true, "label": "..."}.

    Always emits a placeholder shape. splice_assets.py walks the deck after
    render and swaps it for the binary.
    """
    rect_emu = ctx.to_emu(rect)
    left, top, w, h = rect_emu

    if isinstance(content, dict):
        asset_id = content.get("asset_id")
        fit = content.get("fit", "fill")
        label = content.get("label") or (asset_id or "image needed")
    else:
        asset_id = None
        fit = "fill"
        label = str(content) if content else "image needed"

    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, w, h)
    # Marker for splice
    shape.name = f"{PLACEHOLDER_PREFIX}:{asset_id or 'none'}:{fit}"

    # Visual: dashed grey rect with label
    fill = shape.fill
    fill.solid()
    fill.fore_color.rgb = ctx.rgb("tints.grey_60") if "tints" in ctx.theme else _hex_to_rgb("#EEEFF1")

    line = shape.line
    line.color.rgb = ctx.rgb("neutral_medium")
    line.width = Emu(12700)  # ~1pt
    line.dash_style = 7  # MSO_LINE_DASH_STYLE.DASH

    tf = shape.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    _set_run(
        run,
        text=label,
        font=ctx.font_name("body"),
        size_pt=11,
        color_hex=ctx.hex("text_secondary"),
    )


def render_metric(slide, ctx: Context, rect: dict, content: Any,
                  style_overrides: dict | None = None):
    """metric — content is {"value": "$1.8M", "label": "Revenue",
    "delta": "+12%"?, "delta_status": "positive"|"negative"|"warning"?}.

    Layout inside the cell: value (60%) top, label (25%) below, delta (15%) bottom.
    """
    rect_emu = ctx.to_emu(rect)
    left, top, w, h = rect_emu

    if not isinstance(content, dict):
        content = {"value": str(content), "label": ""}

    value = str(content.get("value", ""))
    label = str(content.get("label", ""))
    delta = content.get("delta")
    delta_status = content.get("delta_status", "positive")

    # Value
    value_h = int(h * 0.55)
    box = slide.shapes.add_textbox(left, top, w, value_h)
    tf = box.text_frame
    tf.word_wrap = False
    tf.vertical_anchor = MSO_ANCHOR.BOTTOM
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    style = ctx.type_style("metric_value")
    run = p.add_run()
    _set_run(
        run,
        text=value,
        font=ctx.font_name(style["font"]),
        size_pt=style["size_pt"],
        bold=True,
        color_hex=ctx.hex("accent_primary"),
    )

    # Label
    label_top = top + value_h
    label_h = int(h * 0.25)
    box = slide.shapes.add_textbox(left, label_top, w, label_h)
    tf = box.text_frame
    tf.vertical_anchor = MSO_ANCHOR.TOP
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    label_style = ctx.type_style("metric_label")
    run = p.add_run()
    _set_run(
        run,
        text=label,
        font=ctx.font_name(label_style["font"]),
        size_pt=label_style["size_pt"],
        color_hex=ctx.hex("text_secondary"),
    )

    # Delta
    if delta:
        delta_top = label_top + label_h
        delta_h = h - value_h - label_h
        box = slide.shapes.add_textbox(left, delta_top, w, delta_h)
        tf = box.text_frame
        tf.vertical_anchor = MSO_ANCHOR.TOP
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT
        run = p.add_run()
        _set_run(
            run,
            text=str(delta),
            font=ctx.font_name("body"),
            size_pt=14,
            bold=True,
            color_hex=ctx.hex(f"status.{delta_status}"),
        )


_CHART_TYPE_MAP = {
    "bar": XL_CHART_TYPE.BAR_CLUSTERED,
    "column": XL_CHART_TYPE.COLUMN_CLUSTERED,
    "column_stacked": XL_CHART_TYPE.COLUMN_STACKED,
    "bar_stacked": XL_CHART_TYPE.BAR_STACKED,
    "line": XL_CHART_TYPE.LINE,
    "line_markers": XL_CHART_TYPE.LINE_MARKERS,
    "pie": XL_CHART_TYPE.PIE,
    "doughnut": XL_CHART_TYPE.DOUGHNUT,
    "area": XL_CHART_TYPE.AREA,
    "area_stacked": XL_CHART_TYPE.AREA_STACKED,
}


def render_chart(slide, ctx: Context, rect: dict, content: Any,
                 style_overrides: dict | None = None):
    """chart — content is {"type": "...", "categories": [...],
    "series": [{"name": "...", "values": [...]}, ...]}."""
    if not isinstance(content, dict):
        raise ValueError("chart content must be a dict with type, categories, series")

    rect_emu = ctx.to_emu(rect)
    left, top, w, h = rect_emu

    chart_type = _CHART_TYPE_MAP.get(content.get("type", "column"),
                                     XL_CHART_TYPE.COLUMN_CLUSTERED)
    cats = content.get("categories", [])
    series = content.get("series", [])

    data = CategoryChartData()
    data.categories = cats
    for s in series:
        data.add_series(s.get("name", ""), s.get("values", []))

    chart_shape = slide.shapes.add_chart(chart_type, left, top, w, h, data)
    chart = chart_shape.chart

    chart.has_title = False
    if len(series) > 1:
        chart.has_legend = True
        chart.legend.position = XL_LEGEND_POSITION.BOTTOM
        chart.legend.include_in_layout = False
    else:
        chart.has_legend = False

    # Recolor series with theme accents
    accent_keys = ["accent_primary", "accent_secondary", "accent_tertiary",
                   "neutral_strong", "neutral_medium", "neutral_soft"]
    for i, plot_series in enumerate(chart.plots[0].series):
        color = ctx.rgb(accent_keys[i % len(accent_keys)])
        try:
            fill = plot_series.format.fill
            fill.solid()
            fill.fore_color.rgb = color
        except Exception:
            pass


def render_table(slide, ctx: Context, rect: dict, content: Any,
                 style_overrides: dict | None = None):
    """table — content is {"rows": N, "cols": N, "has_header": bool,
    "data": [[...], ...]}."""
    if not isinstance(content, dict):
        raise ValueError("table content must be a dict")

    rect_emu = ctx.to_emu(rect)
    left, top, w, h = rect_emu

    data = content.get("data", [])
    if not data:
        return
    rows = content.get("rows", len(data))
    cols = content.get("cols", max(len(r) for r in data) if data else 1)
    has_header = content.get("has_header", True)

    table_shape = slide.shapes.add_table(rows, cols, left, top, w, h)
    table = table_shape.table

    body_font = ctx.font_name("body")
    heading_font = ctx.font_name("heading")
    header_bg = ctx.rgb("accent_primary")
    header_fg = ctx.rgb("text_inverse")
    body_fg = ctx.rgb("text_primary")
    zebra_bg = ctx.rgb("grey_90") if "tints" in ctx.theme else _hex_to_rgb("#F5F7F8")

    for r in range(rows):
        for c in range(cols):
            try:
                cell_text = str(data[r][c]) if r < len(data) and c < len(data[r]) else ""
            except (IndexError, TypeError):
                cell_text = ""
            cell = table.cell(r, c)
            cell.text = ""
            tf = cell.text_frame
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT
            run = p.add_run()
            is_header = has_header and r == 0
            _set_run(
                run,
                text=cell_text,
                font=heading_font if is_header else body_font,
                size_pt=12 if is_header else 11,
                bold=is_header,
                color_hex=("#FFFFFF" if is_header else ctx.hex("text_primary")),
            )
            fill = cell.fill
            fill.solid()
            if is_header:
                fill.fore_color.rgb = header_bg
            elif r % 2 == 0:
                fill.fore_color.rgb = zebra_bg
            else:
                fill.fore_color.rgb = _hex_to_rgb("#FFFFFF")


def render_quote(slide, ctx: Context, rect: dict, content: Any,
                 style_overrides: dict | None = None):
    """quote — content is {"text": "...", "attribution": "..."}."""
    if isinstance(content, str):
        content = {"text": content, "attribution": ""}
    text = content.get("text", "")
    attribution = content.get("attribution", "")

    rect_emu = ctx.to_emu(rect)
    left, top, w, h = rect_emu

    quote_h = int(h * 0.75)
    box = slide.shapes.add_textbox(left, top, w, quote_h)
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    style = ctx.type_style("quote")
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    run = p.add_run()
    _set_run(
        run,
        text=f"“{text}”",  # curly quotes
        font=ctx.font_name(style["font"]),
        size_pt=style["size_pt"],
        italic=True,
        color_hex=ctx.hex("text_primary"),
    )

    if attribution:
        attr_top = top + quote_h
        attr_h = h - quote_h
        box = slide.shapes.add_textbox(left, attr_top, w, attr_h)
        tf = box.text_frame
        tf.vertical_anchor = MSO_ANCHOR.TOP
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT
        run = p.add_run()
        _set_run(
            run,
            text=f"— {attribution}",
            font=ctx.font_name("body"),
            size_pt=14,
            color_hex=ctx.hex("text_secondary"),
        )


def render_cta(slide, ctx: Context, rect: dict, content: Any,
               style_overrides: dict | None = None):
    """cta — content is {"label": "...", "target": "...?"}.
    Renders as a filled accent rectangle with the label centered.
    """
    if isinstance(content, str):
        content = {"label": content}
    label = content.get("label", "")

    rect_emu = ctx.to_emu(rect)
    left, top, w, h = rect_emu

    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, w, h)
    shape.fill.solid()
    shape.fill.fore_color.rgb = ctx.rgb("accent_primary")
    shape.line.fill.background()
    tf = shape.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    _set_run(
        run,
        text=label,
        font=ctx.font_name("heading"),
        size_pt=18,
        bold=True,
        color_hex=ctx.hex("text_inverse"),
    )


def render_divider(slide, ctx: Context, rect: dict, content: Any = None,
                   style_overrides: dict | None = None):
    """divider — thin horizontal rule. content is ignored."""
    rect_emu = ctx.to_emu(rect)
    left, top, w, h = rect_emu
    # Draw a thin line in the vertical middle of the rect
    line_h = Emu(12700)  # ~1pt
    mid = top + h // 2 - line_h // 2
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, mid, w, line_h)
    shape.fill.solid()
    shape.fill.fore_color.rgb = ctx.rgb("neutral_soft")
    shape.line.fill.background()


def render_spacer(slide, ctx: Context, rect: dict, content: Any = None,
                  style_overrides: dict | None = None):
    """spacer — explicit empty cell. Renders nothing."""
    return


def render_icon_label(slide, ctx: Context, rect: dict, content: Any,
                      style_overrides: dict | None = None):
    """icon_label — content is {"icon_asset_id": "...", "label": "..."}.

    Left ~25% is an icon placeholder; right ~75% is the label.
    """
    if isinstance(content, str):
        content = {"label": content}
    icon_id = content.get("icon_asset_id")
    label = content.get("label", "")

    rect_emu = ctx.to_emu(rect)
    left, top, w, h = rect_emu
    icon_w = int(w * 0.25)
    gap = int(w * 0.03)

    if icon_id or content.get("with_icon", True):
        # Icon placeholder
        icon_shape = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, left, top, icon_w, h
        )
        icon_shape.name = f"{PLACEHOLDER_PREFIX}:{icon_id or 'none'}:contain"
        icon_shape.fill.solid()
        icon_shape.fill.fore_color.rgb = ctx.rgb("tints.orange_90") if "tints" in ctx.theme else _hex_to_rgb("#FFF5ED")
        icon_shape.line.color.rgb = ctx.rgb("accent_primary")
        icon_shape.line.width = Emu(12700)
        icon_shape.line.dash_style = 7

    label_left = left + icon_w + gap
    label_w = w - icon_w - gap
    box = slide.shapes.add_textbox(label_left, top, label_w, h)
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    run = p.add_run()
    _set_run(
        run,
        text=label,
        font=ctx.font_name("body"),
        size_pt=14,
        color_hex=ctx.hex("text_primary"),
    )


# ---------- Dispatch ----------


COMPONENT_RENDERERS = {
    "heading": render_heading,
    "text": render_text,
    "image": render_image,
    "metric": render_metric,
    "chart": render_chart,
    "table": render_table,
    "quote": render_quote,
    "cta": render_cta,
    "divider": render_divider,
    "spacer": render_spacer,
    "icon_label": render_icon_label,
}


def render_component(slide, ctx: Context, placement: dict):
    """Top-level dispatch: take one component placement and render it.

    `placement` shape:
      {"type": "<component>", "grid": {...}, "content": ..., "style_overrides": {...}?, ...kwargs}

    Recipes emit lists of these; render.py loops over them per slide.
    """
    from grid import placement_to_rect

    comp_type = placement["type"]
    if comp_type not in COMPONENT_RENDERERS:
        raise ValueError(f"unknown component type: {comp_type}")

    rect = placement_to_rect(placement["grid"])
    extra = {k: v for k, v in placement.items()
             if k not in ("type", "grid", "content", "style_overrides")}
    COMPONENT_RENDERERS[comp_type](
        slide,
        ctx,
        rect,
        placement.get("content"),
        style_overrides=placement.get("style_overrides"),
        **extra,
    )
