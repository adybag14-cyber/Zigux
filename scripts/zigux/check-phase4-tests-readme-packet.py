#!/usr/bin/env python3
"""Fail closed on the current Phase 4 tests-root review packet."""

from __future__ import annotations

import argparse
import pathlib
import sys
import tempfile

TARGET_RELATIVE_PATH = pathlib.Path("zigux/tests/README.md")

REQUIRED_MARKERS = [
    "scripts/zigux/check-phase4-gate-evidence.py",
    "scripts/zigux/check-phase4-remaining-gap-matrix.py",
    "Documentation/zigux/phase4-reversible-delivery-evidence.md",
    "scripts/zigux/check-phase4-reversible-delivery-pins.py",
    "scripts/zigux/check-phase4-perf-baseline-packet.py",
    "zigux/tests/phase4_build.zig",
]

SELF_TEST_CASE_NAMES = [
    "baseline_round_trip",
    "missing_gate_evidence_checker",
    "missing_remaining_gap_matrix_checker",
    "missing_reversible_delivery_note",
    "missing_reversible_delivery_pin_checker",
    "missing_perf_baseline_checker",
    "missing_phase4_build_file",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Verify that zigux/tests/README.md keeps the current Phase 4 "
            "tests-root review packet explicit."
        )
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root containing zigux/tests/README.md (default: current directory).",
    )
    parser.add_argument(
        "--file",
        help="Override the tests-root README path for focused checks or self-tests.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the built-in self-test suite and exit.",
    )
    return parser.parse_args()


def target_path(args: argparse.Namespace) -> pathlib.Path:
    if args.file:
        return pathlib.Path(args.file)
    return pathlib.Path(args.repo_root) / TARGET_RELATIVE_PATH


def load_text(path: pathlib.Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"missing file: {path}") from exc


def missing_markers(text: str) -> list[str]:
    return [marker for marker in REQUIRED_MARKERS if marker not in text]


def run_check(args: argparse.Namespace) -> int:
    path = target_path(args)
    missing = missing_markers(load_text(path))
    if missing:
        print("PHASE4_TESTS_README_PACKET_CHECK=fail")
        for marker in missing:
            print(f"missing_marker={marker}")
        return 1
    print("PHASE4_TESTS_README_PACKET_CHECK=pass")
    print(f"checked_file={path}")
    return 0


def write_case(tmpdir: pathlib.Path, text: str) -> pathlib.Path:
    target = tmpdir / "zigux/tests/README.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    return target


def run_self_test() -> int:
    baseline = "\n".join(REQUIRED_MARKERS) + "\n"
    cases = [("baseline_round_trip", baseline, [])]
    for name, marker in zip(SELF_TEST_CASE_NAMES[1:], REQUIRED_MARKERS, strict=True):
        cases.append((name, baseline.replace(marker + "\n", "", 1), [marker]))

    with tempfile.TemporaryDirectory(prefix="phase4-tests-readme-packet-") as tmp:
        tmpdir = pathlib.Path(tmp)
        for name, text, expected_missing in cases:
            path = write_case(tmpdir, text)
            actual_missing = missing_markers(load_text(path))
            if actual_missing != expected_missing:
                print("PHASE4_TESTS_README_PACKET_SELF_TEST=fail")
                print(f"failed_case={name}")
                print(f"expected_missing={expected_missing}")
                print(f"actual_missing={actual_missing}")
                return 1

    print("PHASE4_TESTS_README_PACKET_SELF_TEST=pass")
    print(f"PHASE4_TESTS_README_PACKET_SELF_TEST_CASES={len(cases)}")
    print(
        "PHASE4_TESTS_README_PACKET_SELF_TEST_CASE_NAMES="
        + ",".join(SELF_TEST_CASE_NAMES)
    )
    return 0


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    return run_check(args)


if __name__ == "__main__":
    sys.exit(main())
