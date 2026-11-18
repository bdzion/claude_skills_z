#!/usr/bin/env python3
"""Run the built-in self-test of every bundled script (no network, no model calls).

A script takes part when its source contains "def selftest". Scripts with a
`--selftest` flag are called with it; modules without a CLI (e.g. zfig.py) run their
self-test when executed directly.

Usage:  python tools/selftest.py [skill ...]
"""
from __future__ import annotations

import subprocess
import sys

from _common import skill_dirs


def main(argv: list[str]) -> int:
    failed = 0
    for s in skill_dirs():
        if argv and s.name not in argv:
            continue
        for script in sorted((s / "scripts").glob("*.py")) if (s / "scripts").is_dir() else []:
            src = script.read_text(encoding="utf-8")
            if "def selftest" not in src:
                continue
            cmd = [sys.executable, str(script)] + (["--selftest"] if "--selftest" in src else [])
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            ok = r.returncode == 0
            failed += not ok
            print(f"{'ok  ' if ok else 'FAIL'}  {s.name}/scripts/{script.name}")
            if not ok:
                print("      " + (r.stderr or r.stdout).strip().replace("\n", "\n      ")[-1500:])
    print("\nall self-tests passed" if not failed else f"\n{failed} self-test(s) failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
