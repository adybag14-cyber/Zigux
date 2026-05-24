#!/usr/bin/env python3
"""Guard the bootstrap-backed Phase 2 tool-manifest route packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
MAKEFILE = ROOT / "zigux" / "Makefile"
PHASE2_CLOSURE = ROOT / "Documentation" / "zigux" / "phase2-closure.md"
BOOTSTRAP_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"

SURFACE_PATHS = (
    ROOT / "scripts" / "zigux" / "check-phase2-tool-manifest.py",
    ROOT / "scripts" / "zigux" / "check-phase2-artifact-tools-manifest.py",
    ROOT / "scripts" / "zigux" / "check-phase2-kbuild-routes.py",
    ROOT / "scripts" / "zigux" / "check-phase2-required-make-routes.py",
    ROOT / "scripts" / "zigux" / "validate-phase2.py",
    ROOT / "scripts" / "zigux" / "validate-phase2-closure.py",
    ROOT / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json",
    ROOT / "zigux" / "tests" / "fixtures" / "phase2_artifact_tools_manifest.json",
    WORKFLOW,
    MAKEFILE,
    PHASE2_CLOSURE,
    BOOTSTRAP_NOTES,
    REVIEW_CHECKLIST,
    SCRIPTS_README,
    TESTS_README,
)

WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase2-tool-manifest.py --self-test",
    "run: python3 scripts/zigux/check-phase2-tool-manifest.py",
    "run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py --self-test",
    "run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "run: make -C zigux phase2-tools",
    "run: make -C zigux phase2-validate",
)

MAKEFILE_LINES = (
    "phase2-tools:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kbuild-routes.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-docs-shared-reminder.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-artifact-tools-manifest.py",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
)

TEXT_MARKERS = {
    PHASE2_CLOSURE: (
        "`scripts/zigux/check-phase2-tool-manifest.py`",
        "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
        "`make -C zigux phase2-tools`",
        "`make -C zigux phase2-validate`",
        "the shared tool-manifest packet stays present in the workflow and Linux-style make routes indirectly through `python3 scripts/zigux/validate-phase2.py`",
    ),
    BOOTSTRAP_NOTES: (
        "`scripts/zigux/check-phase2-tool-manifest.py`",
        "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
        "`make -C zigux phase2-tools`",
        "`make -C zigux phase2-validate`",
    ),
    REVIEW_CHECKLIST: (
        "`scripts/zigux/check-phase2-tool-manifest.py`",
        "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
        "`make -C zigux phase2-tools`",
        "`make -C zigux phase2-validate`",
    ),
    SCRIPTS_README: (
        "`scripts/zigux/check-phase2-tool-manifest.py`",
        "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
        "`make -C zigux phase2-tools`",
        "`make -C zigux phase2-validate`",
        "the shipped closure-side reminder, closure-validator, validator entrypoint, make-wrapper, and artifact-support packet explicit",
    ),
    TESTS_README: (
        "`scripts/zigux/check-phase2-tool-manifest.py`",
        "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
        "`make -C zigux phase2-tools`",
        "`make -C zigux phase2-validate`",
    ),
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


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    workflow_text = read_text(resolve_path(root, WORKFLOW))
    for marker in WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))

    makefile_text = read_text(resolve_path(root, MAKEFILE))
    for marker in MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))

    for path, markers in TEXT_MARKERS.items():
        text = read_text(resolve_path(root, path))
        for marker in markers:
            count = text.count(marker)
            if count == 0:
                issues.append(("MISSING_TEXT_MARKER", f"{path.relative_to(ROOT).as_posix()}:{marker}"))
            elif count != 1:
                issues.append(("DUPLICATE_TEXT_MARKER", f"{path.relative_to(ROOT).as_posix()}:{marker}:count={count}"))

    for path in SURFACE_PATHS:
        resolved = resolve_path(root, path)
        if not resolved.exists():
            issues.append(("MISSING_SURFACE_PATH", path.relative_to(ROOT).as_posix()))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    print("PHASE2_BOOTSTRAP_TOOL_MANIFEST_ROUTE_PACKET=fail")
    for code, value in issues:
        print(f"{code}:{value}")
    return 1


def build_self_test_root(root: Path) -> None:
    for path in SURFACE_PATHS:
        if path == WORKFLOW:
            write_text(resolve_path(root, path), "\n".join(WORKFLOW_LINES) + "\n")
        elif path == MAKEFILE:
            write_text(resolve_path(root, path), "\n".join(MAKEFILE_LINES) + "\n")
        elif path in TEXT_MARKERS:
            write_text(resolve_path(root, path), "\n".join(TEXT_MARKERS[path]) + "\n")
        elif path.suffix == ".json":
            write_text(resolve_path(root, path), "{}\n")
        else:
            write_text(resolve_path(root, path), "present\n")


def replace_exact_line(text: str, marker: str, replacement: str = "") -> str:
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
    expected_case_count = (
        1
        + len(WORKFLOW_LINES)
        + len(WORKFLOW_LINES)
        + len(MAKEFILE_LINES)
        + len(MAKEFILE_LINES)
        + sum(len(markers) for markers in TEXT_MARKERS.values())
        + len(SURFACE_PATHS)
        + 2
    )

    with tempfile.TemporaryDirectory(prefix="zigux_phase2_bootstrap_tool_manifest_route_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in WORKFLOW_LINES:
            build_self_test_root(root)
            path = resolve_path(root, WORKFLOW)
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_WORKFLOW_LINE", marker) in collect_issues(root)
            checks_run += 1

        for marker in WORKFLOW_LINES:
            build_self_test_root(root)
            path = resolve_path(root, WORKFLOW)
            path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("DUPLICATE_WORKFLOW_LINE", f"{marker}:count=2") in collect_issues(root)
            checks_run += 1

        for marker in MAKEFILE_LINES:
            build_self_test_root(root)
            path = resolve_path(root, MAKEFILE)
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_MAKEFILE_LINE", marker) in collect_issues(root)
            checks_run += 1

        for marker in MAKEFILE_LINES:
            build_self_test_root(root)
            path = resolve_path(root, MAKEFILE)
            path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("DUPLICATE_MAKEFILE_LINE", f"{marker}:count=2") in collect_issues(root)
            checks_run += 1

        for path, markers in TEXT_MARKERS.items():
            for marker in markers:
                build_self_test_root(root)
                resolved = resolve_path(root, path)
                resolved.write_text(resolved.read_text(encoding="utf-8").replace(marker, "", 1), encoding="utf-8")
                key = f"{path.relative_to(ROOT).as_posix()}:{marker}"
                assert ("MISSING_TEXT_MARKER", key) in collect_issues(root)
                checks_run += 1

        for path in SURFACE_PATHS:
            build_self_test_root(root)
            resolved = resolve_path(root, path)
            resolved.unlink()
            if path in (WORKFLOW, MAKEFILE) or path in TEXT_MARKERS:
                try:
                    collect_issues(root)
                except SystemExit as exc:
                    assert "required file missing" in str(exc)
                    checks_run += 1
                else:
                    raise AssertionError(f"missing required file did not abort: {path}")
            else:
                assert ("MISSING_SURFACE_PATH", path.relative_to(ROOT).as_posix()) in collect_issues(root)
                checks_run += 1

        build_self_test_root(root)
        try:
            collect_issues(root)
        except SystemExit:
            raise AssertionError("valid self-test root aborted unexpectedly")
        checks_run += 1

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

    assert checks_run == expected_case_count, (checks_run, expected_case_count)
    print("PHASE2_BOOTSTRAP_TOOL_MANIFEST_ROUTE_PACKET_SELF_TEST=pass")
    print(f"PHASE2_BOOTSTRAP_TOOL_MANIFEST_ROUTE_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a focused current-like root for manual replay validation",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if args.write_sample_root is not None:
        build_self_test_root(args.write_sample_root.resolve())
        print("PHASE2_BOOTSTRAP_TOOL_MANIFEST_ROUTE_PACKET_SAMPLE_ROOT=pass")
        print(f"PHASE2_BOOTSTRAP_TOOL_MANIFEST_ROUTE_PACKET_SAMPLE_ROOT_PATH={args.write_sample_root.resolve()}")
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_BOOTSTRAP_TOOL_MANIFEST_ROUTE_PACKET=pass")
    print(f"PHASE2_BOOTSTRAP_TOOL_MANIFEST_ROUTE_PACKET_SURFACE_COUNT={len(SURFACE_PATHS)}")
    print(f"PHASE2_BOOTSTRAP_TOOL_MANIFEST_ROUTE_PACKET_WORKFLOW_LINE_COUNT={len(WORKFLOW_LINES)}")
    print("PHASE2_BOOTSTRAP_TOOL_MANIFEST_ROUTE_PACKET_REQUIRED_ROUTES=phase2-tools,phase2-validate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
