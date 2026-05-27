"""reader.py — agent-facing API surface.

CLI commands (use stdout JSON for machine-readability):

  python reader.py theme
  python reader.py list-recipes
  python reader.py recipe-signature <name>
  python reader.py preview-recipe <name> --content '<json>' [--params '<json>']

  python reader.py cell-to-rect --row R --col C [--row-span N] [--col-span N]

  python reader.py measure-text <text> --type-level <name> --cell-rect '<json>'
  python reader.py check-asset-fit --asset '<json>' --cell-rect '<json>' [--fit fill]
  python reader.py contrast-check <fg_hex> <bg_hex>
  python reader.py palette-audit --components '<json>'
  python reader.py grid-audit --components '<json>'
  python reader.py visual-balance --components '<json>'
  python reader.py deck-flow <plan.json>
  python reader.py chart-sanity --content '<json>'

  python reader.py read-assets <asset_dir>
  python reader.py find-asset <asset_dir> [--kind photo] [--tags people,office] [--limit 5]

  python reader.py validate-plan <plan.json>

JSON inputs can come from string args or from a file path (if the arg starts
with @, the rest is treated as a path).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

import grid as grid_mod
from recipes import RECIPES, RECIPE_SIGNATURES
from components import COMPONENT_RENDERERS
from toolbelt import (
    measure_text as _measure_text,
    check_asset_fit as _check_asset_fit,
    contrast_check as _contrast_check,
    palette_audit as _palette_audit,
    grid_audit as _grid_audit,
    visual_balance as _visual_balance,
    deck_flow as _deck_flow,
    chart_sanity as _chart_sanity,
)


THEME_PATH = Path(__file__).parent / "theme.yaml"


# ---------- helpers ----------


def _load_theme() -> dict:
    with open(THEME_PATH) as f:
        return yaml.safe_load(f)


def _load_json_arg(value: str):
    """Parse a JSON argument. If it starts with @, treat as a path."""
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        return value
    if value.startswith("@"):
        with open(value[1:]) as f:
            return json.load(f)
    return json.loads(value)


def _print_json(obj):
    print(json.dumps(obj, indent=2, default=str))


# ---------- module-level API (also usable from imports) ----------


def theme() -> dict:
    return _load_theme()


def list_recipes() -> list[dict]:
    return [{"name": name, **RECIPE_SIGNATURES.get(name, {})} for name in RECIPES]


def recipe_signature(name: str) -> dict:
    if name not in RECIPES:
        raise ValueError(f"unknown recipe: {name}")
    return {"name": name, **RECIPE_SIGNATURES.get(name, {})}


def preview_recipe(name: str, content: dict, params: dict | None = None) -> list[dict]:
    """Resolve a recipe to its component placements (without rendering)."""
    if name not in RECIPES:
        raise ValueError(f"unknown recipe: {name}")
    return RECIPES[name](content, **(params or {}))


def list_components() -> list[str]:
    return sorted(COMPONENT_RENDERERS.keys())


def cell_to_rect(row: int, col: int, row_span: int = 1, col_span: int = 1) -> dict:
    return grid_mod.cell_to_rect(row, col, row_span, col_span)


def measure_text(text: str, type_level: str, cell_rect: dict) -> dict:
    t = _load_theme()
    canvas = t.get("canvas", {})
    return _measure_text(
        text,
        type_level=type_level,
        cell_rect=cell_rect,
        canvas_w_in=canvas.get("width_in", 13.333),
        canvas_h_in=canvas.get("height_in", 7.5),
        theme=t,
    )


def check_asset_fit(asset: dict, cell_rect: dict, fit_mode: str = "fill") -> dict:
    t = _load_theme()
    canvas = t.get("canvas", {})
    return _check_asset_fit(
        asset,
        cell_rect,
        canvas_w_in=canvas.get("width_in", 13.333),
        canvas_h_in=canvas.get("height_in", 7.5),
        fit_mode=fit_mode,
    )


def contrast_check(fg_hex: str, bg_hex: str) -> dict:
    return _contrast_check(fg_hex, bg_hex)


def palette_audit(slide_components: list[dict]) -> dict:
    return _palette_audit(slide_components, _load_theme())


def grid_audit(slide_components: list[dict]) -> dict:
    return _grid_audit(slide_components)


def visual_balance(slide_components: list[dict]) -> dict:
    return _visual_balance(slide_components)


def deck_flow(plan: dict) -> dict:
    return _deck_flow(plan)


def chart_sanity(content: dict) -> dict:
    return _chart_sanity(content)


# ---------- asset directory reads ----------


_ASSET_BINARY_SUFFIXES = {".jpg", ".jpeg", ".png", ".svg", ".gif", ".webp"}


def read_assets(asset_dir: str) -> list[dict]:
    """Walk asset_dir, return list of asset summaries from sidecar YAMLs.

    A sidecar is a file `<id>.yaml` next to the binary. Returns the parsed
    YAML for each, with id defaulting to the filename stem if missing.
    """
    root = Path(asset_dir)
    if not root.exists() or not root.is_dir():
        return []
    out = []
    for yaml_path in sorted(root.glob("*.yaml")):
        if yaml_path.name in {"theme.yaml", "asset_tag_vocab.yaml"}:
            continue
        try:
            with open(yaml_path) as f:
                data = yaml.safe_load(f) or {}
        except yaml.YAMLError:
            continue
        if "id" not in data:
            data["id"] = yaml_path.stem
        # Resolve absolute file path
        if "file" in data and not Path(data["file"]).is_absolute():
            data["abs_path"] = str((root / data["file"]).resolve())
        out.append(data)
    return out


def find_asset(
    asset_dir: str,
    kind: str | None = None,
    tags: list[str] | None = None,
    limit: int = 10,
) -> dict:
    """Filter assets in `asset_dir` by kind + tags (AND). Returns up to `limit`.

    Broadening: if tags filter yields zero, retry without tags (one step only).
    """
    assets = read_assets(asset_dir)
    matches = []
    for a in assets:
        if kind and a.get("kind") != kind:
            continue
        if tags:
            asset_tags = set(a.get("tags") or [])
            if not all(t in asset_tags for t in tags):
                continue
        matches.append(a)

    broadened = False
    if not matches and tags:
        # Retry without tags
        broadened = True
        for a in assets:
            if kind and a.get("kind") != kind:
                continue
            matches.append(a)

    matches = matches[:limit]
    return {
        "count": len(matches),
        "broadened": broadened,
        "matches": matches,
    }


# ---------- whole-plan validation ----------


def validate_plan(plan: dict) -> dict:
    """Run all hard checks against a plan.

    Errors block the build; warnings don't.
    """
    errors: list[dict] = []
    warnings: list[dict] = []

    if not isinstance(plan, dict):
        return {"ok": False, "errors": [{"message": "plan must be a dict"}], "warnings": []}

    if plan.get("version") != "1":
        warnings.append({"kind": "version", "message": "plan version != '1'"})

    slides = plan.get("slides") or []
    if not slides:
        errors.append({"kind": "empty", "message": "plan has no slides"})
        return {"ok": False, "errors": errors, "warnings": warnings}

    # Per-slide checks
    for i, slide in enumerate(slides, start=1):
        recipe_name = slide.get("recipe")
        slide_id = slide.get("id", i)

        if recipe_name not in RECIPES and recipe_name != "free":
            errors.append({
                "kind": "unknown_recipe",
                "slide_id": slide_id,
                "message": f"unknown recipe: {recipe_name}",
            })
            continue

        # Resolve to component placements
        if recipe_name == "free":
            placements = slide.get("components") or []
        else:
            try:
                placements = RECIPES[recipe_name](
                    slide.get("content") or {},
                    **(slide.get("params") or {}),
                )
            except Exception as e:
                errors.append({
                    "kind": "recipe_error",
                    "slide_id": slide_id,
                    "message": f"recipe {recipe_name} raised: {e}",
                })
                continue

        # Grid check
        ga = _grid_audit(placements)
        if not ga["ok"]:
            errors.append({
                "kind": "grid_audit",
                "slide_id": slide_id,
                "details": ga,
            })

        # Palette check (warnings only)
        pa = _palette_audit(placements, _load_theme())
        if not pa["ok"]:
            warnings.append({
                "kind": "palette_audit",
                "slide_id": slide_id,
                "details": pa,
            })

        # Chart sanity on chart components (warnings only)
        for c in placements:
            if c.get("type") == "chart":
                cs = _chart_sanity(c.get("content") or {})
                if not cs["ok"]:
                    warnings.append({
                        "kind": "chart_sanity",
                        "slide_id": slide_id,
                        "details": cs,
                    })

    # Whole-plan flow
    df = _deck_flow(plan)
    if not df["ok"]:
        for issue in df["issues"]:
            warnings.append({"kind": f"deck_flow.{issue['kind']}", "details": issue})

    ok = len(errors) == 0
    return {"ok": ok, "errors": errors, "warnings": warnings}


# ---------- CLI ----------


def _cli():
    p = argparse.ArgumentParser(prog="reader", description="pptx-grid-skill agent API")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("theme")
    sub.add_parser("list-recipes")
    sub.add_parser("list-components")

    r = sub.add_parser("recipe-signature")
    r.add_argument("name")

    r = sub.add_parser("preview-recipe")
    r.add_argument("name")
    r.add_argument("--content", required=True, help="JSON or @path")
    r.add_argument("--params", default="{}")

    r = sub.add_parser("cell-to-rect")
    r.add_argument("--row", type=int, required=True)
    r.add_argument("--col", type=int, required=True)
    r.add_argument("--row-span", type=int, default=1)
    r.add_argument("--col-span", type=int, default=1)

    r = sub.add_parser("measure-text")
    r.add_argument("text")
    r.add_argument("--type-level", required=True)
    r.add_argument("--cell-rect", required=True, help="JSON or @path")

    r = sub.add_parser("check-asset-fit")
    r.add_argument("--asset", required=True)
    r.add_argument("--cell-rect", required=True)
    r.add_argument("--fit", default="fill")

    r = sub.add_parser("contrast-check")
    r.add_argument("fg")
    r.add_argument("bg")

    r = sub.add_parser("palette-audit")
    r.add_argument("--components", required=True)

    r = sub.add_parser("grid-audit")
    r.add_argument("--components", required=True)

    r = sub.add_parser("visual-balance")
    r.add_argument("--components", required=True)

    r = sub.add_parser("deck-flow")
    r.add_argument("plan")

    r = sub.add_parser("chart-sanity")
    r.add_argument("--content", required=True)

    r = sub.add_parser("read-assets")
    r.add_argument("asset_dir")

    r = sub.add_parser("find-asset")
    r.add_argument("asset_dir")
    r.add_argument("--kind", default=None)
    r.add_argument("--tags", default=None, help="comma-separated")
    r.add_argument("--limit", type=int, default=10)

    r = sub.add_parser("validate-plan")
    r.add_argument("plan")

    args = p.parse_args()

    if args.command == "theme":
        _print_json(theme())
    elif args.command == "list-recipes":
        _print_json(list_recipes())
    elif args.command == "list-components":
        _print_json(list_components())
    elif args.command == "recipe-signature":
        _print_json(recipe_signature(args.name))
    elif args.command == "preview-recipe":
        content = _load_json_arg(args.content)
        params = _load_json_arg(args.params)
        _print_json(preview_recipe(args.name, content, params))
    elif args.command == "cell-to-rect":
        _print_json(cell_to_rect(args.row, args.col, args.row_span, args.col_span))
    elif args.command == "measure-text":
        _print_json(measure_text(args.text, args.type_level, _load_json_arg(args.cell_rect)))
    elif args.command == "check-asset-fit":
        _print_json(check_asset_fit(_load_json_arg(args.asset),
                                    _load_json_arg(args.cell_rect),
                                    args.fit))
    elif args.command == "contrast-check":
        _print_json(contrast_check(args.fg, args.bg))
    elif args.command == "palette-audit":
        _print_json(palette_audit(_load_json_arg(args.components)))
    elif args.command == "grid-audit":
        _print_json(grid_audit(_load_json_arg(args.components)))
    elif args.command == "visual-balance":
        _print_json(visual_balance(_load_json_arg(args.components)))
    elif args.command == "deck-flow":
        plan = _load_json_arg(f"@{args.plan}") if not args.plan.startswith("{") else _load_json_arg(args.plan)
        _print_json(deck_flow(plan))
    elif args.command == "chart-sanity":
        _print_json(chart_sanity(_load_json_arg(args.content)))
    elif args.command == "read-assets":
        _print_json(read_assets(args.asset_dir))
    elif args.command == "find-asset":
        tags = args.tags.split(",") if args.tags else None
        _print_json(find_asset(args.asset_dir, kind=args.kind, tags=tags, limit=args.limit))
    elif args.command == "validate-plan":
        plan = _load_json_arg(f"@{args.plan}")
        _print_json(validate_plan(plan))


if __name__ == "__main__":
    _cli()
