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
SCRIPTS_README = Path("scripts/zigux/README.md")

EXPECTED_COORDINATION_OWNERS = [
    "ABI and Runtime Team",
    "Shared Subsystems Pod",
]
EXPECTED_LOCAL_ONLY_POSTURE_NOTE = (
    "The dedicated perf-baseline survey keeps approved local benchmark commands and "
    "approved local-only acceptable limits explicit while shared CI perf promotion "
    "remains intentionally pending."
)
EXPECTED_BOOTSTRAP_CI_POSTURE = (
    "reviewability_only_local_survey_wrappers_not_on_shared_phase4_test_or_bootstrap_workflow"
)
EXPECTED_SELF_TEST_CASES = 39

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
    '"gate_surfaces": [',
    '"surface": "zigux/tests/atomic64_diff.zig"',
    '"surface": "zigux/tests/bitmap_diff.zig"',
    '"kind": "legacy_threshold_replay_alias"',
    '"target_id": "phase4-perf-baseline-bitmap-command-evidence"',
)

SURVEY_MARKERS = (
    'test "phase4 perf baseline survey keeps exact local-only iteration, sample, and replay counts explicit" {',
    'try requireMarkerCount("\\\"acceptable_limit_iterations\\\": 4", 2);',
    'try requireMarkerCount("\\\"acceptable_limit_sample_count\\\": 7", 2);',
    'try requireMarker("\\\"benchmark_command\\\": \\\"zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig\\\"");',
    'try requireMarker("\\\"benchmark_command\\\": \\\"zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig\\\"");',
    'try requireMarker("\\\"shared_ci_perf_promotion_status\\\": \\\"pending\\\"");',
    'try requireMarker("\\\"coordination_owners\\\": [");',
    'try requireMarker("\\\"rollback_owner\\\": \\\"Validation and Perf Team\\\"");',
    'try requireMarker("\\\"decision_owner\\\": \\\"Validation and Perf Team\\\"");',
    'try requireMarker("\\\"dedicated_local_survey_wrapper\\\": \\\"zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig\\\"");',
    'try requireMarker("\\\"dedicated_linux_style_survey_wrapper\\\": \\\"make -C zigux phase4-perf-baseline-survey\\\"");',
    'try requireMarker("\\\"validation_entrypoint\\\": \\\"zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig\\\"");',
    'try requireMarker("\\\"bootstrap_ci_posture\\\": \\\"reviewability_only_local_survey_wrappers_not_on_shared_phase4_test_or_bootstrap_workflow\\\"");',
    'try requireMarker("\\\"shared_lab_and_ci_matrix_anchor\\\": \\\"Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix\\\"");',
    'try requireMarker("\\\"local_only_posture_note\\\": \\\"The dedicated perf-baseline survey keeps approved local benchmark commands and approved local-only acceptable limits explicit while shared CI perf promotion remains intentionally pending.\\\"");',
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
    "Current direct readback in this run confirmed this note, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, `scripts/zigux/check-phase4-tests-readme-packet.py`, `scripts/zigux/check-phase4-reversible-delivery-pins.py`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `scripts/zigux/check-phase4-perf-threshold-matrix.py`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` on current `master`.",
    "Current direct-readback dedicated local-only perf checkers: `scripts/zigux/check-phase4-perf-baseline-packet.py` and `scripts/zigux/check-phase4-perf-threshold-matrix.py`.",
    "Current direct-readback dedicated local-only perf companion members:",
    "  * `zigux/tests/phase4_perf_baseline_manifest.json`",
    "  * `zigux/tests/phase4_perf_baseline_survey.zig`",
    "The direct checker pair now publishes `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=32` and `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=20` here",
)

SCRIPTS_README_MARKERS = (
    "`scripts/zigux/check-artifact-diff-contract.py`, `scripts/zigux/check-phase4-artifact-diff-determinism.py`, `scripts/zigux/check-phase4-artifact-diff-validator-replays.py`, `scripts/zigux/check-phase4-repo-reality-warning.py`, `scripts/zigux/check-phase4-reversible-delivery-pins.py`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `scripts/zigux/check-phase4-perf-threshold-matrix.py`, `scripts/zigux/check-phase4-remaining-gap-matrix.py`, and `scripts/zigux/check-phase4-workflow-route-counts.py` keep the current helper-contract, validator-replay, shared rollback-owner reminder, local-only perf-governance, recovered remaining-gap, and route-inventory packet explicit on current `master`",
    "`Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-validation-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `zigux/tests/atomic64_diff.zig`, `zigux/tests/runtime_atomic64_diff.zig`, `scripts/zigux/check-phase4-perf-threshold-matrix.py`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` remain the current reminder-surface companions for that active Phase 4 rollback-readiness and perf-governance packet",
    "keep the current governance split explicit here too: the direct-readback shared handoff stays narrower than the broader recovered note companions, the Validation and Perf Team remains the decision owner for any broader shared-CI perf promotion, the ABI and Runtime Team plus Shared Subsystems Pod remain the coordination owners for that policy call, and the dedicated perf-baseline survey must stay local-only until a later bounded lane intentionally widens that posture",
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
        missing.append("manifest_json:" + ".".join(str(part) for part in path) + f":expected={expected!r}:actual={current!r}")

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
        (("dedicated_local_survey_wrapper",), "zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig"),
        (("dedicated_linux_style_survey_wrapper",), "make -C zigux phase4-perf-baseline-survey"),
        (("validation_entrypoint",), "zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig"),
        (("bootstrap_ci_posture",), EXPECTED_BOOTSTRAP_CI_POSTURE),
        (("shared_lab_and_ci_matrix_anchor",), "Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix"),
        (("gate_surfaces", 0, "surface"), "zigux/tests/atomic64_diff.zig"),
        (("gate_surfaces", 0, "gate_owner"), "ABI and Runtime Team"),
        (("gate_surfaces", 0, "gate_rollback_owner"), "ABI and Runtime Team"),
        (("gate_surfaces", 0, "threshold_posture"), "threshold_pending_until_runtime_atomic64_scope_widens"),
        (("gate_surfaces", 1, "surface"), "zigux/tests/bitmap_diff.zig"),
        (("gate_surfaces", 1, "gate_owner"), "Shared Subsystems Pod"),
        (("gate_surfaces", 1, "gate_rollback_owner"), "Shared Subsystems Pod"),
        (("gate_surfaces", 1, "threshold_posture"), "threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks"),
        (("atomic64", "gate_owner"), "ABI and Runtime Team"),
        (("atomic64", "gate_rollback_owner"), "ABI and Runtime Team"),
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
        (("bitmap", "gate_owner"), "Shared Subsystems Pod"),
        (("bitmap", "gate_rollback_owner"), "Shared Subsystems Pod"),
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
        (("bitmap", "evidence", 2, "id"), "phase4-perf-baseline-bitmap-command"),
        (("bitmap", "evidence", 2, "kind"), "legacy_threshold_replay_alias"),
        (("bitmap", "evidence", 2, "target_id"), "phase4-perf-baseline-bitmap-command-evidence"),
        (("promotion_decision", "id"), "phase4-perf-baseline-shared-promotion-decision"),
        (("promotion_decision", "status"), "shared CI perf promotion pending"),
        (("promotion_decision", "owner"), "Validation and Perf Team"),
        (("promotion_decision", "coordination_owners"), EXPECTED_COORDINATION_OWNERS),
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
    scripts_readme_path = root / SCRIPTS_README
    for path in (manifest_path, survey_path, matrix_path, checklist_path, note_path, scripts_readme_path):
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
    require_markers(read_text(scripts_readme_path), SCRIPTS_README_MARKERS, "scripts_readme_marker", missing)
    return missing

def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise ValueError(f"missing replacement target: {old!r}")
    return text.replace(old, new, 1)

def build_fixture_tree(root: Path) -> None:
    manifest_data = {
        "lane_key": "P4-L20",
        "phase": "Phase 4",
        "owner": "Validation and Perf Team",
        "rollback_owner": "Validation and Perf Team",
        "decision_owner": "Validation and Perf Team",
        "coordination_owners": EXPECTED_COORDINATION_OWNERS,
        "shared_ci_perf_promotion_status": "pending",
        "local_only_posture_note": EXPECTED_LOCAL_ONLY_POSTURE_NOTE,
        "dedicated_local_survey_wrapper": "zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig",
        "dedicated_linux_style_survey_wrapper": "make -C zigux phase4-perf-baseline-survey",
        "validation_entrypoint": "zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig",
        "bootstrap_ci_posture": EXPECTED_BOOTSTRAP_CI_POSTURE,
        "shared_lab_and_ci_matrix_anchor": "Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix",
        "gate_surfaces": [
            {"surface": "zigux/tests/atomic64_diff.zig", "gate_owner": "ABI and Runtime Team", "gate_rollback_owner": "ABI and Runtime Team", "threshold_posture": "threshold_pending_until_runtime_atomic64_scope_widens"},
            {"surface": "zigux/tests/bitmap_diff.zig", "gate_owner": "Shared Subsystems Pod", "gate_rollback_owner": "Shared Subsystems Pod", "threshold_posture": "threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks"},
        ],
        "atomic64": {
            "gate_owner": "ABI and Runtime Team",
            "gate_rollback_owner": "ABI and Runtime Team",
            "benchmark_command": "zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig",
            "linux_style_wrapper": "make -C zigux phase4-perf-baseline-survey",
            "acceptable_limit_status": "approved_local_only",
            "acceptable_limit_metric": "median_elapsed_ns",
            "acceptable_limit_iterations": 4,
            "acceptable_limit_sample_count": 7,
            "acceptable_limit_max_elapsed_ns": 8192,
            "evidence": [
                {"id": "phase4-perf-baseline-atomic64-acceptable-limit", "kind": "acceptable_limit", "metric": "median_elapsed_ns", "status": "approved_local_only", "sample_count_note": "seven monotonic samples", "max_elapsed_ns": 8192},
                {"id": "phase4-perf-baseline-atomic64-command-evidence", "kind": "threshold_replay", "runs": [{"iterations": 1, "checksum": 3626254113632800175, "final_counter": 130322557735600377}, {"iterations": 4, "checksum": 9210681150676220922, "final_counter": 130322557735600376}]},
            ],
        },
        "bitmap": {
            "gate_owner": "Shared Subsystems Pod",
            "gate_rollback_owner": "Shared Subsystems Pod",
            "benchmark_command": "zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig",
            "linux_style_wrapper": "make -C zigux phase4-perf-baseline-survey",
            "acceptable_limit_status": "approved_local_only",
            "acceptable_limit_metric": "median_elapsed_ns",
            "acceptable_limit_iterations": 4,
            "acceptable_limit_sample_count": 7,
            "acceptable_limit_max_elapsed_ns": 12288,
            "evidence": [
                {"id": "phase4-perf-baseline-bitmap-acceptable-limit", "kind": "acceptable_limit", "metric": "median_elapsed_ns", "status": "approved_local_only", "sample_count_note": "seven monotonic samples", "max_elapsed_ns": 12288},
                {"id": "phase4-perf-baseline-bitmap-command-evidence", "kind": "threshold_replay", "runs": [{"iterations": 1, "checksum": 5216946504564592253, "final_first_zero": 109}, {"iterations": 4, "checksum": 7942141539243507472, "final_first_zero": 109}]},
                {"id": "phase4-perf-baseline-bitmap-command", "kind": "legacy_threshold_replay_alias", "target_id": "phase4-perf-baseline-bitmap-command-evidence"},
            ],
        },
        "promotion_decision": {"id": "phase4-perf-baseline-shared-promotion-decision", "status": "shared CI perf promotion pending", "owner": "Validation and Perf Team", "coordination_owners": EXPECTED_COORDINATION_OWNERS},
    }
    write_text(root / MANIFEST, json.dumps(manifest_data, indent=2) + "\n")
    write_text(root / SURVEY, "\n".join(SURVEY_MARKERS) + "\n")
    write_text(root / MATRIX, """local-only benchmark commands and acceptable limits are approved today
the dedicated perf-baseline survey may keep the approved local benchmark commands and the approved local-only acceptable limits for both landed rollback gates machine-checked
must stay outside the shared `phase4-test` entrypoint until any shared CI perf promotion is intentionally approved
any future shared CI perf-promotion claim must name the Validation and Perf Team as the decision owner and the ABI and Runtime Team plus Shared Subsystems Pod as coordination owners
current replay path: `zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig` and `make -C zigux phase4-perf-baseline-survey`
""")
    write_text(root / REVIEW_CHECKLIST, """keep the directly readable local-only perf packet explicit
keep the Validation and Perf Team as the decision owner for any broader shared-CI perf promotion
keep the ABI and Runtime Team plus Shared Subsystems Pod as coordination owners for that policy call
keep the pending shared-CI perf-promotion posture explicit instead of implying shared CI perf approval
""")
    write_text(root / NOTE, """Current direct readback in this run confirmed this note, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, `scripts/zigux/check-phase4-tests-readme-packet.py`, `scripts/zigux/check-phase4-reversible-delivery-pins.py`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `scripts/zigux/check-phase4-perf-threshold-matrix.py`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` on current `master`.
Current direct-readback dedicated local-only perf checkers: `scripts/zigux/check-phase4-perf-baseline-packet.py` and `scripts/zigux/check-phase4-perf-threshold-matrix.py`.
Current direct-readback dedicated local-only perf companion members:
  * `zigux/tests/phase4_perf_baseline_manifest.json`
  * `zigux/tests/phase4_perf_baseline_survey.zig`
The direct checker pair now publishes `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=32` and `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=20` here
""")
    write_text(root / SCRIPTS_README, """`scripts/zigux/check-artifact-diff-contract.py`, `scripts/zigux/check-phase4-artifact-diff-determinism.py`, `scripts/zigux/check-phase4-artifact-diff-validator-replays.py`, `scripts/zigux/check-phase4-repo-reality-warning.py`, `scripts/zigux/check-phase4-reversible-delivery-pins.py`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `scripts/zigux/check-phase4-perf-threshold-matrix.py`, `scripts/zigux/check-phase4-remaining-gap-matrix.py`, and `scripts/zigux/check-phase4-workflow-route-counts.py` keep the current helper-contract, validator-replay, shared rollback-owner reminder, local-only perf-governance, recovered remaining-gap, and route-inventory packet explicit on current `master`
`Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-validation-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `zigux/tests/atomic64_diff.zig`, `zigux/tests/runtime_atomic64_diff.zig`, `scripts/zigux/check-phase4-perf-threshold-matrix.py`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` remain the current reminder-surface companions for that active Phase 4 rollback-readiness and perf-governance packet
keep the current governance split explicit here too: the direct-readback shared handoff stays narrower than the broader recovered note companions, the Validation and Perf Team remains the decision owner for any broader shared-CI perf promotion, the ABI and Runtime Team plus Shared Subsystems Pod remain the coordination owners for that policy call, and the dedicated perf-baseline survey must stay local-only until a later bounded lane intentionally widens that posture
""")

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
            (
                MANIFEST,
                '"acceptable_limit_iterations": 4',
                '"acceptable_limit_iterations": 5',
                'manifest_count:"acceptable_limit_iterations": 4:expected=2',
            ),
            (
                MANIFEST,
                '"acceptable_limit_sample_count": 7',
                '"acceptable_limit_sample_count": 8',
                'manifest_count:"acceptable_limit_sample_count": 7:expected=2',
            ),
            (
                MANIFEST,
                '"decision_owner": "Validation and Perf Team"',
                '"decision_owner": "ABI and Runtime Team"',
                "manifest_json:decision_owner:",
            ),
            (
                MANIFEST,
                '  "coordination_owners": [\n    "ABI and Runtime Team",\n    "Shared Subsystems Pod"\n  ],',
                '  "coordination_owners": [\n    "ABI and Replay Team",\n    "Shared Subsystems Pod"\n  ],',
                "manifest_json:coordination_owners:",
            ),
            (
                MANIFEST,
                '    "coordination_owners": [\n      "ABI and Runtime Team",\n      "Shared Subsystems Pod"\n    ]',
                '    "coordination_owners": [\n      "ABI and Replay Team",\n      "Shared Subsystems Pod"\n    ]',
                "manifest_json:promotion_decision.coordination_owners:",
            ),
            (
                MANIFEST,
                '"surface": "zigux/tests/atomic64_diff.zig"',
                '"surface": "zigux/tests/runtime_atomic64_diff.zig"',
                "manifest_json:gate_surfaces.0.surface:",
            ),
            (
                MANIFEST,
                '"threshold_posture": "threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks"',
                '"threshold_posture": "threshold_pending_until_bitmap_gate_reaches_ci_perf_approval"',
                "manifest_json:gate_surfaces.1.threshold_posture:",
            ),
            (
                MANIFEST,
                '"benchmark_command": "zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig"',
                '"benchmark_command": "zig build phase4-runtime-atomic64-bench --build-file zigux/tests/phase4_build.zig"',
                'manifest_marker:"benchmark_command": "zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig"',
            ),
            (
                MANIFEST,
                '"dedicated_local_survey_wrapper": "zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig"',
                '"dedicated_local_survey_wrapper": "zig build phase4-local-baseline-survey --build-file zigux/tests/phase4_build.zig"',
                "manifest_json:dedicated_local_survey_wrapper:",
            ),
            (
                MANIFEST,
                '"dedicated_linux_style_survey_wrapper": "make -C zigux phase4-perf-baseline-survey"',
                '"dedicated_linux_style_survey_wrapper": "make -C zigux phase4-local-baseline-survey"',
                "manifest_json:dedicated_linux_style_survey_wrapper:",
            ),
            (
                MANIFEST,
                '"validation_entrypoint": "zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig"',
                '"validation_entrypoint": "zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig"',
                "manifest_json:validation_entrypoint:",
            ),
            (
                MANIFEST,
                '"bootstrap_ci_posture": "reviewability_only_local_survey_wrappers_not_on_shared_phase4_test_or_bootstrap_workflow"',
                '"bootstrap_ci_posture": "approved_for_shared_phase4_test_and_bootstrap_workflow"',
                "manifest_json:bootstrap_ci_posture:",
            ),
            (
                MANIFEST,
                '"shared_lab_and_ci_matrix_anchor": "Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix"',
                '"shared_lab_and_ci_matrix_anchor": "Documentation/zigux/phase4-validation-matrix.md#perf-baseline"',
                "manifest_json:shared_lab_and_ci_matrix_anchor:",
            ),
            (
                MANIFEST,
                '  "atomic64": {\n    "gate_owner": "ABI and Runtime Team",',
                '  "atomic64": {\n    "gate_owner": "ABI and Replay Team",',
                "manifest_json:atomic64.gate_owner:",
            ),
            (
                MANIFEST,
                '  "atomic64": {\n    "gate_owner": "ABI and Runtime Team",\n    "gate_rollback_owner": "ABI and Runtime Team",',
                '  "atomic64": {\n    "gate_owner": "ABI and Runtime Team",\n    "gate_rollback_owner": "ABI and Replay Team",',
                "manifest_json:atomic64.gate_rollback_owner:",
            ),
            (
                MANIFEST,
                '  "bitmap": {\n    "gate_owner": "Shared Subsystems Pod",',
                '  "bitmap": {\n    "gate_owner": "Shared Subsystems Team",',
                "manifest_json:bitmap.gate_owner:",
            ),
            (
                MANIFEST,
                '  "bitmap": {\n    "gate_owner": "Shared Subsystems Pod",\n    "gate_rollback_owner": "Shared Subsystems Pod",',
                '  "bitmap": {\n    "gate_owner": "Shared Subsystems Pod",\n    "gate_rollback_owner": "Shared Subsystems Team",',
                "manifest_json:bitmap.gate_rollback_owner:",
            ),
            (
                MANIFEST,
                '"sample_count_note": "seven monotonic samples"',
                '"sample_count_note": "six monotonic samples"',
                "manifest_json:atomic64.evidence.0.sample_count_note:",
            ),
            (
                MANIFEST,
                '"id": "phase4-perf-baseline-bitmap-command-evidence"',
                '"id": "phase4-perf-baseline-bitmap-run-evidence"',
                "manifest_json:bitmap.evidence.1.id:",
            ),
            (
                MANIFEST,
                '"kind": "legacy_threshold_replay_alias"',
                '"kind": "legacy_threshold_replay_pointer"',
                "manifest_json:bitmap.evidence.2.kind:",
            ),
            (
                MANIFEST,
                '"target_id": "phase4-perf-baseline-bitmap-command-evidence"',
                '"target_id": "phase4-perf-baseline-bitmap-command-proof"',
                'manifest_marker:"target_id": "phase4-perf-baseline-bitmap-command-evidence"',
            ),
            (
                MANIFEST,
                '"id": "phase4-perf-baseline-shared-promotion-decision"',
                '"id": "phase4-perf-baseline-shared-promotion-record"',
                "manifest_json:promotion_decision.id:",
            ),
            (
                SURVEY,
                'try requireMarker("\\\"shared_ci_perf_promotion_status\\\": \\\"pending\\\"");',
                'try requireMarker("\\\"shared_ci_perf_promotion_status\\\": \\\"approved\\\"");',
                'survey_marker:try requireMarker("\\\"shared_ci_perf_promotion_status\\\": \\\"pending\\\"");',
            ),
            (
                SURVEY,
                'try requireMarker("\\\"rollback_owner\\\": \\\"Validation and Perf Team\\\"");',
                'try requireMarker("\\\"rollback_owner\\\": \\\"ABI and Runtime Team\\\"");',
                'survey_marker:try requireMarker("\\\"rollback_owner\\\": \\\"Validation and Perf Team\\\"");',
            ),
            (
                SURVEY,
                'try requireMarker("\\\"decision_owner\\\": \\\"Validation and Perf Team\\\"");',
                'try requireMarker("\\\"decision_owner\\\": \\\"ABI and Runtime Team\\\"");',
                'survey_marker:try requireMarker("\\\"decision_owner\\\": \\\"Validation and Perf Team\\\"");',
            ),
            (
                SURVEY,
                'try requireMarker("\\\"dedicated_local_survey_wrapper\\\": \\\"zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig\\\"");',
                'try requireMarker("\\\"dedicated_local_survey_wrapper\\\": \\\"zig build phase4-local-baseline-survey --build-file zigux/tests/phase4_build.zig\\\"");',
                'survey_marker:try requireMarker("\\\"dedicated_local_survey_wrapper\\\": \\\"zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig\\\"");',
            ),
            (
                SURVEY,
                'try requireMarker("\\\"dedicated_linux_style_survey_wrapper\\\": \\\"make -C zigux phase4-perf-baseline-survey\\\"");',
                'try requireMarker("\\\"dedicated_linux_style_survey_wrapper\\\": \\\"make -C zigux phase4-local-baseline-survey\\\"");',
                'survey_marker:try requireMarker("\\\"dedicated_linux_style_survey_wrapper\\\": \\\"make -C zigux phase4-perf-baseline-survey\\\"");',
            ),
            (
                SURVEY,
                'try requireMarker("\\\"validation_entrypoint\\\": \\\"zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig\\\"");',
                'try requireMarker("\\\"validation_entrypoint\\\": \\\"zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig\\\"");',
                'survey_marker:try requireMarker("\\\"validation_entrypoint\\\": \\\"zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig\\\"");',
            ),
            (
                SURVEY,
                'try requireMarker("\\\"bootstrap_ci_posture\\\": \\\"reviewability_only_local_survey_wrappers_not_on_shared_phase4_test_or_bootstrap_workflow\\\"");',
                'try requireMarker("\\\"bootstrap_ci_posture\\\": \\\"approved_for_shared_phase4_test_and_bootstrap_workflow\\\"");',
                'survey_marker:try requireMarker("\\\"bootstrap_ci_posture\\\": \\\"reviewability_only_local_survey_wrappers_not_on_shared_phase4_test_or_bootstrap_workflow\\\"");',
            ),
            (
                MATRIX,
                "local-only benchmark commands and acceptable limits are approved today",
                "local-only benchmark commands and acceptable limits are pending review today",
                "matrix_marker:local-only benchmark commands and acceptable limits are approved today",
            ),
            (
                REVIEW_CHECKLIST,
                "keep the pending shared-CI perf-promotion posture explicit instead of implying shared CI perf approval",
                "keep the shared-CI perf-promotion posture explicit as approved shared CI perf coverage",
                "review_checklist_marker:keep the pending shared-CI perf-promotion posture explicit instead of implying shared CI perf approval",
            ),
            (
                NOTE,
                "PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=20",
                "PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=8",
                "note_marker:The direct checker pair now publishes `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=32` and `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=20` here",
            ),
            (
                NOTE,
                "Current direct-readback dedicated local-only perf companion members:\n  * `zigux/tests/phase4_perf_baseline_manifest.json`\n  * `zigux/tests/phase4_perf_baseline_survey.zig`",
                "Current direct-readback dedicated local-only perf companion members:\n  * `zigux/tests/phase4_perf_baseline_manifest.json`\n  * `zigux/tests/phase4_perf_baseline_survey_drift.zig`",
                "note_marker:  * `zigux/tests/phase4_perf_baseline_survey.zig`",
            ),
            (
                SCRIPTS_README,
                "`Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-validation-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `zigux/tests/atomic64_diff.zig`, `zigux/tests/runtime_atomic64_diff.zig`, `scripts/zigux/check-phase4-perf-threshold-matrix.py`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` remain the current reminder-surface companions for that active Phase 4 rollback-readiness and perf-governance packet",
                "`Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-validation-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `zigux/tests/atomic64_diff.zig`, `zigux/tests/runtime_atomic64_diff.zig`, `scripts/zigux/check-phase4-perf-threshold-matrix.py`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey_drift.zig` remain the current reminder-surface companions for that active Phase 4 rollback-readiness and perf-governance packet",
                "scripts_readme_marker:`Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-validation-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `zigux/tests/atomic64_diff.zig`, `zigux/tests/runtime_atomic64_diff.zig`, `scripts/zigux/check-phase4-perf-threshold-matrix.py`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` remain the current reminder-surface companions for that active Phase 4 rollback-readiness and perf-governance packet",
            ),
            (
                MANIFEST,
                '"shared_ci_perf_promotion_status": "pending"',
                '"shared_ci_perf_promotion_status": "approved"',
                "manifest_json:shared_ci_perf_promotion_status:",
            ),
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
        (root / SURVEY).unlink()
        if not expect_failure(root, f"file:{SURVEY.as_posix()}"):
            print("PHASE4_PERF_BASELINE_PACKET_SELF_TEST=fail")
            print("missing survey case did not fail closed")
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