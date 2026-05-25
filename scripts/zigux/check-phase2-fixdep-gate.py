#!/usr/bin/env python3
"""Check the current fixdep governance packet against live Phase 2 surfaces."""

from __future__ import annotations

import argparse
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
    MAKEFILE_REL,
    WORKFLOW_REL,
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
    'test "open dependency file classification preserves unrelated open failures" {',
    'test "read failure wording matches C perror prefix" {',
    'test "output write failure uses C-style wording" {',
    'test "flush helper preserves the primary error" {',
    'test "dependency file reads beyond the legacy one mebibyte ceiling" {',
    'test "escaped hash dependency survives concatenated target comment path" {',
    'test "escaped colon dependency survives concatenated target comment path" {',
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
    "EXPECTED_SELF_TEST_CASE_COUNT = 15",
    'print("FIXDEP_SELF_TEST=pass")',
    'print(f"FIXDEP_SELF_TEST_CASE_COUNT={checks_run}")',
    'print("FIXDEP_DIFF=pass")',
    'print("FIXDEP_DETERMINISM=pass")',
    "assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT",
)

FIXDEP_DIFF_CONTRACT_EXACT_LINES = (
    "EXPECTED_FIXTURE_FILES = frozenset(",
    "EXPECTED_CASE_ORDER = list(EXPECTED_CASES)",
    "def validate_fixture_inventory(",
    "actual_files = {path.name for path in fixture_dir.iterdir() if path.is_file()}",
    'raise FileNotFoundError(f"{fixture_dir}:missing_fixtures:{\',\'.join(missing)}")',
    'raise ValueError(f"{fixture_dir}:unexpected_fixtures:{\',\'.join(unexpected)}")',
    "expected_case = EXPECTED_CASES.get(name)",
    'raise ValueError(f"{CASES_PATH}:unexpected_name:{name}")',
    'expected_stdout_name = validated_case.get("expected_stdout", validated_case.get("expected"))',
    'raise FileNotFoundError(f"{CASES_PATH}:missing_expected_output:{expected_stdout_name}")',
    "if expected_exit_code != 0:",
    'expected_stderr_name = validated_case.get("expected_stderr")',
    'raise FileNotFoundError(f"{CASES_PATH}:missing_expected_stderr:{expected_stderr_name}")',
    'if stdout_mode not in (None, "dev_full"):',
    'raise ValueError(f"{CASES_PATH}:{name}:unsupported_stdout_mode:{stdout_mode!r}")',
    'if seen_names != EXPECTED_CASE_ORDER:',
    'raise ValueError(f"{CASES_PATH}:case_order={seen_names!r},expected={EXPECTED_CASE_ORDER!r}")',
    'if len(validated) != len(EXPECTED_CASES):',
    'raise ValueError(f"{CASES_PATH}:count={len(validated)},expected={len(EXPECTED_CASES)}")',
    "missing_names = sorted(set(EXPECTED_CASES) - seen_name_set)",
    'if missing_names:',
    'raise ValueError(f"{CASES_PATH}:missing_name:{missing_names[0]}")',
    "validate_fixture_inventory()",
    "cases = validate_cases(load_cases(CASES_PATH))",
)

VALIDATE_PHASE2_REQUIRED_PATH_LINES = (
    '"scripts/zigux/check-phase2-fixdep-gate.py",',
    '"scripts/zigux/check-fixdep-diff.py",',
    '"scripts/zigux/fixdep.zig",',
    '"zigux/tests/fixtures/fixdep/cases.json",',
)

VALIDATE_PHASE2_REQUIRED_WORKFLOW_LINES = (
    '"run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",',
    '"run: python3 scripts/zigux/check-phase2-fixdep-gate.py",',
    '"run: python3 scripts/zigux/check-fixdep-diff.py --self-test",',
    '"run: python3 scripts/zigux/check-fixdep-diff.py",',
    '"run: zig test scripts/zigux/fixdep.zig",',
    '"run: make -C zigux phase2-fixdep",',
)

VALIDATE_PHASE2_REQUIRED_MAKEFILE_LINES = (
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

CLOSURE_REQUIRED_MARKERS = (
    "`Documentation/zigux/phase2-closure.md`",
    "`zigux/Makefile`",
    "`zigux/tests/README.md`",
    "fixture-backed artifact",
)

FIXDEP_CLOSURE_REQUIRED_MARKERS = (
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
)

FIXDEP_TESTS_README_REQUIRED_MARKERS = (
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`scripts/zigux/fixdep.zig`",
    "`zigux/tests/fixtures/fixdep/cases.json`",
    "`make -C zigux phase2-fixdep`",
)

REQUIRED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "run: python3 scripts/zigux/check-phase2-fixdep-gate.py",
    "run: python3 scripts/zigux/check-fixdep-diff.py --self-test",
    "run: python3 scripts/zigux/check-fixdep-diff.py",
    "run: make -C zigux phase2-fixdep",
    "run: zig test scripts/zigux/fixdep.zig",
)

REQUIRED_MAKEFILE_PHONY_TARGETS = (
    "phase2-fixdep",
    "phase2-validate",
    "phase2",
)

REQUIRED_MAKEFILE_LINES = (
    "phase2-fixdep:",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/fixdep.zig",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
)

EXPECTED_SELF_TEST_CASE_COUNT = (
    1
    + len(FIXDEP_REQUIRED_EXACT_LINES)
    + len(FIXDEP_REQUIRED_EXACT_LINES)
    + len(FIXDEP_DIFF_REQUIRED_EXACT_LINES)
    + len(FIXDEP_DIFF_REQUIRED_EXACT_LINES)
    + len(FIXDEP_DIFF_CONTRACT_EXACT_LINES)
    + len(FIXDEP_DIFF_CONTRACT_EXACT_LINES)
    + len(VALIDATE_PHASE2_REQUIRED_PATH_LINES)
    + len(VALIDATE_PHASE2_REQUIRED_PATH_LINES)
    + len(VALIDATE_PHASE2_REQUIRED_WORKFLOW_LINES)
    + len(VALIDATE_PHASE2_REQUIRED_WORKFLOW_LINES)
    + len(VALIDATE_PHASE2_REQUIRED_MAKEFILE_LINES)
    + len(VALIDATE_PHASE2_REQUIRED_MAKEFILE_LINES)
    + len(REQUIRED_FIXDEP_CASE_NAMES)
    + 9
    + len(CLOSURE_REQUIRED_MARKERS)
    + len(FIXDEP_CLOSURE_REQUIRED_MARKERS)
    + len(TESTS_README_REQUIRED_MARKERS)
    + len(FIXDEP_TESTS_README_REQUIRED_MARKERS)
    + len(REQUIRED_WORKFLOW_LINES)
    + len(REQUIRED_WORKFLOW_LINES)
    + len(REQUIRED_MAKEFILE_PHONY_TARGETS)
    + len(REQUIRED_MAKEFILE_LINES)
    + len(REQUIRED_MAKEFILE_LINES)
    + len(REQUIRED_FILES)
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


def phony_targets_present(text: str) -> set[str]:
    targets: set[str] = set()
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(".PHONY:"):
            _, suffix = stripped.split(":", 1)
            targets.update(token for token in suffix.strip().split() if token)
    return targets


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


def collect_exact_line_order_issue(
    text: str, markers: tuple[str, ...], code: str
) -> list[tuple[str, str]]:
    marker_set = set(markers)
    actual = [line.strip() for line in text.splitlines() if line.strip() in marker_set]
    expected = list(markers)
    if len(actual) != len(expected):
        return []
    if actual != expected:
        return [(code, f"actual={actual!r}:expected={expected!r}")]
    return []


def collect_fixdep_case_issues(path: Path) -> list[tuple[str, str]]:
    try:
        raw_cases = json.loads(read_text(path))
    except json.JSONDecodeError:
        return [("INVALID_FIXDEP_CASES_JSON", path.as_posix())]

    if not isinstance(raw_cases, list):
        return [("INVALID_FIXDEP_CASES_JSON", path.as_posix())]

    issues: list[tuple[str, str]] = []
    actual_names: list[str] = []
    seen_names: set[str] = set()
    duplicate_names: set[str] = set()

    for index, raw_case in enumerate(raw_cases):
        if not isinstance(raw_case, dict):
            issues.append(("INVALID_FIXDEP_CASE_ENTRY", f"index={index}:type={type(raw_case).__name__}"))
            continue

        name = raw_case.get("name")
        if not isinstance(name, str) or not name:
            issues.append(("INVALID_FIXDEP_CASE_NAME", f"index={index}:name={name!r}"))
            continue

        actual_names.append(name)
        if name in seen_names:
            duplicate_names.add(name)
        else:
            seen_names.add(name)

        if name not in REQUIRED_FIXDEP_CASE_NAMES:
            issues.append(("UNEXPECTED_FIXDEP_CASE", name))

    for name in sorted(duplicate_names):
        issues.append(("DUPLICATE_FIXDEP_CASE", name))

    expected_names = list(REQUIRED_FIXDEP_CASE_NAMES)
    if actual_names != expected_names:
        issues.append(
            (
                "FIXDEP_CASE_ORDER_MISMATCH",
                f"actual={actual_names!r}:expected={expected_names!r}",
            )
        )

    issues.extend(
        ("MISSING_FIXDEP_CASE", name)
        for name in REQUIRED_FIXDEP_CASE_NAMES
        if name not in seen_names
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
    closure_text = read_text(resolve(root, PHASE2_CLOSURE_REL))
    tests_readme_text = read_text(resolve(root, TESTS_README_REL))
    makefile_text = read_text(resolve(root, MAKEFILE_REL))
    workflow_text = read_text(resolve(root, WORKFLOW_REL))

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
    issues.extend(
        collect_required_exact_lines(
            validate_phase2_text,
            VALIDATE_PHASE2_REQUIRED_PATH_LINES,
            "MISSING_VALIDATE_PHASE2_PATH_LINE",
            "DUPLICATE_VALIDATE_PHASE2_PATH_LINE",
        )
    )
    issues.extend(
        collect_required_exact_lines(
            validate_phase2_text,
            VALIDATE_PHASE2_REQUIRED_WORKFLOW_LINES,
            "MISSING_VALIDATE_PHASE2_WORKFLOW_LINE",
            "DUPLICATE_VALIDATE_PHASE2_WORKFLOW_LINE",
        )
    )
    issues.extend(
        collect_required_exact_lines(
            validate_phase2_text,
            VALIDATE_PHASE2_REQUIRED_MAKEFILE_LINES,
            "MISSING_VALIDATE_PHASE2_MAKEFILE_LINE",
            "DUPLICATE_VALIDATE_PHASE2_MAKEFILE_LINE",
        )
    )
    issues.extend(collect_fixdep_case_issues(resolve(root, FIXDEP_CASES_REL)))
    issues.extend(
        collect_missing_markers(closure_text, CLOSURE_REQUIRED_MARKERS, "MISSING_CLOSURE_MARKER")
    )
    issues.extend(
        collect_missing_markers(
            closure_text,
            FIXDEP_CLOSURE_REQUIRED_MARKERS,
            "MISSING_FIXDEP_CLOSURE_MARKER",
        )
    )
    issues.extend(
        collect_missing_markers(
            tests_readme_text, TESTS_README_REQUIRED_MARKERS, "MISSING_TESTS_README_MARKER"
        )
    )
    issues.extend(
        collect_missing_markers(
            tests_readme_text,
            FIXDEP_TESTS_README_REQUIRED_MARKERS,
            "MISSING_FIXDEP_TESTS_README_MARKER",
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
    issues.extend(
        collect_exact_line_order_issue(
            workflow_text,
            REQUIRED_WORKFLOW_LINES,
            "FIXDEP_WORKFLOW_ORDER_MISMATCH",
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
    issues.extend(
        collect_exact_line_order_issue(
            makefile_text,
            REQUIRED_MAKEFILE_LINES,
            "FIXDEP_MAKEFILE_ORDER_MISMATCH",
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


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def replace_exact_line(text: str, marker: str, replacement: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def remove_phony_target(text: str, target: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(".PHONY:"):
            prefix, suffix = stripped.split(":", 1)
            targets = [token for token in suffix.strip().split() if token and token != target]
            lines[index] = f"{prefix}: {' '.join(targets)}"
            return "\n".join(lines) + "\n"
    raise AssertionError(f".PHONY line not found while removing target: {target}")


def append_line(text: str, line: str) -> str:
    return text + line + "\n"


def swap_exact_lines(text: str, first: str, second: str) -> str:
    lines = text.splitlines()
    first_index = None
    second_index = None
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped == first and first_index is None:
            first_index = index
        if stripped == second and second_index is None:
            second_index = index
    if first_index is None or second_index is None:
        raise AssertionError(f"marker line not found for swap: {first!r} / {second!r}")
    lines[first_index], lines[second_index] = lines[second_index], lines[first_index]
    return "\n".join(lines) + "\n"


def build_self_test_root(root: Path) -> None:
    write_text(
        resolve(root, FIXDEP_REL),
        "\n".join(
            (
                'test "config parsing trims _MODULE and deduplicates symbols" {',
                "}",
                'test "config parsing ignores prefixed CONFIG tokens like upstream fixdep" {',
                "}",
                'test "config parsing accepts CONFIG tokens after punctuation" {',
                "}",
                'test "config parsing stops at the first embedded NUL" {',
                "}",
                'test "dep parsing returns NoTargets for comment-only depfiles" {',
                "}",
                'test "dep parsing keeps escaped spaces inside tokens" {',
                "}",
                'test "dep parsing continues dependency lines across escaped newlines" {',
                "}",
                'test "dep parsing accepts CRLF lines and continuations" {',
                "}",
                'test "dep parsing does not continue bare carriage-return lines" {',
                "}",
                'test "dep parsing skips bytes after the first embedded NUL" {',
                "}",
                'test "ignored and no-parse file classification matches fixdep rules" {',
                "}",
                'test "file read errors map to C-style messages" {',
                "}",
                'test "file read errors map short reads to unexpected end of file" {',
                "}",
                'test "exact read size helper rejects short reads" {',
                "}",
                'test "path error wording keeps the dedicated fstat prefix" {',
                "}",
                'test "open dependency file classification keeps input-output failures on the C-style path" {',
                "}",
                'test "open dependency file classification preserves unrelated open failures" {',
                "}",
                'test "read failure wording matches C perror prefix" {',
                "}",
                'test "output write failure uses C-style wording" {',
                "}",
                'test "flush helper preserves the primary error" {',
                "}",
                'test "dependency file reads beyond the legacy one mebibyte ceiling" {',
                "}",
                'test "escaped hash dependency survives concatenated target comment path" {',
                "}",
                'test "escaped colon dependency survives concatenated target comment path" {',
                "}",
            )
        )
        + "\n",
    )
    write_text(
        resolve(root, FIXDEP_DIFF_REL),
        "\n".join(
            (
                *FIXDEP_DIFF_REQUIRED_EXACT_LINES,
                *FIXDEP_DIFF_CONTRACT_EXACT_LINES,
            )
        )
        + "\n",
    )
    write_text(
        resolve(root, VALIDATE_PHASE2_REL),
        "\n".join(
            (
                "REQUIRED_PATHS = (",
                *VALIDATE_PHASE2_REQUIRED_PATH_LINES,
                ")",
                "REQUIRED_WORKFLOW_LINES = (",
                *VALIDATE_PHASE2_REQUIRED_WORKFLOW_LINES,
                ")",
                "REQUIRED_MAKEFILE_LINES = (",
                *VALIDATE_PHASE2_REQUIRED_MAKEFILE_LINES,
                ")",
            )
        )
        + "\n",
    )
    write_text(
        resolve(root, FIXDEP_CASES_REL),
        json.dumps([{"name": name} for name in REQUIRED_FIXDEP_CASE_NAMES], indent=2) + "\n",
    )
    write_text(resolve(root, FIXDEP_SURVEY_REL), "present\n")
    write_text(
        resolve(root, PHASE2_CLOSURE_REL),
        "\n".join(
            (
                "# Phase 2 Closure",
                "- `Documentation/zigux/phase2-closure.md`",
                "- `zigux/Makefile`",
                "- `zigux/tests/README.md`",
                "- `scripts/zigux/check-phase2-fixdep-gate.py`",
                "- `scripts/zigux/check-fixdep-diff.py`",
                "- `scripts/zigux/fixdep.zig`",
                "- `zigux/tests/fixtures/fixdep/cases.json`",
                "- `make -C zigux phase2-fixdep`",
                "The bounded Phase 2 tranche remains the directly readable toolchain, kbuild-route, kconfig-bridge, required-make-route, validator-entrypoint, closure-validator, and fixture-backed artifact packet already present on current `master`.",
            )
        )
        + "\n",
    )
    write_text(
        resolve(root, TESTS_README_REL),
        "\n".join(
            (
                "# zigux/tests",
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
        )
        + "\n",
    )
    write_text(
        resolve(root, MAKEFILE_REL),
        "\n".join(
            (
                "PYTHON ?= python3",
                ".PHONY: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2",
                "phase2-fixdep:",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py",
                "\tcd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/fixdep.zig",
                "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
                "phase2: phase2-validate",
            )
        )
        + "\n",
    )
    workflow_lines = [
        "name: zigux-bootstrap",
        "jobs:",
        "  bootstrap:",
        "    steps:",
    ]
    for index, marker in enumerate(REQUIRED_WORKFLOW_LINES, start=1):
        workflow_lines.append(f"      - name: fixdep-step-{index}")
        workflow_lines.append(f"        {marker}")
    write_text(resolve(root, WORKFLOW_REL), "\n".join(workflow_lines) + "\n")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_fixdep_gate_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_self_test_root(root)
        path = resolve(root, FIXDEP_CASES_REL)
        path.write_text("{broken\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("INVALID_FIXDEP_CASES_JSON", path.as_posix()) in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve(root, FIXDEP_CASES_REL)
        path.write_text("{}\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("INVALID_FIXDEP_CASES_JSON", path.as_posix()) in issues
        checks_run += 1

        for marker in FIXDEP_REQUIRED_EXACT_LINES:
            build_self_test_root(root)
            path = resolve(root, FIXDEP_REL)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_FIXDEP_TEST_LINE", marker) in collect_issues(root)
            checks_run += 1

        for marker in FIXDEP_REQUIRED_EXACT_LINES:
            build_self_test_root(root)
            path = resolve(root, FIXDEP_REL)
            path.write_text(append_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("DUPLICATE_FIXDEP_TEST_LINE", f"{marker}:count=2") in collect_issues(root)
            checks_run += 1

        for marker in FIXDEP_DIFF_REQUIRED_EXACT_LINES:
            build_self_test_root(root)
            path = resolve(root, FIXDEP_DIFF_REL)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_FIXDEP_DIFF_LINE", marker) in collect_issues(root)
            checks_run += 1

        for marker in FIXDEP_DIFF_REQUIRED_EXACT_LINES:
            build_self_test_root(root)
            path = resolve(root, FIXDEP_DIFF_REL)
            path.write_text(append_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("DUPLICATE_FIXDEP_DIFF_LINE", f"{marker}:count=2") in collect_issues(root)
            checks_run += 1

        for marker in FIXDEP_DIFF_CONTRACT_EXACT_LINES:
            build_self_test_root(root)
            path = resolve(root, FIXDEP_DIFF_REL)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_FIXDEP_DIFF_CONTRACT_LINE", marker) in collect_issues(root)
            checks_run += 1

        for marker in FIXDEP_DIFF_CONTRACT_EXACT_LINES:
            build_self_test_root(root)
            path = resolve(root, FIXDEP_DIFF_REL)
            path.write_text(append_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert (
                "DUPLICATE_FIXDEP_DIFF_CONTRACT_LINE",
                f"{marker}:count=2",
            ) in collect_issues(root)
            checks_run += 1

        for marker in VALIDATE_PHASE2_REQUIRED_PATH_LINES:
            build_self_test_root(root)
            path = resolve(root, VALIDATE_PHASE2_REL)
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), marker, "# removed"), encoding="utf-8")
            assert ("MISSING_VALIDATE_PHASE2_PATH_LINE", marker) in collect_issues(root)
            checks_run += 1

        for marker in VALIDATE_PHASE2_REQUIRED_PATH_LINES:
            build_self_test_root(root)
            path = resolve(root, VALIDATE_PHASE2_REL)
            path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("DUPLICATE_VALIDATE_PHASE2_PATH_LINE", f"{marker}:count=2") in collect_issues(root)
            checks_run += 1

        for marker in VALIDATE_PHASE2_REQUIRED_WORKFLOW_LINES:
            build_self_test_root(root)
            path = resolve(root, VALIDATE_PHASE2_REL)
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), marker, "# removed"), encoding="utf-8")
            assert ("MISSING_VALIDATE_PHASE2_WORKFLOW_LINE", marker) in collect_issues(root)
            checks_run += 1

        for marker in VALIDATE_PHASE2_REQUIRED_WORKFLOW_LINES:
            build_self_test_root(root)
            path = resolve(root, VALIDATE_PHASE2_REL)
            path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("DUPLICATE_VALIDATE_PHASE2_WORKFLOW_LINE", f"{marker}:count=2") in collect_issues(root)
            checks_run += 1

        for marker in VALIDATE_PHASE2_REQUIRED_MAKEFILE_LINES:
            build_self_test_root(root)
            path = resolve(root, VALIDATE_PHASE2_REL)
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), marker, "# removed"), encoding="utf-8")
            assert ("MISSING_VALIDATE_PHASE2_MAKEFILE_LINE", marker) in collect_issues(root)
            checks_run += 1

        for marker in VALIDATE_PHASE2_REQUIRED_MAKEFILE_LINES:
            build_self_test_root(root)
            path = resolve(root, VALIDATE_PHASE2_REL)
            path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("DUPLICATE_VALIDATE_PHASE2_MAKEFILE_LINE", f"{marker}:count=2") in collect_issues(root)
            checks_run += 1

        for name in REQUIRED_FIXDEP_CASE_NAMES:
            build_self_test_root(root)
            path = resolve(root, FIXDEP_CASES_REL)
            cases = json.loads(path.read_text(encoding="utf-8"))
            cases = [case for case in cases if case.get("name") != name]
            path.write_text(json.dumps(cases, indent=2) + "\n", encoding="utf-8")
            assert ("MISSING_FIXDEP_CASE", name) in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        path = resolve(root, FIXDEP_CASES_REL)
        cases = json.loads(path.read_text(encoding="utf-8"))
        cases[1]["name"] = cases[0]["name"]
        path.write_text(json.dumps(cases, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("DUPLICATE_FIXDEP_CASE", REQUIRED_FIXDEP_CASE_NAMES[0]) in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve(root, FIXDEP_CASES_REL)
        cases = json.loads(path.read_text(encoding="utf-8"))
        cases[0]["name"] = "unexpected_fixdep_case"
        path.write_text(json.dumps(cases, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("UNEXPECTED_FIXDEP_CASE", "unexpected_fixdep_case") in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve(root, FIXDEP_CASES_REL)
        cases = json.loads(path.read_text(encoding="utf-8"))
        cases[0], cases[1] = cases[1], cases[0]
        path.write_text(json.dumps(cases, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert any(code == "FIXDEP_CASE_ORDER_MISMATCH" for code, _ in issues)
        checks_run += 1

        build_self_test_root(root)
        path = resolve(root, FIXDEP_CASES_REL)
        cases = json.loads(path.read_text(encoding="utf-8"))
        cases[0] = "broken"
        path.write_text(json.dumps(cases, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("INVALID_FIXDEP_CASE_ENTRY", "index=0:type=str") in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve(root, FIXDEP_CASES_REL)
        cases = json.loads(path.read_text(encoding="utf-8"))
        cases[0]["name"] = ""
        path.write_text(json.dumps(cases, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("INVALID_FIXDEP_CASE_NAME", "index=0:name=''" ) in issues
        checks_run += 1

        for marker in CLOSURE_REQUIRED_MARKERS:
            build_self_test_root(root)
            path = resolve(root, PHASE2_CLOSURE_REL)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_CLOSURE_MARKER", marker) in collect_issues(root)
            checks_run += 1

        for marker in FIXDEP_CLOSURE_REQUIRED_MARKERS:
            build_self_test_root(root)
            path = resolve(root, PHASE2_CLOSURE_REL)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_FIXDEP_CLOSURE_MARKER", marker) in collect_issues(root)
            checks_run += 1

        for marker in TESTS_README_REQUIRED_MARKERS:
            build_self_test_root(root)
            path = resolve(root, TESTS_README_REL)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_TESTS_README_MARKER", marker) in collect_issues(root)
            checks_run += 1

        for marker in FIXDEP_TESTS_README_REQUIRED_MARKERS:
            build_self_test_root(root)
            path = resolve(root, TESTS_README_REL)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_FIXDEP_TESTS_README_MARKER", marker) in collect_issues(root)
            checks_run += 1

        for marker in REQUIRED_WORKFLOW_LINES:
            build_self_test_root(root)
            path = resolve(root, WORKFLOW_REL)
            path.write_text(
                replace_exact_line(path.read_text(encoding="utf-8"), marker, "run: python3 scripts/zigux/other.py"),
                encoding="utf-8",
            )
            assert ("MISSING_WORKFLOW_LINE", marker) in collect_issues(root)
            checks_run += 1

        for marker in REQUIRED_WORKFLOW_LINES:
            build_self_test_root(root)
            path = resolve(root, WORKFLOW_REL)
            path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("DUPLICATE_WORKFLOW_LINE", f"{marker}:count=2") in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        path = resolve(root, WORKFLOW_REL)
        path.write_text(
            swap_exact_lines(
                path.read_text(encoding="utf-8"),
                REQUIRED_WORKFLOW_LINES[1],
                REQUIRED_WORKFLOW_LINES[2],
            ),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert any(code == "FIXDEP_WORKFLOW_ORDER_MISMATCH" for code, _ in issues)
        checks_run += 1

        for target in REQUIRED_MAKEFILE_PHONY_TARGETS:
            build_self_test_root(root)
            path = resolve(root, MAKEFILE_REL)
            path.write_text(remove_phony_target(path.read_text(encoding="utf-8"), target), encoding="utf-8")
            assert ("MISSING_MAKEFILE_PHONY_TARGET", target) in collect_issues(root)
            checks_run += 1

        for marker in REQUIRED_MAKEFILE_LINES:
            build_self_test_root(root)
            path = resolve(root, MAKEFILE_REL)
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), marker, "# removed"), encoding="utf-8")
            assert ("MISSING_MAKEFILE_LINE", marker) in collect_issues(root)
            checks_run += 1

        for marker in REQUIRED_MAKEFILE_LINES:
            build_self_test_root(root)
            path = resolve(root, MAKEFILE_REL)
            path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("DUPLICATE_MAKEFILE_LINE", f"{marker}:count=2") in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        path = resolve(root, MAKEFILE_REL)
        path.write_text(
            swap_exact_lines(
                path.read_text(encoding="utf-8"),
                REQUIRED_MAKEFILE_LINES[2],
                REQUIRED_MAKEFILE_LINES[3],
            ),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert any(code == "FIXDEP_MAKEFILE_ORDER_MISMATCH" for code, _ in issues)
        checks_run += 1

        for rel in REQUIRED_FILES:
            build_self_test_root(root)
            resolve(root, rel).unlink()
            issues = collect_issues(root)
            assert ("MISSING_REQUIRED_FILE", rel.as_posix()) in issues
            checks_run += 1

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
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
    print(f"PHASE2_FIXDEP_GATE_REQUIRED_FIXDEP_TEST_COUNT={len(FIXDEP_REQUIRED_EXACT_LINES)}")
    print(f"PHASE2_FIXDEP_GATE_REQUIRED_FIXDEP_DIFF_LINE_COUNT={len(FIXDEP_DIFF_REQUIRED_EXACT_LINES)}")
    print(f"PHASE2_FIXDEP_GATE_REQUIRED_FIXDEP_DIFF_CONTRACT_LINE_COUNT={len(FIXDEP_DIFF_CONTRACT_EXACT_LINES)}")
    print(f"PHASE2_FIXDEP_GATE_REQUIRED_VALIDATE_PHASE2_PATH_LINE_COUNT={len(VALIDATE_PHASE2_REQUIRED_PATH_LINES)}")
    print(f"PHASE2_FIXDEP_GATE_REQUIRED_VALIDATE_PHASE2_WORKFLOW_LINE_COUNT={len(VALIDATE_PHASE2_REQUIRED_WORKFLOW_LINES)}")
    print(f"PHASE2_FIXDEP_GATE_REQUIRED_VALIDATE_PHASE2_MAKEFILE_LINE_COUNT={len(VALIDATE_PHASE2_REQUIRED_MAKEFILE_LINES)}")
    print(f"PHASE2_FIXDEP_GATE_REQUIRED_FIXDEP_CASE_COUNT={len(REQUIRED_FIXDEP_CASE_NAMES)}")
    print(f"PHASE2_FIXDEP_GATE_REQUIRED_WORKFLOW_LINE_COUNT={len(REQUIRED_WORKFLOW_LINES)}")
    print(f"PHASE2_FIXDEP_GATE_REQUIRED_MAKEFILE_PHONY_TARGET_COUNT={len(REQUIRED_MAKEFILE_PHONY_TARGETS)}")
    print(f"PHASE2_FIXDEP_GATE_REQUIRED_MAKEFILE_LINE_COUNT={len(REQUIRED_MAKEFILE_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
