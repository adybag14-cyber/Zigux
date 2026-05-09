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
KPROBE_NOTE_PATH = Path("Documentation/zigux/phase4-kprobe-example-gap-survey.md")
KPROBE_MANIFEST_PATH = Path("zigux/tests/phase4_kprobe_example_manifest.json")
KPROBE_SURVEY_PATH = Path("zigux/tests/phase4_kprobe_example_survey.zig")
TEST_FSMOUNT_NOTE_PATH = Path("Documentation/zigux/phase4-test-fsmount-gap-survey.md")
TEST_FSMOUNT_MANIFEST_PATH = Path("zigux/tests/phase4_test_fsmount_manifest.json")
TEST_FSMOUNT_SURVEY_PATH = Path("zigux/tests/phase4_test_fsmount_survey.zig")
PERF_BASELINE_MANIFEST_PATH = Path("zigux/tests/phase4_perf_baseline_manifest.json")
PERF_BASELINE_SURVEY_PATH = Path("zigux/tests/phase4_perf_baseline_survey.zig")

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
    "PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA": str(MANIFEST_PATH),
    "PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA": str(SURVEY_PATH),
}
RUNTIME_PACKET_BLOB_TARGETS = {
    "phase4_build_blob_sha": "zigux/tests/phase4_build.zig",
    "phase4_validator_blob_sha": "scripts/zigux/validate-phase4.py",
    "phase4_validation_matrix_blob_sha": "Documentation/zigux/phase4-validation-matrix.md",
    "phase4_review_checklist_blob_sha": "Documentation/zigux/review-checklist.md",
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
    "bitmap_diff_survey_replay_marker_drift",
    "kprobe_gap_packet_presence_drift",
    "perf_baseline_packet_presence_drift",
    "perf_baseline_note_split_marker_drift",
    "test_fsmount_gap_packet_presence_drift",
    "missing_note_file",
]
PERF_BASELINE_SUMMARY = {
    "phase4_build_step_present": True,
    "phase4_validation_matrix_present": True,
    "shared_phase4_test_step_includes_survey": False,
    "benchmark_command_unapproved": False,
    "acceptable_limit_unapproved": False,
    "atomic64_benchmark_command_approved": True,
    "atomic64_acceptable_limit_approved": True,
    "bitmap_benchmark_command_approved": True,
    "bitmap_acceptable_limit_approved": True,
}


def git_blob_sha1(payload: bytes) -> str:
    return hashlib.sha1(f"blob {len(payload)}\0".encode() + payload).hexdigest()


def read_text(root: Path, relative_path: Path | str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def read_bytes(root: Path, relative_path: Path | str) -> bytes:
    return (root / relative_path).read_bytes()


def exact_status_line_count(text: str, status_line: str) -> int:
    return sum(1 for line in text.splitlines() if line == f"- `{status_line}`")


def validate_runtime_atomic64_packet(root: Path) -> list[str]:
    manifest = json.loads(read_text(root, MANIFEST_PATH))
    survey_text = read_text(root, SURVEY_PATH)
    missing: list[str] = []
    expected_fields = {
        "lane_key": "P4-L02",
        "phase": "Phase 4",
        "owner": "ABI and Runtime Team",
        "rollback_owner": "ABI and Runtime Team",
        "phase4_validator_blob_sha": git_blob_sha1(read_bytes(root, "scripts/zigux/validate-phase4.py")),
        "phase4_validation_matrix_blob_sha": git_blob_sha1(read_bytes(root, "Documentation/zigux/phase4-validation-matrix.md")),
        "phase4_review_checklist_blob_sha": git_blob_sha1(read_bytes(root, "Documentation/zigux/review-checklist.md")),
        "phase9_build_blob_sha": git_blob_sha1(read_bytes(root, "zigux/tests/phase9_build.zig")),
    }
    for field, expected in expected_fields.items():
        if manifest.get(field) != expected:
            missing.append(f"runtime_atomic64_manifest:{field}:{manifest.get(field)}:{expected}")
    sha_counts = {
        git_blob_sha1(read_bytes(root, "zigux/tests/runtime_atomic64_diff.zig")): 2,
        git_blob_sha1(read_bytes(root, "zigux/tests/phase4_build.zig")): 1,
        git_blob_sha1(read_bytes(root, "scripts/zigux/validate-phase4.py")): 1,
        git_blob_sha1(read_bytes(root, "Documentation/zigux/phase4-validation-matrix.md")): 1,
        git_blob_sha1(read_bytes(root, "Documentation/zigux/review-checklist.md")): 1,
        git_blob_sha1(read_bytes(root, "zigux/tests/phase9_build.zig")): 1,
    }
    for sha, expected_count in sha_counts.items():
        actual = survey_text.count(sha)
        if actual != expected_count:
            missing.append(f"runtime_atomic64_survey_sha_count:{sha}:{actual}:{expected_count}")
    for marker in ["approved local benchmark commands", "approved local-only acceptable limits", "shared CI perf promotion"]:
        if marker not in manifest.get("roadmap_gap_summary", "") + manifest.get("ready_next", ""):
            missing.append(f"runtime_atomic64_manifest_marker:{marker}")
    return missing


def validate_perf_baseline_packet(root: Path) -> list[str]:
    manifest = json.loads(read_text(root, PERF_BASELINE_MANIFEST_PATH))
    survey_text = read_text(root, PERF_BASELINE_SURVEY_PATH)
    missing: list[str] = []
    for field, expected in PERF_BASELINE_SUMMARY.items():
        actual = manifest.get("survey_summary", {}).get(field)
        if actual != expected:
            missing.append(f"perf_baseline_summary:{field}:{actual}:{expected}")
    for marker in [
        "phase4 perf baseline survey manifest keeps the current benchmark-command posture explicit",
        "approved_local_only",
        "shared CI perf coverage",
        "131072",
        "8192",
    ]:
        if marker not in survey_text:
            missing.append(f"perf_baseline_survey:{marker}")
    return missing


def validate_gap_packets(root: Path) -> list[str]:
    missing: list[str] = []
    for path in [
        KPROBE_NOTE_PATH,
        KPROBE_MANIFEST_PATH,
        KPROBE_SURVEY_PATH,
        TEST_FSMOUNT_NOTE_PATH,
        TEST_FSMOUNT_MANIFEST_PATH,
        TEST_FSMOUNT_SURVEY_PATH,
    ]:
        if not (root / path).exists():
            missing.append(f"file:{path}")
    return missing


def required_status_lines(root: Path) -> list[str]:
    lines = [
        "PHASE4_EVIDENCE_MODE=github_connector_readback",
        "PHASE4_EVIDENCE_SCOPE=rollback_ownership_and_lab_matrix_current_gate_definitions",
        "PHASE4_EXACT_READBACK_REF=master",
    ]
    for marker, relative_path in PHASE4_GATE_EVIDENCE_BLOB_TARGETS.items():
        lines.append(f"{marker}={git_blob_sha1(read_bytes(root, relative_path))}")
    lines.append(
        "PHASE4_RUNTIME_ATOMIC64_REVIEW_CHECKLIST_BLOB_SHA="
        + git_blob_sha1(read_bytes(root, "Documentation/zigux/review-checklist.md"))
    )
    lines.extend([
        f"PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT={len(PHASE4_GATE_EVIDENCE_BLOB_TARGETS)}",
        f"PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}",
        "PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=" + ",".join(SELF_TEST_CASES),
        "PHASE4_SEPARATE_GATE_EVIDENCE_CHECKER_PRESENT=true",
        "PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_CHECK=true",
        "PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_SELF_TEST=true",
        f"PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT={len(PHASE4_GATE_EVIDENCE_BLOB_TARGETS)}",
        f"PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}",
        "PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=true",
        "PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=true",
        "PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=false",
        "PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=true",
    ])
    return lines


def validate_root(root: Path) -> list[str]:
    note_file = root / NOTE_PATH
    if not note_file.exists():
        return [f"file:{NOTE_PATH}"]
    note_text = read_text(root, NOTE_PATH)
    missing: list[str] = []
    if "## Exact Readback Evidence" not in note_text:
        missing.append("note:missing_exact_readback_heading")
    for line in required_status_lines(root):
        if exact_status_line_count(note_text, line) != 1:
            missing.append(f"note_status:{line}")
    required_markers = [
        "approved local-only command-and-limit evidence",
        "exact-pins the approved local-only command-and-limit evidence for both rollback gates while keeping shared CI perf coverage out of scope",
        "shared perf thresholds for the shipped atomic64 and bitmap rollback gates remain intentionally unapproved",
        "phase4-runtime-atomic64-diff-survey-tests",
        "phase4-bitmap-live-helper-replay-tests",
        "make -C zigux phase4-bitmap-diff-survey",
        "shared gate-evidence note now keeps that adjacent parked packet explicit without claiming a shipped Zig starter",
        "shared validator route now picks that same parked packet up through `scripts/zigux/check-phase4-gate-evidence.py` while `samples/zigux/test_fsmount.zig` remains absent on current `master`",
    ]
    for marker in required_markers:
        if marker not in note_text:
            missing.append(f"note_marker:{marker}")
    missing.extend(validate_runtime_atomic64_packet(root))
    missing.extend(validate_perf_baseline_packet(root))
    missing.extend(validate_gap_packets(root))
    return missing


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def build_fixture_tree(root: Path) -> None:
    fixture_files = {
        "Documentation/zigux/phase4-validation-matrix.md": "validation matrix fixture\n",
        "scripts/zigux/validate-phase4.py": "validator fixture\n",
        "Documentation/zigux/artifact-diff.md": "artifact doc fixture\n",
        "scripts/zigux/check-artifact-diff-contract.py": "contract checker fixture\n",
        "zigux/tests/phase4_build.zig": "phase4 build fixture\n",
        "zigux/Makefile": "makefile fixture\n",
        ".github/workflows/zigux-bootstrap.yml": "workflow fixture\n",
        "Documentation/zigux/README.md": "doc readme fixture\n",
        "scripts/zigux/README.md": "script readme fixture\n",
        "zigux/tests/README.md": "tests readme fixture\n",
        "zigux/tests/atomic64_diff.zig": "atomic64 diff fixture\n",
        "zigux/tests/runtime_atomic64_diff.zig": "runtime atomic64 diff fixture\n",
        "zigux/tests/bitmap_diff.zig": "bitmap diff fixture\n",
        "zigux/tests/phase4_bitmap_live_helper_replay.zig": "bitmap live helper fixture\n",
        "Documentation/zigux/review-checklist.md": "review checklist fixture\n",
        "zigux/tests/phase9_build.zig": "phase9 build fixture\n",
        str(KPROBE_NOTE_PATH): "kprobe note fixture\n",
        str(KPROBE_SURVEY_PATH): "kprobe survey fixture\n",
        str(TEST_FSMOUNT_NOTE_PATH): "test_fsmount note fixture\n",
        str(TEST_FSMOUNT_SURVEY_PATH): "test_fsmount survey fixture\n",
        str(PERF_BASELINE_SURVEY_PATH): "phase4 perf baseline survey manifest keeps the current benchmark-command posture explicit\napproved_local_only\nshared CI perf coverage\n131072\n8192\n",
    }
    for rel, content in fixture_files.items():
        _write(root / rel, content)
    _write(root / KPROBE_MANIFEST_PATH, json.dumps({"shared_gate_evidence_packet_present": True}) + "\n")
    _write(root / TEST_FSMOUNT_MANIFEST_PATH, json.dumps({"shared_gate_evidence_packet_present": False}) + "\n")
    _write(root / PERF_BASELINE_MANIFEST_PATH, json.dumps({"survey_summary": PERF_BASELINE_SUMMARY}) + "\n")
    rt_manifest = {
        "lane_key": "P4-L02",
        "phase": "Phase 4",
        "owner": "ABI and Runtime Team",
        "rollback_owner": "ABI and Runtime Team",
        "roadmap_gap_summary": "approved local benchmark commands approved local-only acceptable limits",
        "ready_next": "shared CI perf promotion",
    }
    for field, rel in RUNTIME_PACKET_BLOB_TARGETS.items():
        rt_manifest[field] = git_blob_sha1(read_bytes(root, rel))
    _write(root / MANIFEST_PATH, json.dumps(rt_manifest) + "\n")
    rt_survey = "\n".join([
        git_blob_sha1(read_bytes(root, "zigux/tests/runtime_atomic64_diff.zig")),
        git_blob_sha1(read_bytes(root, "zigux/tests/runtime_atomic64_diff.zig")),
        git_blob_sha1(read_bytes(root, "zigux/tests/phase4_build.zig")),
        git_blob_sha1(read_bytes(root, "scripts/zigux/validate-phase4.py")),
        git_blob_sha1(read_bytes(root, "Documentation/zigux/phase4-validation-matrix.md")),
        git_blob_sha1(read_bytes(root, "Documentation/zigux/review-checklist.md")),
        git_blob_sha1(read_bytes(root, "zigux/tests/phase9_build.zig")),
    ]) + "\n"
    _write(root / SURVEY_PATH, rt_survey)
    status_lines = "\n".join(f"- `{line}`" for line in required_status_lines(root))
    note = (
        "# Phase 4 Gate Evidence\n\n## Status\n"
        + status_lines
        + "\n\n## Exact Readback Evidence\napproved local-only command-and-limit evidence\nexact-pins the approved local-only command-and-limit evidence for both rollback gates while keeping shared CI perf coverage out of scope\nphase4-runtime-atomic64-diff-survey-tests\nphase4-bitmap-live-helper-replay-tests\nmake -C zigux phase4-bitmap-diff-survey\nshared gate-evidence note now keeps that adjacent parked packet explicit without claiming a shipped Zig starter\nshared validator route now picks that same parked packet up through `scripts/zigux/check-phase4-gate-evidence.py` while `samples/zigux/test_fsmount.zig` remains absent on current `master`\n\n## Current Conclusion\nshared perf thresholds for the shipped atomic64 and bitmap rollback gates remain intentionally unapproved\n"
    )
    _write(root / NOTE_PATH, note)


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase4_gate_evidence_") as tmp_dir:
        root = Path(tmp_dir)
        build_fixture_tree(root)
        assert validate_root(root) == []
        bad = Path(tmp_dir) / "bad"
        build_fixture_tree(bad)
        (bad / NOTE_PATH).unlink()
        assert validate_root(bad) == [f"file:{NOTE_PATH}"]

        bad2 = Path(tmp_dir) / "bad2"
        build_fixture_tree(bad2)
        note_path = bad2 / NOTE_PATH
        note_path.write_text(
            note_path.read_text(encoding="utf-8").replace(
                "exact-pins the approved local-only command-and-limit evidence for both rollback gates while keeping shared CI perf coverage out of scope\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        assert validate_root(bad2) == [
            "note_marker:exact-pins the approved local-only command-and-limit evidence for both rollback gates while keeping shared CI perf coverage out of scope"
        ]
    print("PHASE4_GATE_EVIDENCE_SELF_TEST=pass")
    print(f"PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}")
    print("PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=" + ",".join(SELF_TEST_CASES))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    missing = validate_root(ROOT)
    if missing:
        print("PHASE4_GATE_EVIDENCE_CHECK=fail")
        print("PHASE4_GATE_EVIDENCE_TARGETS_START")
        for item in missing:
            print(item)
        print("PHASE4_GATE_EVIDENCE_TARGETS_END")
        return 1
    print("PHASE4_GATE_EVIDENCE_CHECK=pass")
    print(f"PHASE4_GATE_EVIDENCE_TARGET_COUNT={len(PHASE4_GATE_EVIDENCE_BLOB_TARGETS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
