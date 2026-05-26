#!/usr/bin/env python3
"""Guard the current Phase 2 no-gap packet and next-safe-step handoff."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
CLOSURE_NOTE = ROOT / "Documentation" / "zigux" / "phase2-closure.md"

EXPECTED_GAP_LINE = "- `PHASE2_CURRENT_GAP_PACKET=`"
EXPECTED_NO_GAP_SNIPPET = (
    "No current repo-reality gaps remain inside the bounded Phase 2 closure packet, "
    "current `master` no longer leaves the local-first archive pair, returned "
    "archive-verification and staged-archive helper packet, installer hook, direct "
    "cross-route packet, returned closure-validator companions, primary artifact helper, "
    "fixdep checker packet, helper-local kconfig allconfig guard, or fixture-backed "
    "manifest guards in the repo-reality-gap bucket."
)
EXPECTED_NEXT_STEP_LINE = (
    "- `PHASE2_NEXT_SAFE_STEP=keep the shared Phase 2 closure packet parked unless one "
    "shared reminder surface drifts again; if the shared backlog reopens first, start "
    "with one smallest truthfulness repair in Documentation/zigux/README.md, "
    "zigux/tests/README.md, or the directly coupled shared checker that proves the "
    "drift, and keep fixdep-, genksyms-, and kconfig-local follow-through in their "
    "dedicated lanes`"
)
REQUIRED_MARKERS = (
    "## Current Repo-Reality Gaps",
    EXPECTED_GAP_LINE,
    EXPECTED_NO_GAP_SNIPPET,
    "## Next Step",
    EXPECTED_NEXT_STEP_LINE,
)
EXACT_COUNT_MARKERS = (
    EXPECTED_GAP_LINE,
    EXPECTED_NO_GAP_SNIPPET,
    EXPECTED_NEXT_STEP_LINE,
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def collect_issues(root: Path) -> list[tuple[str, str]]:
    text = read_text(root / CLOSURE_NOTE.relative_to(ROOT))
    issues: list[tuple[str, str]] = []

    for marker in REQUIRED_MARKERS:
        if marker not in text:
            issues.append(("MISSING_MARKER", marker))

    for marker in EXACT_COUNT_MARKERS:
        count = text.count(marker)
        if count != 1:
            issues.append(("EXACT_COUNT_MISMATCH", f"{count}::{marker}"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_CURRENT_GAP_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    write_text(root / CLOSURE_NOTE.relative_to(ROOT), "\n".join(REQUIRED_MARKERS) + "\n")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 1 + len(REQUIRED_MARKERS) + len(EXACT_COUNT_MARKERS)
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_current_gap_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)

        assert collect_issues(root) == []
        checks_run += 1

        note_path = root / CLOSURE_NOTE.relative_to(ROOT)
        text = read_text(note_path)

        for marker in REQUIRED_MARKERS:
            write_text(note_path, replace_once(text, marker))
            issues = collect_issues(root)
            assert ("MISSING_MARKER", marker) in issues, (marker, issues)
            build_sample_root(root)
            text = read_text(note_path)
            checks_run += 1

        for marker in EXACT_COUNT_MARKERS:
            write_text(note_path, text + marker + "\n")
            issues = collect_issues(root)
            assert ("EXACT_COUNT_MISMATCH", f"2::{marker}") in issues, (marker, issues)
            build_sample_root(root)
            text = read_text(note_path)
            checks_run += 1

        if checks_run != expected_case_count:
            raise AssertionError(
                f"self-test count drift: expected {expected_case_count}, got {checks_run}"
            )

    print("PHASE2_CURRENT_GAP_PACKET=self-test-pass")
    print(f"PHASE2_CURRENT_GAP_PACKET_SELF_TEST_CASES={checks_run}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in regression checks instead of repo validation.",
    )
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal passing sample root and exit.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to validate (defaults to current repo root).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root)
        print(f"PHASE2_CURRENT_GAP_PACKET_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)

    print("PHASE2_CURRENT_GAP_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
