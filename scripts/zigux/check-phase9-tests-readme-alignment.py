#!/usr/bin/env python3
"""Fail-closed guard for the shared Phase 9 tests-root runtime packet."""

from __future__ import annotations

import argparse
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
DEFAULT_TESTS_README = REPO_ROOT / "zigux" / "tests" / "README.md"

REQUIRED_MARKERS = (
    "zigux/tests/runtime_loader_gap_survey.zig",
    "zigux/tests/runtime_loader_gap_manifest.json",
    "zigux/tests/runtime_loader_allocator_init_flow.zig",
    "scripts/zigux/validate-phase9.py",
    "make -C zigux phase9-validate",
    "manifest-backed catalog and ownership map",
    "selftest-hook markers",
    "bounded lifecycle-parity posture",
)


def find_missing_markers(text: str) -> list[str]:
    return [marker for marker in REQUIRED_MARKERS if marker not in text]


def check_readme(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    missing = find_missing_markers(text)
    if not missing:
        print("PHASE9_TESTS_README_ALIGNMENT=pass")
        return 0

    for marker in missing:
        print(f"missing_phase9_tests_readme_marker:{marker}")
    return 1


def run_self_test() -> int:
    good = """
    * zigux/tests/runtime_loader_gap_survey.zig
    * zigux/tests/runtime_loader_gap_manifest.json
    * zigux/tests/runtime_loader_allocator_init_flow.zig
    * scripts/zigux/validate-phase9.py
    * make -C zigux phase9-validate
    * manifest-backed catalog and ownership map
    * selftest-hook markers
    * bounded lifecycle-parity posture
    """
    bad = """
    * zigux/tests/runtime_loader_allocator_init_flow.zig
    * scripts/zigux/validate-phase9.py
    """

    good_missing = find_missing_markers(good)
    if good_missing:
        print(
            "phase9_tests_readme_alignment_self_test_failed:"
            f"unexpected_missing={','.join(good_missing)}"
        )
        return 1

    bad_missing = find_missing_markers(bad)
    expected_missing = {
        "zigux/tests/runtime_loader_gap_survey.zig",
        "zigux/tests/runtime_loader_gap_manifest.json",
        "make -C zigux phase9-validate",
        "manifest-backed catalog and ownership map",
        "selftest-hook markers",
        "bounded lifecycle-parity posture",
    }
    if set(bad_missing) != expected_missing:
        print(
            "phase9_tests_readme_alignment_self_test_failed:"
            f"unexpected_negative_case={bad_missing}"
        )
        return 1

    print("PHASE9_TESTS_README_ALIGNMENT_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "readme",
        nargs="?",
        default=DEFAULT_TESTS_README,
        type=Path,
        help="Path to zigux/tests/README.md",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    return check_readme(args.readme)


if __name__ == "__main__":
    raise SystemExit(main())
