# Agent setup (GPT-5.4 and similar)

Two things to configure in your agent platform:

1. **Model parameters** — what to set, with rationale
2. **System instructions** — ready-to-paste text

The agent's runtime needs access to the `skill/` folder in this repo (mount
/ clone / upload — depending on platform). Its working directory should be
`skill/`. Everything the agent needs to compose, validate, and render is
inside that one folder.

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
| `reasoning_summary` | **none** | If left on `auto`, the platform may show the model's chain-of-thought to the user — which looks like the agent "spilling its thoughts" even when the prompt forbids it. Keep `none` unless you're debugging. |
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
  "reasoning": {"effort": "medium", "summary": "none"},
  "text": {"verbosity": "low"}
}
```

For the OpenAI Assistants / Responses API, the field names may differ
slightly (`reasoning.effort` instead of `reasoning_effort`, etc.) — adjust
to your SDK.

---

## 2. System instructions (ready to paste)

The system prompt lives in its own file for easier copy-paste:

📄 **[`AGENT_PROMPT.md`](./AGENT_PROMPT.md)** — open it, select all, paste
into your agent's **system instructions** / **developer message** /
**persona** field. That's the single source of truth for the prompt; this
file just covers the model-parameter settings.

---

## Tips for first runs

When you first wire this up to GPT-5.4:

1. **Vague brief test.** Send "Make a deck about Q4 results" and watch
   that the agent runs a real discovery (1-2 questions at a time,
   acknowledging answers). If it dumps all 5 questions at once or
   narrates "I need to understand the audience first…", the prompt
   isn't holding — re-paste from `AGENT_PROMPT.md` or bump
   `reasoning_effort` to high.

2. **Artifact-existence test.** Halfway through, ask the agent to show
   you the file paths of any artifacts it has created (`outline.json`,
   `slide_N.json`, etc.). If it can't cite paths or the files don't
   exist, it's hallucinating progress — see hard rule about cite-the-path.

3. **Invented-recipe test.** If the agent produces a plan with a recipe
   not in the 26-name catalog, `validate-plan` errors out — safety net
   works. But it shouldn't happen if the agent reads `SKILL.md`.

4. **Text-overflow test.** If the rendered deck shows text spilling out
   of cells, the agent is skipping `validate-slide`. Tighten the
   execution rules in the prompt or escalate `reasoning_effort`.

5. **No vision.** When the agent picks the "wrong" photo from your
   asset library, remember it's reading text descriptions only. Better
   sidecar descriptions = better picks. Re-run `describe_assets.py
   --with-vision-prompts` to refresh.
