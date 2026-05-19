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
    "Documentation/zigux/phase3-policy-slice.md",
    "Documentation/zigux/phase3-validator-support-surface.md",
    "Documentation/zigux/phase3-shared-reminder-gap.md",
    "Documentation/zigux/phase3-kernel-export-shim-governance.md",
    "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md",
    "include/linux/zigux.h",
    "include/zigux/dev_t.h",
    "include/zigux/abi.h",
    "zigux/uapi/version.zig",
    "zigux/uapi/dev_t.zig",
    "zigux/bindings/abi.zig",
    "zigux/bindings/dev_t.zig",
    "zigux/bindings/version.zig",
    "zigux/bindings/notifier_abi.zig",
    "zigux/kernel/export_shim.zig",
    "zigux/helpers/err_ptr.zig",
    "zigux/helpers/xa_value.zig",
    "zigux/helpers/panic_policy.zig",
    "zigux/helpers/allocator_policy.zig",
    "zigux/helpers/unsafe_policy.zig",
    "zigux/helpers/atomic.zig",
    "zigux/helpers/barrier.zig",
    "zigux/helpers/mmio.zig",
    "zigux/unsafe/narrow.zig",
    "zigux/tests/phase3_dev_t_starter_packet.zig",
    "zigux/tests/phase3_dev_t_starter_packet_build.zig",
    "zigux/tests/phase3_dev_t_starter_packet_manifest.json",
    "zigux/tests/phase3_errptr_xarray_starter_packet.zig",
    "zigux/tests/phase3_errptr_xarray_starter_packet_build.zig",
    "zigux/tests/phase3_policy_starter_packet.zig",
    "zigux/tests/phase3_policy_starter_packet_build.zig",
    "zigux/tests/phase3_policy_starter_packet_manifest.json",
    "zigux/tests/phase3_low_level_wrappers.zig",
    "zigux/tests/phase3_low_level_wrappers_build.zig",
    "zigux/tests/phase3_export_uapi_layout.zig",
    "zigux/tests/phase3_export_uapi_layout_build.zig",
    "scripts/zigux/check-phase3-dev-t-starter-packet.py",
    "scripts/zigux/check-phase3-errptr-xarray-starter-packet.py",
    "scripts/zigux/check-phase3-policy-starter-packet.py",
    "scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    "zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    "make -C zigux phase3-export-uapi-layout-test",
    "Documentation/zigux/phase3-export-uapi-boundary-survey.md",
    "Documentation/zigux/phase3-linux-zigux-header-governance.md",
    "scripts/zigux/validate-phase3-export-uapi-survey.py",
    "zigux/tests/fixtures/phase3_abi_manifest.json",
)

TESTS_README_MARKERS = (
    "Documentation/zigux/phase3-abi-slice.md",
    "Documentation/zigux/phase3-errptr-xarray-slice.md",
    "Documentation/zigux/phase3-policy-slice.md",
    "Documentation/zigux/phase3-validator-support-surface.md",
    "Documentation/zigux/phase3-export-uapi-boundary-survey.md",
    "include/linux/zigux.h",
    "include/zigux/dev_t.h",
    "include/zigux/abi.h",
    "zigux/uapi/version.zig",
    "zigux/uapi/dev_t.zig",
    "zigux/bindings/dev_t.zig",
    "zigux/bindings/abi.zig",
    "zigux/helpers/err_ptr.zig",
    "zigux/helpers/xa_value.zig",
    "zigux/helpers/panic_policy.zig",
    "zigux/helpers/allocator_policy.zig",
    "zigux/helpers/unsafe_policy.zig",
    "zigux/tests/phase3_dev_t_starter_packet.zig",
    "zigux/tests/phase3_dev_t_starter_packet_build.zig",
    "zigux/tests/phase3_errptr_xarray_starter_packet.zig",
    "zigux/tests/phase3_errptr_xarray_starter_packet_build.zig",
    "zigux/tests/phase3_policy_starter_packet.zig",
    "zigux/tests/phase3_policy_starter_packet_build.zig",
    "zigux/tests/phase3_policy_starter_packet_manifest.json",
    "scripts/zigux/check-phase3-dev-t-starter-packet.py",
    "scripts/zigux/check-phase3-errptr-xarray-starter-packet.py",
    "scripts/zigux/check-phase3-policy-starter-packet.py",
    "scripts/zigux/validate-phase3-export-uapi-survey.py",
    "instead of presenting the broader validator, export/UAPI layout, low-level-wrapper, catalog, IDR, or IDA packet as shipped tests-root evidence",
    "keep the returned notifier-binding and focused export/UAPI layout replay pair explicit here instead of leaving `zigux/bindings/notifier_abi.zig`, `zigux/kernel/export_shim.zig`, `zigux/tests/phase3_export_uapi_layout.zig`, and `zigux/tests/phase3_export_uapi_layout_build.zig` framed as broader repo-reality gaps",
)

REVIEW_CHECKLIST_MARKERS = (
    "Documentation/zigux/phase3-abi-slice.md",
    "Documentation/zigux/phase3-errptr-xarray-slice.md",
    "Documentation/zigux/phase3-policy-slice.md",
    "Documentation/zigux/phase3-validator-support-surface.md",
    "include/linux/zigux.h",
    "include/zigux/dev_t.h",
    "include/zigux/abi.h",
    "zigux/uapi/dev_t.zig",
    "zigux/bindings/dev_t.zig",
    "zigux/bindings/abi.zig",
    "zigux/helpers/err_ptr.zig",
    "zigux/helpers/xa_value.zig",
    "scripts/zigux/check-phase3-dev-t-starter-packet.py",
    "scripts/zigux/check-phase3-errptr-xarray-starter-packet.py",
    "scripts/zigux/check-phase3-policy-starter-packet.py",
    "Documentation/zigux/phase3-shared-reminder-gap.md",
    "wider validator, export/UAPI layout, low-level-wrapper, catalog, IDR, and IDA routes stay explicit as repo-reality gaps",
)

VALIDATOR_SUPPORT_MARKERS = (
    "Documentation/zigux/phase3-abi-slice.md",
    "Documentation/zigux/phase3-errptr-xarray-slice.md",
    "Documentation/zigux/phase3-policy-slice.md",
    "scripts/zigux/check-phase3-dev-t-starter-packet.py",
    "scripts/zigux/check-phase3-errptr-xarray-starter-packet.py",
    "scripts/zigux/check-phase3-policy-starter-packet.py",
    "zigux/bindings/version.zig",
    "zigux/kernel/export_shim.zig",
    "zigux/tests/phase3_dev_t_starter_packet_manifest.json",
    "zig build phase3-dev-t-starter-packet-test --build-file zigux/tests/phase3_dev_t_starter_packet_build.zig --summary all",
    "zig build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig",
    "scripts/zigux/validate-phase3-export-uapi-survey.py",
    "zigux/tests/phase3_export_uapi_layout.zig",
    "zigux/tests/phase3_export_uapi_layout_build.zig",
    "Documentation/zigux/phase3-shared-reminder-gap.md",
    "scripts/zigux/validate-phase3-validator-support-surface.py",
    "Current `master` does still ship the separately readable shared validator entrypoint through `scripts/zigux/validate-phase3.py`, but that single entrypoint should not be used here to imply that the broader validator-support, export/UAPI survey, catalog, or shared replay packet has returned.",
    "`zigux/tests/README.md` now keeps the returned packet-local export/UAPI survey note and validator explicit beside the starter, helper, policy, and layout-replay packet, so keep any broader shared-summary follow-through parked unless a fresh reread reopens same-packet drift on current `master`.",
    "`Documentation/zigux/phase3-shared-reminder-gap.md` now records the aligned docs-root and tests-root reminders together while keeping scripts-root inventory work separate.",
    "broader validator, export/UAPI layout, catalog, or shared Phase 3 replay packet",
)

VALIDATOR_SUPPORT_EXACT_ONCE_MARKERS = (
    "scripts/zigux/validate-phase3-validator-support-surface.py",
)

SCRIPTS_README_MARKERS = (
    "scripts/zigux/check-phase3-selftest-surface.py",
    "scripts/zigux/check-phase3-readme-tooling-inventory.py",
    "scripts/zigux/check-phase3-shared-tests-routes.py",
    "scripts/zigux/validate-phase3-validator-support-surface.py",
    "`scripts/zigux/validate-phase3-low-level-wrapper-survey.py`",
    "scripts/zigux/validate_phase3_selftest.py",
    "scripts/zigux/run-phase3-checks.py",
    "Documentation/zigux/phase3-boundary-lane-sequencing.md",
    "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md",
    "include/linux/zigux.h",
    "include/zigux/dev_t.h",
    "include/zigux/abi.h",
    "zigux/kernel/export_shim.zig",
    "zigux/bindings/dev_t.zig",
    "zigux/bindings/version.zig",
    "zigux/bindings/abi.zig",
    "zigux/bindings/notifier_abi.zig",
    "zigux/helpers/err_ptr.zig",
    "zigux/helpers/xa_value.zig",
    "zigux/helpers/xarray_slot_view.zig",
    "zigux/helpers/panic_policy.zig",
    "zigux/helpers/allocator_policy.zig",
    "zigux/helpers/unsafe_policy.zig",
    "zigux/helpers/atomic.zig",
    "zigux/helpers/barrier.zig",
    "zigux/helpers/mmio.zig",
    "zigux/unsafe/narrow.zig",
    "zigux/uapi/dev_t.zig",
    "zigux/tests/phase3_low_level_wrappers.zig",
    "zigux/tests/phase3_low_level_wrappers_build.zig",
    "zigux/tests/phase3_xarray_slot_starter_packet.zig",
    "zig build phase3-xarray-slot-starter-packet --build-file zigux/tests/build.zig",
    ".github/workflows/zigux-bootstrap.yml",
    "python3 scripts/zigux/check-phase3-readme-tooling-inventory.py --self-test",
    "python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test",
    "scripts/zigux/check-phase3-catalog-selftest.py",
    "scripts/zigux/phase3_catalog.py",
    "scripts/zigux/generate-phase3-check-wrappers.py",
    "scripts/zigux/validate-phase3.py",
    "still return missing on current `master`",
)

SELFTEST_DRIVER_MARKERS = (
    'Path("scripts/zigux/check-phase3-dev-t-starter-packet.py")',
    'Path("scripts/zigux/check-phase3-errptr-xarray-starter-packet.py")',
    'Path("scripts/zigux/check-phase3-xarray-slot-starter-packet.py")',
    'Path("scripts/zigux/check-phase3-policy-starter-packet.py")',
    'Path("scripts/zigux/validate-phase3.py")',
    'Path("scripts/zigux/check-phase3-abi.py")',
    'Path("scripts/zigux/check-phase3-shared-tests-routes.py")',
    'Path("scripts/zigux/check-phase3-readme-tooling-inventory.py")',
    'Path("scripts/zigux/run-phase3-checks.py")',
    'Path("scripts/zigux/validate-phase3-validator-support-surface.py")',
    'Path("scripts/zigux/validate-phase3-export-uapi-survey.py")',
    'Path("scripts/zigux/validate-phase3-policy-unsafe-survey.py")',
    'Path("scripts/zigux/validate-phase3-low-level-wrapper-survey.py")',
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


def _check_exact_once_markers(path: Path, markers: tuple[str, ...], label: str) -> list[str]:
    try:
        text = _read(path)
    except FileNotFoundError:
        return [f"missing repo file: {path.as_posix()}"]

    issues: list[str] = []
    for marker in markers:
        count = text.count(marker)
        if count != 1:
            issues.append(
                f"{label} exact-count drift: {marker} (expected 1, found {count})"
            )
    return issues


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
        _check_exact_once_markers(
            repo_root / VALIDATOR_SUPPORT_PATH,
            VALIDATOR_SUPPORT_EXACT_ONCE_MARKERS,
            "validator-support note",
        )
    )
    issues.extend(_check_markers(repo_root / SCRIPTS_README_PATH, SCRIPTS_README_MARKERS, "scripts README"))
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


def _remove_exact_line(path: Path, marker: str) -> None:
    lines = _read(path).splitlines()
    try:
        lines.remove(marker)
    except ValueError:
        path.write_text(_read(path).replace(marker, "", 1), encoding="utf-8")
        return
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _append_duplicate_line(path: Path, marker: str) -> None:
    path.write_text(_read(path) + marker + "\n", encoding="utf-8")


def run_self_test() -> int:
    cases = (
        (README_PATH, "Documentation/zigux/phase3-policy-slice.md", "docs README"),
        (README_PATH, "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md", "docs README"),
        (README_PATH, "Documentation/zigux/phase3-kernel-export-shim-governance.md", "docs README"),
        (README_PATH, "zigux/bindings/notifier_abi.zig", "docs README"),
        (README_PATH, "zigux/unsafe/narrow.zig", "docs README"),
        (README_PATH, "scripts/zigux/validate-phase3-low-level-wrapper-survey.py", "docs README"),
        (README_PATH, "zigux/tests/phase3_low_level_wrappers.zig", "docs README"),
        (README_PATH, "zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig", "docs README"),
        (README_PATH, "zigux/tests/phase3_export_uapi_layout.zig", "docs README"),
        (README_PATH, "zigux/tests/phase3_export_uapi_layout_build.zig", "docs README"),
        (README_PATH, "make -C zigux phase3-export-uapi-layout-test", "docs README"),
        (README_PATH, "Documentation/zigux/phase3-export-uapi-boundary-survey.md", "docs README"),
        (README_PATH, "Documentation/zigux/phase3-linux-zigux-header-governance.md", "docs README"),
        (README_PATH, "scripts/zigux/validate-phase3-export-uapi-survey.py", "docs README"),
        (README_PATH, "zigux/tests/fixtures/phase3_abi_manifest.json", "docs README"),
        (
            TESTS_README_PATH,
            "Documentation/zigux/phase3-export-uapi-boundary-survey.md",
            "tests README",
        ),
        (
            TESTS_README_PATH,
            "scripts/zigux/validate-phase3-export-uapi-survey.py",
            "tests README",
        ),
        (
            TESTS_README_PATH,
            "instead of presenting the broader validator, export/UAPI layout, low-level-wrapper, catalog, IDR, or IDA packet as shipped tests-root evidence",
            "tests README",
        ),
        (
            TESTS_README_PATH,
            "keep the returned notifier-binding and focused export/UAPI layout replay pair explicit here instead of leaving `zigux/bindings/notifier_abi.zig`, `zigux/kernel/export_shim.zig`, `zigux/tests/phase3_export_uapi_layout.zig`, and `zigux/tests/phase3_export_uapi_layout_build.zig` framed as broader repo-reality gaps",
            "tests README",
        ),
        (
            REVIEW_CHECKLIST_PATH,
            "wider validator, export/UAPI layout, low-level-wrapper, catalog, IDR, and IDA routes stay explicit as repo-reality gaps",
            "review checklist",
        ),
        (VALIDATOR_SUPPORT_PATH, "zigux/kernel/export_shim.zig", "validator-support note"),
        (VALIDATOR_SUPPORT_PATH, "scripts/zigux/validate-phase3-export-uapi-survey.py", "validator-support note"),
        (VALIDATOR_SUPPORT_PATH, "zigux/tests/phase3_export_uapi_layout.zig", "validator-support note"),
        (VALIDATOR_SUPPORT_PATH, "zigux/tests/phase3_export_uapi_layout_build.zig", "validator-support note"),
        (
            VALIDATOR_SUPPORT_PATH,
            "Current `master` does still ship the separately readable shared validator entrypoint through `scripts/zigux/validate-phase3.py`, but that single entrypoint should not be used here to imply that the broader validator-support, export/UAPI survey, catalog, or shared replay packet has returned.",
            "validator-support note",
        ),
        (
            VALIDATOR_SUPPORT_PATH,
            "`zigux/tests/README.md` now keeps the returned packet-local export/UAPI survey note and validator explicit beside the starter, helper, policy, and layout-replay packet, so keep any broader shared-summary follow-through parked unless a fresh reread reopens same-packet drift on current `master`.",
            "validator-support note",
        ),
        (
            VALIDATOR_SUPPORT_PATH,
            "`Documentation/zigux/phase3-shared-reminder-gap.md` now records the aligned docs-root and tests-root reminders together while keeping scripts-root inventory work separate.",
            "validator-support note",
        ),
        (
            VALIDATOR_SUPPORT_PATH,
            "broader validator, export/UAPI layout, catalog, or shared Phase 3 replay packet",
            "validator-support note",
        ),
        (
            SCRIPTS_README_PATH,
            "python3 scripts/zigux/check-phase3-readme-tooling-inventory.py --self-test",
            "scripts README",
        ),
        (
            SCRIPTS_README_PATH,
            "scripts/zigux/check-phase3-shared-tests-routes.py",
            "scripts README",
        ),
        (
            SCRIPTS_README_PATH,
            "zigux/tests/phase3_xarray_slot_starter_packet.zig",
            "scripts README",
        ),
        (
            SCRIPTS_README_PATH,
            "zig build phase3-xarray-slot-starter-packet --build-file zigux/tests/build.zig",
            "scripts README",
        ),
        (
            SCRIPTS_README_PATH,
            "`scripts/zigux/validate-phase3-low-level-wrapper-survey.py`",
            "scripts README",
        ),
        (
            SCRIPTS_README_PATH,
            "python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test",
            "scripts README",
        ),
        (SCRIPTS_README_PATH, "zigux/bindings/notifier_abi.zig", "scripts README"),
        (SCRIPTS_README_PATH, "zigux/helpers/xarray_slot_view.zig", "scripts README"),
        (SCRIPTS_README_PATH, "zigux/uapi/dev_t.zig", "scripts README"),
        (SCRIPTS_README_PATH, "zigux/helpers/atomic.zig", "scripts README"),
        (SCRIPTS_README_PATH, "zigux/tests/phase3_low_level_wrappers.zig", "scripts README"),
        (SCRIPTS_README_PATH, "zigux/tests/phase3_low_level_wrappers_build.zig", "scripts README"),
        (SCRIPTS_README_PATH, "scripts/zigux/check-phase3-catalog-selftest.py", "scripts README"),
        (SCRIPTS_README_PATH, "scripts/zigux/phase3_catalog.py", "scripts README"),
        (SCRIPTS_README_PATH, "scripts/zigux/generate-phase3-check-wrappers.py", "scripts README"),
        (SCRIPTS_README_PATH, "scripts/zigux/validate-phase3.py", "scripts README"),
        (SCRIPTS_README_PATH, "still return missing on current `master`", "scripts README"),
        (
            SELFTEST_DRIVER_PATH,
            'Path("scripts/zigux/check-phase3-shared-tests-routes.py")',
            "selftest driver",
        ),
        (
            SELFTEST_DRIVER_PATH,
            'Path("scripts/zigux/check-phase3-abi.py")',
            "selftest driver",
        ),
        (
            SELFTEST_DRIVER_PATH,
            'Path("scripts/zigux/check-phase3-xarray-slot-starter-packet.py")',
            "selftest driver",
        ),
        (
            SELFTEST_DRIVER_PATH,
            'Path("scripts/zigux/validate-phase3-export-uapi-survey.py")',
            "selftest driver",
        ),
        (
            SELFTEST_DRIVER_PATH,
            'Path("scripts/zigux/validate-phase3-policy-unsafe-survey.py")',
            "selftest driver",
        ),
        (SELFTEST_DRIVER_PATH, 'Path("scripts/zigux/run-phase3-checks.py")', "selftest driver"),
        (
            SELFTEST_DRIVER_PATH,
            'Path("scripts/zigux/validate-phase3-low-level-wrapper-survey.py")',
            "selftest driver",
        ),
        (SELFTEST_DRIVER_PATH, "PHASE3_VALIDATE_SELFTEST=pass", "selftest driver"),
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
            _remove_exact_line(file_path, marker)
            issues = validate_repo(root)
            expected = f"missing {label} marker: {marker}"
            if not _expect_issue(issues, expected):
                print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
                print(f"expected missing marker was not reported: {expected}")
                return 1

        _populate_repo(root)
        _append_duplicate_line(
            root / VALIDATOR_SUPPORT_PATH,
            "scripts/zigux/validate-phase3-validator-support-surface.py",
        )
        issues = validate_repo(root)
        expected = (
            "validator-support note exact-count drift: "
            "scripts/zigux/validate-phase3-validator-support-surface.py (expected 1, found 2)"
        )
        if not _expect_issue(issues, expected):
            print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected duplicate validator-support marker drift was not reported")
            return 1

    print("PHASE3_SELFTEST_SURFACE_SELF_TEST=pass")
    print(f"PHASE3_SELFTEST_SURFACE_SELF_TEST_CASE_COUNT={len(cases) + 1}")
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