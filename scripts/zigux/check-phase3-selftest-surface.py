#!/usr/bin/env python3
"""Fail-close the shared Phase 3 selftest reminder surface."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


README_PATH = Path("Documentation/zigux/README.md")
TESTS_README_PATH = Path("zigux/tests/README.md")
REVIEW_CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")
VALIDATOR_SUPPORT_PATH = Path("Documentation/zigux/phase3-validator-support-surface.md")
SCRIPTS_README_PATH = Path("scripts/zigux/README.md")
SELFTEST_DRIVER_PATH = Path("scripts/zigux/validate_phase3_selftest.py")

README_MARKERS = (
    "Documentation/zigux/phase3-abi-slice.md",
    "Documentation/zigux/phase3-errptr-xarray-slice.md",
    "Documentation/zigux/phase3-validator-support-surface.md",
    "Documentation/zigux/phase3-shared-reminder-gap.md",
    "include/linux/zigux.h",
    "include/zigux/dev_t.h",
    "zigux/uapi/version.zig",
    "zigux/uapi/dev_t.zig",
    "zigux/bindings/dev_t.zig",
    "zigux/helpers/err_ptr.zig",
    "zigux/helpers/xa_value.zig",
    "zigux/tests/phase3_dev_t_starter_packet.zig",
    "zigux/tests/phase3_errptr_xarray_starter_packet.zig",
    "scripts/zigux/check-phase3-dev-t-starter-packet.py",
    "scripts/zigux/check-phase3-errptr-xarray-starter-packet.py",
)

TESTS_README_MARKERS = (
    "Documentation/zigux/phase3-abi-slice.md",
    "Documentation/zigux/phase3-errptr-xarray-slice.md",
    "Documentation/zigux/phase3-validator-support-surface.md",
    "include/linux/zigux.h",
    "include/zigux/dev_t.h",
    "zigux/uapi/version.zig",
    "zigux/uapi/dev_t.zig",
    "zigux/bindings/dev_t.zig",
    "zigux/helpers/err_ptr.zig",
    "zigux/helpers/xa_value.zig",
    "scripts/zigux/check-phase3-dev-t-starter-packet.py",
    "scripts/zigux/check-phase3-errptr-xarray-starter-packet.py",
    "Documentation/zigux/phase3-abi-header-family-survey.md",
    "zigux/kernel/export_shim.zig",
    "scripts/zigux/validate-phase3-export-uapi-survey.py",
)

REVIEW_CHECKLIST_MARKERS = (
    "Documentation/zigux/phase3-abi-slice.md",
    "Documentation/zigux/phase3-errptr-xarray-slice.md",
    "Documentation/zigux/phase3-validator-support-surface.md",
    "include/linux/zigux.h",
    "include/zigux/dev_t.h",
    "zigux/uapi/version.zig",
    "zigux/uapi/dev_t.zig",
    "zigux/bindings/dev_t.zig",
    "zigux/helpers/err_ptr.zig",
    "zigux/helpers/xa_value.zig",
    "scripts/zigux/check-phase3-dev-t-starter-packet.py",
    "scripts/zigux/check-phase3-errptr-xarray-starter-packet.py",
    "repo-reality gaps rather than shipped current-`master` evidence",
)

VALIDATOR_SUPPORT_MARKERS = (
    "Documentation/zigux/phase3-abi-slice.md",
    "Documentation/zigux/phase3-errptr-xarray-slice.md",
    "Documentation/zigux/phase3-policy-slice.md",
    "scripts/zigux/check-phase3-dev-t-starter-packet.py",
    "scripts/zigux/check-phase3-errptr-xarray-starter-packet.py",
    "scripts/zigux/check-phase3-policy-starter-packet.py",
    "zig build phase3-dev-t-starter-packet-test --build-file zigux/tests/phase3_dev_t_starter_packet_build.zig --summary all",
    "zig build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig",
    "scripts/zigux/validate-phase3-export-uapi-survey.py",
    "zigux/tests/phase3_export_uapi_layout.zig",
    "zigux/tests/phase3_export_uapi_layout_build.zig",
    "zigux/kernel/export_shim.zig",
    "Documentation/zigux/phase3-shared-reminder-gap.md",
    "scripts/zigux/validate-phase3-validator-support-surface.py",
)

SCRIPTS_README_MARKERS = (
    "scripts/zigux/check-phase3-selftest-surface.py",
    "scripts/zigux/validate-phase3-validator-support-surface.py",
    "scripts/zigux/phase3_catalog.py",
    "scripts/zigux/generate-phase3-check-wrappers.py",
    "scripts/zigux/run-phase3-checks.py",
    "Documentation/zigux/phase3-boundary-lane-sequencing.md",
    "scripts/zigux/validate-phase3-abi-bindings-syntax.py",
    "scripts/zigux/check-phase3-abi-dump-gate.py",
    "scripts/zigux/check-phase3-policy-byte-guards.py",
    "scripts/zigux/check-phase3-policy-unsafe-focused-replay.py",
    "scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py",
    "include/linux/zigux.h",
    "include/zigux/dev_t.h",
    "zigux/uapi/version.zig",
    "zigux/uapi/dev_t.zig",
    "zigux/helpers/err_ptr.zig",
    "zigux/helpers/xa_value.zig",
    "zigux/kernel/export_shim.zig",
    "scripts/zigux/validate-phase3-export-uapi-survey.py",
    "zigux/tests/phase3_export_uapi_layout.zig",
)

SELFTEST_DRIVER_MARKERS = (
    'Path("scripts/zigux/check-phase3-dev-t-starter-packet.py")',
    'Path("scripts/zigux/check-phase3-errptr-xarray-starter-packet.py")',
    'Path("scripts/zigux/check-phase3-policy-starter-packet.py")',
    'Path("scripts/zigux/validate-phase3-low-level-wrapper-survey.py")',
    'Path("scripts/zigux/validate-phase3-validator-support-surface.py")',
    'Path("scripts/zigux/check-phase3-selftest-surface.py")',
    "PHASE3_VALIDATE_SELFTEST=pass",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _check_markers(path: Path, markers: tuple[str, ...], label: str) -> list[str]:
    try:
        text = _read(path)
    except FileNotFoundError:
        return [f"missing repo file: {path.as_posix()}"]
    return [f"missing {label} marker: {marker}" for marker in markers if marker not in text]


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    issues.extend(_check_markers(repo_root / README_PATH, README_MARKERS, "docs README"))
    issues.extend(_check_markers(repo_root / TESTS_README_PATH, TESTS_README_MARKERS, "tests README"))
    issues.extend(
        _check_markers(repo_root / REVIEW_CHECKLIST_PATH, REVIEW_CHECKLIST_MARKERS, "review checklist")
    )
    issues.extend(
        _check_markers(
            repo_root / VALIDATOR_SUPPORT_PATH,
            VALIDATOR_SUPPORT_MARKERS,
            "validator-support note",
        )
    )
    issues.extend(
        _check_markers(repo_root / SCRIPTS_README_PATH, SCRIPTS_README_MARKERS, "scripts README")
    )
    issues.extend(
        _check_markers(repo_root / SELFTEST_DRIVER_PATH, SELFTEST_DRIVER_MARKERS, "selftest driver")
    )
    return issues


def _populate_repo(root: Path) -> None:
    _write(root / README_PATH, "\n".join(README_MARKERS) + "\n")
    _write(root / TESTS_README_PATH, "\n".join(TESTS_README_MARKERS) + "\n")
    _write(root / REVIEW_CHECKLIST_PATH, "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n")
    _write(root / VALIDATOR_SUPPORT_PATH, "\n".join(VALIDATOR_SUPPORT_MARKERS) + "\n")
    _write(root / SCRIPTS_README_PATH, "\n".join(SCRIPTS_README_MARKERS) + "\n")
    _write(root / SELFTEST_DRIVER_PATH, "\n".join(SELFTEST_DRIVER_MARKERS) + "\n")


def _expect_issue(issues: list[str], expected: str) -> bool:
    return expected in issues


def run_self_test() -> int:
    cases = (
        (README_PATH, README_MARKERS[0], "docs README"),
        (TESTS_README_PATH, TESTS_README_MARKERS[-1], "tests README"),
        (REVIEW_CHECKLIST_PATH, REVIEW_CHECKLIST_MARKERS[-1], "review checklist"),
        (VALIDATOR_SUPPORT_PATH, VALIDATOR_SUPPORT_MARKERS[-1], "validator-support note"),
        (SCRIPTS_README_PATH, SCRIPTS_README_MARKERS[0], "scripts README"),
        (SELFTEST_DRIVER_PATH, SELFTEST_DRIVER_MARKERS[3], "selftest driver"),
        (SELFTEST_DRIVER_PATH, SELFTEST_DRIVER_MARKERS[5], "selftest driver"),
    )

    with tempfile.TemporaryDirectory(prefix="zigux_phase3_selftest_surface_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for path, marker, label in cases:
            _populate_repo(root)
            file_path = root / path
            file_path.write_text(_read(file_path).replace(marker, "", 1), encoding="utf-8")
            issues = validate_repo(root)
            expected = f"missing {label} marker: {marker}"
            if not _expect_issue(issues, expected):
                print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
                print(f"expected missing marker was not reported: {expected}")
                return 1

    print("PHASE3_SELFTEST_SURFACE_SELF_TEST=pass")
    print("PHASE3_SELFTEST_SURFACE_SELF_TEST_CASE_COUNT=7")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the shared Phase 3 selftest reminder surface."
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
        print("PHASE3_SELFTEST_SURFACE=fail")
        for issue in issues:
            print(issue)
        return 1

    print(f"validated {args.repo_root / SCRIPTS_README_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())