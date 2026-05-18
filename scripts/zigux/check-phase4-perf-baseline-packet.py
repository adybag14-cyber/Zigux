#!/usr/bin/env python3
"""Guard the bounded Phase 4 local-only perf packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

MANIFEST = Path("zigux/tests/phase4_perf_baseline_manifest.json")
SURVEY = Path("zigux/tests/phase4_perf_baseline_survey.zig")
MATRIX = Path("Documentation/zigux/phase4-validation-matrix.md")
REVIEW_CHECKLIST = Path("Documentation/zigux/review-checklist.md")
NOTE = Path("Documentation/zigux/phase4-reversible-delivery-evidence.md")
TESTS_README = Path("zigux/tests/README.md")

EXPECTED_COORDINATION_OWNERS = [
    "ABI and Runtime Team",
    "Shared Subsystems Pod",
]
EXPECTED_LOCAL_ONLY_POSTURE_NOTE = (
    "The dedicated perf-baseline survey keeps approved local benchmark commands and "
    "approved local-only acceptable limits explicit while shared CI perf promotion "
    "remains intentionally pending."
)
EXPECTED_SELF_TEST_CASES = 12

MANIFEST_MARKERS = (
    '"lane_key": "P4-L20"',
    '"phase": "Phase 4"',
    '"owner": "Validation and Perf Team"',
    '"rollback_owner": "Validation and Perf Team"',
    '"decision_owner": "Validation and Perf Team"',
    '"shared_ci_perf_promotion_status": "pending"',
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
    '"status": "shared CI perf promotion pending"',
)

SURVEY_MARKERS = (
    'test "phase4 perf baseline survey keeps exact local-only iteration and sample counts explicit" {',
    'try requireMarkerCount("\\"acceptable_limit_iterations\\": 4", 2);',
    'try requireMarkerCount("\\"acceptable_limit_sample_count\\": 7", 2);',
    'try requireMarker("\\"benchmark_command\\": \\"zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig\\"");',
    'try requireMarker("\\"benchmark_command\\": \\"zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig\\"");',
    'try requireMarker("\\"shared_ci_perf_promotion_status\\": \\"pending\\"");',
    'try requireMarker("\\"coordination_owners\\": [");',
)

MATRIX_MARKERS = (
    "local-only benchmark commands and acceptable limits are approved today",
    "the dedicated perf-baseline survey may keep the approved local benchmark commands and the approved local-only acceptable limits for both landed rollback gates machine-checked",
    "must stay outside the shared `phase4-test` entrypoint until any shared CI perf promotion is intentionally approved",
    "any future shared CI perf-promotion claim must name the Validation and Perf Team as the decision owner and the ABI and Runtime Team plus Shared Subsystems Pod as coordination owners",
    "current replay path: `zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig` and `make -C zigux phase4-perf-baseline-survey`",
)

REVIEW_CHECKLIST_MARKERS = (
    "keep the directly readable local-only perf packet explicit",
    "keep the Validation and Perf Team as the decision owner for any broader shared-CI perf promotion",
    "keep the ABI and Runtime Team plus Shared Subsystems Pod as coordination owners for that policy call",
    "keep the pending shared-CI perf-promotion posture explicit instead of implying shared CI perf approval",
)

NOTE_MARKERS = (
    "Current direct readback in this run confirmed this note, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, `scripts/zigux/check-phase4-reversible-delivery-pins.py`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` on current `master`.",
    "Current direct-readback dedicated local-only perf checker: `scripts/zigux/check-phase4-perf-baseline-packet.py`.",
    "Current direct-readback dedicated local-only perf companion members:",
    "`zigux/tests/phase4_perf_baseline_manifest.json`",
    "`zigux/tests/phase4_perf_baseline_survey.zig`",
    "The direct checker pair now publishes `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=16` and `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=14` here",
)

TESTS_README_MARKERS = (
    "Current direct-readback dedicated local-only perf checker: `scripts/zigux/check-phase4-perf-baseline-packet.py`",
    "Current direct-readback dedicated local-only perf companion members: `zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`",
    "current shared Phase 4 ownership reminder: keep rollback-owner wording, artifact-diff contract references, and remaining-gap truthfulness aligned with `Documentation/zigux/phase4-reversible-delivery-evidence.md` instead of reconstructing the broader packet from older route names alone",
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


def expect_json_value(payload: object, path: tuple[str | int, ...], expected: object, missing: list[str]) -> None:
    current = payload
    for step in path:
        try:
            current = current[step]
        except (KeyError, IndexError, TypeError):
            missing.append(f"manifest_json:{'.'.join(str(part) for part in path)}:missing")
            return
    if current != expected:
        missing.append(
            "manifest_json:"
            + ".".join(str(part) for part in path)
            + f":expected={expected!r}:actual={current!r}"
        )


def validate_manifest_json(manifest_data: dict[str, object], missing: list[str]) -> None:
    expected_values = (
        (("lane_key",), "P4-L20"),
        (("phase",), "Phase 4"),
        (("owner",), "Validation and Perf Team"),
        (("rollback_owner",), "Validation and Perf Team"),
        (("decision_owner",), "Validation and Perf Team"),
        (("coordination_owners",), EXPECTED_COORDINATION_OWNERS),
        (("shared_ci_perf_promotion_status",), "pending"),
        (("local_only_posture_note",), EXPECTED_LOCAL_ONLY_POSTURE_NOTE),
        (("atomic64", "benchmark_command"), "zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig"),
        (("atomic64", "acceptable_limit_max_elapsed_ns"), 8192),
        (("atomic64", "evidence", 1, "runs", 0, "checksum"), 3626254113632800175),
        (("atomic64", "evidence", 1, "runs", 1, "checksum"), 9210681150676220922),
        (("bitmap", "benchmark_command"), "zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig"),
        (("bitmap", "acceptable_limit_max_elapsed_ns"), 12288),
        (("bitmap", "evidence", 1, "runs", 0, "checksum"), 5216946504564592253),
        (("bitmap", "evidence", 1, "runs", 1, "checksum"), 7942141539243507472),
        (("promotion_decision", "status"), "shared CI perf promotion pending"),
        (("promotion_decision", "owner"), "Validation and Perf Team"),
    )
    for path, expected in expected_values:
        expect_json_value(manifest_data, path, expected, missing)


def validate_root(root: Path) -> list[str]:
    missing: list[str] = []

    manifest_path = root / MANIFEST
    survey_path = root / SURVEY
    matrix_path = root / MATRIX
    checklist_path = root / REVIEW_CHECKLIST
    note_path = root / NOTE
    tests_readme_path = root / TESTS_README

    for path in (manifest_path, survey_path, matrix_path, checklist_path, note_path, tests_readme_path):
        if not path.is_file():
            missing.append(f"file:{path.relative_to(root).as_posix()}")

    if missing:
        return missing

    manifest_text = read_text(manifest_path)
    require_markers(manifest_text, MANIFEST_MARKERS, "manifest_marker", missing)
    if manifest_text.count('"acceptable_limit_iterations": 4') != 2:
        missing.append('manifest_count:"acceptable_limit_iterations": 4:expected=2')
    if manifest_text.count('"acceptable_limit_sample_count": 7') != 2:
        missing.append('manifest_count:"acceptable_limit_sample_count": 7:expected=2')

    try:
        manifest_data = json.loads(manifest_text)
    except json.JSONDecodeError as exc:
        missing.append(f"manifest_json:decode:{exc.msg}")
    else:
        validate_manifest_json(manifest_data, missing)

    require_markers(read_text(survey_path), SURVEY_MARKERS, "survey_marker", missing)
    require_markers(read_text(matrix_path), MATRIX_MARKERS, "matrix_marker", missing)
    require_markers(read_text(checklist_path), REVIEW_CHECKLIST_MARKERS, "review_checklist_marker", missing)
    require_markers(read_text(note_path), NOTE_MARKERS, "note_marker", missing)
    require_markers(read_text(tests_readme_path), TESTS_README_MARKERS, "tests_readme_marker", missing)

    return missing


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise ValueError(f"missing replacement target: {old!r}")
    return text.replace(old, new, 1)


def build_fixture_tree(root: Path) -> None:
    write_text(
        root / MANIFEST,
        """{
  "lane_key": "P4-L20",
  "phase": "Phase 4",
  "owner": "Validation and Perf Team",
  "rollback_owner": "Validation and Perf Team",
  "decision_owner": "Validation and Perf Team",
  "coordination_owners": [
    "ABI and Runtime Team",
    "Shared Subsystems Pod"
  ],
  "shared_ci_perf_promotion_status": "pending",
  "local_only_posture_note": "The dedicated perf-baseline survey keeps approved local benchmark commands and approved local-only acceptable limits explicit while shared CI perf promotion remains intentionally pending.",
  "atomic64": {
    "benchmark_command": "zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig",
    "linux_style_wrapper": "make -C zigux phase4-perf-baseline-survey",
    "acceptable_limit_status": "approved_local_only",
    "acceptable_limit_metric": "median_elapsed_ns",
    "acceptable_limit_iterations": 4,
    "acceptable_limit_sample_count": 7,
    "acceptable_limit_max_elapsed_ns": 8192,
    "evidence": [
      {
        "id": "phase4-perf-baseline-atomic64-acceptable-limit",
        "kind": "acceptable_limit",
        "metric": "median_elapsed_ns",
        "status": "approved_local_only",
        "sample_count_note": "seven monotonic samples",
        "max_elapsed_ns": 8192
      },
      {
        "id": "phase4-perf-baseline-atomic64-command-evidence",
        "kind": "threshold_replay",
        "runs": [
          { "iterations": 1, "checksum": 3626254113632800175, "final_counter": 130322557735600377 },
          { "iterations": 4, "checksum": 9210681150676220922, "final_counter": 130322557735600376 }
        ]
      }
    ]
  },
  "bitmap": {
    "benchmark_command": "zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig",
    "linux_style_wrapper": "make -C zigux phase4-perf-baseline-survey",
    "acceptable_limit_status": "approved_local_only",
    "acceptable_limit_metric": "median_elapsed_ns",
    "acceptable_limit_iterations": 4,
    "acceptable_limit_sample_count": 7,
    "acceptable_limit_max_elapsed_ns": 12288,
    "evidence": [
      {
        "id": "phase4-perf-baseline-bitmap-acceptable-limit",
        "kind": "acceptable_limit",
        "metric": "median_elapsed_ns",
        "status": "approved_local_only",
        "sample_count_note": "seven monotonic samples",
        "max_elapsed_ns": 12288
      },
      {
        "id": "phase4-perf-baseline-bitmap-command-evidence",
        "kind": "threshold_replay",
        "runs": [
          { "iterations": 1, "checksum": 5216946504564592253, "final_first_zero": 109 },
          { "iterations": 4, "checksum": 7942141539243507472, "final_first_zero": 109 }
        ]
      }
    ]
  },
  "promotion_decision": {
    "id": "phase4-perf-baseline-shared-promotion-decision",
    "status": "shared CI perf promotion pending",
    "owner": "Validation and Perf Team"
  }
}
""",
    )
    write_text(
        root / SURVEY,
        """test "phase4 perf baseline survey keeps exact local-only iteration and sample counts explicit" {
    try requireMarkerCount("\\"acceptable_limit_iterations\\": 4", 2);
    try requireMarkerCount("\\"acceptable_limit_sample_count\\": 7", 2);
}
test "phase4 perf baseline survey keeps atomic64 and bitmap command evidence explicit" {
    try requireMarker("\\"benchmark_command\\": \\"zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig\\"");
    try requireMarker("\\"benchmark_command\\": \\"zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig\\"");
    try requireMarker("\\"shared_ci_perf_promotion_status\\": \\"pending\\"");
    try requireMarker("\\"coordination_owners\\": [");
}
""",
    )
    write_text(
        root / MATRIX,
        """local-only benchmark commands and acceptable limits are approved today
the dedicated perf-baseline survey may keep the approved local benchmark commands and the approved local-only acceptable limits for both landed rollback gates machine-checked
must stay outside the shared `phase4-test` entrypoint until any shared CI perf promotion is intentionally approved
any future shared CI perf-promotion claim must name the Validation and Perf Team as the decision owner and the ABI and Runtime Team plus Shared Subsystems Pod as coordination owners
current replay path: `zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig` and `make -C zigux phase4-perf-baseline-survey`
""",
    )
    write_text(
        root / REVIEW_CHECKLIST,
        """keep the directly readable local-only perf packet explicit
keep the Validation and Perf Team as the decision owner for any broader shared-CI perf promotion
keep the ABI and Runtime Team plus Shared Subsystems Pod as coordination owners for that policy call
keep the pending shared-CI perf-promotion posture explicit instead of implying shared CI perf approval
""",
    )
    write_text(
        root / NOTE,
        """Current direct readback in this run confirmed this note, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, `scripts/zigux/check-phase4-reversible-delivery-pins.py`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` on current `master`.
Current direct-readback dedicated local-only perf checker: `scripts/zigux/check-phase4-perf-baseline-packet.py`.
Current direct-readback dedicated local-only perf companion members:
`zigux/tests/phase4_perf_baseline_manifest.json`
`zigux/tests/phase4_perf_baseline_survey.zig`
The direct checker pair now publishes `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=16` and `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=14` here
""",
    )
    write_text(
        root / TESTS_README,
        """Current direct-readback dedicated local-only perf checker: `scripts/zigux/check-phase4-perf-baseline-packet.py`
Current direct-readback dedicated local-only perf companion members: `zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`
current shared Phase 4 ownership reminder: keep rollback-owner wording, artifact-diff contract references, and remaining-gap truthfulness aligned with `Documentation/zigux/phase4-reversible-delivery-evidence.md` instead of reconstructing the broader packet from older route names alone
""",
    )


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
        variants = (
            (MANIFEST, '"acceptable_limit_iterations": 4', '"acceptable_limit_iterations": 5', 'manifest_count:"acceptable_limit_iterations": 4:expected=2'),
            (MANIFEST, '"acceptable_limit_sample_count": 7', '"acceptable_limit_sample_count": 8', 'manifest_count:"acceptable_limit_sample_count": 7:expected=2'),
            (MANIFEST, '"decision_owner": "Validation and Perf Team"', '"decision_owner": "ABI and Runtime Team"', 'manifest_json:decision_owner:'),
            (MANIFEST, '"benchmark_command": "zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig"', '"benchmark_command": "zig build phase4-runtime-atomic64-bench --build-file zigux/tests/phase4_build.zig"', 'manifest_marker:"benchmark_command": "zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig"'),
            (SURVEY, 'try requireMarker("\\\"shared_ci_perf_promotion_status\\\": \\\"pending\\\"");', 'try requireMarker("\\\"shared_ci_perf_promotion_status\\\": \\\"approved\\\"");', 'survey_marker:try requireMarker("\\\"shared_ci_perf_promotion_status\\\": \\\"pending\\\"");'),
            (MATRIX, "local-only benchmark commands and acceptable limits are approved today", "local-only benchmark commands and acceptable limits are pending review today", "matrix_marker:local-only benchmark commands and acceptable limits are approved today"),
            (REVIEW_CHECKLIST, "keep the Validation and Perf Team as the decision owner for any broader shared-CI perf promotion", "keep the ABI and Runtime Team as the decision owner for any broader shared-CI perf promotion", "review_checklist_marker:keep the Validation and Perf Team as the decision owner for any broader shared-CI perf promotion"),
            (NOTE, "PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=14", "PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=8", "note_marker:The direct checker pair now publishes `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=16` and `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=14` here"),
            (TESTS_README, "Current direct-readback dedicated local-only perf companion members: `zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`", "Current direct-readback dedicated local-only perf companion members: `zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey_drift.zig`", "tests_readme_marker:Current direct-readback dedicated local-only perf companion members: `zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`"),
        )

        for rel, old, new, expected_prefix in variants:
            build_fixture_tree(root)
            target = root / rel
            write_text(target, replace_once(read_text(target), old, new))
            if not expect_failure(root, expected_prefix):
                print("PHASE4_PERF_BASELINE_PACKET_SELF_TEST=fail")
                print(f"drift case did not fail closed: {expected_prefix}")
                return 1
            cases += 1

        build_fixture_tree(root)
        (root / MANIFEST).unlink()
        if not expect_failure(root, f"file:{MANIFEST.as_posix()}"):
            print("PHASE4_PERF_BASELINE_PACKET_SELF_TEST=fail")
            print("missing manifest case did not fail closed")
            return 1
        cases += 1

        build_fixture_tree(root)
        write_text(root / MANIFEST, "{")
        if not expect_failure(root, "manifest_json:decode:"):
            print("PHASE4_PERF_BASELINE_PACKET_SELF_TEST=fail")
            print("broken manifest JSON case did not fail closed")
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

    missing = validate_root(Path(args.root).resolve())
    if missing:
        print("PHASE4_PERF_BASELINE_PACKET_CHECK=fail")
        for item in missing:
            print(item)
        return 1

    print("PHASE4_PERF_BASELINE_PACKET_CHECK=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
