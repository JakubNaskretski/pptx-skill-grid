# pptx-grid-skill

A grid-based, recipe-driven PowerPoint composition skill for LLM agents.

## What it is

Where v1 of pptx-skill bottled visual fidelity by extracting whole slide
templates from example decks, this skill replaces templates with two
small abstractions an LLM can compose from:

- **A 12×12 grid** with half-column side margins and one-row strips at top
  and bottom. Every element snaps to grid cells — cross-slide drift
  becomes structurally impossible.
- **13 parametric recipes** covering ~90% of business slide archetypes
  (title, section divider, metric strip, two-col, comparison, chart-with-
  takeaway, etc.). The agent calls a recipe by name with content; the
  recipe emits component placements on the grid.

Everything is theme-driven. A single corporate `theme.yaml` carries the
palette, fonts, and type scale. Colors and font choices are resolved at
render time so the same plan renders consistently.

## Asset workflow

Asset binaries live **outside** the skill bundle (storage constraint).
Three CLI scripts manage the flow:

1. `describe_assets.py /path/to/assets/` — walks the folder and emits a
   sidecar YAML per binary (kind, dims, colors auto; tags + description
   filled by user or a vision LLM).
2. Agent composes against the sidecar YAMLs and emits `plan.json` with
   `asset_id` references in image components.
3. `render.py plan.json out.pptx` produces a `.pptx` with image
   *placeholders*.
4. `splice_assets.py out.pptx --assets /path/to/assets/ -o final.pptx`
   swaps placeholders for the real binaries.

## Repo layout

```
SKILL.md                 ← the agent contract (voice, phases, recipe catalog)
theme.yaml               ← corporate theme (colors, fonts, type scale)
asset_tag_vocab.yaml     ← closed asset tag vocabulary
reader.py                ← agent-facing API (theme, recipes, toolbelt, validate)
render.py                ← CLI: plan.json + theme → out.pptx (with placeholders)
splice_assets.py         ← CLI: out.pptx + assets/ → final.pptx
describe_assets.py       ← CLI: assets/ → sidecar YAMLs
grid.py                  ← cell math
components/              ← drawing primitives (heading, text, image, …)
recipes/                 ← 13 parametric layout functions
toolbelt/                ← deterministic critics (measure_text, grid_audit, …)
schemas/                 ← JSON schemas for brief / outline / plan
prompts/                 ← vision-LLM prompts for asset description
examples/                ← reference plan.json + rendered .pptx
tests/                   ← smoke tests
```

## Quickstart

```bash
pip install -r requirements.txt

# Generate an example deck end-to-end:
python render.py examples/example_plan.json examples/out.pptx

# (Optional) with real assets:
python describe_assets.py /path/to/your/assets/
python splice_assets.py examples/out.pptx --assets /path/to/your/assets/ \
    -o examples/final.pptx
```

## Status

MVP — initial build. Single corporate theme. 13 recipes. Asset workflow
via placeholder + splice. See `SKILL.md` for the agent-facing contract.
