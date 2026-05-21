#!/usr/bin/env python3
"""Guard the bounded Phase 4 parked gap-survey note packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

KPROBE_NOTE = Path("Documentation/zigux/phase4-kprobe-example-gap-survey.md")
TEST_FSMOUNT_NOTE = Path("Documentation/zigux/phase4-test-fsmount-gap-survey.md")
KPROBE_MANIFEST = Path("zigux/tests/phase4_kprobe_example_manifest.json")
TEST_FSMOUNT_MANIFEST = Path("zigux/tests/phase4_test_fsmount_manifest.json")

EXPECTED_SELF_TEST_CASE_COUNT = 8
EXPECTED_SELF_TEST_CASES = (
    "baseline_round_trip",
    "missing_kprobe_phase_marker",
    "missing_kprobe_next_step_marker",
    "missing_test_fsmount_phase_marker",
    "missing_test_fsmount_next_step_marker",
    "kprobe_manifest_phase_drift",
    "test_fsmount_manifest_wrapper_drift",
    "test_fsmount_absent_starter_drift",
)

KPROBE_NOTE_MARKERS = (
    "PHASE4_KPROBE_STATUS=parked_gap_packet_landed",
    "PHASE4_KPROBE_LANE_KEY=P4-L19",
    "PHASE4_KPROBE_PHASE=Phase 4",
    "PHASE4_KPROBE_C_ANCHOR=samples/kprobes/kprobe_example.c",
    "PHASE4_KPROBE_CURRENT_LINUX_REPLAY=make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m",
    "PHASE4_KPROBE_LOCAL_LAB_REPLAY=make -C zigux phase4-kprobe-example-survey",
    "PHASE4_KPROBE_LOCAL_SURVEY_WRAPPER=make -C zigux phase4-kprobe-example-survey",
    "PHASE4_KPROBE_BOOTSTRAP_CI_POSTURE=reviewability_only_local_survey_wrapper_not_on_shared_phase4_test_or_bootstrap_workflow",
    "PHASE4_KPROBE_SHARED_LAB_AND_CI_MATRIX_ANCHOR=Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix",
    "PHASE4_KPROBE_VALIDATION_ENTRYPOINT=zig test zigux/tests/phase4_kprobe_example_survey.zig",
    "PHASE4_KPROBE_OWNER=Validation and Perf Team",
    "PHASE4_KPROBE_ROLLBACK_OWNER=Validation and Perf Team",
    "Current `master` still does not ship `samples/zigux/kprobe_example.zig`.",
)

TEST_FSMOUNT_NOTE_MARKERS = (
    "PHASE4_TEST_FSMOUNT_STATUS=parked_gap_packet_landed",
    "PHASE4_TEST_FSMOUNT_LANE_KEY=P4-L19",
    "PHASE4_TEST_FSMOUNT_PHASE=Phase 4",
    "PHASE4_TEST_FSMOUNT_C_ANCHOR=samples/vfs/test-fsmount.c",
    "PHASE4_TEST_FSMOUNT_CURRENT_LINUX_REPLAY=make M=samples/vfs",
    "PHASE4_TEST_FSMOUNT_LOCAL_SURVEY_WRAPPER=zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
    "PHASE4_TEST_FSMOUNT_LINUX_STYLE_SURVEY_WRAPPER=make -C zigux phase4-test-fsmount-survey",
    "PHASE4_TEST_FSMOUNT_BOOTSTRAP_CI_POSTURE=reviewability_only_local_survey_wrappers_not_on_shared_phase4_test_or_bootstrap_workflow",
    "PHASE4_TEST_FSMOUNT_SHARED_LAB_AND_CI_MATRIX_ANCHOR=Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix",
    "PHASE4_TEST_FSMOUNT_THRESHOLD_POSTURE=reviewability_only_no_perf_threshold",
    "PHASE4_TEST_FSMOUNT_OWNER=Validation and Perf Team",
    "PHASE4_TEST_FSMOUNT_ROLLBACK_OWNER=Validation and Perf Team",
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


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise ValueError(f"missing replacement target: {old!r}")
    return text.replace(old, new, 1)


def require_markers(text: str, markers: tuple[str, ...], label: str, failures: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            failures.append(f"{label}:{marker}")


def expect_json_value(payload: object, path: tuple[str | int, ...], expected: object, failures: list[str], label: str) -> None:
    current = payload
    for step in path:
        try:
            current = current[step]
        except (KeyError, IndexError, TypeError):
            failures.append(f"{label}:{'.'.join(str(part) for part in path)}:missing")
            return
    if current != expected:
        failures.append(
            f"{label}:{'.'.join(str(part) for part in path)}:expected={expected!r}:actual={current!r}"
        )


def validate_kprobe_manifest(payload: dict[str, object], failures: list[str]) -> None:
    expected = (
        (("lane_key",), "P4-L19"),
        (("phase",), "Phase 4"),
        (("owner",), "Validation and Perf Team"),
        (("rollback_owner",), "Validation and Perf Team"),
        (("anchor",), "samples/kprobes/kprobe_example.c"),
        (("current_replay",), "make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m"),
        (("isolated_survey_replay",), "zig build phase4-kprobe-example-survey --build-file zigux/tests/phase4_build.zig"),
        (("shared_build_replay",), "phase4-kprobe-example-survey-tests"),
        (("shared_lab_and_ci_matrix_anchor",), "Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix"),
        (("threshold_posture",), "c_anchor_only_until_kprobe_example_starter_lands"),
    )
    for path, value in expected:
        expect_json_value(payload, path, value, failures, "kprobe_manifest")


def validate_test_fsmount_manifest(payload: dict[str, object], failures: list[str]) -> None:
    expected = (
        (("lane_key",), "P4-L19"),
        (("phase",), "Phase 4"),
        (("owner",), "Validation and Perf Team"),
        (("rollback_owner",), "Validation and Perf Team"),
        (("c_anchor",), "samples/vfs/test-fsmount.c"),
        (("current_linux_replay",), "make M=samples/vfs"),
        (("dedicated_local_survey_wrapper",), "zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig"),
        (("dedicated_linux_style_survey_wrapper",), "make -C zigux phase4-test-fsmount-survey"),
        (("shared_build_replay",), "phase4-test-fsmount-survey-tests"),
        (("shared_lab_and_ci_matrix_anchor",), "Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix"),
        (("bootstrap_ci_posture",), "reviewability_only_local_survey_wrappers_not_on_shared_phase4_test_or_bootstrap_workflow"),
        (("threshold_posture",), "reviewability_only_no_perf_threshold"),
    )
    for path, value in expected:
        expect_json_value(payload, path, value, failures, "test_fsmount_manifest")


def validate_root(root: Path) -> list[str]:
    failures: list[str] = []
    files = (KPROBE_NOTE, TEST_FSMOUNT_NOTE, KPROBE_MANIFEST, TEST_FSMOUNT_MANIFEST)
    for rel in files:
        if not (root / rel).is_file():
            failures.append(f"file:{rel.as_posix()}")
    if failures:
        return failures

    kprobe_note_text = read_text(root / KPROBE_NOTE)
    test_fsmount_note_text = read_text(root / TEST_FSMOUNT_NOTE)
    require_markers(kprobe_note_text, KPROBE_NOTE_MARKERS, "kprobe_note_marker", failures)
    require_markers(test_fsmount_note_text, TEST_FSMOUNT_NOTE_MARKERS, "test_fsmount_note_marker", failures)

    try:
        kprobe_manifest = json.loads(read_text(root / KPROBE_MANIFEST))
    except json.JSONDecodeError as exc:
        failures.append(f"kprobe_manifest:decode:{exc.msg}")
    else:
        validate_kprobe_manifest(kprobe_manifest, failures)
        reversible = kprobe_manifest.get("reversible_delivery_evidence")
        next_step = kprobe_manifest.get("next_bounded_evidence_step")
        if not isinstance(reversible, str) or reversible not in kprobe_note_text:
            failures.append("kprobe_note_marker:manifest_reversible_delivery_evidence")
        if not isinstance(next_step, str) or next_step not in kprobe_note_text:
            failures.append("kprobe_note_marker:manifest_next_bounded_evidence_step")

    try:
        test_fsmount_manifest = json.loads(read_text(root / TEST_FSMOUNT_MANIFEST))
    except json.JSONDecodeError as exc:
        failures.append(f"test_fsmount_manifest:decode:{exc.msg}")
    else:
        validate_test_fsmount_manifest(test_fsmount_manifest, failures)
        reversible = test_fsmount_manifest.get("reversible_delivery_evidence")
        next_step = test_fsmount_manifest.get("next_bounded_evidence_step")
        if not isinstance(reversible, str) or reversible not in test_fsmount_note_text:
            failures.append("test_fsmount_note_marker:manifest_reversible_delivery_evidence")
        if not isinstance(next_step, str) or next_step not in test_fsmount_note_text:
            failures.append("test_fsmount_note_marker:manifest_next_bounded_evidence_step")

    return failures


def build_fixture_tree(root: Path) -> None:
    write_text(
        root / KPROBE_NOTE,
        """# Phase 4 kprobe_example Gap Survey
## Status
- `PHASE4_KPROBE_STATUS=parked_gap_packet_landed`
- `PHASE4_KPROBE_LANE_KEY=P4-L19`
- `PHASE4_KPROBE_PHASE=Phase 4`
- `PHASE4_KPROBE_C_ANCHOR=samples/kprobes/kprobe_example.c`
- `PHASE4_KPROBE_CURRENT_LINUX_REPLAY=make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m`
- `PHASE4_KPROBE_LOCAL_LAB_REPLAY=make -C zigux phase4-kprobe-example-survey`
- `PHASE4_KPROBE_LOCAL_SURVEY_WRAPPER=make -C zigux phase4-kprobe-example-survey`
- `PHASE4_KPROBE_BOOTSTRAP_CI_POSTURE=reviewability_only_local_survey_wrapper_not_on_shared_phase4_test_or_bootstrap_workflow`
- `PHASE4_KPROBE_SHARED_LAB_AND_CI_MATRIX_ANCHOR=Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix`
- `PHASE4_KPROBE_VALIDATION_ENTRYPOINT=zig test zigux/tests/phase4_kprobe_example_survey.zig`
- `PHASE4_KPROBE_OWNER=Validation and Perf Team`
- `PHASE4_KPROBE_ROLLBACK_OWNER=Validation and Perf Team`
- `PHASE4_REVERSIBLE_DELIVERY_EVIDENCE=keep the dedicated parked survey packet, the explicit local_lab_replay marker, the local survey wrapper, the explicit bootstrap-CI posture, the direct validation entrypoint, and the absent Zig starter boundary explicit until a later bounded starter lane intentionally widens this surface`

## Current Measurable Status
Current `master` still does not ship `samples/zigux/kprobe_example.zig`.

## Next Bounded Evidence Step
Keep this parked packet adjacent to the shared gate-evidence note, the shared Phase 4 exact-readback packet, the validation matrix, the explicit bootstrap-CI posture, the explicit local lab replay marker, the dedicated local `make -C zigux phase4-kprobe-example-survey` wrapper, and the direct `zig test zigux/tests/phase4_kprobe_example_survey.zig` validation entrypoint until a later bounded Phase 4 lane lands the actual Zig starter with an updated rollback-readiness contract.
""",
    )
    write_text(
        root / TEST_FSMOUNT_NOTE,
        """# Phase 4 test_fsmount Gap Survey
## Status
- `PHASE4_TEST_FSMOUNT_STATUS=parked_gap_packet_landed`
- `PHASE4_TEST_FSMOUNT_LANE_KEY=P4-L19`
- `PHASE4_TEST_FSMOUNT_PHASE=Phase 4`
- `PHASE4_TEST_FSMOUNT_C_ANCHOR=samples/vfs/test-fsmount.c`
- `PHASE4_TEST_FSMOUNT_CURRENT_LINUX_REPLAY=make M=samples/vfs`
- `PHASE4_TEST_FSMOUNT_LOCAL_SURVEY_WRAPPER=zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`
- `PHASE4_TEST_FSMOUNT_LINUX_STYLE_SURVEY_WRAPPER=make -C zigux phase4-test-fsmount-survey`
- `PHASE4_TEST_FSMOUNT_BOOTSTRAP_CI_POSTURE=reviewability_only_local_survey_wrappers_not_on_shared_phase4_test_or_bootstrap_workflow`
- `PHASE4_TEST_FSMOUNT_SHARED_LAB_AND_CI_MATRIX_ANCHOR=Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix`
- `PHASE4_TEST_FSMOUNT_THRESHOLD_POSTURE=reviewability_only_no_perf_threshold`
- `PHASE4_TEST_FSMOUNT_OWNER=Validation and Perf Team`
- `PHASE4_TEST_FSMOUNT_ROLLBACK_OWNER=Validation and Perf Team`
- `PHASE4_REVERSIBLE_DELIVERY_EVIDENCE=keep the dedicated parked survey packet, both local survey wrappers, the explicit bootstrap-CI posture, the explicit no-perf-threshold posture, and the absent Zig starter boundary explicit until a later bounded validator or starter lane intentionally widens this surface`

## Current Measurable Status
Current `master` still does not ship `samples/zigux/test_fsmount.zig`.

## Next Bounded Evidence Step
keep the dedicated parked survey packet adjacent to the shared gate-evidence note, the shared Phase 4 exact-readback packet, the validation matrix, the explicit bootstrap-CI posture, the explicit reviewability-only no-perf-threshold posture, the dedicated local `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig` survey wrapper, and the matching Linux-style `make -C zigux phase4-test-fsmount-survey` wrapper until a later bounded lane intentionally promotes the validator surface or lands the Zig starter
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
  "current_replay": "make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m",
  "isolated_survey_replay": "zig build phase4-kprobe-example-survey --build-file zigux/tests/phase4_build.zig",
  "shared_build_replay": "phase4-kprobe-example-survey-tests",
  "shared_lab_and_ci_matrix_anchor": "Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix",
  "threshold_posture": "c_anchor_only_until_kprobe_example_starter_lands",
  "reversible_delivery_evidence": "PHASE4_REVERSIBLE_DELIVERY_EVIDENCE=keep the dedicated parked survey packet, the explicit local_lab_replay marker, the local survey wrapper, the explicit bootstrap-CI posture, the direct validation entrypoint, and the absent Zig starter boundary explicit until a later bounded starter lane intentionally widens this surface",
  "next_bounded_evidence_step": "Keep this parked packet adjacent to the shared gate-evidence note, the shared Phase 4 exact-readback packet, the validation matrix, the explicit bootstrap-CI posture, the explicit local lab replay marker, the dedicated local `make -C zigux phase4-kprobe-example-survey` wrapper, and the direct `zig test zigux/tests/phase4_kprobe_example_survey.zig` validation entrypoint until a later bounded Phase 4 lane lands the actual Zig starter with an updated rollback-readiness contract."
}
""",
    )
    write_text(
        root / TEST_FSMOUNT_MANIFEST,
        """{
  "lane_key": "P4-L19",
  "phase": "Phase 4",
  "owner": "Validation and Perf Team",
  "rollback_owner": "Validation and Perf Team",
  "c_anchor": "samples/vfs/test-fsmount.c",
  "current_linux_replay": "make M=samples/vfs",
  "dedicated_local_survey_wrapper": "zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
  "dedicated_linux_style_survey_wrapper": "make -C zigux phase4-test-fsmount-survey",
  "shared_build_replay": "phase4-test-fsmount-survey-tests",
  "shared_lab_and_ci_matrix_anchor": "Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix",
  "bootstrap_ci_posture": "reviewability_only_local_survey_wrappers_not_on_shared_phase4_test_or_bootstrap_workflow",
  "threshold_posture": "reviewability_only_no_perf_threshold",
  "reversible_delivery_evidence": "PHASE4_REVERSIBLE_DELIVERY_EVIDENCE=keep the dedicated parked survey packet, both local survey wrappers, the explicit bootstrap-CI posture, the explicit no-perf-threshold posture, and the absent Zig starter boundary explicit until a later bounded validator or starter lane intentionally widens this surface",
  "next_bounded_evidence_step": "keep the dedicated parked survey packet adjacent to the shared gate-evidence note, the shared Phase 4 exact-readback packet, the validation matrix, the explicit bootstrap-CI posture, the explicit reviewability-only no-perf-threshold posture, the dedicated local `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig` survey wrapper, and the matching Linux-style `make -C zigux phase4-test-fsmount-survey` wrapper until a later bounded lane intentionally promotes the validator surface or lands the Zig starter"
}
""",
    )


def run_self_test() -> None:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="phase4-gap-survey-notes-") as tmp:
        root = Path(tmp)
        build_fixture_tree(root)
        if validate_root(root):
            raise AssertionError("baseline_round_trip")
        cases += 1

        mutations = {
            "missing_kprobe_phase_marker": lambda r: write_text(r / KPROBE_NOTE, replace_once(read_text(r / KPROBE_NOTE), "`PHASE4_KPROBE_PHASE=Phase 4`", "")),
            "missing_kprobe_next_step_marker": lambda r: write_text(r / KPROBE_NOTE, replace_once(read_text(r / KPROBE_NOTE), "Keep this parked packet adjacent to the shared gate-evidence note, the shared Phase 4 exact-readback packet, the validation matrix, the explicit bootstrap-CI posture, the explicit local lab replay marker, the dedicated local `make -C zigux phase4-kprobe-example-survey` wrapper, and the direct `zig test zigux/tests/phase4_kprobe_example_survey.zig` validation entrypoint until a later bounded Phase 4 lane lands the actual Zig starter with an updated rollback-readiness contract.", "Next step drift.")),
            "missing_test_fsmount_phase_marker": lambda r: write_text(r / TEST_FSMOUNT_NOTE, replace_once(read_text(r / TEST_FSMOUNT_NOTE), "`PHASE4_TEST_FSMOUNT_PHASE=Phase 4`", "")),
            "missing_test_fsmount_next_step_marker": lambda r: write_text(r / TEST_FSMOUNT_NOTE, replace_once(read_text(r / TEST_FSMOUNT_NOTE), "keep the dedicated parked survey packet adjacent to the shared gate-evidence note, the shared Phase 4 exact-readback packet, the validation matrix, the explicit bootstrap-CI posture, the explicit reviewability-only no-perf-threshold posture, the dedicated local `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig` survey wrapper, and the matching Linux-style `make -C zigux phase4-test-fsmount-survey` wrapper until a later bounded lane intentionally promotes the validator surface or lands the Zig starter", "next step drift")),
            "kprobe_manifest_phase_drift": lambda r: write_text(r / KPROBE_MANIFEST, replace_once(read_text(r / KPROBE_MANIFEST), '"phase": "Phase 4"', '"phase": "Phase 5"')),
            "test_fsmount_manifest_wrapper_drift": lambda r: write_text(r / TEST_FSMOUNT_MANIFEST, replace_once(read_text(r / TEST_FSMOUNT_MANIFEST), '"dedicated_linux_style_survey_wrapper": "make -C zigux phase4-test-fsmount-survey"', '"dedicated_linux_style_survey_wrapper": "make -C zigux phase4-test-fsmount"')),
            "test_fsmount_absent_starter_drift": lambda r: write_text(r / TEST_FSMOUNT_NOTE, replace_once(read_text(r / TEST_FSMOUNT_NOTE), "Current `master` still does not ship `samples/zigux/test_fsmount.zig`.", "Current `master` ships `samples/zigux/test_fsmount.zig`.")),
        }

        for case_name in EXPECTED_SELF_TEST_CASES[1:]:
            build_fixture_tree(root)
            mutations[case_name](root)
            if not validate_root(root):
                raise AssertionError(case_name)
            cases += 1

    if cases != EXPECTED_SELF_TEST_CASE_COUNT:
        raise AssertionError(cases)


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        print("PHASE4_GAP_SURVEY_NOTES_SELF_TEST=pass")
        print(f"PHASE4_GAP_SURVEY_NOTES_SELF_TEST_CASE_COUNT={EXPECTED_SELF_TEST_CASE_COUNT}")
        print("PHASE4_GAP_SURVEY_NOTES_SELF_TEST_CASES=" + ",".join(EXPECTED_SELF_TEST_CASES))
        return 0

    failures = validate_root(Path(args.root).resolve())
    if failures:
        print("PHASE4_GAP_SURVEY_NOTES=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE4_GAP_SURVEY_NOTES=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
