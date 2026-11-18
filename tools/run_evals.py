#!/usr/bin/env python3
"""Run a skill's test cases with Claude Code's built-in evaluator.

Each skill keeps its tests in <skill>/evals/<case>/ (prompt.md, case.yaml, graders/),
the layout `claude plugin eval` reads. This wrapper validates the cases first, then
calls the evaluator for one skill or all of them, with a no-skill baseline arm so the
report shows what the skill adds.

These are real, billed model runs on your Claude account. Start with one skill.

Usage:  python tools/run_evals.py --list
        python tools/run_evals.py water-quality-analysis
        python tools/run_evals.py water-quality-analysis --case "*trend*"
        python tools/run_evals.py --all
Requires Claude Code v2.1.269 or later (`claude --version`).
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys

from _common import REPO, skill_dirs
from validate_skills import check_skill


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("skills", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--list", action="store_true", help="list skills and their cases, run nothing")
    ap.add_argument("--case", help="only cases whose name matches this glob")
    ap.add_argument("--tools", default="Write,Edit,Bash", help="tools the runs may use (default: Write,Edit,Bash)")
    a = ap.parse_args()

    skills = skill_dirs() if (a.all or a.list) else [REPO / s for s in a.skills]
    if not skills:
        ap.print_help(); return 2
    if a.list:
        for s in skills:
            cases = sorted(p.name for p in (s / "evals").glob("*/") if (p / "case.yaml").is_file())
            print(f"{s.name}: {len(cases)} cases")
            for c in cases:
                print(f"   {c}")
        return 0
    if shutil.which("claude") is None:
        print("Claude Code CLI not found; install it, or run the cases by hand from evals/*/prompt.md")
        return 1
    rc = 0
    for s in skills:
        errs = check_skill(s)
        if errs:
            print(f"{s.name}: fix these before running:\n  - " + "\n  - ".join(errs)); rc = 1; continue
        cmd = ["claude", "plugin", "eval", ".", "--allow-tools", a.tools]
        if any((p / "files").is_dir() for p in (s / "evals").iterdir()):
            cmd.append("--scaffold")
        if a.case:
            cmd += ["--case", a.case]
        print(f"\n== {s.name}: {' '.join(cmd)}")
        rc |= subprocess.call(cmd, cwd=s)
    return rc


if __name__ == "__main__":
    sys.exit(main())
