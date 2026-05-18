#!/usr/bin/env python3
"""Fail-close the current Phase 3 scripts-root tooling inventory."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

SCRIPTS_README_PATH = Path("scripts/zigux/README.md")

RUNNER_FILE = Path("scripts/zigux/run-phase3-checks.py")
SHARED_TESTS_ROUTES_FILE = Path("scripts/zigux/check-phase3-shared-tests-routes.py")
BINDING_FILE = Path("zigux/bindings/dev_t.zig")
NOTIFIER_BINDING_FILE = Path("zigux/bindings/notifier_abi.zig")
NARROW_UNSAFE_FILE = Path("zigux/unsafe/narrow.zig")
UAPI_FILE = Path("zigux/uapi/dev_t.zig")
LOW_LEVEL_WRAPPER_SURVEY_VALIDATOR_FILE = Path(
    "scripts/zigux/validate-phase3-low-level-wrapper-survey.py"
)
LOW_LEVEL_WRAPPER_REPLAY_FILE = Path("zigux/tests/phase3_low_level_wrappers.zig")
LOW_LEVEL_WRAPPER_BUILD_FILE = Path("zigux/tests/phase3_low_level_wrappers_build.zig")
EXPORT_UAPI_LAYOUT_REPLAY_FILE = Path("zigux/tests/phase3_export_uapi_layout.zig")
EXPORT_UAPI_LAYOUT_BUILD_FILE = Path("zigux/tests/phase3_export_uapi_layout_build.zig")
WORKFLOW_FILE = Path(".github/workflows/zigux-bootstrap.yml")
POLICY_STARTER_BUILD_FILE = Path("zigux/tests/phase3_policy_starter_packet_build.zig")
XARRAY_SLOT_HELPER_FILE = Path("zigux/helpers/xarray_slot_view.zig")
XARRAY_SLOT_STARTER_FILE = Path("zigux/tests/phase3_xarray_slot_starter_packet.zig")
XARRAY_SLOT_STARTER_CHECK_FILE = Path(
    "scripts/zigux/check-phase3-xarray-slot-starter-packet.py"
)
XARRAY_SLOT_DUMP_FILE = Path("zigux/tests/phase3_xarray_slot_dump.zig")
XARRAY_SLOT_DUMP_BUILD_FILE = Path("zigux/tests/phase3_xarray_slot_dump_build.zig")
XARRAY_SLOT_EXPECTED_FILE = Path(
    "zigux/tests/fixtures/phase3_xarray_slot/expected.json"
)
XARRAY_SLOT_C_HARNESS_FILE = Path(
    "zigux/tests/fixtures/phase3_xarray_slot/phase3_xarray_slot_c_harness.c"
)
XARRAY_SLOT_MANIFEST_FILE = Path("zigux/tests/fixtures/phase3_xarray_slot_manifest.json")
XARRAY_SLOT_PACKET_CHECK_FILE = Path("scripts/zigux/check-phase3-xarray-slot.py")
SHARED_TESTS_BUILD_FILE = Path("zigux/tests/build.zig")
SHARED_VALIDATOR_FILE = Path("scripts/zigux/validate-phase3.py")

RUNNER_MARKER = "scripts/zigux/run-phase3-checks.py"
SHARED_TESTS_ROUTES_MARKER = "scripts/zigux/check-phase3-shared-tests-routes.py"
HEADER_MARKER = "include/linux/zigux.h"
UAPI_MARKER = "zigux/uapi/dev_t.zig"
NOTIFIER_BINDING_MARKER = "zigux/bindings/notifier_abi.zig"
LOW_LEVEL_WRAPPER_SURVEY_VALIDATOR_MARKER = (
    "scripts/zigux/validate-phase3-low-level-wrapper-survey.py"
)
LOW_LEVEL_WRAPPER_SURVEY_SELFTEST_MARKER = (
    "python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test"
)
LOW_LEVEL_WRAPPER_REPLAY_MARKER = "zigux/tests/phase3_low_level_wrappers.zig"
LOW_LEVEL_WRAPPER_BUILD_MARKER = "zigux/tests/phase3_low_level_wrappers_build.zig"
EXPORT_UAPI_LAYOUT_REPLAY_MARKER = "zigux/tests/phase3_export_uapi_layout.zig"
EXPORT_UAPI_LAYOUT_BUILD_MARKER = "zigux/tests/phase3_export_uapi_layout_build.zig"
EXPORT_UAPI_LAYOUT_BUILD_ROUTE_MARKER = (
    "zig build phase3-export-uapi-layout-test --build-file "
    "zigux/tests/phase3_export_uapi_layout_build.zig"
)
WORKFLOW_MARKER = ".github/workflows/zigux-bootstrap.yml"
CATALOG_SELFTEST_GAP_MARKER = "scripts/zigux/check-phase3-catalog-selftest.py"
CATALOG_WRAPPER_GAP_MARKER = "scripts/zigux/phase3_catalog.py"
WRAPPER_GENERATION_GAP_MARKER = "scripts/zigux/generate-phase3-check-wrappers.py"
SHARED_VALIDATOR_MARKER = "scripts/zigux/validate-phase3.py"
MANIFEST_ROOT_GAP_MARKER = "zigux/tests/phase3_abi_manifest.json"
XARRAY_SLOT_HELPER_MARKER = "zigux/helpers/xarray_slot_view.zig"
XARRAY_SLOT_STARTER_MARKER = "zigux/tests/phase3_xarray_slot_starter_packet.zig"
XARRAY_SLOT_STARTER_CHECK_MARKER = (
    "scripts/zigux/check-phase3-xarray-slot-starter-packet.py"
)
XARRAY_SLOT_DUMP_MARKER = "zigux/tests/phase3_xarray_slot_dump.zig"
XARRAY_SLOT_DUMP_BUILD_MARKER = "zigux/tests/phase3_xarray_slot_dump_build.zig"
XARRAY_SLOT_DUMP_BUILD_ROUTE_MARKER = (
    "zig build phase3-xarray-slot-dump --build-file "
    "zigux/tests/phase3_xarray_slot_dump_build.zig"
)
XARRAY_SLOT_EXPECTED_MARKER = "zigux/tests/fixtures/phase3_xarray_slot/expected.json"
XARRAY_SLOT_C_HARNESS_MARKER = (
    "zigux/tests/fixtures/phase3_xarray_slot/phase3_xarray_slot_c_harness.c"
)
XARRAY_SLOT_MANIFEST_MARKER = "zigux/tests/fixtures/phase3_xarray_slot_manifest.json"
XARRAY_SLOT_PACKET_CHECK_MARKER = "scripts/zigux/check-phase3-xarray-slot.py"
SHARED_TESTS_BUILD_MARKER = "zigux/tests/build.zig"
XARRAY_SLOT_BUILD_ROUTE_MARKER = (
    "zig build phase3-xarray-slot-starter-packet --build-file zigux/tests/build.zig"
)
README_GAP_SUMMARY_MARKER = (
    "so treat those catalog, wrapper-generation, closure, and manifest-root routes as current "
    "repo-reality gaps until fresh current-tree proof lands, while `scripts/zigux/validate-phase3.py` "
    "stays framed as the separately readable shared validator entrypoint rather than a missing "
    "scripts-root route"
)

REQUIRED_FILES = (
    Path("Documentation/zigux/phase3-abi-slice.md"),
    Path("Documentation/zigux/phase3-errptr-xarray-slice.md"),
    Path("Documentation/zigux/phase3-policy-slice.md"),
    Path("Documentation/zigux/phase3-validator-support-surface.md"),
    Path("Documentation/zigux/phase3-boundary-lane-sequencing.md"),
    Path("Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md"),
    Path("include/linux/zigux.h"),
    Path("include/zigux/dev_t.h"),
    Path("include/zigux/abi.h"),
    Path("scripts/zigux/check-phase3-selftest-surface.py"),
    SHARED_TESTS_ROUTES_FILE,
    Path("scripts/zigux/validate-phase3-validator-support-surface.py"),
    Path("scripts/zigux/validate_phase3_selftest.py"),
    RUNNER_FILE,
    SHARED_VALIDATOR_FILE,
    Path("scripts/zigux/check-phase3-dev-t-starter-packet.py"),
    Path("scripts/zigux/check-phase3-errptr-xarray-starter-packet.py"),
    XARRAY_SLOT_STARTER_CHECK_FILE,
    XARRAY_SLOT_PACKET_CHECK_FILE,
    Path("scripts/zigux/check-phase3-policy-starter-packet.py"),
    LOW_LEVEL_WRAPPER_SURVEY_VALIDATOR_FILE,
    BINDING_FILE,
    Path("zigux/bindings/version.zig"),
    Path("zigux/bindings/abi.zig"),
    NOTIFIER_BINDING_FILE,
    Path("zigux/helpers/err_ptr.zig"),
    Path("zigux/helpers/xa_value.zig"),
    XARRAY_SLOT_HELPER_FILE,
    Path("zigux/helpers/panic_policy.zig"),
    Path("zigux/helpers/allocator_policy.zig"),
    Path("zigux/helpers/unsafe_policy.zig"),
    Path("zigux/helpers/atomic.zig"),
    Path("zigux/helpers/barrier.zig"),
    Path("zigux/helpers/mmio.zig"),
    NARROW_UNSAFE_FILE,
    Path("zigux/kernel/export_shim.zig"),
    UAPI_FILE,
    Path("zigux/uapi/version.zig"),
    Path("zigux/tests/phase3_dev_t_starter_packet.zig"),
    Path("zigux/tests/phase3_dev_t_starter_packet_build.zig"),
    Path("zigux/tests/phase3_errptr_xarray_starter_packet.zig"),
    Path("zigux/tests/phase3_errptr_xarray_starter_packet_build.zig"),
    XARRAY_SLOT_STARTER_FILE,
    XARRAY_SLOT_DUMP_FILE,
    XARRAY_SLOT_DUMP_BUILD_FILE,
    XARRAY_SLOT_EXPECTED_FILE,
    XARRAY_SLOT_C_HARNESS_FILE,
    XARRAY_SLOT_MANIFEST_FILE,
    SHARED_TESTS_BUILD_FILE,
    Path("zigux/tests/phase3_policy_starter_packet.zig"),
    POLICY_STARTER_BUILD_FILE,
    LOW_LEVEL_WRAPPER_REPLAY_FILE,
    LOW_LEVEL_WRAPPER_BUILD_FILE,
    EXPORT_UAPI_LAYOUT_REPLAY_FILE,
    EXPORT_UAPI_LAYOUT_BUILD_FILE,
    WORKFLOW_FILE,
)

REQUIRED_MARKERS = (
    "Documentation/zigux/phase3-abi-slice.md",
    "Documentation/zigux/phase3-errptr-xarray-slice.md",
    "Documentation/zigux/phase3-policy-slice.md",
    "Documentation/zigux/phase3-validator-support-surface.md",
    "python3 scripts/zigux/check-phase3-readme-tooling-inventory.py --self-test",
    "python3 scripts/zigux/check-phase3-readme-tooling-inventory.py",
    "scripts/zigux/check-phase3-selftest-surface.py",
    "scripts/zigux/check-phase3-shared-tests-routes.py",
    "scripts/zigux/validate-phase3-validator-support-surface.py",
    "scripts/zigux/validate_phase3_selftest.py",
    "scripts/zigux/run-phase3-checks.py",
    "scripts/zigux/validate-phase3.py",
    "scripts/zigux/check-phase3-dev-t-starter-packet.py",
    "scripts/zigux/check-phase3-errptr-xarray-starter-packet.py",
    "scripts/zigux/check-phase3-xarray-slot-starter-packet.py",
    "scripts/zigux/check-phase3-xarray-slot.py",
    "scripts/zigux/check-phase3-policy-starter-packet.py",
    "scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    "Documentation/zigux/phase3-boundary-lane-sequencing.md",
    "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md",
    "include/linux/zigux.h",
    "include/zigux/dev_t.h",
    "include/zigux/abi.h",
    "zigux/helpers/err_ptr.zig",
    "zigux/helpers/xa_value.zig",
    "zigux/helpers/xarray_slot_view.zig",
    "zigux/helpers/panic_policy.zig",
    "zigux/helpers/allocator_policy.zig",
    "zigux/helpers/unsafe_policy.zig",
    "zigux/helpers/atomic.zig",
    "zigux/helpers/barrier.zig",
    "zigux/helpers/mmio.zig",
    "zigux/kernel/export_shim.zig",
    "zigux/bindings/dev_t.zig",
    "zigux/bindings/version.zig",
    "zigux/bindings/abi.zig",
    "zigux/bindings/notifier_abi.zig",
    "zigux/unsafe/narrow.zig",
    "zigux/uapi/dev_t.zig",
    "zigux/uapi/version.zig",
    "zigux/tests/phase3_dev_t_starter_packet.zig",
    "zigux/tests/phase3_dev_t_starter_packet_build.zig",
    "zigux/tests/phase3_errptr_xarray_starter_packet.zig",
    "zigux/tests/phase3_errptr_xarray_starter_packet_build.zig",
    "zigux/tests/phase3_xarray_slot_starter_packet.zig",
    "zigux/tests/phase3_xarray_slot_dump.zig",
    "zigux/tests/phase3_xarray_slot_dump_build.zig",
    "zigux/tests/fixtures/phase3_xarray_slot/phase3_xarray_slot_c_harness.c",
    "zigux/tests/fixtures/phase3_xarray_slot/expected.json",
    "zigux/tests/fixtures/phase3_xarray_slot_manifest.json",
    "zigux/tests/build.zig",
    "zig build phase3-xarray-slot-starter-packet --build-file zigux/tests/build.zig",
    "zig build phase3-xarray-slot-dump --build-file zigux/tests/phase3_xarray_slot_dump_build.zig",
    "zigux/tests/phase3_policy_starter_packet.zig",
    "zigux/tests/phase3_policy_starter_packet_build.zig",
    "zigux/tests/phase3_low_level_wrappers.zig",
    "zigux/tests/phase3_low_level_wrappers_build.zig",
    "zigux/tests/phase3_export_uapi_layout.zig",
    "zigux/tests/phase3_export_uapi_layout_build.zig",
    "zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
    ".github/workflows/zigux-bootstrap.yml",
    LOW_LEVEL_WRAPPER_SURVEY_SELFTEST_MARKER,
    CATALOG_SELFTEST_GAP_MARKER,
    CATALOG_WRAPPER_GAP_MARKER,
    WRAPPER_GENERATION_GAP_MARKER,
    SHARED_VALIDATOR_MARKER,
    MANIFEST_ROOT_GAP_MARKER,
    README_GAP_SUMMARY_MARKER,
)

README_MARKER_CASES = (
    (RUNNER_MARKER, "expected missing runner README marker was not reported"),
    (SHARED_TESTS_ROUTES_MARKER, "expected missing shared-tests-routes README marker was not reported"),
    (HEADER_MARKER, "expected missing header README marker was not reported"),
    (UAPI_MARKER, "expected missing UAPI README marker was not reported"),
    (NOTIFIER_BINDING_MARKER, "expected missing notifier-binding README marker was not reported"),
    (LOW_LEVEL_WRAPPER_SURVEY_VALIDATOR_MARKER, "expected missing low-level-wrapper survey validator README marker was not reported"),
    (LOW_LEVEL_WRAPPER_SURVEY_SELFTEST_MARKER, "expected missing low-level-wrapper survey self-test README marker was not reported"),
    (LOW_LEVEL_WRAPPER_REPLAY_MARKER, "expected missing low-level-wrapper replay README marker was not reported"),
    (LOW_LEVEL_WRAPPER_BUILD_MARKER, "expected missing low-level-wrapper build README marker was not reported"),
    (EXPORT_UAPI_LAYOUT_REPLAY_MARKER, "expected missing export-uapi-layout replay README marker was not reported"),
    (EXPORT_UAPI_LAYOUT_BUILD_MARKER, "expected missing export-uapi-layout build README marker was not reported"),
    (EXPORT_UAPI_LAYOUT_BUILD_ROUTE_MARKER, "expected missing export-uapi-layout build-route README marker was not reported"),
    (WORKFLOW_MARKER, "expected missing workflow README marker was not reported"),
    (CATALOG_SELFTEST_GAP_MARKER, "expected missing catalog-selftest gap README marker was not reported"),
    (CATALOG_WRAPPER_GAP_MARKER, "expected missing catalog wrapper gap README marker was not reported"),
    (WRAPPER_GENERATION_GAP_MARKER, "expected missing wrapper-generation gap README marker was not reported"),
    (SHARED_VALIDATOR_MARKER, "expected missing shared validator README marker was not reported"),
    (MANIFEST_ROOT_GAP_MARKER, "expected missing manifest-root gap README marker was not reported"),
    (XARRAY_SLOT_HELPER_MARKER, "expected missing xarray-slot helper README marker was not reported"),
    (XARRAY_SLOT_STARTER_MARKER, "expected missing xarray-slot starter README marker was not reported"),
    (XARRAY_SLOT_STARTER_CHECK_MARKER, "expected missing xarray-slot starter checker README marker was not reported"),
    (XARRAY_SLOT_DUMP_MARKER, "expected missing xarray-slot dump README marker was not reported"),
    (XARRAY_SLOT_DUMP_BUILD_MARKER, "expected missing xarray-slot dump build README marker was not reported"),
    (XARRAY_SLOT_DUMP_BUILD_ROUTE_MARKER, "expected missing xarray-slot dump build-route README marker was not reported"),
    (XARRAY_SLOT_EXPECTED_MARKER, "expected missing xarray-slot expected fixture README marker was not reported"),
    (XARRAY_SLOT_C_HARNESS_MARKER, "expected missing xarray-slot C harness README marker was not reported"),
    (XARRAY_SLOT_MANIFEST_MARKER, "expected missing xarray-slot manifest README marker was not reported"),
    (XARRAY_SLOT_PACKET_CHECK_MARKER, "expected missing xarray-slot packet checker README marker was not reported"),
    (SHARED_TESTS_BUILD_MARKER, "expected missing shared tests build README marker was not reported"),
    (XARRAY_SLOT_BUILD_ROUTE_MARKER, "expected missing xarray-slot build-route README marker was not reported"),
    (README_GAP_SUMMARY_MARKER, "expected missing repo-reality gap summary README marker was not reported"),
)

FILE_CASES = (
    (RUNNER_FILE, "expected missing runner file was not reported"),
    (SHARED_TESTS_ROUTES_FILE, "expected missing shared-tests-routes file was not reported"),
    (BINDING_FILE, "expected missing binding file was not reported"),
    (NOTIFIER_BINDING_FILE, "expected missing notifier-binding file was not reported"),
    (NARROW_UNSAFE_FILE, "expected missing narrow-unsafe file was not reported"),
    (UAPI_FILE, "expected missing UAPI file was not reported"),
    (LOW_LEVEL_WRAPPER_SURVEY_VALIDATOR_FILE, "expected missing low-level-wrapper survey validator file was not reported"),
    (LOW_LEVEL_WRAPPER_REPLAY_FILE, "expected missing low-level-wrapper replay file was not reported"),
    (LOW_LEVEL_WRAPPER_BUILD_FILE, "expected missing low-level-wrapper build file was not reported"),
    (EXPORT_UAPI_LAYOUT_REPLAY_FILE, "expected missing export-uapi-layout replay file was not reported"),
    (EXPORT_UAPI_LAYOUT_BUILD_FILE, "expected missing export-uapi-layout build file was not reported"),
    (WORKFLOW_FILE, "expected missing workflow file was not reported"),
    (POLICY_STARTER_BUILD_FILE, "expected missing starter build file was not reported"),
    (XARRAY_SLOT_HELPER_FILE, "expected missing xarray-slot helper file was not reported"),
    (XARRAY_SLOT_STARTER_FILE, "expected missing xarray-slot starter file was not reported"),
    (XARRAY_SLOT_STARTER_CHECK_FILE, "expected missing xarray-slot starter checker file was not reported"),
    (XARRAY_SLOT_DUMP_FILE, "expected missing xarray-slot dump file was not reported"),
    (XARRAY_SLOT_DUMP_BUILD_FILE, "expected missing xarray-slot dump build file was not reported"),
    (XARRAY_SLOT_EXPECTED_FILE, "expected missing xarray-slot expected fixture file was not reported"),
    (XARRAY_SLOT_C_HARNESS_FILE, "expected missing xarray-slot C harness file was not reported"),
    (XARRAY_SLOT_MANIFEST_FILE, "expected missing xarray-slot manifest file was not reported"),
    (XARRAY_SLOT_PACKET_CHECK_FILE, "expected missing xarray-slot packet checker file was not reported"),
    (SHARED_TESTS_BUILD_FILE, "expected missing shared tests build file was not reported"),
    (SHARED_VALIDATOR_FILE, "expected missing shared validator file was not reported"),
    (Path("Documentation/zigux/phase3-policy-slice.md"), "expected missing policy-slice file was not reported"),
    (Path("Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md"), "expected missing low-level-wrapper survey note was not reported"),
    (Path("include/zigux/abi.h"), "expected missing ABI header file was not reported"),
    (Path("zigux/helpers/unsafe_policy.zig"), "expected missing unsafe-policy helper file was not reported"),
    (Path("zigux/helpers/atomic.zig"), "expected missing atomic helper file was not reported"),
    (Path("zigux/helpers/barrier.zig"), "expected missing barrier helper file was not reported"),
    (Path("zigux/helpers/mmio.zig"), "expected missing MMIO helper file was not reported"),
    (Path("zigux/kernel/export_shim.zig"), "expected missing export-shim file was not reported"),
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (repo_root / rel_path).is_file():
            issues.append(f"missing repo file: {rel_path.as_posix()}")

    readme_path = repo_root / SCRIPTS_README_PATH
    try:
        readme_text = _read(readme_path)
    except FileNotFoundError:
        return issues + [f"missing repo file: {SCRIPTS_README_PATH.as_posix()}"]

    for marker in REQUIRED_MARKERS:
        if marker not in readme_text:
            issues.append(f"missing scripts README marker: {marker}")
    return issues


def _populate_repo(root: Path) -> None:
    for rel_path in REQUIRED_FILES:
        _write(root / rel_path, rel_path.as_posix() + "\n")
    _write(root / SCRIPTS_README_PATH, "\n".join(REQUIRED_MARKERS) + "\n")


def _expect_missing_marker(root: Path, marker: str, message: str) -> int:
    readme = root / SCRIPTS_README_PATH
    readme.write_text(_read(readme).replace(marker, ""), encoding="utf-8")
    issues = validate_repo(root)
    expected = f"missing scripts README marker: {marker}"
    if expected not in issues:
        print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
        print(message)
        return 1
    return 0


def _expect_missing_file(root: Path, rel_path: Path, message: str) -> int:
    (root / rel_path).unlink()
    issues = validate_repo(root)
    expected = f"missing repo file: {rel_path.as_posix()}"
    if expected not in issues:
        print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
        print(message)
        return 1
    return 0


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_readme_tooling_inventory_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for marker, message in README_MARKER_CASES:
            _populate_repo(root)
            if _expect_missing_marker(root, marker, message) != 0:
                return 1

        for rel_path, message in FILE_CASES:
            _populate_repo(root)
            if _expect_missing_file(root, rel_path, message) != 0:
                return 1

        print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=pass")
        print(
            "PHASE3_README_TOOLING_INVENTORY_SELF_TEST_CASE_COUNT="
            f"{1 + len(README_MARKER_CASES) + len(FILE_CASES)}"
        )
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 3 scripts-root tooling inventory."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains scripts/zigux/README.md",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_README_TOOLING_INVENTORY=fail")
        print("\n".join(issues))
        return 1

    print(f"validated {args.repo_root / SCRIPTS_README_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
