#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


_SELF_PATH = Path(__file__).resolve()
ROOT = _SELF_PATH.parents[2] if len(_SELF_PATH.parents) > 2 else _SELF_PATH.parent
DOCS_ROOT_README = ROOT / "Documentation" / "zigux" / "README.md"
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"

WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py",
)

DOCS_ROOT_README_MARKERS = (
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`python3 scripts/zigux/install-zig.py --self-test`",
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
    "the docs-root Phase 2 summary should also keep the current bootstrap-versus-cross verification split explicit",
)

REVIEW_CHECKLIST_MARKERS = (
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "`zigux/tests/fixtures/phase2_tool_manifest.json`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-kconfig`",
    "`make -C zigux phase2-cross`",
    "`make -C zigux phase2`",
)

TESTS_README_MARKERS = (
    "`python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`",
    "`python3 scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/check-zig-toolchain.py`",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-kconfig`",
    "`make -C zigux phase2-cross`",
    "`make -C zigux phase2`",
    "historical packet members rather than direct tests-root evidence",
)

SCRIPTS_README_PRESENT_MARKERS = (
    "`scripts/zigux/check-phase2-kbuild-routes.py`",
    "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-tests-readme-alignment.py`",
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
)

SCRIPTS_README_WARNING_MARKERS = (
    "`scripts/zigux/check-zig-toolchain.py`",
    "`python3 scripts/zigux/install-zig.py --self-test`",
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross.py`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
    "historical packet members that need fresh re-materialization",
)

SCRIPTS_README_FORBIDDEN_MARKERS = (
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`",
    "`python3 scripts/zigux/check-phase2-toolchain-pin-scope.py`",
)

PRESENT_SURFACE_PATHS = (
    ROOT / "scripts" / "zigux" / "check-phase2-kbuild-routes.py",
    ROOT / "scripts" / "zigux" / "check-phase2-kconfig-selftest-alignment.py",
    ROOT / "scripts" / "zigux" / "check-phase2-tests-readme-alignment.py",
    ROOT / "scripts" / "zigux" / "check-phase2-toolchain-pinning.py",
)

ABSENT_SURFACE_PATHS = (
    ROOT / "Documentation" / "zigux" / "phase2-closure.md",
    ROOT / "scripts" / "zigux" / "install-zig.py",
    ROOT / "scripts" / "zigux" / "check-zig-toolchain.py",
    ROOT / "scripts" / "zigux" / "check-phase2-cross.py",
    ROOT / "scripts" / "zigux" / "validate-phase2.py",
    ROOT / "scripts" / "zigux" / "validate-phase2-closure.py",
    ROOT / "zigux" / "Makefile",
)

REQUIRED_FILES = (
    DOCS_ROOT_README,
    REVIEW_CHECKLIST,
    TESTS_README,
    SCRIPTS_README,
    WORKFLOW,
)

EXPECTED_SELF_TEST_CASE_COUNT = (
    1
    + len(WORKFLOW_LINES) * 2
    + len(DOCS_ROOT_README_MARKERS)
    + len(REVIEW_CHECKLIST_MARKERS)
    + len(TESTS_README_MARKERS)
    + len(SCRIPTS_README_PRESENT_MARKERS)
    + len(SCRIPTS_README_WARNING_MARKERS)
    + len(SCRIPTS_README_FORBIDDEN_MARKERS)
    + len(PRESENT_SURFACE_PATHS)
    + len(ABSENT_SURFACE_PATHS)
    + len(REQUIRED_FILES)
)


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def read_text(root: Path, path: Path) -> str:
    resolved = resolve_path(root, path)
    try:
        return resolved.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {resolved}") from exc


def write_text(root: Path, path: Path, content: str) -> None:
    resolved = resolve_path(root, path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(content, encoding="utf-8")


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_forbidden_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker in text]


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    workflow_text = read_text(root, WORKFLOW)
    docs_root_text = read_text(root, DOCS_ROOT_README)
    review_text = read_text(root, REVIEW_CHECKLIST)
    tests_text = read_text(root, TESTS_README)
    scripts_text = read_text(root, SCRIPTS_README)

    for marker in WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_HOOKS", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_HOOKS", f"{marker}:count={count}"))

    issues.extend(
        collect_missing_markers(
            docs_root_text,
            DOCS_ROOT_README_MARKERS,
            "MISSING_DOCS_ROOT_README_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            review_text,
            REVIEW_CHECKLIST_MARKERS,
            "MISSING_REVIEW_CHECKLIST_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            tests_text,
            TESTS_README_MARKERS,
            "MISSING_TESTS_README_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            scripts_text,
            SCRIPTS_README_PRESENT_MARKERS,
            "MISSING_SCRIPTS_README_PRESENT_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            scripts_text,
            SCRIPTS_README_WARNING_MARKERS,
            "MISSING_SCRIPTS_README_WARNING_MARKERS",
        )
    )
    issues.extend(
        collect_forbidden_markers(
            scripts_text,
            SCRIPTS_README_FORBIDDEN_MARKERS,
            "FORBIDDEN_SCRIPTS_README_MARKERS",
        )
    )

    for path in PRESENT_SURFACE_PATHS:
        if not resolve_path(root, path).exists():
            issues.append(("MISSING_PRESENT_SURFACE_PATHS", path.relative_to(ROOT).as_posix()))

    for path in ABSENT_SURFACE_PATHS:
        if resolve_path(root, path).exists():
            issues.append(("UNEXPECTED_REMATERIALIZED_SURFACE_PATHS", path.relative_to(ROOT).as_posix()))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_TOOLCHAIN_PIN_SCOPE=fail")
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


def build_self_test_root(root: Path) -> None:
    write_text(root, WORKFLOW, "\n".join(WORKFLOW_LINES) + "\n")
    write_text(root, DOCS_ROOT_README, "\n".join(DOCS_ROOT_README_MARKERS) + "\n")
    write_text(root, REVIEW_CHECKLIST, "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n")
    write_text(root, TESTS_README, "\n".join(TESTS_README_MARKERS) + "\n")
    scripts_lines = [
        "# scripts/zigux",
        "",
        "## Phase 2",
        "",
        *SCRIPTS_README_PRESENT_MARKERS,
        *SCRIPTS_README_WARNING_MARKERS,
    ]
    write_text(root, SCRIPTS_README, "\n".join(scripts_lines) + "\n")

    for path in PRESENT_SURFACE_PATHS:
        write_text(root, path, "# present\n")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_toolchain_pin_scope_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in WORKFLOW_LINES:
            build_self_test_root(root)
            path = resolve_path(root, WORKFLOW)
            path.write_text(
                replace_exact_line(path.read_text(encoding="utf-8"), marker, "run: python3 scripts/zigux/other.py"),
                encoding="utf-8",
            )
            assert ("MISSING_WORKFLOW_HOOKS", marker) in collect_issues(root)
            checks_run += 1

        for marker in WORKFLOW_LINES:
            build_self_test_root(root)
            path = resolve_path(root, WORKFLOW)
            path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("DUPLICATE_WORKFLOW_HOOKS", f"{marker}:count=2") in collect_issues(root)
            checks_run += 1

        for path, markers, code in (
            (DOCS_ROOT_README, DOCS_ROOT_README_MARKERS, "MISSING_DOCS_ROOT_README_MARKERS"),
            (REVIEW_CHECKLIST, REVIEW_CHECKLIST_MARKERS, "MISSING_REVIEW_CHECKLIST_MARKERS"),
            (TESTS_README, TESTS_README_MARKERS, "MISSING_TESTS_README_MARKERS"),
            (SCRIPTS_README, SCRIPTS_README_PRESENT_MARKERS, "MISSING_SCRIPTS_README_PRESENT_MARKERS"),
            (SCRIPTS_README, SCRIPTS_README_WARNING_MARKERS, "MISSING_SCRIPTS_README_WARNING_MARKERS"),
        ):
            for marker in markers:
                build_self_test_root(root)
                resolved = resolve_path(root, path)
                resolved.write_text(replace_once(resolved.read_text(encoding="utf-8"), marker), encoding="utf-8")
                assert (code, marker) in collect_issues(root)
                checks_run += 1

        for marker in SCRIPTS_README_FORBIDDEN_MARKERS:
            build_self_test_root(root)
            resolved = resolve_path(root, SCRIPTS_README)
            resolved.write_text(resolved.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            assert ("FORBIDDEN_SCRIPTS_README_MARKERS", marker) in collect_issues(root)
            checks_run += 1

        for path in PRESENT_SURFACE_PATHS:
            build_self_test_root(root)
            resolve_path(root, path).unlink()
            assert ("MISSING_PRESENT_SURFACE_PATHS", path.relative_to(ROOT).as_posix()) in collect_issues(root)
            checks_run += 1

        for path in ABSENT_SURFACE_PATHS:
            build_self_test_root(root)
            write_text(root, path, "# rematerialized\n")
            assert (
                "UNEXPECTED_REMATERIALIZED_SURFACE_PATHS",
                path.relative_to(ROOT).as_posix(),
            ) in collect_issues(root)
            checks_run += 1

        for path in REQUIRED_FILES:
            build_self_test_root(root)
            resolve_path(root, path).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                checks_run += 1
            else:
                raise AssertionError(f"missing file did not abort: {path}")

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST=pass")
    print(f"PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Keep the current Phase 2 toolchain pinning scope explicit across the live "
            "workflow, docs-root, review-checklist, tests-root, and scripts-root reminder surfaces."
        )
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_TOOLCHAIN_PIN_SCOPE=pass")
    print(f"PHASE2_TOOLCHAIN_PIN_SCOPE_WORKFLOW_HOOK_COUNT={len(WORKFLOW_LINES)}")
    print(f"PHASE2_TOOLCHAIN_PIN_SCOPE_PRESENT_PATH_COUNT={len(PRESENT_SURFACE_PATHS)}")
    print(f"PHASE2_TOOLCHAIN_PIN_SCOPE_ABSENT_PATH_COUNT={len(ABSENT_SURFACE_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
