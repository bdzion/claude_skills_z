#!/usr/bin/env python3
"""Check every skill in the repository before it is committed, packaged or uploaded.

Checks per skill:
  * SKILL.md has frontmatter with `name` equal to the folder name and a `description`
    of at most 1024 characters;
  * the upload set (everything except evals/) stays under the claude.ai file limit and
    contains no nested archives;
  * every test-case folder under evals/ has prompt.md, case.yaml (schema 1.1, name equal
    to the folder) and at least one grader with the required header;
  * every skill listed in .claude-plugin/plugin.json exists, and every skill folder is listed.

Usage:  python tools/validate_skills.py            # all skills
        python tools/validate_skills.py water-quality-analysis
Exit status 1 if any check fails.
"""
from __future__ import annotations

import json
import re
import sys

from _common import (ARCHIVE_SUFFIXES, MAX_DESCRIPTION_CHARS, MAX_UPLOAD_FILES, REPO,
                     read_frontmatter, skill_dirs, upload_files)

GRADER_HEAD = re.compile(r"^---\s*\ntype:\s*\w+", re.M)


def check_skill(skill) -> list[str]:
    errs = []
    fm = read_frontmatter(skill / "SKILL.md")
    if fm.get("name") != skill.name:
        errs.append(f"frontmatter name {fm.get('name')!r} != folder {skill.name!r}")
    desc = fm.get("description", "")
    if not desc:
        errs.append("missing description")
    elif len(desc) > MAX_DESCRIPTION_CHARS:
        errs.append(f"description is {len(desc)} chars (> {MAX_DESCRIPTION_CHARS})")
    if re.search(r"<[^<>]*>", desc):
        errs.append("description contains tag-like text such as <id>, which the claude.ai uploader rejects as an XML tag")
    files = upload_files(skill)
    if len(files) > MAX_UPLOAD_FILES:
        errs.append(f"{len(files)} files in the upload set (> {MAX_UPLOAD_FILES})")
    nested = [f.name for f in files if f.name.lower().endswith(ARCHIVE_SUFFIXES)]
    if nested:
        errs.append(f"nested archives would be refused on upload: {nested}")
    evals = skill / "evals"
    if evals.is_dir():
        for case in sorted(p for p in evals.iterdir() if p.is_dir() and p.name not in {"results", "files"}):
            if not (case / "prompt.md").is_file():
                errs.append(f"evals/{case.name}: missing prompt.md")
            cy = case / "case.yaml"
            if not cy.is_file():
                errs.append(f"evals/{case.name}: missing case.yaml")
            else:
                t = cy.read_text(encoding="utf-8")
                if 'schema_version: "1.1"' not in t:
                    errs.append(f"evals/{case.name}: case.yaml needs schema_version: \"1.1\"")
                if not re.search(rf"^name:\s*{re.escape(case.name)}\s*$", t, re.M):
                    errs.append(f"evals/{case.name}: case.yaml name differs from folder")
            graders = sorted((case / "graders").glob("*.md")) if (case / "graders").is_dir() else []
            if not graders:
                errs.append(f"evals/{case.name}: no graders")
            for g in graders:
                if not GRADER_HEAD.match(g.read_text(encoding="utf-8")):
                    errs.append(f"evals/{case.name}/graders/{g.name}: missing grader header")
    return errs


def warnings_for(skill) -> list[str]:
    return [] if (skill / "evals").is_dir() else ["no evals/ folder yet: add test cases before the next edit (see README)"]


def main(argv: list[str]) -> int:
    skills = skill_dirs()
    if argv:
        skills = [s for s in skills if s.name in argv]
    bad = 0
    for s in skills:
        errs = check_skill(s)
        n = len(upload_files(s))
        status = "ok" if not errs else "FAIL"
        print(f"{status:4}  {s.name:32} upload files: {n}")
        for e in errs:
            print(f"      - {e}")
        for w in warnings_for(s):
            print(f"      ~ {w}")
        bad += bool(errs)
    manifest = REPO / ".claude-plugin" / "plugin.json"
    if manifest.is_file() and not argv:
        listed = {p.strip("./") for p in json.loads(manifest.read_text())["skills"]}
        present = {s.name for s in skill_dirs()}
        for missing in sorted(listed - present):
            print(f"FAIL  plugin.json lists {missing!r}, which has no SKILL.md"); bad += 1
        for extra in sorted(present - listed):
            print(f"FAIL  {extra!r} is not listed in plugin.json"); bad += 1
    print(f"\n{bad} problem(s) found" if bad else f"\nall {len(skills)} skills passed")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
