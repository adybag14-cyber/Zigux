#!/usr/bin/env python3
"""Guard the bounded Phase 4 local-only perf packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

MANIFEST = Path("zigux/tests/phase4_perf_baseline_manifest.json")
SURVEY = Path("zigux/tests/phase4_perf_baseline_survey.zig")

EXPECTED_COORDINATION_OWNERS = [
    "ABI and Runtime Team",
    "Shared Subsystems Pod",
]
EXPECTED_LOCAL_ONLY_POSTURE_NOTE = (
    "The dedicated perf-baseline survey keeps approved local benchmark commands and "
    "approved local-only acceptable limits explicit while shared CI perf promotion "
    "remains intentionally pending."
)
EXPECTED_SELF_TEST_CASES = 27

MANIFEST_MARKERS = (
    '"lane_key": "P4-L20"',
    '"phase": "Phase 4"',
    '"owner": "Validation and Perf Team"',
    '"rollback_owner": "Validation and Perf Team"',
    '"decision_owner": "Validation and Perf Team"',
    '"coordination_owners": [',
    '"ABI and Runtime Team"',
    '"Shared Subsystems Pod"',
    '"shared_ci_perf_promotion_status": "pending"',
    '"local_only_posture_note": "The dedicated perf-baseline survey keeps approved local benchmark commands and approved local-only acceptable limits explicit while shared CI perf promotion remains intentionally pending."',
    '"benchmark_command": "zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig"',
    '"benchmark_command": "zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig"',
    '"linux_style_wrapper": "make -C zigux phase4-perf-baseline-survey"',
    '"acceptable_limit_status": "approved_local_only"',
    '"acceptable_limit_metric": "median_elapsed_ns"',
    '"acceptable_limit_iterations": 4',
    '"acceptable_limit_sample_count": 7',
    '"acceptable_limit_max_elapsed_ns": 8192',
    '"acceptable_limit_max_elapsed_ns": 12288',
    '"sample_count_note": "seven monotonic samples"',
    '"id": "phase4-perf-baseline-atomic64-command-evidence"',
    '"checksum": 3626254113632800175',
    '"checksum": 9210681150676220922',
    '"id": "phase4-perf-baseline-bitmap-command-evidence"',
    '"checksum": 5216946504564592253',
    '"checksum": 7942141539243507472',
    '"status": "shared CI perf promotion pending"',
)

SURVEY_MARKERS = (
    'test "phase4 perf baseline survey keeps exact local-only iteration and sample counts explicit" {',
    'try requireMarkerCount("\\\\\\"acceptable_limit_iterations\\\\\\": 4", 2);',
    'try requireMarkerCount("\\\\\\"acceptable_limit_sample_count\\\\\\": 7", 2);',
    'try requireMarkerCount("\\\\\\"sample_count_note\\\\\\": \\\\\"seven monotonic samples\\\\\"\\", 2);',
    'test "phase4 perf baseline survey keeps atomic64 and bitmap command evidence explicit" {',
    'try requireMarker("\\\\\\"owner\\\\\\": \\\\\"Validation and Perf Team\\\\\"");',
    'try requireMarker("\\\\\\"benchmark_command\\\\\\": \\\\\"zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig\\\\\"");',
    'try requireMarker("\\\\\\"benchmark_command\\\\\\": \\\\\"zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig\\\\\"");',
    'try requireMarker("\\\\\\"linux_style_wrapper\\\\\\": \\\\\"make -C zigux phase4-perf-baseline-survey\\\\\"");',
    'try requireMarker("\\\\\\"checksum\\\\\\": 3626254113632800175");',
    'try requireMarker("\\\\\\"checksum\\\\\\": 9210681150676220922");',
    'try requireMarker("\\\\\\"final_counter\\\\\\": 130322557735600377");',
    'try requireMarker("\\\\\\"final_counter\\\\\\": 130322557735600376");',
    'try requireMarker("\\\\\\"checksum\\\\\\": 5216946504564592253");',
    'try requireMarker("\\\\\\"checksum\\\\\\": 7942141539243507472");',
    'try requireMarker("\\\\\\"final_first_zero\\\\\\": 109");',
    'test "phase4 perf baseline survey keeps rollback and decision ownership explicit" {',
    'try requireMarker("\\\\\\"rollback_owner\\\\\\": \\\\\"Validation and Perf Team\\\\\"");',
    'try requireMarker("\\\\\\"decision_owner\\\\\\": \\\\\"Validation and Perf Team\\\\\"");',
    'try requireMarker("\\\\\\"local_only_posture_note\\\\\\": \\\\\"The dedicated perf-baseline survey keeps approved local benchmark commands and approved local-only acceptable limits explicit while shared CI perf promotion remains intentionally pending.\\\\\"");',
    'test "phase4 perf baseline survey keeps the dedicated packet contract reviewable" {',
    'try requireMarker("\\\\\\"id\\\\\\": \\\\\"phase4-perf-baseline-shared-promotion-decision\\\\\"");',
    'try requireMarker("\\\\\\"status\\\\\\": \\\\\"shared CI perf promotion pending\\\\\"");',
    'try requireMarker("\\\\\\"coordination_owners\\\\\\": [");',
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


def require_markers(text: str, markers: tuple[str, ...], label: str, missing: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            missing.append(f"{label}:{marker}")


def read_json(path: Path, missing: list[str]) -> dict[str, object] | None:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        missing.append(f"manifest_json:decode:{exc.msg}")
        return None


def expect_json_value(payload: object, path: tuple[str | int, ...], expected: object, missing: list[str]) -> None:
    current = payload
    for step in path:
        try:
            current = current[step]  # type: ignore[index]
        except (KeyError, IndexError, TypeError):
            path_label = ".".join(str(part) for part in path)
            missing.append(f"manifest_json:{path_label}:missing")
            return
    if current != expected:
        path_label = ".".join(str(part) for part in path)
        missing.append(f"manifest_json:{path_label}:expected={expected!r}:actual={current!r}")


def validate_manifest_json(manifest_data: dict[str, object], missing: list[str]) -> None:
    expected_values: tuple[tuple[tuple[str | int, ...], object], ...] = (
        (("lane_key",), "P4-L20"),
        (("phase",), "Phase 4"),
        (("owner",), "Validation and Perf Team"),
        (("rollback_owner",), "Validation and Perf Team"),
        (("decision_owner",), "Validation and Perf Team"),
        (("coordination_owners",), EXPECTED_COORDINATION_OWNERS),
        (("shared_ci_perf_promotion_status",), "pending"),
        (("local_only_posture_note",), EXPECTED_LOCAL_ONLY_POSTURE_NOTE),
        (("atomic64", "benchmark_command"), "zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig"),
        (("atomic64", "linux_style_wrapper"), "make -C zigux phase4-perf-baseline-survey"),
        (("atomic64", "acceptable_limit_status"), "approved_local_only"),
        (("atomic64", "acceptable_limit_metric"), "median_elapsed_ns"),
        (("atomic64", "acceptable_limit_iterations"), 4),
        (("atomic64", "acceptable_limit_sample_count"), 7),
        (("atomic64", "acceptable_limit_max_elapsed_ns"), 8192),
        (("atomic64", "evidence", 0, "id"), "phase4-perf-baseline-atomic64-acceptable-limit"),
        (("atomic64", "evidence", 0, "kind"), "acceptable_limit"),
        (("atomic64", "evidence", 0, "metric"), "median_elapsed_ns"),
        (("atomic64", "evidence", 0, "status"), "approved_local_only"),
        (("atomic64", "evidence", 0, "sample_count_note"), "seven monotonic samples"),
        (("atomic64", "evidence", 0, "max_elapsed_ns"), 8192),
        (("atomic64", "evidence", 1, "id"), "phase4-perf-baseline-atomic64-command-evidence"),
        (("atomic64", "evidence", 1, "kind"), "threshold_replay"),
        (("atomic64", "evidence", 1, "runs", 0, "iterations"), 1),
        (("atomic64", "evidence", 1, "runs", 0, "checksum"), 3626254113632800175),
        (("atomic64", "evidence", 1, "runs", 0, "final_counter"), 130322557735600377),
        (("atomic64", "evidence", 1, "runs", 1, "iterations"), 4),
        (("atomic64", "evidence", 1, "runs", 1, "checksum"), 9210681150676220922),
        (("atomic64", "evidence", 1, "runs", 1, "final_counter"), 130322557735600376),
        (("bitmap", "benchmark_command"), "zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig"),
        (("bitmap", "linux_style_wrapper"), "make -C zigux phase4-perf-baseline-survey"),
        (("bitmap", "acceptable_limit_status"), "approved_local_only"),
        (("bitmap", "acceptable_limit_metric"), "median_elapsed_ns"),
        (("bitmap", "acceptable_limit_iterations"), 4),
        (("bitmap", "acceptable_limit_sample_count"), 7),
        (("bitmap", "acceptable_limit_max_elapsed_ns"), 12288),
        (("bitmap", "evidence", 0, "id"), "phase4-perf-baseline-bitmap-acceptable-limit"),
        (("bitmap", "evidence", 0, "kind"), "acceptable_limit"),
        (("bitmap", "evidence", 0, "metric"), "median_elapsed_ns"),
        (("bitmap", "evidence", 0, "status"), "approved_local_only"),
        (("bitmap", "evidence", 0, "sample_count_note"), "seven monotonic samples"),
        (("bitmap", "evidence", 0, "max_elapsed_ns"), 12288),
        (("bitmap", "evidence", 1, "id"), "phase4-perf-baseline-bitmap-command-evidence"),
        (("bitmap", "evidence", 1, "kind"), "threshold_replay"),
        (("bitmap", "evidence", 1, "runs", 0, "iterations"), 1),
        (("bitmap", "evidence", 1, "runs", 0, "checksum"), 5216946504564592253),
        (("bitmap", "evidence", 1, "runs", 0, "final_first_zero"), 109),
        (("bitmap", "evidence", 1, "runs", 1, "iterations"), 4),
        (("bitmap", "evidence", 1, "runs", 1, "checksum"), 7942141539243507472),
        (("bitmap", "evidence", 1, "runs", 1, "final_first_zero"), 109),
        (("promotion_decision", "id"), "phase4-perf-baseline-shared-promotion-decision"),
        (("promotion_decision", "status"), "shared CI perf promotion pending"),
        (("promotion_decision", "owner"), "Validation and Perf Team"),
        (("promotion_decision", "coordination_owners"), EXPECTED_COORDINATION_OWNERS),
    )
    for path, expected in expected_values:
        expect_json_value(manifest_data, path, expected, missing)


def validate_root(root: Path) -> list[str]:
    missing: list[str] = []

    manifest = root / MANIFEST
    if not manifest.is_file():
        missing.append(f"file:{MANIFEST.as_posix()}")
    else:
        manifest_text = read_text(manifest)
        require_markers(manifest_text, MANIFEST_MARKERS, "manifest_marker", missing)
        manifest_data = read_json(manifest, missing)
        if manifest_data is not None:
            validate_manifest_json(manifest_data, missing)
        if manifest_text.count('"acceptable_limit_iterations": 4') != 2:
            missing.append('manifest_count:"acceptable_limit_iterations": 4:expected=2')
        if manifest_text.count('"acceptable_limit_sample_count": 7') != 2:
            missing.append('manifest_count:"acceptable_limit_sample_count": 7:expected=2')
        if manifest_text.count('"sample_count_note": "seven monotonic samples"') != 2:
            missing.append('manifest_count:"sample_count_note": "seven monotonic samples":expected=2')
        if manifest_text.count('"final_first_zero": 109') != 2:
            missing.append('manifest_count:"final_first_zero": 109:expected=2')

    survey = root / SURVEY
    if not survey.is_file():
        missing.append(f"file:{SURVEY.as_posix()}")
    else:
        require_markers(read_text(survey), SURVEY_MARKERS, "survey_marker", missing)

    return missing


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise ValueError(f"missing replacement target: {old!r}")
    return text.replace(old, new, 1)


def build_fixture_tree(root: Path) -> None:
    source_root = Path(__file__).resolve().parents[2]
    write_text(root / MANIFEST, read_text(source_root / MANIFEST))
    write_text(root / SURVEY, read_text(source_root / SURVEY))


def expect_failure(root: Path, expected_prefix: str) -> bool:
    return any(item.startswith(expected_prefix) for item in validate_root(root))


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase4-perf-baseline-packet-") as tmp_dir:
        root = Path(tmp_dir)
        build_fixture_tree(root)
        if validate_root(root):
            print("PHASE4_PERF_BASELINE_PACKET_SELF_TEST=fail")
            print("baseline fixture did not validate cleanly")
            return 1
        cases = 1

        manifest = root / MANIFEST
        survey = root / SURVEY

        variants = (
            ('"acceptable_limit_iterations": 4', '"acceptable_limit_iterations": 5', 'manifest_count:"acceptable_limit_iterations": 4'),
            ('"benchmark_command": "zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig"', '"benchmark_command": "zig build phase4-runtime-atomic64-bench --build-file zigux/tests/phase4_build.zig"', 'manifest_marker:"benchmark_command": "zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig"'),
            ('"acceptable_limit_max_elapsed_ns": 8192', '"acceptable_limit_max_elapsed_ns": 9216', 'manifest_marker:"acceptable_limit_max_elapsed_ns": 8192'),
            ('"final_counter": 130322557735600377', '"final_counter": 130322557735600378', "manifest_json:atomic64.evidence.1.runs.0.final_counter:"),
            ('"benchmark_command": "zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig"', '"benchmark_command": "zig build phase4-bitmap-diff-other --build-file zigux/tests/phase4_build.zig"', 'manifest_marker:"benchmark_command": "zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig"'),
            ('"acceptable_limit_max_elapsed_ns": 12288', '"acceptable_limit_max_elapsed_ns": 16384', 'manifest_marker:"acceptable_limit_max_elapsed_ns": 12288'),
            ('"final_first_zero": 109', '"final_first_zero": 110', 'manifest_count:"final_first_zero": 109:expected=2'),
            ('"sample_count_note": "seven monotonic samples"', '"sample_count_note": "eight monotonic samples"', 'manifest_count:"sample_count_note": "seven monotonic samples":expected=2'),
            ('"owner": "Validation and Perf Team"', '"owner": "ABI and Runtime Team"', "manifest_json:owner:"),
            ('"decision_owner": "Validation and Perf Team"', '"decision_owner": "ABI and Runtime Team"', 'manifest_marker:"decision_owner": "Validation and Perf Team"'),
            ('"rollback_owner": "Validation and Perf Team"', '"rollback_owner": "ABI and Runtime Team"', 'manifest_marker:"rollback_owner": "Validation and Perf Team"'),
            (
                '"coordination_owners": [\n'
                '    "ABI and Runtime Team",\n'
                '    "Shared Subsystems Pod"\n'
                '  ]',
                '"coordination_owners": [\n'
                '    "ABI and Replay Team",\n'
                '    "Shared Subsystems Pod"\n'
                '  ]',
                "manifest_json:coordination_owners:",
            ),
            ('"local_only_posture_note": "The dedicated perf-baseline survey keeps approved local benchmark commands and approved local-only acceptable limits explicit while shared CI perf promotion remains intentionally pending."', '"local_only_posture_note": "The dedicated perf-baseline survey still needs shared CI approval."', "manifest_json:local_only_posture_note:"),
            ('"acceptable_limit_status": "approved_local_only"', '"acceptable_limit_status": "pending_review"', "manifest_json:atomic64.acceptable_limit_status:"),
            ('"acceptable_limit_metric": "median_elapsed_ns"', '"acceptable_limit_metric": "mean_elapsed_ns"', "manifest_json:atomic64.acceptable_limit_metric:"),
            ('"shared_ci_perf_promotion_status": "pending"', '"shared_ci_perf_promotion_status": "approved"', 'manifest_marker:"shared_ci_perf_promotion_status": "pending"'),
            ('"status": "shared CI perf promotion pending"', '"status": "shared CI perf promotion approved"', 'manifest_marker:"status": "shared CI perf promotion pending"'),
        )
        for old, new, expected_prefix in variants:
            build_fixture_tree(root)
            write_text(manifest, replace_once(read_text(manifest), old, new))
            if not expect_failure(root, expected_prefix):
                print("PHASE4_PERF_BASELINE_PACKET_SELF_TEST=fail")
                print(f"manifest drift case did not fail closed: {expected_prefix}")
                return 1
            cases += 1

        survey_variants = (
            ('try requireMarkerCount("\\\\\\"acceptable_limit_sample_count\\\\\\": 7", 2);', 'try requireMarkerCount("\\\\\\"acceptable_limit_sample_count\\\\\\": 8", 2);', 'survey_marker:try requireMarkerCount("\\\\\\"acceptable_limit_sample_count\\\\\\": 7", 2);'),
            ('try requireMarkerCount("\\\\\\"sample_count_note\\\\\\": \\\\\"seven monotonic samples\\\\\"\\", 2);', 'try requireMarkerCount("\\\\\\"sample_count_note\\\\\\": \\\\\"eight monotonic samples\\\\\"\\", 2);', 'survey_marker:try requireMarkerCount("\\\\\\"sample_count_note\\\\\\": \\\\\"seven monotonic samples\\\\\"\\", 2);'),
            ('try requireMarker("\\\\\\"benchmark_command\\\\\\": \\\\\"zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig\\\\\"");', 'try requireMarker("\\\\\\"benchmark_command\\\\\\": \\\\\"zig build phase4-runtime-atomic64-bench --build-file zigux/tests/phase4_build.zig\\\\\"");', 'survey_marker:try requireMarker("\\\\\\"benchmark_command\\\\\\": \\\\\"zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig\\\\\"");'),
            ('try requireMarker("\\\\\\"final_counter\\\\\\": 130322557735600376");', 'try requireMarker("\\\\\\"final_counter\\\\\\": 130322557735600379");', 'survey_marker:try requireMarker("\\\\\\"final_counter\\\\\\": 130322557735600376");'),
            ('try requireMarker("\\\\\\"owner\\\\\\": \\\\\"Validation and Perf Team\\\\\"");', 'try requireMarker("\\\\\\"owner\\\\\\": \\\\\"ABI and Runtime Team\\\\\"");', 'survey_marker:try requireMarker("\\\\\\"owner\\\\\\": \\\\\"Validation and Perf Team\\\\\"");'),
            ('try requireMarker("\\\\\\"linux_style_wrapper\\\\\\": \\\\\"make -C zigux phase4-perf-baseline-survey\\\\\"");', 'try requireMarker("\\\\\\"linux_style_wrapper\\\\\\": \\\\\"make -C zigux phase4-perf-baseline\\\\\"");', 'survey_marker:try requireMarker("\\\\\\"linux_style_wrapper\\\\\\": \\\\\"make -C zigux phase4-perf-baseline-survey\\\\\"");'),
            ('try requireMarker("\\\\\\"local_only_posture_note\\\\\\": \\\\\"The dedicated perf-baseline survey keeps approved local benchmark commands and approved local-only acceptable limits explicit while shared CI perf promotion remains intentionally pending.\\\\\"");', 'try requireMarker("\\\\\\"local_only_posture_note\\\\\\": \\\\\"The dedicated perf-baseline survey still needs shared CI approval.\\\\\"");', 'survey_marker:try requireMarker("\\\\\\"local_only_posture_note\\\\\\": \\\\\"The dedicated perf-baseline survey keeps approved local benchmark commands and approved local-only acceptable limits explicit while shared CI perf promotion remains intentionally pending.\\\\\"");'),
            ('try requireMarker("\\\\\\"id\\\\\\": \\\\\"phase4-perf-baseline-shared-promotion-decision\\\\\"");', 'try requireMarker("\\\\\\"id\\\\\\": \\\\\"phase4-perf-baseline-other-decision\\\\\"");', 'survey_marker:try requireMarker("\\\\\\"id\\\\\\": \\\\\"phase4-perf-baseline-shared-promotion-decision\\\\\"");'),
            ('try requireMarker("\\\\\\"status\\\\\\": \\\\\"shared CI perf promotion pending\\\\\"");', 'try requireMarker("\\\\\\"status\\\\\\": \\\\\"shared CI perf promotion approved\\\\\"");', 'survey_marker:try requireMarker("\\\\\\"status\\\\\\": \\\\\"shared CI perf promotion pending\\\\\"");'),
        )
        for old, new, expected_prefix in survey_variants:
            build_fixture_tree(root)
            write_text(survey, replace_once(read_text(survey), old, new))
            if not expect_failure(root, expected_prefix):
                print("PHASE4_PERF_BASELINE_PACKET_SELF_TEST=fail")
                print(f"survey drift case did not fail closed: {expected_prefix}")
                return 1
            cases += 1

        if cases != EXPECTED_SELF_TEST_CASES:
            print("PHASE4_PERF_BASELINE_PACKET_SELF_TEST=fail")
            print(f"expected {EXPECTED_SELF_TEST_CASES} self-test cases, saw {cases}")
            return 1

    print("PHASE4_PERF_BASELINE_PACKET_SELF_TEST=pass")
    print(f"PHASE4_PERF_BASELINE_PACKET_SELF_TEST_CASES={EXPECTED_SELF_TEST_CASES}")
    return 0


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    root = Path(args.root).resolve()
    missing = validate_root(root)
    if missing:
        print("PHASE4_PERF_BASELINE_PACKET_CHECK=fail")
        for item in missing:
            print(item)
        return 1

    print("PHASE4_PERF_BASELINE_PACKET_CHECK=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())