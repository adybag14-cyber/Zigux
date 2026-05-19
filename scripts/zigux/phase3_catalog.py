#!/usr/bin/env python3
"""Inventory the current bounded Phase 3 ABI/runtime packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

PHASE3_CATALOG_PHASE = "Phase 3"
PHASE3_CATALOG_SCOPE = "abi-runtime"

DOC_PATHS = (
    Path("Documentation/zigux/phase3-abi-slice.md"),
    Path("Documentation/zigux/phase3-abi-header-family-survey.md"),
    Path("Documentation/zigux/phase3-errptr-xarray-slice.md"),
    Path("Documentation/zigux/phase3-policy-slice.md"),
    Path("Documentation/zigux/phase3-validator-support-surface.md"),
    Path("Documentation/zigux/phase3-boundary-lane-sequencing.md"),
    Path("Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md"),
    Path("Documentation/zigux/phase3-export-uapi-boundary-survey.md"),
)

HEADER_PATHS = (
    Path("include/linux/zigux.h"),
    Path("include/zigux/dev_t.h"),
    Path("include/zigux/abi.h"),
)

BINDING_PATHS = (
    Path("zigux/uapi/dev_t.zig"),
    Path("zigux/uapi/version.zig"),
    Path("zigux/bindings/dev_t.zig"),
    Path("zigux/bindings/version.zig"),
    Path("zigux/bindings/header_family.zig"),
    Path("zigux/bindings/abi.zig"),
    Path("zigux/bindings/notifier_abi.zig"),
)

HELPER_PATHS = (
    Path("zigux/kernel/export_shim.zig"),
    Path("zigux/helpers/panic_policy.zig"),
    Path("zigux/helpers/allocator_policy.zig"),
    Path("zigux/helpers/unsafe_policy.zig"),
    Path("zigux/helpers/atomic.zig"),
    Path("zigux/helpers/barrier.zig"),
    Path("zigux/helpers/mmio.zig"),
    Path("zigux/helpers/err_ptr.zig"),
    Path("zigux/helpers/xa_value.zig"),
    Path("zigux/helpers/xarray_slot_view.zig"),
    Path("zigux/unsafe/narrow.zig"),
)

VALIDATOR_PATHS = (
    Path("scripts/zigux/check-phase3-readme-tooling-inventory.py"),
    Path("scripts/zigux/check-phase3-selftest-surface.py"),
    Path("scripts/zigux/check-phase3-shared-tests-routes.py"),
    Path("scripts/zigux/validate-phase3-validator-support-surface.py"),
    Path("scripts/zigux/validate_phase3_selftest.py"),
    Path("scripts/zigux/run-phase3-checks.py"),
    Path("scripts/zigux/validate-phase3.py"),
    Path("scripts/zigux/check-phase3-abi.py"),
    Path("scripts/zigux/phase3_catalog.py"),
    Path("scripts/zigux/check-phase3-dev-t-starter-packet.py"),
    Path("scripts/zigux/check-phase3-errptr-xarray-starter-packet.py"),
    Path("scripts/zigux/check-phase3-policy-starter-packet.py"),
    Path("scripts/zigux/check-phase3-catalog-selftest.py"),
    Path("scripts/zigux/validate-phase3-export-uapi-survey.py"),
    Path("scripts/zigux/validate-phase3-low-level-wrapper-survey.py"),
    Path("scripts/zigux/validate-phase3-abi-header-family-survey.py"),
)

TEST_PATHS = (
    Path("zigux/tests/build.zig"),
    Path("zigux/tests/phase3_dev_t_starter_packet.zig"),
    Path("zigux/tests/phase3_dev_t_starter_packet_build.zig"),
    Path("zigux/tests/phase3_errptr_xarray_starter_packet.zig"),
    Path("zigux/tests/phase3_errptr_xarray_starter_packet_build.zig"),
    Path("zigux/tests/phase3_xarray_slot_starter_packet.zig"),
    Path("zigux/tests/phase3_policy_starter_packet.zig"),
    Path("zigux/tests/phase3_policy_starter_packet_build.zig"),
    Path("zigux/tests/phase3_low_level_wrappers.zig"),
    Path("zigux/tests/phase3_low_level_wrappers_build.zig"),
    Path("zigux/tests/phase3_export_uapi_layout.zig"),
    Path("zigux/tests/phase3_export_uapi_layout_build.zig"),
    Path("zigux/tests/phase3_abi_dump_current.zig"),
)

COMMANDS = (
    "python3 scripts/zigux/check-phase3-readme-tooling-inventory.py --self-test",
    "python3 scripts/zigux/check-phase3-selftest-surface.py --self-test",
    "python3 scripts/zigux/check-phase3-shared-tests-routes.py --self-test",
    "python3 scripts/zigux/validate_phase3_selftest.py",
    "python3 scripts/zigux/validate-phase3.py",
    "python3 scripts/zigux/check-phase3-catalog-selftest.py --self-test",
    "python3 scripts/zigux/check-phase3-catalog-selftest.py",
    "python3 scripts/zigux/validate-phase3-export-uapi-survey.py --self-test",
    "python3 scripts/zigux/validate-phase3-export-uapi-survey.py",
    "python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    "python3 scripts/zigux/validate-phase3-abi-header-family-survey.py --self-test",
    "python3 scripts/zigux/validate-phase3-abi-header-family-survey.py",
    "zig build phase3-xarray-slot-starter-packet --build-file zigux/tests/build.zig",
    "zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    "zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _collect_existing(repo_root: Path, rel_paths: tuple[Path, ...]) -> list[str]:
    return [
        rel_path.as_posix()
        for rel_path in rel_paths
        if (repo_root / rel_path).is_file()
    ]


def validate_repo(repo_root: Path) -> list[str]:
    missing: list[str] = []
    for rel_path in (
        *DOC_PATHS,
        *HEADER_PATHS,
        *BINDING_PATHS,
        *HELPER_PATHS,
        *VALIDATOR_PATHS,
        *TEST_PATHS,
    ):
        if not (repo_root / rel_path).is_file():
            missing.append(f"missing repo file: {rel_path.as_posix()}")
    return missing


def build_catalog(repo_root: Path) -> dict[str, object]:
    return {
        "phase": PHASE3_CATALOG_PHASE,
        "scope": PHASE3_CATALOG_SCOPE,
        "docs": _collect_existing(repo_root, DOC_PATHS),
        "headers": _collect_existing(repo_root, HEADER_PATHS),
        "bindings": _collect_existing(repo_root, BINDING_PATHS),
        "helpers": _collect_existing(repo_root, HELPER_PATHS),
        "validators": _collect_existing(repo_root, VALIDATOR_PATHS),
        "tests": _collect_existing(repo_root, TEST_PATHS),
        "commands": list(COMMANDS),
    }


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_catalog_") as tmp_dir:
        root = Path(tmp_dir)
        for rel_path in (
            *DOC_PATHS,
            *HEADER_PATHS,
            *BINDING_PATHS,
            *HELPER_PATHS,
            *VALIDATOR_PATHS,
            *TEST_PATHS,
        ):
            _write(root / rel_path, "// self-test\n")

        issues = validate_repo(root)
        if issues:
            print("PHASE3_CATALOG_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        catalog = build_catalog(root)
        expected_counts = {
            "docs": len(DOC_PATHS),
            "headers": len(HEADER_PATHS),
            "bindings": len(BINDING_PATHS),
            "helpers": len(HELPER_PATHS),
            "validators": len(VALIDATOR_PATHS),
            "tests": len(TEST_PATHS),
            "commands": len(COMMANDS),
        }
        for key, count in expected_counts.items():
            if len(catalog[key]) != count:
                print("PHASE3_CATALOG_SELF_TEST=fail")
                print(f"unexpected {key} count: {len(catalog[key])} != {count}")
                return 1

        missing_probe = root / VALIDATOR_PATHS[-1]
        missing_probe.unlink()
        issues = validate_repo(root)
        expected = f"missing repo file: {VALIDATOR_PATHS[-1].as_posix()}"
        if expected not in issues:
            print("PHASE3_CATALOG_SELF_TEST=fail")
            print("expected missing ABI header-family survey validator route was not reported")
            return 1

    print("PHASE3_CATALOG_SELF_TEST=pass")
    print("PHASE3_CATALOG_SELF_TEST_CASE_COUNT=3")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Inventory the current bounded Phase 3 ABI/runtime packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the current Phase 3 ABI/runtime packet",
    )
    parser.add_argument("--pretty", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_CATALOG=fail")
        print("\n".join(issues))
        return 1

    payload = build_catalog(args.repo_root)
    if args.pretty:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
