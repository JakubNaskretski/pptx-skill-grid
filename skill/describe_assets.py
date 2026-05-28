"""describe_assets.py — walk an asset folder and emit sidecar YAMLs.

For each binary (jpg/png/svg/xml), creates `<stem>.yaml` next to it with:
  - id, file, kind (guessed from extension)
  - width, height, aspect (auto for raster)
  - colors_hex (auto: top 5 dominant colors for raster)
  - tags: []      ← user/LLM fills in
  - description: ""  ← user/LLM fills in

Existing sidecars are left untouched unless --overwrite is set.

With --with-vision-prompts, prints the describer prompt + asset path for
each new asset so the user can paste into a vision LLM and edit the
generated YAML in place.

Usage:
  python describe_assets.py /path/to/assets/
  python describe_assets.py /path/to/assets/ --overwrite
  python describe_assets.py /path/to/assets/ --with-vision-prompts
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml
from PIL import Image


PROMPT_PATH = Path(__file__).parent / "prompts" / "describe_asset.md"
VOCAB_PATH = Path(__file__).parent / "asset_tag_vocab.yaml"


_RASTER_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"}
_VECTOR_EXTS = {".svg", ".emf", ".wmf"}
_XML_EXTS = {".xml"}


def _guess_kind(ext: str) -> str:
    e = ext.lower()
    if e in _RASTER_EXTS:
        return "photo"
    if e == ".svg":
        # SVGs in business decks are overwhelmingly icons / pictograms;
        # user can override to 'illustration' or 'logo' in the sidecar.
        return "icon"
    if e in _VECTOR_EXTS:
        return "vector"
    if e in _XML_EXTS:
        return "vector"
    return "photo"


def _dominant_colors(path: Path, n: int = 5) -> list[str]:
    try:
        img = Image.open(path).convert("RGB")
        img.thumbnail((128, 128))
        quant = img.quantize(colors=n, method=Image.Quantize.MEDIANCUT)
        palette = quant.getpalette()
        if not palette:
            return []
        # First n*3 entries are the chosen palette
        triples = [palette[i * 3:(i + 1) * 3] for i in range(n)]
        return [f"#{r:02X}{g:02X}{b:02X}" for r, g, b in triples if (r, g, b) != (0, 0, 0)][:n]
    except Exception:
        return []


def _raster_metrics(path: Path) -> dict:
    try:
        img = Image.open(path)
        w, h = img.size
        return {
            "width": w,
            "height": h,
            "aspect": round(w / h, 3) if h else None,
            "colors_hex": _dominant_colors(path),
        }
    except Exception:
        return {"width": None, "height": None, "aspect": None, "colors_hex": []}


def _svg_metrics(path: Path) -> dict:
    """Parse SVG width/height from viewBox or explicit attributes."""
    import re
    try:
        text = path.read_text(errors="ignore")[:4000]
    except Exception:
        return {"width": None, "height": None, "aspect": None, "colors_hex": []}
    m = re.search(r'viewBox\s*=\s*"([^"]+)"', text)
    w = h = None
    if m:
        parts = m.group(1).strip().split()
        if len(parts) >= 4:
            try:
                w = float(parts[2])
                h = float(parts[3])
            except ValueError:
                pass
    if w is None:
        mw = re.search(r'\bwidth\s*=\s*"([0-9.]+)', text)
        mh = re.search(r'\bheight\s*=\s*"([0-9.]+)', text)
        if mw and mh:
            try:
                w = float(mw.group(1))
                h = float(mh.group(1))
            except ValueError:
                pass
    return {
        "width": int(w) if w else None,
        "height": int(h) if h else None,
        "aspect": round(w / h, 3) if (w and h) else None,
        "colors_hex": [],  # SVGs may use theme refs; vision LLM can fill if needed
    }


def _build_sidecar(binary: Path) -> dict:
    kind = _guess_kind(binary.suffix)
    base = {
        "id": binary.stem,
        "file": binary.name,
        "kind": kind,
        "tags": [],
        "description": "",
        "status": "pending",
    }
    if binary.suffix.lower() in _RASTER_EXTS:
        base.update(_raster_metrics(binary))
    elif binary.suffix.lower() == ".svg":
        base.update(_svg_metrics(binary))
    return base


def _load_prompt() -> str:
    if PROMPT_PATH.exists():
        return PROMPT_PATH.read_text()
    return "(no prompt template found — see prompts/describe_asset.md)"


def _load_vocab() -> list[str]:
    if VOCAB_PATH.exists():
        data = yaml.safe_load(VOCAB_PATH.read_text()) or {}
        return data.get("tags") or []
    return []


def describe(asset_dir: str, overwrite: bool = False,
             with_vision_prompts: bool = False) -> list[Path]:
    root = Path(asset_dir)
    if not root.exists():
        print(f"asset dir not found: {asset_dir}", file=sys.stderr)
        return []

    written: list[Path] = []
    prompt = _load_prompt() if with_vision_prompts else None
    vocab = _load_vocab() if with_vision_prompts else None

    for binary in sorted(root.iterdir()):
        if not binary.is_file():
            continue
        ext = binary.suffix.lower()
        if ext not in (_RASTER_EXTS | _VECTOR_EXTS | _XML_EXTS):
            continue
        sidecar = binary.with_suffix(".yaml")
        if sidecar.exists() and not overwrite:
            continue
        data = _build_sidecar(binary)
        sidecar.write_text(yaml.safe_dump(data, sort_keys=False))
        written.append(sidecar)

        if with_vision_prompts:
            print("=" * 60)
            print(f"ASSET: {binary}")
            print(f"SIDECAR: {sidecar}")
            print(f"VOCAB: {vocab}")
            print("PROMPT:")
            print(prompt)
            print("=" * 60)

    return written


def _cli():
    p = argparse.ArgumentParser(prog="describe_assets")
    p.add_argument("asset_dir")
    p.add_argument("--overwrite", action="store_true",
                   help="Re-build sidecars even if they exist")
    p.add_argument("--with-vision-prompts", action="store_true",
                   help="Print the describer prompt for each new asset")
    args = p.parse_args()

    written = describe(args.asset_dir, args.overwrite, args.with_vision_prompts)
    print(f"wrote {len(written)} sidecar(s)", file=sys.stderr)


if __name__ == "__main__":
    _cli()
