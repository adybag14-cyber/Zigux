#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parents[2] if len(SCRIPT_PATH.parents) > 2 else SCRIPT_PATH.parent
SHARED_SURVEYED_COMMIT = "3ba64cd4e41a4de1c8fd8dbaecb23702ad9701a3"
SURVEYED_COMMIT_MANIFESTS = [
    "zigux/tests/phase4_runtime_atomic64_diff_manifest.json",
    "zigux/tests/phase4_kprobe_example_manifest.json",
    "zigux/tests/phase4_test_fsmount_manifest.json",
    "zigux/tests/phase4_perf_baseline_manifest.json",
]
SURVEYED_COMMIT_SURVEYS = [
    "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
    "zigux/tests/phase4_kprobe_example_survey.zig",
    "zigux/tests/phase4_test_fsmount_survey.zig",
    "zigux/tests/phase4_perf_baseline_survey.zig",
]

REQUIRED_MARKERS = [
    "PHASE4_EVIDENCE_DATE=",
    "PHASE4_EVIDENCE_MODE=github_connector_readback",
    "PHASE4_EVIDENCE_SCOPE=rollback_ownership_and_lab_matrix_current_gate_definitions",
    "PHASE4_EXACT_READBACK_HEAD=",
    "PHASE4_SHARED_SURVEYED_COMMIT=",
    "PHASE4_VALIDATOR_SELF_TEST=pass",
    "PHASE4_VALIDATION=pass",
    "PHASE4_REQUIRED_FILE_COUNT=",
    "PHASE4_REQUIRED_MARKER_COUNT=",
    "PHASE4_GATE_EVIDENCE_SELF_TEST=pass",
    "PHASE4_GATE_EVIDENCE_CHECK=pass",
    "PHASE4_WORKFLOW_ROUTE_CHECKER_BLOB_SHA=",
    "PHASE4_GATE_EVIDENCE_TARGET_COUNT=",
    "## Exact Readback Evidence",
    "## Current Conclusion",
]

REQUIRED_ARTIFACT_DIFF_CONTRACT_STATUS_MARKERS = [
    "ARTIFACT_DIFF_CONTRACT_SELF_TEST=pass",
    "ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT=9",
    "ARTIFACT_DIFF_CONTRACT=pass",
    "ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT=23",
    "ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT=4",
    "ARTIFACT_DIFF_CONTRACT_CASE_COUNT=27",
]

REQUIRED_SURVEY_ALIGNMENT_MARKERS = [
    "phase4_kprobe_example_survey.zig",
    "phase4_test_fsmount_survey.zig",
    "phase4_perf_baseline_survey.zig",
    "phase4_runtime_atomic64_diff_survey.zig",
]

REQUIRED_SELF_TEST_ROUTE_MARKERS = [
    "Self-test Phase 4 validator",
    "python3 scripts/zigux/validate-phase4.py --self-test",
    "Validate Phase 4 diff gates",
    "Run Phase 4 diff tests",
]

REQUIRED_WORKFLOW_ROUTE_STATUS_MARKERS = [
    "PHASE4_WORKFLOW_ROUTE_COUNTS_SELF_TEST=pass",
    "PHASE4_WORKFLOW_ROUTE_COUNTS=pass",
    "PHASE4_WORKFLOW_ROUTE_COUNTS_REQUIRED_FILE_COUNT=",
    "PHASE4_WORKFLOW_ROUTE_COUNTS_REQUIRED_CHECK_COUNT=",
]

REQUIRED_KPROBE_SURVEY_STATUS_MARKERS = [
    "make -C zigux phase4-kprobe-example-survey",
    "phase4-kprobe-example-survey-tests",
    "shared validator now fails closed on the kprobe survey packet itself",
]

EXACT_WORKFLOW_RUN_COUNT_MARKERS = [
    "one `make -C zigux phase4-validate` run line",
    "one `make -C zigux phase4-test` run line",
]

EXACT_WORKFLOW_RUN_COUNT_EXPECTATIONS = {
    "make -C zigux phase4-validate": 1,
    "make -C zigux phase4-test": 1,
}

REQUIRED_RUNTIME_ATOMIC64_REVERSIBLE_DELIVERY_MARKERS = [
    "`lib/atomic64_test.c` stays the source of truth",
    "removing `atomic64_diff.zig` from the shared `phase4_build.zig` entrypoint is the documented rollback move",
    "`runtime_atomic64_diff.zig` remains the single replay body",
    "the existing Phase 9 runtime atomic64 starter remains the forward path",
]

REQUIRED_PERF_BASELINE_PENDING_THRESHOLD_PLAN_MARKERS = [
    "pending threshold-plan record per shipped rollback gate",
    "`make -C zigux phase4-runtime-atomic64-diff`",
    "`make -C zigux phase4-bitmap-diff`",
    "still-unapproved benchmark-command and acceptable-limit placeholders",
]

REQUIRED_SCRIPTS_ROOT_RUNTIME_ATOMIC64_MARKERS = [
    "`make -C zigux phase4-runtime-atomic64-diff`",
    "`phase4-runtime-atomic64-diff-tests`",
]

SCRIPTS_ROOT_BITMAP_ROUTE_LINE_PREFIX = (
    "the shared validator and `scripts/zigux/check-phase4-gate-evidence.py` "
    "now both exact-count the scripts-root"
)

REQUIRED_SCRIPTS_ROOT_BITMAP_ROUTE_MARKERS = [
    "`make -C zigux phase4-bitmap-diff`",
    "`phase4-bitmap-diff-tests`",
]

EXACT_VALIDATOR_STATUS_LINES = [
    "PHASE4_VALIDATOR_SELF_TEST=pass",
    "PHASE4_VALIDATION=pass",
    "PHASE4_REQUIRED_FILE_COUNT=27",
    "PHASE4_REQUIRED_MARKER_COUNT=64",
]

PHASE4_GATE_EVIDENCE_BLOB_TARGETS = {
    "PHASE4_VALIDATION_MATRIX_BLOB_SHA": "Documentation/zigux/phase4-validation-matrix.md",
    "PHASE4_VALIDATOR_BLOB_SHA": "scripts/zigux/validate-phase4.py",
    "PHASE4_GATE_EVIDENCE_CHECKER_BLOB_SHA": "scripts/zigux/check-phase4-gate-evidence.py",
    "PHASE4_WORKFLOW_ROUTE_CHECKER_BLOB_SHA": "scripts/zigux/check-phase4-workflow-route-counts.py",
    "PHASE4_BUILD_BLOB_SHA": "zigux/tests/phase4_build.zig",
    "PHASE4_MAKEFILE_BLOB_SHA": "zigux/Makefile",
    "PHASE4_WORKFLOW_BLOB_SHA": ".github/workflows/zigux-bootstrap.yml",
    "PHASE4_KPROBE_EXAMPLE_MANIFEST_BLOB_SHA": "zigux/tests/phase4_kprobe_example_manifest.json",
    "PHASE4_KPROBE_EXAMPLE_SURVEY_BLOB_SHA": "zigux/tests/phase4_kprobe_example_survey.zig",
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

def read_json(root: Path, relative_path: str) -> dict[str, object]:
    return json.loads(read_text(root, relative_path))

def is_hex_sha(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 40
        and all(ch in "0123456789abcdef" for ch in value)
    )

def collect_shared_surveyed_commit_markers(root: Path, gate_evidence: str) -> list[str]:
    missing: list[str] = []
    shared_commit: str | None = None
    for relative_path in SURVEYED_COMMIT_MANIFESTS:
        target = root / relative_path
        if not target.exists():
            missing.append(f"file:{relative_path}")
            continue
        manifest = read_json(root, relative_path)
        surveyed_commit = manifest.get("surveyed_commit")
        if not is_hex_sha(surveyed_commit):
            missing.append(f"phase4_gate_evidence:surveyed_commit:{relative_path}")
            continue
        if shared_commit is None:
            shared_commit = surveyed_commit
        elif surveyed_commit != shared_commit:
            missing.append(
                "phase4_gate_evidence:shared_surveyed_commit_mismatch:"
                f"{relative_path}:{surveyed_commit}:{shared_commit}"
            )
    if shared_commit is not None:
        expected_survey_marker = f'const current_surveyed_commit = "{shared_commit}"'
        survey_prefix = 'const current_surveyed_commit = "'
        for relative_path in SURVEYED_COMMIT_SURVEYS:
            target = root / relative_path
            if not target.exists():
                missing.append(f"file:{relative_path}")
                continue
            survey_text = read_text(root, relative_path)
            if expected_survey_marker in survey_text:
                continue
            start = survey_text.find(survey_prefix)
            if start == -1:
                missing.append(f"phase4_gate_evidence:surveyed_commit:{relative_path}")
                continue
            value_start = start + len(survey_prefix)
            value_end = survey_text.find('"', value_start)
            if value_end == -1:
                missing.append(f"phase4_gate_evidence:surveyed_commit:{relative_path}")
                continue
            surveyed_commit = survey_text[value_start:value_end]
            if not is_hex_sha(surveyed_commit):
                missing.append(f"phase4_gate_evidence:surveyed_commit:{relative_path}")
                continue
            missing.append(
                "phase4_gate_evidence:shared_surveyed_commit_mismatch:"
                f"{relative_path}:{surveyed_commit}:{shared_commit}"
            )
    if shared_commit is not None and shared_commit not in gate_evidence:
        missing.append(f"phase4_gate_evidence:{shared_commit}")
    return missing

def collect_exact_workflow_run_count_markers(workflow: str, gate_evidence: str) -> list[str]:
    missing: list[str] = []
    for marker in EXACT_WORKFLOW_RUN_COUNT_MARKERS:
        if marker not in gate_evidence:
            missing.append(f"phase4_gate_evidence:exact_workflow_count:{marker}")
    for command, expected_count in EXACT_WORKFLOW_RUN_COUNT_EXPECTATIONS.items():
        actual_count = workflow.count(command)
        if actual_count != expected_count:
            missing.append(f"workflow_exact_count:{command}:{actual_count}:{expected_count}")
    return missing

def collect_scripts_root_bitmap_route_markers(gate_evidence: str) -> list[str]:
    missing: list[str] = []
    matching_lines = [
        line for line in gate_evidence.splitlines()
        if SCRIPTS_ROOT_BITMAP_ROUTE_LINE_PREFIX in line
    ]
    if len(matching_lines) != 1:
        missing.append(
            "phase4_gate_evidence:scripts_root_bitmap_route_line_count:"
            f"{len(matching_lines)}"
        )
        if not matching_lines:
            return missing
    route_line = matching_lines[0]
    for marker in REQUIRED_SCRIPTS_ROOT_BITMAP_ROUTE_MARKERS:
        actual_count = route_line.count(marker)
        if actual_count != 1:
            missing.append(
                "phase4_gate_evidence:scripts_root_bitmap_route:"
                f"{marker}:{actual_count}"
            )
    return missing

def validate_root(root: Path) -> list[str]:
    missing: list[str] = []
    gate_evidence_path = "Documentation/zigux/phase4-gate-evidence.md"
    if not (root / gate_evidence_path).exists():
        return [f"file:{gate_evidence_path}"]
    gate_evidence = read_text(root, gate_evidence_path)
    workflow_path = ".github/workflows/zigux-bootstrap.yml"
    workflow_target = root / workflow_path
    workflow: str | None = None
    if not workflow_target.exists():
        missing.append(f"file:{workflow_path}")
    else:
        workflow = read_text(root, workflow_path)
    for marker in REQUIRED_MARKERS:
        if marker not in gate_evidence:
            missing.append(f"phase4_gate_evidence:{marker}")
    for marker in REQUIRED_ARTIFACT_DIFF_CONTRACT_STATUS_MARKERS:
        if f"- `{marker}`" not in gate_evidence:
            missing.append(f"phase4_gate_evidence:artifact_diff_contract:{marker}")
    for marker in REQUIRED_SURVEY_ALIGNMENT_MARKERS:
        if marker not in gate_evidence:
            missing.append(f"phase4_gate_evidence:{marker}")
    missing.extend(collect_shared_surveyed_commit_markers(root, gate_evidence))
    for marker in REQUIRED_SELF_TEST_ROUTE_MARKERS:
        if marker not in gate_evidence:
            missing.append(f"phase4_gate_evidence:{marker}")
    for marker in REQUIRED_WORKFLOW_ROUTE_STATUS_MARKERS:
        if marker not in gate_evidence:
            missing.append(f"phase4_gate_evidence:{marker}")
    if workflow is not None:
        missing.extend(collect_exact_workflow_run_count_markers(workflow, gate_evidence))
    for marker in REQUIRED_RUNTIME_ATOMIC64_REVERSIBLE_DELIVERY_MARKERS:
        if marker not in gate_evidence:
            missing.append(f"phase4_gate_evidence:runtime_atomic64_reversible_delivery:{marker}")
    for marker in REQUIRED_PERF_BASELINE_PENDING_THRESHOLD_PLAN_MARKERS:
        if marker not in gate_evidence:
            missing.append(f"phase4_gate_evidence:perf_baseline_pending_threshold_plan:{marker}")
    for marker in REQUIRED_SCRIPTS_ROOT_RUNTIME_ATOMIC64_MARKERS:
        if marker not in gate_evidence:
            missing.append(f"phase4_gate_evidence:scripts_root_runtime_atomic64:{marker}")
    missing.extend(collect_scripts_root_bitmap_route_markers(gate_evidence))
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
    expected_target_count_line = f"PHASE4_GATE_EVIDENCE_TARGET_COUNT={len(PHASE4_GATE_EVIDENCE_BLOB_TARGETS)}"
    if expected_target_count_line not in gate_evidence:
        missing.append(f"phase4_gate_evidence:{expected_target_count_line}")
    return missing

def write_fixture_tree(root: Path) -> None:
    minimal_manifest = json.dumps({"surveyed_commit": SHARED_SURVEYED_COMMIT}) + "\n"
    file_contents = {
        "Documentation/zigux/phase4-validation-matrix.md": "phase4 matrix fixture\n",
        "scripts/zigux/validate-phase4.py": "phase4 validator fixture\n",
        "scripts/zigux/check-phase4-gate-evidence.py": "phase4 gate evidence checker fixture\n",
        "scripts/zigux/check-phase4-workflow-route-counts.py": "phase4 workflow route checker fixture\n",
        "zigux/tests/phase4_build.zig": "phase4 build fixture\n",
        "zigux/Makefile": "phase4 validate fixture\n",
        ".github/workflows/zigux-bootstrap.yml": "\n".join(["Validate Phase 4 diff gates","Run Phase 4 diff tests","make -C zigux phase4-validate","make -C zigux phase4-test"]) + "\n",
        "zigux/tests/phase4_kprobe_example_manifest.json": minimal_manifest,
        "zigux/tests/phase4_kprobe_example_survey.zig": f'const current_surveyed_commit = "{SHARED_SURVEYED_COMMIT}";\nphase4 kprobe example survey fixture\n',
        "zigux/tests/phase4_test_fsmount_manifest.json": minimal_manifest,
        "zigux/tests/phase4_test_fsmount_survey.zig": f'const current_surveyed_commit = "{SHARED_SURVEYED_COMMIT}";\nphase4 test_fsmount survey fixture\n',
        "zigux/tests/phase4_perf_baseline_manifest.json": minimal_manifest,
        "zigux/tests/phase4_perf_baseline_survey.zig": f'const current_surveyed_commit = "{SHARED_SURVEYED_COMMIT}";\nphase4 perf baseline survey fixture\n',
        "zigux/tests/phase4_runtime_atomic64_diff_manifest.json": minimal_manifest,
        "zigux/tests/phase4_runtime_atomic64_diff_survey.zig": f'const current_surveyed_commit = "{SHARED_SURVEYED_COMMIT}";\nphase4 runtime atomic64 survey fixture\n',
        "Documentation/zigux/README.md": "phase4 doc readme fixture\n",
        "scripts/zigux/README.md": "phase4 script readme fixture\n",
        "zigux/tests/README.md": "phase4 tests readme fixture\n",
    }
    for relative_path, content_value in file_contents.items():
        target = root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content_value, encoding="utf-8")
    gate_evidence_lines = [
        "# Phase 4 Gate Evidence",
        "",
        "## Status",
        "",
        "- `PHASE4_EVIDENCE_DATE=2026-05-02`",
        "- `PHASE4_EVIDENCE_MODE=github_connector_readback`",
        "- `PHASE4_EVIDENCE_SCOPE=rollback_ownership_and_lab_matrix_current_gate_definitions`",
        "- `PHASE4_EXACT_READBACK_HEAD=d62742e7ff0747ed15f71f67d505f68ea15ec7ab`",
        f"- `PHASE4_SHARED_SURVEYED_COMMIT={SHARED_SURVEYED_COMMIT}`",
        "- `PHASE4_VALIDATOR_SELF_TEST=pass`",
        "- `PHASE4_VALIDATION=pass`",
        "- `PHASE4_REQUIRED_FILE_COUNT=27`",
        "- `PHASE4_REQUIRED_MARKER_COUNT=64`",
        "- `PHASE4_GATE_EVIDENCE_SELF_TEST=pass`",
        "- `PHASE4_GATE_EVIDENCE_CHECK=pass`",
        f"- `PHASE4_GATE_EVIDENCE_TARGET_COUNT={len(PHASE4_GATE_EVIDENCE_BLOB_TARGETS)}`",
        "- `PHASE4_WORKFLOW_ROUTE_COUNTS_SELF_TEST=pass`",
        "- `PHASE4_WORKFLOW_ROUTE_COUNTS=pass`",
        "- `PHASE4_WORKFLOW_ROUTE_COUNTS_REQUIRED_FILE_COUNT=5`",
        "- `PHASE4_WORKFLOW_ROUTE_COUNTS_REQUIRED_CHECK_COUNT=36`",
        "- `ARTIFACT_DIFF_CONTRACT_SELF_TEST=pass`",
        "- `ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT=9`",
        "- `ARTIFACT_DIFF_CONTRACT=pass`",
        "- `ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT=23`",
        "- `ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT=4`",
        "- `ARTIFACT_DIFF_CONTRACT_CASE_COUNT=27`",
        "",
        "## Exact Readback Evidence",
        "",
        f"- synthetic fixture keeps shared surveyed snapshot `{SHARED_SURVEYED_COMMIT}` explicit through `phase4_runtime_atomic64_diff_survey.zig`, `phase4_kprobe_example_survey.zig`, `phase4_test_fsmount_survey.zig`, and `phase4_perf_baseline_survey.zig`.",
        "- synthetic fixture keeps `Self-test Phase 4 validator` plus `python3 scripts/zigux/validate-phase4.py --self-test` explicit beside `Validate Phase 4 diff gates` and `Run Phase 4 diff tests`.",
        "- on the synthetic workflow, there is one `make -C zigux phase4-validate` run line and one `make -C zigux phase4-test` run line under the Phase 4 steps, and the checker keeps those exact counts fail-closed beside the broader route markers.",
        "- synthetic fixture keeps the current artifact-diff contract evidence explicit too: `ARTIFACT_DIFF_CONTRACT_SELF_TEST=pass`, `ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT=9`, `ARTIFACT_DIFF_CONTRACT=pass`, `ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT=23`, `ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT=4`, and `ARTIFACT_DIFF_CONTRACT_CASE_COUNT=27` remain visible in the exact-readback packet instead of being left implicit behind the external checker row.",
        "- synthetic fixture keeps the runtime atomic64 reversible-delivery packet explicit: `lib/atomic64_test.c` stays the source of truth, removing `atomic64_diff.zig` from the shared `phase4_build.zig` entrypoint is the documented rollback move, `runtime_atomic64_diff.zig` remains the single replay body, and the existing Phase 9 runtime atomic64 starter remains the forward path.",
        "- synthetic fixture keeps one pending threshold-plan record per shipped rollback gate explicit, pinning `make -C zigux phase4-runtime-atomic64-diff` and `make -C zigux phase4-bitmap-diff` beside the still-unapproved benchmark-command and acceptable-limit placeholders.",
        "- synthetic fixture keeps the scripts-root runtime atomic64 packet explicit through `make -C zigux phase4-runtime-atomic64-diff` and `phase4-runtime-atomic64-diff-tests` instead of leaving that scripts-root wording implied behind the broader shared-build list.",
        "- synthetic fixture keeps one dedicated scripts-root bitmap replay sentence explicit: the shared validator and `scripts/zigux/check-phase4-gate-evidence.py` now both exact-count the scripts-root `make -C zigux phase4-bitmap-diff` route and the paired `phase4-bitmap-diff-tests` shared-build marker so the restored scripts-root bitmap surface cannot drift behind broader Phase 4 prose.",
        "- synthetic fixture keeps the kprobe survey packet explicit through `make -C zigux phase4-kprobe-example-survey`, `phase4-kprobe-example-survey-tests`, and the now-landed note that the shared validator now fails closed on the kprobe survey packet itself.",
        "",
        "## Current Conclusion",
        "",
        "- synthetic fixture",
    ]
    for marker, relative_path in PHASE4_GATE_EVIDENCE_BLOB_TARGETS.items():
        digest = git_blob_sha1(read_bytes(root, relative_path))
        gate_evidence_lines.insert(26, f"- `{marker}={digest}`")
    (root / "Documentation/zigux/phase4-gate-evidence.md").write_text("\n".join(gate_evidence_lines) + "\n", encoding="utf-8")

def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase4_gate_evidence_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture_tree(root)
        missing = validate_root(root)
        assert not missing, missing
        write_fixture_tree(root)
        gate_evidence = root / "Documentation/zigux/phase4-gate-evidence.md"
        gate_evidence.write_text(gate_evidence.read_text(encoding="utf-8").replace("## Current Conclusion\n", "", 1), encoding="utf-8")
        missing = validate_root(root)
        assert "phase4_gate_evidence:## Current Conclusion" in missing, missing
        write_fixture_tree(root)
        gate_evidence = root / "Documentation/zigux/phase4-gate-evidence.md"
        gate_evidence.write_text(gate_evidence.read_text(encoding="utf-8").replace("PHASE4_VALIDATION=pass", "PHASE4_VALIDATION=fail", 1), encoding="utf-8")
        missing = validate_root(root)
        assert "phase4_gate_evidence:PHASE4_VALIDATION=pass" in missing, missing
        write_fixture_tree(root)
        gate_evidence = root / "Documentation/zigux/phase4-gate-evidence.md"
        gate_evidence.write_text(gate_evidence.read_text(encoding="utf-8").replace("PHASE4_EXACT_READBACK_HEAD=", "PHASE4_EXACT_READBACK_HEAD_MISSING=", 1), encoding="utf-8")
        missing = validate_root(root)
        assert "phase4_gate_evidence:PHASE4_EXACT_READBACK_HEAD=" in missing, missing
        write_fixture_tree(root)
        gate_evidence = root / "Documentation/zigux/phase4-gate-evidence.md"
        old = "PHASE4_VALIDATOR_BLOB_SHA=" + git_blob_sha1(read_bytes(root, "scripts/zigux/validate-phase4.py"))
        gate_evidence.write_text(
            gate_evidence.read_text(encoding="utf-8").replace(old, "PHASE4_VALIDATOR_BLOB_SHA=deadbeef", 1),
            encoding="utf-8",
        )
        missing = validate_root(root)
        expected = "phase4_gate_evidence:PHASE4_VALIDATOR_BLOB_SHA:" + git_blob_sha1(read_bytes(root, "scripts/zigux/validate-phase4.py"))
        assert expected in missing, missing
        write_fixture_tree(root)
        gate_evidence = root / "Documentation/zigux/phase4-gate-evidence.md"
        old = "PHASE4_WORKFLOW_ROUTE_CHECKER_BLOB_SHA=" + git_blob_sha1(read_bytes(root, "scripts/zigux/check-phase4-workflow-route-counts.py"))
        gate_evidence.write_text(
            gate_evidence.read_text(encoding="utf-8").replace(old, "PHASE4_WORKFLOW_ROUTE_CHECKER_BLOB_SHA=deadbeef", 1),
            encoding="utf-8",
        )
        missing = validate_root(root)
        expected = "phase4_gate_evidence:PHASE4_WORKFLOW_ROUTE_CHECKER_BLOB_SHA:" + git_blob_sha1(read_bytes(root, "scripts/zigux/check-phase4-workflow-route-counts.py"))
        assert expected in missing, missing
        write_fixture_tree(root)
        gate_evidence = root / "Documentation/zigux/phase4-gate-evidence.md"
        gate_evidence.write_text(gate_evidence.read_text(encoding="utf-8").replace("PHASE4_REQUIRED_FILE_COUNT=27", "PHASE4_REQUIRED_FILE_COUNT=21", 1), encoding="utf-8")
        missing = validate_root(root)
        assert "phase4_gate_evidence:PHASE4_REQUIRED_FILE_COUNT=27" in missing, missing
        write_fixture_tree(root)
        gate_evidence = root / "Documentation/zigux/phase4-gate-evidence.md"
        gate_evidence.write_text(gate_evidence.read_text(encoding="utf-8").replace("PHASE4_REQUIRED_MARKER_COUNT=64", "PHASE4_REQUIRED_MARKER_COUNT=45", 1), encoding="utf-8")
        missing = validate_root(root)
        assert "phase4_gate_evidence:PHASE4_REQUIRED_MARKER_COUNT=64" in missing, missing
        write_fixture_tree(root)
        gate_evidence = root / "Documentation/zigux/phase4-gate-evidence.md"
        gate_evidence.write_text(
            gate_evidence.read_text(encoding="utf-8").replace(
                "one `make -C zigux phase4-validate` run line",
                "missing `make -C zigux phase4-validate` run line",
                1,
            ),
            encoding="utf-8",
        )
        missing = validate_root(root)
        assert "phase4_gate_evidence:exact_workflow_count:one `make -C zigux phase4-validate` run line" in missing, missing
        write_fixture_tree(root)
        gate_evidence = root / "Documentation/zigux/phase4-gate-evidence.md"
        gate_evidence.write_text(gate_evidence.read_text(encoding="utf-8").replace("PHASE4_WORKFLOW_ROUTE_COUNTS=pass", "PHASE4_WORKFLOW_ROUTE_COUNTS=fail", 1), encoding="utf-8")
        missing = validate_root(root)
        assert "phase4_gate_evidence:PHASE4_WORKFLOW_ROUTE_COUNTS=pass" in missing, missing
        write_fixture_tree(root)
        gate_evidence = root / "Documentation/zigux/phase4-gate-evidence.md"
        gate_evidence.write_text(
            gate_evidence.read_text(encoding="utf-8").replace(
                "PHASE4_WORKFLOW_ROUTE_COUNTS_REQUIRED_FILE_COUNT=5",
                "PHASE4_WORKFLOW_ROUTE_COUNTS_REQUIRED_FILE_COUNT=4",
                1,
            ),
            encoding="utf-8",
        )
        missing = validate_root(root)
        assert (
            "phase4_gate_evidence:PHASE4_WORKFLOW_ROUTE_COUNTS_REQUIRED_FILE_COUNT="
            in " ".join(missing)
        ), missing
        write_fixture_tree(root)
        gate_evidence = root / "Documentation/zigux/phase4-gate-evidence.md"
        gate_evidence.write_text(
            gate_evidence.read_text(encoding="utf-8").replace(
                "PHASE4_WORKFLOW_ROUTE_COUNTS_REQUIRED_CHECK_COUNT=36",
                "PHASE4_WORKFLOW_ROUTE_COUNTS_REQUIRED_CHECK_COUNT=35",
                1,
            ),
            encoding="utf-8",
        )
        missing = validate_root(root)
        assert (
            "phase4_gate_evidence:PHASE4_WORKFLOW_ROUTE_COUNTS_REQUIRED_CHECK_COUNT="
            in " ".join(missing)
        ), missing
        write_fixture_tree(root)
        gate_evidence = root / "Documentation/zigux/phase4-gate-evidence.md"
        gate_evidence.write_text(gate_evidence.read_text(encoding="utf-8").replace("- `ARTIFACT_DIFF_CONTRACT_CASE_COUNT=27`", "- `ARTIFACT_DIFF_CONTRACT_CASE_COUNT=26`", 1), encoding="utf-8")
        missing = validate_root(root)
        assert "phase4_gate_evidence:artifact_diff_contract:ARTIFACT_DIFF_CONTRACT_CASE_COUNT=27" in missing, missing
        write_fixture_tree(root)
        gate_evidence = root / "Documentation/zigux/phase4-gate-evidence.md"
        gate_evidence.write_text(gate_evidence.read_text(encoding="utf-8").replace("`phase4-runtime-atomic64-diff-tests`", "`phase4-runtime-atomic64-diff-missing`", 1), encoding="utf-8")
        missing = validate_root(root)
        assert "phase4_gate_evidence:scripts_root_runtime_atomic64:`phase4-runtime-atomic64-diff-tests`" in missing, missing
        write_fixture_tree(root)
        gate_evidence = root / "Documentation/zigux/phase4-gate-evidence.md"
        gate_evidence.write_text(
            gate_evidence.read_text(encoding="utf-8").replace(
                "the paired `phase4-bitmap-diff-tests` shared-build marker",
                "the paired `phase4-bitmap-diff-missing` shared-build marker",
                1,
            ),
            encoding="utf-8",
        )
        missing = validate_root(root)
        assert (
            "phase4_gate_evidence:scripts_root_bitmap_route:`phase4-bitmap-diff-tests`:0"
            in missing
        ), missing
        write_fixture_tree(root)
        gate_evidence = root / "Documentation/zigux/phase4-gate-evidence.md"
        gate_evidence.write_text(
            gate_evidence.read_text(encoding="utf-8").replace(
                "the scripts-root `make -C zigux phase4-bitmap-diff` route",
                "the scripts-root `make -C zigux phase4-bitmap-diff` route plus `make -C zigux phase4-bitmap-diff` again",
                1,
            ),
            encoding="utf-8",
        )
        missing = validate_root(root)
        assert (
            "phase4_gate_evidence:scripts_root_bitmap_route:`make -C zigux phase4-bitmap-diff`:2"
            in missing
        ), missing
        print("PHASE4_GATE_EVIDENCE_SELF_TEST=pass")
        return 0

def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the Phase 4 gate-evidence blob packet.")
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
