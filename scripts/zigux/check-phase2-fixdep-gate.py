#!/usr/bin/env python3
"""Check the current fixdep governance packet against live Phase 2 surfaces."""

from __future__ import annotations

import argparse
import ast
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

FIXDEP_REL = Path("scripts/zigux/fixdep.zig")
FIXDEP_DIFF_REL = Path("scripts/zigux/check-fixdep-diff.py")
VALIDATE_PHASE2_REL = Path("scripts/zigux/validate-phase2.py")
FIXDEP_CASES_REL = Path("zigux/tests/fixtures/fixdep/cases.json")
FIXDEP_SURVEY_REL = Path("Documentation/zigux/phase2-fixdep-dual-implementation-survey.md")
PHASE2_CLOSURE_REL = Path("Documentation/zigux/phase2-closure.md")
TESTS_README_REL = Path("zigux/tests/README.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
MAKEFILE_REL = Path("zigux/Makefile")
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")

REQUIRED_FILES = (
    FIXDEP_REL,
    FIXDEP_DIFF_REL,
    VALIDATE_PHASE2_REL,
    FIXDEP_CASES_REL,
    FIXDEP_SURVEY_REL,
    PHASE2_CLOSURE_REL,
    TESTS_README_REL,
    SCRIPTS_README_REL,
    MAKEFILE_REL,
    WORKFLOW_REL,
)

SURVEY_REQUIRED_MARKERS = (
    "Phase 2 roadmap still keeps `scripts/basic/fixdep.c` and `scripts/zigux/fixdep.zig` inside the selected dual-implementation tranche.",
    "bounded thirteen-case external fixdep packet",
    "Current `scripts/zigux/fixdep.zig` already captures `error.PermissionDenied` on the dedicated `fixdep: error opening file:` path, and the live helper also carries a focused regression test for that branch.",
    "Exact-path authenticated contents reads still return missing for `scripts/basic/fixdep.c`",
    "Those same shared reminder surfaces still do not enumerate `Documentation/zigux/phase2-fixdep-dual-implementation-survey.md` alongside the genksyms survey",
)

FIXDEP_REQUIRED_EXACT_LINES = (
    'test "config parsing trims _MODULE and deduplicates symbols" {',
    'test "config parsing ignores prefixed CONFIG tokens like upstream fixdep" {',
    'test "config parsing accepts CONFIG tokens after punctuation" {',
    'test "config parsing stops at the first embedded NUL" {',
    'test "dep parsing returns NoTargets for comment-only depfiles" {',
    'test "dep parsing keeps escaped spaces inside tokens" {',
    'test "dep parsing continues dependency lines across escaped newlines" {',
    'test "dep parsing accepts CRLF lines and continuations" {',
    'test "dep parsing does not continue bare carriage-return lines" {',
    'test "dep parsing skips bytes after the first embedded NUL" {',
    'test "ignored and no-parse file classification matches fixdep rules" {',
    'test "file read errors map to C-style messages" {',
    'test "file read errors map short reads to unexpected end of file" {',
    'test "exact read size helper rejects short reads" {',
    'test "path error wording keeps the dedicated fstat prefix" {',
    'test "open dependency file classification keeps input-output failures on the C-style path" {',
    'test "open dependency file classification keeps PermissionDenied on the C-style path" {',
    'test "open dependency file classification preserves unrelated open failures" {',
    'test "read failure wording matches C perror prefix" {',
    'test "output write failure uses C-style wording" {',
    'test "flush helper preserves the primary error" {',
    'test "dependency file reads beyond the legacy one mebibyte ceiling" {',
    'test "escaped hash dependency survives concatenated target comment path" {',
    'test "escaped colon dependency survives concatenated target comment path" {',
    'test "escaped colon dependency survives concatenated target CRLF comment path" {',
)

FIXDEP_DIFF_REQUIRED_EXACT_LINES = (
    "diff_text(expected_stdout, zig_actual)",
    "diff_text(expected_stdout, zig_repeat)",
    "diff_text(zig_actual, zig_repeat)",
    "diff_text(expected_stderr_path, zig_actual_stderr)",
    "diff_text(expected_stderr_path, zig_repeat_stderr)",
    "diff_text(zig_actual_stderr, zig_repeat_stderr)",
    'ZIG_FIXDEP = ROOT / "scripts" / "zigux" / "fixdep.zig"',
    'EXPECTED_ZIG_FIXDEP = ROOT / "scripts" / "zigux" / "fixdep.zig"',
    "validate_tool_source(ZIG_FIXDEP)",
    "EXPECTED_SELF_TEST_CASE_COUNT = 16",
    'print("FIXDEP_SELF_TEST=pass")',
    'print("FIXDEP_DIFF=pass")',
    'print("FIXDEP_DETERMINISM=pass")',
)

FIXDEP_DIFF_CONTRACT_EXACT_LINES = (
    "EXPECTED_FIXTURE_FILES = frozenset(",
    "EXPECTED_CASE_ORDER = list(EXPECTED_CASES)",
    "def validate_fixture_inventory(",
    "expected_case = EXPECTED_CASES.get(name)",
    'expected_stdout_name = validated_case.get("expected_stdout", validated_case.get("expected"))',
    'raise ValueError(f"{CASES_PATH}:unexpected_name:{name}")',
    'raise ValueError(f"{CASES_PATH}:case_order={seen_names!r},expected={EXPECTED_CASE_ORDER!r}")',
    'raise ValueError(f"{CASES_PATH}:count={len(validated)},expected={len(EXPECTED_CASES)}")',
    'raise ValueError(f"{CASES_PATH}:{name}:unsupported_stdout_mode:{stdout_mode!r}")',
    "validate_fixture_inventory()",
    "cases = validate_cases(load_cases(CASES_PATH))",
)

VALIDATE_PHASE2_REQUIRED_LINES = (
    '"scripts/zigux/check-phase2-fixdep-gate.py",',
    '"scripts/zigux/check-fixdep-diff.py",',
    '"scripts/zigux/fixdep.zig",',
    '"zigux/tests/fixtures/fixdep/cases.json",',
    '"run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",',
    '"run: python3 scripts/zigux/check-phase2-fixdep-gate.py",',
    '"run: python3 scripts/zigux/check-fixdep-diff.py --self-test",',
    '"run: python3 scripts/zigux/check-fixdep-diff.py",',
    '"run: zig test scripts/zigux/fixdep.zig",',
    '"run: make -C zigux phase2-fixdep",',
    '"phase2-fixdep:",',
    '"cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py --self-test",',
    '"cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py",',
    '"cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py --self-test",',
    '"cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py",',
    '"cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/fixdep.zig",',
    '"phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",',
)

REQUIRED_FIXDEP_CASE_NAMES = (
    "sample",
    "sample_multi_target",
    "sample_escaped_space",
    "sample_escaped_colon",
    "sample_concatenated",
    "sample_dependency_continuation",
    "sample_comment_continuation",
    "sample_double_backslash_comment",
    "sample_comment_only",
    "sample_comment_only_stdout_full",
    "sample_missing_dep",
    "sample_missing_dep_stdout_full",
    "sample_output_write",
)

REQUIRED_FIXDEP_EXPECTED_CASES = {
    "sample": {
        "depfile": "sample.d",
        "target": "sample.o",
        "cmdline": "clang -Iinclude -DZIGUX_SAMPLE -c zigux/tests/fixtures/fixdep/sample.c -o sample.o",
        "expected": "sample_expected.txt",
        "expected_exit_code": 0,
    },
    "sample_multi_target": {
        "depfile": "sample_multi_target.d",
        "target": "module/sample2.o",
        "cmdline": "clang -Iinclude -DZIGUX_MULTI -c zigux/tests/fixtures/fixdep/sample2.c -o module/sample2.o",
        "expected": "sample_multi_target_expected.txt",
        "expected_exit_code": 0,
    },
    "sample_escaped_space": {
        "depfile": "sample_escaped_space.d",
        "target": "sample_escaped_space.o",
        "cmdline": "clang -c zigux/tests/fixtures/fixdep/sample_escaped_space_source.c -o sample_escaped_space.o",
        "expected": "sample_escaped_space_expected.txt",
        "expected_exit_code": 0,
    },
    "sample_escaped_colon": {
        "depfile": "sample_escaped_colon.d",
        "target": "sample_escaped_colon.o",
        "cmdline": "clang -c zigux/tests/fixtures/fixdep/sample_escaped_colon_source.c -o sample_escaped_colon.o",
        "expected": "sample_escaped_colon_expected.txt",
        "expected_exit_code": 0,
    },
    "sample_concatenated": {
        "depfile": "sample_concatenated.d",
        "target": "sample_concatenated.o",
        "cmdline": "clang -c zigux/tests/fixtures/fixdep/sample_concatenated_source.c -o sample_concatenated.o",
        "expected": "sample_concatenated_expected.txt",
        "expected_exit_code": 0,
    },
    "sample_dependency_continuation": {
        "depfile": "sample_dependency_continuation.d",
        "target": "sample_dependency_continuation.o",
        "cmdline": "clang -c zigux/tests/fixtures/fixdep/sample_dependency_continuation_source.c -o sample_dependency_continuation.o",
        "expected": "sample_dependency_continuation_expected.txt",
        "expected_exit_code": 0,
    },
    "sample_comment_continuation": {
        "depfile": "sample_comment_continuation.d",
        "target": "sample_comment_continuation.o",
        "cmdline": "clang -c zigux/tests/fixtures/fixdep/sample_comment_continuation_source.c -o sample_comment_continuation.o",
        "expected": "sample_comment_continuation_expected.txt",
        "expected_exit_code": 0,
    },
    "sample_double_backslash_comment": {
        "depfile": "sample_double_backslash_comment.d",
        "target": "sample_double_backslash_comment.o",
        "cmdline": "rustc --emit dep-info=sample_double_backslash_comment.d",
        "expected": "sample_double_backslash_comment_expected.txt",
        "expected_stderr": "sample_double_backslash_comment_expected.stderr.txt",
        "expected_exit_code": 2,
    },
    "sample_comment_only": {
        "depfile": "sample_comment_only.d",
        "target": "sample_comment_only.o",
        "cmdline": "clang -Iinclude -DZIGUX_SAMPLE -c zigux/tests/fixtures/fixdep/sample.c -o sample_comment_only.o",
        "expected": "sample_comment_only_expected.txt",
        "expected_stderr": "sample_comment_only_expected.stderr.txt",
        "expected_exit_code": 1,
    },
    "sample_comment_only_stdout_full": {
        "depfile": "sample_comment_only.d",
        "target": "sample_comment_only_stdout_full.o",
        "cmdline": "clang -Iinclude -DZIGUX_SAMPLE -c zigux/tests/fixtures/fixdep/sample.c -o sample_comment_only_stdout_full.o",
        "expected": "sample_output_write_expected.txt",
        "expected_stderr": "sample_comment_only_expected.stderr.txt",
        "expected_exit_code": 1,
        "stdout_mode": "dev_full",
    },
    "sample_missing_dep": {
        "depfile": "sample_missing_dep.d",
        "target": "sample_missing_dep.o",
        "cmdline": "clang -c zigux/tests/fixtures/fixdep/sample_missing_dep_source.c -o sample_missing_dep.o",
        "expected": "sample_missing_dep_expected.txt",
        "expected_stderr": "sample_missing_dep_expected.stderr.txt",
        "expected_exit_code": 2,
    },
    "sample_missing_dep_stdout_full": {
        "depfile": "sample_missing_dep.d",
        "target": "sample_missing_dep_stdout_full.o",
        "cmdline": "clang -c zigux/tests/fixtures/fixdep/sample_missing_dep_source.c -o sample_missing_dep_stdout_full.o",
        "expected": "sample_output_write_expected.txt",
        "expected_stderr": "sample_missing_dep_expected.stderr.txt",
        "expected_exit_code": 2,
        "stdout_mode": "dev_full",
    },
    "sample_output_write": {
        "depfile": "sample.d",
        "target": "sample_output_write.o",
        "cmdline": "clang -Iinclude -DZIGUX_SAMPLE -c zigux/tests/fixtures/fixdep/sample.c -o sample_output_write.o",
        "expected": "sample_output_write_expected.txt",
        "expected_stderr": "sample_output_write_expected.stderr.txt",
        "expected_exit_code": 1,
        "stdout_mode": "dev_full",
    },
}

CLOSURE_REQUIRED_MARKERS = (
    "`Documentation/zigux/phase2-closure.md`",
    "`zigux/Makefile`",
    "`zigux/tests/README.md`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`scripts/zigux/fixdep.zig`",
    "`zigux/tests/fixtures/fixdep/cases.json`",
    "`make -C zigux phase2-fixdep`",
)

TESTS_README_REQUIRED_MARKERS = (
    "Phase 2 review packet",
    "`Documentation/zigux/phase2-closure.md`",
    "`zigux/Makefile`",
    "`make -C zigux phase2`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`scripts/zigux/fixdep.zig`",
    "`zigux/tests/fixtures/fixdep/cases.json`",
    "`make -C zigux phase2-fixdep`",
)

SCRIPTS_README_REQUIRED_MARKERS = (
    "## Phase 2",
    "current fixdep packet stays reviewable through the dedicated governance guard, parity checker, and shipped `phase2-fixdep` wrapper",
    "`scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` keep the current fixdep governance, determinism, helper, fixture, and CI packet explicit from the scripts root",
    "`python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test`, `python3 scripts/zigux/check-phase2-fixdep-gate.py`, `python3 scripts/zigux/check-fixdep-diff.py --self-test`, `python3 scripts/zigux/check-fixdep-diff.py`, `zig test scripts/zigux/fixdep.zig`, and `make -C zigux phase2-fixdep` replay the shipped fixdep lane without widening into unrelated Phase 2 surfaces",
)

REQUIRED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "run: python3 scripts/zigux/check-phase2-fixdep-gate.py",
    "run: python3 scripts/zigux/check-fixdep-diff.py --self-test",
    "run: python3 scripts/zigux/check-fixdep-diff.py",
    "run: zig test scripts/zigux/fixdep.zig",
    "run: make -C zigux phase2-fixdep",
)

REQUIRED_MAKEFILE_PHONY_TARGETS = ("phase2-fixdep", "phase2-validate", "phase2")

REQUIRED_MAKEFILE_LINES = (
    "phase2-fixdep: phase2-toolchain",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/fixdep.zig",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
)


def resolve(root: Path, rel: Path) -> Path:
    return root / rel


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_required_exact_lines(
    text: str, markers: tuple[str, ...], missing_code: str, duplicate_code: str
) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = count_exact_lines(text, marker)
        if count == 0:
            issues.append((missing_code, marker))
        elif count != 1:
            issues.append((duplicate_code, f"{marker}:count={count}"))
    return issues


def phony_targets_present(text: str) -> set[str]:
    targets: set[str] = set()
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(".PHONY:"):
            _, suffix = stripped.split(":", 1)
            targets.update(token for token in suffix.strip().split() if token)
    return targets


def extract_fixdep_diff_expected_cases(text: str) -> dict[str, dict[str, object]]:
    start_marker = "EXPECTED_CASES ="
    end_marker = "EXPECTED_CASE_ORDER = list(EXPECTED_CASES)"
    start = text.find(start_marker)
    if start == -1:
        raise ValueError("EXPECTED_CASES assignment missing")
    end = text.find(end_marker, start)
    if end == -1:
        raise ValueError("EXPECTED_CASE_ORDER marker missing after EXPECTED_CASES")

    payload = text[start + len(start_marker) : end].strip()
    try:
        value = ast.literal_eval(payload)
    except Exception as exc:
        raise ValueError(f"EXPECTED_CASES literal parse failed: {exc}") from exc

    if not isinstance(value, dict):
        raise ValueError("EXPECTED_CASES is not a dict literal")

    normalized: dict[str, dict[str, object]] = {}
    for key, case in value.items():
        if not isinstance(key, str) or not isinstance(case, dict):
            raise ValueError("EXPECTED_CASES must map strings to dict literals")
        normalized[key] = case
    return normalized


def collect_fixdep_diff_expected_case_issues(text: str) -> list[tuple[str, str]]:
    try:
        actual_cases = extract_fixdep_diff_expected_cases(text)
    except (SyntaxError, ValueError) as exc:
        return [("INVALID_FIXDEP_DIFF_EXPECTED_CASES", str(exc))]

    issues: list[tuple[str, str]] = []
    actual_names = list(actual_cases)
    expected_names = list(REQUIRED_FIXDEP_EXPECTED_CASES)
    if actual_names != expected_names:
        issues.append(
            (
                "FIXDEP_DIFF_EXPECTED_CASE_ORDER_MISMATCH",
                f"actual={actual_names!r}:expected={expected_names!r}",
            )
        )

    for name in expected_names:
        if name not in actual_cases:
            issues.append(("MISSING_FIXDEP_DIFF_EXPECTED_CASE", name))
    for name in actual_names:
        if name not in REQUIRED_FIXDEP_EXPECTED_CASES:
            issues.append(("UNEXPECTED_FIXDEP_DIFF_EXPECTED_CASE", name))

    for name, expected_case in REQUIRED_FIXDEP_EXPECTED_CASES.items():
        actual_case = actual_cases.get(name)
        if actual_case is None:
            continue
        for key in sorted(set(expected_case) | set(actual_case)):
            actual_value = actual_case.get(key)
            expected_value = expected_case.get(key)
            if actual_value != expected_value:
                issues.append(
                    (
                        "FIXDEP_DIFF_EXPECTED_CASE_FIELD_MISMATCH",
                        f"{name}:{key}={actual_value!r}:expected={expected_value!r}",
                    )
                )
    return issues


def collect_fixdep_case_issues(path: Path) -> list[tuple[str, str]]:
    try:
        raw_cases = json.loads(read_text(path))
    except json.JSONDecodeError:
        return [("INVALID_FIXDEP_CASES_JSON", path.as_posix())]

    if not isinstance(raw_cases, list):
        return [("INVALID_FIXDEP_CASES_JSON", path.as_posix())]

    issues: list[tuple[str, str]] = []
    names: list[str] = []
    seen: set[str] = set()
    duplicates: set[str] = set()
    actual_cases_by_name: dict[str, dict[str, object]] = {}
    for index, raw_case in enumerate(raw_cases):
        if not isinstance(raw_case, dict):
            issues.append(("INVALID_FIXDEP_CASE_ENTRY", f"index={index}:type={type(raw_case).__name__}"))
            continue
        name = raw_case.get("name")
        if not isinstance(name, str) or not name:
            issues.append(("INVALID_FIXDEP_CASE_NAME", f"index={index}:name={name!r}"))
            continue
        names.append(name)
        if name in seen:
            duplicates.add(name)
        seen.add(name)
        if name not in REQUIRED_FIXDEP_CASE_NAMES:
            issues.append(("UNEXPECTED_FIXDEP_CASE", name))
        if name not in actual_cases_by_name:
            actual_cases_by_name[name] = raw_case

    for name in sorted(duplicates):
        issues.append(("DUPLICATE_FIXDEP_CASE", name))

    expected_names = list(REQUIRED_FIXDEP_CASE_NAMES)
    if names != expected_names:
        issues.append(("FIXDEP_CASE_ORDER_MISMATCH", f"actual={names!r}:expected={expected_names!r}"))

    for name in REQUIRED_FIXDEP_CASE_NAMES:
        if name not in seen:
            issues.append(("MISSING_FIXDEP_CASE", name))

    for name, expected_case in REQUIRED_FIXDEP_EXPECTED_CASES.items():
        actual_case = actual_cases_by_name.get(name)
        if actual_case is None:
            continue
        actual_keys = set(actual_case) - {"name"}
        expected_keys = set(expected_case)
        for key in sorted(actual_keys | expected_keys):
            actual_value = actual_case.get(key)
            expected_value = expected_case.get(key)
            if actual_value != expected_value:
                issues.append(
                    (
                        "FIXDEP_CASE_FIELD_MISMATCH",
                        f"{name}:{key}={actual_value!r}:expected={expected_value!r}",
                    )
                )
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for rel in REQUIRED_FILES:
        if not resolve(root, rel).exists():
            issues.append(("MISSING_REQUIRED_FILE", rel.as_posix()))
    if issues:
        return issues

    fixdep_text = read_text(resolve(root, FIXDEP_REL))
    fixdep_diff_text = read_text(resolve(root, FIXDEP_DIFF_REL))
    validate_phase2_text = read_text(resolve(root, VALIDATE_PHASE2_REL))
    survey_text = read_text(resolve(root, FIXDEP_SURVEY_REL))
    closure_text = read_text(resolve(root, PHASE2_CLOSURE_REL))
    tests_readme_text = read_text(resolve(root, TESTS_README_REL))
    scripts_readme_text = read_text(resolve(root, SCRIPTS_README_REL))
    makefile_text = read_text(resolve(root, MAKEFILE_REL))
    workflow_text = read_text(resolve(root, WORKFLOW_REL))

    issues.extend(collect_missing_markers(survey_text, SURVEY_REQUIRED_MARKERS, "MISSING_SURVEY_MARKER"))
    issues.extend(
        collect_required_exact_lines(
            fixdep_text,
            FIXDEP_REQUIRED_EXACT_LINES,
            "MISSING_FIXDEP_TEST_LINE",
            "DUPLICATE_FIXDEP_TEST_LINE",
        )
    )
    issues.extend(
        collect_required_exact_lines(
            fixdep_diff_text,
            FIXDEP_DIFF_REQUIRED_EXACT_LINES,
            "MISSING_FIXDEP_DIFF_LINE",
            "DUPLICATE_FIXDEP_DIFF_LINE",
        )
    )
    issues.extend(
        collect_required_exact_lines(
            fixdep_diff_text,
            FIXDEP_DIFF_CONTRACT_EXACT_LINES,
            "MISSING_FIXDEP_DIFF_CONTRACT_LINE",
            "DUPLICATE_FIXDEP_DIFF_CONTRACT_LINE",
        )
    )
    issues.extend(collect_fixdep_diff_expected_case_issues(fixdep_diff_text))
    issues.extend(
        collect_required_exact_lines(
            validate_phase2_text,
            VALIDATE_PHASE2_REQUIRED_LINES,
            "MISSING_VALIDATE_PHASE2_LINE",
            "DUPLICATE_VALIDATE_PHASE2_LINE",
        )
    )
    issues.extend(collect_fixdep_case_issues(resolve(root, FIXDEP_CASES_REL)))
    issues.extend(collect_missing_markers(closure_text, CLOSURE_REQUIRED_MARKERS, "MISSING_CLOSURE_MARKER"))
    issues.extend(
        collect_missing_markers(
            tests_readme_text,
            TESTS_README_REQUIRED_MARKERS,
            "MISSING_TESTS_README_MARKER",
        )
    )
    issues.extend(
        collect_missing_markers(
            scripts_readme_text,
            SCRIPTS_README_REQUIRED_MARKERS,
            "MISSING_SCRIPTS_README_MARKER",
        )
    )
    issues.extend(
        collect_required_exact_lines(
            workflow_text,
            REQUIRED_WORKFLOW_LINES,
            "MISSING_WORKFLOW_LINE",
            "DUPLICATE_WORKFLOW_LINE",
        )
    )
    phony_targets = phony_targets_present(makefile_text)
    for target in REQUIRED_MAKEFILE_PHONY_TARGETS:
        if target not in phony_targets:
            issues.append(("MISSING_MAKEFILE_PHONY_TARGET", target))
    issues.extend(
        collect_required_exact_lines(
            makefile_text,
            REQUIRED_MAKEFILE_LINES,
            "MISSING_MAKEFILE_LINE",
            "DUPLICATE_MAKEFILE_LINE",
        )
    )
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_FIXDEP_GATE=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(resolve(root, FIXDEP_REL), "\n".join(FIXDEP_REQUIRED_EXACT_LINES) + "\n")
    write_text(
        resolve(root, FIXDEP_DIFF_REL),
        "\n".join(
            (
                *FIXDEP_DIFF_REQUIRED_EXACT_LINES,
                "EXPECTED_CASES = " + repr(REQUIRED_FIXDEP_EXPECTED_CASES),
                "EXPECTED_CASE_ORDER = list(EXPECTED_CASES)",
                *tuple(
                    marker
                    for marker in FIXDEP_DIFF_CONTRACT_EXACT_LINES
                    if marker != "EXPECTED_CASE_ORDER = list(EXPECTED_CASES)"
                ),
            )
        )
        + "\n",
    )
    write_text(resolve(root, VALIDATE_PHASE2_REL), "\n".join(VALIDATE_PHASE2_REQUIRED_LINES) + "\n")
    write_text(
        resolve(root, FIXDEP_CASES_REL),
        json.dumps(
            [{"name": name, **REQUIRED_FIXDEP_EXPECTED_CASES[name]} for name in REQUIRED_FIXDEP_CASE_NAMES],
            indent=2,
        )
        + "\n",
    )
    write_text(resolve(root, FIXDEP_SURVEY_REL), "\n".join(SURVEY_REQUIRED_MARKERS) + "\n")
    write_text(resolve(root, PHASE2_CLOSURE_REL), "\n".join(CLOSURE_REQUIRED_MARKERS) + "\n")
    write_text(resolve(root, TESTS_README_REL), "\n".join(TESTS_README_REQUIRED_MARKERS) + "\n")
    write_text(resolve(root, SCRIPTS_README_REL), "\n".join(SCRIPTS_README_REQUIRED_MARKERS) + "\n")
    write_text(
        resolve(root, MAKEFILE_REL),
        ".PHONY: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2\n"
        + "\n".join(REQUIRED_MAKEFILE_LINES)
        + "\n",
    )
    write_text(resolve(root, WORKFLOW_REL), "\n".join(REQUIRED_WORKFLOW_LINES) + "\n")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_fixdep_gate_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        path = resolve(root, FIXDEP_DIFF_REL)
        original = read_text(path)

        path.write_text(original.replace("'sample_output_write': {", "'sample_output_write_removed': {", 1), encoding="utf-8")
        issues = collect_issues(root)
        assert ("MISSING_FIXDEP_DIFF_EXPECTED_CASE", "sample_output_write") in issues
        assert ("UNEXPECTED_FIXDEP_DIFF_EXPECTED_CASE", "sample_output_write_removed") in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve(root, FIXDEP_DIFF_REL)
        original = read_text(path)
        path.write_text(
            original.replace("'stdout_mode': 'dev_full'", "'stdout_mode': 'pipe_full'", 1),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert (
            "FIXDEP_DIFF_EXPECTED_CASE_FIELD_MISMATCH",
            "sample_comment_only_stdout_full:stdout_mode='pipe_full':expected='dev_full'",
        ) in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve(root, FIXDEP_DIFF_REL)
        original = read_text(path)
        path.write_text(original.replace("'sample': {", "'zzz': {", 1), encoding="utf-8")
        issues = collect_issues(root)
        assert any(code == "FIXDEP_DIFF_EXPECTED_CASE_ORDER_MISMATCH" for code, _ in issues)
        checks_run += 1

        build_self_test_root(root)
        path = resolve(root, FIXDEP_CASES_REL)
        original_cases = json.loads(read_text(path))
        original_cases[0]["target"] = "sample-renamed.o"
        path.write_text(json.dumps(original_cases, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert (
            "FIXDEP_CASE_FIELD_MISMATCH",
            "sample:target='sample-renamed.o':expected='sample.o'",
        ) in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve(root, FIXDEP_CASES_REL)
        path.write_text("{broken\n", encoding="utf-8")
        assert ("INVALID_FIXDEP_CASES_JSON", path.as_posix()) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve(root, FIXDEP_SURVEY_REL)
        path.write_text(read_text(path).replace(SURVEY_REQUIRED_MARKERS[0], "", 1), encoding="utf-8")
        assert ("MISSING_SURVEY_MARKER", SURVEY_REQUIRED_MARKERS[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve(root, SCRIPTS_README_REL)
        path.write_text(read_text(path).replace(SCRIPTS_README_REQUIRED_MARKERS[1], "", 1), encoding="utf-8")
        assert ("MISSING_SCRIPTS_README_MARKER", SCRIPTS_README_REQUIRED_MARKERS[1]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve(root, MAKEFILE_REL)
        path.write_text(read_text(path).replace(REQUIRED_MAKEFILE_LINES[0], "", 1), encoding="utf-8")
        assert ("MISSING_MAKEFILE_LINE", REQUIRED_MAKEFILE_LINES[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve(root, WORKFLOW_REL)
        path.write_text(read_text(path).replace(REQUIRED_WORKFLOW_LINES[0], "", 1), encoding="utf-8")
        assert ("MISSING_WORKFLOW_LINE", REQUIRED_WORKFLOW_LINES[0]) in collect_issues(root)
        checks_run += 1

    print("PHASE2_FIXDEP_GATE_SELF_TEST=pass")
    print(f"PHASE2_FIXDEP_GATE_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the live fixdep governance packet matches current Phase 2 surfaces."
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_FIXDEP_GATE=pass")
    print(f"PHASE2_FIXDEP_GATE_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE2_FIXDEP_GATE_REQUIRED_FIXDEP_CASE_COUNT={len(REQUIRED_FIXDEP_CASE_NAMES)}")
    print(f"PHASE2_FIXDEP_GATE_REQUIRED_EXPECTED_CASE_COUNT={len(REQUIRED_FIXDEP_EXPECTED_CASES)}")
    print(f"PHASE2_FIXDEP_GATE_REQUIRED_WORKFLOW_LINE_COUNT={len(REQUIRED_WORKFLOW_LINES)}")
    print(f"PHASE2_FIXDEP_GATE_REQUIRED_MAKEFILE_LINE_COUNT={len(REQUIRED_MAKEFILE_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
