#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parents[2] if len(SCRIPT_PATH.parents) > 2 else SCRIPT_PATH.parent
NOTE_PATH = Path("Documentation/zigux/phase4-gate-evidence.md")
MANIFEST_PATH = Path("zigux/tests/phase4_runtime_atomic64_diff_manifest.json")
SURVEY_PATH = Path("zigux/tests/phase4_runtime_atomic64_diff_survey.zig")

PHASE4_GATE_EVIDENCE_BLOB_TARGETS = {
    "PHASE4_VALIDATION_MATRIX_BLOB_SHA": "Documentation/zigux/phase4-validation-matrix.md",
    "PHASE4_VALIDATOR_BLOB_SHA": "scripts/zigux/validate-phase4.py",
    "PHASE4_ARTIFACT_DIFF_DOC_BLOB_SHA": "Documentation/zigux/artifact-diff.md",
    "PHASE4_ARTIFACT_DIFF_CONTRACT_CHECKER_BLOB_SHA": "scripts/zigux/check-artifact-diff-contract.py",
    "PHASE4_BUILD_BLOB_SHA": "zigux/tests/phase4_build.zig",
    "PHASE4_MAKEFILE_BLOB_SHA": "zigux/Makefile",
    "PHASE4_WORKFLOW_BLOB_SHA": ".github/workflows/zigux-bootstrap.yml",
    "PHASE4_DOC_README_BLOB_SHA": "Documentation/zigux/README.md",
    "PHASE4_SCRIPT_README_BLOB_SHA": "scripts/zigux/README.md",
    "PHASE4_TESTS_README_BLOB_SHA": "zigux/tests/README.md",
    "PHASE4_ATOMIC64_DIFF_BLOB_SHA": "zigux/tests/atomic64_diff.zig",
    "PHASE4_RUNTIME_ATOMIC64_DIFF_BLOB_SHA": "zigux/tests/runtime_atomic64_diff.zig",
    "PHASE4_BITMAP_DIFF_BLOB_SHA": "zigux/tests/bitmap_diff.zig",
    "PHASE4_BITMAP_LIVE_HELPER_REPLAY_BLOB_SHA": "zigux/tests/phase4_bitmap_live_helper_replay.zig",
    "PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA": "zigux/tests/phase4_runtime_atomic64_diff_manifest.json",
    "PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA": "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
}
PHASE4_RUNTIME_ATOMIC64_PACKET_BLOB_TARGETS = {
    "phase4_build_blob_sha": "zigux/tests/phase4_build.zig",
    "phase4_validator_blob_sha": "scripts/zigux/validate-phase4.py",
    "phase4_validation_matrix_blob_sha": "Documentation/zigux/phase4-validation-matrix.md",
    "phase9_build_blob_sha": "zigux/tests/phase9_build.zig",
}
SELF_TEST_CASES = [
    "baseline_round_trip",
    "shipped_target_count_drift",
    "missing_exact_readback_heading",
    "validator_blob_pin_drift",
    "phase4_build_manifest_blob_pin_drift",
    "phase4_build_survey_blob_pin_drift",
    "phase9_build_manifest_blob_pin_drift",
    "phase9_build_survey_blob_pin_drift",
    "gate_evidence_self_test_case_count_drift",
    "gate_evidence_self_test_cases_drift",
    "shared_validator_reruns_gate_evidence_self_test_drift",
    "shared_validator_expected_target_count_drift",
    "shared_validator_expected_self_test_case_count_drift",
    "missing_note_file",
]

REQUIRED_STATUS_LINES = [
    "PHASE4_EVIDENCE_MODE=github_connector_readback",
    "PHASE4_EVIDENCE_SCOPE=rollback_ownership_and_lab_matrix_current_gate_definitions",
    "PHASE4_EXACT_READBACK_REF=master",
    f"PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT={len(PHASE4_GATE_EVIDENCE_BLOB_TARGETS)}",
    f"PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}",
    "PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=" + ",".join(SELF_TEST_CASES),
    "PHASE4_SEPARATE_GATE_EVIDENCE_CHECKER_PRESENT=true",
    "PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_CHECK=true",
    "PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_SELF_TEST=true",
    f"PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT={len(PHASE4_GATE_EVIDENCE_BLOB_TARGETS)}",
    f"PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}",
    "PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=true",
    "PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=false",
    "PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=false",
    "PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=false",
]
REQUIRED_STATUS_PREFIXES = [
    "PHASE4_EVIDENCE_DATE=",
]

REQUIRED_NOTE_MARKERS = [
    "## Exact Readback Evidence",
    "## Current Conclusion",
    "`scripts/zigux/check-phase4-gate-evidence.py`",
    "`zigux/tests/phase4_runtime_atomic64_diff_manifest.json`",
    "`zigux/tests/phase4_runtime_atomic64_diff_survey.zig`",
    "`phase4-runtime-atomic64-diff-survey-tests`",
    "`phase4-bitmap-live-helper-replay-tests`",
    "`Documentation/zigux/artifact-diff.md`",
    "`Documentation/zigux/README.md`",
    "`zig build phase4-bitmap-live-helper-replay --build-file zigux/tests/phase4_build.zig`",
    "manifest-backed runtime atomic64 survey pair now pins the same current `phase4_build.zig`, `validate-phase4.py`, `phase4-validation-matrix.md`, and `phase9_build.zig` blobs that this note names",
    "`samples/zigux/kprobe_example.zig` remains absent",
    "`samples/zigux/test_fsmount.zig` remains absent",
    "hard perf thresholds for the shipped atomic64 and bitmap rollback gates remain intentionally unapproved",
]


def git_blob_sha1(payload: bytes) -> str:
    header = f"blob {len(payload)}\0".encode("utf-8")
    return hashlib.sha1(header + payload).hexdigest()


def read_text(root: Path, relative_path: Path | str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def read_bytes(root: Path, relative_path: Path | str) -> bytes:
    return (root / relative_path).read_bytes()


def exact_status_line_count(text: str, status_line: str) -> int:
    return sum(1 for line in text.splitlines() if line == f"- `{status_line}`")


def validate_runtime_atomic64_packet(root: Path) -> list[str]:
    manifest_file = root / MANIFEST_PATH
    survey_file = root / SURVEY_PATH
    missing: list[str] = []

    if not manifest_file.exists():
        return [f"file:{MANIFEST_PATH}"]
    if not survey_file.exists():
        return [f"file:{SURVEY_PATH}"]

    try:
        manifest = json.loads(read_text(root, MANIFEST_PATH))
    except json.JSONDecodeError as exc:
        return [f"phase4_gate_evidence:invalid_runtime_atomic64_manifest:{exc.msg}"]

    survey_text = read_text(root, SURVEY_PATH)
    for field, relative_path in PHASE4_RUNTIME_ATOMIC64_PACKET_BLOB_TARGETS.items():
        expected = git_blob_sha1(read_bytes(root, relative_path))
        actual = manifest.get(field)
        if actual is None:
            missing.append(f"phase4_gate_evidence:missing_runtime_atomic64_manifest_field:{field}")
            continue
        if actual != expected:
            missing.append(
                f"phase4_gate_evidence:runtime_atomic64_manifest_blob:{field}:{actual}:{expected}"
            )
        count = survey_text.count(expected)
        if count != 1:
            missing.append(
                f"phase4_gate_evidence:runtime_atomic64_survey_blob_exact_count:{field}:{expected}:{count}"
            )

    return missing


def validate_root(root: Path) -> list[str]:
    note_file = root / NOTE_PATH
    if not note_file.exists():
        return [f"file:{NOTE_PATH}"]

    note_text = read_text(root, NOTE_PATH)
    missing: list[str] = []

    for status_prefix in REQUIRED_STATUS_PREFIXES:
        count = sum(
            1
            for line in note_text.splitlines()
            if line.startswith("- `") and line.endswith("`") and line[3:-1].startswith(status_prefix)
        )
        if count != 1:
            missing.append(f"phase4_gate_evidence:status_prefix_exact_count:{status_prefix}:{count}")

    for status_line in REQUIRED_STATUS_LINES:
        count = exact_status_line_count(note_text, status_line)
        if count != 1:
            missing.append(f"phase4_gate_evidence:status_exact_count:{status_line}:{count}")

    for marker in REQUIRED_NOTE_MARKERS:
        if marker not in note_text:
            missing.append(f"phase4_gate_evidence:{marker}")

    for marker, relative_path in PHASE4_GATE_EVIDENCE_BLOB_TARGETS.items():
        target = root / relative_path
        if not target.exists():
            missing.append(f"file:{relative_path}")
            continue
        digest = git_blob_sha1(read_bytes(root, relative_path))
        count = exact_status_line_count(note_text, f"{marker}={digest}")
        if count != 1:
            missing.append(f"phase4_gate_evidence:blob_exact_count:{marker}:{digest}:{count}")

    missing.extend(validate_runtime_atomic64_packet(root))
    return missing


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def build_fixture_note(root: Path) -> str:
    lines = [
        "# Phase 4 Gate Evidence",
        "This note records one exact readback snapshot for the current Phase 4 rollback-ownership and lab-matrix gate definitions.",
        "",
        "## Status",
        "- `PHASE4_EVIDENCE_DATE=2026-05-05`",
        "- `PHASE4_EVIDENCE_MODE=github_connector_readback`",
        "- `PHASE4_EVIDENCE_SCOPE=rollback_ownership_and_lab_matrix_current_gate_definitions`",
        "- `PHASE4_EXACT_READBACK_REF=master`",
    ]
    for marker, relative_path in PHASE4_GATE_EVIDENCE_BLOB_TARGETS.items():
        digest = git_blob_sha1(read_bytes(root, relative_path))
        lines.append(f"- `{marker}={digest}`")
    lines.extend(
        [
            f"- `PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT={len(PHASE4_GATE_EVIDENCE_BLOB_TARGETS)}`",
            f"- `PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}`",
            "- `PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=" + ",".join(SELF_TEST_CASES) + "`",
            "- `PHASE4_SEPARATE_GATE_EVIDENCE_CHECKER_PRESENT=true`",
            "- `PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_CHECK=true`",
            "- `PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_SELF_TEST=true`",
            "- `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT="
            + str(len(PHASE4_GATE_EVIDENCE_BLOB_TARGETS))
            + "`",
            "- `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT="
            + str(len(SELF_TEST_CASES))
            + "`",
            "- `PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=true`",
            "- `PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=false`",
            "- `PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=false`",
            "- `PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=false`",
            "",
            "## Exact Readback Evidence",
            "- `Documentation/zigux/artifact-diff.md` and `Documentation/zigux/README.md` stay aligned with the shipped packet.",
            "- `scripts/zigux/check-phase4-gate-evidence.py` now exact-counts the current narrower packet.",
            "- `zigux/tests/phase4_runtime_atomic64_diff_manifest.json` and `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` remain the manifest-backed runtime atomic64 survey pair.",
            "- The shared build still exposes `phase4-runtime-atomic64-diff-survey-tests` and `phase4-bitmap-live-helper-replay-tests`.",
            "- The current helper-backed bitmap rollback lab replay route remains `zig build phase4-bitmap-live-helper-replay --build-file zigux/tests/phase4_build.zig`, matching the live helper-backed row in `Documentation/zigux/phase4-validation-matrix.md`.",
            "- The exact-readback set is now current for the shipped validator-backed packet, and the manifest-backed runtime atomic64 survey pair now pins the same current `phase4_build.zig`, `validate-phase4.py`, `phase4-validation-matrix.md`, and `phase9_build.zig` blobs that this note names.",
            "- Current `master` still treats the missing roadmap-backed sample gates as gaps: `samples/zigux/kprobe_example.zig` remains absent and `samples/zigux/test_fsmount.zig` remains absent.",
            "",
            "## Current Conclusion",
            "- hard perf thresholds for the shipped atomic64 and bitmap rollback gates remain intentionally unapproved.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_runtime_atomic64_packet_fixture(root: Path) -> None:
    manifest = {
        field: git_blob_sha1(read_bytes(root, relative_path))
        for field, relative_path in PHASE4_RUNTIME_ATOMIC64_PACKET_BLOB_TARGETS.items()
    }
    write_text(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
    write_text(
        root / SURVEY_PATH,
        "\n".join(
            [
                'const std = @import("std");',
                "",
                'test "fixture keeps current phase4 build, validator, matrix, and phase9 build pins" {',
                f"    // phase4 build pin {manifest['phase4_build_blob_sha']}",
                f"    // validator pin {manifest['phase4_validator_blob_sha']}",
                f"    // matrix pin {manifest['phase4_validation_matrix_blob_sha']}",
                f"    // phase9 build pin {manifest['phase9_build_blob_sha']}",
                "}",
                "",
            ]
        ),
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase4_gate_evidence_") as tmp_dir:
        root = Path(tmp_dir)

        for relative_path in PHASE4_GATE_EVIDENCE_BLOB_TARGETS.values():
            write_text(root / relative_path, f"fixture for {relative_path}\n")
        for relative_path in PHASE4_RUNTIME_ATOMIC64_PACKET_BLOB_TARGETS.values():
            write_text(root / relative_path, f"fixture for {relative_path}\n")

        write_runtime_atomic64_packet_fixture(root)
        write_text(root / NOTE_PATH, build_fixture_note(root))

        missing = validate_root(root)
        assert not missing, missing

        note_text = read_text(root, NOTE_PATH)
        write_text(
            root / NOTE_PATH,
            note_text.replace(
                f"PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT={len(PHASE4_GATE_EVIDENCE_BLOB_TARGETS)}",
                "PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT=15",
                1,
            ),
        )
        missing = validate_root(root)
        assert missing == [
            "phase4_gate_evidence:status_exact_count:PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT=16:0"
        ], missing

        write_text(root / NOTE_PATH, build_fixture_note(root))
        write_text(
            root / NOTE_PATH,
            read_text(root, NOTE_PATH).replace("## Exact Readback Evidence\n", "", 1),
        )
        missing = validate_root(root)
        assert missing == ["phase4_gate_evidence:## Exact Readback Evidence"], missing

        write_text(root / NOTE_PATH, build_fixture_note(root))
        validator_blob_sha = git_blob_sha1(
            read_bytes(root, PHASE4_GATE_EVIDENCE_BLOB_TARGETS["PHASE4_VALIDATOR_BLOB_SHA"])
        )
        write_text(
            root / NOTE_PATH,
            read_text(root, NOTE_PATH).replace(
                f"PHASE4_VALIDATOR_BLOB_SHA={validator_blob_sha}",
                "PHASE4_VALIDATOR_BLOB_SHA=0000000000000000000000000000000000000000",
                1,
            ),
        )
        missing = validate_root(root)
        assert missing == [
            f"phase4_gate_evidence:blob_exact_count:PHASE4_VALIDATOR_BLOB_SHA:{validator_blob_sha}:0"
        ], missing

        write_runtime_atomic64_packet_fixture(root)
        write_text(root / NOTE_PATH, build_fixture_note(root))
        manifest = json.loads(read_text(root, MANIFEST_PATH))
        phase4_build_sha = git_blob_sha1(
            read_bytes(root, PHASE4_RUNTIME_ATOMIC64_PACKET_BLOB_TARGETS["phase4_build_blob_sha"])
        )
        manifest["phase4_build_blob_sha"] = "0000000000000000000000000000000000000000"
        write_text(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        manifest_blob_sha = git_blob_sha1(read_bytes(root, MANIFEST_PATH))
        missing = validate_root(root)
        assert missing == [
            "phase4_gate_evidence:blob_exact_count:PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA:"
            f"{manifest_blob_sha}:0",
            "phase4_gate_evidence:runtime_atomic64_manifest_blob:phase4_build_blob_sha:"
            "0000000000000000000000000000000000000000:"
            f"{phase4_build_sha}",
        ], missing

        write_runtime_atomic64_packet_fixture(root)
        write_text(root / NOTE_PATH, build_fixture_note(root))
        write_text(
            root / SURVEY_PATH,
            read_text(root, SURVEY_PATH).replace(
                phase4_build_sha, "1111111111111111111111111111111111111111", 1
            ),
        )
        survey_blob_sha = git_blob_sha1(read_bytes(root, SURVEY_PATH))
        missing = validate_root(root)
        assert missing == [
            "phase4_gate_evidence:blob_exact_count:PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA:"
            f"{survey_blob_sha}:0",
            "phase4_gate_evidence:runtime_atomic64_survey_blob_exact_count:"
            f"phase4_build_blob_sha:{phase4_build_sha}:0",
        ], missing

        write_runtime_atomic64_packet_fixture(root)
        write_text(root / NOTE_PATH, build_fixture_note(root))
        manifest = json.loads(read_text(root, MANIFEST_PATH))
        phase9_build_sha = git_blob_sha1(
            read_bytes(root, PHASE4_RUNTIME_ATOMIC64_PACKET_BLOB_TARGETS["phase9_build_blob_sha"])
        )
        manifest["phase9_build_blob_sha"] = "0000000000000000000000000000000000000000"
        write_text(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        manifest_blob_sha = git_blob_sha1(read_bytes(root, MANIFEST_PATH))
        missing = validate_root(root)
        assert missing == [
            "phase4_gate_evidence:blob_exact_count:PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA:"
            f"{manifest_blob_sha}:0",
            "phase4_gate_evidence:runtime_atomic64_manifest_blob:phase9_build_blob_sha:"
            "0000000000000000000000000000000000000000:"
            f"{phase9_build_sha}",
        ], missing

        write_runtime_atomic64_packet_fixture(root)
        write_text(root / NOTE_PATH, build_fixture_note(root))
        write_text(
            root / SURVEY_PATH,
            read_text(root, SURVEY_PATH).replace(
                phase9_build_sha, "2222222222222222222222222222222222222222", 1
            ),
        )
        survey_blob_sha = git_blob_sha1(read_bytes(root, SURVEY_PATH))
        missing = validate_root(root)
        assert missing == [
            "phase4_gate_evidence:blob_exact_count:PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA:"
            f"{survey_blob_sha}:0",
            "phase4_gate_evidence:runtime_atomic64_survey_blob_exact_count:"
            f"phase9_build_blob_sha:{phase9_build_sha}:0",
        ], missing

        write_runtime_atomic64_packet_fixture(root)
        write_text(root / NOTE_PATH, build_fixture_note(root))
        write_text(
            root / NOTE_PATH,
            read_text(root, NOTE_PATH).replace(
                f"PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}",
                "PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=13",
                1,
            ),
        )
        missing = validate_root(root)
        assert missing == [
            "phase4_gate_evidence:status_exact_count:"
            f"PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}:0"
        ], missing

        write_runtime_atomic64_packet_fixture(root)
        write_text(root / NOTE_PATH, build_fixture_note(root))
        write_text(
            root / NOTE_PATH,
            read_text(root, NOTE_PATH).replace(
                "PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=" + ",".join(SELF_TEST_CASES),
                "PHASE4_GATE_EVIDENCE_SELF_TEST_CASES="
                + ",".join(SELF_TEST_CASES[:-1]),
                1,
            ),
        )
        missing = validate_root(root)
        assert missing == [
            "phase4_gate_evidence:status_exact_count:"
            "PHASE4_GATE_EVIDENCE_SELF_TEST_CASES="
            + ",".join(SELF_TEST_CASES)
            + ":0"
        ], missing

        write_runtime_atomic64_packet_fixture(root)
        write_text(root / NOTE_PATH, build_fixture_note(root))
        write_text(
            root / NOTE_PATH,
            read_text(root, NOTE_PATH).replace(
                "PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_SELF_TEST=true",
                "PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_SELF_TEST=false",
                1,
            ),
        )
        missing = validate_root(root)
        assert missing == [
            "phase4_gate_evidence:status_exact_count:"
            "PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_SELF_TEST=true:0"
        ], missing

        write_runtime_atomic64_packet_fixture(root)
        write_text(root / NOTE_PATH, build_fixture_note(root))
        write_text(
            root / NOTE_PATH,
            read_text(root, NOTE_PATH).replace(
                f"PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT={len(PHASE4_GATE_EVIDENCE_BLOB_TARGETS)}",
                "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=15",
                1,
            ),
        )
        missing = validate_root(root)
        assert missing == [
            "phase4_gate_evidence:status_exact_count:"
            f"PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT={len(PHASE4_GATE_EVIDENCE_BLOB_TARGETS)}:0"
        ], missing

        write_runtime_atomic64_packet_fixture(root)
        write_text(root / NOTE_PATH, build_fixture_note(root))
        write_text(
            root / NOTE_PATH,
            read_text(root, NOTE_PATH).replace(
                f"PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}",
                "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=13",
                1,
            ),
        )
        missing = validate_root(root)
        assert missing == [
            "phase4_gate_evidence:status_exact_count:"
            f"PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}:0"
        ], missing

        write_text(root / NOTE_PATH, build_fixture_note(root))
        (root / NOTE_PATH).unlink()
        missing = validate_root(root)
        assert missing == [f"file:{NOTE_PATH}"], missing

    print("PHASE4_GATE_EVIDENCE_SELF_TEST=pass")
    print(f"PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}")
    print("PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=" + ",".join(SELF_TEST_CASES))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the live Phase 4 gate-evidence note against the current shipped packet."
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
