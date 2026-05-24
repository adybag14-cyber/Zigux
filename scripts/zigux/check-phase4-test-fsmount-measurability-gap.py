#!/usr/bin/env python3
"""Survey the remaining Phase 4 test_fsmount measurability gap."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

NOTE = Path("Documentation/zigux/phase4-test-fsmount-gap-survey.md")
MANIFEST = Path("zigux/tests/phase4_test_fsmount_manifest.json")
MATRIX = Path("Documentation/zigux/phase4-validation-matrix.md")
GATE_EVIDENCE = Path("Documentation/zigux/phase4-gate-evidence.md")

EXPECTED_SELF_TEST_CASE_COUNT = 6

EXPECTED_NOTE_MARKERS = (
    "PHASE4_TEST_FSMOUNT_STATUS=parked_gap_packet_landed",
    "PHASE4_TEST_FSMOUNT_LANE_KEY=P4-L19",
    "PHASE4_TEST_FSMOUNT_C_ANCHOR=samples/vfs/test-fsmount.c",
    "PHASE4_TEST_FSMOUNT_CURRENT_LINUX_REPLAY=make M=samples/vfs",
    "PHASE4_TEST_FSMOUNT_LOCAL_LAB_REPLAY=zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
    "PHASE4_TEST_FSMOUNT_LOCAL_SURVEY_WRAPPER=zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
    "PHASE4_TEST_FSMOUNT_LINUX_STYLE_SURVEY_WRAPPER=make -C zigux phase4-test-fsmount-survey",
    "PHASE4_TEST_FSMOUNT_BOOTSTRAP_CI_POSTURE=reviewability_only_local_survey_wrappers_not_on_shared_phase4_test_or_bootstrap_workflow",
    "PHASE4_TEST_FSMOUNT_SHARED_LAB_AND_CI_MATRIX_ANCHOR=Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix",
    "PHASE4_TEST_FSMOUNT_VALIDATION_ENTRYPOINT=zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
    "PHASE4_TEST_FSMOUNT_OWNER=Validation and Perf Team",
    "PHASE4_TEST_FSMOUNT_ROLLBACK_OWNER=Validation and Perf Team",
    "PHASE4_TEST_FSMOUNT_THRESHOLD_POSTURE=reviewability_only_no_perf_threshold",
    "Current `master` still does not ship `samples/zigux/test_fsmount.zig`.",
)

EXPECTED_MATRIX_MARKERS = (
    "* current replay path: `make M=samples/vfs`",
    "* dedicated local survey wrapper: `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`",
    "* dedicated Linux-style survey wrapper: `make -C zigux phase4-test-fsmount-survey`",
    "* validation entrypoint: `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`",
    "* survey owner: `Validation and Perf Team`",
    "* rollback owner: `Validation and Perf Team`",
    "reviewability_only_no_perf_threshold",
)

EXPECTED_GATE_EVIDENCE_MARKERS = (
    "Documentation/zigux/phase4-test-fsmount-gap-survey.md",
    "zigux/tests/phase4_test_fsmount_manifest.json",
    "zigux/tests/phase4_test_fsmount_survey.zig",
    "zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
    "make -C zigux phase4-test-fsmount-survey",
    "reviewability_only_no_perf_threshold",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", help="repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="run built-in fixture tests")
    return parser.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def require_markers(text: str, markers: tuple[str, ...], label: str, issues: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            issues.append(f"{label}:{marker}")


def validate_root(root: Path) -> list[str]:
    issues: list[str] = []
    required = (NOTE, MANIFEST, MATRIX, GATE_EVIDENCE)
    for path in required:
        if not (root / path).is_file():
            issues.append(f"file:{path.as_posix()}")
    if issues:
        return issues

    note_text = read_text(root / NOTE)
    matrix_text = read_text(root / MATRIX)
    gate_evidence_text = read_text(root / GATE_EVIDENCE)
    manifest_text = read_text(root / MANIFEST)

    require_markers(note_text, EXPECTED_NOTE_MARKERS, "note", issues)
    require_markers(matrix_text, EXPECTED_MATRIX_MARKERS, "matrix", issues)
    require_markers(gate_evidence_text, EXPECTED_GATE_EVIDENCE_MARKERS, "gate_evidence", issues)

    try:
        payload = json.loads(manifest_text)
    except json.JSONDecodeError as exc:
        issues.append(f"manifest:decode:{exc.msg}")
        return issues

    if payload.get("lane_key") != "P4-L19":
        issues.append(f"manifest:lane_key:{payload.get('lane_key')!r}")
    if payload.get("phase") != "Phase 4":
        issues.append(f"manifest:phase:{payload.get('phase')!r}")
    if payload.get("c_anchor") != "samples/vfs/test-fsmount.c":
        issues.append(f"manifest:c_anchor:{payload.get('c_anchor')!r}")
    if payload.get("current_linux_replay") != "make M=samples/vfs":
        issues.append(f"manifest:current_linux_replay:{payload.get('current_linux_replay')!r}")
    if payload.get("local_lab_replay") != "zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig":
        issues.append("manifest:local_lab_replay")
    if payload.get("dedicated_local_survey_wrapper") != "zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig":
        issues.append("manifest:dedicated_local_survey_wrapper")
    if payload.get("dedicated_linux_style_survey_wrapper") != "make -C zigux phase4-test-fsmount-survey":
        issues.append("manifest:dedicated_linux_style_survey_wrapper")
    if payload.get("bootstrap_ci_posture") != "reviewability_only_local_survey_wrappers_not_on_shared_phase4_test_or_bootstrap_workflow":
        issues.append("manifest:bootstrap_ci_posture")
    if payload.get("shared_lab_and_ci_matrix_anchor") != "Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix":
        issues.append("manifest:shared_lab_and_ci_matrix_anchor")
    if payload.get("validation_entrypoint") != "zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig":
        issues.append("manifest:validation_entrypoint")
    if payload.get("owner") != "Validation and Perf Team":
        issues.append("manifest:owner")
    if payload.get("rollback_owner") != "Validation and Perf Team":
        issues.append("manifest:rollback_owner")
    if payload.get("current_measurable_status") != "absent_on_current_master_but_reviewable_through_the_dedicated_gap_packet_without_claiming_a_shipped_zig_starter":
        issues.append("manifest:current_measurable_status")
    if payload.get("threshold_posture") != "reviewability_only_no_perf_threshold":
        issues.append("manifest:threshold_posture")
    if payload.get("reversible_delivery_evidence") != "PHASE4_REVERSIBLE_DELIVERY_EVIDENCE=keep the dedicated parked survey packet, both local survey wrappers, the explicit bootstrap-CI posture, the explicit no-perf-threshold posture, and the absent Zig starter boundary explicit until a later bounded validator or starter lane intentionally widens this surface":
        issues.append("manifest:reversible_delivery_evidence")
    if payload.get("next_bounded_evidence_step") != "keep the dedicated parked survey packet adjacent to the shared gate-evidence note, the shared Phase 4 exact-readback packet, the validation matrix, the explicit bootstrap-CI posture, the explicit local lab replay marker, the explicit reviewability-only no-perf-threshold posture, the dedicated local `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig` survey wrapper, and the matching Linux-style `make -C zigux phase4-test-fsmount-survey` wrapper until a later bounded lane intentionally promotes the validator surface or lands the Zig starter":
        issues.append("manifest:next_bounded_evidence_step")

    return issues


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise ValueError(f"missing replacement target: {old!r}")
    return text.replace(old, new, 1)


def write_fixture_tree(root: Path) -> None:
    write_text(
        root / NOTE,
        "\n".join(
            [
                "# Phase 4 test_fsmount Gap Survey",
                "PHASE4_TEST_FSMOUNT_STATUS=parked_gap_packet_landed",
                "PHASE4_TEST_FSMOUNT_LANE_KEY=P4-L19",
                "PHASE4_TEST_FSMOUNT_C_ANCHOR=samples/vfs/test-fsmount.c",
                "PHASE4_TEST_FSMOUNT_CURRENT_LINUX_REPLAY=make M=samples/vfs",
                "PHASE4_TEST_FSMOUNT_LOCAL_LAB_REPLAY=zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
                "PHASE4_TEST_FSMOUNT_LOCAL_SURVEY_WRAPPER=zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
                "PHASE4_TEST_FSMOUNT_LINUX_STYLE_SURVEY_WRAPPER=make -C zigux phase4-test-fsmount-survey",
                "PHASE4_TEST_FSMOUNT_BOOTSTRAP_CI_POSTURE=reviewability_only_local_survey_wrappers_not_on_shared_phase4_test_or_bootstrap_workflow",
                "PHASE4_TEST_FSMOUNT_SHARED_LAB_AND_CI_MATRIX_ANCHOR=Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix",
                "PHASE4_TEST_FSMOUNT_VALIDATION_ENTRYPOINT=zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
                "PHASE4_TEST_FSMOUNT_OWNER=Validation and Perf Team",
                "PHASE4_TEST_FSMOUNT_ROLLBACK_OWNER=Validation and Perf Team",
                "PHASE4_TEST_FSMOUNT_THRESHOLD_POSTURE=reviewability_only_no_perf_threshold",
                "Current `master` still does not ship `samples/zigux/test_fsmount.zig`.",
                "",
            ]
        ),
    )
    write_text(
        root / MANIFEST,
        json.dumps(
            {
                "lane_key": "P4-L19",
                "phase": "Phase 4",
                "c_anchor": "samples/vfs/test-fsmount.c",
                "current_linux_replay": "make M=samples/vfs",
                "local_lab_replay": "zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
                "dedicated_local_survey_wrapper": "zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
                "dedicated_linux_style_survey_wrapper": "make -C zigux phase4-test-fsmount-survey",
                "bootstrap_ci_posture": "reviewability_only_local_survey_wrappers_not_on_shared_phase4_test_or_bootstrap_workflow",
                "shared_lab_and_ci_matrix_anchor": "Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix",
                "validation_entrypoint": "zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
                "owner": "Validation and Perf Team",
                "rollback_owner": "Validation and Perf Team",
                "current_measurable_status": "absent_on_current_master_but_reviewable_through_the_dedicated_gap_packet_without_claiming_a_shipped_zig_starter",
                "threshold_posture": "reviewability_only_no_perf_threshold",
                "reversible_delivery_evidence": "PHASE4_REVERSIBLE_DELIVERY_EVIDENCE=keep the dedicated parked survey packet, both local survey wrappers, the explicit bootstrap-CI posture, the explicit no-perf-threshold posture, and the absent Zig starter boundary explicit until a later bounded validator or starter lane intentionally widens this surface",
                "next_bounded_evidence_step": "keep the dedicated parked survey packet adjacent to the shared gate-evidence note, the shared Phase 4 exact-readback packet, the validation matrix, the explicit bootstrap-CI posture, the explicit local lab replay marker, the explicit reviewability-only no-perf-threshold posture, the dedicated local `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig` survey wrapper, and the matching Linux-style `make -C zigux phase4-test-fsmount-survey` wrapper until a later bounded lane intentionally promotes the validator surface or lands the Zig starter",
            },
            indent=2,
        )
        + "\n",
    )
    write_text(root / MATRIX, "\n".join(EXPECTED_MATRIX_MARKERS) + "\n")
    write_text(root / GATE_EVIDENCE, "\n".join(EXPECTED_GATE_EVIDENCE_MARKERS) + "\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase4-test-fsmount-gap-") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture_tree(root)
        if validate_root(root):
            print("PHASE4_TEST_FSMOUNT_MEASURABILITY_GAP_SELF_TEST=fail")
            print("baseline fixture did not validate cleanly")
            return 1

        cases = 1

        variants = (
            (NOTE, "PHASE4_TEST_FSMOUNT_LOCAL_LAB_REPLAY=zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig", "PHASE4_TEST_FSMOUNT_LOCAL_LAB_REPLAY=zig build phase4-test-fsmount-gap-survey --build-file zigux/tests/phase4_build.zig", "note:PHASE4_TEST_FSMOUNT_LOCAL_LAB_REPLAY=zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig"),
            (NOTE, "Current `master` still does not ship `samples/zigux/test_fsmount.zig`.", "Current `master` now ships `samples/zigux/test_fsmount.zig`.", "note:Current `master` still does not ship `samples/zigux/test_fsmount.zig`."),
            (MANIFEST, '"threshold_posture": "reviewability_only_no_perf_threshold"', '"threshold_posture": "approved_local_only"', "manifest:threshold_posture"),
            (MANIFEST, '"next_bounded_evidence_step": "keep the dedicated parked survey packet adjacent to the shared gate-evidence note, the shared Phase 4 exact-readback packet, the validation matrix, the explicit bootstrap-CI posture, the explicit local lab replay marker, the explicit reviewability-only no-perf-threshold posture, the dedicated local `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig` survey wrapper, and the matching Linux-style `make -C zigux phase4-test-fsmount-survey` wrapper until a later bounded lane intentionally promotes the validator surface or lands the Zig starter"', '"next_bounded_evidence_step": "land the starter directly"', "manifest:next_bounded_evidence_step"),
            (MANIFEST, '"local_lab_replay": "zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig"', '"local_lab_replay": "make -C zigux phase4-test-fsmount-survey"', "manifest:local_lab_replay"),
        )
        for rel, old, new, prefix in variants:
            write_fixture_tree(root)
            target = root / rel
            write_text(target, replace_once(read_text(target), old, new))
            issues = validate_root(root)
            if not any(item.startswith(prefix) for item in issues):
                print("PHASE4_TEST_FSMOUNT_MEASURABILITY_GAP_SELF_TEST=fail")
                print(f"missing expected failure prefix: {prefix}")
                return 1
            cases += 1

        if cases != EXPECTED_SELF_TEST_CASE_COUNT:
            print("PHASE4_TEST_FSMOUNT_MEASURABILITY_GAP_SELF_TEST=fail")
            print(f"expected {EXPECTED_SELF_TEST_CASE_COUNT} cases, saw {cases}")
            return 1

        print("PHASE4_TEST_FSMOUNT_MEASURABILITY_GAP_SELF_TEST=pass")
        print(f"PHASE4_TEST_FSMOUNT_MEASURABILITY_GAP_SELF_TEST_CASE_COUNT={cases}")
        return 0


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    root = Path(args.root).resolve()
    issues = validate_root(root)
    if issues:
        print("PHASE4_TEST_FSMOUNT_MEASURABILITY_GAP=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE4_TEST_FSMOUNT_MEASURABILITY_GAP=pass")
    print("PHASE4_TEST_FSMOUNT_MEASURABILITY_GAP_STATUS=explicit_local_lab_replay_marker_landed_zig_starter_still_absent")
    print("PHASE4_TEST_FSMOUNT_MEASURABILITY_GAP_REQUIRED_FILE_COUNT=4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
