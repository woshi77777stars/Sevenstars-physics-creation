"""Inject native PowerPoint entrance animations into a .pptx slide.

python-pptx has no animation API, so this module appends the standard
`<p:timing>` block to the slide XML. Each target paragraph gets a click
effect (presetID 1 = Appear). The XML shape follows the canonical
PowerPoint presentation markup.
"""

from __future__ import annotations

from lxml import etree


_P = "http://schemas.openxmlformats.org/presentationml/2006/main"


def _q(tag: str) -> str:
    return f"{{{_P}}}{tag}"


def _sub(parent, tag: str, **attrs) -> etree._Element:
    el = etree.SubElement(parent, _q(tag))
    for key, value in attrs.items():
        el.set(key, str(value))
    return el


def _condition(parent, delay: str = "0", evt: str | None = None) -> etree._Element:
    attrs = {"delay": delay}
    if evt:
        attrs["evt"] = evt
    return _sub(parent, "cond", **attrs)


def _click_effect(shape_id: int, paragraph_index: int, effect_id: int, on_click: bool) -> etree._Element:
    par = etree.Element(_q("par"))
    outer = _sub(par, "cTn", id=str(effect_id), fill="hold")
    st = _sub(outer, "stCondLst")
    _condition(st, delay="indefinite" if on_click else "0")
    child_lst = _sub(outer, "childTnLst")
    inner_par = _sub(child_lst, "par")
    effect = _sub(
        inner_par,
        "cTn",
        id=str(effect_id + 1),
        presetID="1",
        presetClass="entr",
        presetSubtype="0",
        fill="hold",
        grpId="0",
        nodeType="clickEffect",
    )
    effect_st = _sub(effect, "stCondLst")
    _condition(effect_st, delay="0")
    effect_lst = _sub(effect, "childTnLst")
    set_el = _sub(effect_lst, "set")
    beh = _sub(set_el, "cBhvr")
    beh_ctn = _sub(beh, "cTn", id=str(effect_id + 2), dur="1", fill="hold")
    beh_st = _sub(beh_ctn, "stCondLst")
    _condition(beh_st, delay="0")
    tgt = _sub(beh, "tgtEl")
    sp_tgt = _sub(tgt, "spTgt", spid=str(shape_id))
    tx_el = _sub(sp_tgt, "txEl")
    _sub(tx_el, "pRg", st=str(paragraph_index), end=str(paragraph_index))
    attr_names = _sub(beh, "attrNameLst")
    _sub(attr_names, "attrName").text = "style.visibility"
    to = _sub(set_el, "to")
    _sub(to, "strVal", val="visible")
    return par


def build_timing(shape_id: int, paragraph_count: int, triggers: list[str] | None = None) -> etree._Element:
    """Build `<p:timing>` that reveals each paragraph of a shape on click.

    `triggers[i]` may be "click" (default) or "with_previous".
    """
    timing = etree.Element(_q("timing"))
    tn_lst = _sub(timing, "tnLst")
    par = _sub(tn_lst, "par")
    root_ctn = _sub(par, "cTn", id="1", dur="indefinite", restart="never", nodeType="tmRoot")
    root_lst = _sub(root_ctn, "childTnLst")
    seq = _sub(root_lst, "seq", concurrent="1", nextAc="seek")
    main = _sub(seq, "cTn", id="2", dur="indefinite", nodeType="mainSeq")
    main_lst = _sub(main, "childTnLst")

    effect_id = 10
    for i in range(paragraph_count):
        trigger = (triggers or [])[i] if i < len(triggers or []) else "click"
        main_lst.append(_click_effect(shape_id, i, effect_id, on_click=trigger != "with_previous"))
        effect_id += 3

    prev = _sub(seq, "prevCondLst")
    prev_cond = _condition(prev, delay="0", evt="onPrev")
    _sub(_sub(prev_cond, "tgtEl"), "sldTgt")
    nxt = _sub(seq, "nextCondLst")
    next_cond = _condition(nxt, delay="0", evt="onNext")
    _sub(_sub(next_cond, "tgtEl"), "sldTgt")

    _sub(timing, "bldLst")
    return timing


def inject_slide_animations(slide, shape_id: int, paragraph_count: int, triggers: list[str] | None = None) -> None:
    """Append a click-reveal timing block to a python-pptx slide."""
    sld = slide._element  # noqa: SLF001 - python-pptx internal access, standard practice
    existing = sld.find(_q("timing"))
    if existing is not None:
        sld.remove(existing)
    timing = build_timing(shape_id, paragraph_count, triggers)

    # Schema order inside <p:sld>: cSld, clrMapOvr?, transition?, timing?, extLst?
    anchor = None
    for tag in ("transition", "clrMapOvr"):
        candidate = sld.find(_q(tag))
        if candidate is not None:
            anchor = candidate
            break
    if anchor is None:
        anchor = sld.find(_q("cSld"))
    anchor.addnext(timing)


def timing_summary(slide) -> dict:
    """Extract animation facts from a slide for tests."""
    sld = slide._element  # noqa: SLF001
    timing = sld.find(_q("timing"))
    if timing is None:
        return {"present": False, "issues": []}
    effects = timing.findall(".//" + _q("cTn"))
    click_effects = [e for e in effects if e.get("nodeType") == "clickEffect"]
    prgs = timing.findall(".//" + _q("pRg"))
    spids = {t.get("spid") for t in timing.findall(".//" + _q("spTgt"))}
    issues = []

    # Order inside <p:sld>: cSld first, timing after transition/clrMapOvr.
    sld_tags = [etree.QName(c).localname for c in sld]
    if "timing" in sld_tags:
        if sld_tags.index("cSld") > sld_tags.index("timing"):
            issues.append("timing-before-cSld")
        for forbidden_before in ("transition", "clrMapOvr"):
            if forbidden_before in sld_tags and sld_tags.index(forbidden_before) > sld_tags.index("timing"):
                issues.append(f"timing-before-{forbidden_before}")
        if sld_tags[-1] == "extLst" and sld_tags.index("timing") > sld_tags.index("extLst"):
            issues.append("timing-after-extLst")

    # Every click effect must carry the full canonical set structure.
    for effect in click_effects:
        set_el = effect.find(".//" + _q("set"))
        if set_el is None:
            issues.append("missing-set")
            continue
        if set_el.find(".//" + _q("spTgt")) is None or set_el.find(".//" + _q("pRg")) is None:
            issues.append("missing-paragraph-target")
        if set_el.find(".//" + _q("attrName")) is None:
            issues.append("missing-attrName")
        if set_el.find(".//" + _q("strVal")) is None or set_el.find(".//" + _q("strVal")).get("val") != "visible":
            issues.append("missing-visible-to")

    # <p:bldLst/> must follow <p:tnLst/> as the last child of <p:timing>.
    timing_tags = [etree.QName(c).localname for c in timing]
    if timing_tags and timing_tags != ["tnLst", "bldLst"]:
        issues.append("bad-timing-children")
    return {
        "present": True,
        "click_effects": len(click_effects),
        "paragraph_ranges": [(r.get("st"), r.get("end")) for r in prgs],
        "shape_ids": spids,
        "issues": issues,
    }
