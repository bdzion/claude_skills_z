#!/usr/bin/env python3
"""Check a proposal draft against section limits taken from the CURRENT funder guidelines.

The limits file is written by hand from the funder's official instructions for this
competition (never from memory), and records where they came from:

  {"funder": "Mitacs Accelerate", "source_url": "https://...", "accessed": "2026-11-18",
   "sections": {"Project description": {"max_words": 1500},
                "Lay summary": {"max_chars": 2000, "count_spaces": true}},
   "required_sections": ["Project description", "Lay summary", "Budget justification"]}

The draft is Markdown or plain text with each section under a heading (#, ## or ###)
whose text matches the section name (case-insensitive). For .docx drafts, python-docx is
used when installed (heading styles become sections).

Usage:  python compliance_check.py draft.md limits.json
        python compliance_check.py --selftest
Word counts split on whitespace, as most word processors do; character counts include
spaces unless count_spaces is false. Funder systems may count differently, so leave a margin.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def sections_from_text(text: str) -> dict[str, str]:
    out, cur, buf = {}, None, []
    for line in text.splitlines():
        m = re.match(r"^#{1,3}\s+(.*\S)\s*$", line)
        if m:
            if cur is not None:
                out[cur] = "\n".join(buf).strip()
            cur, buf = m.group(1).strip(), []
        elif cur is not None:
            buf.append(line)
    if cur is not None:
        out[cur] = "\n".join(buf).strip()
    return out


def sections_from_docx(path: str) -> dict[str, str]:
    import docx  # python-docx
    out, cur, buf = {}, None, []
    for p in docx.Document(path).paragraphs:
        if p.style.name.lower().startswith("heading"):
            if cur is not None:
                out[cur] = "\n".join(buf).strip()
            cur, buf = p.text.strip(), []
        elif cur is not None:
            buf.append(p.text)
    if cur is not None:
        out[cur] = "\n".join(buf).strip()
    return out


def check(sections: dict[str, str], limits: dict) -> list[dict]:
    norm = {k.lower(): v for k, v in sections.items()}
    rows = []
    for name, lim in limits.get("sections", {}).items():
        body = norm.get(name.lower())
        if body is None:
            rows.append(dict(section=name, status="MISSING")); continue
        words = len(body.split())
        chars = len(body) if lim.get("count_spaces", True) else len(re.sub(r"\s", "", body))
        status, notes = "ok", []
        if "max_words" in lim and words > lim["max_words"]:
            status = "OVER"; notes.append(f"{words - lim['max_words']} words over")
        if "max_chars" in lim and chars > lim["max_chars"]:
            status = "OVER"; notes.append(f"{chars - lim['max_chars']} characters over")
        if status == "ok" and "max_words" in lim and words > 0.95 * lim["max_words"]:
            notes.append("within 5 % of the word limit; funder counters may differ")
        rows.append(dict(section=name, words=words, chars=chars, status=status, notes="; ".join(notes)))
    for req in limits.get("required_sections", []):
        if req.lower() not in norm and not any(r["section"].lower() == req.lower() for r in rows):
            rows.append(dict(section=req, status="MISSING (required)"))
    return rows


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv == ["--selftest"]:
        return selftest()
    if len(argv) != 2:
        print(__doc__); return 2
    draft, limits_path = argv
    limits = json.loads(Path(limits_path).read_text())
    secs = sections_from_docx(draft) if draft.lower().endswith(".docx") else sections_from_text(Path(draft).read_text(encoding="utf-8"))
    rows = check(secs, limits)
    print(f"# limits: {limits.get('funder', '?')} | source: {limits.get('source_url', 'NOT RECORDED')} | accessed: {limits.get('accessed', 'NOT RECORDED')}")
    for r in rows:
        print(f"{r['status']:18} {r['section']:40} {r.get('words', ''):>6} words {r.get('chars', ''):>7} chars  {r.get('notes', '')}")
    if not limits.get("source_url"):
        print("# warning: limits have no source URL; take them from the official guidelines and record the link")
    return 1 if any(r["status"] != "ok" for r in rows) else 0


def selftest() -> int:
    text = "# Lay summary\n" + "word " * 120 + "\n## Project description\n" + "word " * 1600 + "\n"
    lim = {"sections": {"Lay summary": {"max_words": 150}, "Project description": {"max_words": 1500},
                        "Budget justification": {"max_words": 500}}}
    rows = {r["section"]: r for r in check(sections_from_text(text), lim)}
    assert rows["Lay summary"]["status"] == "ok" and rows["Lay summary"]["words"] == 120
    assert rows["Project description"]["status"] == "OVER" and "100 words over" in rows["Project description"]["notes"]
    assert rows["Budget justification"]["status"] == "MISSING"
    print("compliance_check selftest passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
