#!/usr/bin/env python3
"""Fail-close the focused Phase 3 catalog selftest reminder surface."""

from __future__ import annotations

import argparse
from pathlib import Path
import tempfile


DOCS_README_PATH = Path("Documentation/zigux/README.md")
CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")
TESTS_README_PATH = Path("zigux/tests/README.md")
SCRIPTS_README_PATH = Path("scripts/zigux/README.md")
SELFTEST_DRIVER_PATH = Path("scripts/zigux/validate_phase3_selftest.py")
MAKEFILE_PATH = Path("zigux/Makefile")

DOCS_README_MARKERS = (
    "scripts/zigux/check-phase3-catalog-selftest.py",
    "python3 scripts/zigux/phase3_catalog.py --self-test",
    "python3 scripts/zigux/phase3_catalog.py --audit-doc-sync",
)
DOCS_README_PHASE3_PREFIX = "Phase 3 notes\n"
DOCS_README_PHASE3_NEXT_PREFIX = "Phase 5 notes\n"

CHECKLIST_MARKERS = (
    "scripts/zigux/check-phase3-catalog-selftest.py",
    "python3 scripts/zigux/phase3_catalog.py --audit-doc-sync",
    "make -C zigux phase3-selftest",
)
CHECKLIST_PHASE3_REMINDER_PREFIX = (
    "  * if the change touches the shared Phase 3 ABI/runtime packet, do "
)
CHECKLIST_PHASE3_REMINDER_NEXT_PREFIX = (
    "  * if the change touches the shared Phase 4 validation packet, do "
)

TESTS_README_MARKERS = (
    "scripts/zigux/check-phase3-catalog-selftest.py",
    "scripts/zigux/phase3_catalog.py --self-test",
    "scripts/zigux/phase3_check_lib.py --self-test",
    "scripts/zigux/generate-phase3-check-wrappers.py --check",
    "scripts/zigux/run-phase3-checks.py --self-test",
    "scripts/zigux/phase3_catalog.py --audit-doc-sync",
    "make -C zigux phase3-selftest",
)
TESTS_README_PHASE3_REMINDER_PREFIX = (
    "  * keep the focused Phase 3 validator-support replay explicit in the tests root too:"
)
TESTS_README_PHASE3_REMINDER_NEXT_PREFIX = (
    "  * keep the shared Phase 4 rollback packet explicit in the tests root too:"
)

SCRIPTS_README_MARKERS = (
    "check-phase3-catalog-selftest.py",
    "phase3_catalog.py",
    "phase3_check_lib.py",
    "generate-phase3-check-wrappers.py",
    "run-phase3-checks.py",
    "python3 scripts/zigux/phase3_catalog.py --self-test",
    "python3 scripts/zigux/phase3_catalog.py --audit-doc-sync",
)
SCRIPTS_README_PHASE3_PREFIX = "Phase 3 flow - "
SCRIPTS_README_PHASE3_NEXT_PREFIX = "Phase 4 flow - "
SCRIPTS_README_PHASE3_SECTION_MARKERS = (
    "check-phase3-catalog-selftest.py",
    "python3 scripts/zigux/phase3_catalog.py --self-test",
    "python3 scripts/zigux/phase3_catalog.py --audit-doc-sync",
    "python3 scripts/zigux/phase3_check_lib.py --self-test",
    "python3 scripts/zigux/generate-phase3-check-wrappers.py --check",
    "python3 scripts/zigux/run-phase3-checks.py --slug abi",
)

SELFTEST_DRIVER_MARKERS = (
    'Path("scripts/zigux/check-phase3-catalog-selftest.py")',
    'Path("scripts/zigux/phase3_catalog.py"), ("--self-test",)',
    'Path("scripts/zigux/phase3_check_lib.py"), ("--self-test",)',
    'Path("scripts/zigux/generate-phase3-check-wrappers.py"), ("--self-test",)',
    'Path("scripts/zigux/run-phase3-checks.py"), ("--self-test",)',
)
MAKEFILE_MARKERS = (
    "phase3-validate:",
    "$(PYTHON) scripts/zigux/check-phase3-catalog-selftest.py --self-test",
    "$(PYTHON) scripts/zigux/phase3_catalog.py --self-test",
    "$(PYTHON) scripts/zigux/phase3_catalog.py --audit-doc-sync",
    "$(PYTHON) scripts/zigux/phase3_check_lib.py --self-test",
    "$(PYTHON) scripts/zigux/generate-phase3-check-wrappers.py --self-test",
    "$(PYTHON) scripts/zigux/generate-phase3-check-wrappers.py --check",
    "$(PYTHON) scripts/zigux/run-phase3-checks.py --self-test",
    "phase3-selftest:",
)

DOCS_README_PHASE3_MARKER_COUNTS = {marker: 1 for marker in DOCS_README_MARKERS}
CHECKLIST_PHASE3_MARKER_COUNTS = {marker: 1 for marker in CHECKLIST_MARKERS}
TESTS_README_PHASE3_MARKER_COUNTS = {marker: 1 for marker in TESTS_README_MARKERS}
SCRIPTS_README_PHASE3_MARKER_COUNTS = {
    marker: 1 for marker in SCRIPTS_README_PHASE3_SECTION_MARKERS
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _check_markers(path: Path, markers: tuple[str, ...], label: str) -> list[str]:
    try:
        text = _read(path)
    except FileNotFoundError:
        return [f"missing repo file: {path.as_posix()}"]
    return [
        f"missing {label} marker: {marker}"
        for marker in markers
        if marker not in text
    ]


def _extract_section(text: str, start_prefix: str, next_prefix: str | None) -> str | None:
    if start_prefix not in text:
        return None
    section = text.split(start_prefix, 1)[1]
    if next_prefix is not None and next_prefix in section:
        section = section.split(next_prefix, 1)[0]
    elif next_prefix is None and "\n## " in section:
        section = section.split("\n## ", 1)[0]
    return section


def _check_section_marker_counts(
    path: Path,
    start_prefix: str,
    next_prefix: str | None,
    marker_counts: dict[str, int],
    label: str,
) -> list[str]:
    try:
        text = _read(path)
    except FileNotFoundError:
        return [f"missing repo file: {path.as_posix()}"]

    section = _extract_section(text, start_prefix, next_prefix)
    if section is None:
        return [f"missing {label} section"]

    issues: list[str] = []
    for marker, expected_count in marker_counts.items():
        actual_count = section.count(marker)
        if actual_count != expected_count:
            issues.append(
                f"{label} marker count drift: {marker} "
                f"(expected {expected_count}, found {actual_count})"
            )
    return issues


def _check_docs_readme_phase3(path: Path) -> list[str]:
    return _check_section_marker_counts(
        path,
        DOCS_README_PHASE3_PREFIX,
        DOCS_README_PHASE3_NEXT_PREFIX,
        DOCS_README_PHASE3_MARKER_COUNTS,
        "docs README Phase 3 notes",
    )


def _check_review_checklist_phase3(path: Path) -> list[str]:
    return _check_section_marker_counts(
        path,
        CHECKLIST_PHASE3_REMINDER_PREFIX,
        CHECKLIST_PHASE3_REMINDER_NEXT_PREFIX,
        CHECKLIST_PHASE3_MARKER_COUNTS,
        "review checklist Phase 3 reminder",
    )


def _check_tests_readme_phase3(path: Path) -> list[str]:
    return _check_section_marker_counts(
        path,
        TESTS_README_PHASE3_REMINDER_PREFIX,
        TESTS_README_PHASE3_REMINDER_NEXT_PREFIX,
        TESTS_README_PHASE3_MARKER_COUNTS,
        "tests README Phase 3 reminder",
    )


def _check_scripts_readme_phase3(path: Path) -> list[str]:
    return _check_section_marker_counts(
        path,
        SCRIPTS_README_PHASE3_PREFIX,
        SCRIPTS_README_PHASE3_NEXT_PREFIX,
        SCRIPTS_README_PHASE3_MARKER_COUNTS,
        "scripts README Phase 3 flow",
    )


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    issues.extend(
        _check_markers(repo_root / DOCS_README_PATH, DOCS_README_MARKERS, "docs README")
    )
    issues.extend(_check_docs_readme_phase3(repo_root / DOCS_README_PATH))
    issues.extend(
        _check_markers(repo_root / CHECKLIST_PATH, CHECKLIST_MARKERS, "review checklist")
    )
    issues.extend(_check_review_checklist_phase3(repo_root / CHECKLIST_PATH))
    issues.extend(
        _check_markers(repo_root / TESTS_README_PATH, TESTS_README_MARKERS, "tests README")
    )
    issues.extend(_check_tests_readme_phase3(repo_root / TESTS_README_PATH))
    issues.extend(
        _check_markers(
            repo_root / SCRIPTS_README_PATH, SCRIPTS_README_MARKERS, "scripts README"
        )
    )
    issues.extend(_check_scripts_readme_phase3(repo_root / SCRIPTS_README_PATH))
    issues.extend(
        _check_markers(
            repo_root / SELFTEST_DRIVER_PATH, SELFTEST_DRIVER_MARKERS, "selftest driver"
        )
    )
    issues.extend(_check_markers(repo_root / MAKEFILE_PATH, MAKEFILE_MARKERS, "makefile"))
    return issues


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _populate_repo(root: Path) -> None:
    _write(
        root / DOCS_README_PATH,
        "\n".join(
            (
                DOCS_README_PHASE3_PREFIX.rstrip("\n"),
                *DOCS_README_MARKERS,
                DOCS_README_PHASE3_NEXT_PREFIX.rstrip("\n"),
            )
        )
        + "\n",
    )
    _write(
        root / CHECKLIST_PATH,
        "\n".join(
            (
                "## Validation",
                CHECKLIST_PHASE3_REMINDER_PREFIX,
                *CHECKLIST_MARKERS,
                CHECKLIST_PHASE3_REMINDER_NEXT_PREFIX,
            )
        )
        + "\n",
    )
    _write(
        root / TESTS_README_PATH,
        "\n".join(
            (
                TESTS_README_PHASE3_REMINDER_PREFIX,
                *TESTS_README_MARKERS,
                TESTS_README_PHASE3_REMINDER_NEXT_PREFIX,
            )
        )
        + "\n",
    )
    _write(
        root / SCRIPTS_README_PATH,
        "\n".join(
            (
                SCRIPTS_README_PHASE3_PREFIX,
                *SCRIPTS_README_PHASE3_SECTION_MARKERS,
                SCRIPTS_README_PHASE3_NEXT_PREFIX,
            )
        )
        + "\n",
    )
    _write(root / SELFTEST_DRIVER_PATH, "\n".join(SELFTEST_DRIVER_MARKERS) + "\n")
    _write(root / MAKEFILE_PATH, "\n".join(MAKEFILE_MARKERS) + "\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_catalog_selftest_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_CATALOG_SELFTEST_SURFACE_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        broken_path = root / DOCS_README_PATH
        broken_path.write_text(
            _read(broken_path).replace(
                "python3 scripts/zigux/phase3_catalog.py --self-test",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "docs README Phase 3 notes marker count drift: "
            "python3 scripts/zigux/phase3_catalog.py --self-test "
            "(expected 1, found 0)"
        )
        if expected not in issues:
            print("PHASE3_CATALOG_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected docs README Phase 3 section drift was not reported")
            return 1

        _populate_repo(root)
        broken_path.write_text(
            _read(broken_path).replace(
                "python3 scripts/zigux/phase3_catalog.py --audit-doc-sync",
                DOCS_README_PHASE3_NEXT_PREFIX
                + "python3 scripts/zigux/phase3_catalog.py --audit-doc-sync",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "docs README Phase 3 notes marker count drift: "
            "python3 scripts/zigux/phase3_catalog.py --audit-doc-sync "
            "(expected 1, found 0)"
        )
        if expected not in issues:
            print("PHASE3_CATALOG_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected docs README next-section drift was not reported")
            return 1

        _populate_repo(root)
        broken_path = root / CHECKLIST_PATH
        broken_path.write_text(
            _read(broken_path).replace(
                "scripts/zigux/check-phase3-catalog-selftest.py",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "review checklist Phase 3 reminder marker count drift: "
            "scripts/zigux/check-phase3-catalog-selftest.py "
            "(expected 1, found 0)"
        )
        if expected not in issues:
            print("PHASE3_CATALOG_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected review checklist marker drift was not reported")
            return 1

        _populate_repo(root)
        broken_path = root / TESTS_README_PATH
        broken_path.write_text(
            _read(broken_path).replace(
                "scripts/zigux/phase3_catalog.py --audit-doc-sync",
                TESTS_README_PHASE3_REMINDER_NEXT_PREFIX
                + "\n"
                + "scripts/zigux/phase3_catalog.py --audit-doc-sync",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "tests README Phase 3 reminder marker count drift: "
            "scripts/zigux/phase3_catalog.py --audit-doc-sync "
            "(expected 1, found 0)"
        )
        if expected not in issues:
            print("PHASE3_CATALOG_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected tests README section drift was not reported")
            return 1

        _populate_repo(root)
        broken_path.write_text(
            _read(broken_path).replace(
                "scripts/zigux/generate-phase3-check-wrappers.py --check",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "tests README Phase 3 reminder marker count drift: "
            "scripts/zigux/generate-phase3-check-wrappers.py --check "
            "(expected 1, found 0)"
        )
        if expected not in issues:
            print("PHASE3_CATALOG_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected tests README wrapper-check drift was not reported")
            return 1

        _populate_repo(root)
        broken_path = root / SCRIPTS_README_PATH
        broken_path.write_text(
            _read(broken_path).replace(
                "python3 scripts/zigux/run-phase3-checks.py --slug abi",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "scripts README Phase 3 flow marker count drift: "
            "python3 scripts/zigux/run-phase3-checks.py --slug abi "
            "(expected 1, found 0)"
        )
        if expected not in issues:
            print("PHASE3_CATALOG_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected scripts README Phase 3 drift was not reported")
            return 1

        _populate_repo(root)
        broken_path.write_text(
            _read(broken_path).replace(
                "check-phase3-catalog-selftest.py",
                "check-phase3-catalog-selftest.py\ncheck-phase3-catalog-selftest.py",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "scripts README Phase 3 flow marker count drift: "
            "check-phase3-catalog-selftest.py (expected 1, found 2)"
        )
        if expected not in issues:
            print("PHASE3_CATALOG_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected scripts README duplicate drift was not reported")
            return 1

        _populate_repo(root)
        broken_path = root / SELFTEST_DRIVER_PATH
        broken_path.write_text(
            _read(broken_path).replace(
                'Path("scripts/zigux/phase3_check_lib.py"), ("--self-test",)',
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "missing selftest driver marker: "
            'Path("scripts/zigux/phase3_check_lib.py"), ("--self-test",)'
        )
        if expected not in issues:
            print("PHASE3_CATALOG_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected selftest driver marker was not reported")
            return 1

        _populate_repo(root)
        broken_path = root / MAKEFILE_PATH
        broken_path.write_text(
            _read(broken_path).replace(
                "$(PYTHON) scripts/zigux/run-phase3-checks.py --self-test",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "missing makefile marker: "
            "$(PYTHON) scripts/zigux/run-phase3-checks.py --self-test"
        )
        if expected not in issues:
            print("PHASE3_CATALOG_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected makefile run-phase3-checks marker was not reported")
            return 1

    print("PHASE3_CATALOG_SELFTEST_SURFACE_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the focused Phase 3 catalog selftest reminder surface."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the shared Phase 3 reminder files",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_CATALOG_SELFTEST_SURFACE=fail")
        for issue in issues:
            print(issue)
        return 1

    print(f"validated {args.repo_root / SCRIPTS_README_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
