#!/usr/bin/env python3
"""Guard the bounded Phase 4 remaining-gap matrix packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

MATRIX = Path("Documentation/zigux/phase4-validation-matrix.md")
KPROBE_NOTE = Path("Documentation/zigux/phase4-kprobe-example-gap-survey.md")
TEST_FSMOUNT_NOTE = Path("Documentation/zigux/phase4-test-fsmount-gap-survey.md")
KPROBE_MANIFEST = Path("zigux/tests/phase4_kprobe_example_manifest.json")
TEST_FSMOUNT_MANIFEST = Path("zigux/tests/phase4_test_fsmount_manifest.json")
PERF_MANIFEST = Path("zigux/tests/phase4_perf_baseline_manifest.json")

EXPECTED_SELF_TEST_CASE_COUNT = 16

MATRIX_MARKERS = (
    "`scripts/zigux/check-phase4-remaining-gap-matrix.py`",
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
)

KPROBE_NOTE_MARKERS = (
    "PHASE4_KPROBE_STATUS=parked_gap_packet_landed",
    "PHASE4_KPROBE_LANE_KEY=P4-L19",
    "PHASE4_KPROBE_C_ANCHOR=samples/kprobes/kprobe_example.c",
    "PHASE4_KPROBE_CURRENT_LINUX_REPLAY=make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m",
    "PHASE4_KPROBE_LOCAL_LAB_REPLAY=make -C zigux phase4-kprobe-example-survey",
    "PHASE4_KPROBE_LOCAL_SURVEY_WRAPPER=make -C zigux phase4-kprobe-example-survey",
    "PHASE4_KPROBE_BOOTSTRAP_CI_POSTURE=reviewability_only_local_survey_wrapper_not_on_shared_phase4_test_or_bootstrap_workflow",
    "PHASE4_KPROBE_VALIDATION_ENTRYPOINT=zig test zigux/tests/phase4_kprobe_example_survey.zig",
    "PHASE4_KPROBE_OWNER=Validation and Perf Team",
    "PHASE4_KPROBE_ROLLBACK_OWNER=Validation and Perf Team",
    "PHASE4_REVERSIBLE_DELIVERY_EVIDENCE=keep the dedicated parked survey packet, the explicit local_lab_replay marker, the local survey wrapper, the explicit bootstrap-CI posture, the direct validation entrypoint, and the absent Zig starter boundary explicit until a later bounded validator or starter lane intentionally widens this surface",
    "Current `master` still does not ship `samples/zigux/kprobe_example.zig`.",
)

TEST_FSMOUNT_NOTE_MARKERS = (
    "PHASE4_TEST_FSMOUNT_STATUS=parked_gap_packet_landed",
    "PHASE4_TEST_FSMOUNT_LANE_KEY=P4-L19",
    "PHASE4_TEST_FSMOUNT_C_ANCHOR=samples/vfs/test-fsmount.c",
    "PHASE4_TEST_FSMOUNT_CURRENT_LINUX_REPLAY=make M=samples/vfs",
    "PHASE4_TEST_FSMOUNT_LOCAL_SURVEY_WRAPPER=zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
    "PHASE4_TEST_FSMOUNT_LINUX_STYLE_SURVEY_WRAPPER=make -C zigux phase4-test-fsmount-survey",
    "PHASE4_TEST_FSMOUNT_BOOTSTRAP_CI_POSTURE=reviewability_only_local_survey_wrappers_not_on_shared_phase4_test_or_bootstrap_workflow",
    "PHASE4_TEST_FSMOUNT_SHARED_LAB_AND_CI_MATRIX_ANCHOR=Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix",
    "PHASE4_TEST_FSMOUNT_THRESHOLD_POSTURE=reviewability_only_no_perf_threshold",
    "PHASE4_TEST_FSMOUNT_OWNER=Validation and Perf Team",
    "PHASE4_TEST_FSMOUNT_ROLLBACK_OWNER=Validation and Perf Team",
    "PHASE4_REVERSIBLE_DELIVERY_EVIDENCE=keep the dedicated parked survey packet, both local survey wrappers, the explicit bootstrap-CI posture, the explicit no-perf-threshold posture, and the absent Zig starter boundary explicit until a later bounded validator or starter lane intentionally widens this surface",
    "Current `master` still does not ship `samples/zigux/test_fsmount.zig`.",
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
        (("shared_build_replay",), "phase4-kprobe-example-survey-tests"),
        (("threshold_posture",), "c_anchor_only_until_kprobe_example_starter_lands"),
        (("survey_summary", "kprobe_makefile_replay_present"), True),
        (("survey_summary", "zig_sample_present"), False),
        (("survey_summary", "phase4_build_present"), True),
        (("survey_summary", "phase4_validation_matrix_present"), True),
        (("survey_summary", "phase4_gate_evidence_present"), True),
        (("gaps", 3, "id"), "phase4-kprobe-example-shared-validator-promotion"),
        (("gaps", 3, "status"), "ready_next"),
        (("gaps", 4, "id"), "phase4-kprobe-example-zig-sample"),
        (("gaps", 4, "status"), "ready_next"),
    )
    for path, expected in expected_values:
        expect_json_value(payload, path, expected, missing, "kprobe_manifest")


def validate_test_fsmount_manifest(payload: dict[str, object], missing: list[str]) -> None:
    expected_values = (
        (("lane_key",), "P4-L19"),
        (("phase",), "Phase 4"),
        (("c_anchor",), "samples/vfs/test-fsmount.c"),
        (("current_linux_replay",), "make M=samples/vfs"),
        (("dedicated_local_survey_wrapper",), "zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig"),
        (("dedicated_linux_style_survey_wrapper",), "make -C zigux phase4-test-fsmount-survey"),
        (("bootstrap_ci_posture",), "reviewability_only_local_survey_wrappers_not_on_shared_phase4_test_or_bootstrap_workflow"),
        (("shared_lab_and_ci_matrix_anchor",), "Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix"),
        (("validation_entrypoint",), "zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig"),
        (("owner",), "Validation and Perf Team"),
        (("rollback_owner",), "Validation and Perf Team"),
        (("current_measurable_status",), "absent_on_current_master_but_reviewable_through_the_dedicated_gap_packet_without_claiming_a_shipped_zig_starter"),
        (("threshold_posture",), "reviewability_only_no_perf_threshold"),
    )
    for path, expected in expected_values:
        expect_json_value(payload, path, expected, missing, "test_fsmount_manifest")


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
        (("promotion_decision", "status"), "shared CI perf promotion pending"),
        (("promotion_decision", "owner"), "Validation and Perf Team"),
    )
    for path, expected in expected_values:
        expect_json_value(payload, path, expected, missing, "perf_manifest")


def validate_root(root: Path) -> list[str]:
    missing: list[str] = []
    required = (
        MATRIX,
        KPROBE_NOTE,
        TEST_FSMOUNT_NOTE,
        KPROBE_MANIFEST,
        TEST_FSMOUNT_MANIFEST,
        PERF_MANIFEST,
    )
    for path in required:
        if not (root / path).is_file():
            missing.append(f"file:{path.as_posix()}")
    if missing:
        return missing

    require_markers(read_text(root / MATRIX), MATRIX_MARKERS, "matrix_marker", missing)
    require_markers(read_text(root / KPROBE_NOTE), KPROBE_NOTE_MARKERS, "kprobe_note_marker", missing)
    require_markers(read_text(root / TEST_FSMOUNT_NOTE), TEST_FSMOUNT_NOTE_MARKERS, "test_fsmount_note_marker", missing)

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
    write_text(
        root / MATRIX,
        """# Phase 4 Validation Matrix
`scripts/zigux/check-phase4-remaining-gap-matrix.py`
`Documentation/zigux/phase4-kprobe-example-gap-survey.md`
`zigux/tests/phase4_kprobe_example_manifest.json`
`zigux/tests/phase4_kprobe_example_survey.zig`
`make -C zigux phase4-kprobe-example-survey`
c_anchor_only_until_kprobe_example_starter_lands
`Documentation/zigux/phase4-test-fsmount-gap-survey.md`
`zigux/tests/phase4_test_fsmount_manifest.json`
`zigux/tests/phase4_test_fsmount_survey.zig`
`zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`
`make -C zigux phase4-test-fsmount-survey`
reviewability_only_no_perf_threshold
`zigux/tests/phase4_perf_baseline_manifest.json`
shared CI perf promotion pending
`python3 scripts/zigux/check-phase4-perf-baseline-packet.py --self-test` then `python3 scripts/zigux/check-phase4-perf-baseline-packet.py`
Validation and Perf Team owning that policy decision
""",
    )
    write_text(
        root / KPROBE_NOTE,
        """PHASE4_KPROBE_STATUS=parked_gap_packet_landed
PHASE4_KPROBE_LANE_KEY=P4-L19
PHASE4_KPROBE_C_ANCHOR=samples/kprobes/kprobe_example.c
PHASE4_KPROBE_CURRENT_LINUX_REPLAY=make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m
PHASE4_KPROBE_LOCAL_LAB_REPLAY=make -C zigux phase4-kprobe-example-survey
PHASE4_KPROBE_LOCAL_SURVEY_WRAPPER=make -C zigux phase4-kprobe-example-survey
PHASE4_KPROBE_BOOTSTRAP_CI_POSTURE=reviewability_only_local_survey_wrapper_not_on_shared_phase4_test_or_bootstrap_workflow
PHASE4_KPROBE_VALIDATION_ENTRYPOINT=zig test zigux/tests/phase4_kprobe_example_survey.zig
PHASE4_KPROBE_OWNER=Validation and Perf Team
PHASE4_KPROBE_ROLLBACK_OWNER=Validation and Perf Team
PHASE4_REVERSIBLE_DELIVERY_EVIDENCE=keep the dedicated parked survey packet, the explicit local_lab_replay marker, the local survey wrapper, the explicit bootstrap-CI posture, the direct validation entrypoint, and the absent Zig starter boundary explicit until a later bounded validator or starter lane intentionally widens this surface
Current `master` still does not ship `samples/zigux/kprobe_example.zig`.
""",
    )
    write_text(
        root / TEST_FSMOUNT_NOTE,
        """PHASE4_TEST_FSMOUNT_STATUS=parked_gap_packet_landed
PHASE4_TEST_FSMOUNT_LANE_KEY=P4-L19
PHASE4_TEST_FSMOUNT_C_ANCHOR=samples/vfs/test-fsmount.c
PHASE4_TEST_FSMOUNT_CURRENT_LINUX_REPLAY=make M=samples/vfs
PHASE4_TEST_FSMOUNT_LOCAL_SURVEY_WRAPPER=zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig
PHASE4_TEST_FSMOUNT_LINUX_STYLE_SURVEY_WRAPPER=make -C zigux phase4-test-fsmount-survey
PHASE4_TEST_FSMOUNT_BOOTSTRAP_CI_POSTURE=reviewability_only_local_survey_wrappers_not_on_shared_phase4_test_or_bootstrap_workflow
PHASE4_TEST_FSMOUNT_SHARED_LAB_AND_CI_MATRIX_ANCHOR=Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix
PHASE4_TEST_FSMOUNT_THRESHOLD_POSTURE=reviewability_only_no_perf_threshold
PHASE4_TEST_FSMOUNT_OWNER=Validation and Perf Team
PHASE4_TEST_FSMOUNT_ROLLBACK_OWNER=Validation and Perf Team
PHASE4_REVERSIBLE_DELIVERY_EVIDENCE=keep the dedicated parked survey packet, both local survey wrappers, the explicit bootstrap-CI posture, the explicit no-perf-threshold posture, and the absent Zig starter boundary explicit until a later bounded validator or starter lane intentionally widens this surface
Current `master` still does not ship `samples/zigux/test_fsmount.zig`.
""",
    )
    write_text(
        root / KPROBE_MANIFEST,
        """{
  "lane_key": "P4-L19",
  "phase": "Phase 4",
  "owner": "Validation and Perf Team",
  "rollback_owner": "Validation and Perf Team",
  "anchor": "samples/kprobes/kprobe_example.c",
  "roadmap_destinations": ["samples/zigux/kprobe_example.zig"],
  "current_replay": "make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m",
  "isolated_survey_replay": "zig build phase4-kprobe-example-survey --build-file zigux/tests/phase4_build.zig",
  "shared_build_replay": "phase4-kprobe-example-survey-tests",
  "threshold_posture": "c_anchor_only_until_kprobe_example_starter_lands",
  "survey_summary": {
    "kprobe_makefile_replay_present": true,
    "zig_sample_present": false,
    "phase4_build_present": true,
    "phase4_validation_matrix_present": true,
    "phase4_gate_evidence_present": true
  },
  "gaps": [
    {},
    {},
    {},
    { "id": "phase4-kprobe-example-shared-validator-promotion", "status": "ready_next" },
    { "id": "phase4-kprobe-example-zig-sample", "status": "ready_next" }
  ]
}
""",
    )
    write_text(
        root / TEST_FSMOUNT_MANIFEST,
        """{
  "lane_key": "P4-L19",
  "phase": "Phase 4",
  "c_anchor": "samples/vfs/test-fsmount.c",
  "current_linux_replay": "make M=samples/vfs",
  "dedicated_local_survey_wrapper": "zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
  "dedicated_linux_style_survey_wrapper": "make -C zigux phase4-test-fsmount-survey",
  "bootstrap_ci_posture": "reviewability_only_local_survey_wrappers_not_on_shared_phase4_test_or_bootstrap_workflow",
  "shared_lab_and_ci_matrix_anchor": "Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix",
  "validation_entrypoint": "zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
  "owner": "Validation and Perf Team",
  "rollback_owner": "Validation and Perf Team",
  "current_measurable_status": "absent_on_current_master_but_reviewable_through_the_dedicated_gap_packet_without_claiming_a_shipped_zig_starter",
  "threshold_posture": "reviewability_only_no_perf_threshold"
}
""",
    )
    write_text(
        root / PERF_MANIFEST,
        """{
  "lane_key": "P4-L20",
  "phase": "Phase 4",
  "owner": "Validation and Perf Team",
  "rollback_owner": "Validation and Perf Team",
  "decision_owner": "Validation and Perf Team",
  "coordination_owners": ["ABI and Runtime Team", "Shared Subsystems Pod"],
  "shared_ci_perf_promotion_status": "pending",
  "local_only_posture_note": "The dedicated perf-baseline survey keeps approved local benchmark commands and approved local-only acceptable limits explicit while shared CI perf promotion remains intentionally pending.",
  "promotion_decision": {
    "status": "shared CI perf promotion pending",
    "owner": "Validation and Perf Team"
  }
}
""",
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
            (MATRIX, "`python3 scripts/zigux/check-phase4-perf-baseline-packet.py --self-test` then `python3 scripts/zigux/check-phase4-perf-baseline-packet.py`", "`python3 scripts/zigux/check-phase4-perf-baseline-packet.py`", "matrix_marker:`python3 scripts/zigux/check-phase4-perf-baseline-packet.py --self-test` then `python3 scripts/zigux/check-phase4-perf-baseline-packet.py`"),
            (MATRIX, "Validation and Perf Team owning that policy decision", "ABI and Runtime Team owning that policy decision", "matrix_marker:Validation and Perf Team owning that policy decision"),
            (KPROBE_NOTE, "PHASE4_KPROBE_LOCAL_LAB_REPLAY=make -C zigux phase4-kprobe-example-survey", "PHASE4_KPROBE_LOCAL_LAB_REPLAY=make -C zigux phase4-kprobe-lab-survey", "kprobe_note_marker:PHASE4_KPROBE_LOCAL_LAB_REPLAY=make -C zigux phase4-kprobe-example-survey"),
            (KPROBE_NOTE, "PHASE4_KPROBE_LOCAL_SURVEY_WRAPPER=make -C zigux phase4-kprobe-example-survey", "PHASE4_KPROBE_LOCAL_SURVEY_WRAPPER=make -C zigux phase4-kprobe-gap-survey", "kprobe_note_marker:PHASE4_KPROBE_LOCAL_SURVEY_WRAPPER=make -C zigux phase4-kprobe-example-survey"),
            (KPROBE_NOTE, "PHASE4_KPROBE_BOOTSTRAP_CI_POSTURE=reviewability_only_local_survey_wrapper_not_on_shared_phase4_test_or_bootstrap_workflow", "PHASE4_KPROBE_BOOTSTRAP_CI_POSTURE=shared_phase4_test_route", "kprobe_note_marker:PHASE4_KPROBE_BOOTSTRAP_CI_POSTURE=reviewability_only_local_survey_wrapper_not_on_shared_phase4_test_or_bootstrap_workflow"),
            (KPROBE_MANIFEST, "\"phase4_build_present\": true", "\"phase4_build_present\": false", "kprobe_manifest:survey_summary.phase4_build_present:expected=True"),
            (KPROBE_MANIFEST, "\"threshold_posture\": \"c_anchor_only_until_kprobe_example_starter_lands\"", "\"threshold_posture\": \"reviewability_only_no_perf_threshold\"", "kprobe_manifest:threshold_posture:expected='c_anchor_only_until_kprobe_example_starter_lands'"),
            (TEST_FSMOUNT_NOTE, "PHASE4_TEST_FSMOUNT_THRESHOLD_POSTURE=reviewability_only_no_perf_threshold", "PHASE4_TEST_FSMOUNT_THRESHOLD_POSTURE=approved_local_only", "test_fsmount_note_marker:PHASE4_TEST_FSMOUNT_THRESHOLD_POSTURE=reviewability_only_no_perf_threshold"),
            (TEST_FSMOUNT_NOTE, "PHASE4_TEST_FSMOUNT_BOOTSTRAP_CI_POSTURE=reviewability_only_local_survey_wrappers_not_on_shared_phase4_test_or_bootstrap_workflow", "PHASE4_TEST_FSMOUNT_BOOTSTRAP_CI_POSTURE=shared_phase4_test_route", "test_fsmount_note_marker:PHASE4_TEST_FSMOUNT_BOOTSTRAP_CI_POSTURE=reviewability_only_local_survey_wrappers_not_on_shared_phase4_test_or_bootstrap_workflow"),
            (TEST_FSMOUNT_NOTE, "PHASE4_TEST_FSMOUNT_SHARED_LAB_AND_CI_MATRIX_ANCHOR=Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix", "PHASE4_TEST_FSMOUNT_SHARED_LAB_AND_CI_MATRIX_ANCHOR=Documentation/zigux/phase4-gate-evidence.md", "test_fsmount_note_marker:PHASE4_TEST_FSMOUNT_SHARED_LAB_AND_CI_MATRIX_ANCHOR=Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix"),
            (TEST_FSMOUNT_MANIFEST, "\"dedicated_linux_style_survey_wrapper\": \"make -C zigux phase4-test-fsmount-survey\"", "\"dedicated_linux_style_survey_wrapper\": \"make -C zigux phase4-test-fsmount-gap\"", "test_fsmount_manifest:dedicated_linux_style_survey_wrapper:expected='make -C zigux phase4-test-fsmount-survey'"),
            (PERF_MANIFEST, "\"shared_ci_perf_promotion_status\": \"pending\"", "\"shared_ci_perf_promotion_status\": \"approved\"", "perf_manifest:shared_ci_perf_promotion_status:expected='pending'"),
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

        write_fixture_tree(root)
        (root / KPROBE_NOTE).unlink()
        if not expect_failure(root, f"file:{KPROBE_NOTE.as_posix()}"):
            print("PHASE4_REMAINING_GAP_MATRIX_SELF_TEST=fail")
            print("missing kprobe note case did not fail closed")
            return 1
        cases += 1

        write_fixture_tree(root)
        (root / PERF_MANIFEST).unlink()
        if not expect_failure(root, f"file:{PERF_MANIFEST.as_posix()}"):
            print("PHASE4_REMAINING_GAP_MATRIX_SELF_TEST=fail")
            print("missing perf manifest case did not fail closed")
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
