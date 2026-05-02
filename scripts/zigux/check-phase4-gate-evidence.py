#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import tempfile
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parents[2] if len(SCRIPT_PATH.parents) > 2 else SCRIPT_PATH.parent
SHARED_SURVEYED_COMMIT = "3ba64cd4e41a4de1c8fd8dbaecb23702ad9701a3"

REQUIRED_MARKERS = [
    "PHASE4_EVIDENCE_DATE=",
    "PHASE4_EVIDENCE_MODE=github_connector_readback",
    "PHASE4_EVIDENCE_SCOPE=rollback_ownership_and_lab_matrix_current_gate_definitions",
    "PHASE4_VALIDATOR_SELF_TEST=pass",
    "PHASE4_VALIDATION=pass",
    "PHASE4_REQUIRED_FILE_COUNT=",
    "PHASE4_REQUIRED_MARKER_COUNT=",
    "PHASE4_GATE_EVIDENCE_SELF_TEST=pass",
    "PHASE4_GATE_EVIDENCE_CHECK=pass",
    "PHASE4_GATE_EVIDENCE_TARGET_COUNT=",
    "## Exact Readback Evidence",
    "## Current Conclusion",
]

REQUIRED_SURVEY_ALIGNMENT_MARKERS = [
    SHARED_SURVEYED_COMMIT,
    "phase4_test_fsmount_survey.zig",
    "phase4_perf_baseline_survey.zig",
    "phase4_runtime_atomic64_diff_survey.zig",
]

EXACT_VALIDATOR_STATUS_LINES = [
    "PHASE4_VALIDATOR_SELF_TEST=pass",
    "PHASE4_VALIDATION=pass",
    "PHASE4_REQUIRED_FILE_COUNT=23",
    "PHASE4_REQUIRED_MARKER_COUNT=236",
]

PHASE4_GATE_EVIDENCE_BLOB_TARGETS = {
    "PHASE4_VALIDATION_MATRIX_BLOB_SHA": "Documentation/zigux/phase4-validation-matrix.md",
    "PHASE4_VALIDATOR_BLOB_SHA": "scripts/zigux/validate-phase4.py",
    "PHASE4_GATE_EVIDENCE_CHECKER_BLOB_SHA": "scripts/zigux/check-phase4-gate-evidence.py",
    "PHASE4_BUILD_BLOB_SHA": "zigux/tests/phase4_build.zig",
    "PHASE4_MAKEFILE_BLOB_SHA": "zigux/Makefile",
    "PHASE4_WORKFLOW_BLOB_SHA": ".github/workflows/zigux-bootstrap.yml",
    "PHASE4_TEST_FSMOUNT_MANIFEST_BLOB_SHA": "zigux/tests/phase4_test_fsmount_manifest.json",
    "PHASE4_TEST_FSMOUNT_SURVEY_BLOB_SHA": "zigux/tests/phase4_test_fsmount_survey.zig",
    "PHASE4_PERF_BASELINE_MANIFEST_BLOB_SHA": "zigux/tests/phase4_perf_baseline_manifest.json",
    "PHASE4_PERF_BASELINE_SURVEY_BLOB_SHA": "zigux/tests/phase4_perf_baseline_survey.zig",
    "PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA": "zigux/tests/phase4_runtime_atomic64_diff_manifest.json",
    "PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA": "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
    "PHASE4_DOC_README_BLOB_SHA": "Documentation/zigux/README.md",
    "PHASE4_SCRIPT_README_BLOB_SHA": "scripts/zigux/README.md",
    "PHASE4_TESTS_README_BLOB_SHA": "zigux/tests/README.md",
}


def git_blob_sha1(payload: bytes) -> str:
    header = f"blob {len(payload)}\0".encode("utf-8")
    return hashlib.sha1(header + payload).hexdigest()


def read_bytes(root: Path, relative_path: str) -> bytes:
    return (root / relative_path).read_bytes()


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def validate_root(root: Path) -> list[str]:
    missing: list[str] = []

    gate_evidence_path = "Documentation/zigux/phase4-gate-evidence.md"
    if not (root / gate_evidence_path).exists():
        return [f"file:{gate_evidence_path}"]

    gate_evidence = read_text(root, gate_evidence_path)
    for marker in REQUIRED_MARKERS:
        if marker not in gate_evidence:
            missing.append(f"phase4_gate_evidence:{marker}")
    for marker in REQUIRED_SURVEY_ALIGNMENT_MARKERS:
        if marker not in gate_evidence:
            missing.append(f"phase4_gate_evidence:{marker}")
    for line in EXACT_VALIDATOR_STATUS_LINES:
        if f"`{line}`" not in gate_evidence:
            missing.append(f"phase4_gate_evidence:{line}")

    for marker, relative_path in PHASE4_GATE_EVIDENCE_BLOB_TARGETS.items():
        target = root / relative_path
        if not target.exists():
            missing.append(f"file:{relative_path}")
            continue
        digest = git_blob_sha1(read_bytes(root, relative_path))
        evidence_line = f"`{marker}={digest}`"
        if evidence_line not in gate_evidence:
            missing.append(f"phase4_gate_evidence:{marker}:{digest}")

    expected_target_count_line = (
        f"PHASE4_GATE_EVIDENCE_TARGET_COUNT={len(PHASE4_GATE_EVIDENCE_BLOB_TARGETS)}"
    )
    if expected_target_count_line not in gate_evidence:
        missing.append(f"phase4_gate_evidence:{expected_target_count_line}")

    return missing


def write_fixture_tree(root: Path) -> None:
    file_contents = {
        "Documentation/zigux/phase4-validation-matrix.md": "phase4 matrix fixture\n",
        "scripts/zigux/validate-phase4.py": "phase4 validator fixture\n",
        "scripts/zigux/check-phase4-gate-evidence.py": "phase4 gate evidence checker fixture\n",
        "zigux/tests/phase4_build.zig": "phase4 build fixture\n",
        "zigux/Makefile": "phase4 validate fixture\n",
        ".github/workflows/zigux-bootstrap.yml": "phase4 workflow fixture\n",
        "zigux/tests/phase4_test_fsmount_manifest.json": "{}\n",
        "zigux/tests/phase4_test_fsmount_survey.zig": "phase4 test_fsmount survey fixture\n",
        "zigux/tests/phase4_perf_baseline_manifest.json": "{}\n",
        "zigux/tests/phase4_perf_baseline_survey.zig": "phase4 perf baseline survey fixture\n",
        "zigux/tests/phase4_runtime_atomic64_diff_manifest.json": "{}\n",
        "zigux/tests/phase4_runtime_atomic64_diff_survey.zig": "phase4 runtime atomic64 survey fixture\n",
        "Documentation/zigux/README.md": "phase4 doc readme fixture\n",
        "scripts/zigux/README.md": "phase4 script readme fixture\n",
        "zigux/tests/README.md": "phase4 tests readme fixture\n",
    }

    for relative_path, content in file_contents.items():
        target = root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    gate_evidence_lines = [
        "# Phase 4 Gate Evidence",
        "",
        "## Status",
        "",
        "- `PHASE4_EVIDENCE_DATE=2026-05-01`",
        "- `PHASE4_EVIDENCE_MODE=github_connector_readback`",
        "- `PHASE4_EVIDENCE_SCOPE=rollback_ownership_and_lab_matrix_current_gate_definitions`",
        "- `PHASE4_VALIDATOR_SELF_TEST=pass`",
        "- `PHASE4_VALIDATION=pass`",
        "- `PHASE4_REQUIRED_FILE_COUNT=23`",
        "- `PHASE4_REQUIRED_MARKER_COUNT=236`",
        "- `PHASE4_GATE_EVIDENCE_SELF_TEST=pass`",
        "- `PHASE4_GATE_EVIDENCE_CHECK=pass`",
        f"- `PHASE4_GATE_EVIDENCE_TARGET_COUNT={len(PHASE4_GATE_EVIDENCE_BLOB_TARGETS)}`",
        "",
        "## Exact Readback Evidence",
        "",
        f"- synthetic fixture keeps shared surveyed snapshot `{SHARED_SURVEYED_COMMIT}` explicit through `phase4_runtime_atomic64_diff_survey.zig`, `phase4_test_fsmount_survey.zig`, and `phase4_perf_baseline_survey.zig`.",
        "",
        "## Current Conclusion",
        "",
        "- synthetic fixture",
    ]
    for marker, relative_path in PHASE4_GATE_EVIDENCE_BLOB_TARGETS.items():
        digest = git_blob_sha1(read_bytes(root, relative_path))
        gate_evidence_lines.insert(14, f"- `{marker}={digest}`")

    (root / "Documentation/zigux/phase4-gate-evidence.md").write_text(
        "\n".join(gate_evidence_lines) + "\n",
        encoding="utf-8",
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase4_gate_evidence_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture_tree(root)

        missing = validate_root(root)
        assert not missing, missing

        gate_evidence = root / "Documentation/zigux/phase4-gate-evidence.md"
        gate_evidence.write_text(
            gate_evidence.read_text(encoding="utf-8").replace(
                "## Current Conclusion\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        missing = validate_root(root)
        assert "phase4_gate_evidence:## Current Conclusion" in missing, missing

        write_fixture_tree(root)
        gate_evidence = root / "Documentation/zigux/phase4-gate-evidence.md"
        gate_evidence.write_text(
            gate_evidence.read_text(encoding="utf-8").replace(
                "PHASE4_VALIDATION=pass",
                "PHASE4_VALIDATION=fail",
                1,
            ),
            encoding="utf-8",
        )
        missing = validate_root(root)
        assert "phase4_gate_evidence:PHASE4_VALIDATION=pass" in missing, missing

        write_fixture_tree(root)
        gate_evidence = root / "Documentation/zigux/phase4-gate-evidence.md"
        gate_evidence.write_text(
            gate_evidence.read_text(encoding="utf-8").replace(
                "PHASE4_REQUIRED_FILE_COUNT=23",
                "PHASE4_REQUIRED_FILE_COUNT=21",
                1,
            ),
            encoding="utf-8",
        )
        missing = validate_root(root)
        assert (
            "phase4_gate_evidence:PHASE4_REQUIRED_FILE_COUNT=23" in missing
        ), missing

        write_fixture_tree(root)
        gate_evidence = root / "Documentation/zigux/phase4-gate-evidence.md"
        gate_evidence.write_text(
            gate_evidence.read_text(encoding="utf-8").replace(
                "PHASE4_REQUIRED_MARKER_COUNT=236",
                "PHASE4_REQUIRED_MARKER_COUNT=231",
                1,
            ),
            encoding="utf-8",
        )
        missing = validate_root(root)
        assert (
            "phase4_gate_evidence:PHASE4_REQUIRED_MARKER_COUNT=236" in missing
        ), missing

        write_fixture_tree(root)
        gate_evidence = root / "Documentation/zigux/phase4-gate-evidence.md"
        gate_evidence.write_text(
            gate_evidence.read_text(encoding="utf-8").replace(
                f"PHASE4_GATE_EVIDENCE_TARGET_COUNT={len(PHASE4_GATE_EVIDENCE_BLOB_TARGETS)}",
                "PHASE4_GATE_EVIDENCE_TARGET_COUNT=14",
                1,
            ),
            encoding="utf-8",
        )
        missing = validate_root(root)
        assert (
            "phase4_gate_evidence:PHASE4_GATE_EVIDENCE_TARGET_COUNT=15" in missing
        ), missing

        write_fixture_tree(root)
        gate_evidence = root / "Documentation/zigux/phase4-gate-evidence.md"
        gate_evidence.write_text(
            gate_evidence.read_text(encoding="utf-8").replace(
                "PHASE4_GATE_EVIDENCE_CHECK=pass",
                "PHASE4_GATE_EVIDENCE_CHECK=fail",
                1,
            ),
            encoding="utf-8",
        )
        missing = validate_root(root)
        assert (
            "phase4_gate_evidence:PHASE4_GATE_EVIDENCE_CHECK=pass" in missing
        ), missing

        write_fixture_tree(root)
        gate_evidence = root / "Documentation/zigux/phase4-gate-evidence.md"
        gate_evidence.write_text(
            gate_evidence.read_text(encoding="utf-8").replace(
                SHARED_SURVEYED_COMMIT,
                "0" * 40,
                1,
            ),
            encoding="utf-8",
        )
        missing = validate_root(root)
        assert f"phase4_gate_evidence:{SHARED_SURVEYED_COMMIT}" in missing, missing

        write_fixture_tree(root)
        gate_evidence = root / "Documentation/zigux/phase4-gate-evidence.md"
        gate_evidence.write_text(
            gate_evidence.read_text(encoding="utf-8").replace(
                "phase4_test_fsmount_survey.zig",
                "phase4_test_fsmount_survey_missing.zig",
                1,
            ),
            encoding="utf-8",
        )
        missing = validate_root(root)
        assert (
            "phase4_gate_evidence:phase4_test_fsmount_survey.zig" in missing
        ), missing

        write_fixture_tree(root)
        checker = root / "scripts/zigux/check-phase4-gate-evidence.py"
        checker.unlink()
        missing = validate_root(root)
        assert "file:scripts/zigux/check-phase4-gate-evidence.py" in missing, missing

        write_fixture_tree(root)
        tests_readme = root / "zigux/tests/README.md"
        tests_readme.unlink()
        missing = validate_root(root)
        assert "file:zigux/tests/README.md" in missing, missing

        write_fixture_tree(root)
        gate_evidence = root / "Documentation/zigux/phase4-gate-evidence.md"
        gate_evidence.write_text(
            gate_evidence.read_text(encoding="utf-8").replace(
                "PHASE4_DOC_README_BLOB_SHA=",
                "PHASE4_DOC_README_BLOB_SHA=broken",
                1,
            ),
            encoding="utf-8",
        )
        missing = validate_root(root)
        assert any(
            marker.startswith("phase4_gate_evidence:PHASE4_DOC_README_BLOB_SHA:")
            for marker in missing
        ), missing

        write_fixture_tree(root)
        gate_evidence = root / "Documentation/zigux/phase4-gate-evidence.md"
        gate_evidence.write_text(
            gate_evidence.read_text(encoding="utf-8").replace(
                "PHASE4_TEST_FSMOUNT_SURVEY_BLOB_SHA=",
                "PHASE4_TEST_FSMOUNT_SURVEY_BLOB_SHA=broken",
                1,
            ),
            encoding="utf-8",
        )
        missing = validate_root(root)
        assert any(
            marker.startswith(
                "phase4_gate_evidence:PHASE4_TEST_FSMOUNT_SURVEY_BLOB_SHA:"
            )
            for marker in missing
        ), missing

        write_fixture_tree(root)
        gate_evidence = root / "Documentation/zigux/phase4-gate-evidence.md"
        gate_evidence.write_text(
            gate_evidence.read_text(encoding="utf-8").replace(
                "PHASE4_TESTS_README_BLOB_SHA=",
                "PHASE4_TESTS_README_BLOB_SHA=broken",
                1,
            ),
            encoding="utf-8",
        )
        missing = validate_root(root)
        assert any(
            marker.startswith("phase4_gate_evidence:PHASE4_TESTS_README_BLOB_SHA:")
            for marker in missing
        ), missing

    print("PHASE4_GATE_EVIDENCE_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the Phase 4 gate-evidence blob packet."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the built-in synthetic gate-evidence coverage check.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing = validate_root(ROOT)
    if missing:
        print("PHASE4_GATE_EVIDENCE_CHECK=fail")
        print("MISSING_PHASE4_GATE_EVIDENCE_MARKERS_START")
        for marker in missing:
            print(marker)
        print("MISSING_PHASE4_GATE_EVIDENCE_MARKERS_END")
        return 1

    print("PHASE4_GATE_EVIDENCE_CHECK=pass")
    print(f"PHASE4_GATE_EVIDENCE_TARGET_COUNT={len(PHASE4_GATE_EVIDENCE_BLOB_TARGETS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
