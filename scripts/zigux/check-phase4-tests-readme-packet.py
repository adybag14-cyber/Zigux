#!/usr/bin/env python3
"""Guard the current Phase 4 packet claims in zigux/tests/README.md."""

from __future__ import annotations

import argparse
import pathlib
import sys
import tempfile

TARGET_RELATIVE_PATH = pathlib.Path("zigux/tests/README.md")

REQUIRED_PRESENT_MARKERS = (
    "# zigux/tests",
    "This directory is the home of reusable Zigux parity and differential validation harnesses.",
    "## Phase 4 rollback-ownership and lab-matrix packet",
    "Documentation/zigux/phase4-reversible-delivery-evidence.md",
    "Documentation/zigux/phase4-gate-evidence.md",
    "scripts/zigux/check-phase4-repo-reality-warning.py",
    "scripts/zigux/check-phase4-tests-readme-packet.py",
    "scripts/zigux/check-phase4-reversible-delivery-pins.py",
    "scripts/zigux/check-phase4-perf-baseline-packet.py",
    "scripts/zigux/validate-phase4.py",
    "zigux/tests/phase4_perf_baseline_manifest.json",
    "zigux/tests/phase4_perf_baseline_survey.zig",
    "zigux/tests/phase4_build.zig",
    "zigux/tests/bitmap_diff.zig",
    "zigux/tests/phase4_bitmap_live_helper_replay.zig",
    "zigux/tests/atomic64_diff.zig",
    "zigux/tests/runtime_atomic64_diff.zig",
    "zigux/tests/phase4_runtime_atomic64_diff_manifest.json",
    "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
    "Documentation/zigux/phase4-kprobe-example-gap-survey.md",
    "Documentation/zigux/phase4-test-fsmount-gap-survey.md",
    "make -C zigux phase4-perf-baseline-survey",
    "Validation and Perf Team",
    "ABI and Runtime Team",
    "Shared Subsystems Pod",
)

SELF_TEST_CASE_NAMES = (
    "baseline_round_trip",
    "missing_header",
    "missing_intro",
    "missing_phase4_heading",
    "missing_phase4_note_reference",
    "missing_phase4_gate_evidence_reference",
    "missing_phase4_repo_reality_warning_reference",
    "missing_phase4_tests_readme_checker_reference",
    "missing_phase4_reversible_delivery_checker_reference",
    "missing_phase4_perf_checker_reference",
    "missing_phase4_validator_reference",
    "missing_phase4_perf_manifest_reference",
    "missing_phase4_perf_survey_reference",
    "missing_phase4_build_reference",
    "missing_phase4_bitmap_reference",
    "missing_phase4_bitmap_replay_reference",
    "missing_phase4_atomic64_reference",
    "missing_phase4_runtime_atomic64_reference",
    "missing_phase4_owner_split_reference",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Verify that zigux/tests/README.md carries the current shared "
            "Phase 4 rollback-ownership and lab-matrix reminder packet."
        )
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root containing zigux/tests/README.md (default: current directory).",
    )
    parser.add_argument(
        "--file",
        help="Override the README path for focused checks or self-tests.",
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


def collect_issues(text: str) -> list[str]:
    issues: list[str] = []
    for marker in REQUIRED_PRESENT_MARKERS:
        if marker not in text:
            issues.append(f"missing_required_marker={marker}")
    return issues


def run_check(args: argparse.Namespace) -> int:
    path = target_path(args)
    issues = collect_issues(load_text(path))
    if issues:
        print("PHASE4_TESTS_README_PACKET_CHECK=fail")
        for issue in issues:
            print(issue)
        return 1
    print("PHASE4_TESTS_README_PACKET_CHECK=pass")
    print(f"checked_file={path}")
    print(f"phase4_required_marker_count={len(REQUIRED_PRESENT_MARKERS)}")
    return 0


def write_case(tmpdir: pathlib.Path, text: str) -> pathlib.Path:
    target = tmpdir / TARGET_RELATIVE_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    return target


def baseline_text() -> str:
    return "\n".join(REQUIRED_PRESENT_MARKERS) + "\n"


def run_self_test() -> int:
    baseline = baseline_text()
    cases = (
        ("baseline_round_trip", baseline, []),
        (
            "missing_header",
            baseline.replace(REQUIRED_PRESENT_MARKERS[0] + "\n", "", 1),
            [f"missing_required_marker={REQUIRED_PRESENT_MARKERS[0]}"],
        ),
        (
            "missing_intro",
            baseline.replace(REQUIRED_PRESENT_MARKERS[1] + "\n", "", 1),
            [f"missing_required_marker={REQUIRED_PRESENT_MARKERS[1]}"],
        ),
        (
            "missing_phase4_heading",
            baseline.replace(REQUIRED_PRESENT_MARKERS[2] + "\n", "", 1),
            [f"missing_required_marker={REQUIRED_PRESENT_MARKERS[2]}"],
        ),
        (
            "missing_phase4_note_reference",
            baseline.replace(REQUIRED_PRESENT_MARKERS[3] + "\n", "", 1),
            [f"missing_required_marker={REQUIRED_PRESENT_MARKERS[3]}"],
        ),
        (
            "missing_phase4_gate_evidence_reference",
            baseline.replace(REQUIRED_PRESENT_MARKERS[4] + "\n", "", 1),
            [f"missing_required_marker={REQUIRED_PRESENT_MARKERS[4]}"],
        ),
        (
            "missing_phase4_repo_reality_warning_reference",
            baseline.replace(REQUIRED_PRESENT_MARKERS[5] + "\n", "", 1),
            [f"missing_required_marker={REQUIRED_PRESENT_MARKERS[5]}"],
        ),
        (
            "missing_phase4_tests_readme_checker_reference",
            baseline.replace(REQUIRED_PRESENT_MARKERS[6] + "\n", "", 1),
            [f"missing_required_marker={REQUIRED_PRESENT_MARKERS[6]}"],
        ),
        (
            "missing_phase4_reversible_delivery_checker_reference",
            baseline.replace(REQUIRED_PRESENT_MARKERS[7] + "\n", "", 1),
            [f"missing_required_marker={REQUIRED_PRESENT_MARKERS[7]}"],
        ),
        (
            "missing_phase4_perf_checker_reference",
            baseline.replace(REQUIRED_PRESENT_MARKERS[8] + "\n", "", 1),
            [f"missing_required_marker={REQUIRED_PRESENT_MARKERS[8]}"],
        ),
        (
            "missing_phase4_validator_reference",
            baseline.replace(REQUIRED_PRESENT_MARKERS[9] + "\n", "", 1),
            [f"missing_required_marker={REQUIRED_PRESENT_MARKERS[9]}"],
        ),
        (
            "missing_phase4_perf_manifest_reference",
            baseline.replace(REQUIRED_PRESENT_MARKERS[10] + "\n", "", 1),
            [f"missing_required_marker={REQUIRED_PRESENT_MARKERS[10]}"],
        ),
        (
            "missing_phase4_perf_survey_reference",
            baseline.replace(REQUIRED_PRESENT_MARKERS[11] + "\n", "", 1),
            [f"missing_required_marker={REQUIRED_PRESENT_MARKERS[11]}"],
        ),
        (
            "missing_phase4_build_reference",
            baseline.replace(REQUIRED_PRESENT_MARKERS[12] + "\n", "", 1),
            [f"missing_required_marker={REQUIRED_PRESENT_MARKERS[12]}"],
        ),
        (
            "missing_phase4_bitmap_reference",
            baseline.replace(REQUIRED_PRESENT_MARKERS[13] + "\n", "", 1),
            [f"missing_required_marker={REQUIRED_PRESENT_MARKERS[13]}"],
        ),
        (
            "missing_phase4_bitmap_replay_reference",
            baseline.replace(REQUIRED_PRESENT_MARKERS[14] + "\n", "", 1),
            [f"missing_required_marker={REQUIRED_PRESENT_MARKERS[14]}"],
        ),
        (
            "missing_phase4_atomic64_reference",
            baseline.replace(REQUIRED_PRESENT_MARKERS[15] + "\n", "", 1),
            [f"missing_required_marker={REQUIRED_PRESENT_MARKERS[15]}"],
        ),
        (
            "missing_phase4_runtime_atomic64_reference",
            baseline.replace(REQUIRED_PRESENT_MARKERS[16] + "\n", "", 1),
            [f"missing_required_marker={REQUIRED_PRESENT_MARKERS[16]}"],
        ),
        (
            "missing_phase4_owner_split_reference",
            baseline
            .replace(REQUIRED_PRESENT_MARKERS[22] + "\n", "", 1)
            .replace(REQUIRED_PRESENT_MARKERS[23] + "\n", "", 1)
            .replace(REQUIRED_PRESENT_MARKERS[24] + "\n", "", 1),
            [
                f"missing_required_marker={REQUIRED_PRESENT_MARKERS[22]}",
                f"missing_required_marker={REQUIRED_PRESENT_MARKERS[23]}",
                f"missing_required_marker={REQUIRED_PRESENT_MARKERS[24]}",
            ],
        ),
    )

    with tempfile.TemporaryDirectory(prefix="phase4-tests-readme-packet-") as tmp:
        tmpdir = pathlib.Path(tmp)
        for name, text, expected in cases:
            path = write_case(tmpdir, text)
            actual = collect_issues(load_text(path))
            if actual != expected:
                print("PHASE4_TESTS_README_PACKET_SELF_TEST=fail")
                print(f"failed_case={name}")
                print(f"expected={expected}")
                print(f"actual={actual}")
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