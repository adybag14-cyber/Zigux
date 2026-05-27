#!/usr/bin/env python3
"""Guard the current Phase 2 validation-wrapper packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2] if len(HERE.parents) > 2 else Path.cwd()

BOOTSTRAP_WORKFLOW_ROUTES = Path("scripts/zigux/check-phase2-bootstrap-workflow-routes.py")
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE = Path("zigux/Makefile")
VALIDATOR = Path("scripts/zigux/validate-phase2.py")
CLOSURE_VALIDATOR = Path("scripts/zigux/validate-phase2-closure.py")
TOOLCHAIN_NOTES = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
PHASE2_CLOSURE = Path("Documentation/zigux/phase2-closure.md")
TOOL_MANIFEST = Path("zigux/tests/fixtures/phase2_tool_manifest.json")

REQUIRED_FILES = (
    BOOTSTRAP_WORKFLOW_ROUTES,
    MAKEFILE,
    VALIDATOR,
    CLOSURE_VALIDATOR,
    TOOLCHAIN_NOTES,
    PHASE2_CLOSURE,
    TOOL_MANIFEST,
)

REQUIRED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py --self-test",
    "run: python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py",
    "run: make -C zigux phase2-toolchain",
    "run: make -C zigux phase2-tools",
    "run: make -C zigux phase2-kconfig",
    "run: make -C zigux phase2-cross",
    "run: make -C zigux phase2-genksyms",
    "run: make -C zigux phase2-fixdep",
    "run: make -C zigux phase2-validate",
    "run: python3 scripts/zigux/validate-phase2.py",
)

REQUIRED_MAKEFILE_LINES = (
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
    "phase2: phase2-validate",
)

REQUIRED_VALIDATOR_MARKERS = (
    '"scripts/zigux/check-phase2-bootstrap-workflow-routes.py",',
    '"run: python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py --self-test",',
    '"run: python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py",',
    '"run: make -C zigux phase2-validate",',
    '"phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",',
    'print("PHASE2_VALIDATION=pass")',
)

REQUIRED_CLOSURE_VALIDATOR_MARKERS = (
    'BOOTSTRAP_WORKFLOW_ROUTES_CHECKER_REL = Path("scripts/zigux/check-phase2-bootstrap-workflow-routes.py")',
    '"`scripts/zigux/check-phase2-bootstrap-workflow-routes.py`",',
    '"`make -C zigux phase2-validate`",',
    'print("PHASE2_CLOSURE_VALIDATION=pass")',
)

REQUIRED_TOOLCHAIN_NOTES_SNIPPETS = (
    "`scripts/zigux/check-phase2-bootstrap-workflow-routes.py`",
    "`scripts/zigux/validate-phase2.py`",
    "`make -C zigux phase2-validate`",
)

REQUIRED_CLOSURE_SNIPPETS = (
    "`scripts/zigux/check-phase2-bootstrap-workflow-routes.py`",
    "`scripts/zigux/validate-phase2.py`",
    "`make -C zigux phase2-validate`",
    "`PHASE2_SHARED_MAKE_ROUTES=",
)

REQUIRED_MANIFEST_SNIPPETS = (
    '"scripts/zigux/check-phase2-bootstrap-workflow-routes.py"',
    '"scripts/zigux/validate-phase2.py"',
    '"make -C zigux phase2-validate"',
    '"make -C zigux phase2"',
)

EXPECTED_SELF_TEST_CASE_COUNT = 22


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


def remove_once(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, "", 1)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    workflow_text = read_text(root / WORKFLOW)

    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            issues.append(("MISSING_REQUIRED_FILE", rel.as_posix()))

    if issues:
        return issues

    makefile_text = read_text(root / MAKEFILE)
    validator_text = read_text(root / VALIDATOR)
    closure_validator_text = read_text(root / CLOSURE_VALIDATOR)
    notes_text = read_text(root / TOOLCHAIN_NOTES)
    closure_text = read_text(root / PHASE2_CLOSURE)
    manifest_text = read_text(root / TOOL_MANIFEST)

    for marker in REQUIRED_WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))

    for marker in REQUIRED_MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))

    for marker in REQUIRED_VALIDATOR_MARKERS:
        count = validator_text.count(marker)
        if count == 0:
            issues.append(("MISSING_VALIDATOR_MARKER", marker))
        elif count != 1:
            issues.append(("DUPLICATE_VALIDATOR_MARKER", f"{marker}:count={count}"))

    for marker in REQUIRED_CLOSURE_VALIDATOR_MARKERS:
        count = closure_validator_text.count(marker)
        if count == 0:
            issues.append(("MISSING_CLOSURE_VALIDATOR_MARKER", marker))
        elif count != 1:
            issues.append(("DUPLICATE_CLOSURE_VALIDATOR_MARKER", f"{marker}:count={count}"))

    for marker in REQUIRED_TOOLCHAIN_NOTES_SNIPPETS:
        if marker not in notes_text:
            issues.append(("MISSING_TOOLCHAIN_NOTES_MARKER", marker))

    for marker in REQUIRED_CLOSURE_SNIPPETS:
        if marker not in closure_text:
            issues.append(("MISSING_CLOSURE_MARKER", marker))

    for marker in REQUIRED_MANIFEST_SNIPPETS:
        if marker not in manifest_text:
            issues.append(("MISSING_MANIFEST_MARKER", marker))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_VALIDATION_WRAPPER=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(root / WORKFLOW, "\n".join(("name: zigux-bootstrap", *REQUIRED_WORKFLOW_LINES)) + "\n")
    write_text(
        root / MAKEFILE,
        "\n".join(("PYTHON ?= python3", "PHASE2_SCRIPT_ROOT := ../scripts/zigux", *REQUIRED_MAKEFILE_LINES)) + "\n",
    )
    write_text(root / VALIDATOR, "\n".join(REQUIRED_VALIDATOR_MARKERS) + "\n")
    write_text(root / CLOSURE_VALIDATOR, "\n".join(REQUIRED_CLOSURE_VALIDATOR_MARKERS) + "\n")
    write_text(root / TOOLCHAIN_NOTES, "\n".join(REQUIRED_TOOLCHAIN_NOTES_SNIPPETS) + "\n")
    write_text(root / PHASE2_CLOSURE, "\n".join(REQUIRED_CLOSURE_SNIPPETS) + "\n")
    write_text(root / TOOL_MANIFEST, "\n".join(REQUIRED_MANIFEST_SNIPPETS) + "\n")
    write_text(root / BOOTSTRAP_WORKFLOW_ROUTES, "present\n")


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_validation_wrapper_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks += 1

        for marker in (REQUIRED_WORKFLOW_LINES[0], REQUIRED_WORKFLOW_LINES[-1], REQUIRED_WORKFLOW_LINES[-2]):
            build_self_test_root(root)
            path = root / WORKFLOW
            path.write_text(replace_exact_line(read_text(path), marker, "run: python3 scripts/zigux/other.py"), encoding="utf-8")
            assert (("MISSING_WORKFLOW_LINE", marker)) in collect_issues(root)
            checks += 1

        for marker in (REQUIRED_WORKFLOW_LINES[1], REQUIRED_WORKFLOW_LINES[-2]):
            build_self_test_root(root)
            path = root / WORKFLOW
            path.write_text(duplicate_exact_line(read_text(path), marker), encoding="utf-8")
            assert (("DUPLICATE_WORKFLOW_LINE", f"{marker}:count=2")) in collect_issues(root)
            checks += 1

        for marker in (REQUIRED_MAKEFILE_LINES[0], REQUIRED_MAKEFILE_LINES[-1]):
            build_self_test_root(root)
            path = root / MAKEFILE
            path.write_text(replace_exact_line(read_text(path), marker, "# removed"), encoding="utf-8")
            assert (("MISSING_MAKEFILE_LINE", marker)) in collect_issues(root)
            checks += 1

        for marker in (REQUIRED_MAKEFILE_LINES[1], REQUIRED_MAKEFILE_LINES[-2]):
            build_self_test_root(root)
            path = root / MAKEFILE
            path.write_text(duplicate_exact_line(read_text(path), marker), encoding="utf-8")
            assert (("DUPLICATE_MAKEFILE_LINE", f"{marker}:count=2")) in collect_issues(root)
            checks += 1

        for marker in (REQUIRED_VALIDATOR_MARKERS[0], REQUIRED_VALIDATOR_MARKERS[-1]):
            build_self_test_root(root)
            path = root / VALIDATOR
            path.write_text(remove_once(read_text(path), marker), encoding="utf-8")
            assert (("MISSING_VALIDATOR_MARKER", marker)) in collect_issues(root)
            checks += 1

        build_self_test_root(root)
        path = root / VALIDATOR
        path.write_text(read_text(path) + REQUIRED_VALIDATOR_MARKERS[1] + "\n", encoding="utf-8")
        assert (("DUPLICATE_VALIDATOR_MARKER", f"{REQUIRED_VALIDATOR_MARKERS[1]}:count=2")) in collect_issues(root)
        checks += 1

        for marker in (REQUIRED_CLOSURE_VALIDATOR_MARKERS[0], REQUIRED_CLOSURE_VALIDATOR_MARKERS[-1]):
            build_self_test_root(root)
            path = root / CLOSURE_VALIDATOR
            path.write_text(remove_once(read_text(path), marker), encoding="utf-8")
            assert (("MISSING_CLOSURE_VALIDATOR_MARKER", marker)) in collect_issues(root)
            checks += 1

        build_self_test_root(root)
        path = root / CLOSURE_VALIDATOR
        path.write_text(read_text(path) + REQUIRED_CLOSURE_VALIDATOR_MARKERS[1] + "\n", encoding="utf-8")
        assert (("DUPLICATE_CLOSURE_VALIDATOR_MARKER", f"{REQUIRED_CLOSURE_VALIDATOR_MARKERS[1]}:count=2")) in collect_issues(root)
        checks += 1

        for rel, marker, code in (
            (TOOLCHAIN_NOTES, REQUIRED_TOOLCHAIN_NOTES_SNIPPETS[0], "MISSING_TOOLCHAIN_NOTES_MARKER"),
            (PHASE2_CLOSURE, REQUIRED_CLOSURE_SNIPPETS[-1], "MISSING_CLOSURE_MARKER"),
            (TOOL_MANIFEST, REQUIRED_MANIFEST_SNIPPETS[-1], "MISSING_MANIFEST_MARKER"),
        ):
            build_self_test_root(root)
            path = root / rel
            path.write_text(remove_once(read_text(path), marker), encoding="utf-8")
            assert (code, marker) in collect_issues(root)
            checks += 1

        for rel in (BOOTSTRAP_WORKFLOW_ROUTES, VALIDATOR, TOOL_MANIFEST):
            build_self_test_root(root)
            (root / rel).unlink()
            assert (("MISSING_REQUIRED_FILE", rel.as_posix())) in collect_issues(root)
            checks += 1

    assert checks == EXPECTED_SELF_TEST_CASE_COUNT, checks
    print("PHASE2_VALIDATION_WRAPPER_SELF_TEST=pass")
    print(f"PHASE2_VALIDATION_WRAPPER_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_VALIDATION_WRAPPER=pass")
    print(f"PHASE2_VALIDATION_WRAPPER_WORKFLOW_LINE_COUNT={len(REQUIRED_WORKFLOW_LINES)}")
    print(f"PHASE2_VALIDATION_WRAPPER_MAKEFILE_LINE_COUNT={len(REQUIRED_MAKEFILE_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
