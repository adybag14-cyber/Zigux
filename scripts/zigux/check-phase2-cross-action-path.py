#!/usr/bin/env python3
"""Guard the current Phase 2 cross-route action path."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
ROOT = HERE.parents[3] if len(HERE.parents) > 3 else Path.cwd()

WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
DOCS_ROOT_README = Path("Documentation/zigux/README.md")
BOOTSTRAP_NOTES = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
REVIEW_CHECKLIST = Path("Documentation/zigux/review-checklist.md")
TESTS_README = Path("zigux/tests/README.md")
SCRIPTS_README = Path("scripts/zigux/README.md")
MAKEFILE = Path("zigux/Makefile")
CHECK_CROSS = Path("scripts/zigux/check-phase2-cross.py")
CHECK_CROSS_ALIGNMENT = Path("scripts/zigux/check-phase2-cross-selftest-alignment.py")
CROSS_FIXTURE = Path("zigux/tests/fixtures/phase2_cross_targets.json")

REQUIRED_FILES = (
    WORKFLOW,
    DOCS_ROOT_README,
    BOOTSTRAP_NOTES,
    REVIEW_CHECKLIST,
    TESTS_README,
    SCRIPTS_README,
    MAKEFILE,
    CHECK_CROSS,
    CHECK_CROSS_ALIGNMENT,
    CROSS_FIXTURE,
)

REQUIRED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase2-cross.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross.py",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "run: make -C zigux phase2-cross",
)

REQUIRED_MAKEFILE_LINES = (
    "phase2-cross:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
)

REQUIRED_DOCS_ROOT_MARKERS = (
    "`scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "`make -C zigux phase2-cross`",
)

REQUIRED_BOOTSTRAP_MARKERS = (
    "`scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross.py`",
    "`python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`make -C zigux phase2-cross`",
)

REQUIRED_REVIEW_MARKERS = (
    "`scripts/zigux/check-phase2-cross.py`",
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross.py`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "`make -C zigux phase2-cross`",
)

REQUIRED_TESTS_MARKERS = (
    "`scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "`make -C zigux phase2-cross`",
)

REQUIRED_SCRIPTS_MARKERS = (
    "`scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross.py`",
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


def exact_line_index(text: str, marker: str) -> int | None:
    for index, line in enumerate(text.splitlines()):
        if line.strip() == marker:
            return index
    return None


def replace_exact_line(text: str, marker: str, replacement: str = "") -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def collect_marker_issues(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for rel in REQUIRED_FILES:
        if not resolve(root, rel).exists():
            issues.append(("MISSING_REQUIRED_FILE", rel.as_posix()))
    if issues:
        return issues

    workflow_text = read_text(resolve(root, WORKFLOW))
    docs_root_text = read_text(resolve(root, DOCS_ROOT_README))
    bootstrap_text = read_text(resolve(root, BOOTSTRAP_NOTES))
    review_text = read_text(resolve(root, REVIEW_CHECKLIST))
    tests_text = read_text(resolve(root, TESTS_README))
    scripts_text = read_text(resolve(root, SCRIPTS_README))
    makefile_text = read_text(resolve(root, MAKEFILE))

    workflow_indices: list[int] = []
    for marker in REQUIRED_WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
            continue
        if count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))
            continue
        workflow_indices.append(exact_line_index(workflow_text, marker) or 0)
    if len(workflow_indices) == len(REQUIRED_WORKFLOW_LINES) and workflow_indices != sorted(workflow_indices):
        issues.append(("WORKFLOW_ORDER_MISMATCH", "phase2-cross-run-order"))

    makefile_indices: list[int] = []
    for marker in REQUIRED_MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
            continue
        if count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))
            continue
        makefile_indices.append(exact_line_index(makefile_text, marker) or 0)
    if len(makefile_indices) == len(REQUIRED_MAKEFILE_LINES) and makefile_indices != sorted(makefile_indices):
        issues.append(("MAKEFILE_ORDER_MISMATCH", "phase2-cross-run-order"))

    issues.extend(
        collect_marker_issues(docs_root_text, REQUIRED_DOCS_ROOT_MARKERS, "MISSING_DOCS_ROOT_MARKER")
    )
    issues.extend(
        collect_marker_issues(bootstrap_text, REQUIRED_BOOTSTRAP_MARKERS, "MISSING_BOOTSTRAP_MARKER")
    )
    issues.extend(
        collect_marker_issues(review_text, REQUIRED_REVIEW_MARKERS, "MISSING_REVIEW_MARKER")
    )
    issues.extend(collect_marker_issues(tests_text, REQUIRED_TESTS_MARKERS, "MISSING_TESTS_MARKER"))
    issues.extend(
        collect_marker_issues(scripts_text, REQUIRED_SCRIPTS_MARKERS, "MISSING_SCRIPTS_README_MARKER")
    )
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_CROSS_ACTION_PATH=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    write_text(resolve(root, WORKFLOW), "\n".join(REQUIRED_WORKFLOW_LINES) + "\n")
    write_text(resolve(root, DOCS_ROOT_README), "\n".join(REQUIRED_DOCS_ROOT_MARKERS) + "\n")
    write_text(resolve(root, BOOTSTRAP_NOTES), "\n".join(REQUIRED_BOOTSTRAP_MARKERS) + "\n")
    write_text(resolve(root, REVIEW_CHECKLIST), "\n".join(REQUIRED_REVIEW_MARKERS) + "\n")
    write_text(resolve(root, TESTS_README), "\n".join(REQUIRED_TESTS_MARKERS) + "\n")
    write_text(resolve(root, SCRIPTS_README), "\n".join(REQUIRED_SCRIPTS_MARKERS) + "\n")
    write_text(resolve(root, MAKEFILE), "\n".join(REQUIRED_MAKEFILE_LINES) + "\n")
    write_text(resolve(root, CHECK_CROSS), "present\n")
    write_text(resolve(root, CHECK_CROSS_ALIGNMENT), "present\n")
    write_text(resolve(root, CROSS_FIXTURE), "{\n  \"phase\": \"Phase 2\"\n}\n")


def run_self_test() -> int:
    expected_case_count = (
        1
        + len(REQUIRED_WORKFLOW_LINES)
        + len(REQUIRED_WORKFLOW_LINES)
        + 1
        + len(REQUIRED_MAKEFILE_LINES)
        + len(REQUIRED_MAKEFILE_LINES)
        + 1
        + len(REQUIRED_DOCS_ROOT_MARKERS)
        + len(REQUIRED_BOOTSTRAP_MARKERS)
        + len(REQUIRED_REVIEW_MARKERS)
        + len(REQUIRED_TESTS_MARKERS)
        + len(REQUIRED_SCRIPTS_MARKERS)
        + len(REQUIRED_FILES)
    )
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_action_path_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        for marker in REQUIRED_WORKFLOW_LINES:
            build_sample_root(root)
            workflow_path = resolve(root, WORKFLOW)
            workflow_path.write_text(
                replace_exact_line(workflow_path.read_text(encoding="utf-8"), marker, "run: python3 scripts/zigux/other.py"),
                encoding="utf-8",
            )
            assert ("MISSING_WORKFLOW_LINE", marker) in collect_issues(root)
            checks += 1

        for marker in REQUIRED_WORKFLOW_LINES:
            build_sample_root(root)
            workflow_path = resolve(root, WORKFLOW)
            workflow_path.write_text(
                workflow_path.read_text(encoding="utf-8").replace(marker, f"{marker}\n{marker}", 1),
                encoding="utf-8",
            )
            assert ("DUPLICATE_WORKFLOW_LINE", f"{marker}:count=2") in collect_issues(root)
            checks += 1

        build_sample_root(root)
        workflow_path = resolve(root, WORKFLOW)
        workflow_path.write_text("\n".join(reversed(REQUIRED_WORKFLOW_LINES)) + "\n", encoding="utf-8")
        assert ("WORKFLOW_ORDER_MISMATCH", "phase2-cross-run-order") in collect_issues(root)
        checks += 1

        for marker in REQUIRED_MAKEFILE_LINES:
            build_sample_root(root)
            makefile_path = resolve(root, MAKEFILE)
            makefile_path.write_text(
                replace_exact_line(makefile_path.read_text(encoding="utf-8"), marker, "# removed"),
                encoding="utf-8",
            )
            assert ("MISSING_MAKEFILE_LINE", marker) in collect_issues(root)
            checks += 1

        for marker in REQUIRED_MAKEFILE_LINES:
            build_sample_root(root)
            makefile_path = resolve(root, MAKEFILE)
            makefile_path.write_text(
                makefile_path.read_text(encoding="utf-8").replace(marker, f"{marker}\n{marker}", 1),
                encoding="utf-8",
            )
            assert ("DUPLICATE_MAKEFILE_LINE", f"{marker}:count=2") in collect_issues(root)
            checks += 1

        build_sample_root(root)
        makefile_path = resolve(root, MAKEFILE)
        makefile_path.write_text("\n".join(reversed(REQUIRED_MAKEFILE_LINES)) + "\n", encoding="utf-8")
        assert ("MAKEFILE_ORDER_MISMATCH", "phase2-cross-run-order") in collect_issues(root)
        checks += 1

        for marker in REQUIRED_DOCS_ROOT_MARKERS:
            build_sample_root(root)
            path = resolve(root, DOCS_ROOT_README)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_DOCS_ROOT_MARKER", marker) in collect_issues(root)
            checks += 1

        for marker in REQUIRED_BOOTSTRAP_MARKERS:
            build_sample_root(root)
            path = resolve(root, BOOTSTRAP_NOTES)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_BOOTSTRAP_MARKER", marker) in collect_issues(root)
            checks += 1

        for marker in REQUIRED_REVIEW_MARKERS:
            build_sample_root(root)
            path = resolve(root, REVIEW_CHECKLIST)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_REVIEW_MARKER", marker) in collect_issues(root)
            checks += 1

        for marker in REQUIRED_TESTS_MARKERS:
            build_sample_root(root)
            path = resolve(root, TESTS_README)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_TESTS_MARKER", marker) in collect_issues(root)
            checks += 1

        for marker in REQUIRED_SCRIPTS_MARKERS:
            build_sample_root(root)
            path = resolve(root, SCRIPTS_README)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_SCRIPTS_README_MARKER", marker) in collect_issues(root)
            checks += 1

        for rel in REQUIRED_FILES:
            build_sample_root(root)
            resolve(root, rel).unlink()
            assert ("MISSING_REQUIRED_FILE", rel.as_posix()) in collect_issues(root)
            checks += 1

    assert checks == expected_case_count, (checks, expected_case_count)
    print("PHASE2_CROSS_ACTION_PATH_SELF_TEST=pass")
    print(f"PHASE2_CROSS_ACTION_PATH_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in self-test cases")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    workflow_text = read_text(resolve(args.root, WORKFLOW))
    makefile_text = read_text(resolve(args.root, MAKEFILE))
    print("PHASE2_CROSS_ACTION_PATH=pass")
    print(
        "PHASE2_CROSS_ACTION_PATH_WORKFLOW_LINE_COUNT="
        f"{sum(count_exact_lines(workflow_text, marker) for marker in REQUIRED_WORKFLOW_LINES)}"
    )
    print(
        "PHASE2_CROSS_ACTION_PATH_MAKEFILE_LINE_COUNT="
        f"{sum(count_exact_lines(makefile_text, marker) for marker in REQUIRED_MAKEFILE_LINES)}"
    )
    print(f"PHASE2_CROSS_ACTION_PATH_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
