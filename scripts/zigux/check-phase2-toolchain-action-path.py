#!/usr/bin/env python3
"""Guard the current Phase 2 toolchain reminder action path."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
ROOT = HERE.parents[3] if len(HERE.parents) > 3 else Path.cwd()

WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
BOOTSTRAP_NOTES = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
SCRIPTS_README = Path("scripts/zigux/README.md")
REVIEW_CHECKLIST = Path("Documentation/zigux/review-checklist.md")
TESTS_README = Path("zigux/tests/README.md")
CHECK_ZIG_TOOLCHAIN = Path("scripts/zigux/check-zig-toolchain.py")
CHECK_TOOLCHAIN_PINNING = Path("scripts/zigux/check-phase2-toolchain-pinning.py")
CHECK_TOOLCHAIN_PIN_SCOPE = Path("scripts/zigux/check-phase2-toolchain-pin-scope.py")
INSTALL_ZIG = Path("scripts/zigux/install-zig.py")
CHECK_PHASE2_CROSS = Path("scripts/zigux/check-phase2-cross.py")
THIRD_PARTY_README = Path("third_party/README.md")
MAKEFILE = Path("zigux/Makefile")

REQUIRED_FILES = (
    WORKFLOW,
    BOOTSTRAP_NOTES,
    SCRIPTS_README,
    REVIEW_CHECKLIST,
    TESTS_README,
    CHECK_ZIG_TOOLCHAIN,
    CHECK_TOOLCHAIN_PINNING,
    CHECK_TOOLCHAIN_PIN_SCOPE,
    INSTALL_ZIG,
    CHECK_PHASE2_CROSS,
    THIRD_PARTY_README,
    MAKEFILE,
)

REQUIRED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "run: make -C zigux phase2-toolchain",
)

REQUIRED_SCRIPTS_README_MARKERS = (
    "`scripts/zigux/check-zig-toolchain.py`",
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`third_party/README.md`",
    "`make -C zigux phase2-toolchain`",
)

REQUIRED_BOOTSTRAP_MARKERS = (
    "`scripts/zigux/check-zig-toolchain.py`",
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`third_party/README.md`",
    "`.github/workflows/zigux-bootstrap.yml`",
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test`",
    "`python3 scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`",
    "`python3 scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`make -C zigux phase2-toolchain`",
)

REQUIRED_REVIEW_MARKERS = (
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
)

REQUIRED_TESTS_MARKERS = (
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`",
    "`python3 scripts/zigux/install-zig.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "`make -C zigux phase2-toolchain`",
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


def exact_line_index(text: str, marker: str) -> int | None:
    for index, line in enumerate(text.splitlines()):
        if line.strip() == marker:
            return index
    return None


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for rel in REQUIRED_FILES:
        if not resolve(root, rel).exists():
            issues.append(("MISSING_REQUIRED_FILE", rel.as_posix()))
    if issues:
        return issues

    workflow_text = read_text(resolve(root, WORKFLOW))
    bootstrap_text = read_text(resolve(root, BOOTSTRAP_NOTES))
    scripts_text = read_text(resolve(root, SCRIPTS_README))
    review_text = read_text(resolve(root, REVIEW_CHECKLIST))
    tests_text = read_text(resolve(root, TESTS_README))

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
    if len(workflow_indices) == len(REQUIRED_WORKFLOW_LINES) and workflow_indices != sorted(
        workflow_indices
    ):
        issues.append(("WORKFLOW_ORDER_MISMATCH", "phase2-toolchain-run-order"))

    for marker in REQUIRED_SCRIPTS_README_MARKERS:
        if marker not in scripts_text:
            issues.append(("MISSING_SCRIPTS_README_MARKER", marker))

    for marker in REQUIRED_BOOTSTRAP_MARKERS:
        if marker not in bootstrap_text:
            issues.append(("MISSING_BOOTSTRAP_MARKER", marker))

    for marker in REQUIRED_REVIEW_MARKERS:
        if marker not in review_text:
            issues.append(("MISSING_REVIEW_MARKER", marker))

    for marker in REQUIRED_TESTS_MARKERS:
        if marker not in tests_text:
            issues.append(("MISSING_TESTS_MARKER", marker))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_TOOLCHAIN_ACTION_PATH=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    write_text(resolve(root, WORKFLOW), "\n".join(REQUIRED_WORKFLOW_LINES) + "\n")
    write_text(resolve(root, BOOTSTRAP_NOTES), "\n".join(REQUIRED_BOOTSTRAP_MARKERS) + "\n")
    write_text(resolve(root, SCRIPTS_README), "\n".join(REQUIRED_SCRIPTS_README_MARKERS) + "\n")
    write_text(resolve(root, REVIEW_CHECKLIST), "\n".join(REQUIRED_REVIEW_MARKERS) + "\n")
    write_text(resolve(root, TESTS_README), "\n".join(REQUIRED_TESTS_MARKERS) + "\n")
    write_text(resolve(root, CHECK_ZIG_TOOLCHAIN), "present\n")
    write_text(resolve(root, CHECK_TOOLCHAIN_PINNING), "present\n")
    write_text(resolve(root, CHECK_TOOLCHAIN_PIN_SCOPE), "present\n")
    write_text(resolve(root, INSTALL_ZIG), "present\n")
    write_text(resolve(root, CHECK_PHASE2_CROSS), "present\n")
    write_text(resolve(root, THIRD_PARTY_README), "present\n")
    write_text(resolve(root, MAKEFILE), "present\n")


def run_self_test() -> int:
    expected_case_count = (
        1
        + len(REQUIRED_WORKFLOW_LINES)
        + len(REQUIRED_WORKFLOW_LINES)
        + 1
        + len(REQUIRED_SCRIPTS_README_MARKERS)
        + len(REQUIRED_BOOTSTRAP_MARKERS)
        + len(REQUIRED_REVIEW_MARKERS)
        + len(REQUIRED_TESTS_MARKERS)
        + len(REQUIRED_FILES)
    )
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_toolchain_action_path_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        for marker in REQUIRED_WORKFLOW_LINES:
            build_sample_root(root)
            workflow_path = resolve(root, WORKFLOW)
            workflow_path.write_text(
                replace_exact_line(
                    workflow_path.read_text(encoding="utf-8"),
                    marker,
                    "run: python3 scripts/zigux/other.py",
                ),
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
        assert ("WORKFLOW_ORDER_MISMATCH", "phase2-toolchain-run-order") in collect_issues(root)
        checks += 1

        for marker in REQUIRED_SCRIPTS_README_MARKERS:
            build_sample_root(root)
            readme_path = resolve(root, SCRIPTS_README)
            readme_path.write_text(
                replace_once(readme_path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert ("MISSING_SCRIPTS_README_MARKER", marker) in collect_issues(root)
            checks += 1

        for marker in REQUIRED_BOOTSTRAP_MARKERS:
            build_sample_root(root)
            notes_path = resolve(root, BOOTSTRAP_NOTES)
            notes_path.write_text(
                replace_once(notes_path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert ("MISSING_BOOTSTRAP_MARKER", marker) in collect_issues(root)
            checks += 1

        for marker in REQUIRED_REVIEW_MARKERS:
            build_sample_root(root)
            review_path = resolve(root, REVIEW_CHECKLIST)
            review_path.write_text(
                replace_once(review_path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert ("MISSING_REVIEW_MARKER", marker) in collect_issues(root)
            checks += 1

        for marker in REQUIRED_TESTS_MARKERS:
            build_sample_root(root)
            tests_path = resolve(root, TESTS_README)
            tests_path.write_text(
                replace_once(tests_path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert ("MISSING_TESTS_MARKER", marker) in collect_issues(root)
            checks += 1

        for rel in REQUIRED_FILES:
            build_sample_root(root)
            resolve(root, rel).unlink()
            assert ("MISSING_REQUIRED_FILE", rel.as_posix()) in collect_issues(root)
            checks += 1

    assert checks == expected_case_count, (checks, expected_case_count)
    print("PHASE2_TOOLCHAIN_ACTION_PATH_SELF_TEST=pass")
    print(f"PHASE2_TOOLCHAIN_ACTION_PATH_SELF_TEST_CASE_COUNT={checks}")
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
    scripts_text = read_text(resolve(args.root, SCRIPTS_README))
    bootstrap_text = read_text(resolve(args.root, BOOTSTRAP_NOTES))
    print("PHASE2_TOOLCHAIN_ACTION_PATH=pass")
    print(
        "PHASE2_TOOLCHAIN_ACTION_PATH_WORKFLOW_LINE_COUNT="
        f"{sum(count_exact_lines(workflow_text, marker) for marker in REQUIRED_WORKFLOW_LINES)}"
    )
    print(
        "PHASE2_TOOLCHAIN_ACTION_PATH_SCRIPTS_MARKER_COUNT="
        f"{sum(1 for marker in REQUIRED_SCRIPTS_README_MARKERS if marker in scripts_text)}"
    )
    print(
        "PHASE2_TOOLCHAIN_ACTION_PATH_BOOTSTRAP_MARKER_COUNT="
        f"{sum(1 for marker in REQUIRED_BOOTSTRAP_MARKERS if marker in bootstrap_text)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
