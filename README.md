# pptx-grid-skill

A grid-based, recipe-driven PowerPoint composition skill for LLM agents. The
agent picks parametric layouts from a catalog and fills typed slots; a render
step turns the plan into a `.pptx` with brand-correct typography, tables, and
spacing.

## Two key abstractions

- **A 12×12 grid** with half-column side margins and a one-row strip top and
  bottom. Every element snaps to grid cells — cross-slide drift is
  structurally impossible.
- **26 parametric recipes** covering the typical business-deck archetypes
  (cover, section divider, agenda, single-metric, metric-strip, comparison,
  N-up, chart, table variants, team cards, …). The agent calls a recipe by
  name with content; the recipe emits component placements on the grid.

Theme-driven. A single corporate `theme.yaml` carries the palette, fonts,
and type scale — sized to match a real branded reference deck. The agent
references colors by *name* (`accent_primary`, `tints.grey_30`, …), never
by hex. Render time resolves names to actual hex.

## Recipe catalog (26)

| Group | Recipes |
|---|---|
| Openers / closers | `title_only`, `cta_closing` |
| Section breaks | `section_divider` (right / left / center alignment) |
| Content (text) | `title_bullets`, `two_col_text`, `comparison`, `agenda` |
| Content + image | `title_hero_image`, `text_image_split` |
| Metrics & statements | `single_metric` (`size`: hero 150pt / mega 200pt; optional `sub_value`), `metric_strip` (2-4 KPIs), `big_statement` (66pt), `numbered_list_6up` (115pt numerals) |
| Multi-item icon layouts | `three_up`, `four_up`, `six_up` |
| Multi-item image cards | `two_card_row`, `three_card_row`, `matrix_2x2` |
| Team-specific | `team_strip` (4 in a row), `team_grid_2x2` |
| Quotes | `quote` (66pt italic with attribution) |
| Tables | `table_full`, `table_with_callout` — both accept `style` ∈ {header_accent, zebra_neutral, filled_accent, filled_neutral, minimal, underline_accent, underline_neutral} |
| Charts | `chart_full`, `chart_with_takeaway` |
| Escape hatch | `free` (direct component placements — discouraged) |

## Backgrounds (per-slide)

Each slide spec accepts `"background": "white" | "light_grey" | "light_orange"`
(default white).

## Type scale (calibrated to the brand reference deck)

| Level | Size | Weight | Use |
|---|---|---|---|
| `section_number` | 350pt | regular, Arial | the giant numeral in `section_divider` |
| `mega_metric` | 200pt | regular, Arial | `single_metric` with `size: mega` |
| `hero_metric` | 150pt | regular, Arial | `single_metric` default |
| `numbered_item` | 115pt | regular, Arial | `numbered_list_6up` numerals |
| `statement` | 66pt | regular, Georgia | `big_statement` text |
| `sub_metric` | 66pt | regular, Arial | `single_metric.sub_value` |
| `metric_value` | 48pt | regular | `metric_strip` values |
| `h1` | 48pt | regular, Georgia | slide titles |
| `h2` | 28pt | bold | column labels |
| `h3` | 18pt | bold | card labels |
| `body` | 15pt | regular, Arial | body text and bullets |
| `caption` | 11pt | regular, Arial | footers, secondary lines |
| `quote` | 28pt | italic, Georgia | pull-quotes |

Big-text weights match source exactly (`b="0"` on every big-number placeholder).
Small headings stay bold for hierarchy in tight cells.

## Architecture

```
You / your data           ┐
   theme.yaml             │  (extracted from brand template once)
   pptx_extracted_private │  binaries — outside repo
                          │
The agent ─────────────────▶ plan.json
   reads SKILL.md         │
   picks recipes          │
   calls reader.py        │  (validate-slide / find-asset / measure-text)
   emits structured JSON  │
                          │
You / render scripts ─────▶ final.pptx
   render.py              │  plan + theme → .pptx with placeholders
   splice_assets.py       │  swaps placeholders for binaries
```

The agent never accesses the brand template or the asset binaries directly.
It works against `theme.yaml` (text) and sidecar `.yaml` files (text
descriptions of assets).

## Asset workflow

Binaries live **outside** the skill bundle (storage / privacy).

```bash
# 1) Once per asset folder — generates sidecar YAMLs alongside binaries
python describe_assets.py /path/to/assets/

# 2) Agent reads the sidecars (descriptions, tags, dims) and writes
#    plan.json with asset_id refs in image components

# 3) Render produces a .pptx with image placeholders (no binaries embedded)
python render.py plan.json out.pptx

# 4) Splice the binaries in — produces the final shippable .pptx
python splice_assets.py out.pptx --assets /path/to/assets/ -o final.pptx
```

## Repo layout

```
SKILL.md                 ← agent contract — what the agent reads
AGENT_SETUP.md           ← model parameters + ready-to-paste system instructions
README.md                ← this file
theme.yaml               ← single source of truth for palette / fonts / type scale
asset_tag_vocab.yaml     ← closed tag list for asset sidecars
prompts/describe_asset.md← prompt template for vision-LLM asset description

reader.py                ← agent-facing CLI (theme / recipes / toolbelt / validate)
render.py                ← CLI: plan.json → out.pptx (with image placeholders)
splice_assets.py         ← CLI: out.pptx + assets/ → final.pptx
describe_assets.py       ← CLI: assets/ → sidecar YAMLs
grid.py                  ← cell-rect math

components/              ← drawing primitives + card compound component
recipes/                 ← 26 parametric layout functions
toolbelt/                ← deterministic critics (measure_text, grid_audit, …)
schemas/                 ← brief / outline / plan JSON schemas
examples/                ← example_plan, example_branded, example_v2,
                           example_showcase + their JSON plans
tests/                   ← smoke tests
```

## Quickstart

```bash
pip install -r requirements.txt

# 25-slide narrative showcase exercising most of the surface
python render.py examples/example_showcase.json examples/out_showcase.pptx
open examples/out_showcase.pptx
```

## Workflow for the agent

The full contract lives in `SKILL.md`. Four phases:

1. **Discovery** — agent runs a structured interview, fills `brief.json`.
2. **Outline** — slide-by-slide TOC with recipe + summary per slide.
3. **Batch build** — 3 slides at a time. After each: `python reader.py
   validate-slide slide.json` returns `{errors, warnings}` from grid_audit
   + measure_text per text component + chart_sanity + palette_audit.
   Tiered severity catches overflow before render.
4. **Polish** — whole-deck `validate-plan`, address any deck_flow warnings,
   emit final `plan.json`.

The agent stops at `plan.json`. You run `render.py` and `splice_assets.py`
yourself.

## Setting up the agent

See [`AGENT_SETUP.md`](./AGENT_SETUP.md) for:

- GPT-5.4 parameter recommendations (temperature, reasoning effort,
  verbosity, etc.)
- Ready-to-paste system instructions

## Status

Single corporate theme. 26 recipes. 7 table styles. Card compound component.
Toolbelt + validate-slide. Asset workflow via placeholder + splice. Examples
include a 25-slide narrative showcase (`example_showcase.json`).

Next direction (not yet implemented): native brand-template integration via
`--brand-template` flag — would let `render.py` start from a brand `.pptx`
so master decorations (logos, page numbers, brand bars) and native
PowerPoint table styles ride along automatically.
