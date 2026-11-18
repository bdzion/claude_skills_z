#!/usr/bin/env python3
"""Build an editable PowerPoint research poster from a JSON content spec, then check it.

Content first: the spec holds the text, figures and section plan the author approved;
this script only lays it out on a fixed grid so nothing is hand-placed.

Spec (see assets/example_spec.json):
  size        "A0-portrait" | "A0-landscape" | "A1-portrait" | "48x36" | "36x48" | [W, H] inches
  columns     2-4;   colours {"header": hex, "accent": hex, "conclusion": hex} (optional)
  title, authors, affiliations, contact, poster_id, logos [paths] (optional)
  sections    [{"heading", "column" (0-based), "paragraphs": [...], "image": path,
                "caption", "image_width_frac": 0-1 (default 1)}]
  conclusion  {"headline", "text"}

Typography scales with poster size from A0-equivalent values (body 32 pt, never under
24 pt at A0). PowerPoint caps slides at 56 in; larger posters must be built at half
scale and printed at 200 % (the script refuses sizes over 56 in and says so).

Checks written to <out>_layout.json and printed:
  * estimated column overflow (text height estimated from font size and column width;
    the render is the final judge),
  * image resolution at printed size (warn under 150 dpi),
  * minimum font size.

Usage:
  python build_poster.py spec.json --out poster.pptx [--render]
  python build_poster.py --selftest
--render converts to PDF with LibreOffice (soffice) and writes a PNG preview with
PyMuPDF, when those are installed. On a machine with PowerPoint, export the PDF from
PowerPoint itself for exact fonts.
"""
from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

SIZES = {"A0-portrait": (33.11, 46.81), "A0-landscape": (46.81, 33.11), "A1-portrait": (23.39, 33.11),
         "48x36": (48.0, 36.0), "36x48": (36.0, 48.0)}
A0_SHORT = 33.11
BASE_PT = dict(title=96, authors=40, affil=30, heading=54, body=32, caption=26, concl_head=64, concl_text=34)
MIN_BODY_A0 = 24
FONT = "Calibri"


def rgb(h):
    h = h.lstrip("#"); return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def text_height_in(text, size_pt, width_in, line_spacing=1.2, char_w=0.46, para_space=0.4):
    """Wrapped-text height estimate: mean glyph width ~0.46 em (Calibri/Arial body text),
    plus the paragraph spacing add_text applies. Checked against LibreOffice renders;
    the rendered poster remains the final check."""
    cpl = max(1, int((width_in - 0.1) * 72 / (char_w * size_pt)))
    paras = text.split("\n")
    lines = sum(max(1, math.ceil(len(p) / cpl)) for p in paras)
    return (lines * line_spacing * size_pt + (len(paras) - 1) * para_space * size_pt) / 72 + 0.1


def add_text(slide, x, y, w, h, paras, size, bold=False, color="222222", align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = True; tf.vertical_anchor = anchor
    for m in ("margin_left", "margin_right", "margin_top", "margin_bottom"):
        setattr(tf, m, Inches(0.05))
    for i, p in enumerate(paras if isinstance(paras, list) else [paras]):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        para.alignment = align
        para.space_after = Pt(size * 0.4)
        r = para.add_run(); r.text = p
        r.font.size = Pt(size); r.font.bold = bold; r.font.name = FONT; r.font.color.rgb = rgb(color)
    return tb


def band(slide, x, y, w, h, color):
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid(); s.fill.fore_color.rgb = rgb(color); s.line.fill.background()
    return s


def build(spec: dict, out: str, base_dir: Path) -> dict:
    W, H = SIZES[spec["size"]] if isinstance(spec["size"], str) else tuple(spec["size"])
    if max(W, H) > 56:
        raise SystemExit(f"{W}x{H} in exceeds PowerPoint's 56 in limit: build at half scale ([{W/2}, {H/2}]) and print at 200 %")
    k = min(W, H) / A0_SHORT
    pt = {n: v * k for n, v in BASE_PT.items()}
    col = {"header": "0B3C5D", "accent": "1F77B4", "conclusion": "E8F1F8", **spec.get("colours", {})}
    margin, gutter = 1.0 * k, 0.7 * k
    ncol = int(spec.get("columns", 3))
    col_w = (W - 2 * margin - (ncol - 1) * gutter) / ncol
    warnings: list[str] = []

    prs = Presentation(); prs.slide_width, prs.slide_height = Inches(W), Inches(H)
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # header band: title, authors, affiliations, contact, poster ID, logos
    inner_w = W - 2 * margin
    logos = spec.get("logos", [])
    logo_w = 4.0 * k * len(logos)
    th = text_height_in(spec["title"], pt["title"], inner_w - logo_w)
    ah = text_height_in(spec.get("authors", ""), pt["authors"], inner_w - logo_w)
    fh = text_height_in(spec.get("affiliations", ""), pt["affil"], inner_w - logo_w)
    head_h = margin * 0.6 + th + ah + fh + margin * 0.6
    band(slide, 0, 0, W, head_h, col["header"])
    y = margin * 0.6
    add_text(slide, margin, y, inner_w - logo_w, th, spec["title"], pt["title"], bold=True, color="FFFFFF"); y += th
    add_text(slide, margin, y, inner_w - logo_w, ah, spec.get("authors", ""), pt["authors"], color="FFFFFF"); y += ah
    meta = " | ".join(x for x in [spec.get("affiliations", ""), spec.get("contact", ""), spec.get("poster_id", "")] if x)
    add_text(slide, margin, y, inner_w - logo_w, fh, meta, pt["affil"], color="DDE6EE")
    for i, lg in enumerate(logos):
        p = base_dir / lg
        if p.is_file():
            slide.shapes.add_picture(str(p), Inches(W - margin - (i + 1) * 4.0 * k + 0.3 * k), Inches(margin * 0.6), width=Inches(3.4 * k))
        else:
            warnings.append(f"logo not found: {lg}")

    # conclusion band (bottom), sized from its text
    c = spec.get("conclusion", {})
    ch_h = text_height_in(c.get("headline", ""), pt["concl_head"], inner_w - 1.0 * k)
    ct_h = text_height_in(c.get("text", ""), pt["concl_text"], inner_w - 1.0 * k)
    concl_h = ch_h + ct_h + 1.2 * k
    concl_top = H - margin - concl_h
    band(slide, margin, concl_top, inner_w, concl_h, col["conclusion"])
    add_text(slide, margin + 0.5 * k, concl_top + 0.4 * k, inner_w - 1.0 * k, ch_h, c.get("headline", ""), pt["concl_head"], bold=True, color=col["header"])
    add_text(slide, margin + 0.5 * k, concl_top + 0.4 * k + ch_h, inner_w - 1.0 * k, ct_h, c.get("text", ""), pt["concl_text"])

    # columns
    top = head_h + margin
    cursor = [top] * ncol
    layout = []
    for s in spec["sections"]:
        ci = int(s.get("column", 0)); x = margin + ci * (col_w + gutter); y = cursor[ci]
        hh = text_height_in(s["heading"], pt["heading"], col_w) + 0.2 * k
        band(slide, x, y, col_w, hh, col["accent"])
        add_text(slide, x + 0.15 * k, y, col_w - 0.3 * k, hh, s["heading"], pt["heading"], bold=True, color="FFFFFF", anchor=MSO_ANCHOR.MIDDLE)
        y += hh + 0.3 * k
        body = "\n".join(s.get("paragraphs", []))
        if body:
            bh = text_height_in(body, pt["body"], col_w)
            add_text(slide, x, y, col_w, bh, s["paragraphs"], pt["body"]); y += bh + 0.2 * k
        if s.get("image"):
            p = base_dir / s["image"]
            if not p.is_file():
                warnings.append(f"{s['heading']}: image not found: {s['image']}")
            else:
                from PIL import Image
                with Image.open(p) as im:
                    px_w, px_h = im.size
                iw = col_w * float(s.get("image_width_frac", 1.0)); ih = iw * px_h / px_w
                slide.shapes.add_picture(str(p), Inches(x + (col_w - iw) / 2), Inches(y), width=Inches(iw))
                dpi = px_w / iw
                if dpi < 150:
                    warnings.append(f"{s['heading']}: image prints at {dpi:.0f} dpi (< 150); supply a larger or vector version")
                y += ih + 0.15 * k
                if s.get("caption"):
                    cap_h = text_height_in(s["caption"], pt["caption"], col_w)
                    add_text(slide, x, y, col_w, cap_h, s["caption"], pt["caption"], color="555555"); y += cap_h
        y += gutter
        layout.append(dict(section=s["heading"], column=ci, top_in=round(cursor[ci], 2), bottom_in=round(y, 2)))
        cursor[ci] = y
    avail = concl_top - gutter * 0.5
    for i, bottom in enumerate(cursor):
        if bottom > avail:
            warnings.append(f"column {i}: content runs about {bottom - avail:.1f} in past the conclusion band; cut text or move a section")
    if pt["body"] < MIN_BODY_A0 * k:
        warnings.append("body text below minimum size")
    prs.save(out)
    report = dict(size_in=[W, H], scale_vs_A0=round(k, 3), columns=ncol, column_width_in=round(col_w, 2),
                  font_pt={n: round(v, 1) for n, v in pt.items()},
                  column_fill_pct=[round(100 * (b - top) / (avail - top)) for b in cursor],
                  sections=layout, warnings=warnings)
    Path(out).with_name(Path(out).stem + "_layout.json").write_text(json.dumps(report, indent=2))
    return report


def render(pptx: str, dpi: int = 20) -> list[str]:
    out = []
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        return ["LibreOffice not found: export the PDF from PowerPoint and preview it there"]
    d = str(Path(pptx).resolve().parent)
    subprocess.run([soffice, "--headless", "--convert-to", "pdf", "--outdir", d, pptx], check=True, capture_output=True, timeout=300)
    pdf = str(Path(pptx).with_suffix(".pdf")); out.append(pdf)
    try:
        import pymupdf
        doc = pymupdf.open(pdf); png = str(Path(pptx).with_suffix(".png"))
        doc[0].get_pixmap(dpi=dpi).save(png); out.append(png)
    except ImportError:
        out.append("PyMuPDF not installed: no PNG preview")
    return out


def selftest() -> int:
    import tempfile

    from PIL import Image
    d = Path(tempfile.mkdtemp())
    Image.new("RGB", (3000, 1800), (200, 220, 240)).save(d / "fig.png")
    Image.new("RGB", (400, 300), (240, 200, 200)).save(d / "small.png")
    spec = {"size": "A0-portrait", "columns": 3, "title": "Test poster title", "authors": "A. Author, B. Author",
            "affiliations": "University", "sections": [
                {"heading": "Background", "column": 0, "paragraphs": ["Short text. " * 20]},
                {"heading": "Methods", "column": 1, "paragraphs": ["Text. " * 30], "image": "fig.png", "caption": "Figure 1."},
                {"heading": "Results", "column": 2, "paragraphs": ["Text. " * 30], "image": "small.png"}],
            "conclusion": {"headline": "One-sentence takeaway.", "text": "Supporting paragraph."}}
    r = build(spec, str(d / "p.pptx"), d)
    assert (d / "p.pptx").is_file() and not any("past the conclusion" in w for w in r["warnings"]), r["warnings"]
    assert any(w.startswith("Results:") and "dpi" in w for w in r["warnings"]), "low-resolution image must be flagged"
    assert abs(r["font_pt"]["body"] - 32) < 0.1
    spec["sections"][0]["paragraphs"] = ["Very long text that keeps going. " * 400]
    r2 = build(spec, str(d / "p2.pptx"), d)
    assert any("past the conclusion" in w for w in r2["warnings"]), "overflow must be flagged"
    try:
        build({**spec, "size": [72, 36]}, str(d / "big.pptx"), d)
        raise AssertionError("oversize slide must be refused")
    except SystemExit:
        pass
    print("build_poster selftest passed")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", nargs="?"); ap.add_argument("--out", default="poster.pptx")
    ap.add_argument("--render", action="store_true"); ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.spec:
        ap.error("spec JSON is required")
    spec_path = Path(a.spec)
    rep = build(json.loads(spec_path.read_text(encoding="utf-8")), a.out, spec_path.parent)
    print(json.dumps({k: rep[k] for k in ("size_in", "columns", "font_pt", "column_fill_pct", "warnings")}, indent=2))
    if a.render:
        for p in render(a.out):
            print("render:", p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
