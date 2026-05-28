# Agent setup (GPT-5.4 and similar)

Two things to configure in your agent platform:

1. **Model parameters** — what to set, with rationale
2. **System instructions** — ready-to-paste text

If your platform doesn't expose a particular parameter, leave it at the
provider default. The recommended values below are the *useful* settings;
anything missing isn't a dealbreaker.

---

## 1. Model parameters

| Parameter | Recommended | Why |
|---|---|---|
| `temperature` | **0.3** | Task is structured — pick a recipe from a fixed list, fill typed slots, validate. Low temp keeps the model disciplined (no inventing recipes, no schema drift). Some creativity at the wording layer (bullet text, titles) is fine; 0.3 gives that without breaking structure. |
| `top_p` | **1.0** (default) | Either set `temperature` OR `top_p`, not both. We use `temperature`. |
| `frequency_penalty` | **0.0** | Decks legitimately repeat tokens — same recipe name many times, same phrasing patterns across slides. Penalizing repetition would make the agent dodge recipe names. Leave off. |
| `presence_penalty` | **0.0** | We want the agent to stay on topic (the brief), not introduce new concepts. Leave off. |
| `reasoning_effort` | **medium** (default) | The agent's work is multi-step: pick recipe → fill content → validate → revise. Medium gives the model room to plan a slide without exploding latency. Use **high** if the user reports the agent making bad recipe choices or skipping validation. |
| `reasoning_summary` | **auto** | Visibility for debugging. Set **none** in production once you're confident. |
| `verbosity` | **low** | Every agent output is structured (JSON for brief/outline/plan, one-line confirmations otherwise). The SKILL.md voice section explicitly forbids paragraph-style replies. Low verbosity reinforces this. |
| `image_detail` | **low** (or N/A) | The compose phase has no vision input — assets are described in text via their sidecar YAMLs. If your platform requires a value, low is fine. |
| `max_output_tokens` / context | leave high | A 25-slide plan + reasoning trace can be ~10-20K tokens. Don't truncate. |

### Quick reference (JSON-style for OpenAI-compatible APIs)

```json
{
  "temperature": 0.3,
  "top_p": 1.0,
  "frequency_penalty": 0.0,
  "presence_penalty": 0.0,
  "reasoning": {"effort": "medium", "summary": "auto"},
  "text": {"verbosity": "low"}
}
```

For the OpenAI Assistants / Responses API, the field names may differ
slightly (`reasoning.effort` instead of `reasoning_effort`, etc.) — adjust
to your SDK.

---

## 2. System instructions (ready to paste)

Paste the block below into your agent's **system instructions** /
**developer message** / **persona** field — whatever your platform calls the
top-level prompt that prefixes every conversation.

This is a tight summary of what's in `SKILL.md`. The full `SKILL.md` ships
in the skill bundle alongside `theme.yaml`, recipes, etc. and is what the
agent consults via tool calls — these system instructions just set the tone
and forbidden behaviors.

---

```
You are a deck-building agent using the pptx-grid-skill. You produce a
plan.json that the user renders to PowerPoint via a separate render script.
You never run the render or splice scripts yourself.

## How you work

Walk every deck through four phases in order. Don't skip ahead.

  Phase 1 — Discovery     interview the user; fill brief.json
  Phase 2 — Outline       slide-by-slide TOC (recipe + summary); 1 round
  Phase 3 — Batch build   3 slides at a time; validate-slide each one
  Phase 4 — Polish        validate-plan whole deck; address errors

If a transition condition is not met (e.g. brief has a blank field, outline
not approved), refuse yourself and re-ask.

## Tooling

You call the skill via:

  python reader.py theme                        — load theme.yaml
  python reader.py list-recipes                 — full recipe catalog
  python reader.py recipe-signature <name>      — fields a recipe accepts
  python reader.py preview-recipe <name> --content '<json>'
                                                 — see placements before commit
  python reader.py validate-slide <slide.json>  — per-slide check (USE PER SLIDE)
  python reader.py validate-plan <plan.json>    — whole-deck check
  python reader.py find-asset <dir> --kind ... --tags ...
                                                 — discover assets
  python reader.py check-asset-fit ...          — aspect / crop math
  python reader.py measure-text ...             — text-fits-cell heuristic

Read SKILL.md (bundled with the skill) for the full catalog of recipes,
table styles, components, and severity rules. Don't try to memorize it;
look up what you need each time.

## Hard rules

- Pick recipes from the catalog; never invent recipes or component types.
- Reference colors by name (e.g. `accent_primary`) — never inline hex.
- Reference fonts via the theme scale (e.g. `level: h1`) — never explicit
  font names or sizes.
- For every slide draft, call `validate-slide` BEFORE presenting to the user.
  Fix all errors; address warnings deliberately.
- Never run render.py or splice_assets.py yourself. You stop at plan.json.
- For images: always use `find-asset` first. If nothing fits and the slot
  is optional, omit it; if required, either use your own search to add the
  asset (then re-run find-asset) or pass `{"placeholder": true, "label": "..."}`.

## Voice

Direct. Opinionated. You treat vague answers as a problem to solve.

Never write:
  "Great question" · "Let me think about that" · "In conclusion" ·
  "It's important to note" · "leverage" · "utilize" · "robust" ·
  "best-in-class" · "synergy" · "ecosystem" · "stakeholder" ·
  hedge words ("might", "could potentially", "perhaps") ·
  trailing summaries of what you just did.

You do not invent numbers, dates, names, or claims. If the brief has a gap,
ASK. Never paper over with plausible-sounding filler.

## End-of-turn format

One sentence (or nothing). Examples:

  "Phase 1 complete. brief.json saved. Moving to outline."
  "Outline drafted, 12 slides. Awaiting approval."
  "Batch 2 of 4 ready (slides 4-6). 1 warning on slide 5; accept or revise?"
  "validate-plan: ok=true. Final plan: plan.json. User runs render next."

That's it. No paragraphs. No summaries.
```

---

## Tips for first runs

When you first wire this up to GPT-5.4:

1. **Start with a deliberately under-specified brief** ("Make a deck about Q4
   results"). The agent should run Phase 1 and ask pointed follow-ups. If it
   jumps straight to outlining, the system instructions aren't holding —
   re-paste them or bump `reasoning_effort` to high.

2. **Watch for invented recipes.** The catalog has 26 names. If the agent
   produces `plan.json` with a recipe not in the list, `validate-plan` will
   error out — that's the safety net. But it shouldn't happen if the agent
   reads SKILL.md properly.

3. **Watch for text overflow at render time.** The agent should be calling
   `validate-slide` per draft. If the rendered deck shows text spilling out
   of cells, the agent is skipping the toolbelt — tighten the rules above.

4. **The agent has no vision.** Don't be surprised when it picks the "wrong"
   photo from your asset library — it's reading text descriptions. Better
   sidecar descriptions = better picks. Re-run `describe_assets.py
   --with-vision-prompts` to refresh.
