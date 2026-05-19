#!/usr/bin/env python3
"""Fail-close the current Phase 3 catalog selftest guard."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

CATALOG_PATH = Path("scripts/zigux/phase3_catalog.py")
SURVEY_PATH = Path("Documentation/zigux/phase3-export-uapi-boundary-survey.md")
EXPORT_UAPI_VALIDATOR_PATH = Path("scripts/zigux/validate-phase3-export-uapi-survey.py")

REQUIRED_MARKERS = {
    CATALOG_PATH: (
        'PHASE3_CATALOG_PHASE = "Phase 3"',
        'PHASE3_CATALOG_SCOPE = "abi-runtime"',
        'Path("Documentation/zigux/phase3-export-uapi-boundary-survey.md")',
        '"python3 scripts/zigux/validate-phase3-export-uapi-survey.py --self-test"',
        '"python3 scripts/zigux/validate-phase3-export-uapi-survey.py"',
        '"zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig"',
        'print("PHASE3_CATALOG_SELF_TEST=pass")',
    ),
    SURVEY_PATH: (
        "PHASE3_EXPORT_UAPI_CATALOG_SELFTEST_GUARD=scripts/zigux/check-phase3-catalog-selftest.py",
        "Current `master` no longer shows a separate packet-local repo-reality gap for this starter export/UAPI packet.",
    ),
    EXPORT_UAPI_VALIDATOR_PATH: (
        'CATALOG_SELFTEST_CHECK_PATH = Path("scripts/zigux/check-phase3-catalog-selftest.py")',
        'print("PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=pass")',
    ),
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    for relative_path, markers in REQUIRED_MARKERS.items():
        path = repo_root / relative_path
        try:
            text = _read(path)
        except FileNotFoundError:
            issues.append(f"missing repo file: {relative_path.as_posix()}")
            continue
        for marker in markers:
            if marker not in text:
                issues.append(f"missing {relative_path.as_posix()} marker: {marker}")
    return issues


def _populate_repo(root: Path) -> None:
    for relative_path, markers in REQUIRED_MARKERS.items():
        _write(root / relative_path, "\n".join(markers) + "\n")


def _expect_missing_marker(
    root: Path, relative_path: Path, marker: str, message: str
) -> int:
    path = root / relative_path
    path.write_text(_read(path).replace(marker, "", 1), encoding="utf-8")
    issues = validate_repo(root)
    expected = f"missing {relative_path.as_posix()} marker: {marker}"
    if expected not in issues:
        print("PHASE3_CATALOG_SELFTEST_CHECK_SELF_TEST=fail")
        print(message)
        return 1
    return 0


def run_self_test() -> int:
    marker_cases = (
        (
            CATALOG_PATH,
            '"python3 scripts/zigux/validate-phase3-export-uapi-survey.py --self-test"',
            "expected missing catalog export-uapi self-test route marker was not reported",
        ),
        (
            CATALOG_PATH,
            '"zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig"',
            "expected missing catalog export-uapi layout route marker was not reported",
        ),
        (
            SURVEY_PATH,
            "PHASE3_EXPORT_UAPI_CATALOG_SELFTEST_GUARD=scripts/zigux/check-phase3-catalog-selftest.py",
            "expected missing survey catalog-selftest guard marker was not reported",
        ),
        (
            EXPORT_UAPI_VALIDATOR_PATH,
            'CATALOG_SELFTEST_CHECK_PATH = Path("scripts/zigux/check-phase3-catalog-selftest.py")',
            "expected missing export-uapi validator catalog-selftest marker was not reported",
        ),
    )

    with tempfile.TemporaryDirectory(prefix="zigux_phase3_catalog_selftest_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_CATALOG_SELFTEST_CHECK_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for relative_path, marker, message in marker_cases:
            _populate_repo(root)
            if _expect_missing_marker(root, relative_path, marker, message) != 0:
                return 1

    print("PHASE3_CATALOG_SELFTEST_CHECK_SELF_TEST=pass")
    print(f"PHASE3_CATALOG_SELFTEST_CHECK_SELF_TEST_CASE_COUNT={1 + len(marker_cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 3 catalog selftest guard."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the Phase 3 catalog helper packet",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_CATALOG_SELFTEST_CHECK=fail")
        print("\n".join(issues))
        return 1

    print(f"validated {args.repo_root / CATALOG_PATH}")
    print("PHASE3_CATALOG_SELFTEST_CHECK=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
