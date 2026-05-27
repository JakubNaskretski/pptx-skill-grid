"""render.py — turn a plan.json into a .pptx with image placeholders.

Usage:
  python render.py plan.json out.pptx [--theme theme.yaml]

After render, image components are placeholder shapes whose `name` attribute
starts with `ASSET_PLACEHOLDER:`. Run splice_assets.py to swap them for real
binaries.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml
from pptx import Presentation
from pptx.util import Inches

from components import Context, render_component
from recipes import RECIPES


def render(plan: dict, theme: dict, out_path: str) -> None:
    prs = Presentation()
    canvas = theme.get("canvas", {})
    prs.slide_width = Inches(canvas.get("width_in", 13.333))
    prs.slide_height = Inches(canvas.get("height_in", 7.5))

    ctx = Context.from_theme(theme)

    # Use the blank layout — index 6 is typical for "Blank" in default master.
    blank_layout = prs.slide_layouts[6]

    for slide_spec in plan.get("slides", []):
        slide = prs.slides.add_slide(blank_layout)
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

    prs.save(out_path)


def _load_yaml(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def _load_json(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def _cli():
    p = argparse.ArgumentParser(prog="render")
    p.add_argument("plan", help="plan.json")
    p.add_argument("out", help="output .pptx path")
    p.add_argument("--theme", default=None,
                   help="theme.yaml path (defaults to ./theme.yaml)")
    args = p.parse_args()

    plan = _load_json(args.plan)
    theme_path = args.theme or str(Path(__file__).parent / "theme.yaml")
    theme = _load_yaml(theme_path)

    render(plan, theme, args.out)
    print(f"wrote {args.out}", file=sys.stderr)


if __name__ == "__main__":
    _cli()
