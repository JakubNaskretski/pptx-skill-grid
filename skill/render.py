"""render.py — turn a plan.json into a .pptx.

Usage:
  python render.py plan.json out.pptx [--theme theme.yaml] [--assets DIR]
                                       [--no-splice]

Render produces a .pptx with image placeholders. If an `assets/` directory
exists (either passed via --assets or the bundled skill assets/ folder),
this script auto-splices the binaries in so the output is a ready-to-ship
deck. Pass --no-splice to keep the placeholder version (e.g. for re-splicing
later against a different asset folder).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Emu, Inches

from components import Context, render_component


# Slide background enum → theme color key.
# white     → palette.background     (#FFFFFF)
# light_grey → palette.surface       (#EBEBEB)
# light_orange → tints.orange_60     (#FFE8D4)
BACKGROUND_COLOR_KEYS = {
    "white":        "background",
    "light_grey":   "surface",
    "light_orange": "tints.orange_60",
}


def _apply_background(slide, ctx: Context, bg_kind: str) -> None:
    """Paint a full-bleed rect as the slide background.

    python-pptx's slide.background only sets master-inherited fills, which
    don't always render in viewers; a full-canvas rect is more reliable.
    """
    if bg_kind in (None, "white"):
        return  # default white from the master
    color_key = BACKGROUND_COLOR_KEYS.get(bg_kind)
    if not color_key:
        raise ValueError(f"unknown background: {bg_kind}")
    canvas_w = Inches(ctx.canvas_w_in)
    canvas_h = Inches(ctx.canvas_h_in)
    rect = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, canvas_w, canvas_h)
    rect.fill.solid()
    rect.fill.fore_color.rgb = ctx.rgb(color_key)
    rect.line.fill.background()
    rect.name = "SLIDE_BACKGROUND"
    # Send to back: move the bg rect XML to the start of spTree's shape list
    sp_tree = rect._element.getparent()
    sp_tree.remove(rect._element)
    # Find the first non-pictogram shape — insert after nvGrpSpPr/grpSpPr but
    # before other shapes. The simplest is to insert at index 2 (after the
    # two required header children).
    sp_tree.insert(2, rect._element)


from recipes import RECIPES

PRIVATE_CONFIG_PATH = Path(__file__).parent / "private_config.yaml"


def _load_private_config() -> dict:
    """Load private_config.yaml if it exists; return {} otherwise.

    private_config.yaml is gitignored. It carries org-specific settings
    (company_name, logo, page numbers, etc.) the user keeps local.
    """
    if not PRIVATE_CONFIG_PATH.exists():
        return {}
    try:
        with open(PRIVATE_CONFIG_PATH) as f:
            return yaml.safe_load(f) or {}
    except yaml.YAMLError:
        return {}


def _apply_decorations(slide, ctx: Context, slide_spec: dict, plan: dict,
                       config: dict, total_slides: int) -> None:
    """Stamp logo, presentation title, and page number on every non-cover
    slide. Driven by `private_config.yaml`. Skips cover (id=1)."""
    from pptx.enum.text import PP_ALIGN
    from pptx.util import Pt

    if not config:
        return
    slide_id = slide_spec.get("id", 0)
    if slide_id == 1:
        return  # cover skips decorations

    canvas_w_in = ctx.canvas_w_in
    canvas_h_in = ctx.canvas_h_in
    footer_y_in = canvas_h_in * 13 / 14 + 0.06  # just below content area

    # --- 1. Presentation title at header-left ---
    if config.get("presentation_title", {}).get("enabled"):
        company = (config.get("company_name") or "").strip()
        deck_title = (plan.get("deck_title") or "").strip()
        parts = [p for p in (company, deck_title) if p]
        if parts:
            text = " · ".join(parts)
            box = slide.shapes.add_textbox(
                Inches(canvas_w_in * 0.04),
                Inches(0.12),
                Inches(canvas_w_in * 0.70),
                Inches(0.28),
            )
            tf = box.text_frame
            tf.word_wrap = False
            tf.margin_left = Emu(0)
            tf.margin_right = Emu(0)
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT
            run = p.add_run()
            run.text = text
            run.font.name = ctx.font_name("body")
            run.font.size = Pt(10)
            run.font.color.rgb = ctx.rgb("text_secondary")

    # --- 2. Page number at footer-right ---
    if config.get("page_numbers", {}).get("enabled"):
        text = f"{slide_id} / {total_slides}"
        box = slide.shapes.add_textbox(
            Inches(canvas_w_in * 0.85),
            Inches(footer_y_in),
            Inches(canvas_w_in * 0.11),
            Inches(0.28),
        )
        tf = box.text_frame
        tf.word_wrap = False
        tf.margin_left = Emu(0)
        tf.margin_right = Emu(0)
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.RIGHT
        run = p.add_run()
        run.text = text
        run.font.name = ctx.font_name("body")
        run.font.size = Pt(10)
        run.font.color.rgb = ctx.rgb("text_secondary")

    # --- 3. Logo at footer-left ---
    logo_cfg = config.get("logo") or {}
    logo_id = logo_cfg.get("asset_id")
    if logo_id:
        asset_dir = Path(__file__).parent / "assets"
        logo_path = None
        for ext in (".png", ".jpg", ".jpeg", ".webp"):
            cand = asset_dir / f"{logo_id}{ext}"
            if cand.exists():
                logo_path = cand
                break
        x = Inches(canvas_w_in * 0.04)
        y = Inches(footer_y_in - 0.05)
        h = Inches(0.40)
        if logo_path:
            slide.shapes.add_picture(str(logo_path), x, y, height=h)
        else:
            # Placeholder so the user sees "logo missing" until they add it
            shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y,
                                           Inches(0.40), h)
            shape.name = f"ASSET_PLACEHOLDER:{logo_id}:contain"
            shape.fill.solid()
            shape.fill.fore_color.rgb = ctx.rgb("tints.grey_60")
            shape.line.color.rgb = ctx.rgb("neutral_medium")
            shape.line.width = Emu(12700)
            shape.line.dash_style = 7
            tf = shape.text_frame
            tf.margin_left = Emu(0)
            tf.margin_right = Emu(0)
            p = tf.paragraphs[0]
            from pptx.enum.text import PP_ALIGN as _A
            p.alignment = _A.CENTER
            run = p.add_run()
            run.text = "logo"
            run.font.name = ctx.font_name("body")
            run.font.size = Pt(8)
            run.font.color.rgb = ctx.rgb("text_secondary")


def render(plan: dict, theme: dict, out_path: str) -> None:
    prs = Presentation()
    canvas = theme.get("canvas", {})
    prs.slide_width = Inches(canvas.get("width_in", 13.333))
    prs.slide_height = Inches(canvas.get("height_in", 7.5))

    ctx = Context.from_theme(theme)
    config = _load_private_config()

    # Use the blank layout — index 6 is typical for "Blank" in default master.
    blank_layout = prs.slide_layouts[6]
    total_slides = len(plan.get("slides", []))

    for slide_spec in plan.get("slides", []):
        slide = prs.slides.add_slide(blank_layout)

        # Background first so it sits underneath everything.
        bg = slide_spec.get("background", "white")
        _apply_background(slide, ctx, bg)

        recipe = slide_spec.get("recipe")
        if recipe == "free":
            placements = slide_spec.get("components") or []
        else:
            if recipe not in RECIPES:
                raise ValueError(f"unknown recipe: {recipe}")
            placements = RECIPES[recipe](
                slide_spec.get("content") or {},
                **(slide_spec.get("params") or {}),
            )

        for placement in placements:
            render_component(slide, ctx, placement)

        # Decorations (logo, page number, presentation title) — non-cover only.
        _apply_decorations(slide, ctx, slide_spec, plan, config, total_slides)

    prs.save(out_path)


def _load_yaml(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def _load_json(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


DEFAULT_ASSETS_DIR = Path(__file__).parent / "assets"


def _should_splice(assets_dir: Path) -> bool:
    """True iff the directory has at least one sidecar .yaml that isn't the
    README/vocab/theme."""
    if not assets_dir.exists() or not assets_dir.is_dir():
        return False
    skip = {"theme.yaml", "asset_tag_vocab.yaml"}
    for p in assets_dir.glob("*.yaml"):
        if p.name not in skip:
            return True
    return False


def _cli():
    p = argparse.ArgumentParser(prog="render")
    p.add_argument("plan", help="plan.json")
    p.add_argument("out", help="output .pptx path")
    p.add_argument("--theme", default=None,
                   help="theme.yaml path (defaults to ./theme.yaml)")
    p.add_argument("--assets", default=None,
                   help="asset directory (defaults to bundled assets/ if present). "
                        "Pass an external path to override.")
    p.add_argument("--no-splice", action="store_true",
                   help="Skip the splice step and leave image placeholders.")
    args = p.parse_args()

    plan = _load_json(args.plan)
    theme_path = args.theme or str(Path(__file__).parent / "theme.yaml")
    theme = _load_yaml(theme_path)

    render(plan, theme, args.out)
    print(f"wrote {args.out}", file=sys.stderr)

    # Auto-splice unless suppressed.
    if args.no_splice:
        return
    assets_dir = Path(args.assets) if args.assets else DEFAULT_ASSETS_DIR
    if _should_splice(assets_dir):
        try:
            from splice_assets import splice
        except ImportError:
            print("(splice_assets.py not importable — skipping splice)", file=sys.stderr)
            return
        warnings = splice(args.out, str(assets_dir), args.out)
        print(f"spliced from {assets_dir}"
              + (f" ({len(warnings)} warnings)" if warnings else ""),
              file=sys.stderr)
    else:
        print(f"(no sidecars in {assets_dir} — leaving placeholders)",
              file=sys.stderr)


if __name__ == "__main__":
    _cli()
