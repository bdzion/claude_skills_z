#!/usr/bin/env python3
"""Build upload zips for claude.ai (Customize -> Skills -> Add -> Upload skill).

Each zip holds one top-level folder named after the skill, with SKILL.md inside, and
leaves out evals/ and caches. The script refuses to build a zip that claude.ai would
refuse (too many files, or an archive inside).

Usage:  python tools/package_skill.py water-quality-analysis [more skills...]
        python tools/package_skill.py --all
Zips are written to dist/.
"""
from __future__ import annotations

import sys
import zipfile

from _common import (ARCHIVE_SUFFIXES, MAX_UPLOAD_FILES, REPO, skill_dirs,
                     upload_files)


def build(skill) -> str:
    files = upload_files(skill)
    if len(files) > MAX_UPLOAD_FILES:
        raise SystemExit(f"{skill.name}: {len(files)} files exceeds the upload limit ({MAX_UPLOAD_FILES})")
    nested = [f.name for f in files if f.name.lower().endswith(ARCHIVE_SUFFIXES)]
    if nested:
        raise SystemExit(f"{skill.name}: contains archives, which the uploader refuses: {nested}")
    out = REPO / "dist" / f"{skill.name}.zip"
    out.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for f in files:
            z.write(f, f"{skill.name}/{f.relative_to(skill).as_posix()}")
    return f"{out.relative_to(REPO)}  ({len(files)} files)"


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__); return 2
    targets = skill_dirs() if argv == ["--all"] else [REPO / a.strip("/") for a in argv]
    for t in targets:
        if not (t / "SKILL.md").is_file():
            raise SystemExit(f"{t.name}: no SKILL.md")
        print(build(t))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
