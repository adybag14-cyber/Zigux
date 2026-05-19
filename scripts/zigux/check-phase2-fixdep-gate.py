#!/usr/bin/env python3
"""Check the current fixdep governance packet against live Phase 2 surfaces."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

FIXDEP_REL = Path("scripts/zigux/fixdep.zig")
PHASE2_CLOSURE_REL = Path("Documentation/zigux/phase2-closure.md")
ARTIFACT_DIFF_REL = Path("Documentation/zigux/artifact-diff.md")
TESTS_README_REL = Path("zigux/tests/README.md")
MAKEFILE_REL = Path("zigux/Makefile")
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")

REQUIRED_FILES = (
    FIXDEP_REL,
    PHASE2_CLOSURE_REL,
    ARTIFACT_DIFF_REL,
    TESTS_README_REL,
    MAKEFILE_REL,
    WORKFLOW_REL,
)

FIXDEP_REQUIRED_MARKERS = (
    'test "dep parsing returns NoTargets for comment-only depfiles"',
    'test "dep parsing keeps escaped spaces inside tokens"',
    'test "escaped hash dependency survives concatenated target comment path"',
    'test "escaped colon dependency survives concatenated target comment path"',
    'test "output write failure uses C-style wording"',
)

CLOSURE_REQUIRED_MARKERS = (
    "`Documentation/zigux/phase2-closure.md`",
    "`zigux/Makefile`",
    "`zigux/tests/README.md`",
    "fixture-backed artifact-diff packet",
)

ARTIFACT_REQUIRED_MARKERS = (
    "`zigux/tests/fixtures/fixdep/sample_expected.txt`",
    "`zigux/tests/fixtures/fixdep/sample_multi_target_expected.txt`",
    "`zigux/tests/fixtures/fixdep/sample_escaped_space_expected.txt`",
)

TESTS_README_REQUIRED_MARKERS = (
    "Phase 2 review packet",
    "`Documentation/zigux/phase2-closure.md`",
    "`zigux/Makefile`",
    "`make -C zigux phase2`",
)

FORBIDDEN_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "run: python3 scripts/zigux/check-phase2-fixdep-gate.py",
    "run: python3 scripts/zigux/check-fixdep-diff.py --self-test",
    "run: python3 scripts/zigux/check-fixdep-diff.py",
    "run: zig test scripts/zigux/fixdep.zig",
)

FORBIDDEN_MAKEFILE_LINES = (
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-fixdep-gate.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-fixdep-gate.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-fixdep-diff.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-fixdep-diff.py",
    "zig test scripts/zigux/fixdep.zig",
)

EXPECTED_SELF_TEST_CASE_COUNT = (
    1
    + len(FIXDEP_REQUIRED_MARKERS)
    + len(CLOSURE_REQUIRED_MARKERS)
    + len(ARTIFACT_REQUIRED_MARKERS)
    + len(TESTS_README_REQUIRED_MARKERS)
    + len(FORBIDDEN_WORKFLOW_LINES)
    + len(FORBIDDEN_MAKEFILE_LINES)
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


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_forbidden_exact_lines(
    text: str, markers: tuple[str, ...], code: str
) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = count_exact_lines(text, marker)
        if count != 0:
            issues.append((code, f"{marker}:count={count}"))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for rel in REQUIRED_FILES:
        if not resolve(root, rel).exists():
            issues.append(("MISSING_REQUIRED_FILE", rel.as_posix()))

    if issues:
        return issues

    fixdep_text = read_text(resolve(root, FIXDEP_REL))
    closure_text = read_text(resolve(root, PHASE2_CLOSURE_REL))
    artifact_text = read_text(resolve(root, ARTIFACT_DIFF_REL))
    tests_readme_text = read_text(resolve(root, TESTS_README_REL))
    makefile_text = read_text(resolve(root, MAKEFILE_REL))
    workflow_text = read_text(resolve(root, WORKFLOW_REL))

    issues.extend(collect_missing_markers(fixdep_text, FIXDEP_REQUIRED_MARKERS, "MISSING_FIXDEP_MARKER"))
    issues.extend(
        collect_missing_markers(closure_text, CLOSURE_REQUIRED_MARKERS, "MISSING_CLOSURE_MARKER")
    )
    issues.extend(
        collect_missing_markers(artifact_text, ARTIFACT_REQUIRED_MARKERS, "MISSING_ARTIFACT_MARKER")
    )
    issues.extend(
        collect_missing_markers(
            tests_readme_text, TESTS_README_REQUIRED_MARKERS, "MISSING_TESTS_README_MARKER"
        )
    )
    issues.extend(
        collect_forbidden_exact_lines(workflow_text, FORBIDDEN_WORKFLOW_LINES, "UNEXPECTED_WORKFLOW_LINE")
    )
    issues.extend(
        collect_forbidden_exact_lines(makefile_text, FORBIDDEN_MAKEFILE_LINES, "UNEXPECTED_MAKEFILE_LINE")
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


def append_line(text: str, line: str) -> str:
    return text + line + "\n"


def build_self_test_root(root: Path) -> None:
    write_text(
        resolve(root, FIXDEP_REL),
        "\n".join(
            (
                "test \"dep parsing returns NoTargets for comment-only depfiles\" {}",
                "test \"dep parsing keeps escaped spaces inside tokens\" {}",
                "test \"escaped hash dependency survives concatenated target comment path\" {}",
                "test \"escaped colon dependency survives concatenated target comment path\" {}",
                "test \"output write failure uses C-style wording\" {}",
            )
        )
        + "\n",
    )
    write_text(
        resolve(root, PHASE2_CLOSURE_REL),
        "\n".join(
            (
                "# Phase 2 Closure",
                "- `Documentation/zigux/phase2-closure.md`",
                "- `zigux/Makefile`",
                "- `zigux/tests/README.md`",
                "The bounded Phase 2 tranche remains the directly readable toolchain, kbuild-route, kconfig-bridge, required-make-route, validator-entrypoint, closure-validator, and fixture-backed artifact-diff packet already present on current `master`.",
            )
        )
        + "\n",
    )
    write_text(
        resolve(root, ARTIFACT_DIFF_REL),
        "\n".join(ARTIFACT_REQUIRED_MARKERS) + "\n",
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
            )
        )
        + "\n",
    )
    write_text(
        resolve(root, MAKEFILE_REL),
        "\n".join(
            (
                "PYTHON ?= python3",
                ".PHONY: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-validate phase2",
                "phase2: phase2-validate",
            )
        )
        + "\n",
    )
    write_text(
        resolve(root, WORKFLOW_REL),
        "\n".join(
            (
                "name: zigux-bootstrap",
                "jobs:",
                "  bootstrap:",
                "    steps:",
                "      - run: make -C zigux phase2",
            )
        )
        + "\n",
    )


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_fixdep_gate_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in FIXDEP_REQUIRED_MARKERS:
            build_self_test_root(root)
            path = resolve(root, FIXDEP_REL)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_FIXDEP_MARKER", marker) in collect_issues(root)
            checks_run += 1

        for marker in CLOSURE_REQUIRED_MARKERS:
            build_self_test_root(root)
            path = resolve(root, PHASE2_CLOSURE_REL)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_CLOSURE_MARKER", marker) in collect_issues(root)
            checks_run += 1

        for marker in ARTIFACT_REQUIRED_MARKERS:
            build_self_test_root(root)
            path = resolve(root, ARTIFACT_DIFF_REL)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_ARTIFACT_MARKER", marker) in collect_issues(root)
            checks_run += 1

        for marker in TESTS_README_REQUIRED_MARKERS:
            build_self_test_root(root)
            path = resolve(root, TESTS_README_REL)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_TESTS_README_MARKER", marker) in collect_issues(root)
            checks_run += 1

        for marker in FORBIDDEN_WORKFLOW_LINES:
            build_self_test_root(root)
            path = resolve(root, WORKFLOW_REL)
            path.write_text(append_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("UNEXPECTED_WORKFLOW_LINE", f"{marker}:count=1") in collect_issues(root)
            checks_run += 1

        for marker in FORBIDDEN_MAKEFILE_LINES:
            build_self_test_root(root)
            path = resolve(root, MAKEFILE_REL)
            path.write_text(append_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("UNEXPECTED_MAKEFILE_LINE", f"{marker}:count=1") in collect_issues(root)
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
    print(f"PHASE2_FIXDEP_GATE_HELPER_MARKER_COUNT={len(FIXDEP_REQUIRED_MARKERS)}")
    print(f"PHASE2_FIXDEP_GATE_FORBIDDEN_WORKFLOW_LINE_COUNT={len(FORBIDDEN_WORKFLOW_LINES)}")
    print(f"PHASE2_FIXDEP_GATE_FORBIDDEN_MAKEFILE_LINE_COUNT={len(FORBIDDEN_MAKEFILE_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())