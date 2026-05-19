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
    "scripts/zigux/check-phase4-repo-reality-warning.py",
    "scripts/zigux/check-phase4-reversible-delivery-pins.py",
    "scripts/zigux/check-phase4-perf-baseline-packet.py",
    "zigux/tests/phase4_perf_baseline_manifest.json",
    "zigux/tests/phase4_perf_baseline_survey.zig",
    "zigux/tests/README.md",
]

RECOVERED_BROADER_PACKET = [
    "Documentation/zigux/phase4-gate-evidence.md",
    "Documentation/zigux/phase4-validation-matrix.md",
    "scripts/zigux/check-phase4-gate-evidence.py",
    "scripts/zigux/check-phase4-remaining-gap-matrix.py",
]

SPLIT_READBACK_COMPANIONS = [
    "scripts/zigux/validate-phase4.py",
    "zigux/tests/phase4_build.zig",
    "zigux/tests/bitmap_diff.zig",
    "zigux/tests/phase4_bitmap_live_helper_replay.zig",
    "zigux/tests/atomic64_diff.zig",
    "zigux/tests/runtime_atomic64_diff.zig",
]

REQUIRED_TEXT_MARKERS = [
    "Keep the current bounded Phase 4 reminder packet explicit through `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, `scripts/zigux/check-phase4-reversible-delivery-pins.py`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`, and `zigux/tests/README.md`.",
    "Keep the recovered broader note-and-checker companions explicit through `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts/zigux/check-phase4-gate-evidence.py`, and `scripts/zigux/check-phase4-remaining-gap-matrix.py`",
    "Current `master` keeps the shared Phase 4 rollback packet split rather than absent: `scripts/zigux/validate-phase4.py`, `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig` still do not materialize through authenticated contents reads in this runtime, while `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig` are directly readable roadmap-backed differential-gate evidence again.",
    "Current direct-readback dedicated local-only perf checker: `scripts/zigux/check-phase4-perf-baseline-packet.py`",
    "Current direct-readback dedicated local-only perf companion members: `zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`",
    "current shared Phase 4 ownership reminder: keep rollback-owner wording, artifact-diff contract references, and remaining-gap truthfulness aligned with `Documentation/zigux/phase4-reversible-delivery-evidence.md` instead of reconstructing the broader packet from older route names alone",
]

REQUIRED_MARKERS = (
    REQUIRED_TEXT_MARKERS
    + DIRECT_READBACK_PACKET
    + RECOVERED_BROADER_PACKET
    + SPLIT_READBACK_COMPANIONS
)

SELF_TEST_CASE_NAMES = [
    "baseline_round_trip",
    "missing_direct_readback_summary",
    "missing_recovered_packet_summary",
    "missing_split_readback_summary",
    "missing_local_perf_checker",
    "missing_local_perf_companions",
    "missing_owner_handoff",
    "missing_atomic64_current_head_evidence",
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
    print(f"phase4_recovered_broader_marker_count={len(RECOVERED_BROADER_PACKET)}")
    print(f"phase4_split_readback_marker_count={len(SPLIT_READBACK_COMPANIONS)}")
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
        REQUIRED_TEXT_MARKERS[2],
        REQUIRED_TEXT_MARKERS[3],
        REQUIRED_TEXT_MARKERS[4],
        REQUIRED_TEXT_MARKERS[5],
        "zigux/tests/atomic64_diff.zig",
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
