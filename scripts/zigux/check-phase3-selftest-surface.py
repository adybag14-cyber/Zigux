#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from collections import Counter
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parents[2] if len(SCRIPT_PATH.parents) > 2 else SCRIPT_PATH.parent

REQUIRED_FILES = [
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase3-abi-slice.md",
    "scripts/zigux/README.md",
    "scripts/zigux/validate_phase3_selftest.py",
    "zigux/Makefile",
    "zigux/tests/README.md",
]

DOCS_ROOT_MARKERS = [
    "scripts/zigux/validate_phase3_selftest.py",
    "scripts/zigux/check-phase3-selftest-surface.py",
    "scripts/zigux/phase3_catalog.py --self-test",
    "make -C zigux phase3-selftest",
    "without duplicating the default `phase3-validate` route",
]

REVIEW_CHECKLIST_MARKERS = [
    "scripts/zigux/validate_phase3_selftest.py",
    "scripts/zigux/check-phase3-selftest-surface.py",
    "make -C zigux phase3-selftest",
    "manual-only support-script rerun",
    "without implying that `phase3-selftest` is part of the default `phase3-validate` route",
]

ABI_SLICE_MARKERS = [
    "python3 scripts/zigux/validate_phase3_selftest.py",
    "python3 scripts/zigux/check-phase3-selftest-surface.py",
    "python3 scripts/zigux/check-phase3-readme-tooling-inventory.py --self-test",
    "python3 scripts/zigux/phase3_catalog.py --self-test",
    "python3 scripts/zigux/phase3_check_lib.py --self-test",
    "python3 scripts/zigux/generate-phase3-check-wrappers.py --check",
    "python3 scripts/zigux/run-phase3-checks.py --self-test",
    "python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    "make -C zigux phase3-selftest",
    "focused support-script safety check only; `make -C zigux phase3-validate` already invokes the underlying helper self-tests, README tooling inventory checks, catalog sanity checks, wrapper drift checks, and shared runner self-checks directly.",
]

SCRIPTS_README_MARKERS = [
    "validate_phase3_selftest.py",
    "The live support packet inside that same validator-first route is `check-phase3-readme-tooling-inventory.py`",
    "phase3_catalog.py --self-test",
    "make -C zigux phase3-selftest",
    "manual or targeted safety check instead of duplicating the default validation route",
]

TESTS_README_MARKERS = [
    "scripts/zigux/validate_phase3_selftest.py",
    "scripts/zigux/phase3_catalog.py --self-test",
    "scripts/zigux/phase3_check_lib.py --self-test",
    "scripts/zigux/generate-phase3-check-wrappers.py --check",
    "scripts/zigux/run-phase3-checks.py --self-test",
    "make -C zigux phase3-selftest",
    "opt-in safety check that complements but does not duplicate `make -C zigux phase3-validate`",
]

MAKEFILE_MARKERS = [
    "PHONY += phase3-validate phase3-selftest phase3-abi phase3-interop phase3",
    "phase3-selftest:\n\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate_phase3_selftest.py",
    "phase3: phase3-validate phase3-abi phase3-interop",
]


def normalized_marker_lines(text: str) -> list[str]:
    lines: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("- "):
            line = line[2:].strip()
        if line.startswith("* "):
            line = line[2:].strip()
        if line.startswith("`") and line.endswith("`") and len(line) >= 2:
            line = line[1:-1]
        lines.append(line)
    return lines


def exact_marker_count(text: str, marker: str, *, normalized: bool) -> int:
    if "\n" not in marker:
        lines = normalized_marker_lines(text) if normalized else text.splitlines()
        return Counter(lines).get(marker, 0)

    haystack = normalized_marker_lines(text) if normalized else text.splitlines()
    needle = marker.splitlines()
    if normalized:
        needle = normalized_marker_lines(marker)

    count = 0
    width = len(needle)
    for index in range(0, len(haystack) - width + 1):
        if haystack[index : index + width] == needle:
            count += 1
    return count


def collect_marker_count_issues(text: str, markers: list[str], *, prefix: str, normalized: bool = True) -> list[str]:
    issues: list[str] = []
    for marker in markers:
        count = exact_marker_count(text, marker, normalized=normalized)
        if count == 0:
            issues.append(f"{prefix}:{marker}")
        elif count != 1:
            issues.append(f"duplicate_{prefix}_marker:{count}:{marker}")
    return issues


def validate_root(root: Path) -> list[str]:
    issues: list[str] = []

    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            issues.append(f"missing_file:{rel}")

    if issues:
        return issues

    docs_root = (root / "Documentation/zigux/README.md").read_text(encoding="utf-8")
    review = (root / "Documentation/zigux/review-checklist.md").read_text(encoding="utf-8")
    abi_slice = (root / "Documentation/zigux/phase3-abi-slice.md").read_text(encoding="utf-8")
    scripts_readme = (root / "scripts/zigux/README.md").read_text(encoding="utf-8")
    tests_readme = (root / "zigux/tests/README.md").read_text(encoding="utf-8")
    makefile = (root / "zigux/Makefile").read_text(encoding="utf-8")

    issues.extend(collect_marker_count_issues(docs_root, DOCS_ROOT_MARKERS, prefix="docs_root"))
    issues.extend(collect_marker_count_issues(review, REVIEW_CHECKLIST_MARKERS, prefix="review_checklist"))
    issues.extend(collect_marker_count_issues(abi_slice, ABI_SLICE_MARKERS, prefix="abi_slice"))
    issues.extend(collect_marker_count_issues(scripts_readme, SCRIPTS_README_MARKERS, prefix="scripts_readme"))
    issues.extend(collect_marker_count_issues(tests_readme, TESTS_README_MARKERS, prefix="tests_readme"))
    issues.extend(collect_marker_count_issues(makefile, MAKEFILE_MARKERS, prefix="makefile", normalized=False))
    return issues


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")



def build_self_test_root(root: Path) -> None:
    for rel in REQUIRED_FILES:
        write_text(root / rel, "")

    write_text(root / "Documentation/zigux/README.md", "\n".join(DOCS_ROOT_MARKERS) + "\n")
    write_text(root / "Documentation/zigux/review-checklist.md", "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n")
    write_text(root / "Documentation/zigux/phase3-abi-slice.md", "\n".join(ABI_SLICE_MARKERS) + "\n")
    write_text(root / "scripts/zigux/README.md", "\n".join(SCRIPTS_README_MARKERS) + "\n")
    write_text(root / "zigux/tests/README.md", "\n".join(TESTS_README_MARKERS) + "\n")
    write_text(root / "zigux/Makefile", "\n".join(MAKEFILE_MARKERS) + "\n")
    write_text(root / "scripts/zigux/validate_phase3_selftest.py", "present\n")



def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase3_selftest_surface_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)

        assert validate_root(root) == []

        write_text(root / "Documentation/zigux/README.md", "make -C zigux phase3-selftest\n")
        issues = validate_root(root)
        assert "docs_root:scripts/zigux/validate_phase3_selftest.py" in issues
        assert "docs_root:scripts/zigux/check-phase3-selftest-surface.py" in issues
        assert "docs_root:scripts/zigux/phase3_catalog.py --self-test" in issues
        assert "docs_root:without duplicating the default `phase3-validate` route" in issues

        build_self_test_root(root)
        write_text(
            root / "Documentation/zigux/README.md",
            "\n".join(DOCS_ROOT_MARKERS + [DOCS_ROOT_MARKERS[0]]) + "\n",
        )
        issues = validate_root(root)
        assert (
            "duplicate_docs_root_marker:2:scripts/zigux/validate_phase3_selftest.py"
            in issues
        )

        build_self_test_root(root)
        write_text(
            root / "Documentation/zigux/README.md",
            "this sentence mentions scripts/zigux/validate_phase3_selftest.py without making it a marker\n",
        )
        issues = validate_root(root)
        assert "docs_root:scripts/zigux/validate_phase3_selftest.py" in issues

        build_self_test_root(root)
        write_text(root / "Documentation/zigux/review-checklist.md", "scripts/zigux/validate_phase3_selftest.py\n")
        issues = validate_root(root)
        assert "review_checklist:scripts/zigux/check-phase3-selftest-surface.py" in issues
        assert "review_checklist:make -C zigux phase3-selftest" in issues

        build_self_test_root(root)
        write_text(
            root / "Documentation/zigux/review-checklist.md",
            "\n".join(REVIEW_CHECKLIST_MARKERS + [REVIEW_CHECKLIST_MARKERS[2]]) + "\n",
        )
        issues = validate_root(root)
        assert "duplicate_review_checklist_marker:2:make -C zigux phase3-selftest" in issues

        build_self_test_root(root)
        write_text(root / "Documentation/zigux/phase3-abi-slice.md", "python3 scripts/zigux/validate_phase3_selftest.py\n")
        issues = validate_root(root)
        assert "abi_slice:python3 scripts/zigux/check-phase3-selftest-surface.py" in issues
        assert "abi_slice:python3 scripts/zigux/phase3_catalog.py --self-test" in issues
        assert "abi_slice:python3 scripts/zigux/phase3_check_lib.py --self-test" in issues
        assert "abi_slice:python3 scripts/zigux/generate-phase3-check-wrappers.py --check" in issues
        assert "abi_slice:python3 scripts/zigux/run-phase3-checks.py --self-test" in issues
        assert "abi_slice:python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py" in issues
        assert "abi_slice:make -C zigux phase3-selftest" in issues

        build_self_test_root(root)
        write_text(
            root / "Documentation/zigux/phase3-abi-slice.md",
            "\n".join(ABI_SLICE_MARKERS + [ABI_SLICE_MARKERS[1]]) + "\n",
        )
        issues = validate_root(root)
        assert (
            "duplicate_abi_slice_marker:2:python3 scripts/zigux/check-phase3-selftest-surface.py"
            in issues
        )

        build_self_test_root(root)
        write_text(root / "scripts/zigux/README.md", "validate_phase3_selftest.py\n")
        issues = validate_root(root)
        assert (
            "scripts_readme:The live support packet inside that same validator-first route is `check-phase3-readme-tooling-inventory.py`"
            in issues
        )
        assert "scripts_readme:phase3_catalog.py --self-test" in issues
        assert "scripts_readme:make -C zigux phase3-selftest" in issues

        build_self_test_root(root)
        write_text(
            root / "scripts/zigux/README.md",
            "\n".join(SCRIPTS_README_MARKERS + [SCRIPTS_README_MARKERS[0]]) + "\n",
        )
        issues = validate_root(root)
        assert "duplicate_scripts_readme_marker:2:validate_phase3_selftest.py" in issues

        build_self_test_root(root)
        write_text(root / "zigux/tests/README.md", "scripts/zigux/validate_phase3_selftest.py\n")
        issues = validate_root(root)
        assert "tests_readme:scripts/zigux/phase3_catalog.py --self-test" in issues
        assert "tests_readme:scripts/zigux/phase3_check_lib.py --self-test" in issues
        assert "tests_readme:scripts/zigux/generate-phase3-check-wrappers.py --check" in issues
        assert "tests_readme:scripts/zigux/run-phase3-checks.py --self-test" in issues
        assert "tests_readme:make -C zigux phase3-selftest" in issues
        assert (
            "tests_readme:opt-in safety check that complements but does not duplicate `make -C zigux phase3-validate`"
            in issues
        )

        build_self_test_root(root)
        write_text(
            root / "zigux/tests/README.md",
            "\n".join(TESTS_README_MARKERS + [TESTS_README_MARKERS[1]]) + "\n",
        )
        issues = validate_root(root)
        assert (
            "duplicate_tests_readme_marker:2:scripts/zigux/phase3_catalog.py --self-test"
            in issues
        )

        build_self_test_root(root)
        write_text(root / "zigux/Makefile", "phase3-selftest:\n")
        issues = validate_root(root)
        assert (
            "makefile:PHONY += phase3-validate phase3-selftest phase3-abi phase3-interop phase3"
            in issues
        )
        assert "makefile:phase3: phase3-validate phase3-abi phase3-interop" in issues

        build_self_test_root(root)
        write_text(
            root / "zigux/Makefile",
            "\n".join(MAKEFILE_MARKERS + [MAKEFILE_MARKERS[0]]) + "\n",
        )
        issues = validate_root(root)
        assert (
            "duplicate_makefile_marker:2:PHONY += phase3-validate phase3-selftest phase3-abi phase3-interop phase3"
            in issues
        )

        build_self_test_root(root)
        (root / "scripts/zigux/validate_phase3_selftest.py").unlink()
        issues = validate_root(root)
        assert "missing_file:scripts/zigux/validate_phase3_selftest.py" in issues

    print("PHASE3_SELFTEST_SURFACE_SELF_TEST=pass")
    print("PHASE3_SELFTEST_SURFACE_SELF_TEST_CASE_COUNT=14")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the shipped Phase 3 selftest review surface stays aligned."
    )
    parser.add_argument(
        "--repo-root",
        default=str(ROOT),
        help="Path to the Zigux repository root.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in coverage without a repository checkout.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_root(Path(args.repo_root).resolve())
    if issues:
        print("PHASE3_SELFTEST_SURFACE=fail")
        print("PHASE3_SELFTEST_SURFACE_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE3_SELFTEST_SURFACE_ISSUES_END")
        return 1

    print("PHASE3_SELFTEST_SURFACE=pass")
    print(
        "PHASE3_SELFTEST_SURFACE_MARKER_COUNT="
        f"{len(DOCS_ROOT_MARKERS) + len(REVIEW_CHECKLIST_MARKERS) + len(ABI_SLICE_MARKERS) + len(SCRIPTS_README_MARKERS) + len(TESTS_README_MARKERS) + len(MAKEFILE_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
