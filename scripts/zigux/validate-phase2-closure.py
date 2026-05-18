#!/usr/bin/env python3
"""Validate the current Phase 2 closure note against the shipped closure packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
PHASE2_CLOSURE_REL = Path("Documentation/zigux/phase2-closure.md")
PHASE2_BOOTSTRAP_NOTES_REL = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
PHASE2_VALIDATE_REL = Path("scripts/zigux/validate-phase2.py")
PHASE2_CLOSURE_VALIDATE_REL = Path("scripts/zigux/validate-phase2-closure.py")
TOOLCHAIN_CHECKER_REL = Path("scripts/zigux/check-zig-toolchain.py")
PINNING_CHECKER_REL = Path("scripts/zigux/check-phase2-toolchain-pinning.py")
PIN_SCOPE_CHECKER_REL = Path("scripts/zigux/check-phase2-toolchain-pin-scope.py")
KBUILD_CHECKER_REL = Path("scripts/zigux/check-phase2-kbuild-routes.py")
DOCS_REMINDER_CHECKER_REL = Path("scripts/zigux/check-phase2-docs-shared-reminder.py")
REQUIRED_ROUTES_CHECKER_REL = Path("scripts/zigux/check-phase2-required-make-routes.py")
MAKEFILE_REL = Path("zigux/Makefile")
MANIFEST_REL = Path("zigux/tests/fixtures/phase2_tool_manifest.json")
ARTIFACT_MANIFEST_REL = Path("zigux/tests/fixtures/phase2_artifact_tools_manifest.json")

REQUIRED_FILES = (
    WORKFLOW_REL,
    PHASE2_CLOSURE_REL,
    PHASE2_BOOTSTRAP_NOTES_REL,
    PHASE2_VALIDATE_REL,
    PHASE2_CLOSURE_VALIDATE_REL,
    TOOLCHAIN_CHECKER_REL,
    PINNING_CHECKER_REL,
    PIN_SCOPE_CHECKER_REL,
    KBUILD_CHECKER_REL,
    DOCS_REMINDER_CHECKER_REL,
    REQUIRED_ROUTES_CHECKER_REL,
    MAKEFILE_REL,
    MANIFEST_REL,
    ARTIFACT_MANIFEST_REL,
)

REQUIRED_CLOSURE_MARKERS = (
    "`scripts/zigux/validate-phase2.py`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`scripts/zigux/check-zig-toolchain.py`",
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/check-phase2-kbuild-routes.py`",
    "`scripts/zigux/check-phase2-docs-shared-reminder.py`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`zigux/Makefile`",
    "`zigux/tests/fixtures/phase2_tool_manifest.json`",
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
    "`python3 scripts/zigux/validate-phase2-closure.py --self-test`",
    "`python3 scripts/zigux/validate-phase2-closure.py`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
    "Restoring this validator closes one repo-reality gap inside the bounded Phase 2 closure packet",
    "The remaining current `master` repo-reality gaps are the installer and direct cross-route companions:",
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
)

FORBIDDEN_CLOSURE_MARKERS = (
    "`scripts/zigux/validate-phase2-closure.py`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase2-cross.py`, `zigux/tests/fixtures/phase2_cross_targets.json`",
    "Current `master` still does not directly materialize the older closure-validator companion, installer hook, and direct cross-route companions",
)

REQUIRED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py",
    "run: python3 scripts/zigux/validate-phase2.py",
)

REQUIRED_MAKEFILE_LINES = (
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
)

REQUIRED_MANIFEST_GAPS = (
    "scripts/zigux/install-zig.py",
    "scripts/zigux/check-phase2-cross.py",
    "zigux/tests/fixtures/phase2_cross_targets.json",
)

FORBIDDEN_MANIFEST_GAPS = ("scripts/zigux/validate-phase2-closure.py",)

EXPECTED_SELF_TEST_CASE_COUNT = (
    1
    + len(REQUIRED_CLOSURE_MARKERS)
    + len(FORBIDDEN_CLOSURE_MARKERS)
    + len(REQUIRED_WORKFLOW_LINES)
    + len(REQUIRED_WORKFLOW_LINES)
    + len(REQUIRED_MAKEFILE_LINES)
    + len(REQUIRED_MANIFEST_GAPS)
    + len(FORBIDDEN_MANIFEST_GAPS)
    + 4
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


def read_json(path: Path) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for rel in REQUIRED_FILES:
        if not resolve(root, rel).exists():
            issues.append(("MISSING_REQUIRED_FILE", rel.as_posix()))

    if issues:
        return issues

    workflow_text = read_text(resolve(root, WORKFLOW_REL))
    closure_text = read_text(resolve(root, PHASE2_CLOSURE_REL))
    makefile_text = read_text(resolve(root, MAKEFILE_REL))
    manifest = read_json(resolve(root, MANIFEST_REL))
    if not isinstance(manifest, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "root"))
        return issues

    manifest_gaps = manifest.get("repo_reality_gaps")
    if not isinstance(manifest_gaps, list):
        issues.append(("INVALID_MANIFEST_SHAPE", "repo_reality_gaps"))
        return issues

    for marker in REQUIRED_CLOSURE_MARKERS:
        if marker not in closure_text:
            issues.append(("MISSING_CLOSURE_MARKER", marker))

    for marker in FORBIDDEN_CLOSURE_MARKERS:
        if marker in closure_text:
            issues.append(("FORBIDDEN_CLOSURE_MARKER", marker))

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

    for marker in REQUIRED_MANIFEST_GAPS:
        if marker not in manifest_gaps:
            issues.append(("MISSING_MANIFEST_GAP", marker))

    for marker in FORBIDDEN_MANIFEST_GAPS:
        if marker in manifest_gaps:
            issues.append(("FORBIDDEN_MANIFEST_GAP", marker))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_CLOSURE_VALIDATION=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    closure_text = """# Phase 2 Closure

## Status

- `PHASE2_STATUS=parked`
- `PHASE2_CLOSURE_RESTORE_STATE=docs_plus_manifest`

## Current Closure Packet

- `Documentation/zigux/phase2-closure.md`
- `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`
- `scripts/zigux/validate-phase2.py`
- `scripts/zigux/validate-phase2-closure.py`
- `scripts/zigux/check-zig-toolchain.py`
- `scripts/zigux/check-phase2-toolchain-pinning.py`
- `scripts/zigux/check-phase2-toolchain-pin-scope.py`
- `scripts/zigux/check-phase2-kbuild-routes.py`
- `scripts/zigux/check-phase2-docs-shared-reminder.py`
- `scripts/zigux/check-phase2-required-make-routes.py`
- `zigux/Makefile`
- `zigux/tests/fixtures/phase2_tool_manifest.json`
- `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`

Restoring this validator closes one repo-reality gap inside the bounded Phase 2 closure packet while keeping the current shipped toolchain, kbuild, and make-wrapper tranche explicit.

## Current Repo-Reality Gaps

The remaining current `master` repo-reality gaps are the installer and direct cross-route companions:

- `scripts/zigux/install-zig.py`
- `scripts/zigux/check-phase2-cross.py`
- `zigux/tests/fixtures/phase2_cross_targets.json`

## Closure Validation

- `python3 scripts/zigux/validate-phase2-closure.py --self-test`
- `python3 scripts/zigux/validate-phase2-closure.py`
- `make -C zigux phase2-validate`
- `make -C zigux phase2`
"""
    write_text(resolve(root, WORKFLOW_REL), "\n".join(("name: zigux-bootstrap", *REQUIRED_WORKFLOW_LINES)) + "\n")
    write_text(resolve(root, PHASE2_CLOSURE_REL), closure_text)
    write_text(resolve(root, PHASE2_BOOTSTRAP_NOTES_REL), "present\n")
    write_text(resolve(root, PHASE2_VALIDATE_REL), "present\n")
    write_text(resolve(root, PHASE2_CLOSURE_VALIDATE_REL), "present\n")
    write_text(resolve(root, TOOLCHAIN_CHECKER_REL), "present\n")
    write_text(resolve(root, PINNING_CHECKER_REL), "present\n")
    write_text(resolve(root, PIN_SCOPE_CHECKER_REL), "present\n")
    write_text(resolve(root, KBUILD_CHECKER_REL), "present\n")
    write_text(resolve(root, DOCS_REMINDER_CHECKER_REL), "present\n")
    write_text(resolve(root, REQUIRED_ROUTES_CHECKER_REL), "present\n")
    write_text(
        resolve(root, MANIFEST_REL),
        json.dumps(
            {
                "phase": "Phase 2",
                "repo_reality_gaps": list(REQUIRED_MANIFEST_GAPS),
            },
            indent=2,
        )
        + "\n",
    )
    write_text(resolve(root, ARTIFACT_MANIFEST_REL), "{}\n")
    write_text(
        resolve(root, MAKEFILE_REL),
        "\n".join(
            (
                "PYTHON ?= python3",
                "PHASE2_SCRIPT_ROOT := ../scripts/zigux",
                "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross",
                "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py",
                "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
                "phase2: phase2-validate",
            )
        )
        + "\n",
    )


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


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_closure_validate_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in REQUIRED_CLOSURE_MARKERS:
            build_self_test_root(root)
            path = resolve(root, PHASE2_CLOSURE_REL)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_CLOSURE_MARKER", marker) in issues
            checks_run += 1

        for marker in FORBIDDEN_CLOSURE_MARKERS:
            build_self_test_root(root)
            path = resolve(root, PHASE2_CLOSURE_REL)
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            issues = collect_issues(root)
            assert ("FORBIDDEN_CLOSURE_MARKER", marker) in issues
            checks_run += 1

        for marker in REQUIRED_WORKFLOW_LINES:
            build_self_test_root(root)
            path = resolve(root, WORKFLOW_REL)
            path.write_text(
                replace_exact_line(path.read_text(encoding="utf-8"), marker, "run: python3 scripts/zigux/other.py"),
                encoding="utf-8",
            )
            issues = collect_issues(root)
            assert ("MISSING_WORKFLOW_LINE", marker) in issues
            checks_run += 1

        for marker in REQUIRED_WORKFLOW_LINES:
            build_self_test_root(root)
            path = resolve(root, WORKFLOW_REL)
            path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("DUPLICATE_WORKFLOW_LINE", f"{marker}:count=2") in issues
            checks_run += 1

        for marker in REQUIRED_MAKEFILE_LINES:
            build_self_test_root(root)
            path = resolve(root, MAKEFILE_REL)
            path.write_text(
                replace_exact_line(path.read_text(encoding="utf-8"), marker, "\t# removed"),
                encoding="utf-8",
            )
            issues = collect_issues(root)
            assert ("MISSING_MAKEFILE_LINE", marker) in issues
            checks_run += 1

        for marker in REQUIRED_MANIFEST_GAPS:
            build_self_test_root(root)
            path = resolve(root, MANIFEST_REL)
            manifest = read_json(path)
            assert isinstance(manifest, dict)
            manifest["repo_reality_gaps"] = [value for value in manifest["repo_reality_gaps"] if value != marker]
            write_text(path, json.dumps(manifest, indent=2) + "\n")
            issues = collect_issues(root)
            assert ("MISSING_MANIFEST_GAP", marker) in issues
            checks_run += 1

        for marker in FORBIDDEN_MANIFEST_GAPS:
            build_self_test_root(root)
            path = resolve(root, MANIFEST_REL)
            manifest = read_json(path)
            assert isinstance(manifest, dict)
            manifest["repo_reality_gaps"].append(marker)
            write_text(path, json.dumps(manifest, indent=2) + "\n")
            issues = collect_issues(root)
            assert ("FORBIDDEN_MANIFEST_GAP", marker) in issues
            checks_run += 1

        build_self_test_root(root)
        path = resolve(root, MANIFEST_REL)
        write_text(path, "{not-json}\n")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid json in required file" in str(exc)
            assert str(path) in str(exc)
        else:
            raise AssertionError("invalid manifest json did not abort")
        checks_run += 1

        for rel in (PHASE2_CLOSURE_REL, WORKFLOW_REL, MAKEFILE_REL):
            build_self_test_root(root)
            resolve(root, rel).unlink()
            issues = collect_issues(root)
            assert ("MISSING_REQUIRED_FILE", rel.as_posix()) in issues
            checks_run += 1

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_CLOSURE_VALIDATION_SELF_TEST=pass")
    print(f"PHASE2_CLOSURE_VALIDATION_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 2 closure note against the shipped closure packet."
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_CLOSURE_VALIDATION=pass")
    print("PHASE2_CLOSURE_STATUS=parked")
    print("PHASE2_CLOSURE_PACKET=closure_note_and_validator")
    print(
        "PHASE2_CLOSURE_REMAINING_GAPS="
        "scripts/zigux/install-zig.py,scripts/zigux/check-phase2-cross.py,zigux/tests/fixtures/phase2_cross_targets.json"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())