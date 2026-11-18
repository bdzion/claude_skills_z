#!/usr/bin/env python3
"""Build the point-by-point response-to-reviewers letter (.docx) from the revision plan.

Input: the plan JSON from parse_comments.py, filled in as the revision proceeds
(response, changes, location for each item), plus optional letter metadata:

  {"journal": "...", "manuscript_id": "...", "title": "...", "authors": "...",
   "opening": "paragraph to the editor", "items": [ ...plan items... ]}
  (a bare list of items is accepted too)

Layout per item: "Comment R1.3" heading, the reviewer's text (italic, grey, indented),
"Response:" in colour, then "Changes in the manuscript (location):" with the revised text
indented. Items without a response are written with a red [RESPONSE PENDING] marker and
listed on the console, so an unfinished letter cannot pass for a finished one.

Usage:  python build_response_letter.py plan.json --out response_letter.docx
           [--font Calibri --size 11 --colour 1F4E79]
        python build_response_letter.py --selftest
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt, RGBColor


def _rgb(h):
    h = h.lstrip("#"); return RGBColor(int(h[:2], 16), int(h[2:4], 16), int(h[4:], 16))


def _para(doc, text="", bold=False, italic=False, colour=None, indent_cm=0.0, size=None, space_after=6):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(indent_cm); p.paragraph_format.space_after = Pt(space_after)
    if text:
        r = p.add_run(text); r.bold = bold; r.italic = italic
        if colour:
            r.font.color.rgb = _rgb(colour)
        if size:
            r.font.size = Pt(size)
    return p


def build(data, out: str, font="Calibri", size=11, colour="1F4E79") -> list[str]:
    meta = data if isinstance(data, dict) else {"items": data}
    items = meta["items"]
    doc = Document()
    st = doc.styles["Normal"]; st.font.name = font; st.font.size = Pt(size)
    for s in doc.sections:
        s.left_margin = s.right_margin = Cm(2.5)
    h = doc.add_paragraph(); h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = h.add_run("Response to the Editor and Reviewers"); r.bold = True; r.font.size = Pt(size + 3)
    for label, key in (("Journal", "journal"), ("Manuscript ID", "manuscript_id"), ("Title", "title"), ("Authors", "authors")):
        if meta.get(key):
            p = _para(doc, space_after=0); p.add_run(f"{label}: ").bold = True; p.add_run(meta[key])
    _para(doc)
    _para(doc, meta.get("opening") or "[Opening paragraph to the editor: thank the editor and reviewers once, "
          "summarise the main changes in two or three sentences, and explain how changes are marked in the revised manuscript.]")
    pending, current = [], None
    for it in items:
        if it["source"] != current:
            current = it["source"]
            doc.add_heading(current, level=2)
        _para(doc, f"Comment {it['id']}", bold=True, space_after=2)
        _para(doc, it["comment"], italic=True, colour="595959", indent_cm=0.75)
        p = _para(doc, space_after=4)
        rr = p.add_run("Response: "); rr.bold = True; rr.font.color.rgb = _rgb(colour)
        if it.get("response", "").strip():
            r2 = p.add_run(it["response"].strip()); r2.font.color.rgb = _rgb(colour)
        else:
            r2 = p.add_run("[RESPONSE PENDING]"); r2.bold = True; r2.font.color.rgb = _rgb("C00000")
            pending.append(it["id"])
        if it.get("changes", "").strip():
            loc = f" ({it['location']})" if it.get("location") else " ([location to add])"
            _para(doc, f"Changes in the manuscript{loc}:", bold=True, space_after=2)
            _para(doc, it["changes"].strip(), indent_cm=0.75)
        _para(doc, space_after=2)
    doc.save(out)
    return pending


def selftest() -> int:
    import tempfile
    sys.path.insert(0, str(Path(__file__).parent))
    from parse_comments import SAMPLE, parse
    plan = parse(SAMPLE)
    plan[1].update(response="We agree and now justify the period in Section 2.3.", changes="The calibration period (2012–2017) spans wet and dry years ...", location="page 7, lines 140–146")
    out = Path(tempfile.mkdtemp()) / "letter.docx"
    pending = build({"journal": "J. Environ. Manage.", "manuscript_id": "JEMA-D-26-0000", "items": plan}, str(out))
    assert out.is_file() and pending == ["E.1", "R1.2", "R1.3", "R2.1", "R2.2"], pending
    text = "\n".join(p.text for p in Document(str(out)).paragraphs)
    assert "Comment R1.1" in text and "page 7, lines 140–146" in text and text.count("[RESPONSE PENDING]") == 5
    print("build_response_letter selftest passed")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plan", nargs="?"); ap.add_argument("--out", default="response_letter.docx")
    ap.add_argument("--font", default="Calibri"); ap.add_argument("--size", type=int, default=11)
    ap.add_argument("--colour", default="1F4E79"); ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.plan:
        ap.error("plan JSON is required")
    pending = build(json.loads(Path(a.plan).read_text(encoding="utf-8")), a.out, a.font, a.size, a.colour)
    print(f"wrote {a.out}")
    if pending:
        print(f"{len(pending)} item(s) still without a response: {', '.join(pending)}")
    return 1 if pending else 0


if __name__ == "__main__":
    sys.exit(main())
