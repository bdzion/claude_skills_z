"""Shared helpers for the repository tools (standard library only)."""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
# Upload limits observed on claude.ai (Customize -> Skills), November 2026:
# a 182-file zip uploaded, 224- and 255-file zips were refused for too many files,
# and a zip that contained another zip was refused. 180 keeps a margin.
MAX_UPLOAD_FILES = 180
MAX_DESCRIPTION_CHARS = 1024
ARCHIVE_SUFFIXES = (".zip", ".tar", ".gz", ".tgz", ".7z", ".rar", ".skill")
EXCLUDE_FROM_UPLOAD = {"evals", "__pycache__", ".ipynb_checkpoints"}


def skill_dirs() -> list[Path]:
    """Every top-level folder that holds a SKILL.md."""
    return sorted(p.parent for p in REPO.glob("*/SKILL.md"))


def read_frontmatter(skill_md: Path) -> dict[str, str]:
    """Minimal YAML frontmatter reader for the two keys skills need (name, description)."""
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError(f"{skill_md}: no frontmatter")
    block = text.split("---", 2)[1]
    out: dict[str, str] = {}
    for key in ("name", "description"):
        m = re.search(rf"^{key}:\s*(.+)$", block, re.M)
        if m:
            out[key] = m.group(1).strip().strip('"').strip("'")
    return out


def upload_files(skill: Path) -> list[Path]:
    """Files that go into an upload zip for this skill (tests and caches left out)."""
    files = []
    for p in sorted(skill.rglob("*")):
        if p.is_file() and not (set(p.relative_to(skill).parts) & EXCLUDE_FROM_UPLOAD):
            files.append(p)
    return files
