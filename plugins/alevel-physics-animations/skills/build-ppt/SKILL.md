---
name: build-ppt
description: Build PowerPoint decks with native entrance animations for the alevel-physics-animations plugin. Use when a teacher asks for text that appears step by step, a definition/derivation slide set, or an editable .pptx courseware file.
---

# Build a PowerPoint deck (native animations)

Goal: a `.pptx` for PowerPoint/WPS in which each step appears on click, and which the teacher can edit by hand afterwards.

## Standard flow

1. Confirm the topic id with `python scripts/anim.py topics`.
2. Build: `python scripts/anim.py ppt <topic> [--out outputs/pptx]`. `ppt-all` builds all 25 topics.
3. Verify: `python scripts/anim.py verify` reopens every deck and asserts that each step paragraph has its own `<p:timing>` entrance effect and that the text is intact.

## Content model

Decks are data-driven from `scripts/content/<topic>.deck.json`:

```json
{
  "topic": "capacitance",
  "topic_number": 19,
  "topic_name": "Capacitance",
  "title": "Capacitance",
  "steps": [
    {"text": "Capacitance C = Q/V."},
    {"text": "Energy stored = ½CV².", "trigger": "with_previous"}
  ]
}
```

Each step becomes one paragraph. Default trigger is "click"; set `"trigger": "with_previous"` to reveal a step together with the previous one. Keep steps to 4-8 short sentences.

## Edit a generated deck

- Editing the layout after generation: the deck is a normal `.pptx`; open it in PowerPoint or WPS and change text or position. Do not rebuild from scratch when a small edit suffices.
- To change which step appears when, edit `steps` and rebuild — the animation XML is regenerated deterministically.
- Embedding a video: insert the rendered MP4 in PowerPoint directly (Insert > Video); do not hand-edit the animation XML.

## Before first classroom use

Open one generated deck in PowerPoint (or WPS) and step through it once to
confirm the click animations play and no "repair file" prompt appears. The
automated checks assert the canonical XML structure; this one manual open is
the final compatibility gate.

## Implementation notes

- `scripts/ppt_builder.py` builds the deck; `scripts/ppt_anim.py` injects canonical `<p:timing>` XML (presetID 1 = Appear, per-paragraph `<p:pRg>` targets).
- `scripts/templates/ppt-master.pptx` is the reusable 16:9 master. `build_deck`
  loads it (and drops its two example slides) whenever it exists; regenerate
  it with `python scripts/anim.py template`.
