#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


_SELF_PATH = Path(__file__).resolve()
ROOT = _SELF_PATH.parents[2] if len(_SELF_PATH.parents) >= 3 else _SELF_PATH.parent

REQUIRED_FILES = [
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase1-closure.md",
    "zigux/tests/README.md",
    "scripts/zigux/install-zig.py",
    "scripts/zigux/check-phase1-installer-review-surfaces.py",
]

EXACT_COUNT_MARKERS = {
    "Documentation/zigux/README.md": [
        (
            "docs_root_phase1_installer_companion_checks",
            "- `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` keep the closed host-side helper packet reviewable through the shared helper build entrypoint and the Linux-style replay route, while `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/README.md`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, `python3 scripts/zigux/install-zig.py --self-test`, and `python3 scripts/zigux/check-phase1-installer-review-surfaces.py --self-test` keep the closure, installer-backed workflow-viability replay, the dedicated installer-review alignment checker, bootstrap-workflow replay, and validator-first contract explicit from the docs root instead of leaving the Phase 1 packet split across scripts, tests, closure notes, and workflow wiring alone.",
            1,
        ),
    ],
    "Documentation/zigux/review-checklist.md": [
        (
            "review_checklist_phase1_installer_companion_checks",
            "  * if the change touches the closed Phase 1 host-tools packet, do `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase1-closure.md`, `scripts/zigux/README.md`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase1-installer-review-surfaces.py --self-test`, `zigux/tests/README.md`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_helper_manifest.json`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` still agree on the same closed helper tranche and validator-first replay path without widening Phase 1 beyond the bounded host-side helper packet?",
            1,
        ),
    ],
    "Documentation/zigux/phase1-closure.md": [
        (
            "phase1_closure_installer_selftest_gate",
            "- `python3 scripts/zigux/install-zig.py --self-test` stays reviewable as the bounded installer-viability replay for that in-repo download step",
            1,
        ),
    ],
    "zigux/tests/README.md": [
        (
            "tests_root_phase1_installer_companion_checks",
            "  * keep `python3 scripts/zigux/install-zig.py --self-test` and `python3 scripts/zigux/check-phase1-installer-review-surfaces.py --self-test` visible as focused companion checks for the closed Phase 1 installer-review surface without widening the counted tests-root packet line that `scripts/zigux/validate-phase1.py` currently enforces",
            1,
        ),
    ],
}

EXACT_LINE_COUNT_MARKERS = {
    "Documentation/zigux/phase1-closure.md": [
        (
            "phase1_closure_installer_companion_checks",
            "- `python3 scripts/zigux/install-zig.py --self-test`",
            1,
        ),
        (
            "phase1_closure_installer_reviewer_companion_checks",
            "- `python3 scripts/zigux/check-phase1-installer-review-surfaces.py --self-test`",
            1,
        ),
    ],
}


def collect_missing_files(root: Path) -> list[str]:
    return [rel for rel in REQUIRED_FILES if not (root / rel).exists()]


def collect_exact_count_issues(text: str, markers: list[tuple[str, str, int]]) -> list[str]:
    issues: list[str] = []
    for label, marker, expected_count in markers:
        actual_count = text.count(marker)
        if actual_count != expected_count:
            issues.append(f"{label}:expected={expected_count}:actual={actual_count}")
    return issues


def collect_exact_line_count_issues(text: str, markers: list[tuple[str, str, int]]) -> list[str]:
    line_counts: dict[str, int] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        line_counts[line] = line_counts.get(line, 0) + 1

    issues: list[str] = []
    for label, marker, expected_count in markers:
        actual_count = line_counts.get(marker, 0)
        if actual_count != expected_count:
            issues.append(f"{label}:expected={expected_count}:actual={actual_count}")
    return issues


def validate_root(root: Path) -> list[str]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return [f"missing_file:{path}" for path in missing_files]

    issues: list[str] = []
    for rel_path, markers in EXACT_COUNT_MARKERS.items():
        text = (root / rel_path).read_text(encoding="utf-8")
        issues.extend(collect_exact_count_issues(text, markers))
    for rel_path, markers in EXACT_LINE_COUNT_MARKERS.items():
        text = (root / rel_path).read_text(encoding="utf-8")
        issues.extend(collect_exact_line_count_issues(text, markers))
    return issues


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_self_test_root(root: Path) -> None:
    for rel_path in REQUIRED_FILES:
        write_text(root / rel_path, "// fixture\n")

    for rel_path, markers in EXACT_COUNT_MARKERS.items():
        write_text(
            root / rel_path,
            "\n".join(marker for _, marker, _ in markers) + "\n",
        )
    for rel_path, markers in EXACT_LINE_COUNT_MARKERS.items():
        existing = (root / rel_path).read_text(encoding="utf-8") if (root / rel_path).exists() else ""
        write_text(
            root / rel_path,
            existing + "\n".join(marker for _, marker, _ in markers) + "\n",
        )


def run_self_test() -> int:
    self_test_case_count = 0

    def expect_case(issues: list[str], *expected: str) -> None:
        nonlocal self_test_case_count
        for issue in expected:
            assert issue in issues
        self_test_case_count += 1

    with tempfile.TemporaryDirectory(prefix="phase1_installer_companion_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert validate_root(root) == []

        write_text(root / "Documentation/zigux/README.md", "")
        issues = validate_root(root)
        expect_case(issues, "docs_root_phase1_installer_companion_checks:expected=1:actual=0")

        build_self_test_root(root)
        docs_marker = EXACT_COUNT_MARKERS["Documentation/zigux/README.md"][0][1]
        write_text(root / "Documentation/zigux/README.md", f"{docs_marker}\n{docs_marker}\n")
        issues = validate_root(root)
        expect_case(issues, "docs_root_phase1_installer_companion_checks:expected=1:actual=2")

        build_self_test_root(root)
        write_text(root / "Documentation/zigux/review-checklist.md", "")
        issues = validate_root(root)
        expect_case(
            issues,
            "review_checklist_phase1_installer_companion_checks:expected=1:actual=0",
        )

        build_self_test_root(root)
        checklist_marker = EXACT_COUNT_MARKERS["Documentation/zigux/review-checklist.md"][0][1]
        write_text(
            root / "Documentation/zigux/review-checklist.md",
            f"{checklist_marker}\n{checklist_marker}\n",
        )
        issues = validate_root(root)
        expect_case(
            issues,
            "review_checklist_phase1_installer_companion_checks:expected=1:actual=2",
        )

        build_self_test_root(root)
        write_text(root / "Documentation/zigux/phase1-closure.md", "")
        issues = validate_root(root)
        expect_case(
            issues,
            "phase1_closure_installer_selftest_gate:expected=1:actual=0",
            "phase1_closure_installer_companion_checks:expected=1:actual=0",
            "phase1_closure_installer_reviewer_companion_checks:expected=1:actual=0",
        )

        build_self_test_root(root)
        closure_markers = EXACT_COUNT_MARKERS["Documentation/zigux/phase1-closure.md"]
        closure_line_markers = EXACT_LINE_COUNT_MARKERS["Documentation/zigux/phase1-closure.md"]
        write_text(
            root / "Documentation/zigux/phase1-closure.md",
            "\n".join(marker for _, marker, _ in closure_markers)
            + "\n"
            + "\n".join(marker for _, marker, _ in closure_line_markers)
            + "\n"
            + closure_line_markers[1][1]
            + "\n",
        )
        issues = validate_root(root)
        expect_case(
            issues,
            "phase1_closure_installer_reviewer_companion_checks:expected=1:actual=2",
        )

        build_self_test_root(root)
        write_text(root / "zigux/tests/README.md", "")
        issues = validate_root(root)
        expect_case(issues, "tests_root_phase1_installer_companion_checks:expected=1:actual=0")

        build_self_test_root(root)
        tests_marker = EXACT_COUNT_MARKERS["zigux/tests/README.md"][0][1]
        write_text(root / "zigux/tests/README.md", f"{tests_marker}\n{tests_marker}\n")
        issues = validate_root(root)
        expect_case(issues, "tests_root_phase1_installer_companion_checks:expected=1:actual=2")

        build_self_test_root(root)
        (root / "scripts/zigux/install-zig.py").unlink()
        issues = validate_root(root)
        expect_case(issues, "missing_file:scripts/zigux/install-zig.py")

        build_self_test_root(root)
        (root / "scripts/zigux/check-phase1-installer-review-surfaces.py").unlink()
        issues = validate_root(root)
        expect_case(issues, "missing_file:scripts/zigux/check-phase1-installer-review-surfaces.py")

    print("PHASE1_INSTALLER_COMPANION_CHECKS_SELF_TEST=pass")
    print(f"PHASE1_INSTALLER_COMPANION_CHECKS_SELF_TEST_CASE_COUNT={self_test_case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that Phase 1 installer companion self-test surfaces stay aligned."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in coverage without reading a repo checkout.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_root(ROOT)
    if issues:
        print("PHASE1_INSTALLER_COMPANION_CHECKS=fail")
        print("PHASE1_INSTALLER_COMPANION_CHECKS_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE1_INSTALLER_COMPANION_CHECKS_ISSUES_END")
        return 1

    print("PHASE1_INSTALLER_COMPANION_CHECKS=pass")
    print(
        "PHASE1_INSTALLER_COMPANION_CHECKS_MARKER_COUNT="
        f"{sum(len(markers) for markers in EXACT_COUNT_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
