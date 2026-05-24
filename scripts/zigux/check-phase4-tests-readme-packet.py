#!/usr/bin/env python3
"""Guard the current narrow Phase 4 packet in zigux/tests/README.md."""

from __future__ import annotations

import argparse
import pathlib
import sys
import tempfile

TARGET_RELATIVE_PATH = pathlib.Path("zigux/tests/README.md")

REQUIRED_PRESENT_MARKERS = (
    "# zigux/tests",
    "This directory is the home of reusable Zigux parity and differential validation harnesses.",
    "## Phase 5 sample packet",
    "Keep the recovered broader note-and-checker companions explicit through `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts/zigux/check-phase4-gate-evidence.py`, and `scripts/zigux/check-phase4-remaining-gap-matrix.py`",
    "Current direct-readback dedicated local-only perf companion members: `zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`",
)

FORBIDDEN_PHASE4_MARKERS = (
    "## Phase 4",
    "Documentation/zigux/phase4-reversible-delivery-evidence.md",
    "scripts/zigux/check-phase4-repo-reality-warning.py",
    "scripts/zigux/check-phase4-reversible-delivery-pins.py",
    "make -C zigux phase4-perf-baseline-survey",
    "scripts/zigux/check-phase4-tests-readme-packet.py",
)

SELF_TEST_CASE_NAMES = (
    "baseline_round_trip",
    "missing_header",
    "missing_phase5_anchor",
    "stale_phase4_heading",
    "stale_phase4_note_reference",
    "stale_phase4_gate_evidence_note_reference",
    "stale_phase4_repo_reality_warning_reference",
    "stale_phase4_perf_manifest_reference",
    "stale_phase4_perf_reference",
    "stale_phase4_perf_make_route",
    "stale_phase4_gate_evidence_checker_reference",
    "stale_phase4_reversible_delivery_checker_reference",
    "stale_phase4_perf_checker_reference",
    "stale_phase4_bitmap_reference",
    "stale_phase4_tests_readme_checker_reference",
)

EXPECTED_SELF_TEST_CASES = 15


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Verify that zigux/tests/README.md carries the current narrow Phase 4 "
            "tests-root reminder packet without regressing into older wider packet claims."
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
    for marker in FORBIDDEN_PHASE4_MARKERS:
        if marker in text:
            issues.append(f"stale_phase4_marker_present={marker}")
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
    print(f"phase4_forbidden_marker_count={len(FORBIDDEN_PHASE4_MARKERS)}")
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
    if len(SELF_TEST_CASE_NAMES) != EXPECTED_SELF_TEST_CASES:
        print("PHASE4_TESTS_README_PACKET_SELF_TEST=fail")
        print(
            "expected_self_test_case_name_count="
            f"{EXPECTED_SELF_TEST_CASES}"
        )
        print(f"actual_self_test_case_name_count={len(SELF_TEST_CASE_NAMES)}")
        return 1
    cases = (
        ("baseline_round_trip", baseline, []),
        (
            "missing_header",
            baseline.replace(REQUIRED_PRESENT_MARKERS[0] + "\n", "", 1),
            [f"missing_required_marker={REQUIRED_PRESENT_MARKERS[0]}"],
        ),
        (
            "missing_phase5_anchor",
            baseline.replace(REQUIRED_PRESENT_MARKERS[2] + "\n", "", 1),
            [f"missing_required_marker={REQUIRED_PRESENT_MARKERS[2]}"],
        ),
        (
            "stale_phase4_heading",
            baseline + "## Phase 4\n",
            [f"stale_phase4_marker_present={FORBIDDEN_PHASE4_MARKERS[0]}"],
        ),
        (
            "stale_phase4_note_reference",
            baseline + FORBIDDEN_PHASE4_MARKERS[1] + "\n",
            [f"stale_phase4_marker_present={FORBIDDEN_PHASE4_MARKERS[1]}"],
        ),
        (
            "stale_phase4_gate_evidence_note_reference",
            baseline.replace(REQUIRED_PRESENT_MARKERS[3] + "\n", "", 1),
            [f"missing_required_marker={REQUIRED_PRESENT_MARKERS[3]}"],
        ),
        (
            "stale_phase4_repo_reality_warning_reference",
            baseline + FORBIDDEN_PHASE4_MARKERS[2] + "\n",
            [f"stale_phase4_marker_present={FORBIDDEN_PHASE4_MARKERS[2]}"],
        ),
        (
            "stale_phase4_perf_manifest_reference",
            baseline.replace(REQUIRED_PRESENT_MARKERS[4] + "\n", "", 1),
            [f"missing_required_marker={REQUIRED_PRESENT_MARKERS[4]}"],
        ),
        (
            "stale_phase4_perf_reference",
            baseline.replace(REQUIRED_PRESENT_MARKERS[4], "Current direct-readback local perf companion members"),
            [f"missing_required_marker={REQUIRED_PRESENT_MARKERS[4]}"],
        ),
        (
            "stale_phase4_perf_make_route",
            baseline + FORBIDDEN_PHASE4_MARKERS[4] + "\n",
            [f"stale_phase4_marker_present={FORBIDDEN_PHASE4_MARKERS[4]}"],
        ),
        (
            "stale_phase4_gate_evidence_checker_reference",
            baseline.replace("scripts/zigux/check-phase4-gate-evidence.py", "scripts/zigux/check-phase4-gate-evidence-legacy.py"),
            [f"missing_required_marker={REQUIRED_PRESENT_MARKERS[3]}"],
        ),
        (
            "stale_phase4_reversible_delivery_checker_reference",
            baseline + FORBIDDEN_PHASE4_MARKERS[3] + "\n",
            [f"stale_phase4_marker_present={FORBIDDEN_PHASE4_MARKERS[3]}"],
        ),
        (
            "stale_phase4_perf_checker_reference",
            baseline.replace("scripts/zigux/check-phase4-remaining-gap-matrix.py", "scripts/zigux/check-phase4-remaining-gap-matrix-legacy.py"),
            [f"missing_required_marker={REQUIRED_PRESENT_MARKERS[3]}"],
        ),
        (
            "stale_phase4_bitmap_reference",
            baseline.replace("zigux/tests/phase4_perf_baseline_survey.zig", "zigux/tests/phase4_bitmap_diff_survey.zig"),
            [f"missing_required_marker={REQUIRED_PRESENT_MARKERS[4]}"],
        ),
        (
            "stale_phase4_tests_readme_checker_reference",
            baseline + FORBIDDEN_PHASE4_MARKERS[5] + "\n",
            [f"stale_phase4_marker_present={FORBIDDEN_PHASE4_MARKERS[5]}"],
        ),
    )
    if len(cases) != EXPECTED_SELF_TEST_CASES:
        print("PHASE4_TESTS_README_PACKET_SELF_TEST=fail")
        print(f"expected_self_test_case_count={EXPECTED_SELF_TEST_CASES}")
        print(f"actual_self_test_case_count={len(cases)}")
        return 1

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
