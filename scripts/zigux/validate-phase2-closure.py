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
INSTALL_ZIG_REL = Path("scripts/zigux/install-zig.py")
TOOLCHAIN_CHECKER_REL = Path("scripts/zigux/check-zig-toolchain.py")
PINNING_CHECKER_REL = Path("scripts/zigux/check-phase2-toolchain-pinning.py")
PIN_SCOPE_CHECKER_REL = Path("scripts/zigux/check-phase2-toolchain-pin-scope.py")
KBUILD_CHECKER_REL = Path("scripts/zigux/check-phase2-kbuild-routes.py")
KCONFIG_ALIGNMENT_REL = Path("scripts/zigux/check-phase2-kconfig-selftest-alignment.py")
TESTS_ALIGNMENT_REL = Path("scripts/zigux/check-phase2-tests-readme-alignment.py")
CROSS_CHECKER_REL = Path("scripts/zigux/check-phase2-cross.py")
CROSS_ALIGNMENT_REL = Path("scripts/zigux/check-phase2-cross-selftest-alignment.py")
DOCS_REMINDER_CHECKER_REL = Path("scripts/zigux/check-phase2-docs-shared-reminder.py")
REQUIRED_ROUTES_CHECKER_REL = Path("scripts/zigux/check-phase2-required-make-routes.py")
TOOLCHAIN_POLICY_REL = Path("scripts/zigux/zig-toolchain-policy.json")
CONF_BRIDGE_REL = Path("scripts/zigux/kconfig/conf_bridge.zig")
CONFDATA_BRIDGE_REL = Path("scripts/zigux/kconfig/confdata_bridge.zig")
MAKEFILE_REL = Path("zigux/Makefile")
MANIFEST_REL = Path("zigux/tests/fixtures/phase2_tool_manifest.json")
ARTIFACT_MANIFEST_REL = Path("zigux/tests/fixtures/phase2_artifact_tools_manifest.json")
CROSS_FIXTURE_REL = Path("zigux/tests/fixtures/phase2_cross_targets.json")
CONF_MANIFEST_REL = Path("zigux/tests/fixtures/kconfig_bridge/conf_manifest.json")
CONFDATA_MANIFEST_REL = Path("zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json")
KCONFIG_CASES_REL = Path("zigux/tests/fixtures/kconfig_bridge/cases.json")

REQUIRED_FILES = (
    WORKFLOW_REL,
    PHASE2_CLOSURE_REL,
    PHASE2_BOOTSTRAP_NOTES_REL,
    PHASE2_VALIDATE_REL,
    PHASE2_CLOSURE_VALIDATE_REL,
    INSTALL_ZIG_REL,
    TOOLCHAIN_CHECKER_REL,
    PINNING_CHECKER_REL,
    PIN_SCOPE_CHECKER_REL,
    KBUILD_CHECKER_REL,
    KCONFIG_ALIGNMENT_REL,
    TESTS_ALIGNMENT_REL,
    CROSS_CHECKER_REL,
    CROSS_ALIGNMENT_REL,
    DOCS_REMINDER_CHECKER_REL,
    REQUIRED_ROUTES_CHECKER_REL,
    TOOLCHAIN_POLICY_REL,
    CONF_BRIDGE_REL,
    CONFDATA_BRIDGE_REL,
    MAKEFILE_REL,
    MANIFEST_REL,
    ARTIFACT_MANIFEST_REL,
    CROSS_FIXTURE_REL,
    CONF_MANIFEST_REL,
    CONFDATA_MANIFEST_REL,
    KCONFIG_CASES_REL,
)

REQUIRED_CLOSURE_MARKERS = (
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`scripts/zigux/check-phase2-docs-shared-reminder.py`",
    "`scripts/zigux/validate-phase2.py`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`zigux/tests/fixtures/phase2_tool_manifest.json`",
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "`python3 scripts/zigux/install-zig.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "`python3 scripts/zigux/check-phase2-required-make-routes.py --self-test`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-kconfig`",
    "`make -C zigux phase2-cross`",
    "`PHASE2_CURRENT_GAP_PACKET=`",
    "The older fixdep dual-implementation reminder surfaces are no longer part of the current closure-side authority on `master`;",
)

FORBIDDEN_CLOSURE_MARKERS = (
    "`Documentation/zigux/phase2-fixdep-next-step-note.md`",
    "`scripts/basic/fixdep.c`",
    "`scripts/zigux/fixdep.zig`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`zigux/tests/fixtures/fixdep/cases.json`",
    "The remaining current `master` repo-reality gaps are the installer and direct cross-route companions:",
)

REQUIRED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "run: python3 scripts/zigux/check-phase2-required-make-routes.py --self-test",
    "run: python3 scripts/zigux/check-phase2-required-make-routes.py",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "run: python3 scripts/zigux/check-phase2-docs-shared-reminder.py --self-test",
    "run: python3 scripts/zigux/check-phase2-docs-shared-reminder.py",
    "run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py",
    "run: python3 scripts/zigux/validate-phase2.py",
)

REQUIRED_MAKEFILE_LINES = (
    "phase2-toolchain:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py",
    "phase2-tools:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kbuild-routes.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-docs-shared-reminder.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py",
    "phase2-kconfig:",
    "phase2-cross:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
)

EXPECTED_MANIFEST_BOOTSTRAP_HELPERS = ("scripts/zigux/install-zig.py",)
EXPECTED_MANIFEST_CROSS_SUPPORT = (
    "scripts/zigux/check-phase2-cross.py",
    "zigux/tests/fixtures/phase2_cross_targets.json",
)
EXPECTED_MANIFEST_FIXTURE_ROSTER = (
    "zigux/tests/fixtures/kconfig_bridge/cases.json",
    "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json",
    "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json",
)
FORBIDDEN_MANIFEST_GAPS = (
    "scripts/zigux/install-zig.py",
    "scripts/zigux/check-phase2-cross.py",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "scripts/zigux/validate-phase2-closure.py",
)

EXPECTED_SELF_TEST_CASE_COUNT = (
    1
    + len(REQUIRED_CLOSURE_MARKERS)
    + len(FORBIDDEN_CLOSURE_MARKERS)
    + len(REQUIRED_WORKFLOW_LINES)
    + 1
    + len(REQUIRED_MAKEFILE_LINES)
    + 1
    + 1
    + 1
    + 1
    + 1
    + 3
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


def require_manifest_list(issues: list[tuple[str, str]], manifest: dict[str, object], key: str) -> list[str] | None:
    value = manifest.get("present_surfaces")
    if not isinstance(value, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "present_surfaces"))
        return None
    entry = value.get(key)
    if not isinstance(entry, list):
        issues.append(("INVALID_MANIFEST_SHAPE", key))
        return None
    normalized: list[str] = []
    for item in entry:
        if not isinstance(item, str):
            issues.append(("INVALID_MANIFEST_SHAPE", key))
            return None
        normalized.append(item)
    return normalized


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

    manifest_gaps = manifest.get("repo_reality_gaps")
    if not isinstance(manifest_gaps, list):
        issues.append(("INVALID_MANIFEST_SHAPE", "repo_reality_gaps"))
        return issues
    if manifest_gaps:
        issues.append(("UNEXPECTED_MANIFEST_GAPS", ",".join(str(value) for value in manifest_gaps)))
    for marker in FORBIDDEN_MANIFEST_GAPS:
        if marker in manifest_gaps:
            issues.append(("FORBIDDEN_MANIFEST_GAP", marker))

    bootstrap_helpers = require_manifest_list(issues, manifest, "bootstrap_helpers")
    cross_support = require_manifest_list(issues, manifest, "cross_route_support")
    fixture_roster = require_manifest_list(issues, manifest, "fixture_roster")
    make_wrappers = require_manifest_list(issues, manifest, "make_wrappers")

    if bootstrap_helpers is not None:
        for marker in EXPECTED_MANIFEST_BOOTSTRAP_HELPERS:
            if marker not in bootstrap_helpers:
                issues.append(("MISSING_MANIFEST_SURFACE", f"bootstrap_helpers:{marker}"))
    if cross_support is not None:
        for marker in EXPECTED_MANIFEST_CROSS_SUPPORT:
            if marker not in cross_support:
                issues.append(("MISSING_MANIFEST_SURFACE", f"cross_route_support:{marker}"))
    if fixture_roster is not None:
        for marker in EXPECTED_MANIFEST_FIXTURE_ROSTER:
            if marker not in fixture_roster:
                issues.append(("MISSING_MANIFEST_SURFACE", f"fixture_roster:{marker}"))
    if make_wrappers is not None:
        for marker in (
            "make -C zigux phase2-toolchain",
            "make -C zigux phase2-tools",
            "make -C zigux phase2-kconfig",
            "make -C zigux phase2-cross",
            "make -C zigux phase2-validate",
            "make -C zigux phase2",
        ):
            if marker not in make_wrappers:
                issues.append(("MISSING_MANIFEST_SURFACE", f"make_wrappers:{marker}"))

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
- manifest: `zigux/tests/fixtures/phase2_tool_manifest.json`

## Current Closure Packet

- `scripts/zigux/install-zig.py`
- `scripts/zigux/check-phase2-cross.py`
- `scripts/zigux/check-phase2-cross-selftest-alignment.py`
- `scripts/zigux/check-phase2-required-make-routes.py`
- `scripts/zigux/check-phase2-docs-shared-reminder.py`
- `scripts/zigux/validate-phase2.py`
- `scripts/zigux/validate-phase2-closure.py`
- `zigux/tests/fixtures/phase2_tool_manifest.json`
- `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`
- `zigux/tests/fixtures/phase2_cross_targets.json`

## Current Repo-Reality Gaps

The older fixdep dual-implementation reminder surfaces are no longer part of the current closure-side authority on `master`; closure follow-through should stay tied to the toolchain, cross-route, kconfig, make-wrapper, and validator packet that the repo still ships directly.

- `PHASE2_CURRENT_GAP_PACKET=`

## Closure Validation

- `python3 scripts/zigux/install-zig.py --self-test`
- `python3 scripts/zigux/check-phase2-cross.py --self-test`
- `python3 scripts/zigux/check-phase2-required-make-routes.py --self-test`
- `python3 scripts/zigux/validate-phase2-closure.py --self-test`
- `python3 scripts/zigux/validate-phase2-closure.py`
- `make -C zigux phase2-tools`
- `make -C zigux phase2-kconfig`
- `make -C zigux phase2-cross`
"""
    workflow_lines = ["name: zigux-bootstrap", *REQUIRED_WORKFLOW_LINES]
    makefile_lines = [
        "PYTHON ?= python3",
        "PHASE2_SCRIPT_ROOT := ../scripts/zigux",
        *REQUIRED_MAKEFILE_LINES,
    ]
    manifest = {
        "phase": "Phase 2",
        "repo_reality_gaps": [],
        "present_surfaces": {
            "bootstrap_helpers": list(EXPECTED_MANIFEST_BOOTSTRAP_HELPERS),
            "cross_route_support": list(EXPECTED_MANIFEST_CROSS_SUPPORT),
            "fixture_roster": list(EXPECTED_MANIFEST_FIXTURE_ROSTER),
            "make_wrappers": [
                "make -C zigux phase2-toolchain",
                "make -C zigux phase2-tools",
                "make -C zigux phase2-kconfig",
                "make -C zigux phase2-cross",
                "make -C zigux phase2-validate",
                "make -C zigux phase2",
            ],
        },
    }

    write_text(resolve(root, WORKFLOW_REL), "\n".join(workflow_lines) + "\n")
    write_text(resolve(root, PHASE2_CLOSURE_REL), closure_text)
    write_text(resolve(root, PHASE2_BOOTSTRAP_NOTES_REL), "present\n")
    write_text(resolve(root, PHASE2_VALIDATE_REL), "present\n")
    write_text(resolve(root, PHASE2_CLOSURE_VALIDATE_REL), "present\n")
    write_text(resolve(root, INSTALL_ZIG_REL), "present\n")
    write_text(resolve(root, TOOLCHAIN_CHECKER_REL), "present\n")
    write_text(resolve(root, PINNING_CHECKER_REL), "present\n")
    write_text(resolve(root, PIN_SCOPE_CHECKER_REL), "present\n")
    write_text(resolve(root, KBUILD_CHECKER_REL), "present\n")
    write_text(resolve(root, KCONFIG_ALIGNMENT_REL), "present\n")
    write_text(resolve(root, TESTS_ALIGNMENT_REL), "present\n")
    write_text(resolve(root, CROSS_CHECKER_REL), "present\n")
    write_text(resolve(root, CROSS_ALIGNMENT_REL), "present\n")
    write_text(resolve(root, DOCS_REMINDER_CHECKER_REL), "present\n")
    write_text(resolve(root, REQUIRED_ROUTES_CHECKER_REL), "present\n")
    write_text(resolve(root, TOOLCHAIN_POLICY_REL), "present\n")
    write_text(resolve(root, CONF_BRIDGE_REL), "present\n")
    write_text(resolve(root, CONFDATA_BRIDGE_REL), "present\n")
    write_text(resolve(root, MAKEFILE_REL), "\n".join(makefile_lines) + "\n")
    write_text(resolve(root, MANIFEST_REL), json.dumps(manifest, indent=2) + "\n")
    write_text(resolve(root, ARTIFACT_MANIFEST_REL), "{}\n")
    write_text(resolve(root, CROSS_FIXTURE_REL), "{}\n")
    write_text(resolve(root, CONF_MANIFEST_REL), "{}\n")
    write_text(resolve(root, CONFDATA_MANIFEST_REL), "{}\n")
    write_text(resolve(root, KCONFIG_CASES_REL), "[]\n")


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
            assert ("MISSING_CLOSURE_MARKER", marker) in collect_issues(root)
            checks_run += 1

        for marker in FORBIDDEN_CLOSURE_MARKERS:
            build_self_test_root(root)
            path = resolve(root, PHASE2_CLOSURE_REL)
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            assert ("FORBIDDEN_CLOSURE_MARKER", marker) in collect_issues(root)
            checks_run += 1

        for marker in REQUIRED_WORKFLOW_LINES:
            build_self_test_root(root)
            path = resolve(root, WORKFLOW_REL)
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), marker, "run: python3 scripts/zigux/other.py"), encoding="utf-8")
            assert ("MISSING_WORKFLOW_LINE", marker) in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        path = resolve(root, WORKFLOW_REL)
        path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), REQUIRED_WORKFLOW_LINES[0]), encoding="utf-8")
        assert ("DUPLICATE_WORKFLOW_LINE", f"{REQUIRED_WORKFLOW_LINES[0]}:count=2") in collect_issues(root)
        checks_run += 1

        for marker in REQUIRED_MAKEFILE_LINES:
            build_self_test_root(root)
            path = resolve(root, MAKEFILE_REL)
            replacement = "# removed" if not marker.startswith("$(PYTHON)") else "\t# removed"
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), marker, replacement), encoding="utf-8")
            assert ("MISSING_MAKEFILE_LINE", marker) in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        path = resolve(root, MAKEFILE_REL)
        path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), REQUIRED_MAKEFILE_LINES[0]), encoding="utf-8")
        assert ("DUPLICATE_MAKEFILE_LINE", f"{REQUIRED_MAKEFILE_LINES[0]}:count=2") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve(root, MANIFEST_REL)
        manifest = read_json(path)
        assert isinstance(manifest, dict)
        manifest["repo_reality_gaps"] = ["scripts/zigux/install-zig.py"]
        write_text(path, json.dumps(manifest, indent=2) + "\n")
        issues = collect_issues(root)
        assert ("UNEXPECTED_MANIFEST_GAPS", "scripts/zigux/install-zig.py") in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve(root, MANIFEST_REL)
        manifest = read_json(path)
        assert isinstance(manifest, dict)
        manifest["present_surfaces"]["bootstrap_helpers"] = []
        write_text(path, json.dumps(manifest, indent=2) + "\n")
        assert ("MISSING_MANIFEST_SURFACE", "bootstrap_helpers:scripts/zigux/install-zig.py") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve(root, MANIFEST_REL)
        manifest = read_json(path)
        assert isinstance(manifest, dict)
        manifest["present_surfaces"]["cross_route_support"] = ["scripts/zigux/check-phase2-cross.py"]
        write_text(path, json.dumps(manifest, indent=2) + "\n")
        assert ("MISSING_MANIFEST_SURFACE", "cross_route_support:zigux/tests/fixtures/phase2_cross_targets.json") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve(root, MANIFEST_REL)
        manifest = read_json(path)
        assert isinstance(manifest, dict)
        manifest["present_surfaces"]["fixture_roster"] = [
            "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json",
            "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json",
        ]
        write_text(path, json.dumps(manifest, indent=2) + "\n")
        assert ("MISSING_MANIFEST_SURFACE", "fixture_roster:zigux/tests/fixtures/kconfig_bridge/cases.json") in collect_issues(root)
        checks_run += 1

        for rel in (PHASE2_CLOSURE_REL, WORKFLOW_REL, MAKEFILE_REL):
            build_self_test_root(root)
            resolve(root, rel).unlink()
            assert ("MISSING_REQUIRED_FILE", rel.as_posix()) in collect_issues(root)
            checks_run += 1

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_CLOSURE_VALIDATION_SELF_TEST=pass")
    print(f"PHASE2_CLOSURE_VALIDATION_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the current Phase 2 closure note against the shipped closure packet.")
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
    print("PHASE2_CLOSURE_PACKET=toolchain_cross_kconfig_closure")
    print("PHASE2_CLOSURE_REMAINING_GAPS=")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
