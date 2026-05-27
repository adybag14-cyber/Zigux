#!/usr/bin/env python3
"""Fail closed on the exact Phase 4 local-only perf-threshold matrix lines."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

MATRIX = Path("Documentation/zigux/phase4-validation-matrix.md")
NOTE = Path("Documentation/zigux/phase4-reversible-delivery-evidence.md")
LANE = Path("Documentation/zigux/phase4-validation-lane-sequencing.md")
MANIFEST = Path("zigux/tests/phase4_perf_baseline_manifest.json")
PHASE4_BUILD = Path("zigux/tests/phase4_build.zig")
EXPECTED_SELF_TEST_CASES = 23

SELF_TEST_MANIFEST = """{
  "atomic64": {
    "benchmark_command": "zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig",
    "acceptable_limit_metric": "median_elapsed_ns",
    "acceptable_limit_max_elapsed_ns": 8192,
    "acceptable_limit_iterations": 4,
    "acceptable_limit_sample_count": 7
  },
  "bitmap": {
    "benchmark_command": "zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig",
    "acceptable_limit_metric": "median_elapsed_ns",
    "acceptable_limit_max_elapsed_ns": 12288,
    "acceptable_limit_iterations": 4,
    "acceptable_limit_sample_count": 7
  }
}
"""

SELF_TEST_MATRIX = """# Phase 4 Validation Matrix

## Local-Only Perf Promotion
  * any future shared CI perf-promotion claim must name the Validation and Perf Team as the decision owner and rollback owner, and the ABI and Runtime Team plus Shared Subsystems Pod as coordination owners
  * promotion rollback owner: `Validation and Perf Team`
  * gate owners: `ABI and Runtime Team` and `Shared Subsystems Pod`
  * rollback owners: `ABI and Runtime Team` and `Shared Subsystems Pod`
  * `zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig` approved local-only acceptable limit: `median_elapsed_ns <= 8192` over `4` iterations with `7` monotonic samples
  * `zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig` approved local-only acceptable limit: `median_elapsed_ns <= 12288` over `4` iterations with `7` monotonic samples
"""

SELF_TEST_NOTE = """Current direct readback in this run confirmed this note, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, `scripts/zigux/check-phase4-tests-readme-packet.py`, `scripts/zigux/check-phase4-reversible-delivery-pins.py`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `scripts/zigux/check-phase4-perf-threshold-matrix.py`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` on current `master`.
Current direct-readback dedicated local-only perf checkers: `scripts/zigux/check-phase4-perf-baseline-packet.py` and `scripts/zigux/check-phase4-perf-threshold-matrix.py`.
"""

SELF_TEST_LANE = """- directly readable dedicated local-only perf packet that still stays adjacent to the shared handoff:
  - `scripts/zigux/check-phase4-perf-baseline-packet.py`
  - `scripts/zigux/check-phase4-perf-threshold-matrix.py`
  - `zigux/tests/phase4_perf_baseline_manifest.json`
  - `zigux/tests/phase4_perf_baseline_survey.zig`
- `scripts/zigux/check-phase4-perf-baseline-packet.py`, `scripts/zigux/check-phase4-perf-threshold-matrix.py`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` remain directly readable adjacent evidence inside the perf-only lane rather than historical companions.
Keep the Validation and Perf Team decision-owner and rollback-owner cue in the dedicated local-only perf packet, but leave the current cross-family coordination-owner split with the ABI and Runtime Team plus Shared Subsystems Pod in the shared exact-readback lane because that wording spans both landed rollback gates.
"""

SELF_TEST_BUILD = """const phase4_perf_baseline_survey = @import("phase4_perf_baseline_survey.zig");
const phase4_perf_baseline_survey_step = "phase4-perf-baseline-survey";
"""

NOTE_MARKERS = (
    "`scripts/zigux/check-phase4-perf-threshold-matrix.py`",
    "Current direct-readback dedicated local-only perf checkers: `scripts/zigux/check-phase4-perf-baseline-packet.py` and `scripts/zigux/check-phase4-perf-threshold-matrix.py`.",
)

LANE_MARKERS = (
    "  - `scripts/zigux/check-phase4-perf-threshold-matrix.py`",
    "`scripts/zigux/check-phase4-perf-baseline-packet.py`, `scripts/zigux/check-phase4-perf-threshold-matrix.py`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` remain directly readable adjacent evidence inside the perf-only lane rather than historical companions.",
    "Keep the Validation and Perf Team decision-owner and rollback-owner cue in the dedicated local-only perf packet, but leave the current cross-family coordination-owner split with the ABI and Runtime Team plus Shared Subsystems Pod in the shared exact-readback lane because that wording spans both landed rollback gates.",
)

MATRIX_OWNER_MARKERS = (
    "any future shared CI perf-promotion claim must name the Validation and Perf Team as the decision owner and rollback owner, and the ABI and Runtime Team plus Shared Subsystems Pod as coordination owners",
    "promotion rollback owner: `Validation and Perf Team`",
    "gate owners: `ABI and Runtime Team` and `Shared Subsystems Pod`",
    "rollback owners: `ABI and Runtime Team` and `Shared Subsystems Pod`",
)

PHASE4_BUILD_MARKERS = (
    "phase4_perf_baseline_survey.zig",
    "phase4-perf-baseline-survey",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", help="repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="run the built-in fixture self-test")
    return parser.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_atomic64_line(manifest: dict[str, object]) -> str:
    atomic64 = manifest["atomic64"]
    return (
        f"`{atomic64['benchmark_command']}` approved local-only acceptable limit: "
        f"`{atomic64['acceptable_limit_metric']} <= {atomic64['acceptable_limit_max_elapsed_ns']}` "
        f"over `{atomic64['acceptable_limit_iterations']}` iterations with "
        f"`{atomic64['acceptable_limit_sample_count']}` monotonic samples"
    )


def build_bitmap_line(manifest: dict[str, object]) -> str:
    bitmap = manifest["bitmap"]
    return (
        f"`{bitmap['benchmark_command']}` approved local-only acceptable limit: "
        f"`{bitmap['acceptable_limit_metric']} <= {bitmap['acceptable_limit_max_elapsed_ns']}` "
        f"over `{bitmap['acceptable_limit_iterations']}` iterations with "
        f"`{bitmap['acceptable_limit_sample_count']}` monotonic samples"
    )


def require_markers(text: str, markers: tuple[str, ...], label: str, issues: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            issues.append(f"{label}:{marker}")


def validate_root(root: Path) -> list[str]:
    issues: list[str] = []
    matrix_path = root / MATRIX
    note_path = root / NOTE
    lane_path = root / LANE
    manifest_path = root / MANIFEST
    phase4_build_path = root / PHASE4_BUILD
    if not matrix_path.is_file():
        issues.append(f"file:{MATRIX.as_posix()}")
    if not note_path.is_file():
        issues.append(f"file:{NOTE.as_posix()}")
    if not lane_path.is_file():
        issues.append(f"file:{LANE.as_posix()}")
    if not manifest_path.is_file():
        issues.append(f"file:{MANIFEST.as_posix()}")
    if not phase4_build_path.is_file():
        issues.append(f"file:{PHASE4_BUILD.as_posix()}")
    if issues:
        return issues

    try:
        manifest = json.loads(read_text(manifest_path))
    except json.JSONDecodeError as exc:
        return [f"manifest_json:decode:{exc.msg}"]

    matrix_text = read_text(matrix_path)
    atomic64_line = build_atomic64_line(manifest)
    bitmap_line = build_bitmap_line(manifest)
    if atomic64_line not in matrix_text:
        issues.append(f"matrix_line_missing:{atomic64_line}")
    if bitmap_line not in matrix_text:
        issues.append(f"matrix_line_missing:{bitmap_line}")

    require_markers(matrix_text, MATRIX_OWNER_MARKERS, "matrix_owner_marker", issues)
    require_markers(read_text(note_path), NOTE_MARKERS, "note_marker", issues)
    require_markers(read_text(lane_path), LANE_MARKERS, "lane_marker", issues)
    require_markers(read_text(phase4_build_path), PHASE4_BUILD_MARKERS, "phase4_build_marker", issues)
    return issues


def build_fixture_tree(root: Path) -> None:
    write_text(root / MANIFEST, SELF_TEST_MANIFEST)
    write_text(root / MATRIX, SELF_TEST_MATRIX)
    write_text(root / NOTE, SELF_TEST_NOTE)
    write_text(root / LANE, SELF_TEST_LANE)
    write_text(root / PHASE4_BUILD, SELF_TEST_BUILD)


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise ValueError(f"missing replacement target: {old!r}")
    return text.replace(old, new, 1)


def replace_after_anchor(text: str, anchor: str, old: str, new: str) -> str:
    anchor_index = text.find(anchor)
    if anchor_index == -1:
        raise ValueError(f"missing anchor: {anchor!r}")
    target_index = text.find(old, anchor_index)
    if target_index == -1:
        raise ValueError(f"missing replacement target after anchor {anchor!r}: {old!r}")
    return text[:target_index] + new + text[target_index + len(old) :]


def expect_failure(root: Path, expected_prefix: str) -> bool:
    return any(item.startswith(expected_prefix) for item in validate_root(root))


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase4-perf-threshold-matrix-") as tmp_dir:
        root = Path(tmp_dir)
        build_fixture_tree(root)
        if validate_root(root):
            print("PHASE4_PERF_THRESHOLD_MATRIX_SELF_TEST=fail")
            print("baseline fixture did not validate cleanly")
            return 1

        cases = 1
        variants = (
            (
                MATRIX,
                "`zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig` approved local-only acceptable limit: `median_elapsed_ns <= 8192` over `4` iterations with `7` monotonic samples",
                "`zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig` approved local-only acceptable limit: `median_elapsed_ns <= 9000` over `4` iterations with `7` monotonic samples",
                "matrix_line_missing:`zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig` approved local-only acceptable limit: `median_elapsed_ns <= 8192` over `4` iterations with `7` monotonic samples",
            ),
            (
                MATRIX,
                "`zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig` approved local-only acceptable limit: `median_elapsed_ns <= 12288` over `4` iterations with `7` monotonic samples",
                "`zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig` approved local-only acceptable limit: `median_elapsed_ns <= 13000` over `4` iterations with `7` monotonic samples",
                "matrix_line_missing:`zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig` approved local-only acceptable limit: `median_elapsed_ns <= 12288` over `4` iterations with `7` monotonic samples",
            ),
            (
                MANIFEST,
                "\"acceptable_limit_iterations\": 4",
                "\"acceptable_limit_iterations\": 5",
                "matrix_line_missing:`zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig` approved local-only acceptable limit:",
            ),
            (
                MANIFEST,
                "\"acceptable_limit_sample_count\": 7",
                "\"acceptable_limit_sample_count\": 8",
                "matrix_line_missing:`zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig` approved local-only acceptable limit:",
            ),
            (
                MANIFEST,
                "\"acceptable_limit_max_elapsed_ns\": 8192",
                "\"acceptable_limit_max_elapsed_ns\": 9000",
                "matrix_line_missing:`zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig` approved local-only acceptable limit:",
            ),
        )
        for rel, old, new, expected_prefix in variants:
            build_fixture_tree(root)
            target = root / rel
            write_text(target, replace_once(read_text(target), old, new))
            if not expect_failure(root, expected_prefix):
                print("PHASE4_PERF_THRESHOLD_MATRIX_SELF_TEST=fail")
                print(f"drift case did not fail closed: {expected_prefix}")
                return 1
            cases += 1

        bitmap_manifest_variants = (
            (
                "\"acceptable_limit_iterations\": 4",
                "\"acceptable_limit_iterations\": 5",
                "matrix_line_missing:`zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig` approved local-only acceptable limit:",
            ),
            (
                "\"acceptable_limit_sample_count\": 7",
                "\"acceptable_limit_sample_count\": 8",
                "matrix_line_missing:`zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig` approved local-only acceptable limit:",
            ),
            (
                "\"acceptable_limit_max_elapsed_ns\": 12288",
                "\"acceptable_limit_max_elapsed_ns\": 13000",
                "matrix_line_missing:`zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig` approved local-only acceptable limit:",
            ),
        )
        for old, new, expected_prefix in bitmap_manifest_variants:
            build_fixture_tree(root)
            target = root / MANIFEST
            write_text(
                target,
                replace_after_anchor(read_text(target), "\"bitmap\": {", old, new),
            )
            if not expect_failure(root, expected_prefix):
                print("PHASE4_PERF_THRESHOLD_MATRIX_SELF_TEST=fail")
                print(f"bitmap drift case did not fail closed: {expected_prefix}")
                return 1
            cases += 1

        matrix_owner_variants = (
            (
                "any future shared CI perf-promotion claim must name the Validation and Perf Team as the decision owner and rollback owner, and the ABI and Runtime Team plus Shared Subsystems Pod as coordination owners",
                "any future shared CI perf-promotion claim must name the Validation and Perf Team as the decision owner while shared ownership details are handled elsewhere",
                "matrix_owner_marker:any future shared CI perf-promotion claim must name the Validation and Perf Team as the decision owner and rollback owner, and the ABI and Runtime Team plus Shared Subsystems Pod as coordination owners",
            ),
            (
                "promotion rollback owner: `Validation and Perf Team`",
                "promotion owner: `Validation and Perf Team`",
                "matrix_owner_marker:promotion rollback owner: `Validation and Perf Team`",
            ),
            (
                "gate owners: `ABI and Runtime Team` and `Shared Subsystems Pod`",
                "gate owner: `ABI and Runtime Team`",
                "matrix_owner_marker:gate owners: `ABI and Runtime Team` and `Shared Subsystems Pod`",
            ),
            (
                "rollback owners: `ABI and Runtime Team` and `Shared Subsystems Pod`",
                "rollback owner: `ABI and Runtime Team`",
                "matrix_owner_marker:rollback owners: `ABI and Runtime Team` and `Shared Subsystems Pod`",
            ),
        )
        for old, new, expected_prefix in matrix_owner_variants:
            build_fixture_tree(root)
            target = root / MATRIX
            write_text(target, replace_once(read_text(target), old, new))
            if not expect_failure(root, expected_prefix):
                print("PHASE4_PERF_THRESHOLD_MATRIX_SELF_TEST=fail")
                print(f"matrix owner drift case did not fail closed: {expected_prefix}")
                return 1
            cases += 1

        build_fixture_tree(root)
        write_text(
            root / NOTE,
            replace_once(
                read_text(root / NOTE),
                "Current direct-readback dedicated local-only perf checkers: `scripts/zigux/check-phase4-perf-baseline-packet.py` and `scripts/zigux/check-phase4-perf-threshold-matrix.py`.",
                "Current direct-readback dedicated local-only perf checkers: `scripts/zigux/check-phase4-perf-baseline-packet.py`.",
            ),
        )
        if not expect_failure(root, "note_marker:Current direct-readback dedicated local-only perf checkers:"):
            print("PHASE4_PERF_THRESHOLD_MATRIX_SELF_TEST=fail")
            print("note checker drift case did not fail closed")
            return 1
        cases += 1

        build_fixture_tree(root)
        write_text(
            root / LANE,
            replace_once(
                read_text(root / LANE),
                "  - `scripts/zigux/check-phase4-perf-threshold-matrix.py`\n",
                "",
            ),
        )
        if not expect_failure(root, "lane_marker:  - `scripts/zigux/check-phase4-perf-threshold-matrix.py`"):
            print("PHASE4_PERF_THRESHOLD_MATRIX_SELF_TEST=fail")
            print("lane checker drift case did not fail closed")
            return 1
        cases += 1

        build_fixture_tree(root)
        write_text(
            root / LANE,
            replace_once(
                read_text(root / LANE),
                "Keep the Validation and Perf Team decision-owner and rollback-owner cue in the dedicated local-only perf packet, but leave the current cross-family coordination-owner split with the ABI and Runtime Team plus Shared Subsystems Pod in the shared exact-readback lane because that wording spans both landed rollback gates.\n",
                "Keep the Validation and Perf Team decision-owner cue in the dedicated local-only perf packet, but leave the current cross-family coordination-owner split with the ABI and Runtime Team plus Shared Subsystems Pod in the shared exact-readback lane because that wording spans both landed rollback gates.\n",
            ),
        )
        if not expect_failure(root, "lane_marker:Keep the Validation and Perf Team decision-owner and rollback-owner cue in the dedicated local-only perf packet"):
            print("PHASE4_PERF_THRESHOLD_MATRIX_SELF_TEST=fail")
            print("lane rollback-owner cue drift case did not fail closed")
            return 1
        cases += 1

        build_fixture_tree(root)
        write_text(
            root / PHASE4_BUILD,
            replace_once(
                read_text(root / PHASE4_BUILD),
                "phase4_perf_baseline_survey.zig",
                "phase4_perf_baseline_packet.zig",
            ),
        )
        if not expect_failure(root, "phase4_build_marker:phase4_perf_baseline_survey.zig"):
            print("PHASE4_PERF_THRESHOLD_MATRIX_SELF_TEST=fail")
            print("phase4 build file drift case did not fail closed for survey source marker")
            return 1
        cases += 1

        build_fixture_tree(root)
        write_text(
            root / PHASE4_BUILD,
            replace_once(
                read_text(root / PHASE4_BUILD),
                "phase4-perf-baseline-survey",
                "phase4-local-baseline-survey",
            ),
        )
        if not expect_failure(root, "phase4_build_marker:phase4-perf-baseline-survey"):
            print("PHASE4_PERF_THRESHOLD_MATRIX_SELF_TEST=fail")
            print("phase4 build file drift case did not fail closed for build route marker")
            return 1
        cases += 1

        build_fixture_tree(root)
        (root / LANE).unlink()
        if not expect_failure(root, f"file:{LANE.as_posix()}"):
            print("PHASE4_PERF_THRESHOLD_MATRIX_SELF_TEST=fail")
            print("missing lane file case did not fail closed")
            return 1
        cases += 1

        build_fixture_tree(root)
        (root / NOTE).unlink()
        if not expect_failure(root, f"file:{NOTE.as_posix()}"):
            print("PHASE4_PERF_THRESHOLD_MATRIX_SELF_TEST=fail")
            print("missing note file case did not fail closed")
            return 1
        cases += 1

        build_fixture_tree(root)
        (root / MANIFEST).unlink()
        if not expect_failure(root, f"file:{MANIFEST.as_posix()}"):
            print("PHASE4_PERF_THRESHOLD_MATRIX_SELF_TEST=fail")
            print("missing manifest file case did not fail closed")
            return 1
        cases += 1

        build_fixture_tree(root)
        write_text(root / MANIFEST, "{")
        if not expect_failure(root, "manifest_json:decode:"):
            print("PHASE4_PERF_THRESHOLD_MATRIX_SELF_TEST=fail")
            print("broken manifest JSON case did not fail closed")
            return 1
        cases += 1

        build_fixture_tree(root)
        (root / PHASE4_BUILD).unlink()
        if not expect_failure(root, f"file:{PHASE4_BUILD.as_posix()}"):
            print("PHASE4_PERF_THRESHOLD_MATRIX_SELF_TEST=fail")
            print("missing phase4 build file case did not fail closed")
            return 1
        cases += 1

        if cases != EXPECTED_SELF_TEST_CASES:
            print("PHASE4_PERF_THRESHOLD_MATRIX_SELF_TEST=fail")
            print(f"expected {EXPECTED_SELF_TEST_CASES} self-test cases, saw {cases}")
            return 1

    print("PHASE4_PERF_THRESHOLD_MATRIX_SELF_TEST=pass")
    print(f"PHASE4_PERF_THRESHOLD_MATRIX_SELF_TEST_CASES={EXPECTED_SELF_TEST_CASES}")
    return 0


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    issues = validate_root(Path(args.root).resolve())
    if issues:
        print("PHASE4_PERF_THRESHOLD_MATRIX=fail")
        for issue in issues:
            print(issue)
        return 1
    print("PHASE4_PERF_THRESHOLD_MATRIX=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
