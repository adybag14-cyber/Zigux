#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import tempfile
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parents[2] if len(SCRIPT_PATH.parents) > 2 else SCRIPT_PATH.parent
NOTE_PATH = Path("Documentation/zigux/phase4-gate-evidence.md")
VALIDATOR_PATH = Path("scripts/zigux/validate-phase4.py")

PHASE4_GATE_EVIDENCE_BLOB_TARGETS = {
    "PHASE4_VALIDATION_MATRIX_BLOB_SHA": "Documentation/zigux/phase4-validation-matrix.md",
    "PHASE4_VALIDATOR_BLOB_SHA": "scripts/zigux/validate-phase4.py",
    "PHASE4_GATE_EVIDENCE_CHECKER_BLOB_SHA": "scripts/zigux/check-phase4-gate-evidence.py",
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

REQUIRED_STATUS_PREFIXES = [
    "PHASE4_EVIDENCE_DATE=",
    "PHASE4_EVIDENCE_MODE=github_connector_readback",
    "PHASE4_EVIDENCE_SCOPE=rollback_ownership_and_lab_matrix_current_gate_definitions",
    "PHASE4_EXACT_READBACK_HEAD=",
    "PHASE4_SEPARATE_GATE_EVIDENCE_CHECKER_PRESENT=true",
    "PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=true",
    "PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=false",
    "PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=false",
    "PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=false",
]

REQUIRED_NOTE_MARKERS = [
    "## Exact Readback Evidence",
    "## Current Conclusion",
    "`scripts/zigux/check-phase4-gate-evidence.py`",
    "`zigux/tests/phase4_runtime_atomic64_diff_manifest.json`",
    "`zigux/tests/phase4_runtime_atomic64_diff_survey.zig`",
    "`phase4-runtime-atomic64-diff-survey-tests`",
    "`phase4-bitmap-live-helper-replay-tests`",
    "The three root README summaries",
    "Current `master` does not ship shared-gate blob targets for `phase4_kprobe_example`, `phase4_test_fsmount`, or `phase4_perf_baseline`",
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


def load_validator_module(root: Path):
    validator_path = root / VALIDATOR_PATH
    if not validator_path.exists():
        return None
    spec = importlib.util.spec_from_file_location("zigux_validate_phase4", validator_path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def expected_status_lines(module) -> list[str]:
    return [
        "PHASE4_VALIDATOR_SELF_TEST=pass",
        "PHASE4_VALIDATION=pass",
        f"PHASE4_REQUIRED_FILE_COUNT={len(module.REQUIRED_FILES)}",
        f"PHASE4_REQUIRED_MARKER_COUNT={module.required_marker_count()}",
        "PHASE4_GATE_EVIDENCE_SELF_TEST=pass",
        "PHASE4_GATE_EVIDENCE_CHECK=pass",
        f"PHASE4_GATE_EVIDENCE_TARGET_COUNT={len(PHASE4_GATE_EVIDENCE_BLOB_TARGETS)}",
        "ARTIFACT_DIFF_CONTRACT=pass",
        f"ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT={len(module.EXPECTED_ARTIFACT_DIFF_CONTRACT_BASE_CASES)}",
        f"ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT={len(module.EXPECTED_ARTIFACT_DIFF_CONTRACT_REPEAT_CASES)}",
        f"ARTIFACT_DIFF_CONTRACT_CASE_COUNT={len(module.EXPECTED_ARTIFACT_DIFF_CONTRACT_CASES)}",
    ]


def validate_root(root: Path) -> list[str]:
    note_file = root / NOTE_PATH
    if not note_file.exists():
        return [f"file:{NOTE_PATH}"]

    note_text = read_text(root, NOTE_PATH)
    missing: list[str] = []

    for status_prefix in REQUIRED_STATUS_PREFIXES:
        if f"`{status_prefix}" not in note_text:
            missing.append(f"phase4_gate_evidence:{status_prefix}")

    for marker in REQUIRED_NOTE_MARKERS:
        if marker not in note_text:
            missing.append(f"phase4_gate_evidence:{marker}")

    module = load_validator_module(root)
    if module is None:
        missing.append("phase4_gate_evidence:validator_module_load")
        return missing

    for status_line in expected_status_lines(module):
        count = exact_status_line_count(note_text, status_line)
        if count != 1:
            missing.append(f"phase4_gate_evidence:status_exact_count:{status_line}:{count}")

    for marker, relative_path in PHASE4_GATE_EVIDENCE_BLOB_TARGETS.items():
        target = root / relative_path
        if not target.exists():
            missing.append(f"file:{relative_path}")
            continue
        digest = git_blob_sha1(read_bytes(root, relative_path))
        expected_line = f"- `{marker}={digest}`"
        if expected_line not in note_text:
            missing.append(f"phase4_gate_evidence:{marker}:{digest}")

    return missing


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def build_fixture_note(root: Path, checker_blob_sha: str) -> str:
    module = load_validator_module(root)
    assert module is not None
    status_lines = [
        "# Phase 4 Gate Evidence",
        "This note records one exact readback snapshot for the current Phase 4 rollback-ownership and lab-matrix gate definitions.",
        "",
        "## Status",
        f"- `PHASE4_EVIDENCE_DATE=2026-05-05`",
        "- `PHASE4_EVIDENCE_MODE=github_connector_readback`",
        "- `PHASE4_EVIDENCE_SCOPE=rollback_ownership_and_lab_matrix_current_gate_definitions`",
        "- `PHASE4_EXACT_READBACK_HEAD=ee124761ef3ef5fcc6bb9cd8b7fe8d1fce326839`",
    ]
    for marker, relative_path in PHASE4_GATE_EVIDENCE_BLOB_TARGETS.items():
        digest = checker_blob_sha if marker == "PHASE4_GATE_EVIDENCE_CHECKER_BLOB_SHA" else git_blob_sha1(read_bytes(root, relative_path))
        status_lines.append(f"- `{marker}={digest}`")
    for status_line in expected_status_lines(module):
        status_lines.append(f"- `{status_line}`")
    status_lines.extend(
        [
            "- `PHASE4_SEPARATE_GATE_EVIDENCE_CHECKER_PRESENT=true`",
            "- `PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=true`",
            "- `PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=false`",
            "- `PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=false`",
            "- `PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=false`",
            "",
            "## Exact Readback Evidence",
            "- The current validator-backed Phase 4 packet is the live set recorded directly in `scripts/zigux/validate-phase4.py`: `scripts/zigux/artifact_diff.py`, `scripts/zigux/check-artifact-diff-contract.py`, `scripts/zigux/validate-phase4.py`, `Documentation/zigux/artifact-diff.md`, `Documentation/zigux/phase4-validation-matrix.md`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/atomic64_diff.zig`, `zigux/tests/runtime_atomic64_diff.zig`, `zigux/tests/bitmap_diff.zig`, `zigux/tests/phase4_bitmap_live_helper_replay.zig`, and `zigux/tests/phase4_build.zig`.",
            "- The dedicated gate-evidence checker at `scripts/zigux/check-phase4-gate-evidence.py` now tracks that exact-readback note against the current smaller Phase 4 packet on `master`, including the gate-evidence checker itself, the three root README surfaces, and the manifest-backed runtime atomic64 handoff pair in `zigux/tests/phase4_runtime_atomic64_diff_manifest.json` and `zigux/tests/phase4_runtime_atomic64_diff_survey.zig`.",
            "- The shared build packet on current `master` wires exactly four replay surfaces: `phase4-runtime-atomic64-diff-tests`, `phase4-runtime-atomic64-diff-survey-tests`, `phase4-bitmap-diff-tests`, and `phase4-bitmap-live-helper-replay-tests`.",
            "- `Documentation/zigux/artifact-diff.md`, `Documentation/zigux/phase4-validation-matrix.md`, and `scripts/zigux/validate-phase4.py` agree on the bounded Phase 4 packet: host-side artifact-diff contract replay, the roadmap-facing atomic64 wrapper plus runtime-backed survey handoff, the synthetic bitmap rollback gate, and the helper-backed bitmap replay.",
            "- The three root README summaries still keep the validator route, the roadmap-facing `zigux/tests/atomic64_diff.zig` wrapper, the shared `zigux/tests/runtime_atomic64_diff.zig` replay body, `zigux/tests/bitmap_diff.zig`, and the shared `zigux/tests/phase4_build.zig` route explicit, but they still underdescribe `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` as a distinct shipped Phase 4 replay surface.",
            "- Current `master` does not ship shared-gate blob targets for `phase4_kprobe_example`, `phase4_test_fsmount`, or `phase4_perf_baseline`; the live matrix still treats those as remaining roadmap gaps rather than part of the shipped validator-backed packet pinned here.",
            "",
            "## Current Conclusion",
            "- The current exact-readback packet is limited to the files that live `master` actually ships for rollback ownership, matrix wording, validator wiring, the artifact-diff contract, the shared build route, the bitmap helper replay, the dedicated gate-evidence checker, and the runtime-atomic64 wrapper handoff plus its manifest-backed survey evidence.",
            "- The matrix, validator, shared build entrypoint, artifact-diff note, and dedicated gate-evidence checker are aligned on the current live gate definitions.",
            "- The remaining roadmap-backed gaps are unchanged: `samples/zigux/kprobe_example.zig` remains absent, `samples/zigux/test_fsmount.zig` remains absent, and hard perf thresholds for the shipped atomic64 and bitmap rollback gates remain intentionally unapproved.",
        ]
    )
    return "\n".join(status_lines) + "\n"


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase4_gate_evidence_") as tmp_dir:
        root = Path(tmp_dir)

        for relative_path in PHASE4_GATE_EVIDENCE_BLOB_TARGETS.values():
            write_text(root / relative_path, f"fixture for {relative_path}\n")

        write_text(
            root / VALIDATOR_PATH,
            "REQUIRED_FILES = ['phase4'] * 12\n"
            "EXPECTED_ARTIFACT_DIFF_CONTRACT_BASE_CASES = ['a'] * 21\n"
            "EXPECTED_ARTIFACT_DIFF_CONTRACT_REPEAT_CASES = ['b'] * 4\n"
            "EXPECTED_ARTIFACT_DIFF_CONTRACT_CASES = ['c'] * 25\n\n"
            "def required_marker_count() -> int:\n"
            "    return 54\n",
        )

        checker_blob_sha = git_blob_sha1(read_bytes(root, Path("scripts/zigux/check-phase4-gate-evidence.py")))
        write_text(root / NOTE_PATH, build_fixture_note(root, checker_blob_sha))

        missing = validate_root(root)
        assert not missing, missing

        note_text = read_text(root, NOTE_PATH)
        write_text(root / NOTE_PATH, note_text.replace(checker_blob_sha, "deadbeef", 1))
        missing = validate_root(root)
        assert any(item.startswith("phase4_gate_evidence:PHASE4_GATE_EVIDENCE_CHECKER_BLOB_SHA:") for item in missing), missing

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
