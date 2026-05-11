#!/usr/bin/env python3
"""Validate the dedicated Phase 4 test_fsmount gap packet."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


NOTE_REL = Path("Documentation/zigux/phase4-test-fsmount-gap-survey.md")
MANIFEST_REL = Path("zigux/tests/phase4_test_fsmount_manifest.json")
SURVEY_REL = Path("zigux/tests/phase4_test_fsmount_survey.zig")
TESTS_README_REL = Path("zigux/tests/README.md")
MATRIX_REL = Path("Documentation/zigux/phase4-validation-matrix.md")
GATE_EVIDENCE_REL = Path("Documentation/zigux/phase4-gate-evidence.md")
MAKEFILE_REL = Path("zigux/Makefile")

NOTE_MARKERS = [
    "PHASE4_TEST_FSMOUNT_STATUS=parked_gap_packet_landed",
    "PHASE4_TEST_FSMOUNT_C_ANCHOR=samples/vfs/test-fsmount.c",
    "PHASE4_TEST_FSMOUNT_CURRENT_LINUX_REPLAY=make M=samples/vfs",
    "PHASE4_TEST_FSMOUNT_LOCAL_SURVEY_WRAPPER=zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
    "PHASE4_TEST_FSMOUNT_LINUX_STYLE_SURVEY_WRAPPER=make -C zigux phase4-test-fsmount-survey",
    "PHASE4_TEST_FSMOUNT_VALIDATION_ENTRYPOINT=zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
    "PHASE4_TEST_FSMOUNT_OWNER=Validation and Perf Team",
    "PHASE4_TEST_FSMOUNT_ROLLBACK_OWNER=Validation and Perf Team",
    "PHASE4_TEST_FSMOUNT_THRESHOLD_POSTURE=reviewability_only_no_perf_threshold",
    "PHASE4_REVERSIBLE_DELIVERY_EVIDENCE=keep the dedicated parked survey packet, both local survey wrappers, the explicit no-perf-threshold posture, and the absent Zig starter boundary explicit until a later bounded validator or starter lane intentionally widens this surface",
    "Current `master` still does not ship `samples/zigux/test_fsmount.zig`.",
    "reviewability-only no-perf-threshold posture",
]

MANIFEST_EXPECTATIONS = {
    "lane_key": "P4-L19",
    "phase": "Phase 4",
    "c_anchor": "samples/vfs/test-fsmount.c",
    "current_linux_replay": "make M=samples/vfs",
    "dedicated_local_survey_wrapper": "zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
    "dedicated_linux_style_survey_wrapper": "make -C zigux phase4-test-fsmount-survey",
    "validation_entrypoint": "zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
    "owner": "Validation and Perf Team",
    "rollback_owner": "Validation and Perf Team",
    "current_measurable_status": "absent_on_current_master_but_reviewable_through_the_dedicated_gap_packet_without_claiming_a_shipped_zig_starter",
    "threshold_posture": "reviewability_only_no_perf_threshold",
    "reversible_delivery_evidence": "PHASE4_REVERSIBLE_DELIVERY_EVIDENCE=keep the dedicated parked survey packet, both local survey wrappers, the explicit no-perf-threshold posture, and the absent Zig starter boundary explicit until a later bounded validator or starter lane intentionally widens this surface",
}

SURVEY_MARKERS = [
    'test "phase4 test_fsmount survey keeps the parked gap packet explicit" {',
    'test "phase4 test_fsmount survey keeps threshold posture explicit" {',
    'test "phase4 test_fsmount survey keeps reversible-delivery evidence explicit" {',
    'test "phase4 test_fsmount survey keeps the bounded next step explicit" {',
    '\\"dedicated_linux_style_survey_wrapper\\": \\"make -C zigux phase4-test-fsmount-survey\\"',
    '\\"threshold_posture\\": \\"reviewability_only_no_perf_threshold\\"',
    '\\"owner\\": \\"Validation and Perf Team\\"',
]

TESTS_README_MARKERS = [
    "Documentation/zigux/phase4-test-fsmount-gap-survey.md",
    "zigux/tests/phase4_test_fsmount_manifest.json",
    "zigux/tests/phase4_test_fsmount_survey.zig",
    "zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
    "make -C zigux phase4-test-fsmount-survey",
]

MATRIX_MARKERS = [
    "samples/zigux/test_fsmount.zig",
    "zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
    "make -C zigux phase4-test-fsmount-survey",
    "reviewability_only_no_perf_threshold",
]

GATE_EVIDENCE_MARKERS = [
    "Documentation/zigux/phase4-test-fsmount-gap-survey.md",
    "zigux/tests/phase4_test_fsmount_manifest.json",
    "zigux/tests/phase4_test_fsmount_survey.zig",
    "zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
    "make -C zigux phase4-test-fsmount-survey",
    "reviewability_only_no_perf_threshold",
    "samples/zigux/test_fsmount.zig",
]

MAKEFILE_MARKERS = [
    "phase4-test-fsmount-survey",
    "phase4-test-fsmount-survey:",
    "$(ZIG) build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
]

EXPECTED_SELF_TEST_CASES = [
    "baseline_round_trip",
    "missing_note_marker",
    "manifest_owner_drift",
    "survey_wrapper_drift",
    "tests_readme_wrapper_drift",
    "matrix_threshold_drift",
    "gate_evidence_route_drift",
    "makefile_target_drift",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def ensure_markers(label: str, text: str, markers: list[str]) -> list[str]:
    return [f"{label}:{marker}" for marker in markers if marker not in text]


def validate_root(root: Path) -> list[str]:
    failures: list[str] = []
    paths = {
        "note": root / NOTE_REL,
        "manifest": root / MANIFEST_REL,
        "survey": root / SURVEY_REL,
        "tests_readme": root / TESTS_README_REL,
        "matrix": root / MATRIX_REL,
        "gate_evidence": root / GATE_EVIDENCE_REL,
        "makefile": root / MAKEFILE_REL,
    }

    for path in paths.values():
        if not path.exists():
            failures.append(f"file:{path.relative_to(root).as_posix()}")
    if failures:
        return failures

    note = read_text(paths["note"])
    manifest = json.loads(read_text(paths["manifest"]))
    survey = read_text(paths["survey"])
    tests_readme = read_text(paths["tests_readme"])
    matrix = read_text(paths["matrix"])
    gate_evidence = read_text(paths["gate_evidence"])
    makefile = read_text(paths["makefile"])

    failures.extend(ensure_markers("note", note, NOTE_MARKERS))
    for key, expected in MANIFEST_EXPECTATIONS.items():
        actual = manifest.get(key)
        if actual != expected:
            failures.append(f"manifest:{key}:{actual}:{expected}")
    failures.extend(ensure_markers("survey", survey, SURVEY_MARKERS))
    failures.extend(ensure_markers("tests_readme", tests_readme, TESTS_README_MARKERS))
    failures.extend(ensure_markers("matrix", matrix, MATRIX_MARKERS))
    failures.extend(ensure_markers("gate_evidence", gate_evidence, GATE_EVIDENCE_MARKERS))
    failures.extend(ensure_markers("makefile", makefile, MAKEFILE_MARKERS))
    return failures


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_fixture_tree(root: Path) -> None:
    write_text(
        root / NOTE_REL,
        """# Phase 4 test_fsmount Gap Survey

## Status
- `PHASE4_TEST_FSMOUNT_STATUS=parked_gap_packet_landed`
- `PHASE4_TEST_FSMOUNT_LANE_KEY=P4-L19`
- `PHASE4_TEST_FSMOUNT_PHASE=Phase 4`
- `PHASE4_TEST_FSMOUNT_C_ANCHOR=samples/vfs/test-fsmount.c`
- `PHASE4_TEST_FSMOUNT_CURRENT_LINUX_REPLAY=make M=samples/vfs`
- `PHASE4_TEST_FSMOUNT_LOCAL_SURVEY_WRAPPER=zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`
- `PHASE4_TEST_FSMOUNT_LINUX_STYLE_SURVEY_WRAPPER=make -C zigux phase4-test-fsmount-survey`
- `PHASE4_TEST_FSMOUNT_VALIDATION_ENTRYPOINT=zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`
- `PHASE4_TEST_FSMOUNT_OWNER=Validation and Perf Team`
- `PHASE4_TEST_FSMOUNT_ROLLBACK_OWNER=Validation and Perf Team`
- `PHASE4_TEST_FSMOUNT_THRESHOLD_POSTURE=reviewability_only_no_perf_threshold`
- `PHASE4_REVERSIBLE_DELIVERY_EVIDENCE=keep the dedicated parked survey packet, both local survey wrappers, the explicit no-perf-threshold posture, and the absent Zig starter boundary explicit until a later bounded validator or starter lane intentionally widens this surface`

Current `master` still does not ship `samples/zigux/test_fsmount.zig`.

That packet keeps the current C anchor, replay path, owner, rollback owner, dedicated
local survey routes, and the current reviewability-only no-perf-threshold posture
measurable while the shared Phase 4 rollback-readiness lane remains below starter
implementation.
""",
    )
    write_text(root / MANIFEST_REL, json.dumps(MANIFEST_EXPECTATIONS, indent=2) + "\n")
    write_text(
        root / SURVEY_REL,
        """const std = @import("std");

test "phase4 test_fsmount survey keeps the parked gap packet explicit" {
    _ = std.testing.allocator;
    _ = "\\"dedicated_linux_style_survey_wrapper\\": \\"make -C zigux phase4-test-fsmount-survey\\"";
    _ = "\\"owner\\": \\"Validation and Perf Team\\"";
}

test "phase4 test_fsmount survey keeps threshold posture explicit" {
    _ = std.testing.allocator;
    _ = "\\"threshold_posture\\": \\"reviewability_only_no_perf_threshold\\"";
}

test "phase4 test_fsmount survey keeps reversible-delivery evidence explicit" {
    _ = std.testing.allocator;
}

test "phase4 test_fsmount survey keeps the bounded next step explicit" {
    _ = std.testing.allocator;
}
""",
    )
    write_text(
        root / TESTS_README_REL,
        """# zigux/tests
Documentation/zigux/phase4-test-fsmount-gap-survey.md
zigux/tests/phase4_test_fsmount_manifest.json
zigux/tests/phase4_test_fsmount_survey.zig
zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig
make -C zigux phase4-test-fsmount-survey
""",
    )
    write_text(
        root / MATRIX_REL,
        """# Phase 4 Validation Matrix
samples/zigux/test_fsmount.zig
zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig
make -C zigux phase4-test-fsmount-survey
reviewability_only_no_perf_threshold
""",
    )
    write_text(
        root / GATE_EVIDENCE_REL,
        """# Phase 4 Gate Evidence
Documentation/zigux/phase4-test-fsmount-gap-survey.md
zigux/tests/phase4_test_fsmount_manifest.json
zigux/tests/phase4_test_fsmount_survey.zig
zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig
make -C zigux phase4-test-fsmount-survey
reviewability_only_no_perf_threshold
samples/zigux/test_fsmount.zig
""",
    )
    write_text(
        root / MAKEFILE_REL,
        """PHONY += phase4-test-fsmount-survey

phase4-test-fsmount-survey:
\tcd $(ZIGUX_ROOT) && $(ZIG) build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig
""",
    )


def expect_failure(root: Path, expected: str) -> None:
    failures = validate_root(root)
    if expected not in failures:
        raise AssertionError(f"expected failure {expected!r}, got {failures!r}")


def run_self_test() -> int:
    covered: list[str] = []
    with TemporaryDirectory(prefix="zigux_phase4_test_fsmount_checker_") as tempdir:
        root = Path(tempdir)
        write_fixture_tree(root)

        failures = validate_root(root)
        if failures:
            print("PHASE4_TEST_FSMOUNT_PACKET_SELF_TEST=fail")
            print("\n".join(failures))
            return 1
        covered.append("baseline_round_trip")

        note_path = root / NOTE_REL
        original_note = read_text(note_path)
        note_path.write_text(
            original_note.replace(
                "PHASE4_REVERSIBLE_DELIVERY_EVIDENCE=",
                "PHASE4_REVERSIBLE_DELIVERY_PROOF=",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            root,
            "note:PHASE4_REVERSIBLE_DELIVERY_EVIDENCE=keep the dedicated parked survey packet, both local survey wrappers, the explicit no-perf-threshold posture, and the absent Zig starter boundary explicit until a later bounded validator or starter lane intentionally widens this surface",
        )
        covered.append("missing_note_marker")
        note_path.write_text(original_note, encoding="utf-8")

        manifest_path = root / MANIFEST_REL
        manifest = json.loads(read_text(manifest_path))
        manifest["owner"] = "Tooling and Validation Team"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_failure(
            root,
            "manifest:owner:Tooling and Validation Team:Validation and Perf Team",
        )
        covered.append("manifest_owner_drift")
        write_fixture_tree(root)

        survey_path = root / SURVEY_REL
        original_survey = read_text(survey_path)
        survey_path.write_text(
            original_survey.replace(
                'make -C zigux phase4-test-fsmount-survey',
                'make -C zigux phase4-test-fsmount-gap',
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            root,
            'survey:\\\"dedicated_linux_style_survey_wrapper\\\": \\\"make -C zigux phase4-test-fsmount-survey\\\"',
        )
        covered.append("survey_wrapper_drift")
        write_fixture_tree(root)

        tests_readme_path = root / TESTS_README_REL
        tests_readme_path.write_text("# zigux/tests\n", encoding="utf-8")
        expect_failure(
            root,
            "tests_readme:make -C zigux phase4-test-fsmount-survey",
        )
        covered.append("tests_readme_wrapper_drift")
        write_fixture_tree(root)

        matrix_path = root / MATRIX_REL
        matrix_path.write_text(
            read_text(matrix_path).replace(
                "reviewability_only_no_perf_threshold",
                "shared_ci_perf_promoted",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            root,
            "matrix:reviewability_only_no_perf_threshold",
        )
        covered.append("matrix_threshold_drift")
        write_fixture_tree(root)

        gate_evidence_path = root / GATE_EVIDENCE_REL
        gate_evidence_path.write_text(
            read_text(gate_evidence_path).replace(
                "zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
                "zig build phase4-test-fsmount-gap --build-file zigux/tests/phase4_build.zig",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            root,
            "gate_evidence:zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
        )
        covered.append("gate_evidence_route_drift")
        write_fixture_tree(root)

        makefile_path = root / MAKEFILE_REL
        makefile_path.write_text("PHONY += phase4-test\n", encoding="utf-8")
        expect_failure(
            root,
            "makefile:phase4-test-fsmount-survey:",
        )
        covered.append("makefile_target_drift")

    if covered != EXPECTED_SELF_TEST_CASES:
        print("PHASE4_TEST_FSMOUNT_PACKET_SELF_TEST=fail")
        print(f"unexpected self-test coverage: {covered!r}")
        return 1

    print("PHASE4_TEST_FSMOUNT_PACKET_SELF_TEST=pass")
    print(f"PHASE4_TEST_FSMOUNT_PACKET_SELF_TEST_CASE_COUNT={len(covered)}")
    print(
        "PHASE4_TEST_FSMOUNT_PACKET_SELF_TEST_CASES=" + ",".join(EXPECTED_SELF_TEST_CASES)
    )
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Validate the dedicated Phase 4 test_fsmount gap packet."
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()

    failures = validate_root(args.repo_root)
    if failures:
        print("PHASE4_TEST_FSMOUNT_PACKET=fail")
        print("PHASE4_TEST_FSMOUNT_PACKET_FAILURES_START")
        for item in failures:
            print(item)
        print("PHASE4_TEST_FSMOUNT_PACKET_FAILURES_END")
        return 1

    print("PHASE4_TEST_FSMOUNT_PACKET=pass")
    print("PHASE4_TEST_FSMOUNT_PACKET_REQUIRED_FILE_COUNT=7")
    print(
        "PHASE4_TEST_FSMOUNT_PACKET_REQUIRED_CHECK_COUNT="
        + str(
            len(NOTE_MARKERS)
            + len(MANIFEST_EXPECTATIONS)
            + len(SURVEY_MARKERS)
            + len(TESTS_README_MARKERS)
            + len(MATRIX_MARKERS)
            + len(GATE_EVIDENCE_MARKERS)
            + len(MAKEFILE_MARKERS)
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
