#!/usr/bin/env python3
"""Look up every DOI written in the skills against Crossref and print what each resolves to.

Use it after adding a reference to a skill: a DOI that does not resolve, or resolves to a
different paper than the one cited, is an error to fix before committing. The check only
sends the DOIs themselves to api.crossref.org.

Usage:  python tools/check_dois.py                 # all skills
        python tools/check_dois.py water-quality-analysis
Set CROSSREF_MAILTO=you@example.org to join Crossref's polite pool.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

from _common import REPO, skill_dirs

DOI = re.compile(r"\b(10\.\d{4,9}/[^\s\"<>`|]+)")


def lookup(doi: str) -> str:
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="/()")
    ua = "claude_skills_z-doi-check/1.0" + (f" (mailto:{os.environ['CROSSREF_MAILTO']})" if os.environ.get("CROSSREF_MAILTO") else "")
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": ua}), timeout=20) as r:
            m = json.load(r)["message"]
    except Exception as e:  # noqa: BLE001 - report any failure as unresolved
        return f"NOT RESOLVED ({e.__class__.__name__})"
    au = (m.get("author") or [{}])[0].get("family", "?")
    yr = (m.get("issued", {}).get("date-parts") or [[None]])[0][0]
    return f"{au} {yr}. {(m.get('title') or [''])[0][:90]}"


def main(argv: list[str]) -> int:
    skills = [s for s in skill_dirs() if not argv or s.name in argv]
    bad = 0
    for s in skills:
        dois = set()
        for f in s.rglob("*.md"):
            if "evals" in f.parts:
                continue
            for d in DOI.findall(f.read_text(encoding="utf-8")):
                d = d.rstrip(".,;:]")
                while d.endswith(")") and d.count(")") > d.count("("):
                    d = d[:-1].rstrip(".,;:")  # drop a closing bracket that belongs to the text
                dois.add(d)
        if not dois:
            continue
        print(f"\n== {s.name} ({len(dois)} DOIs)")
        for d in sorted(dois):
            res = lookup(d)
            bad += res.startswith("NOT")
            print(f"  {d}\n      -> {res}")
            time.sleep(0.2)
    print(f"\n{bad} unresolved" if bad else "\nall DOIs resolved; check each title matches the citation")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
