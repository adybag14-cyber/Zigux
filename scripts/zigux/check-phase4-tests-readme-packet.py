#!/usr/bin/env python3
"""Fail closed on the current Phase 4 tests-root repo-reality packet."""

from __future__ import annotations

import argparse
import pathlib
import sys
import tempfile

TARGET_RELATIVE_PATH = pathlib.Path("zigux/tests/README.md")

DIRECT_READBACK_PACKET = [
    "Documentation/zigux/phase4-reversible-delivery-evidence.md",
    "Documentation/zigux/review-checklist.md",
    "zigux/tests/README.md",
    "scripts/zigux/check-phase4-repo-reality-warning.py",
    "scripts/zigux/check-phase4-reversible-delivery-pins.py",
]

MISSING_BROADER_PACKET = [
    "Documentation/zigux/phase4-gate-evidence.md",
    "Documentation/zigux/phase4-validation-matrix.md",
    "scripts/zigux/check-phase4-gate-evidence.py",
    "scripts/zigux/check-phase4-perf-baseline-packet.py",
    "scripts/zigux/validate-phase4.py",
    "zigux/tests/phase4_build.zig",
    "zigux/tests/phase4_perf_baseline_manifest.json",
    "zigux/tests/phase4_perf_baseline_survey.zig",
]

REQUIRED_TEXT_MARKERS = [
    "roadmap-backed Phase 4 differential-gate destinations still missing on current `master`",
    "current direct-readback Phase 4 rollback packet",
    "repo-reality warning for the broader Phase 4 validator, lab-matrix, and local-only perf packet",
    "historical provenance for that missing broader packet",
    "current shared Phase 4 ownership reminder: keep rollback-owner wording, artifact-diff contract references, and remaining-gap truthfulness aligned with `Documentation/zigux/phase4-reversible-delivery-evidence.md` instead of reconstructing the broader packet from older route names alone",
    "historical Phase 4 route names such as the parked kprobe and `test_fsmount` survey companions, the validator-first routes, and the direct local-only perf routes stay owned by the reversible-delivery handoff note until the dedicated exact-pin refresh or a broader republish makes those companion blob values directly readable again",
]

REQUIRED_MARKERS = (
    REQUIRED_TEXT_MARKERS
    + DIRECT_READBACK_PACKET
    + MISSING_BROADER_PACKET
    + [
        "zigux/tests/atomic64_diff.zig",
        "zigux/tests/runtime_atomic64_diff.zig",
    ]
)

SELF_TEST_CASE_NAMES = [
    "baseline_round_trip",
    "missing_atomic64_gap_summary",
    "missing_direct_readback_summary",
    "missing_repo_reality_warning_checker",
    "missing_validate_phase4_gap",
    "missing_phase4_build_gap",
    "missing_broader_gap_summary",
    "missing_owner_handoff",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Verify that zigux/tests/README.md keeps the current Phase 4 "
            "repo-reality packet explicit."
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
    print(f"phase4_direct_readback_marker_count={len(DIRECT_READBACK_PACKET)}")
    print(f"phase4_missing_broader_marker_count={len(MISSING_BROADER_PACKET)}")
    return 0


def write_case(tmpdir: pathlib.Path, text: str) -> pathlib.Path:
    target = tmpdir / TARGET_RELATIVE_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    return target


def run_self_test() -> int:
    baseline = "\n".join(REQUIRED_MARKERS) + "\n"
    case_markers = [
        REQUIRED_TEXT_MARKERS[0],
        REQUIRED_TEXT_MARKERS[1],
        DIRECT_READBACK_PACKET[3],
        MISSING_BROADER_PACKET[4],
        MISSING_BROADER_PACKET[5],
        REQUIRED_TEXT_MARKERS[2],
        REQUIRED_TEXT_MARKERS[4],
    ]
    cases = [("baseline_round_trip", baseline, [])]
    for name, marker in zip(SELF_TEST_CASE_NAMES[1:], case_markers, strict=True):
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
