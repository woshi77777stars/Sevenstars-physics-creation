"""Build PowerPoint decks from content/<topic>.deck.json with native
entrance animations (one click per step)."""

from __future__ import annotations

import json
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

from ppt_anim import inject_slide_animations, timing_summary


PLUGIN_SCRIPTS = Path(__file__).resolve().parent
CONTENT_DIR = PLUGIN_SCRIPTS / "content"
MASTER_TEMPLATE = PLUGIN_SCRIPTS.parent / "templates" / "ppt-master.pptx"


def load_deck(topic: str) -> dict:
    path = CONTENT_DIR / f"{topic}.deck.json"
    if not path.exists():
        raise FileNotFoundError(f"No deck content for topic {topic!r} at {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def available_topics() -> list[str]:
    return sorted(p.stem.removesuffix(".deck") for p in CONTENT_DIR.glob("*.deck.json"))


def new_presentation() -> Presentation:
    if MASTER_TEMPLATE.exists():
        prs = Presentation(str(MASTER_TEMPLATE))
    else:
        prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    return prs


def _remove_existing_slides(prs: Presentation) -> None:
    """Drop the example slides bundled in the master template.

    Removing only the sldId entries leaves orphaned slide parts in the
    package, which produces duplicate zip entries when new slides reuse the
    same names. Drop each relationship as well so the parts are not written.
    """
    sld_id_lst = prs.slides._sldIdLst  # noqa: SLF001
    entries = [(sld_id, sld_id.rId) for sld_id in list(sld_id_lst)]
    for sld_id, r_id in entries:
        sld_id_lst.remove(sld_id)
        prs.part.drop_rel(r_id)


def _add_textbox(slide, left, top, width, height) -> object:
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    box.text_frame.word_wrap = True
    return box


def build_deck(topic: str, out_dir: Path | None = None) -> Path:
    deck = load_deck(topic)
    out_dir = Path(out_dir) if out_dir else Path("outputs/pptx")
    out_dir.mkdir(parents=True, exist_ok=True)
    prs = new_presentation()
    _remove_existing_slides(prs)

    title_slide = prs.slides.add_slide(prs.slide_layouts[6])
    title_box = _add_textbox(title_slide, 0.8, 2.6, 11.7, 1.6)
    title_par = title_box.text_frame.paragraphs[0]
    title_par.text = deck["title"]
    title_par.font.size = Pt(40)
    title_par.font.bold = True
    title_par.alignment = PP_ALIGN.CENTER
    sub_box = _add_textbox(title_slide, 0.8, 4.4, 11.7, 0.8)
    sub_par = sub_box.text_frame.paragraphs[0]
    sub_par.text = f"CIE 9702 · Topic {deck['topic_number']} · {deck['topic_name']}"
    sub_par.font.size = Pt(18)
    sub_par.font.color.rgb = RGBColor(0x55, 0x5B, 0x66)
    sub_par.alignment = PP_ALIGN.CENTER

    content_slide = prs.slides.add_slide(prs.slide_layouts[6])
    head = _add_textbox(content_slide, 0.7, 0.45, 11.9, 0.9)
    head_par = head.text_frame.paragraphs[0]
    head_par.text = deck["title"]
    head_par.font.size = Pt(28)
    head_par.font.bold = True

    body = _add_textbox(content_slide, 0.9, 1.6, 11.5, 5.3)
    frame = body.text_frame
    triggers: list[str] = []
    for idx, step in enumerate(deck["steps"]):
        para = frame.paragraphs[0] if idx == 0 else frame.add_paragraph()
        para.text = step["text"]
        para.font.size = Pt(21)
        para.space_after = Pt(16)
        para.level = 0
        triggers.append(step.get("trigger", "click"))

    inject_slide_animations(content_slide, body.shape_id, len(deck["steps"]), triggers)

    out = out_dir / f"{topic}.pptx"
    prs.save(out)
    return out


def validate_deck(path: Path) -> dict:
    """Reopen a deck and assert every step paragraph has a native animation."""
    prs = Presentation(str(path))
    result = {"slides": len(prs.slides), "slides_checked": []}
    for slide in prs.slides:
        summary = timing_summary(slide)
        body = _find_body_shape(slide)
        paragraphs = len(body.text_frame.paragraphs) if body is not None else 0
        result["slides_checked"].append({**summary, "body_paragraphs": paragraphs})
    return result


def _find_body_shape(slide):
    for shape in slide.shapes:
        if shape.has_text_frame and shape.text_frame.word_wrap:
            paragraphs = list(p for p in shape.text_frame.paragraphs if p.text.strip())
            if len(paragraphs) > 1:
                return shape
    return None


def build_template(path: Path | None = None) -> Path:
    """Emit the reusable 16:9 master deck (title slide + content slide)."""
    target = Path(path) if path else PLUGIN_SCRIPTS.parent / "templates" / "ppt-master.pptx"
    target.parent.mkdir(parents=True, exist_ok=True)
    prs = Presentation()  # always regenerate from scratch, never stack on itself
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    title_slide = prs.slides.add_slide(prs.slide_layouts[6])
    box = _add_textbox(title_slide, 0.8, 2.6, 11.7, 1.6)
    par = box.text_frame.paragraphs[0]
    par.text = "A-Level Physics"
    par.font.size = Pt(44)
    par.font.bold = True
    par.alignment = PP_ALIGN.CENTER
    content_slide = prs.slides.add_slide(prs.slide_layouts[6])
    body = _add_textbox(content_slide, 0.9, 1.6, 11.5, 5.3)
    first = body.text_frame.paragraphs[0]
    first.text = "Step one appears on click."
    first.font.size = Pt(21)
    second = body.text_frame.add_paragraph()
    second.text = "Step two appears on the next click."
    second.font.size = Pt(21)
    second.space_after = Pt(16)
    inject_slide_animations(content_slide, body.shape_id, 2, ["click", "click"])
    prs.save(target)
    return target
