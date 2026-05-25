#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()

SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
DOCS_README = ROOT / "Documentation" / "zigux" / "README.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
PHASE2_CLOSURE = ROOT / "Documentation" / "zigux" / "phase2-closure.md"
MAKEFILE = ROOT / "zigux" / "Makefile"
PHASE2_TOOL_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json"

REQUIRED_SCRIPTS_README_MARKERS = (
    "## Phase 2",
    "the current scripts-root bridge packet stays reviewable through the live toolchain checker, installer helper, direct cross-route packet",
    "`scripts/zigux/check-phase2-kbuild-routes.py`",
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/check-phase2-docs-shared-reminder.py`",
    "`scripts/zigux/check-phase2-tests-readme-alignment.py`",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `zigux/Makefile`",
    "`scripts/zigux/check-phase2-tool-manifest.py` and `zigux/tests/fixtures/phase2_tool_manifest.json` keep the fixture-backed current Phase 2 tool packet explicit from the scripts root beside the closure-side validator packet and the surviving alignment guards",
    "`scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master`",
    "keep those installer, tool-manifest, artifact-support, direct cross-route, genksyms bridge, and fixdep surfaces explicit beside the shipped toolchain and kbuild reminder packet",
)

EXACT_COUNT_SCRIPTS_README_MARKERS = (
    "`scripts/zigux/check-phase2-tool-manifest.py` and `zigux/tests/fixtures/phase2_tool_manifest.json` keep the fixture-backed current Phase 2 tool packet explicit from the scripts root beside the closure-side validator packet and the surviving alignment guards",
    "keep those installer, tool-manifest, artifact-support, direct cross-route, genksyms bridge, and fixdep surfaces explicit beside the shipped toolchain and kbuild reminder packet",
)

FORBIDDEN_SCRIPTS_README_MARKERS = (
    "repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`",
    "`zigux/Makefile`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-validate`, and `make -C zigux phase2` stay framed as repo-reality gaps",
)

REQUIRED_DOCS_README_MARKERS = (
    "Phase 2 notes",
    "`scripts/zigux/README.md`",
    "`scripts/zigux/validate-phase2.py`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`scripts/zigux/check-phase2-docs-shared-reminder.py`",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`scripts/zigux/fixdep.zig`",
)

REQUIRED_TESTS_README_MARKERS = (
    "## Phase 2 review packet",
    "`scripts/zigux/README.md`",
    "`scripts/zigux/validate-phase2.py`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`scripts/zigux/check-phase2-tests-readme-alignment.py`",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "the current directly readable Phase 2 packet is the scripts-root kbuild, installer, direct cross-route, cross-selftest, docs-shared-reminder, tool-manifest, artifact-tools-manifest, required-make-route, toolchain reminder, helper-local kconfig allconfig guard, kconfig bridge checker, the dedicated genksyms survey, selftest-alignment guard, bridge helper, and standalone version-side-effect proofs, fixdep governance and parity set plus the live kconfig bridge helpers, the restored closure-side note, validator entrypoint, closure validator, the shipped `zigux/Makefile` wrappers, and their fixture roster",
)

REQUIRED_CLOSURE_MARKERS = (
    "`scripts/zigux/README.md`",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`scripts/zigux/validate-phase2.py`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`zigux/Makefile`",
    "`zigux/tests/fixtures/phase2_tool_manifest.json`",
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-kconfig`",
    "`make -C zigux phase2-cross`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
)

REQUIRED_MAKEFILE_LINES = (
    "phase2-toolchain:",
    "phase2-tools:",
    "phase2-kconfig: phase2-toolchain",
    "phase2-cross:",
    "phase2-genksyms: phase2-toolchain",
    "phase2-fixdep: phase2-toolchain",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "phase2: phase2-validate",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kbuild-routes.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-docs-shared-reminder.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-artifact-tools-manifest.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
)

REQUIRED_MANIFEST_SURFACES = (
    "scripts/zigux/check-phase2-tests-readme-alignment.py",
    "scripts/zigux/check-phase2-docs-shared-reminder.py",
    "scripts/zigux/check-phase2-tool-manifest.py",
    "scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "scripts/zigux/check-phase2-required-make-routes.py",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
    "scripts/zigux/install-zig.py",
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/validate-phase2-closure.py",
    "zigux/Makefile",
    "make -C zigux phase2-toolchain",
    "make -C zigux phase2-tools",
    "make -C zigux phase2-kconfig",
    "make -C zigux phase2-cross",
    "make -C zigux phase2-genksyms",
    "make -C zigux phase2-fixdep",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
    "zigux/tests/fixtures/phase2_tool_manifest.json",
    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
    "zigux/tests/fixtures/phase2_cross_targets.json",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def read_manifest(path: Path) -> dict[str, object]:
    try:
        payload = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"required json invalid: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"required json has invalid top-level shape: {path}")
    return payload


def resolve_path(root: Path, path: Path) -> Path:
    try:
        rel = path.relative_to(ROOT)
    except ValueError:
        rel = path
    return root / rel


def collect_manifest_strings(value: object) -> set[str]:
    if isinstance(value, str):
        return {value}
    if isinstance(value, list):
        strings: set[str] = set()
        for item in value:
            strings.update(collect_manifest_strings(item))
        return strings
    if isinstance(value, dict):
        strings: set[str] = set()
        for item in value.values():
            strings.update(collect_manifest_strings(item))
        return strings
    return set()


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_forbidden_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker in text]


def collect_exact_count_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = text.count(marker)
        if count != 1:
            issues.append((code, f"{count}::{marker}"))
    return issues


def collect_manifest_surface_issues(strings: set[str]) -> list[tuple[str, str]]:
    return [("MISSING_MANIFEST_SURFACE", surface) for surface in REQUIRED_MANIFEST_SURFACES if surface not in strings]


def collect_makefile_line_issues(text: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in REQUIRED_MAKEFILE_LINES:
        count = sum(1 for line in text.splitlines() if line.strip() == marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{count}::{marker}"))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    scripts_readme_text = read_text(resolve_path(root, SCRIPTS_README))
    docs_readme_text = read_text(resolve_path(root, DOCS_README))
    tests_readme_text = read_text(resolve_path(root, TESTS_README))
    closure_text = read_text(resolve_path(root, PHASE2_CLOSURE))
    makefile_text = read_text(resolve_path(root, MAKEFILE))
    manifest = read_manifest(resolve_path(root, PHASE2_TOOL_MANIFEST))
    manifest_strings = collect_manifest_strings(manifest)

    issues = collect_missing_markers(
        scripts_readme_text,
        REQUIRED_SCRIPTS_README_MARKERS,
        "MISSING_SCRIPTS_README_MARKER",
    )
    issues.extend(
        collect_exact_count_markers(
            scripts_readme_text,
            EXACT_COUNT_SCRIPTS_README_MARKERS,
            "EXACT_COUNT_SCRIPTS_README_MARKER",
        )
    )
    issues.extend(
        collect_forbidden_markers(
            scripts_readme_text,
            FORBIDDEN_SCRIPTS_README_MARKERS,
            "FORBIDDEN_SCRIPTS_README_MARKER",
        )
    )
    issues.extend(collect_missing_markers(docs_readme_text, REQUIRED_DOCS_README_MARKERS, "MISSING_DOCS_README_MARKER"))
    issues.extend(collect_missing_markers(tests_readme_text, REQUIRED_TESTS_README_MARKERS, "MISSING_TESTS_README_MARKER"))
    issues.extend(collect_missing_markers(closure_text, REQUIRED_CLOSURE_MARKERS, "MISSING_CLOSURE_MARKER"))
    issues.extend(collect_makefile_line_issues(makefile_text))
    issues.extend(collect_manifest_surface_issues(manifest_strings))
    if manifest.get("repo_reality_gaps") != []:
        issues.append(("NONEMPTY_MANIFEST_GAPS", json.dumps(manifest.get("repo_reality_gaps"), sort_keys=True)))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_SCRIPTS_README_ALIGNMENT=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_self_test_root(root: Path) -> None:
    write_text(resolve_path(root, SCRIPTS_README), "\n".join(REQUIRED_SCRIPTS_README_MARKERS) + "\n")
    write_text(resolve_path(root, DOCS_README), "\n".join(REQUIRED_DOCS_README_MARKERS) + "\n")
    write_text(resolve_path(root, TESTS_README), "\n".join(REQUIRED_TESTS_README_MARKERS) + "\n")
    write_text(resolve_path(root, PHASE2_CLOSURE), "\n".join(REQUIRED_CLOSURE_MARKERS) + "\n")
    write_text(
        resolve_path(root, MAKEFILE),
        "PYTHON ?= python3\nPHASE2_SCRIPT_ROOT := ../scripts/zigux\nZIGUX_ROOT := ..\n\n"
        + "\n".join(REQUIRED_MAKEFILE_LINES)
        + "\n",
    )
    write_text(
        resolve_path(root, PHASE2_TOOL_MANIFEST),
        json.dumps(
            {
                "phase": "Phase 2",
                "present_surfaces": {"all": list(REQUIRED_MANIFEST_SURFACES)},
                "repo_reality_gaps": [],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )


def remove_all(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, "")


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = (
        1
        + len(REQUIRED_SCRIPTS_README_MARKERS)
        + len(EXACT_COUNT_SCRIPTS_README_MARKERS)
        + len(FORBIDDEN_SCRIPTS_README_MARKERS)
        + len(REQUIRED_DOCS_README_MARKERS)
        + len(REQUIRED_TESTS_README_MARKERS)
        + len(REQUIRED_CLOSURE_MARKERS)
        + len(REQUIRED_MAKEFILE_LINES)
        + len(REQUIRED_MANIFEST_SURFACES)
        + 1
    )
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_scripts_readme_alignment_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        scripts_readme_path = resolve_path(root, SCRIPTS_README)
        scripts_readme_text = read_text(scripts_readme_path)
        for marker in REQUIRED_SCRIPTS_README_MARKERS:
            write_text(scripts_readme_path, remove_all(scripts_readme_text, marker))
            issues = collect_issues(root)
            assert ("MISSING_SCRIPTS_README_MARKER", marker) in issues, (marker, issues)
            build_self_test_root(root)
            scripts_readme_text = read_text(scripts_readme_path)
            checks_run += 1

        for marker in EXACT_COUNT_SCRIPTS_README_MARKERS:
            write_text(scripts_readme_path, scripts_readme_text + marker + "\n")
            issues = collect_issues(root)
            assert ("EXACT_COUNT_SCRIPTS_README_MARKER", f"2::{marker}") in issues, (marker, issues)
            build_self_test_root(root)
            scripts_readme_text = read_text(scripts_readme_path)
            checks_run += 1

        for marker in FORBIDDEN_SCRIPTS_README_MARKERS:
            write_text(scripts_readme_path, scripts_readme_text + marker + "\n")
            issues = collect_issues(root)
            assert ("FORBIDDEN_SCRIPTS_README_MARKER", marker) in issues, (marker, issues)
            build_self_test_root(root)
            scripts_readme_text = read_text(scripts_readme_path)
            checks_run += 1

        docs_readme_path = resolve_path(root, DOCS_README)
        docs_readme_text = read_text(docs_readme_path)
        for marker in REQUIRED_DOCS_README_MARKERS:
            write_text(docs_readme_path, remove_all(docs_readme_text, marker))
            issues = collect_issues(root)
            assert ("MISSING_DOCS_README_MARKER", marker) in issues, (marker, issues)
            build_self_test_root(root)
            docs_readme_text = read_text(docs_readme_path)
            checks_run += 1

        tests_readme_path = resolve_path(root, TESTS_README)
        tests_readme_text = read_text(tests_readme_path)
        for marker in REQUIRED_TESTS_README_MARKERS:
            write_text(tests_readme_path, remove_all(tests_readme_text, marker))
            issues = collect_issues(root)
            assert ("MISSING_TESTS_README_MARKER", marker) in issues, (marker, issues)
            build_self_test_root(root)
            tests_readme_text = read_text(tests_readme_path)
            checks_run += 1

        closure_path = resolve_path(root, PHASE2_CLOSURE)
        closure_text = read_text(closure_path)
        for marker in REQUIRED_CLOSURE_MARKERS:
            write_text(closure_path, remove_all(closure_text, marker))
            issues = collect_issues(root)
            assert ("MISSING_CLOSURE_MARKER", marker) in issues, (marker, issues)
            build_self_test_root(root)
            closure_text = read_text(closure_path)
            checks_run += 1

        makefile_path = resolve_path(root, MAKEFILE)
        makefile_text = read_text(makefile_path)
        for marker in REQUIRED_MAKEFILE_LINES:
            lines = [line for line in makefile_text.splitlines() if line.strip() != marker]
            write_text(makefile_path, "\n".join(lines) + "\n")
            issues = collect_issues(root)
            assert ("MISSING_MAKEFILE_LINE", marker) in issues, (marker, issues)
            build_self_test_root(root)
            makefile_text = read_text(makefile_path)
            checks_run += 1

        manifest_path = resolve_path(root, PHASE2_TOOL_MANIFEST)
        manifest = read_manifest(manifest_path)
        for marker in REQUIRED_MANIFEST_SURFACES:
            manifest["present_surfaces"]["all"] = [entry for entry in manifest["present_surfaces"]["all"] if entry != marker]
            write_text(manifest_path, json.dumps(manifest, indent=2, sort_keys=True) + "\n")
            issues = collect_issues(root)
            assert ("MISSING_MANIFEST_SURFACE", marker) in issues, (marker, issues)
            build_self_test_root(root)
            manifest = read_manifest(manifest_path)
            checks_run += 1

        manifest["repo_reality_gaps"] = ["gap"]
        write_text(manifest_path, json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        issues = collect_issues(root)
        assert ("NONEMPTY_MANIFEST_GAPS", json.dumps(["gap"])) in issues, issues
        checks_run += 1

        if checks_run != expected_case_count:
            raise AssertionError(f"self-test count drift: expected {expected_case_count}, got {checks_run}")

    print("PHASE2_SCRIPTS_README_ALIGNMENT=self-test-pass")
    print(f"PHASE2_SCRIPTS_README_ALIGNMENT_SELF_TEST_CASES={checks_run}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="Run built-in regression checks instead of repo validation")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_SCRIPTS_README_ALIGNMENT=pass")
    print(f"PHASE2_SCRIPTS_README_ALIGNMENT_MARKER_COUNT={len(REQUIRED_SCRIPTS_README_MARKERS)}")
    print(f"PHASE2_SCRIPTS_README_ALIGNMENT_EXACT_COUNT_MARKER_COUNT={len(EXACT_COUNT_SCRIPTS_README_MARKERS)}")
    print(f"PHASE2_SCRIPTS_README_ALIGNMENT_FORBIDDEN_MARKER_COUNT={len(FORBIDDEN_SCRIPTS_README_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
