#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import tempfile
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parents[2] if len(SCRIPT_PATH.parents) > 2 else SCRIPT_PATH.parent
NOTE_PATH = Path("Documentation/zigux/phase4-gate-evidence.md")

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

REQUIRED_STATUS_LINES = [
    "PHASE4_EVIDENCE_MODE=github_connector_readback",
    "PHASE4_EVIDENCE_SCOPE=rollback_ownership_and_lab_matrix_current_gate_definitions",
    "PHASE4_EXACT_READBACK_REF=master",
    f"PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT={len(PHASE4_GATE_EVIDENCE_BLOB_TARGETS)}",
    "PHASE4_SEPARATE_GATE_EVIDENCE_CHECKER_PRESENT=true",
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
            "- `PHASE4_SEPARATE_GATE_EVIDENCE_CHECKER_PRESENT=true`",
            "- `PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=true`",
            "- `PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=false`",
            "- `PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=false`",
            "- `PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=false`",
            "",
            "## Exact Readback Evidence",
            "- `Documentation/zigux/artifact-diff.md` and `Documentation/zigux/README.md` stay aligned with the shipped packet.",
            "- `scripts/zigux/check-phase4-gate-evidence.py` now exact-counts the current narrower packet.",
            "- `zigux/tests/phase4_runtime_atomic64_diff_manifest.json` and `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` remain pinned as the manifest-backed runtime atomic64 survey pair.",
            "- The shared build packet still exposes `phase4-runtime-atomic64-diff-survey-tests` and `phase4-bitmap-live-helper-replay-tests`.",
            "- Current `master` still treats the missing roadmap-backed sample gates as gaps: `samples/zigux/kprobe_example.zig` remains absent and `samples/zigux/test_fsmount.zig` remains absent.",
            "",
            "## Current Conclusion",
            "- hard perf thresholds for the shipped atomic64 and bitmap rollback gates remain intentionally unapproved.",
        ]
    )
    return "\n".join(lines) + "\n"


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase4_gate_evidence_") as tmp_dir:
        root = Path(tmp_dir)

        for relative_path in PHASE4_GATE_EVIDENCE_BLOB_TARGETS.values():
            write_text(root / relative_path, f"fixture for {relative_path}\n")

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

    print("PHASE4_GATE_EVIDENCE_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the live Phase 4 gate-evidence note against the current shipped packet.")
    parser.add_argument("--self-test", action="store_true", help="Run the built-in synthetic gate-evidence coverage check.")
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
