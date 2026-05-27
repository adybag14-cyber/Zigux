#!/usr/bin/env python3
"""Guard the bounded Phase 4 remaining-gap matrix packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

MATRIX = Path("Documentation/zigux/phase4-validation-matrix.md")
MEASURABILITY_GAP_NOTE = Path("Documentation/zigux/phase4-measurability-gap-survey.md")
KPROBE_NOTE = Path("Documentation/zigux/phase4-kprobe-example-gap-survey.md")
TEST_FSMOUNT_NOTE = Path("Documentation/zigux/phase4-test-fsmount-gap-survey.md")
KPROBE_MANIFEST = Path("zigux/tests/phase4_kprobe_example_manifest.json")
KPROBE_SURVEY = Path("zigux/tests/phase4_kprobe_example_survey.zig")
TEST_FSMOUNT_MANIFEST = Path("zigux/tests/phase4_test_fsmount_manifest.json")
TEST_FSMOUNT_SURVEY = Path("zigux/tests/phase4_test_fsmount_survey.zig")
PERF_MANIFEST = Path("zigux/tests/phase4_perf_baseline_manifest.json")
PHASE4_BUILD = Path("zigux/tests/phase4_build.zig")

EXPECTED_SELF_TEST_CASE_COUNT = 43

KPROBE_SURVEYED_COMMIT = "3ba64cd4e41a4de1c8fd8dbaecb23702ad9701a3"
TEST_FSMOUNT_SURVEYED_COMMIT = "3ba64cd4e41a4de1c8fd8dbaecb23702ad9701a3"
KPROBE_SHARED_BUILD_REPLAY = "phase4-kprobe-example-survey-tests"
TEST_FSMOUNT_SHARED_BUILD_REPLAY = "phase4-test-fsmount-survey-tests"
KPROBE_MATRIX_ANCHOR = "Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix"
TEST_FSMOUNT_MATRIX_ANCHOR = "Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix"
PERF_MATRIX_ANCHOR = "Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix"

KPROBE_REVERSIBLE_DELIVERY_EVIDENCE = (
    "PHASE4_REVERSIBLE_DELIVERY_EVIDENCE=keep the dedicated parked survey packet, "
    "the explicit local_lab_replay marker, the local survey wrapper, the explicit "
    "bootstrap-CI posture, the direct validation entrypoint, and the absent Zig "
    "starter boundary explicit until a later bounded starter lane intentionally "
    "widens this surface"
)
KPROBE_NEXT_BOUNDED_EVIDENCE_STEP = (
    "Keep this parked packet adjacent to the shared gate-evidence note, the shared "
    "Phase 4 exact-readback packet, the validation matrix, the explicit "
    "bootstrap-CI posture, the explicit local lab replay marker, the dedicated "
    "local `make -C zigux phase4-kprobe-example-survey` wrapper, and the direct "
    "`zig test zigux/tests/phase4_kprobe_example_survey.zig` validation entrypoint "
    "until a later bounded Phase 4 lane lands the actual Zig starter with an "
    "updated rollback-readiness contract."
)
TEST_FSMOUNT_REVERSIBLE_DELIVERY_EVIDENCE = (
    "PHASE4_REVERSIBLE_DELIVERY_EVIDENCE=keep the dedicated parked survey packet, "
    "both local survey wrappers, the explicit bootstrap-CI posture, the explicit "
    "no-perf-threshold posture, and the absent Zig starter boundary explicit until "
    "a later bounded validator or starter lane intentionally widens this surface"
)
TEST_FSMOUNT_NEXT_BOUNDED_EVIDENCE_STEP = (
    "keep the dedicated parked survey packet adjacent to the shared gate-evidence "
    "note, the shared Phase 4 exact-readback packet, the validation matrix, the "
    "explicit bootstrap-CI posture, the explicit local lab replay marker, the explicit reviewability-only "
    "no-perf-threshold posture, the dedicated local `zig build "
    "phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig` survey "
    "wrapper, and the matching Linux-style `make -C zigux "
    "phase4-test-fsmount-survey` wrapper until a later bounded lane intentionally "
    "promotes the validator surface or lands the Zig starter"
)

MATRIX_MARKERS = (
    "`scripts/zigux/check-phase4-remaining-gap-matrix.py`",
    "`Documentation/zigux/phase4-measurability-gap-survey.md`",
    "`Documentation/zigux/phase4-kprobe-example-gap-survey.md`",
    "`zigux/tests/phase4_kprobe_example_manifest.json`",
    "`zigux/tests/phase4_kprobe_example_survey.zig`",
    "`make -C zigux phase4-kprobe-example-survey`",
    "c_anchor_only_until_kprobe_example_starter_lands",
    "`Documentation/zigux/phase4-test-fsmount-gap-survey.md`",
    "`zigux/tests/phase4_test_fsmount_manifest.json`",
    "`zigux/tests/phase4_test_fsmount_survey.zig`",
    "`zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`",
    "`make -C zigux phase4-test-fsmount-survey`",
    "reviewability_only_no_perf_threshold",
    "`zigux/tests/phase4_perf_baseline_manifest.json`",
    "shared CI perf promotion pending",
    "`python3 scripts/zigux/check-phase4-perf-baseline-packet.py --self-test` then `python3 scripts/zigux/check-phase4-perf-baseline-packet.py`",
    "Validation and Perf Team owning that policy decision",
    "gate owners: `ABI and Runtime Team` and `Shared Subsystems Pod`",
    "rollback owners: `ABI and Runtime Team` and `Shared Subsystems Pod`",
)

MEASURABILITY_GAP_NOTE_MARKERS = (
    "# Phase 4 Measurability Gap Survey",
    "PHASE4_MEASURABILITY_GAP_REMAINING_PACKET_COUNT=3",
    "`Documentation/zigux/phase4-kprobe-example-gap-survey.md`, `zigux/tests/phase4_kprobe_example_manifest.json`, and `zigux/tests/phase4_kprobe_example_survey.zig`",
    "`Documentation/zigux/phase4-test-fsmount-gap-survey.md`, `zigux/tests/phase4_test_fsmount_manifest.json`, and `zigux/tests/phase4_test_fsmount_survey.zig`",
    "`zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, and `scripts/zigux/check-phase4-perf-threshold-matrix.py`",
    "`Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-reversible-delivery-evidence.md`, and `scripts/zigux/validate-phase4.py`",
)

KPROBE_NOTE_MARKERS = (
    "PHASE4_KPROBE_STATUS=parked_gap_packet_landed",
    "PHASE4_KPROBE_LANE_KEY=P4-L19",
    "PHASE4_KPROBE_C_ANCHOR=samples/kprobes/kprobe_example.c",
    "PHASE4_KPROBE_CURRENT_LINUX_REPLAY=make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m",
    "PHASE4_KPROBE_LOCAL_LAB_REPLAY=make -C zigux phase4-kprobe-example-survey",
    "PHASE4_KPROBE_LOCAL_SURVEY_WRAPPER=make -C zigux phase4-kprobe-example-survey",
    "PHASE4_KPROBE_BOOTSTRAP_CI_POSTURE=reviewability_only_local_survey_wrapper_not_on_shared_phase4_test_or_bootstrap_workflow",
    f"PHASE4_KPROBE_SHARED_LAB_AND_CI_MATRIX_ANCHOR={KPROBE_MATRIX_ANCHOR}",
    "PHASE4_KPROBE_VALIDATION_ENTRYPOINT=zig test zigux/tests/phase4_kprobe_example_survey.zig",
    "PHASE4_KPROBE_OWNER=Validation and Perf Team",
    "PHASE4_KPROBE_ROLLBACK_OWNER=Validation and Perf Team",
    f"PHASE4_REVERSIBLE_DELIVERY_EVIDENCE={KPROBE_REVERSIBLE_DELIVERY_EVIDENCE.split('=', 1)[1]}",
    "Current `master` still does not ship `samples/zigux/kprobe_example.zig`.",
)

TEST_FSMOUNT_NOTE_MARKERS = (
    "PHASE4_TEST_FSMOUNT_STATUS=parked_gap_packet_landed",
    "PHASE4_TEST_FSMOUNT_LANE_KEY=P4-L19",
    "PHASE4_TEST_FSMOUNT_C_ANCHOR=samples/vfs/test-fsmount.c",
    "PHASE4_TEST_FSMOUNT_CURRENT_LINUX_REPLAY=make M=samples/vfs",
    "PHASE4_TEST_FSMOUNT_LOCAL_LAB_REPLAY=zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
    "PHASE4_TEST_FSMOUNT_LOCAL_SURVEY_WRAPPER=zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
    "PHASE4_TEST_FSMOUNT_LINUX_STYLE_SURVEY_WRAPPER=make -C zigux phase4-test-fsmount-survey",
    "PHASE4_TEST_FSMOUNT_BOOTSTRAP_CI_POSTURE=reviewability_only_local_survey_wrappers_not_on_shared_phase4_test_or_bootstrap_workflow",
    f"PHASE4_TEST_FSMOUNT_SHARED_LAB_AND_CI_MATRIX_ANCHOR={TEST_FSMOUNT_MATRIX_ANCHOR}",
    "PHASE4_TEST_FSMOUNT_VALIDATION_ENTRYPOINT=zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
    "PHASE4_TEST_FSMOUNT_THRESHOLD_POSTURE=reviewability_only_no_perf_threshold",
    "PHASE4_TEST_FSMOUNT_OWNER=Validation and Perf Team",
    "PHASE4_TEST_FSMOUNT_ROLLBACK_OWNER=Validation and Perf Team",
    f"PHASE4_REVERSIBLE_DELIVERY_EVIDENCE={TEST_FSMOUNT_REVERSIBLE_DELIVERY_EVIDENCE.split('=', 1)[1]}",
    "Current `master` still does not ship `samples/zigux/test_fsmount.zig`.",
)

PHASE4_BUILD_MARKERS = (
    "phase4_test_fsmount_survey.zig",
    TEST_FSMOUNT_SHARED_BUILD_REPLAY,
    "phase4-test-fsmount-survey",
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


def expect_json_value(payload: object, path: tuple[str | int, ...], expected: object, missing: list[str], label: str) -> None:
    current = payload
    for step in path:
        try:
            current = current[step]
        except (KeyError, IndexError, TypeError):
            missing.append(f"{label}:{'.'.join(str(part) for part in path)}:missing")
            return
    if current != expected:
        missing.append(
            f"{label}:{'.'.join(str(part) for part in path)}:expected={expected!r}:actual={current!r}"
        )


def expect_lower_hex_sha(payload: object, path: tuple[str | int, ...], missing: list[str], label: str) -> None:
    current = payload
    for step in path:
        try:
            current = current[step]
        except (KeyError, IndexError, TypeError):
            missing.append(f"{label}:{'.'.join(str(part) for part in path)}:missing")
            return
    if not isinstance(current, str) or len(current) != 40 or any(ch not in "0123456789abcdef" for ch in current):
        missing.append(f"{label}:{'.'.join(str(part) for part in path)}:invalid_lower_hex_sha:{current!r}")


def validate_kprobe_manifest(payload: dict[str, object], missing: list[str]) -> None:
    expected_values = (
        (("lane_key",), "P4-L19"),
        (("phase",), "Phase 4"),
        (("owner",), "Validation and Perf Team"),
        (("rollback_owner",), "Validation and Perf Team"),
        (("anchor",), "samples/kprobes/kprobe_example.c"),
        (("roadmap_destinations",), ["samples/zigux/kprobe_example.zig"]),
        (("current_replay",), "make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m"),
        (("isolated_survey_replay",), "zig build phase4-kprobe-example-survey --build-file zigux/tests/phase4_build.zig"),
        (("shared_build_replay",), KPROBE_SHARED_BUILD_REPLAY),
        (("shared_lab_and_ci_matrix_anchor",), KPROBE_MATRIX_ANCHOR),
        (("threshold_posture",), "c_anchor_only_until_kprobe_example_starter_lands"),
        (("reversible_delivery_evidence",), KPROBE_REVERSIBLE_DELIVERY_EVIDENCE),
        (("next_bounded_evidence_step",), KPROBE_NEXT_BOUNDED_EVIDENCE_STEP),
        (("survey_summary", "kprobe_makefile_replay_present"), True),
        (("survey_summary", "kprobe_anchor_symbol_present"), True),
        (("survey_summary", "zig_sample_present"), False),
        (("survey_summary", "phase4_build_present"), True),
        (("survey_summary", "phase4_validation_matrix_present"), True),
        (("survey_summary", "phase4_gate_evidence_present"), True),
        (("gaps", 3, "id"), "phase4-kprobe-example-shared-validator-promotion"),
        (("gaps", 3, "status"), "starter_landed"),
        (("gaps", 4, "id"), "phase4-kprobe-example-zig-sample"),
        (("gaps", 4, "status"), "ready_next"),
    )
    for path, expected in expected_values:
        expect_json_value(payload, path, expected, missing, "kprobe_manifest")
    expect_lower_hex_sha(payload, ("surveyed_commit",), missing, "kprobe_manifest")


def validate_test_fsmount_manifest(payload: dict[str, object], missing: list[str]) -> None:
    expected_values = (
        (("lane_key",), "P4-L19"),
        (("phase",), "Phase 4"),
        (("c_anchor",), "samples/vfs/test-fsmount.c"),
        (("roadmap_destinations",), ["samples/zigux/test_fsmount.zig"]),
        (("current_linux_replay",), "make M=samples/vfs"),
        (("local_lab_replay",), "zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig"),
        (("dedicated_local_survey_wrapper",), "zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig"),
        (("dedicated_linux_style_survey_wrapper",), "make -C zigux phase4-test-fsmount-survey"),
        (("shared_build_replay",), TEST_FSMOUNT_SHARED_BUILD_REPLAY),
        (("bootstrap_ci_posture",), "reviewability_only_local_survey_wrappers_not_on_shared_phase4_test_or_bootstrap_workflow"),
        (("shared_lab_and_ci_matrix_anchor",), TEST_FSMOUNT_MATRIX_ANCHOR),
        (("validation_entrypoint",), "zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig"),
        (("owner",), "Validation and Perf Team"),
        (("rollback_owner",), "Validation and Perf Team"),
        (("current_measurable_status",), "absent_on_current_master_but_reviewable_through_the_dedicated_gap_packet_without_claiming_a_shipped_zig_starter"),
        (("threshold_posture",), "reviewability_only_no_perf_threshold"),
        (("reversible_delivery_evidence",), TEST_FSMOUNT_REVERSIBLE_DELIVERY_EVIDENCE),
        (("next_bounded_evidence_step",), TEST_FSMOUNT_NEXT_BOUNDED_EVIDENCE_STEP),
        (("survey_summary", "zig_sample_present"), False),
        (("survey_summary", "phase4_build_present"), True),
        (("survey_summary", "phase4_validation_matrix_present"), True),
        (("survey_summary", "phase4_gate_evidence_present"), True),
        (("survey_summary", "scripts_readme_present"), True),
        (("survey_summary", "tests_readme_present"), True),
        (("gaps", 2, "id"), "phase4-test-fsmount-shared-validator-promotion"),
        (("gaps", 2, "status"), "starter_landed"),
        (("gaps", 4, "id"), "phase4-test-fsmount-zig-sample"),
        (("gaps", 4, "status"), "ready_next"),
    )
    for path, expected in expected_values:
        expect_json_value(payload, path, expected, missing, "test_fsmount_manifest")
    expect_lower_hex_sha(payload, ("surveyed_commit",), missing, "test_fsmount_manifest")


def validate_perf_manifest(payload: dict[str, object], missing: list[str]) -> None:
    expected_values = (
        (("lane_key",), "P4-L20"),
        (("phase",), "Phase 4"),
        (("owner",), "Validation and Perf Team"),
        (("rollback_owner",), "Validation and Perf Team"),
        (("decision_owner",), "Validation and Perf Team"),
        (("coordination_owners",), ["ABI and Runtime Team", "Shared Subsystems Pod"]),
        (("shared_ci_perf_promotion_status",), "pending"),
        (("local_only_posture_note",), "The dedicated perf-baseline survey keeps approved local benchmark commands and approved local-only acceptable limits explicit while shared CI perf promotion remains intentionally pending."),
        (("dedicated_local_survey_wrapper",), "zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig"),
        (("dedicated_linux_style_survey_wrapper",), "make -C zigux phase4-perf-baseline-survey"),
        (("validation_entrypoint",), "zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig"),
        (("bootstrap_ci_posture",), "reviewability_only_local_survey_wrappers_not_on_shared_phase4_test_or_bootstrap_workflow"),
        (("shared_lab_and_ci_matrix_anchor",), PERF_MATRIX_ANCHOR),
        (("atomic64", "gate_owner"), "ABI and Runtime Team"),
        (("atomic64", "gate_rollback_owner"), "ABI and Runtime Team"),
        (("atomic64", "benchmark_command"), "zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig"),
        (("bitmap", "gate_owner"), "Shared Subsystems Pod"),
        (("bitmap", "gate_rollback_owner"), "Shared Subsystems Pod"),
        (("bitmap", "benchmark_command"), "zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig"),
        (("promotion_decision", "status"), "shared CI perf promotion pending"),
        (("promotion_decision", "owner"), "Validation and Perf Team"),
        (("promotion_decision", "coordination_owners"), ["ABI and Runtime Team", "Shared Subsystems Pod"]),
    )
    for path, expected in expected_values:
        expect_json_value(payload, path, expected, missing, "perf_manifest")


def validate_root(root: Path) -> list[str]:
    missing: list[str] = []
    for path in (
        MATRIX,
        MEASURABILITY_GAP_NOTE,
        KPROBE_NOTE,
        TEST_FSMOUNT_NOTE,
        KPROBE_MANIFEST,
        KPROBE_SURVEY,
        TEST_FSMOUNT_MANIFEST,
        TEST_FSMOUNT_SURVEY,
        PERF_MANIFEST,
        PHASE4_BUILD,
    ):
        if not (root / path).is_file():
            missing.append(f"file:{path.as_posix()}")
    if missing:
        return missing

    require_markers(read_text(root / MATRIX), MATRIX_MARKERS, "matrix_marker", missing)
    require_markers(read_text(root / MEASURABILITY_GAP_NOTE), MEASURABILITY_GAP_NOTE_MARKERS, "measurability_gap_note_marker", missing)
    require_markers(read_text(root / KPROBE_NOTE), KPROBE_NOTE_MARKERS, "kprobe_note_marker", missing)
    require_markers(read_text(root / TEST_FSMOUNT_NOTE), TEST_FSMOUNT_NOTE_MARKERS, "test_fsmount_note_marker", missing)
    require_markers(read_text(root / PHASE4_BUILD), PHASE4_BUILD_MARKERS, "phase4_build_marker", missing)

    try:
        validate_kprobe_manifest(json.loads(read_text(root / KPROBE_MANIFEST)), missing)
    except json.JSONDecodeError as exc:
        missing.append(f"kprobe_manifest:decode:{exc.msg}")

    try:
        validate_test_fsmount_manifest(json.loads(read_text(root / TEST_FSMOUNT_MANIFEST)), missing)
    except json.JSONDecodeError as exc:
        missing.append(f"test_fsmount_manifest:decode:{exc.msg}")

    try:
        validate_perf_manifest(json.loads(read_text(root / PERF_MANIFEST)), missing)
    except json.JSONDecodeError as exc:
        missing.append(f"perf_manifest:decode:{exc.msg}")

    return missing


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise ValueError(f"missing replacement target: {old!r}")
    return text.replace(old, new, 1)


def write_fixture_tree(root: Path) -> None:
    write_text(root / MATRIX, "\n".join(["# Phase 4 Validation Matrix", *MATRIX_MARKERS]) + "\n")
    write_text(root / MEASURABILITY_GAP_NOTE, "\n".join(MEASURABILITY_GAP_NOTE_MARKERS) + "\n")
    write_text(root / KPROBE_NOTE, "\n".join(KPROBE_NOTE_MARKERS) + "\n")
    write_text(root / TEST_FSMOUNT_NOTE, "\n".join(TEST_FSMOUNT_NOTE_MARKERS) + "\n")
    write_text(root / KPROBE_SURVEY, 'test "phase4 kprobe survey fixture" {}\n')
    write_text(root / TEST_FSMOUNT_SURVEY, 'test "phase4 test-fsmount survey fixture" {}\n')
    write_text(root / PHASE4_BUILD, "\n".join(PHASE4_BUILD_MARKERS) + "\n")

    write_text(
        root / KPROBE_MANIFEST,
        json.dumps(
            {
                "lane_key": "P4-L19",
                "phase": "Phase 4",
                "owner": "Validation and Perf Team",
                "rollback_owner": "Validation and Perf Team",
                "surveyed_commit": KPROBE_SURVEYED_COMMIT,
                "anchor": "samples/kprobes/kprobe_example.c",
                "roadmap_destinations": ["samples/zigux/kprobe_example.zig"],
                "current_replay": "make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m",
                "isolated_survey_replay": "zig build phase4-kprobe-example-survey --build-file zigux/tests/phase4_build.zig",
                "shared_build_replay": KPROBE_SHARED_BUILD_REPLAY,
                "shared_lab_and_ci_matrix_anchor": KPROBE_MATRIX_ANCHOR,
                "threshold_posture": "c_anchor_only_until_kprobe_example_starter_lands",
                "reversible_delivery_evidence": KPROBE_REVERSIBLE_DELIVERY_EVIDENCE,
                "next_bounded_evidence_step": KPROBE_NEXT_BOUNDED_EVIDENCE_STEP,
                "survey_summary": {
                    "kprobe_makefile_replay_present": true,
                    "kprobe_anchor_symbol_present": true,
                    "zig_sample_present": false,
                    "phase4_build_present": true,
                    "phase4_validation_matrix_present": true,
                    "phase4_gate_evidence_present": true
                },
                "gaps": [
                    {"id": "phase4-kprobe-example-survey-manifest", "status": "starter_landed"},
                    {"id": "phase4-kprobe-example-survey-gate", "status": "starter_landed"},
                    {"id": "phase4-kprobe-example-c-anchor-replay", "status": "starter_landed"},
                    {"id": "phase4-kprobe-example-shared-validator-promotion", "status": "starter_landed"},
                    {"id": "phase4-kprobe-example-zig-sample", "status": "ready_next"}
                ]
            },
            indent=2,
        ) + "\n",
    )

    write_text(
        root / TEST_FSMOUNT_MANIFEST,
        json.dumps(
            {
                "lane_key": "P4-L19",
                "phase": "Phase 4",
                "surveyed_commit": TEST_FSMOUNT_SURVEYED_COMMIT,
                "c_anchor": "samples/vfs/test-fsmount.c",
                "roadmap_destinations": ["samples/zigux/test_fsmount.zig"],
                "current_linux_replay": "make M=samples/vfs",
                "local_lab_replay": "zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
                "dedicated_local_survey_wrapper": "zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
                "dedicated_linux_style_survey_wrapper": "make -C zigux phase4-test-fsmount-survey",
                "shared_build_replay": TEST_FSMOUNT_SHARED_BUILD_REPLAY,
                "bootstrap_ci_posture": "reviewability_only_local_survey_wrappers_not_on_shared_phase4_test_or_bootstrap_workflow",
                "shared_lab_and_ci_matrix_anchor": TEST_FSMOUNT_MATRIX_ANCHOR,
                "validation_entrypoint": "zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
                "owner": "Validation and Perf Team",
                "rollback_owner": "Validation and Perf Team",
                "current_measurable_status": "absent_on_current_master_but_reviewable_through_the_dedicated_gap_packet_without_claiming_a_shipped_zig_starter",
                "threshold_posture": "reviewability_only_no_perf_threshold",
                "reversible_delivery_evidence": TEST_FSMOUNT_REVERSIBLE_DELIVERY_EVIDENCE,
                "next_bounded_evidence_step": TEST_FSMOUNT_NEXT_BOUNDED_EVIDENCE_STEP,
                "survey_summary": {
                    "zig_sample_present": false,
                    "phase4_build_present": true,
                    "phase4_validation_matrix_present": true,
                    "phase4_gate_evidence_present": true,
                    "scripts_readme_present": true,
                    "tests_readme_present": true
                },
                "gaps": [
                    {"id": "phase4-test-fsmount-survey-manifest", "status": "starter_landed"},
                    {"id": "phase4-test-fsmount-survey-gate", "status": "starter_landed"},
                    {"id": "phase4-test-fsmount-shared-validator-promotion", "status": "starter_landed"},
                    {"id": "phase4-test-fsmount-readme-alignment", "status": "starter_landed"},
                    {"id": "phase4-test-fsmount-zig-sample", "status": "ready_next"}
                ]
            },
            indent=2,
        ) + "\n",
    )

    write_text(
        root / PERF_MANIFEST,
        json.dumps(
            {
                "lane_key": "P4-L20",
                "phase": "Phase 4",
                "owner": "Validation and Perf Team",
                "rollback_owner": "Validation and Perf Team",
                "decision_owner": "Validation and Perf Team",
                "coordination_owners": ["ABI and Runtime Team", "Shared Subsystems Pod"],
                "shared_ci_perf_promotion_status": "pending",
                "local_only_posture_note": "The dedicated perf-baseline survey keeps approved local benchmark commands and approved local-only acceptable limits explicit while shared CI perf promotion remains intentionally pending.",
                "dedicated_local_survey_wrapper": "zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig",
                "dedicated_linux_style_survey_wrapper": "make -C zigux phase4-perf-baseline-survey",
                "validation_entrypoint": "zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig",
                "bootstrap_ci_posture": "reviewability_only_local_survey_wrappers_not_on_shared_phase4_test_or_bootstrap_workflow",
                "shared_lab_and_ci_matrix_anchor": PERF_MATRIX_ANCHOR,
                "atomic64": {
                    "gate_owner": "ABI and Runtime Team",
                    "gate_rollback_owner": "ABI and Runtime Team",
                    "benchmark_command": "zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig"
                },
                "bitmap": {
                    "gate_owner": "Shared Subsystems Pod",
                    "gate_rollback_owner": "Shared Subsystems Pod",
                    "benchmark_command": "zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig"
                },
                "promotion_decision": {
                    "status": "shared CI perf promotion pending",
                    "owner": "Validation and Perf Team",
                    "coordination_owners": ["ABI and Runtime Team", "Shared Subsystems Pod"]
                }
            },
            indent=2,
        ) + "\n",
    )


def expect_failure(root: Path, expected_prefix: str) -> bool:
    return any(item.startswith(expected_prefix) for item in validate_root(root))


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase4-remaining-gap-matrix-") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture_tree(root)
        if validate_root(root):
            print("PHASE4_REMAINING_GAP_MATRIX_SELF_TEST=fail")
            print("baseline fixture did not validate cleanly")
            return 1

        cases = 1
        variants = (
            (MATRIX, "`scripts/zigux/check-phase4-remaining-gap-matrix.py`", "`scripts/zigux/check-phase4-gap-matrix.py`", "matrix_marker:`scripts/zigux/check-phase4-remaining-gap-matrix.py`"),
            (MATRIX, "`Documentation/zigux/phase4-measurability-gap-survey.md`", "`Documentation/zigux/phase4-gap-summary.md`", "matrix_marker:`Documentation/zigux/phase4-measurability-gap-survey.md`"),
            (MATRIX, "`Documentation/zigux/phase4-kprobe-example-gap-survey.md`", "`Documentation/zigux/phase4-kprobe-gap-survey.md`", "matrix_marker:`Documentation/zigux/phase4-kprobe-example-gap-survey.md`"),
            (MATRIX, "`zigux/tests/phase4_kprobe_example_manifest.json`", "`zigux/tests/phase4_kprobe_gap_manifest.json`", "matrix_marker:`zigux/tests/phase4_kprobe_example_manifest.json`"),
            (MATRIX, "`zigux/tests/phase4_kprobe_example_survey.zig`", "`zigux/tests/phase4_kprobe_gap_survey.zig`", "matrix_marker:`zigux/tests/phase4_kprobe_example_survey.zig`"),
            (MATRIX, "`make -C zigux phase4-kprobe-example-survey`", "`make -C zigux phase4-kprobe-gap-survey`", "matrix_marker:`make -C zigux phase4-kprobe-example-survey`"),
            (MATRIX, "c_anchor_only_until_kprobe_example_starter_lands", "reviewability_only_no_perf_threshold", "matrix_marker:c_anchor_only_until_kprobe_example_starter_lands"),
            (MATRIX, "`Documentation/zigux/phase4-test-fsmount-gap-survey.md`", "`Documentation/zigux/phase4-fsmount-gap-survey.md`", "matrix_marker:`Documentation/zigux/phase4-test-fsmount-gap-survey.md`"),
            (MATRIX, "`zigux/tests/phase4_test_fsmount_manifest.json`", "`zigux/tests/phase4_test_fsmount_gap_manifest.json`", "matrix_marker:`zigux/tests/phase4_test_fsmount_manifest.json`"),
            (MATRIX, "`zigux/tests/phase4_test_fsmount_survey.zig`", "`zigux/tests/phase4_test_fsmount_gap_survey.zig`", "matrix_marker:`zigux/tests/phase4_test_fsmount_survey.zig`"),
            (MATRIX, "`zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`", "`zig build phase4-test-fsmount-gap-survey --build-file zigux/tests/phase4_build.zig`", "matrix_marker:`zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`"),
            (MATRIX, "`make -C zigux phase4-test-fsmount-survey`", "`make -C zigux phase4-test-fsmount-gap-survey`", "matrix_marker:`make -C zigux phase4-test-fsmount-survey`"),
            (MATRIX, "`zigux/tests/phase4_perf_baseline_manifest.json`", "`zigux/tests/phase4_perf_manifest.json`", "matrix_marker:`zigux/tests/phase4_perf_baseline_manifest.json`"),
            (MEASURABILITY_GAP_NOTE, "PHASE4_MEASURABILITY_GAP_REMAINING_PACKET_COUNT=3", "PHASE4_MEASURABILITY_GAP_REMAINING_PACKET_COUNT=2", "measurability_gap_note_marker:PHASE4_MEASURABILITY_GAP_REMAINING_PACKET_COUNT=3"),
            (MEASURABILITY_GAP_NOTE, "`Documentation/zigux/phase4-kprobe-example-gap-survey.md`, `zigux/tests/phase4_kprobe_example_manifest.json`, and `zigux/tests/phase4_kprobe_example_survey.zig`", "`Documentation/zigux/phase4-kprobe-gap-survey.md`, `zigux/tests/phase4_kprobe_example_manifest.json`, and `zigux/tests/phase4_kprobe_example_survey.zig`", "measurability_gap_note_marker:`Documentation/zigux/phase4-kprobe-example-gap-survey.md`, `zigux/tests/phase4_kprobe_example_manifest.json`, and `zigux/tests/phase4_kprobe_example_survey.zig`"),
            (MEASURABILITY_GAP_NOTE, "`Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-reversible-delivery-evidence.md`, and `scripts/zigux/validate-phase4.py`", "`Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-gate-evidence.md`, and `Documentation/zigux/phase4-reversible-delivery-evidence.md`", "measurability_gap_note_marker:`Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-reversible-delivery-evidence.md`, and `scripts/zigux/validate-phase4.py`"),
            (MEASURABILITY_GAP_NOTE, "`zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, and `scripts/zigux/check-phase4-perf-threshold-matrix.py`", "`zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`, and `scripts/zigux/check-phase4-perf-baseline-packet.py`", "measurability_gap_note_marker:`zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, and `scripts/zigux/check-phase4-perf-threshold-matrix.py`"),
            (KPROBE_NOTE, "PHASE4_KPROBE_LOCAL_LAB_REPLAY=make -C zigux phase4-kprobe-example-survey", "PHASE4_KPROBE_LOCAL_LAB_REPLAY=make -C zigux phase4-kprobe-gap-survey", "kprobe_note_marker:PHASE4_KPROBE_LOCAL_LAB_REPLAY=make -C zigux phase4-kprobe-example-survey"),
            (KPROBE_NOTE, "PHASE4_KPROBE_VALIDATION_ENTRYPOINT=zig test zigux/tests/phase4_kprobe_example_survey.zig", "PHASE4_KPROBE_VALIDATION_ENTRYPOINT=zig test zigux/tests/phase4_kprobe_gap_survey.zig", "kprobe_note_marker:PHASE4_KPROBE_VALIDATION_ENTRYPOINT=zig test zigux/tests/phase4_kprobe_example_survey.zig"),
            (KPROBE_MANIFEST, f'"surveyed_commit": "{KPROBE_SURVEYED_COMMIT}"', '"surveyed_commit": "INVALID"', "kprobe_manifest:surveyed_commit:invalid_lower_hex_sha:'INVALID'"),
            (KPROBE_MANIFEST, f'"shared_build_replay": "{KPROBE_SHARED_BUILD_REPLAY}"', '"shared_build_replay": "phase4-kprobe-gap-survey-tests"', f"kprobe_manifest:shared_build_replay:expected='{KPROBE_SHARED_BUILD_REPLAY}'"),
            (KPROBE_MANIFEST, '"status": "ready_next"', '"status": "starter_landed"', "kprobe_manifest:gaps.4.status:expected='ready_next'"),
            (TEST_FSMOUNT_NOTE, "PHASE4_TEST_FSMOUNT_LOCAL_LAB_REPLAY=zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig", "PHASE4_TEST_FSMOUNT_LOCAL_LAB_REPLAY=zig build phase4-test-fsmount-gap-survey --build-file zigux/tests/phase4_build.zig", "test_fsmount_note_marker:PHASE4_TEST_FSMOUNT_LOCAL_LAB_REPLAY=zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig"),
            (TEST_FSMOUNT_NOTE, "PHASE4_TEST_FSMOUNT_VALIDATION_ENTRYPOINT=zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig", "PHASE4_TEST_FSMOUNT_VALIDATION_ENTRYPOINT=zig build phase4-test-fsmount-gap-survey --build-file zigux/tests/phase4_build.zig", "test_fsmount_note_marker:PHASE4_TEST_FSMOUNT_VALIDATION_ENTRYPOINT=zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig"),
            (TEST_FSMOUNT_MANIFEST, f'"surveyed_commit": "{TEST_FSMOUNT_SURVEYED_COMMIT}"', '"surveyed_commit": "INVALID"', "test_fsmount_manifest:surveyed_commit:invalid_lower_hex_sha:'INVALID'"),
            (TEST_FSMOUNT_MANIFEST, f'"shared_build_replay": "{TEST_FSMOUNT_SHARED_BUILD_REPLAY}"', '"shared_build_replay": "phase4-test-fsmount-gap-survey-tests"', f"test_fsmount_manifest:shared_build_replay:expected='{TEST_FSMOUNT_SHARED_BUILD_REPLAY}'"),
            (TEST_FSMOUNT_MANIFEST, '"tests_readme_present": true', '"tests_readme_present": false', "test_fsmount_manifest:survey_summary.tests_readme_present:expected=True:actual=False"),
            (TEST_FSMOUNT_MANIFEST, '"id": "phase4-test-fsmount-zig-sample",\n      "status": "ready_next"', '"id": "phase4-test-fsmount-zig-sample",\n      "status": "starter_landed"', "test_fsmount_manifest:gaps.4.status:expected='ready_next'"),
            (PHASE4_BUILD, TEST_FSMOUNT_SHARED_BUILD_REPLAY, "phase4-test-fsmount-gap-survey-tests", f"phase4_build_marker:{TEST_FSMOUNT_SHARED_BUILD_REPLAY}"),
            (PERF_MANIFEST, f'"shared_lab_and_ci_matrix_anchor": "{PERF_MATRIX_ANCHOR}"', '"shared_lab_and_ci_matrix_anchor": "Documentation/zigux/phase4-gate-evidence.md#exact-readback-evidence"', f"perf_manifest:shared_lab_and_ci_matrix_anchor:expected='{PERF_MATRIX_ANCHOR}'"),
            (PERF_MANIFEST, '"shared_ci_perf_promotion_status": "pending"', '"shared_ci_perf_promotion_status": "approved"', "perf_manifest:shared_ci_perf_promotion_status:expected='pending'"),
            (PERF_MANIFEST, '"gate_rollback_owner": "ABI and Runtime Team"', '"gate_rollback_owner": "Validation and Perf Team"', "perf_manifest:atomic64.gate_rollback_owner:expected='ABI and Runtime Team'"),
            (PERF_MANIFEST, '"benchmark_command": "zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig"', '"benchmark_command": "zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig"', "perf_manifest:bitmap.benchmark_command:expected='zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig'"),
            (PERF_MANIFEST, '"status": "shared CI perf promotion pending",\n    "owner": "Validation and Perf Team"', '"status": "shared CI perf promotion pending",\n    "owner": "Shared Subsystems Pod"', "perf_manifest:promotion_decision.owner:expected='Validation and Perf Team'"),
        )
        for rel, old, new, expected_prefix in variants:
            write_fixture_tree(root)
            target = root / rel
            write_text(target, replace_once(read_text(target), old, new))
            if not expect_failure(root, expected_prefix):
                print("PHASE4_REMAINING_GAP_MATRIX_SELF_TEST=fail")
                print(f"missing expected failure prefix: {expected_prefix}")
                return 1
            cases += 1

        for rel in (MEASURABILITY_GAP_NOTE, KPROBE_NOTE, KPROBE_SURVEY, TEST_FSMOUNT_SURVEY, PHASE4_BUILD):
            write_fixture_tree(root)
            (root / rel).unlink()
            if not expect_failure(root, f"file:{rel.as_posix()}"):
                print("PHASE4_REMAINING_GAP_MATRIX_SELF_TEST=fail")
                print(f"missing file case did not fail closed: {rel.as_posix()}")
                return 1
            cases += 1

        for rel, label in ((KPROBE_MANIFEST, "kprobe_manifest"), (TEST_FSMOUNT_MANIFEST, "test_fsmount_manifest"), (PERF_MANIFEST, "perf_manifest")):
            write_fixture_tree(root)
            write_text(root / rel, "{")
            if not expect_failure(root, f"{label}:decode:"):
                print("PHASE4_REMAINING_GAP_MATRIX_SELF_TEST=fail")
                print(f"broken JSON case did not fail closed: {label}")
                return 1
            cases += 1

        if cases != EXPECTED_SELF_TEST_CASE_COUNT:
            print("PHASE4_REMAINING_GAP_MATRIX_SELF_TEST=fail")
            print(f"expected {EXPECTED_SELF_TEST_CASE_COUNT} self-test cases, saw {cases}")
            return 1

        print("PHASE4_REMAINING_GAP_MATRIX_SELF_TEST=pass")
        print(f"PHASE4_REMAINING_GAP_MATRIX_SELF_TEST_CASE_COUNT={cases}")
        return 0


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    root = Path(args.root).resolve()
    missing = validate_root(root)
    if missing:
        print("PHASE4_REMAINING_GAP_MATRIX=fail")
        for item in missing:
            print(item)
        return 1

    print("PHASE4_REMAINING_GAP_MATRIX=pass")
    print("PHASE4_REMAINING_GAP_MATRIX_PACKET_COUNT=6")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
