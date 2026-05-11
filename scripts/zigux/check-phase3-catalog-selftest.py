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
CHECKLIST_MARKERS = (
    "scripts/zigux/check-phase3-catalog-selftest.py",
    "python3 scripts/zigux/phase3_catalog.py --audit-doc-sync",
    "make -C zigux phase3-selftest",
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
SCRIPTS_README_MARKERS = (
    "check-phase3-catalog-selftest.py",
    "phase3_catalog.py",
    "phase3_check_lib.py",
    "generate-phase3-check-wrappers.py",
    "run-phase3-checks.py",
    "python3 scripts/zigux/phase3_catalog.py --self-test",
    "python3 scripts/zigux/phase3_catalog.py --audit-doc-sync",
)
SELFTEST_DRIVER_MARKERS = (
    'Path("scripts/zigux/check-phase3-catalog-selftest.py")',
    'Path("scripts/zigux/phase3_catalog.py"), ("--self-test",)',
)
MAKEFILE_MARKERS = (
    "phase3-validate:",
    "$(PYTHON) scripts/zigux/check-phase3-catalog-selftest.py --self-test",
    "$(PYTHON) scripts/zigux/phase3_catalog.py --self-test",
    "$(PYTHON) scripts/zigux/phase3_catalog.py --audit-doc-sync",
    "$(PYTHON) scripts/zigux/generate-phase3-check-wrappers.py --check",
    "phase3-selftest:",
)


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


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    issues.extend(
        _check_markers(repo_root / DOCS_README_PATH, DOCS_README_MARKERS, "docs README")
    )
    issues.extend(
        _check_markers(repo_root / CHECKLIST_PATH, CHECKLIST_MARKERS, "review checklist")
    )
    issues.extend(
        _check_markers(repo_root / TESTS_README_PATH, TESTS_README_MARKERS, "tests README")
    )
    issues.extend(
        _check_markers(
            repo_root / SCRIPTS_README_PATH, SCRIPTS_README_MARKERS, "scripts README"
        )
    )
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
    _write(root / DOCS_README_PATH, "\n".join(DOCS_README_MARKERS) + "\n")
    _write(root / CHECKLIST_PATH, "\n".join(CHECKLIST_MARKERS) + "\n")
    _write(root / TESTS_README_PATH, "\n".join(TESTS_README_MARKERS) + "\n")
    _write(root / SCRIPTS_README_PATH, "\n".join(SCRIPTS_README_MARKERS) + "\n")
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
            "missing docs README marker: "
            "python3 scripts/zigux/phase3_catalog.py --self-test"
        )
        if expected not in issues:
            print("PHASE3_CATALOG_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected docs README self-test marker was not reported")
            return 1

        _populate_repo(root)
        broken_path = root / TESTS_README_PATH
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
            "missing tests README marker: "
            "scripts/zigux/generate-phase3-check-wrappers.py --check"
        )
        if expected not in issues:
            print("PHASE3_CATALOG_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected tests README wrapper-check marker was not reported")
            return 1

        _populate_repo(root)
        broken_path = root / SELFTEST_DRIVER_PATH
        broken_path.write_text(
            _read(broken_path).replace(
                'Path("scripts/zigux/check-phase3-catalog-selftest.py")',
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "missing selftest driver marker: "
            'Path("scripts/zigux/check-phase3-catalog-selftest.py")'
        )
        if expected not in issues:
            print("PHASE3_CATALOG_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected selftest driver marker was not reported")
            return 1

        _populate_repo(root)
        broken_path = root / MAKEFILE_PATH
        broken_path.write_text(
            _read(broken_path).replace(
                "$(PYTHON) scripts/zigux/phase3_catalog.py --audit-doc-sync",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "missing makefile marker: "
            "$(PYTHON) scripts/zigux/phase3_catalog.py --audit-doc-sync"
        )
        if expected not in issues:
            print("PHASE3_CATALOG_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected makefile audit-doc-sync marker was not reported")
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
