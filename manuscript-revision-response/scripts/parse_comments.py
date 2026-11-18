#!/usr/bin/env python3
"""Turn an editor's decision letter and reviewer reports into a numbered revision plan.

Input: plain text (paste the decision e-mail or export the reports to .txt). The parser
recognises blocks headed "Editor", "Associate Editor", "Handling Editor", "Reviewer 1",
"Reviewer #2", "Referee 3" and similar, then splits each block into items at numbered
points ("1.", "2)", "Comment 3:", "Q4.") or bullets; a block with no numbering is split
at blank lines. Items get stable IDs (E.1, AE.2, R1.3 ...) that the response letter uses.

Nothing is classified automatically: category (revise / clarify / disagree / out of
scope), effort and the response are for the author to decide. The plan is written as
JSON (for build_response_letter.py) and Markdown (to read and discuss).

Usage:  python parse_comments.py reviews.txt --out plan.json
        python parse_comments.py --selftest
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HEADER = re.compile(
    r"^\s*(?:comments?\s+(?:from|of|by)\s+(?:the\s+)?)?"
    r"(?P<who>associate\s+editor|handling\s+editor|editor(?:-in-chief)?|reviewer|referee)"
    r"\s*#?\s*(?P<num>\d+)?\s*(?:'s)?\s*(?:comments?|report)?\s*[:.\-–]?\s*$", re.I)
ITEM = re.compile(r"^\s*(?:(?:comment|point|q|issue)\s*)?(?P<n>\d{1,3})\s*[.):]\s+(?P<text>.*\S)", re.I)
BULLET = re.compile(r"^\s*[-*•]\s+(?P<text>.*\S)")


def source_id(who: str, num: str | None) -> tuple[str, str]:
    w = who.lower()
    if "associate" in w or "handling" in w:
        return "AE", "Associate Editor"
    if w.startswith("editor"):
        return "E", "Editor"
    return f"R{num or '?'}", f"Reviewer {num or '?'}"


def split_items(lines: list[str]) -> list[str]:
    items, cur, numbered = [], [], any(ITEM.match(l) or BULLET.match(l) for l in lines)
    for line in lines:
        m = ITEM.match(line) or BULLET.match(line)
        if numbered and m:
            if cur:
                items.append(" ".join(cur).strip())
            cur = [m.group("text")]
        elif not numbered and not line.strip():
            if cur:
                items.append(" ".join(cur).strip()); cur = []
        elif line.strip():
            cur.append(line.strip())
    if cur:
        items.append(" ".join(cur).strip())
    return [i for i in items if len(i) > 3]


def parse(text: str) -> list[dict]:
    blocks, cur_id, cur_name, buf = [], None, None, []
    for line in text.splitlines():
        m = HEADER.match(line)
        if m:
            if cur_id:
                blocks.append((cur_id, cur_name, buf))
            cur_id, cur_name = source_id(m.group("who"), m.group("num")); buf = []
        elif cur_id:
            buf.append(line)
    if cur_id:
        blocks.append((cur_id, cur_name, buf))
    if not blocks:
        blocks = [("C", "Comments", text.splitlines())]
    plan, seen = [], {}
    for sid, name, lines in blocks:
        start = seen.get(sid, 0)
        for k, item in enumerate(split_items(lines), start + 1):
            plan.append(dict(id=f"{sid}.{k}", source=name, comment=item, category="", effort="",
                             status="todo", response="", changes="", location=""))
        seen[sid] = start + len(split_items(lines))
    return plan


def to_markdown(plan: list[dict]) -> str:
    rows = ["| ID | Source | Comment (abridged) | Category | Status |", "|---|---|---|---|---|"]
    for p in plan:
        c = p["comment"].replace("|", "/")
        rows.append(f"| {p['id']} | {p['source']} | {c[:140] + ('…' if len(c) > 140 else '')} | {p['category']} | {p['status']} |")
    return "\n".join(rows) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("reviews", nargs="?"); ap.add_argument("--out", default="plan.json")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.reviews:
        ap.error("reviews text file is required")
    plan = parse(Path(a.reviews).read_text(encoding="utf-8", errors="replace"))
    Path(a.out).write_text(json.dumps(plan, indent=2, ensure_ascii=False), encoding="utf-8")
    Path(a.out).with_suffix(".md").write_text(to_markdown(plan), encoding="utf-8")
    by = {}
    for p in plan:
        by[p["source"]] = by.get(p["source"], 0) + 1
    print(f"{len(plan)} items: " + ", ".join(f"{k} {v}" for k, v in by.items()))
    print(f"wrote {a.out} and {Path(a.out).with_suffix('.md')}; check the split against the original before relying on it")
    print("note: text before the first Editor/Reviewer heading is not included; editors often put requests in the letter body, so add those by hand")
    return 0


SAMPLE = """Dear Dr. Bodrud-Doza,
Your manuscript requires major revision.

Comments from the Editor:
Please shorten the Introduction and address both reviewers.

Reviewer #1:
1. The calibration period is short. Please justify.
2. Figure 3 axis labels lack units.
3) Discuss legacy phosphorus as an alternative explanation.

Reviewer 2's comments
- The indicator selection criteria are unclear.
- Consider adding a table of data sources.
"""


def selftest() -> int:
    plan = parse(SAMPLE)
    ids = [p["id"] for p in plan]
    assert ids == ["E.1", "R1.1", "R1.2", "R1.3", "R2.1", "R2.2"], ids
    assert plan[3]["comment"].startswith("Discuss legacy") and plan[0]["source"] == "Editor"
    assert all(p["category"] == "" and p["status"] == "todo" for p in plan)
    assert "| R1.2 |" in to_markdown(plan)
    print("parse_comments selftest passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
