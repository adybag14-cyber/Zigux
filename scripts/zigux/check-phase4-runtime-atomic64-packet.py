#!/usr/bin/env python3
"""Guard the Phase 4 runtime atomic64 handoff packet."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parents[2] if len(SCRIPT_PATH.parents) > 2 else SCRIPT_PATH.parent

GATE_EVIDENCE = Path("Documentation/zigux/phase4-gate-evidence.md")
PHASE4_MATRIX = Path("Documentation/zigux/phase4-validation-matrix.md")
REVIEW_CHECKLIST = Path("Documentation/zigux/review-checklist.md")
VALIDATOR = Path("scripts/zigux/validate-phase4.py")
PHASE4_BUILD = Path("zigux/tests/phase4_build.zig")
PHASE9_BUILD = Path("zigux/tests/phase9_build.zig")
ATOMIC64_DIFF = Path("zigux/tests/atomic64_diff.zig")
RUNTIME_ATOMIC64_DIFF = Path("zigux/tests/runtime_atomic64_diff.zig")
MANIFEST = Path("zigux/tests/phase4_runtime_atomic64_diff_manifest.json")
SURVEY = Path("zigux/tests/phase4_runtime_atomic64_diff_survey.zig")
PERF_MANIFEST = Path("zigux/tests/phase4_perf_baseline_manifest.json")
PERF_SURVEY = Path("zigux/tests/phase4_perf_baseline_survey.zig")

REQUIRED_FILES = [
    GATE_EVIDENCE,
    PHASE4_MATRIX,
    REVIEW_CHECKLIST,
    VALIDATOR,
    PHASE4_BUILD,
    PHASE9_BUILD,
    ATOMIC64_DIFF,
    RUNTIME_ATOMIC64_DIFF,
    MANIFEST,
    SURVEY,
    PERF_MANIFEST,
    PERF_SURVEY,
]

MANIFEST_SHA_FIELDS = {
    "phase4_build_blob_sha": PHASE4_BUILD,
    "phase4_validator_blob_sha": VALIDATOR,
    "phase4_validation_matrix_blob_sha": PHASE4_MATRIX,
    "phase4_review_checklist_blob_sha": REVIEW_CHECKLIST,
    "phase9_build_blob_sha": PHASE9_BUILD,
}

REQUIRED_REVERSIBLE_DELIVERY_MARKERS = [
    "zigux/tests/atomic64_diff.zig",
    "zigux/tests/runtime_atomic64_diff.zig",
    "zigux/tests/phase4_build.zig",
    "scripts/zigux/validate-phase4.py",
    "Documentation/zigux/phase4-gate-evidence.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase4-validation-matrix.md",
    "zigux/tests/phase4_perf_baseline_manifest.json",
    "zigux/tests/phase4_perf_baseline_survey.zig",
]

REQUIRED_SURVEY_MARKERS = [
    'test "phase 4 atomic64 survey keeps wrapper handoff, owner map, and current local-only perf evidence explicit" {',
    'test "phase 4 atomic64 survey keeps the current roadmap gap summary reviewable" {',
    'test "phase 4 atomic64 survey keeps reversible delivery and next-step evidence explicit" {',
    "Documentation/zigux/phase4-gate-evidence.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase4-validation-matrix.md",
    "zigux/tests/phase4_perf_baseline_manifest.json",
    "zigux/tests/phase4_perf_baseline_survey.zig",
]

REQUIRED_GATE_EVIDENCE_MARKERS = [
    "PHASE4_VALIDATOR_BLOB_SHA=",
    "PHASE4_BUILD_BLOB_SHA=",
    "PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA=",
    "PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA=",
    "PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=true",
    "PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_CHECK=true",
    "shared CI perf thresholds for the shipped atomic64 and bitmap rollback gates remain intentionally unapproved.",
]

REQUIRED_PHASE4_MATRIX_MARKERS = [
    "`zigux/tests/atomic64_diff.zig` bounded atomic64 exchange, cmpxchg, add_unless, bitwise, and selftest-family replay via the shared runtime-backed gate",
    "`zigux/tests/phase4_runtime_atomic64_diff_survey.zig` manifest-backed survey that keeps the wrapper, runtime replay body, validator, matrix, and reviewer checklist aligned around the same bounded atomic64 handoff",
    "`zig build phase4-runtime-atomic64-diff-survey --build-file zigux/tests/phase4_build.zig`",
    "`threshold_pending_until_runtime_atomic64_scope_widens`",
    "`zigux/tests/phase4_perf_baseline_manifest.json`",
    "`zigux/tests/phase4_perf_baseline_survey.zig`",
]

REQUIRED_VALIDATOR_MARKERS = [
    "phase4_runtime_atomic64_diff_manifest.json",
    "phase4_runtime_atomic64_diff_survey.zig",
    "run_phase4_runtime_atomic64_packet_check",
]

REQUIRED_BUILD_MARKERS = [
    '"phase4-runtime-atomic64-diff"',
    '"phase4-runtime-atomic64-diff-survey"',
    "runtime_atomic64_diff_step.dependOn(&run_atomic64_diff_tests.step);",
    "runtime_atomic64_diff_survey_step.dependOn(&run_runtime_atomic64_diff_survey_tests.step);",
]

SELF_TEST_CASES = [
    "baseline_round_trip",
    "missing_manifest_sha_field",
    "manifest_sha_drift",
    "missing_reversible_delivery_evidence",
    "reversible_delivery_marker_drift",
    "survey_marker_drift",
    "survey_sha_exact_count_drift",
    "gate_evidence_presence_flag_drift",
    "matrix_runtime_atomic64_marker_drift",
    "validator_runtime_atomic64_marker_drift",
    "build_runtime_atomic64_survey_route_drift",
]


def git_blob_sha1(payload: bytes) -> str:
    return hashlib.sha1(f"blob {len(payload)}\0".encode() + payload).hexdigest()


def read_text(root: Path, relative_path: Path) -> str:
    try:
        return (root / relative_path).read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise RuntimeError(f"missing required file: {relative_path.as_posix()}") from exc


def ensure_markers(text: str, markers: list[str], label: str) -> None:
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise RuntimeError(f"{label} is missing required fragments: {missing}")


def ensure_required_files(root: Path) -> None:
    missing = [path.as_posix() for path in REQUIRED_FILES if not (root / path).exists()]
    if missing:
        raise RuntimeError(f"missing required files: {missing}")


def ensure_manifest_alignment(root: Path) -> None:
    manifest = json.loads(read_text(root, MANIFEST))
    for field, relative_path in MANIFEST_SHA_FIELDS.items():
        expected = git_blob_sha1((root / relative_path).read_bytes())
        actual = manifest.get(field)
        if actual != expected:
            raise RuntimeError(
                f"unexpected manifest blob sha for {field}: expected {expected}, got {actual}"
            )

    reversible_delivery = manifest.get("reversible_delivery_evidence")
    if not isinstance(reversible_delivery, str) or not reversible_delivery.strip():
        raise RuntimeError("missing reversible_delivery_evidence in phase4 runtime atomic64 manifest")
    ensure_markers(
        reversible_delivery,
        REQUIRED_REVERSIBLE_DELIVERY_MARKERS,
        "phase4 runtime atomic64 reversible delivery evidence",
    )


def ensure_survey_alignment(root: Path) -> None:
    survey_text = read_text(root, SURVEY)
    ensure_markers(survey_text, REQUIRED_SURVEY_MARKERS, SURVEY.as_posix())

    for relative_path in MANIFEST_SHA_FIELDS.values():
        sha = git_blob_sha1((root / relative_path).read_bytes())
        count = survey_text.count(sha)
        if count != 1:
            raise RuntimeError(
                f"{SURVEY.as_posix()} must carry blob sha {sha} exactly once, found {count}"
            )


def ensure_phase4_surface_alignment(root: Path) -> None:
    ensure_markers(
        read_text(root, GATE_EVIDENCE),
        REQUIRED_GATE_EVIDENCE_MARKERS,
        GATE_EVIDENCE.as_posix(),
    )
    ensure_markers(
        read_text(root, PHASE4_MATRIX),
        REQUIRED_PHASE4_MATRIX_MARKERS,
        PHASE4_MATRIX.as_posix(),
    )
    ensure_markers(
        read_text(root, VALIDATOR),
        REQUIRED_VALIDATOR_MARKERS,
        VALIDATOR.as_posix(),
    )
    ensure_markers(
        read_text(root, PHASE4_BUILD),
        REQUIRED_BUILD_MARKERS,
        PHASE4_BUILD.as_posix(),
    )


def check(root: Path) -> None:
    ensure_required_files(root)
    ensure_manifest_alignment(root)
    ensure_survey_alignment(root)
    ensure_phase4_surface_alignment(root)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_fixture_tree(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        write_text(root / relative_path, f"placeholder for {relative_path.as_posix()}\n")

    write_text(
        root / GATE_EVIDENCE,
        "\n".join(
            [
                "# Phase 4 Gate Evidence",
                "`PHASE4_VALIDATOR_BLOB_SHA=placeholder`",
                "`PHASE4_BUILD_BLOB_SHA=placeholder`",
                "`PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA=placeholder`",
                "`PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA=placeholder`",
                "`PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=true`",
                "`PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_CHECK=true`",
                "shared CI perf thresholds for the shipped atomic64 and bitmap rollback gates remain intentionally unapproved.",
                "",
            ]
        ),
    )

    write_text(
        root / PHASE4_MATRIX,
        "\n".join(
            [
                "# Phase 4 Validation Matrix",
                "`zigux/tests/atomic64_diff.zig` bounded atomic64 exchange, cmpxchg, add_unless, bitwise, and selftest-family replay via the shared runtime-backed gate",
                "`zigux/tests/phase4_runtime_atomic64_diff_survey.zig` manifest-backed survey that keeps the wrapper, runtime replay body, validator, matrix, and reviewer checklist aligned around the same bounded atomic64 handoff",
                "`zig build phase4-runtime-atomic64-diff-survey --build-file zigux/tests/phase4_build.zig`",
                "`threshold_pending_until_runtime_atomic64_scope_widens`",
                "`zigux/tests/phase4_perf_baseline_manifest.json`",
                "`zigux/tests/phase4_perf_baseline_survey.zig`",
                "",
            ]
        ),
    )

    write_text(
        root / VALIDATOR,
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "phase4_runtime_atomic64_diff_manifest.json",
                "phase4_runtime_atomic64_diff_survey.zig",
                "run_phase4_runtime_atomic64_packet_check",
                "",
            ]
        ),
    )

    write_text(
        root / PHASE4_BUILD,
        "\n".join(
            [
                "const runtime_atomic64_diff_step = b.step(",
                '    "phase4-runtime-atomic64-diff",',
                ");",
                "runtime_atomic64_diff_step.dependOn(&run_atomic64_diff_tests.step);",
                "const runtime_atomic64_diff_survey_step = b.step(",
                '    "phase4-runtime-atomic64-diff-survey",',
                ");",
                "runtime_atomic64_diff_survey_step.dependOn(&run_runtime_atomic64_diff_survey_tests.step);",
                "",
            ]
        ),
    )

    write_text(root / PHASE9_BUILD, "phase9 build placeholder\n")
    write_text(root / ATOMIC64_DIFF, "atomic64 diff placeholder\n")
    write_text(root / RUNTIME_ATOMIC64_DIFF, "runtime atomic64 diff placeholder\n")
    write_text(root / REVIEW_CHECKLIST, "review checklist placeholder\n")
    write_text(root / PERF_MANIFEST, "{}\n")
    write_text(root / PERF_SURVEY, "perf survey placeholder\n")

    phase4_build_sha = git_blob_sha1((root / PHASE4_BUILD).read_bytes())
    validator_sha = git_blob_sha1((root / VALIDATOR).read_bytes())
    matrix_sha = git_blob_sha1((root / PHASE4_MATRIX).read_bytes())
    review_checklist_sha = git_blob_sha1((root / REVIEW_CHECKLIST).read_bytes())
    phase9_build_sha = git_blob_sha1((root / PHASE9_BUILD).read_bytes())

    manifest = {
        "phase4_build_blob_sha": phase4_build_sha,
        "phase4_validator_blob_sha": validator_sha,
        "phase4_validation_matrix_blob_sha": matrix_sha,
        "phase4_review_checklist_blob_sha": review_checklist_sha,
        "phase9_build_blob_sha": phase9_build_sha,
        "reversible_delivery_evidence": (
            "keep zigux/tests/atomic64_diff.zig, zigux/tests/runtime_atomic64_diff.zig, "
            "zigux/tests/phase4_build.zig, scripts/zigux/validate-phase4.py, "
            "Documentation/zigux/phase4-gate-evidence.md, Documentation/zigux/review-checklist.md, "
            "Documentation/zigux/phase4-validation-matrix.md, zigux/tests/phase4_perf_baseline_manifest.json, "
            "and zigux/tests/phase4_perf_baseline_survey.zig aligned."
        ),
    }
    write_text(root / MANIFEST, json.dumps(manifest, indent=2) + "\n")

    write_text(
        root / SURVEY,
        "\n".join(
            [
                'const std = @import("std");',
                'test "phase 4 atomic64 survey keeps wrapper handoff, owner map, and current local-only perf evidence explicit" {',
                "    _ = std.testing.allocator;",
                "}",
                'test "phase 4 atomic64 survey keeps the current roadmap gap summary reviewable" {',
                "    _ = std.testing.allocator;",
                "}",
                'test "phase 4 atomic64 survey keeps reversible delivery and next-step evidence explicit" {',
                "    _ = std.testing.allocator;",
                "}",
                "// Documentation/zigux/phase4-gate-evidence.md",
                "// Documentation/zigux/review-checklist.md",
                "// Documentation/zigux/phase4-validation-matrix.md",
                "// zigux/tests/phase4_perf_baseline_manifest.json",
                "// zigux/tests/phase4_perf_baseline_survey.zig",
                f"// {phase4_build_sha}",
                f"// {validator_sha}",
                f"// {matrix_sha}",
                f"// {review_checklist_sha}",
                f"// {phase9_build_sha}",
                "",
            ]
        ),
    )


def expect_failure(label: str, fn) -> None:
    try:
        fn()
    except RuntimeError:
        return
    raise AssertionError(f"{label} did not fail")


def run_self_test() -> int:
    covered_cases: list[str] = []

    with tempfile.TemporaryDirectory(prefix="phase4_runtime_atomic64_packet_") as tempdir:
        root = Path(tempdir)

        build_fixture_tree(root)
        check(root)
        covered_cases.append("baseline_round_trip")

        manifest_path = root / MANIFEST
        original_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

        missing_field_manifest = dict(original_manifest)
        missing_field_manifest.pop("phase4_build_blob_sha")
        write_text(manifest_path, json.dumps(missing_field_manifest, indent=2) + "\n")
        expect_failure("missing manifest sha field", lambda: check(root))
        covered_cases.append("missing_manifest_sha_field")

        build_fixture_tree(root)
        manifest_path = root / MANIFEST
        drift_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        drift_manifest["phase4_validator_blob_sha"] = "deadbeef"
        write_text(manifest_path, json.dumps(drift_manifest, indent=2) + "\n")
        expect_failure("manifest sha drift", lambda: check(root))
        covered_cases.append("manifest_sha_drift")

        build_fixture_tree(root)
        manifest_path = root / MANIFEST
        missing_evidence_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        missing_evidence_manifest.pop("reversible_delivery_evidence")
        write_text(manifest_path, json.dumps(missing_evidence_manifest, indent=2) + "\n")
        expect_failure("missing reversible delivery evidence", lambda: check(root))
        covered_cases.append("missing_reversible_delivery_evidence")

        build_fixture_tree(root)
        manifest_path = root / MANIFEST
        drift_evidence_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        drift_evidence_manifest["reversible_delivery_evidence"] = drift_evidence_manifest[
            "reversible_delivery_evidence"
        ].replace("Documentation/zigux/phase4-validation-matrix.md", "Documentation/zigux/phase4-validation-matrix-drift.md")
        write_text(manifest_path, json.dumps(drift_evidence_manifest, indent=2) + "\n")
        expect_failure("reversible delivery marker drift", lambda: check(root))
        covered_cases.append("reversible_delivery_marker_drift")

        build_fixtureTree = None
        build_fixture_tree(root)
        survey_path = root / SURVEY
        write_text(
            survey_path,
            survey_path.read_text(encoding="utf-8").replace(
                'test "phase 4 atomic64 survey keeps the current roadmap gap summary reviewable" {',
                'test "phase 4 atomic64 survey drifted" {',
                1,
            ),
        )
        expect_failure("survey marker drift", lambda: check(root))
        covered_cases.append("survey_marker_drift")

        build_fixture_tree(root)
        survey_path = root / SURVEY
        validator_sha = git_blob_sha1((root / VALIDATOR).read_bytes())
        write_text(
            survey_path,
            survey_path.read_text(encoding="utf-8").replace(f"// {validator_sha}", "", 1),
        )
        expect_failure("survey sha exact count drift", lambda: check(root))
        covered_cases.append("survey_sha_exact_count_drift")

        build_fixture_tree(root)
        gate_evidence_path = root / GATE_EVIDENCE
        write_text(
            gate_evidence_path,
            gate_evidence_path.read_text(encoding="utf-8").replace(
                "`PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=true`",
                "`PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=false`",
                1,
            ),
        )
        expect_failure("gate evidence presence flag drift", lambda: check(root))
        covered_cases.append("gate_evidence_presence_flag_drift")

        build_fixture_tree(root)
        matrix_path = root / PHASE4_MATRIX
        write_text(
            matrix_path,
            matrix_path.read_text(encoding="utf-8").replace(
                "`zig build phase4-runtime-atomic64-diff-survey --build-file zigux/tests/phase4_build.zig`",
                "`zig build phase4-runtime-atomic64-diff-survey-drift --build-file zigux/tests/phase4_build.zig`",
                1,
            ),
        )
        expect_failure("matrix runtime atomic64 marker drift", lambda: check(root))
        covered_cases.append("matrix_runtime_atomic64_marker_drift")

        build_fixture_tree(root)
        validator_path = root / VALIDATOR
        write_text(
            validator_path,
            validator_path.read_text(encoding="utf-8").replace(
                "run_phase4_runtime_atomic64_packet_check",
                "run_phase4_runtime_atomic64_packet_check_drift",
                1,
            ),
        )
        expect_failure("validator runtime atomic64 marker drift", lambda: check(root))
        covered_cases.append("validator_runtime_atomic64_marker_drift")

        build_fixture_tree(root)
        build_path = root / PHASE4_BUILD
        write_text(
            build_path,
            build_path.read_text(encoding="utf-8").replace(
                "runtime_atomic64_diff_survey_step.dependOn(&run_runtime_atomic64_diff_survey_tests.step);",
                "",
                1,
            ),
        )
        expect_failure("build runtime atomic64 survey route drift", lambda: check(root))
        covered_cases.append("build_runtime_atomic64_survey_route_drift")

    if covered_cases != SELF_TEST_CASES:
        raise AssertionError(
            f"self-test catalog drifted: expected {SELF_TEST_CASES}, got {covered_cases}"
        )

    print("PHASE4_RUNTIME_ATOMIC64_PACKET_SELF_TEST=pass")
    print(f"PHASE4_RUNTIME_ATOMIC64_PACKET_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}")
    print("PHASE4_RUNTIME_ATOMIC64_PACKET_SELF_TEST_CASES=" + ",".join(SELF_TEST_CASES))
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()

    try:
        check(args.root.resolve())
    except RuntimeError as exc:
        print(f"PHASE4_RUNTIME_ATOMIC64_PACKET=fail: {exc}", file=sys.stderr)
        return 1

    print("PHASE4_RUNTIME_ATOMIC64_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
