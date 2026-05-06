#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import tempfile


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else Path.cwd()
NOTE = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")

REQUIRED_LINES = (
    "- shared kconfig selftest-alignment self-test: `python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test`",
    "- shared kconfig selftest-alignment guard: `python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py`",
    "- shared kconfig bridge self-test: `python3 scripts/zigux/check-kconfig-bridge.py --self-test`",
    "- shared kconfig bridge parity gate: `python3 scripts/zigux/check-kconfig-bridge.py`",
)

REQUIRED_SUBSTRINGS = (
    "`phase2-kconfig` Makefile lane",
    "`zig test scripts/zigux/kconfig/conf_bridge.zig`",
    "`zig test scripts/zigux/kconfig/confdata_bridge.zig`",
)

EXPECTED_SELF_TEST_CASE_COUNT = 8


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []
    note_text = read_text(root / NOTE)

    for line in REQUIRED_LINES:
        count = sum(1 for item in note_text.splitlines() if item.strip() == line)
        if count == 0:
            issues.append(f"missing_line:{line}")
        elif count != 1:
            issues.append(f"duplicate_line:{line}:count={count}")

    for marker in REQUIRED_SUBSTRINGS:
        if marker not in note_text:
            issues.append(f"missing_marker:{marker}")

    return issues


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_valid_note() -> str:
    return """# Phase 2 Toolchain Bootstrap Notes

- shared kconfig selftest-alignment self-test: `python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test`
- shared kconfig selftest-alignment guard: `python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py`
- shared kconfig bridge self-test: `python3 scripts/zigux/check-kconfig-bridge.py --self-test`
- shared kconfig bridge parity gate: `python3 scripts/zigux/check-kconfig-bridge.py`
- `python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test` and `python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py` keep this bootstrap note aligned with the already-shipped `check-kconfig-bridge.py` self-test plus live guard, the `phase2-kconfig` Makefile lane, and the bounded `zig test scripts/zigux/kconfig/conf_bridge.zig` plus `zig test scripts/zigux/kconfig/confdata_bridge.zig` replays.
"""


def run_self_test() -> int:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="zigux_p2_kconfig_bootstrap_note_") as tmp_dir:
        root = Path(tmp_dir)
        note_path = root / NOTE

        write_text(note_path, build_valid_note())
        assert collect_issues(root) == []

        for line in REQUIRED_LINES:
            write_text(note_path, build_valid_note().replace(line + "\n", "", 1))
            issues = collect_issues(root)
            assert f"missing_line:{line}" in issues
            cases += 1

        duplicate_line = REQUIRED_LINES[2]
        write_text(
            note_path,
            build_valid_note().replace(
                duplicate_line + "\n",
                duplicate_line + "\n" + duplicate_line + "\n",
                1,
            ),
        )
        issues = collect_issues(root)
        assert f"duplicate_line:{duplicate_line}:count=2" in issues
        cases += 1

        for marker in REQUIRED_SUBSTRINGS:
            write_text(note_path, build_valid_note().replace(marker, "", 1))
            issues = collect_issues(root)
            assert f"missing_marker:{marker}" in issues
            cases += 1

    assert cases == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_KCONFIG_BOOTSTRAP_NOTE_SELF_TEST=pass")
    print(f"PHASE2_KCONFIG_BOOTSTRAP_NOTE_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 2 bootstrap note keeps the shipped kconfig self-test and bridge hooks explicit."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root)
    if issues:
        print("PHASE2_KCONFIG_BOOTSTRAP_NOTE=fail")
        print("PHASE2_KCONFIG_BOOTSTRAP_NOTE_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE2_KCONFIG_BOOTSTRAP_NOTE_ISSUES_END")
        return 1

    print("PHASE2_KCONFIG_BOOTSTRAP_NOTE=pass")
    print(f"PHASE2_KCONFIG_BOOTSTRAP_NOTE_REQUIRED_LINE_COUNT={len(REQUIRED_LINES)}")
    print(f"PHASE2_KCONFIG_BOOTSTRAP_NOTE_REQUIRED_MARKER_COUNT={len(REQUIRED_SUBSTRINGS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
