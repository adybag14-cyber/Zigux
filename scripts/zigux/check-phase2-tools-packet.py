#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
MAKEFILE = ROOT / "zigux" / "Makefile"
DOCS_README = ROOT / "Documentation" / "zigux" / "README.md"
BOOTSTRAP_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json"

PHASE2_TOOLS_ROUTE = "make -C zigux phase2-tools"
PHASE2_TOOLS_ROUTE_MARKER = f"`{PHASE2_TOOLS_ROUTE}`"
PHASE2_TOOLS_WORKFLOW_LINE = f"run: {PHASE2_TOOLS_ROUTE}"

PHASE2_TOOLS_CHECKERS = (
    "scripts/zigux/check-phase2-kbuild-routes.py",
    "scripts/zigux/check-phase2-docs-shared-reminder.py",
    "scripts/zigux/check-phase2-required-make-routes.py",
    "scripts/zigux/check-phase2-artifact-tools-manifest.py",
)

WORKFLOW_LINES = tuple(
    f"run: python3 {checker}{suffix}"
    for checker in PHASE2_TOOLS_CHECKERS
    for suffix in (" --self-test", "")
) + (PHASE2_TOOLS_WORKFLOW_LINE,)

MAKEFILE_LINES = ("phase2-tools:",) + tuple(
    f"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/{Path(checker).name}" for checker in PHASE2_TOOLS_CHECKERS
)

SURFACE_MARKERS = {
    DOCS_README: (
        "scripts/zigux/check-phase2-required-make-routes.py",
        "scripts/zigux/check-phase2-artifact-tools-manifest.py",
        PHASE2_TOOLS_ROUTE_MARKER,
    ),
    BOOTSTRAP_NOTES: (
        "scripts/zigux/check-phase2-kbuild-routes.py --self-test",
        "scripts/zigux/check-phase2-docs-shared-reminder.py --self-test",
        "scripts/zigux/check-phase2-required-make-routes.py --self-test",
        "scripts/zigux/check-phase2-artifact-tools-manifest.py --self-test",
        PHASE2_TOOLS_ROUTE_MARKER,
    ),
    REVIEW_CHECKLIST: (
        "scripts/zigux/check-phase2-required-make-routes.py",
        "scripts/zigux/check-phase2-artifact-tools-manifest.py",
        PHASE2_TOOLS_ROUTE_MARKER,
    ),
    SCRIPTS_README: (
        "scripts/zigux/check-phase2-required-make-routes.py",
        "scripts/zigux/check-phase2-artifact-tools-manifest.py",
        PHASE2_TOOLS_ROUTE_MARKER,
    ),
    TESTS_README: (
        "scripts/zigux/check-phase2-required-make-routes.py",
        "scripts/zigux/check-phase2-artifact-tools-manifest.py",
        PHASE2_TOOLS_ROUTE_MARKER,
    ),
}

MANIFEST_REQUIRED_TOP_LEVEL = {
    "phase": "Phase 2",
    "status": "active",
}


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


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


def load_manifest(path: Path) -> dict:
    return json.loads(read_text(path))


def find_duplicate_strings(values: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for value in values:
        if value in seen and value not in duplicates:
            duplicates.append(value)
        seen.add(value)
    return duplicates


def collect_workflow_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    workflow_text = read_text(resolve_path(root, WORKFLOW))
    for line in WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, line)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", line))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{line}:count={count}"))
    return issues


def collect_makefile_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    makefile_text = read_text(resolve_path(root, MAKEFILE))
    for line in MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, line)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", line))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{line}:count={count}"))
    return issues


def collect_surface_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for path, markers in SURFACE_MARKERS.items():
        text = read_text(resolve_path(root, path))
        for marker in markers:
            if marker not in text:
                issues.append(("MISSING_SURFACE_MARKER", f"{path.as_posix()}::{marker}"))
    return issues


def collect_manifest_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    manifest = load_manifest(resolve_path(root, MANIFEST))
    for key, expected in MANIFEST_REQUIRED_TOP_LEVEL.items():
        if manifest.get(key) != expected:
            issues.append(("MANIFEST_TOP_LEVEL_MISMATCH", key))

    surfaces = manifest.get("present_surfaces")
    if not isinstance(surfaces, dict):
        issues.append(("MISSING_MANIFEST_SECTION", "present_surfaces"))
        return issues

    checkers = surfaces.get("checkers")
    if not isinstance(checkers, list):
        issues.append(("MISSING_MANIFEST_SECTION", "present_surfaces.checkers"))
    else:
        string_checkers = [entry for entry in checkers if isinstance(entry, str)]
        for duplicate in find_duplicate_strings(string_checkers):
            issues.append(("DUPLICATE_MANIFEST_CHECKER", duplicate))
        for checker in PHASE2_TOOLS_CHECKERS:
            if checker not in string_checkers:
                issues.append(("MISSING_MANIFEST_CHECKER", checker))

    wrappers = surfaces.get("make_wrappers")
    if not isinstance(wrappers, list):
        issues.append(("MISSING_MANIFEST_SECTION", "present_surfaces.make_wrappers"))
    else:
        string_wrappers = [entry for entry in wrappers if isinstance(entry, str)]
        for duplicate in find_duplicate_strings(string_wrappers):
            issues.append(("DUPLICATE_MANIFEST_WRAPPER", duplicate))
        if PHASE2_TOOLS_ROUTE not in string_wrappers:
            issues.append(("MISSING_MANIFEST_WRAPPER", PHASE2_TOOLS_ROUTE))

    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    issues.extend(collect_workflow_issues(root))
    issues.extend(collect_makefile_issues(root))
    issues.extend(collect_surface_issues(root))
    issues.extend(collect_manifest_issues(root))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    print("PHASE2_TOOLS_PACKET=fail")
    for code, value in issues:
        print(f"{code}:{value}")
    return 1


def build_self_test_manifest() -> dict:
    return {
        "phase": "Phase 2",
        "status": "active",
        "present_surfaces": {
            "checkers": list(PHASE2_TOOLS_CHECKERS),
            "make_wrappers": [PHASE2_TOOLS_ROUTE],
        },
    }


def build_self_test_root(root: Path) -> None:
    write_text(resolve_path(root, WORKFLOW), "\n".join(WORKFLOW_LINES) + "\n")
    write_text(resolve_path(root, MAKEFILE), "\n".join(MAKEFILE_LINES) + "\n")
    for path, markers in SURFACE_MARKERS.items():
        write_text(resolve_path(root, path), "\n".join(markers) + "\n")
    write_text(resolve_path(root, MANIFEST), json.dumps(build_self_test_manifest(), indent=2) + "\n")


def replace_exact_line(text: str, marker: str, replacement: str = "") -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"line not found: {marker}")


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"line not found: {marker}")


def replace_once(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, "", 1)


def run_self_test() -> int:
    expected_case_count = (
        1
        + len(WORKFLOW_LINES)
        + len(WORKFLOW_LINES)
        + len(MAKEFILE_LINES)
        + len(MAKEFILE_LINES)
        + sum(len(markers) for markers in SURFACE_MARKERS.values())
        + len(PHASE2_TOOLS_CHECKERS)
        + 1
        + 1
        + 1
    )
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_tools_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for line in WORKFLOW_LINES:
            build_self_test_root(root)
            path = resolve_path(root, WORKFLOW)
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), line), encoding="utf-8")
            assert ("MISSING_WORKFLOW_LINE", line) in collect_issues(root)
            checks_run += 1

        for line in WORKFLOW_LINES:
            build_self_test_root(root)
            path = resolve_path(root, WORKFLOW)
            path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), line), encoding="utf-8")
            assert ("DUPLICATE_WORKFLOW_LINE", f"{line}:count=2") in collect_issues(root)
            checks_run += 1

        for line in MAKEFILE_LINES:
            build_self_test_root(root)
            path = resolve_path(root, MAKEFILE)
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), line), encoding="utf-8")
            assert ("MISSING_MAKEFILE_LINE", line) in collect_issues(root)
            checks_run += 1

        for line in MAKEFILE_LINES:
            build_self_test_root(root)
            path = resolve_path(root, MAKEFILE)
            path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), line), encoding="utf-8")
            assert ("DUPLICATE_MAKEFILE_LINE", f"{line}:count=2") in collect_issues(root)
            checks_run += 1

        for surface_path, markers in SURFACE_MARKERS.items():
            for marker in markers:
                build_self_test_root(root)
                path = resolve_path(root, surface_path)
                path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
                assert ("MISSING_SURFACE_MARKER", f"{surface_path.as_posix()}::{marker}") in collect_issues(root)
                checks_run += 1

        for checker in PHASE2_TOOLS_CHECKERS:
            build_self_test_root(root)
            path = resolve_path(root, MANIFEST)
            manifest = json.loads(path.read_text(encoding="utf-8"))
            manifest["present_surfaces"]["checkers"].remove(checker)
            path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
            assert ("MISSING_MANIFEST_CHECKER", checker) in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, MANIFEST)
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["present_surfaces"]["make_wrappers"] = []
        path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        assert ("MISSING_MANIFEST_WRAPPER", PHASE2_TOOLS_ROUTE) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, MANIFEST)
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["present_surfaces"]["checkers"].append(PHASE2_TOOLS_CHECKERS[0])
        path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        assert ("DUPLICATE_MANIFEST_CHECKER", PHASE2_TOOLS_CHECKERS[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, MANIFEST)
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["phase"] = "broken"
        path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        assert ("MANIFEST_TOP_LEVEL_MISMATCH", "phase") in collect_issues(root)
        checks_run += 1

    assert checks_run == expected_case_count
    print("PHASE2_TOOLS_PACKET_SELF_TEST=pass")
    print(f"PHASE2_TOOLS_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the current Phase 2 tools packet aligned across workflow, Makefile, notes, and manifest surfaces."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run the built-in contract self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_TOOLS_PACKET=pass")
    print(f"PHASE2_TOOLS_PACKET_CHECKER_COUNT={len(PHASE2_TOOLS_CHECKERS)}")
    print(f"PHASE2_TOOLS_PACKET_SURFACE_COUNT={len(SURFACE_MARKERS) + 3}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
