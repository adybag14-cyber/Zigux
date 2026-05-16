#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PHASE2_CROSS_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross.py"
PHASE2_VALIDATOR = ROOT / "scripts" / "zigux" / "validate-phase2.py"
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
MAKEFILE = ROOT / "zigux" / "Makefile"
CLOSURE_DOC = ROOT / "Documentation" / "zigux" / "phase2-closure.md"
BOOTSTRAP_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
DOCS_ROOT_README = ROOT / "Documentation" / "zigux" / "README.md"
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
TARGETS_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"

PHASE2_VALIDATE_TARGET_NAME = "phase2-validate"
PHASE2_VALIDATE_TARGET_HEADER = "phase2-validate: phase2-tools phase2-kconfig"
PHASE2_CROSS_TARGET_NAME = "phase2-cross"
PHASE2_CROSS_TARGET_HEADER = "phase2-cross: phase2-toolchain"
PHASE2_CROSS_WORKFLOW_JOB_NAME = "phase2-cross"

EXPECTED_TARGETS = [
    "x86_64-linux-musl",
    "aarch64-linux-musl",
    "riscv64-linux-musl",
]

EXPECTED_ZIG_TEST_FILES = [
    "scripts/zigux/fixdep.zig",
    "scripts/zigux/genksyms.zig",
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
]

EXACT_WORKFLOW_RUN_COUNTS = {
    "python3 scripts/zigux/check-phase2-cross.py --self-test": 1,
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test": 1,
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py": 1,
    "python3 scripts/zigux/check-phase2-cross.py --target ${{ matrix.zig_target }}": 1,
}

EXACT_MAKEFILE_RUN_COUNTS = {
    "scripts/zigux/check-phase2-cross.py --self-test": 1,
    "scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test": 1,
    "scripts/zigux/check-phase2-cross-selftest-alignment.py": 1,
    "scripts/zigux/check-phase2-cross.py": 1,
}

PHASE2_VALIDATE_TARGET_REQUIRED_LINES = [
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase2-closure.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross-selftest-alignment.py",
]

PHASE2_CROSS_TARGET_REQUIRED_LINES = [
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py",
]

WORKFLOW_SCOPE_REQUIRED_FRAGMENTS = [
    "Documentation/zigux/**",
    "scripts/zigux/**",
    "zigux/**",
    ".github/workflows/zigux-bootstrap.yml",
]

WORKFLOW_SCOPE_PATTERN_MARKERS = [
    "\\.github/workflows/zigux-bootstrap\\.yml",
    "scripts/zigux/install-zig\\.py",
    "scripts/zigux/check-phase2-cross\\.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment\\.py",
    "scripts/zigux/fixdep\\.zig",
    "scripts/zigux/genksyms\\.zig",
    "scripts/zigux/kconfig/conf_bridge\\.zig",
    "scripts/zigux/kconfig/confdata_bridge\\.zig",
    "scripts/zigux/zig-toolchain-policy\\.json",
    "zigux/Makefile",
    "zigux/tests/fixtures/phase2_cross_targets\\.json",
]

PHASE2_CROSS_WORKFLOW_JOB_MARKERS = [
    "      - name: Install Zig",
    "        run: python3 scripts/zigux/install-zig.py --channel 0.17.0-dev.87+9b177a7d2 --dest .zig-toolchain",
    "      - name: Check bounded Phase 2 cross-target compile",
    "        run: python3 scripts/zigux/check-phase2-cross.py --target ${{ matrix.zig_target }}",
]

PHASE2_CROSS_WORKFLOW_JOB_FORBIDDEN_MARKERS = [
    "python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "python3 scripts/zigux/check-zig-toolchain.py",
]

PHASE2_CROSS_CHECKER_MARKERS = [
    'CHECK_ZIG_TOOLCHAIN = ROOT / "scripts" / "zigux" / "check-zig-toolchain.py"',
    "EXPECTED_TARGETS = [",
    "EXPECTED_ZIG_TEST_FILES = [",
    "def run_toolchain_preflight(",
    '[sys.executable, str(root / "scripts" / "zigux" / "check-zig-toolchain.py"), "--zig", zig_executable],',
    '    "scripts/zigux/fixdep.zig",',
    '    "scripts/zigux/genksyms.zig",',
    '    "scripts/zigux/kconfig/conf_bridge.zig",',
    '    "scripts/zigux/kconfig/confdata_bridge.zig",',
    'print("PHASE2_CROSS_SELF_TEST=pass")',
    'print(f"PHASE2_CROSS_TARGET_COUNT={len(targets)}")',
    'print(f"PHASE2_CROSS_FILE_COUNT={len(zig_test_files)}")',
]

PHASE2_VALIDATOR_MARKERS = [
    'ROOT / "scripts" / "zigux" / "check-phase2-cross.py"',
    'ROOT / "scripts" / "zigux" / "check-phase2-cross-selftest-alignment.py"',
    '"zigux/tests/fixtures/phase2_cross_targets.json"',
    '("zig", "test", ROOT / "scripts" / "zigux" / "fixdep.zig")',
    '("zig", "test", ROOT / "scripts" / "zigux" / "genksyms.zig")',
    '("zig", "test", ROOT / "scripts" / "zigux" / "kconfig" / "conf_bridge.zig")',
    '("zig", "test", ROOT / "scripts" / "zigux" / "kconfig" / "confdata_bridge.zig")',
]

BOOTSTRAP_NOTES_MATRIX_BOUNDARY_SENTENCE = (
    "the closure note, tests root, and Makefile keep the committed "
    "`zigux/tests/fixtures/phase2_tool_manifest.json` plus "
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json` packet, the bounded "
    "direct `zig test scripts/zigux/fixdep.zig`, `zig test scripts/zigux/genksyms.zig`, "
    "`zig test scripts/zigux/kconfig/conf_bridge.zig`, and `zig test "
    "scripts/zigux/kconfig/confdata_bridge.zig` replays, and the committed genksyms "
    "bridge fixture plus kconfig manifest packet reviewable without reopening the "
    "dedicated genksyms or kconfig lanes from this bootstrap note"
)

BOOTSTRAP_NOTES_CROSS_WORKFLOW_BOUNDARY_SENTENCE = (
    "the dedicated `phase2-cross` workflow job currently reuses the same pinned installer "
    "path and reaches the live toolchain preflight through `scripts/zigux/check-phase2-cross.py --target <matrix-zig-target>`, "
    "whose target-mode path reruns `scripts/zigux/check-zig-toolchain.py --zig <resolved-zig>` before the cross-target Zig tests, "
    "so bootstrap and cross-target verification now share the same pinned-toolchain gate even though the cross route still adds the "
    "target replay packet on top of that preflight on current `master`"
)

BOOTSTRAP_NOTES_STALE_CROSS_WORKFLOW_BOUNDARY_SENTENCE = (
    "the dedicated `phase2-cross` workflow job currently reuses the same pinned installer "
    "path but stops at installer-side archive verification plus `scripts/zigux/check-phase2-cross.py`, "
    "so the broader closure packet should treat bootstrap and cross-target verification as adjacent "
    "but not identical routes until a later bounded follow-up adds the live checker there too"
)

DOCS_ROOT_README_BOUNDARY_SENTENCE = (
    "the docs-root Phase 2 summary should also keep the current bootstrap-versus-cross "
    "verification split explicit: the dedicated `phase2-cross` workflow job still reuses "
    "the pinned installer path but stops at installer-side archive verification plus "
    "`python3 scripts/zigux/check-phase2-cross.py --target <matrix-zig-target>`, while "
    "the Linux-style `make -C zigux phase2-cross` route still picks up `phase2-toolchain` "
    'and its `python3 scripts/zigux/check-zig-toolchain.py --zig "$(ZIG)"` replay through '
    "`zigux/Makefile`."
)

CLOSURE_MARKERS = [
    "shared cross compile self-test: `python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "shared cross compile gate: `python3 scripts/zigux/check-phase2-cross.py`",
    "shared cross-selftest alignment self-test: `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test`",
    "shared cross-selftest alignment gate: `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "make -C zigux phase2-cross",
    "direct replay owners stay bounded on current `master`: `zig test scripts/zigux/fixdep.zig`, `zig test scripts/zigux/genksyms.zig`, `zig test scripts/zigux/kconfig/conf_bridge.zig`, and `zig test scripts/zigux/kconfig/confdata_bridge.zig` remain the shipped direct Phase 2 Zig replays",
]

BOOTSTRAP_NOTES_MARKERS = [
    "shared cross selftest-alignment self-test: `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test`",
    "shared cross selftest-alignment gate: `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "the three-target compile matrix in `zigux/tests/fixtures/phase2_cross_targets.json` stays separate from the `x86_64-linux` bootstrap archive pin",
    BOOTSTRAP_NOTES_MATRIX_BOUNDARY_SENTENCE,
    BOOTSTRAP_NOTES_CROSS_WORKFLOW_BOUNDARY_SENTENCE,
]

BOOTSTRAP_NOTES_FORBIDDEN_MARKERS = [
    "the direct kconfig and confdata Zig replays reviewable",
    BOOTSTRAP_NOTES_STALE_CROSS_WORKFLOW_BOUNDARY_SENTENCE,
]

DOCS_ROOT_README_MARKERS = [
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    DOCS_ROOT_README_BOUNDARY_SENTENCE,
]

SCRIPTS_README_MARKERS = [
    "shared cross compile self-test: `python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "shared cross compile gate: `python3 scripts/zigux/check-phase2-cross.py`",
    "shared cross-selftest alignment self-test: `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test`",
    "shared cross-selftest alignment gate: `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py`",
]

TESTS_README_MARKERS = [
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "scripts/zigux/genksyms.zig",
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
    "make -C zigux phase2-cross",
]

REVIEW_CHECKLIST_MARKERS = [
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "scripts/zigux/genksyms.zig",
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
]

EXPECTED_SELF_TEST_CASE_COUNT = 93


def load_json_object(path: Path, *, label: str) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit(f"{label}:expected_object")
    return payload


def validate_targets_manifest(payload: dict[str, object]) -> list[str]:
    issues: list[str] = []
    if payload.get("phase") != "Phase 2":
        issues.append(f"targets:phase={payload.get('phase')!r}:expected='Phase 2'")
    if payload.get("status") != "closed":
        issues.append(f"targets:status={payload.get('status')!r}:expected='closed'")
    if payload.get("target_count") != len(EXPECTED_TARGETS):
        issues.append(
            f"targets:target_count={payload.get('target_count')!r}:expected={len(EXPECTED_TARGETS)}"
        )
    targets = payload.get("targets")
    if not isinstance(targets, list):
        issues.append("targets:targets:expected_list")
        return issues
    if targets != EXPECTED_TARGETS:
        issues.append("targets:targets=expected_exact_list")
    zig_test_files = payload.get("zig_test_files")
    if zig_test_files != EXPECTED_ZIG_TEST_FILES:
        issues.append("targets:zig_test_files=expected_exact_list")
    return issues


def validate_required_markers(text: str, *, label: str, markers: list[str]) -> list[str]:
    issues: list[str] = []
    for marker in markers:
        if marker not in text:
            issues.append(f"{label}:missing_marker:{marker}")
    return issues


def validate_forbidden_markers(text: str, *, label: str, markers: list[str]) -> list[str]:
    issues: list[str] = []
    for marker in markers:
        if marker in text:
            issues.append(f"{label}:forbidden_marker:{marker}")
    return issues


def validate_workflow_scope_fragments(text: str) -> list[str]:
    return validate_required_markers(
        text,
        label="workflow_scope",
        markers=WORKFLOW_SCOPE_REQUIRED_FRAGMENTS,
    )


def extract_workflow_scope_pattern(text: str) -> str | None:
    marker = "if printf '%s\\n' \\\"$changed_files\\\" | grep -Eq '"
    start = text.find(marker)
    if start == -1:
        return None
    start += len(marker)
    end = text.find("'; then", start)
    if end == -1:
        return None
    return text[start:end]


def validate_workflow_scope_pattern(text: str) -> list[str]:
    pattern = extract_workflow_scope_pattern(text)
    if pattern is None:
        return ["workflow_scope_pattern:missing"]
    return validate_required_markers(
        pattern,
        label="workflow_scope_pattern",
        markers=WORKFLOW_SCOPE_PATTERN_MARKERS,
    )


def extract_workflow_job_block(text: str, job_name: str) -> str | None:
    header = f"  {job_name}:"
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line == header:
            block: list[str] = [line]
            for following in lines[index + 1 :]:
                if not following:
                    block.append(following)
                    continue
                if not following.startswith("  ") and not following.startswith(" "):
                    break
                if following.startswith("  ") and not following.startswith("    "):
                    break
                block.append(following)
            return "\n".join(block)
    return None


def validate_phase2_cross_workflow_job(text: str) -> list[str]:
    block = extract_workflow_job_block(text, PHASE2_CROSS_WORKFLOW_JOB_NAME)
    if block is None:
        return ["workflow_phase2_cross_job:missing"]
    issues: list[str] = []
    issues.extend(
        validate_required_markers(
            block,
            label="workflow_phase2_cross_job",
            markers=PHASE2_CROSS_WORKFLOW_JOB_MARKERS,
        )
    )
    issues.extend(
        validate_forbidden_markers(
            block,
            label="workflow_phase2_cross_job",
            markers=PHASE2_CROSS_WORKFLOW_JOB_FORBIDDEN_MARKERS,
        )
    )
    return issues


def validate_exact_workflow_runs(text: str) -> list[str]:
    issues: list[str] = []
    for command, expected_count in EXACT_WORKFLOW_RUN_COUNTS.items():
        expected_line = f"run: {command}"
        count = sum(1 for line in text.splitlines() if line.strip() == expected_line)
        if count != expected_count:
            issues.append(f"workflow_exact_run:{command}:count={count}:expected={expected_count}")
    return issues


# Keep the published self-test path tolerant of the older camel-cased helper name.
validate_exact_workflowRuns = validate_exact_workflow_runs


def validate_exact_makefile_runs(text: str) -> list[str]:
    issues: list[str] = []
    for command, expected_count in EXACT_MAKEFILE_RUN_COUNTS.items():
        count = sum(1 for line in text.splitlines() if line.strip().endswith(command))
        if count != expected_count:
            issues.append(f"makefile_exact_run:{command}:count={count}:expected={expected_count}")
    return issues


def extract_makefile_target_block(text: str, target_name: str) -> tuple[str, list[str]] | None:
    target_header = f"{target_name}:"
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.startswith(target_header):
            commands: list[str] = []
            for following in lines[index + 1 :]:
                if following.startswith("\t"):
                    commands.append(following.strip())
                    continue
                if not following.strip():
                    continue
                break
            return line.strip(), commands
    return None


def validate_makefile_target_scope(text: str) -> list[str]:
    issues: list[str] = []

    validate_block = extract_makefile_target_block(text, PHASE2_VALIDATE_TARGET_NAME)
    if validate_block is None:
        issues.append(f"makefile_target_missing:{PHASE2_VALIDATE_TARGET_NAME}")
    else:
        header, commands = validate_block
        if header != PHASE2_VALIDATE_TARGET_HEADER:
            issues.append(
                "makefile_target_scope:"
                f"{PHASE2_VALIDATE_TARGET_NAME}:header={header!r}:expected={PHASE2_VALIDATE_TARGET_HEADER!r}"
            )
        if commands != PHASE2_VALIDATE_TARGET_REQUIRED_LINES:
            issues.append(
                "makefile_target_scope:"
                f"{PHASE2_VALIDATE_TARGET_NAME}:actual={commands!r}:expected={PHASE2_VALIDATE_TARGET_REQUIRED_LINES!r}"
            )

    cross_block = extract_makefile_target_block(text, PHASE2_CROSS_TARGET_NAME)
    if cross_block is None:
        issues.append(f"makefile_target_missing:{PHASE2_CROSS_TARGET_NAME}")
    else:
        header, commands = cross_block
        if header != PHASE2_CROSS_TARGET_HEADER:
            issues.append(
                "makefile_target_scope:"
                f"{PHASE2_CROSS_TARGET_NAME}:header={header!r}:expected={PHASE2_CROSS_TARGET_HEADER!r}"
            )
        if commands != PHASE2_CROSS_TARGET_REQUIRED_LINES:
            issues.append(
                "makefile_target_scope:"
                f"{PHASE2_CROSS_TARGET_NAME}:actual={commands!r}:expected={PHASE2_CROSS_TARGET_REQUIRED_LINES!r}"
            )
    return issues


def run_self_test() -> int:
    checks_run = 0
    valid_targets = {
        "phase": "Phase 2",
        "status": "closed",
        "target_count": 3,
        "targets": list(EXPECTED_TARGETS),
        "zig_test_files": list(EXPECTED_ZIG_TEST_FILES),
    }
    if validate_targets_manifest(valid_targets):
        raise SystemExit("phase2-cross-alignment:self-test:valid_targets_manifest")
    checks_run += 1

    bad_count = dict(valid_targets)
    bad_count["target_count"] = 2
    issues = validate_targets_manifest(bad_count)
    if "targets:target_count=2:expected=3" not in issues:
        raise SystemExit("phase2-cross-alignment:self-test:target_count_mismatch")
    checks_run += 1

    bad_targets = dict(valid_targets)
    bad_targets["targets"] = ["x86_64-linux-musl"]
    issues = validate_targets_manifest(bad_targets)
    if "targets:targets=expected_exact_list" not in issues:
        raise SystemExit("phase2-cross-alignment:self-test:target_list_mismatch")
    checks_run += 1

    bad_zig_test_files = dict(valid_targets)
    bad_zig_test_files["zig_test_files"] = ["scripts/zigux/genksyms.zig"]
    issues = validate_targets_manifest(bad_zig_test_files)
    if "targets:zig_test_files=expected_exact_list" not in issues:
        raise SystemExit("phase2-cross-alignment:self-test:zig_test_file_list_mismatch")
    checks_run += 1

    cross_checker_issues = validate_required_markers(
        "\n".join(PHASE2_CROSS_CHECKER_MARKERS),
        label="phase2_cross_checker",
        markers=PHASE2_CROSS_CHECKER_MARKERS,
    )
    if cross_checker_issues:
        raise SystemExit("phase2-cross-alignment:self-test:cross_checker_marker_presence")
    checks_run += 1

    for marker in PHASE2_CROSS_CHECKER_MARKERS:
        cross_checker_missing = validate_required_markers(
            "\n".join(item for item in PHASE2_CROSS_CHECKER_MARKERS if item != marker),
            label="phase2_cross_checker",
            markers=PHASE2_CROSS_CHECKER_MARKERS,
        )
        expected_cross_checker_issue = f"phase2_cross_checker:missing_marker:{marker}"
        if cross_checker_missing != [expected_cross_checker_issue]:
            raise SystemExit("phase2-cross-alignment:self-test:cross_checker_marker_failure")
        checks_run += 1

    validator_issues = validate_required_markers(
        "\n".join(PHASE2_VALIDATOR_MARKERS),
        label="phase2_validator",
        markers=PHASE2_VALIDATOR_MARKERS,
    )
    if validator_issues:
        raise SystemExit("phase2-cross-alignment:self-test:validator_marker_presence")
    checks_run += 1

    for marker in PHASE2_VALIDATOR_MARKERS:
        validator_missing = validate_required_markers(
            "\n".join(item for item in PHASE2_VALIDATOR_MARKERS if item != marker),
            label="phase2_validator",
            markers=PHASE2_VALIDATOR_MARKERS,
        )
        expected_validator_issue = f"phase2_validator:missing_marker:{marker}"
        if validator_missing != [expected_validator_issue]:
            raise SystemExit("phase2-cross-alignment:self-test:validator_marker_failure")
        checks_run += 1

    workflow_text = "\n".join(
        [
            "run: python3 scripts/zigux/check-phase2-cross.py --self-test",
            "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
            "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
            "run: python3 scripts/zigux/check-phase2-cross.py --target ${{ matrix.zig_target }}",
        ]
    )
    if validate_exact_workflow_runs(workflow_text):
        raise SystemExit("phase2-cross-alignment:self-test:workflow_counts")
    checks_run += 1

    bad_workflow = ""
    issues = validate_exact_workflow_runs(bad_workflow)
    if not any(issue.startswith("workflow_exact_run:") for issue in issues):
        raise SystemExit("phase2-cross-alignment:self-test:workflow_count_failure")
    checks_run += 1

    duplicate_workflow = workflow_text + "\nrun: python3 scripts/zigux/check-phase2-cross.py --self-test"
    duplicate_workflow_issues = validate_exact_workflow_runs(duplicate_workflow)
    expected_duplicate_workflow_issue = (
        "workflow_exact_run:python3 scripts/zigux/check-phase2-cross.py --self-test:count=2:expected=1"
    )
    if duplicate_workflow_issues != [expected_duplicate_workflow_issue]:
        raise SystemExit("phase2-cross-alignment:self-test:workflow_duplicate_failure")
    checks_run += 1

    valid_workflow_job = "\n".join(
        [
            "  phase2-cross:",
            "    if: needs.phase2_cross_scope.outputs.should_run == 'true'",
            "    needs: [bootstrap, phase2_cross_scope]",
            "    runs-on: ubuntu-latest",
            "    steps:",
            "      - name: Install Zig",
            "        run: python3 scripts/zigux/install-zig.py --channel 0.17.0-dev.87+9b177a7d2 --dest .zig-toolchain",
            "      - name: Check bounded Phase 2 cross-target compile",
            "        run: python3 scripts/zigux/check-phase2-cross.py --target ${{ matrix.zig_target }}",
            "",
            "  next-job:",
            "    runs-on: ubuntu-latest",
        ]
    )
    if validate_phase2_cross_workflow_job(valid_workflow_job):
        raise SystemExit("phase2-cross-alignment:self-test:workflow_job_markers")
    checks_run += 1

    missing_workflow_job_issues = validate_phase2_cross_workflow_job("jobs:\n  bootstrap:\n    runs-on: ubuntu-latest")
    if missing_workflow_job_issues != ["workflow_phase2_cross_job:missing"]:
        raise SystemExit("phase2-cross-alignment:self-test:workflow_job_missing")
    checks_run += 1

    for marker in PHASE2_CROSS_WORKFLOW_JOB_MARKERS:
        workflow_job_missing_marker = valid_workflow_job.replace(f"{marker}\n", "", 1)
        expected_workflow_job_marker_issue = (
            f"workflow_phase2_cross_job:missing_marker:{marker}"
        )
        if validate_phase2_cross_workflow_job(workflow_job_missing_marker) != [
            expected_workflow_job_marker_issue
        ]:
            raise SystemExit("phase2-cross-alignment:self-test:workflow_job_marker_failure")
        checks_run += 1

    for marker in PHASE2_CROSS_WORKFLOW_JOB_FORBIDDEN_MARKERS:
        workflow_job_with_forbidden_toolchain_gate = valid_workflow_job.replace(
            "      - name: Check bounded Phase 2 cross-target compile\n",
            "      - name: Check Zig toolchain\n        run: "
            f"{marker}\n"
            "      - name: Check bounded Phase 2 cross-target compile\n",
            1,
        )
        expected_workflow_job_forbidden_issues = [
            f"workflow_phase2_cross_job:forbidden_marker:{forbidden_marker}"
            for forbidden_marker in PHASE2_CROSS_WORKFLOW_JOB_FORBIDDEN_MARKERS
            if forbidden_marker in marker
        ]
        if validate_phase2_cross_workflow_job(workflow_job_with_forbidden_toolchain_gate) != (
            expected_workflow_job_forbidden_issues
        ):
            raise SystemExit("phase2-cross-alignment:self-test:workflow_job_forbidden_failure")
        checks_run += 1

    scope_text = "\n".join(WORKFLOW_SCOPE_REQUIRED_FRAGMENTS)
    if validate_workflow_scope_fragments(scope_text):
        raise SystemExit("phase2-cross-alignment:self-test:workflow_scope")
    checks_run += 1

    scope_issues = validate_workflow_scope_fragments("scripts/zigux/**")
    if "workflow_scope:missing_marker:Documentation/zigux/**" not in scope_issues:
        raise SystemExit("phase2-cross-alignment:self-test:workflow_scope_failure")
    if "workflow_scope:missing_marker:.github/workflows/zigux-bootstrap.yml" not in scope_issues:
        raise SystemExit("phase2-cross-alignment:self-test:workflow_scope_workflow_failure")
    checks_run += 1

    scope_pattern_text = """if printf '%s\\n' \\\"$changed_files\\\" | grep -Eq '^(\\.github/workflows/zigux-bootstrap\\.yml|scripts/zigux/install-zig\\.py|scripts/zigux/check-phase2-cross\\.py|scripts/zigux/check-phase2-cross-selftest-alignment\\.py|scripts/zigux/fixdep\\.zig|scripts/zigux/genksyms\\.zig|scripts/zigux/kconfig/conf_bridge\\.zig|scripts/zigux/kconfig/confdata_bridge\\.zig|scripts/zigux/zig-toolchain-policy\\.json|zigux/Makefile|zigux/tests/fixtures/phase2_cross_targets\\.json)$'; then"""
    if validate_workflow_scope_pattern(scope_pattern_text):
        raise SystemExit("phase2-cross-alignment:self-test:workflow_scope_pattern")
    checks_run += 1

    missing_scope_pattern = scope_pattern_text.replace("scripts/zigux/genksyms\\.zig|", "", 1)
    missing_scope_pattern_issues = validate_workflow_scope_pattern(missing_scope_pattern)
    expected_scope_pattern_issue = "workflow_scope_pattern:missing_marker:scripts/zigux/genksyms\\.zig"
    if missing_scope_pattern_issues != [expected_scope_pattern_issue]:
        raise SystemExit("phase2-cross-alignment:self-test:workflow_scope_pattern_failure")
    checks_run += 1

    missing_confdata_scope_pattern = scope_pattern_text.replace(
        "scripts/zigux/kconfig/confdata_bridge\\.zig|", "", 1
    )
    missing_confdata_scope_pattern_issues = validate_workflow_scope_pattern(
        missing_confdata_scope_pattern
    )
    expected_confdata_scope_pattern_issue = (
        "workflow_scope_pattern:missing_marker:scripts/zigux/kconfig/confdata_bridge\\.zig"
    )
    if missing_confdata_scope_pattern_issues != [expected_confdata_scope_pattern_issue]:
        raise SystemExit("phase2-cross-alignment:self-test:workflow_scope_pattern_confdata_failure")
    checks_run += 1

    missing_install_scope_pattern = scope_pattern_text.replace(
        "scripts/zigux/install-zig\\.py|", "", 1
    )
    missing_install_scope_pattern_issues = validate_workflow_scope_pattern(
        missing_install_scope_pattern
    )
    expected_install_scope_pattern_issue = (
        "workflow_scope_pattern:missing_marker:scripts/zigux/install-zig\\.py"
    )
    if missing_install_scope_pattern_issues != [expected_install_scope_pattern_issue]:
        raise SystemExit("phase2-cross-alignment:self-test:workflow_scope_pattern_install_failure")
    checks_run += 1

    missing_toolchain_policy_scope_pattern = scope_pattern_text.replace(
        "scripts/zigux/zig-toolchain-policy\\.json|", "", 1
    )
    missing_toolchain_policy_scope_pattern_issues = validate_workflow_scope_pattern(
        missing_toolchain_policy_scope_pattern
    )
    expected_toolchain_policy_scope_pattern_issue = (
        "workflow_scope_pattern:missing_marker:scripts/zigux/zig-toolchain-policy\\.json"
    )
    if (
        missing_toolchain_policy_scope_pattern_issues
        != [expected_toolchain_policy_scope_pattern_issue]
    ):
        raise SystemExit(
            "phase2-cross-alignment:self-test:workflow_scope_pattern_toolchain_policy_failure"
        )
    checks_run += 1

    missing_makefile_scope_pattern = scope_pattern_text.replace(
        "zigux/Makefile|", "", 1
    )
    missing_makefile_scope_pattern_issues = validate_workflow_scope_pattern(
        missing_makefile_scope_pattern
    )
    expected_makefile_scope_pattern_issue = (
        "workflow_scope_pattern:missing_marker:zigux/Makefile"
    )
    if missing_makefile_scope_pattern_issues != [expected_makefile_scope_pattern_issue]:
        raise SystemExit(
            "phase2-cross-alignment:self-test:workflow_scope_pattern_makefile_failure"
        )
    checks_run += 1

    makefile_text = "\n".join(
        [
            "phase2-validate: phase2-tools phase2-kconfig",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase2-closure.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross-selftest-alignment.py",
            "phase2-cross: phase2-toolchain",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py",
        ]
    )
    if validate_exact_makefile_runs(makefile_text):
        raise SystemExit("phase2-cross-alignment:self-test:makefile_counts")
    checks_run += 1

    missing_makefile_issues = validate_exact_makefile_runs("")
    expected_missing_makefile_issue = (
        "makefile_exact_run:scripts/zigux/check-phase2-cross.py --self-test:count=0:expected=1"
    )
    if expected_missing_makefile_issue not in missing_makefile_issues:
        raise SystemExit("phase2-cross-alignment:self-test:makefile_count_failure")
    checks_run += 1

    duplicate_makefile = (
        makefile_text
        + "\n\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py --self-test"
    )
    duplicate_makefile_issues = validate_exact_makefile_runs(duplicate_makefile)
    expected_duplicate_makefile_issue = (
        "makefile_exact_run:scripts/zigux/check-phase2-cross.py --self-test:count=2:expected=1"
    )
    if duplicate_makefile_issues != [expected_duplicate_makefile_issue]:
        raise SystemExit("phase2-cross-alignment:self-test:makefile_duplicate_failure")
    checks_run += 1

    if validate_makefile_target_scope(makefile_text):
        raise SystemExit("phase2-cross-alignment:self-test:makefile_target_scope")
    checks_run += 1

    moved_cross_gate = "\n".join(
        [
            "phase2-validate: phase2-tools phase2-kconfig",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase2-closure.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross-selftest-alignment.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py",
            "phase2-cross: phase2-toolchain",
        ]
    )
    moved_cross_issues = validate_makefile_target_scope(moved_cross_gate)
    if not any(
        issue.startswith("makefile_target_scope:phase2-validate:actual=")
        for issue in moved_cross_issues
    ):
        raise SystemExit("phase2-cross-alignment:self-test:moved_cross_gate_validate_failure")
    if not any(
        issue.startswith("makefile_target_scope:phase2-cross:actual=")
        for issue in moved_cross_issues
    ):
        raise SystemExit("phase2-cross-alignment:self-test:moved_cross_GATE_cross_failure")
    checks_run += 2

    bad_cross_header = makefile_text.replace(
        "phase2-cross: phase2-toolchain",
        "phase2-cross: phase2-tools",
    )
    bad_cross_header_issues = validate_makefile_target_scope(bad_cross_header)
    expected_bad_cross_header_issue = (
        "makefile_target_scope:phase2-cross:"
        "header='phase2-cross: phase2-tools':expected='phase2-cross: phase2-toolchain'"
    )
    if bad_cross_header_issues != [expected_bad_cross_header_issue]:
        raise SystemExit("phase2-cross-alignment:self-test:cross_header_failure")
    checks_run += 1

    marker_issues = validate_required_markers(
        "alpha\nbeta\ngamma",
        label="sample",
        markers=["alpha", "gamma"],
    )
    if marker_issues:
        raise SystemExit("phase2-cross-alignment:self-test:marker_presence")
    checks_run += 1

    marker_issues = validate_required_markers(
        "alpha\nbeta\ngamma",
        label="sample",
        markers=["delta"],
    )
    if marker_issues != ["sample:missing_marker:delta"]:
        raise SystemExit("phase2-cross-alignment:self-test:marker_failure_shape")
    checks_run += 1

    bootstrap_issues = validate_required_markers(
        "\n".join(BOOTSTRAP_NOTES_MARKERS),
        label="phase2_bootstrap_notes",
        markers=BOOTSTRAP_NOTES_MARKERS,
    )
    if bootstrap_issues:
        raise SystemExit("phase2-cross-alignment:self-test:bootstrap_marker_presence")
    checks_run += 1

    for marker in BOOTSTRAP_NOTES_MARKERS:
        bootstrap_missing = validate_required_markers(
            "\n".join(item for item in BOOTSTRAP_NOTES_MARKERS if item != marker),
            label="phase2_bootstrap_notes",
            markers=BOOTSTRAP_NOTES_MARKERS,
        )
        expected_bootstrap_issue = (
            "phase2_bootstrap_notes:missing_marker:"
            f"{marker}"
        )
        if bootstrap_missing != [expected_bootstrap_issue]:
            raise SystemExit("phase2-cross-alignment:self-test:bootstrap_marker_failure")
        checks_run += 1

    bootstrap_forbidden_issues = validate_forbidden_markers(
        "\n".join(BOOTSTRAP_NOTES_MARKERS),
        label="phase2_bootstrap_notes",
        markers=BOOTSTRAP_NOTES_FORBIDDEN_MARKERS,
    )
    if bootstrap_forbidden_issues:
        raise SystemExit("phase2-cross-alignment:self-test:bootstrap_forbidden_presence")
    checks_run += 1

    bootstrap_forbidden_failure = validate_forbidden_markers(
        "\n".join(BOOTSTRAP_NOTES_MARKERS + BOOTSTRAP_NOTES_FORBIDDEN_MARKERS),
        label="phase2_bootstrap_notes",
        markers=BOOTSTRAP_NOTES_FORBIDDEN_MARKERS,
    )
    expected_forbidden_issues = [
        "phase2_bootstrap_notes:forbidden_marker:the direct kconfig and confdata Zig replays reviewable",
        f"phase2_bootstrap_notes:forbidden_marker:{BOOTSTRAP_NOTES_STALE_CROSS_WORKFLOW_BOUNDARY_SENTENCE}",
    ]
    if bootstrap_forbidden_failure != expected_forbidden_issues:
        raise SystemExit("phase2-cross-alignment:self-test:bootstrap_forbidden_failure")
    checks_run += 1

    docs_root_readme_issues = validate_required_markers(
        "\n".join(DOCS_ROOT_README_MARKERS),
        label="phase2_docs_root_readme",
        markers=DOCS_ROOT_README_MARKERS,
    )
    if docs_root_readme_issues:
        raise SystemExit("phase2-cross-alignment:self-test:docs_root_readme_marker_presence")
    checks_run += 1

    for marker in DOCS_ROOT_README_MARKERS:
        docs_root_readme_missing = validate_required_markers(
            "\n".join(item for item in DOCS_ROOT_README_MARKERS if item != marker),
            label="phase2_docs_root_readme",
            markers=DOCS_ROOT_README_MARKERS,
        )
        expected_docs_root_issue = (
            "phase2_docs_root_readme:missing_marker:"
            f"{marker}"
        )
        if docs_root_readme_missing != [expected_docs_root_issue]:
            raise SystemExit("phase2-cross-alignment:self-test:docs_root_readme_marker_failure")
        checks_run += 1

    scripts_readme_issues = validate_required_markers(
        "\n".join(SCRIPTS_README_MARKERS),
        label="phase2_scripts_readme",
        markers=SCRIPTS_README_MARKERS,
    )
    if scripts_readme_issues:
        raise SystemExit("phase2-cross-alignment:self-test:scripts_readme_marker_presence")
    checks_run += 1

    for marker in SCRIPTS_README_MARKERS:
        scripts_readme_missing = validate_required_markers(
            "\n".join(item for item in SCRIPTS_README_MARKERS if item != marker),
            label="phase2_scripts_readme",
            markers=SCRIPTS_README_MARKERS,
        )
        expected_scripts_readme_issue = (
            "phase2_scripts_readme:missing_marker:"
            f"{marker}"
        )
        if scripts_readme_missing != [expected_scripts_readme_issue]:
            raise SystemExit("phase2-cross-alignment:self-test:scripts_readme_marker_failure")
        checks_run += 1

    tests_readme_issues = validate_required_markers(
        "\n".join(TESTS_README_MARKERS),
        label="phase2_tests_readme",
        markers=TESTS_README_MARKERS,
    )
    if tests_readme_issues:
        raise SystemExit("phase2-cross-alignment:self-test:tests_readme_marker_presence")
    checks_run += 1

    for marker in TESTS_README_MARKERS:
        tests_readme_missing = validate_required_markers(
            "\n".join(item for item in TESTS_README_MARKERS if item != marker),
            label="phase2_tests_readme",
            markers=TESTS_README_MARKERS,
        )
        expected_tests_issue = f"phase2_tests_readme:missing_marker:{marker}"
        if tests_readme_missing != [expected_tests_issue]:
            raise SystemExit("phase2-cross-alignment:self-test:tests_readme_marker_failure")
        checks_run += 1

    review_checklist_issues = validate_required_markers(
        "\n".join(REVIEW_CHECKLIST_MARKERS),
        label="phase2_review_checklist",
        markers=REVIEW_CHECKLIST_MARKERS,
    )
    if review_checklist_issues:
        raise SystemExit("phase2-cross-alignment:self-test:review_checklist_marker_presence")
    checks_run += 1

    for marker in REVIEW_CHECKLIST_MARKERS:
        review_checklist_missing = validate_required_markers(
            "\n".join(item for item in REVIEW_CHECKLIST_MARKERS if item != marker),
            label="phase2_review_checklist",
            markers=REVIEW_CHECKLIST_MARKERS,
        )
        expected_review_checklist_issue = (
            "phase2_review_checklist:missing_marker:"
            f"{marker}"
        )
        if review_checklist_missing != [expected_review_checklist_issue]:
            raise SystemExit("phase2-cross-alignment:self-test:review_checklist_marker_failure")
        checks_run += 1

    for marker in CLOSURE_MARKERS:
        closure_missing = validate_required_markers(
            "\n".join(item for item in CLOSURE_MARKERS if item != marker),
            label="phase2_closure_doc",
            markers=CLOSURE_MARKERS,
        )
        expected_closure_issue = (
            "phase2_closure_doc:missing_marker:"
            f"{marker}"
        )
        if closure_missing != [expected_closure_issue]:
            raise SystemExit("phase2-cross-alignment:self-test:closure_marker_failure")
        checks_run += 1

    with tempfile.TemporaryDirectory(prefix="phase2_cross_alignment_selftest_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        manifest_path = tmp_root / "phase2_cross_targets.json"
        manifest_path.write_text(json.dumps(valid_targets), encoding="utf-8")
        round_trip = load_json_object(manifest_path, label="targets")
        if round_trip["targets"] != EXPECTED_TARGETS:
            raise SystemExit("phase2-cross-alignment:self-test:json_round_trip")
        checks_run += 1
        if round_trip["zig_test_files"] != EXPECTED_ZIG_TEST_FILES:
            raise SystemExit("phase2-cross-alignment:self-test:json_zig_test_files_round_trip")
        checks_run += 1

    if checks_run != EXPECTED_SELF_TEST_CASE_COUNT:
        raise SystemExit(
            "phase2-cross-alignment:self-test:case_count:"
            f"actual={checks_run}:expected={EXPECTED_SELF_TEST_CASE_COUNT}"
        )

    print("PHASE2_CROSS_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE2_CROSS_ALIGNMENT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 2 cross-target checker aligned with the shared validator and published closure packet."
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in alignment checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    required_files = [
        PHASE2_CROSS_CHECKER,
        PHASE2_VALIDATOR,
        WORKFLOW,
        MAKEFILE,
        CLOSURE_DOC,
        BOOTSTRAP_NOTES,
        DOCS_ROOT_README,
        SCRIPTS_README,
        TESTS_README,
        REVIEW_CHECKLIST,
        TARGETS_MANIFEST,
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_files if not path.exists()]
    if missing:
        print("PHASE2_CROSS_ALIGNMENT=fail")
        print("MISSING_PHASE2_CROSS_ALIGNMENT_FILES_START")
        for item in missing:
            print(item)
        print("MISSING_PHASE2_CROSS_ALIGNMENT_FILES_END")
        return 1

    workflow_text = WORKFLOW.read_text(encoding="utf-8")
    issues: list[str] = []
    issues.extend(
        validate_targets_manifest(load_json_object(TARGETS_MANIFEST, label="targets"))
    )
    issues.extend(
        validate_required_markers(
            PHASE2_CROSS_CHECKER.read_text(encoding="utf-8"),
            label="phase2_cross_checker",
            markers=PHASE2_CROSS_CHECKER_MARKERS,
        )
    )
    issues.extend(
        validate_required_markers(
            PHASE2_VALIDATOR.read_text(encoding="utf-8"),
            label="phase2_validator",
            markers=PHASE2_VALIDATOR_MARKERS,
        )
    )
    issues.extend(
        validate_required_markers(
            CLOSURE_DOC.read_text(encoding="utf-8"),
            label="phase2_closure_doc",
            markers=CLOSURE_MARKERS,
        )
    )
    bootstrap_text = BOOTSTRAP_NOTES.read_text(encoding="utf-8")
    issues.extend(
        validate_required_markers(
            bootstrap_text,
            label="phase2_bootstrap_notes",
            markers=BOOTSTRAP_NOTES_MARKERS,
        )
    )
    issues.extend(
        validate_forbidden_markers(
            bootstrap_text,
            label="phase2_bootstrap_notes",
            markers=BOOTSTRAP_NOTES_FORBIDDEN_MARKERS,
        )
    )
    issues.extend(
        validate_required_markers(
            DOCS_ROOT_README.read_text(encoding="utf-8"),
            label="phase2_docs_root_readme",
            markers=DOCS_ROOT_README_MARKERS,
        )
    )
    issues.extend(
        validate_required_markers(
            SCRIPTS_README.read_text(encoding="utf-8"),
            label="phase2_scripts_readme",
            markers=SCRIPTS_README_MARKERS,
        )
    )
    issues.extend(
        validate_required_markers(
            TESTS_README.read_text(encoding="utf-8"),
            label="phase2_tests_readme",
            markers=TESTS_README_MARKERS,
        )
    )
    issues.extend(
        validate_required_markers(
            REVIEW_CHECKLIST.read_text(encoding="utf-8"),
            label="phase2_review_checklist",
            markers=REVIEW_CHECKLIST_MARKERS,
        )
    )
    issues.extend(validate_exact_workflow_runs(workflow_text))
    issues.extend(validate_workflow_scope_fragments(workflow_text))
    issues.extend(validate_workflow_scope_pattern(workflow_text))
    issues.extend(validate_phase2_cross_workflow_job(workflow_text))

    makefile_text = MAKEFILE.read_text(encoding="utf-8")
    issues.extend(validate_exact_makefile_runs(makefile_text))
    issues.extend(validate_makefile_target_scope(makefile_text))

    if issues:
        print("PHASE2_CROSS_ALIGNMENT=fail")
        print("INVALID_PHASE2_CROSS_ALIGNMENT_START")
        for item in issues:
            print(item)
        print("INVALID_PHASE2_CROSS_ALIGNMENT_END")
        return 1

    print("PHASE2_CROSS_ALIGNMENT=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())