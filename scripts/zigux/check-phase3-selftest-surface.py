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
    "Documentation/zigux/phase3-boundary-lane-sequencing.md",
    "scripts/zigux/README.md",
    "scripts/zigux/validate-phase3.py",
    "scripts/zigux/validate_phase3_selftest.py",
    "scripts/zigux/check-phase3-selftest-surface.py",
    "scripts/zigux/check-phase3-readme-tooling-inventory.py",
    "scripts/zigux/check-phase3-abi-dump-gate.py",
    "scripts/zigux/check-phase3-catalog-selftest.py",
    "scripts/zigux/validate-phase3-abi-bindings-syntax.py",
    "scripts/zigux/survey-phase3-abi-constant-parity.py",
    "scripts/zigux/validate-phase3-policy-unsafe-survey.py",
    "scripts/zigux/check-phase3-policy-byte-guards.py",
    "scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    "scripts/zigux/validate-phase3-export-uapi-survey.py",
    "scripts/zigux/phase3_catalog.py",
    "scripts/zigux/phase3_check_lib.py",
    "scripts/zigux/generate-phase3-check-wrappers.py",
    "scripts/zigux/run-phase3-checks.py",
    "zigux/Makefile",
    "zigux/tests/README.md",
]

DOCS_ROOT_MARKERS = [
    "Documentation/zigux/phase3-boundary-lane-sequencing.md",
    "scripts/zigux/validate_phase3_selftest.py",
    "scripts/zigux/check-phase3-selftest-surface.py",
    "scripts/zigux/check-phase3-readme-tooling-inventory.py",
    "scripts/zigux/check-phase3-abi-dump-gate.py",
    "scripts/zigux/check-phase3-catalog-selftest.py",
    "scripts/zigux/validate-phase3-policy-unsafe-survey.py",
    "scripts/zigux/check-phase3-policy-byte-guards.py",
    "scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    "scripts/zigux/validate-phase3-export-uapi-survey.py",
    "scripts/zigux/validate-phase3-abi-bindings-syntax.py",
    "scripts/zigux/survey-phase3-abi-constant-parity.py",
    "scripts/zigux/phase3_check_lib.py",
    "scripts/zigux/generate-phase3-check-wrappers.py",
    "python3 scripts/zigux/validate-phase3.py",
    "python3 scripts/zigux/validate-phase3.py --slug abi",
    "python3 scripts/zigux/phase3_catalog.py --audit-doc-sync",
    "python3 scripts/zigux/run-phase3-checks.py --slug abi",
    "python3 scripts/zigux/phase3_catalog.py --self-test",
    "make -C zigux phase3-validate",
    "make -C zigux phase3",
    "without duplicating the default `phase3-validate` route",
]

REVIEW_CHECKLIST_MARKERS = [
    "Documentation/zigux/phase3-boundary-lane-sequencing.md",
    "scripts/zigux/validate-phase3.py",
    "scripts/zigux/validate_phase3_selftest.py",
    "scripts/zigux/check-phase3-selftest-surface.py",
    "scripts/zigux/check-phase3-readme-tooling-inventory.py",
    "scripts/zigux/check-phase3-abi-dump-gate.py",
    "scripts/zigux/check-phase3-catalog-selftest.py",
    "scripts/zigux/validate-phase3-policy-unsafe-survey.py",
    "scripts/zigux/check-phase3-policy-byte-guards.py",
    "scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    "scripts/zigux/validate-phase3-export-uapi-survey.py",
    "scripts/zigux/validate-phase3-abi-bindings-syntax.py",
    "scripts/zigux/survey-phase3-abi-constant-parity.py",
    "scripts/zigux/phase3_catalog.py",
    "scripts/zigux/phase3_check_lib.py",
    "scripts/zigux/generate-phase3-check-wrappers.py",
    "scripts/zigux/run-phase3-checks.py",
    "python3 scripts/zigux/phase3_catalog.py --audit-doc-sync",
    "make -C zigux phase3-selftest",
    "manual-only support-script rerun",
    "without implying that `phase3-selftest` is part of the default `phase3-validate` route",
]

ABI_SLICE_MARKERS = [
    "python3 scripts/zigux/validate-phase3-abi-bindings-syntax.py",
    "python3 scripts/zigux/validate-phase3-abi-bindings-syntax.py --self-test",
    "python3 scripts/zigux/validate_phase3_selftest.py",
    "python3 scripts/zigux/check-phase3-selftest-surface.py --self-test",
    "python3 scripts/zigux/check-phase3-selftest-surface.py",
    "python3 scripts/zigux/check-phase3-readme-tooling-inventory.py --self-test",
    "python3 scripts/zigux/check-phase3-readme-tooling-inventory.py",
    "python3 scripts/zigux/check-phase3-abi-dump-gate.py --self-test",
    "python3 scripts/zigux/check-phase3-abi-dump-gate.py",
    "python3 scripts/zigux/check-phase3-catalog-selftest.py --self-test",
    "python3 scripts/zigux/phase3_catalog.py --self-test",
    "python3 scripts/zigux/phase3_catalog.py --audit-doc-sync",
    "python3 scripts/zigux/phase3_check_lib.py --self-test",
    "python3 scripts/zigux/generate-phase3-check-wrappers.py --check",
    "python3 scripts/zigux/run-phase3-checks.py --self-test",
    "python3 scripts/zigux/survey-phase3-abi-constant-parity.py",
    "python3 scripts/zigux/survey-phase3-abi-constant-parity.py --self-test",
    "python3 scripts/zigux/validate-phase3-policy-unsafe-survey.py",
    "python3 scripts/zigux/validate-phase3-policy-unsafe-survey.py --self-test",
    "python3 scripts/zigux/check-phase3-policy-byte-guards.py",
    "python3 scripts/zigux/check-phase3-policy-byte-guards.py --self-test",
    "python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    "python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test",
    "python3 scripts/zigux/validate-phase3-export-uapi-survey.py",
    "python3 scripts/zigux/validate-phase3-export-uapi-survey.py --self-test",
    "make -C zigux phase3-selftest",
    "focused support-script safety check only; `make -C zigux phase3-validate` already invokes the underlying helper self-tests, README tooling inventory checks, catalog sanity checks, wrapper drift checks, shared catalog doc-sync auditing, and shared runner self-checks directly.",
]

SCRIPTS_README_MARKERS = [
    "validate_phase3_selftest.py",
    "The live support packet inside that same validator-first route is `check-phase3-readme-tooling-inventory.py`",
    "check-phase3-abi-dump-gate.py",
    "check-phase3-catalog-selftest.py",
    "survey-phase3-abi-constant-parity.py",
    "validate-phase3-policy-unsafe-survey.py",
    "check-phase3-policy-byte-guards.py",
    "validate-phase3-low-level-wrapper-survey.py",
    "validate-phase3-export-uapi-survey.py",
    "validate-phase3-abi-bindings-syntax.py",
    "phase3_catalog.py --self-test",
    "phase3_catalog.py --audit-doc-sync",
    "phase3_check_lib.py",
    "generate-phase3-check-wrappers.py",
    "run-phase3-checks.py",
    "make -C zigux phase3-selftest",
    "manual or targeted safety check instead of duplicating the default validation route",
]

TESTS_README_MARKERS = [
    "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md",
    "python3 scripts/zigux/validate_phase3_selftest.py",
    "scripts/zigux/check-phase3-selftest-surface.py",
    "scripts/zigux/check-phase3-readme-tooling-inventory.py",
    "scripts/zigux/check-phase3-abi-dump-gate.py",
    "scripts/zigux/check-phase3-catalog-selftest.py",
    "scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    "scripts/zigux/validate-phase3-policy-unsafe-survey.py",
    "scripts/zigux/check-phase3-policy-byte-guards.py",
    "scripts/zigux/validate-phase3-export-uapi-survey.py",
    "scripts/zigux/validate-phase3-abi-bindings-syntax.py",
    "scripts/zigux/survey-phase3-abi-constant-parity.py",
    "scripts/zigux/phase3_catalog.py --self-test",
    "scripts/zigux/phase3_check_lib.py --self-test",
    "python3 scripts/zigux/phase3_catalog.py --audit-doc-sync",
    "scripts/zigux/generate-phase3-check-wrappers.py --check",
    "scripts/zigux/run-phase3-checks.py --self-test",
    "scripts/zigux/run-phase3-checks.py",
    "make -C zigux phase3-selftest",
    "opt-in safety check that complements but does not duplicate `make -C zigux phase3-validate`",
]

MAKEFILE_MARKERS = [
    "PHONY += phase3-validate phase3-selftest phase3-abi phase3-interop phase3",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/survey-phase3-abi-constant-parity.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/survey-phase3-abi-constant-parity.py --self-test",
    "phase3-interop:\n\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/run-phase3-checks.py",
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


def substring_marker_count(
    text: str,
    marker: str,
    *,
    subtract_markers: list[str] | None = None,
) -> int:
    count = text.count(marker)
    if subtract_markers:
        for other in subtract_markers:
            if other != marker and marker in other:
                count -= text.count(other)
    return count


def backticked_or_line_marker_count(text: str, marker: str) -> int:
    return text.count(f"`{marker}`") + sum(1 for line in normalized_marker_lines(text) if line == marker)


def collect_marker_count_issues(
    text: str,
    markers: list[str],
    *,
    prefix: str,
    normalized: bool = True,
    substring: bool = False,
    backticked: bool = False,
    subtract_containing_markers: bool = False,
) -> list[str]:
    issues: list[str] = []
    for marker in markers:
        if substring:
            count = substring_marker_count(
                text,
                marker,
                subtract_markers=markers if subtract_containing_markers else None,
            )
        elif backticked:
            count = backticked_or_line_marker_count(text, marker)
        else:
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

    docs_root_inline_markers = [
        marker for marker in DOCS_ROOT_MARKERS if marker != "without duplicating the default `phase3-validate` route"
    ]
    docs_root_phrase_markers = [
        marker for marker in DOCS_ROOT_MARKERS if marker not in docs_root_inline_markers
    ]
    issues.extend(
        collect_marker_count_issues(
            docs_root,
            docs_root_inline_markers,
            prefix="docs_root",
            substring=False,
            normalized=False,
            backticked=True,
        )
    )
    issues.extend(
        collect_marker_count_issues(
            docs_root,
            docs_root_phrase_markers,
            prefix="docs_root",
            substring=True,
        )
    )
    issues.extend(
        collect_marker_count_issues(
            review,
            REVIEW_CHECKLIST_MARKERS,
            prefix="review_checklist",
            substring=True,
            subtract_containing_markers=True,
        )
    )
    issues.extend(collect_marker_count_issues(abi_slice, ABI_SLICE_MARKERS, prefix="abi_slice"))
    scripts_readme_inline_markers = [
        marker
        for marker in SCRIPTS_README_MARKERS
        if marker
        != "The live support packet inside that same validator-first route is `check-phase3-readme-tooling-inventory.py`"
        and marker != "manual or targeted safety check instead of duplicating the default validation route"
    ]
    scripts_readme_phrase_markers = [
        marker for marker in SCRIPTS_README_MARKERS if marker not in scripts_readme_inline_markers
    ]
    issues.extend(
        collect_marker_count_issues(
            scripts_readme,
            scripts_readme_inline_markers,
            prefix="scripts_readme",
            substring=False,
            normalized=False,
            backticked=True,
        )
    )
    issues.extend(
        collect_marker_count_issues(
            scripts_readme,
            scripts_readme_phrase_markers,
            prefix="scripts_readme",
            substring=True,
        )
    )
    tests_readme_inline_markers = [
        marker
        for marker in TESTS_README_MARKERS
        if marker.startswith("Documentation/")
        or marker.startswith("scripts/")
        or marker.startswith("python3 ")
        or marker.startswith("make -C ")
    ]
    tests_readme_phrase_markers = [
        marker for marker in TESTS_README_MARKERS if marker not in tests_readme_inline_markers
    ]
    issues.extend(
        collect_marker_count_issues(
            tests_readme,
            tests_readme_inline_markers,
            prefix="tests_readme",
            substring=False,
            normalized=False,
            backticked=True,
        )
    )
    issues.extend(
        collect_marker_count_issues(
            tests_readme,
            tests_readme_phrase_markers,
            prefix="tests_readme",
            substring=True,
        )
    )
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
    case_count = 0
    root_validator = globals()["validate_root"]
    with tempfile.TemporaryDirectory(prefix="phase3_selftest_surface_") as tmp_dir:
        root = Path(tmp_dir)

        def validate_root(root_path: Path) -> list[str]:
            nonlocal case_count
            case_count += 1
            return root_validator(root_path)

        build_self_test_root(root)

        assert validate_root(root) == []

        write_text(root / "Documentation/zigux/README.md", "make -C zigux phase3-selftest\n")
        issues = validate_root(root)
        assert "docs_root:Documentation/zigux/phase3-boundary-lane-sequencing.md" in issues
        assert "docs_root:scripts/zigux/validate_phase3_selftest.py" in issues
        assert "docs_root:scripts/zigux/check-phase3-selftest-surface.py" in issues
        assert "docs_root:scripts/zigux/check-phase3-readme-tooling-inventory.py" in issues
        assert "docs_root:scripts/zigux/check-phase3-abi-dump-gate.py" in issues
        assert "docs_root:scripts/zigux/check-phase3-catalog-selftest.py" in issues
        assert "docs_root:scripts/zigux/validate-phase3-policy-unsafe-survey.py" in issues
        assert "docs_root:scripts/zigux/check-phase3-policy-byte-guards.py" in issues
        assert "docs_root:scripts/zigux/validate-phase3-low-level-wrapper-survey.py" in issues
        assert "docs_root:scripts/zigux/validate-phase3-export-uapi-survey.py" in issues
        assert "docs_root:scripts/zigux/validate-phase3-abi-bindings-syntax.py" in issues
        assert "docs_root:scripts/zigux/survey-phase3-abi-constant-parity.py" in issues
        assert "docs_root:scripts/zigux/phase3_check_lib.py" in issues
        assert "docs_root:scripts/zigux/generate-phase3-check-wrappers.py" in issues
        assert "docs_root:python3 scripts/zigux/validate-phase3.py" in issues
        assert "docs_root:python3 scripts/zigux/validate-phase3.py --slug abi" in issues
        assert "docs_root:python3 scripts/zigux/phase3_catalog.py --audit-doc-sync" in issues
        assert "docs_root:python3 scripts/zigux/run-phase3-checks.py --slug abi" in issues
        assert "docs_root:python3 scripts/zigux/phase3_catalog.py --self-test" in issues
        assert "docs_root:make -C zigux phase3-validate" in issues
        assert "docs_root:make -C zigux phase3" in issues
        assert "docs_root:without duplicating the default `phase3-validate` route" in issues

        build_self_test_root(root)
        write_text(
            root / "Documentation/zigux/README.md",
            "\n".join(DOCS_ROOT_MARKERS + [DOCS_ROOT_MARKERS[0]]) + "\n",
        )
        issues = validate_root(root)
        assert (
            "duplicate_docs_root_marker:2:Documentation/zigux/phase3-boundary-lane-sequencing.md"
            in issues
        )

        build_self_test_root(root)
        write_text(
            root / "Documentation/zigux/README.md",
            "\n".join(DOCS_ROOT_MARKERS + [DOCS_ROOT_MARKERS[2]]) + "\n",
        )
        issues = validate_root(root)
        assert (
            "duplicate_docs_root_marker:2:scripts/zigux/check-phase3-selftest-surface.py"
            in issues
        )

        build_self_test_root(root)
        write_text(
            root / "Documentation/zigux/README.md",
            "The docs-root summary keeps Documentation/zigux/phase3-boundary-lane-sequencing.md visible inside a longer sentence.\n"
            + "\n".join(marker for marker in DOCS_ROOT_MARKERS[1:] if marker != "scripts/zigux/validate_phase3_selftest.py")
            + "\n",
        )
        issues = validate_root(root)
        assert "docs_root:Documentation/zigux/phase3-boundary-lane-sequencing.md" in issues

        build_self_test_root(root)
        write_text(
            root / "Documentation/zigux/README.md",
            "The docs-root summary keeps scripts/zigux/validate_phase3_selftest.py visible inside a longer sentence.\n"
            + "\n".join(DOCS_ROOT_MARKERS[2:])
            + "\n",
        )
        issues = validate_root(root)
        assert "docs_root:scripts/zigux/validate_phase3_selftest.py" in issues

        build_self_test_root(root)
        write_text(
            root / "Documentation/zigux/README.md",
            "this sentence mentions scripts/zigux/validate_phase3_selftest without the .py marker\n",
        )
        issues = validate_root(root)
        assert "docs_root:scripts/zigux/validate_phase3_selftest.py" in issues

        build_self_test_root(root)
        write_text(root / "Documentation/zigux/review-checklist.md", "scripts/zigux/validate_phase3_selftest.py\n")
        issues = validate_root(root)
        assert "review_checklist:Documentation/zigux/phase3-boundary-lane-sequencing.md" in issues
        assert "review_checklist:scripts/zigux/validate-phase3.py" in issues
        assert "review_checklist:scripts/zigux/check-phase3-selftest-surface.py" in issues
        assert "review_checklist:scripts/zigux/check-phase3-readme-tooling-inventory.py" in issues
        assert "review_checklist:scripts/zigux/check-phase3-abi-dump-gate.py" in issues
        assert "review_checklist:scripts/zigux/check-phase3-catalog-selftest.py" in issues
        assert "review_checklist:scripts/zigux/validate-phase3-policy-unsafe-survey.py" in issues
        assert "review_checklist:scripts/zigux/check-phase3-policy-byte-guards.py" in issues
        assert "review_checklist:scripts/zigux/validate-phase3-low-level-wrapper-survey.py" in issues
        assert "review_checklist:scripts/zigux/validate-phase3-export-uapi-survey.py" in issues
        assert "review_checklist:scripts/zigux/validate-phase3-abi-bindings-syntax.py" in issues
        assert "review_checklist:scripts/zigux/survey-phase3-abi-constant-parity.py" in issues
        assert "review_checklist:scripts/zigux/phase3_catalog.py" in issues
        assert "review_checklist:scripts/zigux/phase3_check_lib.py" in issues
        assert "review_checklist:scripts/zigux/generate-phase3-check-wrappers.py" in issues
        assert "review_checklist:scripts/zigux/run-phase3-checks.py" in issues
        assert "review_checklist:python3 scripts/zigux/phase3_catalog.py --audit-doc-sync" in issues
        assert "review_checklist:make -C zigux phase3-selftest" in issues

        build_self_test_root(root)
        write_text(
            root / "Documentation/zigux/review-checklist.md",
            "\n".join(
                REVIEW_CHECKLIST_MARKERS[:4]
                 + [
                     "the review packet keeps scripts/zigux/check-phase3-readme-tooling-inventory.py, scripts/zigux/check-phase3-abi-dump-gate.py, scripts/zigux/check-phase3-catalog-selftest.py, scripts/zigux/validate-phase3-policy-unsafe-survey.py, scripts/zigux/check-phase3-policy-byte-guards.py, scripts/zigux/validate-phase3-low-level-wrapper-survey.py, scripts/zigux/validate-phase3-export-uapi-survey.py, scripts/zigux/validate-phase3-abi-bindings-syntax.py, scripts/zigux/survey-phase3-abi-constant-parity.py, scripts/zigux/phase3_catalog.py, scripts/zigux/phase3_check_lib.py, scripts/zigux/generate-phase3-check-wrappers.py, scripts/zigux/run-phase3-checks.py, python3 scripts/zigux/phase3_catalog.py --audit-doc-sync, and make -C zigux phase3-selftest visible inside one longer checklist sentence"
                 ]
                + REVIEW_CHECKLIST_MARKERS[19:]
            )
            + "\n",
        )
        assert validate_root(root) == []

        build_self_test_root(root)
        write_text(
            root / "Documentation/zigux/review-checklist.md",
            "\n".join(REVIEW_CHECKLIST_MARKERS + [REVIEW_CHECKLIST_MARKERS[0]]) + "\n",
        )
        issues = validate_root(root)
        assert (
            "duplicate_review_checklist_marker:2:Documentation/zigux/phase3-boundary-lane-sequencing.md"
            in issues
        )

        build_self_test_root(root)
        write_text(
            root / "Documentation/zigux/review-checklist.md",
            "\n".join(REVIEW_CHECKLIST_MARKERS + [REVIEW_CHECKLIST_MARKERS[18]]) + "\n",
        )
        issues = validate_root(root)
        assert "duplicate_review_checklist_marker:2:make -C zigux phase3-selftest" in issues

        build_self_test_root(root)
        write_text(
            root / "Documentation/zigux/review-checklist.md",
            "\n".join(REVIEW_CHECKLIST_MARKERS + [REVIEW_CHECKLIST_MARKERS[12]]) + "\n",
        )
        issues = validate_root(root)
        assert (
            "duplicate_review_checklist_marker:2:scripts/zigux/survey-phase3-abi-constant-parity.py"
            in issues
        )

        build_self_test_root(root)
        write_text(
            root / "Documentation/zigux/review-checklist.md",
            "\n".join(REVIEW_CHECKLIST_MARKERS + [REVIEW_CHECKLIST_MARKERS[16]]) + "\n",
        )
        issues = validate_root(root)
        assert (
            "duplicate_review_checklist_marker:2:scripts/zigux/run-phase3-checks.py"
            in issues
        )

        build_self_test_root(root)
        write_text(root / "Documentation/zigux/phase3-abi-slice.md", "python3 scripts/zigux/validate_phase3_selftest.py\n")
        issues = validate_root(root)
        assert "abi_slice:python3 scripts/zigux/validate-phase3-abi-bindings-syntax.py" in issues
        assert "abi_slice:python3 scripts/zigux/validate-phase3-abi-bindings-syntax.py --self-test" in issues
        assert "abi_slice:python3 scripts/zigux/check-phase3-selftest-surface.py --self-test" in issues
        assert "abi_slice:python3 scripts/zigux/check-phase3-selftest-surface.py" in issues
        assert "abi_slice:python3 scripts/zigux/check-phase3-readme-tooling-inventory.py --self-test" in issues
        assert "abi_slice:python3 scripts/zigux/check-phase3-readme-tooling-inventory.py" in issues
        assert "abi_slice:python3 scripts/zigux/check-phase3-abi-dump-gate.py --self-test" in issues
        assert "abi_slice:python3 scripts/zigux/check-phase3-abi-dump-gate.py" in issues
        assert "abi_slice:python3 scripts/zigux/check-phase3-catalog-selftest.py --self-test" in issues
        assert "abi_slice:python3 scripts/zigux/phase3_catalog.py --self-test" in issues
        assert "abi_slice:python3 scripts/zigux/phase3_catalog.py --audit-doc-sync" in issues
        assert "abi_slice:python3 scripts/zigux/phase3_check_lib.py --self-test" in issues
        assert "abi_slice:python3 scripts/zigux/generate-phase3-check-wrappers.py --check" in issues
        assert "abi_slice:python3 scripts/zigux/run-phase3-checks.py --self-test" in issues
        assert "abi_slice:python3 scripts/zigux/survey-phase3-abi-constant-parity.py" in issues
        assert "abi_slice:python3 scripts/zigux/survey-phase3-abi-constant-parity.py --self-test" in issues
        assert "abi_slice:python3 scripts/zigux/validate-phase3-policy-unsafe-survey.py" in issues
        assert "abi_slice:python3 scripts/zigux/validate-phase3-policy-unsafe-survey.py --self-test" in issues
        assert "abi_slice:python3 scripts/zigux/check-phase3-policy-byte-guards.py" in issues
        assert "abi_slice:python3 scripts/zigux/check-phase3-policy-byte-guards.py --self-test" in issues
        assert "abi_slice:python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py" in issues
        assert "abi_slice:python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test" in issues
        assert "abi_slice:python3 scripts/zigux/validate-phase3-export-uapi-survey.py" in issues
        assert "abi_slice:python3 scripts/zigux/validate-phase3-export-uapi-survey.py --self-test" in issues
        assert "abi_slice:make -C zigux phase3-selftest" in issues

        build_self_test_root(root)
        write_text(
            root / "Documentation/zigux/phase3-abi-slice.md",
            "\n".join(ABI_SLICE_MARKERS + [ABI_SLICE_MARKERS[3]]) + "\n",
        )
        issues = validate_root(root)
        assert (
            "duplicate_abi_slice_marker:2:python3 scripts/zigux/check-phase3-selftest-surface.py --self-test"
            in issues
        )

        build_self_test_root(root)
        write_text(
            root / "Documentation/zigux/phase3-abi-slice.md",
            "\n".join(ABI_SLICE_MARKERS + [ABI_SLICE_MARKERS[4]]) + "\n",
        )
        issues = validate_root(root)
        assert (
            "duplicate_abi_slice_marker:2:python3 scripts/zigux/check-phase3-selftest-surface.py"
            in issues
        )

        build_self_test_root(root)
        write_text(
            root / "Documentation/zigux/phase3-abi-slice.md",
            "\n".join(ABI_SLICE_MARKERS + [ABI_SLICE_MARKERS[6]]) + "\n",
        )
        issues = validate_root(root)
        assert (
            "duplicate_abi_slice_marker:2:python3 scripts/zigux/check-phase3-readme-tooling-inventory.py"
            in issues
        )

        build_self_test_root(root)
        write_text(
            root / "Documentation/zigux/phase3-abi-slice.md",
            "\n".join(ABI_SLICE_MARKERS + [ABI_SLICE_MARKERS[8]]) + "\n",
        )
        issues = validate_root(root)
        assert (
            "duplicate_abi_slice_marker:2:python3 scripts/zigux/check-phase3-abi-dump-gate.py"
            in issues
        )

        build_self_test_root(root)
        write_text(
            root / "Documentation/zigux/phase3-abi-slice.md",
            "\n".join(ABI_SLICE_MARKERS + [ABI_SLICE_MARKERS[10]]) + "\n",
        )
        issues = validate_root(root)
        assert (
            "duplicate_abi_slice_marker:2:python3 scripts/zigux/phase3_catalog.py --self-test"
            in issues
        )

        build_self_test_root(root)
        write_text(
            root / "Documentation/zigux/phase3-abi-slice.md",
            "\n".join(ABI_SLICE_MARKERS + [ABI_SLICE_MARKERS[15]]) + "\n",
        )
        issues = validate_root(root)
        assert (
            "duplicate_abi_slice_marker:2:python3 scripts/zigux/survey-phase3-abi-constant-parity.py"
            in issues
        )

        build_self_test_root(root)
        write_text(
            root / "Documentation/zigux/phase3-abi-slice.md",
            "\n".join(ABI_SLICE_MARKERS + [ABI_SLICE_MARKERS[17]]) + "\n",
        )
        issues = validate_root(root)
        assert (
            "duplicate_abi_slice_marker:2:python3 scripts/zigux/validate-phase3-policy-unsafe-survey.py"
            in issues
        )

        build_self_test_root(root)
        write_text(root / "scripts/zigux/README.md", "validate_phase3_selftest.py\n")
        issues = validate_root(root)
        assert (
            "scripts_readme:The live support packet inside that same validator-first route is `check-phase3-readme-tooling-inventory.py`"
            in issues
        )
        assert "scripts_readme:check-phase3-abi-dump-gate.py" in issues
        assert "scripts_readme:check-phase3-catalog-selftest.py" in issues
        assert "scripts_readme:survey-phase3-abi-constant-parity.py" in issues
        assert "scripts_readme:validate-phase3-policy-unsafe-survey.py" in issues
        assert "scripts_readme:check-phase3-policy-byte-guards.py" in issues
        assert "scripts_readme:validate-phase3-low-level-wrapper-survey.py" in issues
        assert "scripts_readme:validate-phase3-export-uapi-survey.py" in issues
        assert "scripts_readme:validate-phase3-abi-bindings-syntax.py" in issues
        assert "scripts_readme:phase3_catalog.py --self-test" in issues
        assert "scripts_readme:phase3_catalog.py --audit-doc-sync" in issues
        assert "scripts_readme:phase3_check_lib.py" in issues
        assert "scripts_readme:generate-phase3-check-wrappers.py" in issues
        assert "scripts_readme:run-phase3-checks.py" in issues
        assert "scripts_readme:make -C zigux phase3-selftest" in issues

        build_self_test_root(root)
        write_text(
            root / "scripts/zigux/README.md",
            "\n".join(SCRIPTS_README_MARKERS + [SCRIPTS_README_MARKERS[0]]) + "\n",
        )
        issues = validate_root(root)
        assert "duplicate_scripts_readme_marker:2:validate_phase3_selftest.py" in issues

        build_self_test_root(root)
        write_text(
            root / "scripts/zigux/README.md",
            "The live support packet inside that same validator-first route is `check-phase3-readme-tooling-inventory.py`, `check-phase3-abi-dump-gate.py`, `check-phase3-catalog-selftest.py`, `validate-phase3-policy-unsafe-survey.py`, `check-phase3-policy-byte-guards.py`, `validate-phase3-low-level-wrapper-survey.py`, `validate-phase3-export-uapi-survey.py`, `validate-phase3-abi-bindings-syntax.py`, `survey-phase3-abi-constant-parity.py`, `phase3_catalog.py`, `phase3_check_lib.py`, `generate-phase3-check-wrappers.py`, and `run-phase3-checks.py`.\n"
            "Use `validate_phase3_selftest.py` for the isolated validator replay.\n"
            "`phase3_catalog.py --self-test`, `phase3_catalog.py --audit-doc-sync`, and `make -C zigux phase3-selftest` remain a manual or targeted safety check instead of duplicating the default validation route, while `python3 scripts/zigux/run-phase3-checks.py --slug abi` keeps the shared ABI interop route explicit.\n",
        )
        assert validate_root(root) == []

        build_self_test_root(root)
        write_text(
            root / "scripts/zigux/README.md",
            "The live support packet inside that same validator-first route is `check-phase3-readme-tooling-inventory.py`, `check-phase3-abi-dump-gate.py`, `check-phase3-catalog-selftest.py`, `validate-phase3-policy-unsafe-survey.py`, `check-phase3-policy-byte-guards.py`, `validate-phase3-low-level-wrapper-survey.py`, `validate-phase3-export-uapi-survey.py`, `validate-phase3-abi-bindings-syntax.py`, `survey-phase3-abi-constant-parity.py`, `phase3_catalog.py`, `phase3_check_lib.py`, `generate-phase3-check-wrappers.py`, and the shared route only appears as `python3 scripts/zigux/run-phase3-checks.py --slug abi`.\n"
            "Use `validate_phase3_selftest.py` for the isolated validator replay.\n"
            "`phase3_catalog.py --self-test`, `phase3_catalog.py --audit-doc-sync`, and `make -C zigux phase3-selftest` remain a manual or targeted safety check instead of duplicating the default validation route.\n",
        )
        issues = validate_root(root)
        assert "scripts_readme:run-phase3-checks.py" in issues

        build_self_test_root(root)
        write_text(
            root / "zigux/tests/README.md",
            "python3 scripts/zigux/validate_phase3_selftest.py\n",
        )
        issues = validate_root(root)
        assert "tests_readme:Documentation/zigux/phase3-policy-unsafe-boundary-survey.md" in issues
        assert "tests_readme:scripts/zigux/check-phase3-selftest-surface.py" in issues
        assert "tests_readme:scripts/zigux/check-phase3-readme-tooling-inventory.py" in issues
        assert "tests_readme:scripts/zigux/check-phase3-abi-dump-gate.py" in issues
        assert "tests_readme:scripts/zigux/check-phase3-catalog-selftest.py" in issues
        assert "tests_readme:scripts/zigux/validate-phase3-low-level-wrapper-survey.py" in issues
        assert "tests_readme:scripts/zigux/validate-phase3-policy-unsafe-survey.py" in issues
        assert "tests_readme:scripts/zigux/check-phase3-policy-byte-guards.py" in issues
        assert "tests_readme:scripts/zigux/validate-phase3-export-uapi-survey.py" in issues
        assert "tests_readme:scripts/zigux/validate-phase3-abi-bindings-syntax.py" in issues
        assert "tests_readme:scripts/zigux/survey-phase3-abi-constant-parity.py" in issues
        assert "tests_readme:scripts/zigux/phase3_catalog.py --self-test" in issues
        assert "tests_readme:scripts/zigux/phase3_check_lib.py --self-test" in issues
        assert "tests_readme:python3 scripts/zigux/phase3_catalog.py --audit-doc-sync" in issues
        assert "tests_readme:scripts/zigux/generate-phase3-check-wrappers.py --check" in issues
        assert "tests_readme:scripts/zigux/run-phase3-checks.py --self-test" in issues
        assert "tests_readme:scripts/zigux/run-phase3-checks.py" in issues
        assert "tests_readme:make -C zigux phase3-selftest" in issues
        assert (
            "tests_readme:opt-in safety check that complements but does not duplicate `make -C zigux phase3-validate`"
            in issues
        )

        build_self_test_root(root)
        write_text(root / "zigux/tests/README.md", "scripts/zigux/validate_phase3_selftest.py\n")
        issues = validate_root(root)
        assert "tests_readme:python3 scripts/zigux/validate_phase3_selftest.py" in issues

        build_self_test_root(root)
        write_text(
            root / "zigux/tests/README.md",
            "\n".join(
                marker
                for marker in TESTS_README_MARKERS
                if marker != "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md"
            ) + "\n",
        )
        issues = validate_root(root)
        assert "tests_readme:Documentation/zigux/phase3-policy-unsafe-boundary-survey.md" in issues

        build_self_test_root(root)
        write_text(
            root / "zigux/tests/README.md",
            "\n".join(
                TESTS_README_MARKERS
                + ["Documentation/zigux/phase3-policy-unsafe-boundary-survey.md"]
            ) + "\n",
        )
        issues = validate_root(root)
        assert (
            "duplicate_tests_readme_marker:2:Documentation/zigux/phase3-policy-unsafe-boundary-survey.md"
            in issues
        )

        build_self_test_root(root)
        write_text(
            root / "zigux/tests/README.md",
            "\n".join(TESTS_README_MARKERS + [TESTS_README_MARKERS[2]]) + "\n",
        )
        issues = validate_root(root)
        assert (
            "duplicate_tests_readme_marker:2:scripts/zigux/check-phase3-selftest-surface.py"
            in issues
        )

        build_self_test_root(root)
        write_text(
            root / "zigux/tests/README.md",
            "\n".join(TESTS_README_MARKERS + [TESTS_README_MARKERS[5]]) + "\n",
        )
        issues = validate_root(root)
        assert (
            "duplicate_tests_readme_marker:2:scripts/zigux/check-phase3-catalog-selftest.py"
            in issues
        )

        build_self_test_root(root)
        write_text(
            root / "zigux/tests/README.md",
            "\n".join(marker for marker in TESTS_README_MARKERS if marker != "scripts/zigux/check-phase3-catalog-selftest.py") + "\n",
        )
        issues = validate_root(root)
        assert "tests_readme:scripts/zigux/check-phase3-catalog-selftest.py" in issues

        build_self_test_root(root)
        write_text(
            root / "zigux/tests/README.md",
            "\n".join(TESTS_README_MARKERS + [TESTS_README_MARKERS[11]]) + "\n",
        )
        issues = validate_root(root)
        assert (
            "duplicate_tests_readme_marker:2:scripts/zigux/survey-phase3-abi-constant-parity.py"
            in issues
        )

        build_self_test_root(root)
        write_text(
            root / "zigux/tests/README.md",
            "\n".join(TESTS_README_MARKERS + ["scripts/zigux/run-phase3-checks.py"]) + "\n",
        )
        issues = validate_root(root)
        assert (
            "duplicate_tests_readme_marker:2:scripts/zigux/run-phase3-checks.py"
            in issues
        )

        build_self_test_root(root)
        write_text(
            root / "zigux/tests/README.md",
            "\n".join(marker for marker in TESTS_README_MARKERS if marker != "scripts/zigux/run-phase3-checks.py") + "\n",
        )
        issues = validate_root(root)
        assert "tests_readme:scripts/zigux/run-phase3-checks.py" in issues

        build_self_test_root(root)
        write_text(root / "zigux/Makefile", "phase3-selftest:\n")
        issues = validate_root(root)
        assert (
            "makefile:PHONY += phase3-validate phase3-selftest phase3-abi phase3-interop phase3"
            in issues
        )
        assert (
            "makefile:phase3-interop:\n\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/run-phase3-checks.py"
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
        write_text(
            root / "zigux/Makefile",
            "\n".join(MAKEFILE_MARKERS[1:]) + "\n",
        )
        issues = validate_root(root)
        assert (
            "makefile:PHONY += phase3-validate phase3-selftest phase3-abi phase3-interop phase3"
            in issues
        )

        build_self_test_root(root)
        write_text(
            root / "zigux/Makefile",
            "\n".join(MAKEFILE_MARKERS + [MAKEFILE_MARKERS[1]]) + "\n",
        )
        issues = validate_root(root)
        assert (
            "duplicate_makefile_marker:2:cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/survey-phase3-abi-constant-parity.py"
            in issues
        )

        build_self_test_root(root)
        (root / "scripts/zigux/validate-phase3.py").unlink()
        issues = validate_root(root)
        assert "missing_file:scripts/zigux/validate-phase3.py" in issues

        build_self_test_root(root)
        (root / "scripts/zigux/validate_phase3_selftest.py").unlink()
        issues = validate_root(root)
        assert "missing_file:scripts/zigux/validate_phase3_selftest.py" in issues

        build_self_test_root(root)
        (root / "scripts/zigux/check-phase3-readme-tooling-inventory.py").unlink()
        issues = validate_root(root)
        assert "missing_file:scripts/zigux/check-phase3-readme-tooling-inventory.py" in issues

        build_self_test_root(root)
        (root / "scripts/zigux/check-phase3-abi-dump-gate.py").unlink()
        issues = validate_root(root)
        assert "missing_file:scripts/zigux/check-phase3-abi-dump-gate.py" in issues

        build_self_test_root(root)
        (root / "scripts/zigux/validate-phase3-export-uapi-survey.py").unlink()
        issues = validate_root(root)
        assert "missing_file:scripts/zigux/validate-phase3-export-uapi-survey.py" in issues

        build_self_test_root(root)
        (root / "scripts/zigux/check-phase3-policy-byte-guards.py").unlink()
        issues = validate_root(root)
        assert "missing_file:scripts/zigux/check-phase3-policy-byte-guards.py" in issues

        build_self_test_root(root)
        (root / "scripts/zigux/survey-phase3-abi-constant-parity.py").unlink()
        issues = validate_root(root)
        assert "missing_file:scripts/zigux/survey-phase3-abi-constant-parity.py" in issues

        build_self_test_root(root)
        (root / "Documentation/zigux/phase3-boundary-lane-sequencing.md").unlink()
        issues = validate_root(root)
        assert "missing_file:Documentation/zigux/phase3-boundary-lane-sequencing.md" in issues

    print("PHASE3_SELFTEST_SURFACE_SELF_TEST=pass")
    print(f"PHASE3_SELFTEST_SURFACE_SELF_TEST_CASE_COUNT={case_count}")
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
