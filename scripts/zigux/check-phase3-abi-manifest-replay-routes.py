#!/usr/bin/env python3
"""Fail-close the Phase 3 ABI manifest's shared replay routes."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

VALIDATOR_PATH = Path("scripts/zigux/validate-phase3.py")
MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_abi_manifest.json")

CURRENT_NEXT_SAFE_STEP = (
    "keep the shared Phase 3 policy, export/UAPI, and low-level wrapper packet "
    "aligned with the dedicated replay routes and only reopen this manifest if the "
    "checker, focused builds, or reminder surfaces drift again"
)

REQUIRED_VALIDATOR_MARKERS = (
    '"scripts/zigux/check-phase3-abi-manifest-replay-routes.py"',
    '"scripts/zigux/check-phase3-abi-support-packet.py"',
    '"scripts/zigux/check-phase3-wrapper-templates.py"',
    '"scripts/zigux/generate-phase3-check-wrappers.py"',
    '"scripts/zigux/check-phase3-list-hlist.py"',
    '"python3 scripts/zigux/check-phase3-abi.py --self-test"',
    '"python3 scripts/zigux/check-phase3-abi.py"',
    '"python3 scripts/zigux/check-phase3-abi-manifest-replay-routes.py --self-test"',
    '"python3 scripts/zigux/check-phase3-abi-manifest-replay-routes.py"',
    '"python3 scripts/zigux/check-phase3-abi-support-packet.py --self-test"',
    '"python3 scripts/zigux/check-phase3-abi-support-packet.py"',
    '"python3 scripts/zigux/check-phase3-wrapper-templates.py --self-test"',
    '"python3 scripts/zigux/check-phase3-wrapper-templates.py"',
    '"python3 scripts/zigux/generate-phase3-check-wrappers.py --self-test"',
    '"python3 scripts/zigux/validate-phase3.py --self-test"',
    '"python3 scripts/zigux/validate-phase3.py"',
    '"python3 scripts/zigux/check-phase3-selftest-surface.py --self-test"',
    '"python3 scripts/zigux/check-phase3-selftest-surface.py"',
    '"python3 scripts/zigux/validate-phase3-validator-support-surface.py --self-test"',
    '"python3 scripts/zigux/validate-phase3-validator-support-surface.py"',
    '"python3 scripts/zigux/validate-phase3-export-uapi-survey.py --self-test"',
    '"python3 scripts/zigux/validate-phase3-export-uapi-survey.py"',
    '"python3 scripts/zigux/check-phase3-export-uapi-c-header-smoke.py --self-test"',
    '"python3 scripts/zigux/check-phase3-export-uapi-c-header-smoke.py"',
    '"python3 scripts/zigux/validate-phase3-policy-unsafe-survey.py --self-test"',
    '"python3 scripts/zigux/validate-phase3-policy-unsafe-survey.py"',
    '"python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test"',
    '"python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py"',
    '"python3 scripts/zigux/validate-phase3-linux-zigux-header-governance.py --self-test"',
    '"python3 scripts/zigux/validate-phase3-linux-zigux-header-governance.py"',
    '"python3 scripts/zigux/check-phase3-policy-starter-packet.py --self-test"',
    '"python3 scripts/zigux/check-phase3-policy-starter-packet.py"',
    '"python3 scripts/zigux/check-phase3-policy-dump.py --self-test"',
    '"python3 scripts/zigux/check-phase3-policy-dump.py"',
    '"python3 scripts/zigux/check-phase3-dev-t-starter-packet.py --self-test"',
    '"python3 scripts/zigux/check-phase3-dev-t-starter-packet.py"',
    '"python3 scripts/zigux/check-phase3-errptr-xarray-starter-packet.py --self-test"',
    '"python3 scripts/zigux/check-phase3-errptr-xarray-starter-packet.py"',
    '"python3 scripts/zigux/check-phase3-xarray-slot-starter-packet.py --self-test"',
    '"python3 scripts/zigux/check-phase3-xarray-slot-starter-packet.py"',
    '"python3 scripts/zigux/check-phase3-xarray-slot.py --self-test"',
    '"python3 scripts/zigux/check-phase3-xarray-slot.py"',
    '"python3 scripts/zigux/check-phase3-shared-tests-routes.py --self-test"',
    '"python3 scripts/zigux/check-phase3-shared-tests-routes.py"',
    '"python3 scripts/zigux/check-phase3-catalog-selftest.py --self-test"',
    '"python3 scripts/zigux/check-phase3-catalog-selftest.py"',
    '"python3 scripts/zigux/validate-phase3-abi-header-family-survey.py --self-test"',
    '"python3 scripts/zigux/validate-phase3-abi-header-family-survey.py"',
    '"python3 scripts/zigux/validate_phase3_selftest.py"',
    '"python3 scripts/zigux/run-phase3-checks.py"',
    '"make -C zigux phase3-validate"',
    '"python3 scripts/zigux/check-phase3-bitmap-cpumask.py --self-test"',
    '"python3 scripts/zigux/check-phase3-bitmap-cpumask.py"',
    '"python3 scripts/zigux/check-phase3-list-hlist-starter-packet.py --self-test"',
    '"python3 scripts/zigux/check-phase3-list-hlist-starter-packet.py"',
    '"python3 scripts/zigux/check-phase3-list-hlist.py --self-test"',
    '"python3 scripts/zigux/check-phase3-list-hlist.py --repo-root . --zig zig --cc gcc"',
    '"zig build phase3-dev-t-starter-packet-test --build-file zigux/tests/phase3_dev_t_starter_packet_build.zig --summary all"',
    '"zig build phase3-errptr-xarray-dump --build-file zigux/tests/phase3_errptr_xarray_dump_build.zig"',
    '"zig build phase3-xarray-slot-starter-packet-test --build-file zigux/tests/phase3_xarray_slot_starter_packet_build.zig"',
    '"zig build phase3-xarray-slot-dump --build-file zigux/tests/phase3_xarray_slot_dump_build.zig"',
    '"zig build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig"',
    '"make -C zigux phase3-policy-starter-packet-test"',
    '"zig build phase3-abi-core-packet --build-file zigux/tests/build.zig"',
    '"zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig"',
    '"zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig"',
    '"zig build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig"',
    '"make -C zigux phase3-export-shim-test"',
    '"zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig"',
    '"make -C zigux phase3-policy-dump"',
    '"zig build phase3-dump --build-file zigux/tests/build.zig"',
    '"make -C zigux phase3-dump"',
    '"zig build phase3-low-level-wrappers --build-file zigux/tests/build.zig"',
    '"make -C zigux phase3-low-level-wrappers"',
    '"zig build phase3-test --build-file zigux/tests/build.zig"',
    '"make -C zigux phase3-test"',
    '"make -C zigux phase3"',
    '"zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig"',
    '"make -C zigux phase3-export-uapi-layout"',
    '"make -C zigux phase3-export-uapi-layout-test"',
    '"make -C zigux phase3-low-level-wrappers-test"',
    '"zig build phase3-bitmap-cpumask-starter-packet --build-file zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig"',
    '"zig build phase3-list-hlist-starter-packet --build-file zigux/tests/phase3_list_hlist_starter_packet_build.zig"',
    '"zig build phase3-list-hlist-dump --build-file zigux/tests/phase3_list_hlist_dump_build.zig"',
)

REQUIRED_MANIFEST_FIELDS = {
    "phase": "Phase 3",
    "lane": "abi-runtime",
    "slug": "phase3-abi-packet",
    "status": "shared_abi_and_header_family_binding_surface_present",
    "scope": (
        "shared ABI bindings, directly coupled helper decoding, header-family "
        "follow-through, notifier layouts, export-status layout, and "
        "header-compatibility replay"
    ),
    "next_safe_step": CURRENT_NEXT_SAFE_STEP,
}

REQUIRED_PACKET_FILES = (
    "scripts/zigux/check-phase3-abi-manifest-replay-routes.py",
    "scripts/zigux/check-phase3-abi-support-packet.py",
    "Documentation/zigux/phase3-export-uapi-boundary-survey.md",
    "scripts/zigux/validate-phase3-export-uapi-survey.py",
    "Documentation/zigux/phase3-validator-support-surface.md",
    "scripts/zigux/validate-phase3-validator-support-surface.py",
    "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md",
    "scripts/zigux/validate-phase3-policy-unsafe-survey.py",
    "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md",
    "scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    "Documentation/zigux/phase3-linux-zigux-header-governance.md",
    "scripts/zigux/validate-phase3-linux-zigux-header-governance.py",
    "include/zigux/dev_t.h",
    "zigux/uapi/dev_t.zig",
    "zigux/bindings/dev_t.zig",
    "scripts/zigux/check-phase3-dev-t-starter-packet.py",
    "Documentation/zigux/phase3-errptr-xarray-slice.md",
    "zigux/helpers/err_ptr.zig",
    "zigux/helpers/xa_value.zig",
    "scripts/zigux/check-phase3-errptr-xarray-starter-packet.py",
    "zigux/tests/phase3_errptr_xarray_starter_packet.zig",
    "zigux/tests/phase3_errptr_xarray_starter_packet_build.zig",
    "zigux/tests/phase3_errptr_xarray_starter_packet_manifest.json",
    "zigux/tests/phase3_errptr_xarray_dump.zig",
    "zigux/tests/phase3_errptr_xarray_dump_build.zig",
    "Documentation/zigux/phase3-xarray-slot-slice.md",
    "zigux/helpers/xarray_slot_view.zig",
    "scripts/zigux/check-phase3-xarray-slot-starter-packet.py",
    "scripts/zigux/check-phase3-xarray-slot.py",
    "zigux/tests/phase3_xarray_slot_starter_packet.zig",
    "zigux/tests/phase3_xarray_slot_starter_packet_build.zig",
    "zigux/tests/phase3_xarray_slot_dump.zig",
    "zigux/tests/phase3_xarray_slot_dump_build.zig",
    "zigux/tests/fixtures/phase3_xarray_slot/phase3_xarray_slot_c_harness.c",
    "zigux/tests/fixtures/phase3_xarray_slot/expected.json",
    "zigux/tests/fixtures/phase3_xarray_slot_manifest.json",
    "zigux/tests/phase3_export_uapi_c_header_smoke.c",
    "scripts/zigux/check-phase3-export-uapi-c-header-smoke.py",
    "scripts/zigux/check-phase3-wrapper-templates.py",
    "scripts/zigux/generate-phase3-check-wrappers.py",
    "zigux/tests/phase3_dev_t_starter_packet.zig",
    "zigux/tests/phase3_dev_t_starter_packet_build.zig",
    "zigux/tests/phase3_dev_t_starter_packet_manifest.json",
    "zigux/tests/phase3_export_uapi_layout.zig",
    "zigux/tests/phase3_export_uapi_layout_build.zig",
    "zigux/tests/phase3_export_shim_build.zig",
    "zigux/kernel/export_shim.zig",
    "zigux/tests/phase3_policy_dump.zig",
    "zigux/tests/phase3_policy_dump_build.zig",
    "zigux/tests/fixtures/phase3_policy_dump_expected.txt",
    "scripts/zigux/check-phase3-policy-dump.py",
    "scripts/zigux/validate_phase3_selftest.py",
    "scripts/zigux/run-phase3-checks.py",
    "scripts/zigux/check-phase3-readme-tooling-inventory.py",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "Documentation/zigux/phase3-bitmap-cpumask-slice.md",
    "zigux/helpers/bitmap_view.zig",
    "zigux/helpers/cpumask_view.zig",
    "zigux/tests/phase3_bitmap_cpumask_starter_packet.zig",
    "zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig",
    "zigux/tests/fixtures/phase3_bitmap_cpumask/phase3_bitmap_cpumask_c_harness.c",
    "zigux/tests/fixtures/phase3_bitmap_cpumask/expected.json",
    "zigux/tests/fixtures/phase3_bitmap_cpumask_manifest.json",
    "scripts/zigux/check-phase3-bitmap-cpumask.py",
    "Documentation/zigux/phase3-list-hlist-slice.md",
    "zigux/helpers/list_view.zig",
    "zigux/helpers/hlist_view.zig",
    "zigux/tests/phase3_list_hlist_starter_packet.zig",
    "zigux/tests/phase3_list_hlist_starter_packet_build.zig",
    "zigux/tests/fixtures/phase3_list_hlist_manifest.json",
    "scripts/zigux/check-phase3-list-hlist-starter-packet.py",
    "zigux/tests/phase3_list_hlist_dump.zig",
    "zigux/tests/phase3_list_hlist_dump_build.zig",
    "zigux/tests/fixtures/phase3_list_hlist/phase3_list_hlist_c_harness.c",
    "zigux/tests/fixtures/phase3_list_hlist/expected.json",
    "scripts/zigux/check-phase3-list-hlist.py",
)

REQUIRED_REPLAY_ROUTES = (
    "python3 scripts/zigux/check-phase3-abi.py --self-test",
    "python3 scripts/zigux/check-phase3-abi.py",
    "python3 scripts/zigux/check-phase3-abi-manifest-replay-routes.py --self-test",
    "python3 scripts/zigux/check-phase3-abi-manifest-replay-routes.py",
    "python3 scripts/zigux/check-phase3-abi-support-packet.py --self-test",
    "python3 scripts/zigux/check-phase3-abi-support-packet.py",
    "python3 scripts/zigux/check-phase3-policy-starter-packet.py --self-test",
    "python3 scripts/zigux/check-phase3-policy-starter-packet.py",
    "python3 scripts/zigux/check-phase3-policy-dump.py --self-test",
    "python3 scripts/zigux/check-phase3-policy-dump.py",
    "python3 scripts/zigux/check-phase3-shared-tests-routes.py --self-test",
    "python3 scripts/zigux/check-phase3-shared-tests-routes.py",
    "python3 scripts/zigux/check-phase3-readme-tooling-inventory.py --self-test",
    "python3 scripts/zigux/check-phase3-readme-tooling-inventory.py",
    "python3 scripts/zigux/check-phase3-wrapper-templates.py --self-test",
    "python3 scripts/zigux/check-phase3-wrapper-templates.py",
    "python3 scripts/zigux/check-phase3-catalog-selftest.py --self-test",
    "python3 scripts/zigux/check-phase3-catalog-selftest.py",
    "python3 scripts/zigux/validate-phase3.py --self-test",
    "python3 scripts/zigux/validate-phase3.py",
    "python3 scripts/zigux/validate-phase3-validator-support-surface.py --self-test",
    "python3 scripts/zigux/validate-phase3-validator-support-surface.py",
    "python3 scripts/zigux/validate-phase3-export-uapi-survey.py --self-test",
    "python3 scripts/zigux/validate-phase3-export-uapi-survey.py",
    "python3 scripts/zigux/validate-phase3-abi-header-family-survey.py --self-test",
    "python3 scripts/zigux/validate-phase3-abi-header-family-survey.py",
    "python3 scripts/zigux/validate-phase3-policy-unsafe-survey.py --self-test",
    "python3 scripts/zigux/validate-phase3-policy-unsafe-survey.py",
    "python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test",
    "python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    "python3 scripts/zigux/validate-phase3-linux-zigux-header-governance.py --self-test",
    "python3 scripts/zigux/validate-phase3-linux-zigux-header-governance.py",
    "python3 scripts/zigux/check-phase3-selftest-surface.py --self-test",
    "python3 scripts/zigux/check-phase3-selftest-surface.py",
    "python3 scripts/zigux/generate-phase3-check-wrappers.py --self-test",
    "python3 scripts/zigux/validate_phase3_selftest.py",
    "python3 scripts/zigux/run-phase3-checks.py",
    "make -C zigux phase3-validate",
    "python3 scripts/zigux/check-phase3-dev-t-starter-packet.py --self-test",
    "python3 scripts/zigux/check-phase3-dev-t-starter-packet.py",
    "python3 scripts/zigux/check-phase3-errptr-xarray-starter-packet.py --self-test",
    "python3 scripts/zigux/check-phase3-errptr-xarray-starter-packet.py",
    "python3 scripts/zigux/check-phase3-xarray-slot-starter-packet.py --self-test",
    "python3 scripts/zigux/check-phase3-xarray-slot-starter-packet.py",
    "python3 scripts/zigux/check-phase3-xarray-slot.py --self-test",
    "python3 scripts/zigux/check-phase3-xarray-slot.py",
    "python3 scripts/zigux/check-phase3-export-uapi-c-header-smoke.py --self-test",
    "python3 scripts/zigux/check-phase3-export-uapi-c-header-smoke.py",
    "python3 scripts/zigux/check-phase3-bitmap-cpumask.py --self-test",
    "python3 scripts/zigux/check-phase3-bitmap-cpumask.py",
    "python3 scripts/zigux/check-phase3-list-hlist-starter-packet.py --self-test",
    "python3 scripts/zigux/check-phase3-list-hlist-starter-packet.py",
    "python3 scripts/zigux/check-phase3-list-hlist.py --self-test",
    "python3 scripts/zigux/check-phase3-list-hlist.py --repo-root . --zig zig --cc gcc",
    "zig build phase3-dev-t-starter-packet-test --build-file zigux/tests/phase3_dev_t_starter_packet_build.zig --summary all",
    "zig build phase3-errptr-xarray-dump --build-file zigux/tests/phase3_errptr_xarray_dump_build.zig",
    "zig build phase3-xarray-slot-starter-packet-test --build-file zigux/tests/phase3_xarray_slot_starter_packet_build.zig",
    "zig build phase3-xarray-slot-dump --build-file zigux/tests/phase3_xarray_slot_dump_build.zig",
    "zig build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig",
    "make -C zigux phase3-policy-starter-packet-test",
    "zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig",
    "make -C zigux phase3-policy-dump",
    "zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig",
    "zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
    "zig build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig",
    "make -C zigux phase3-export-shim-test",
    "make -C zigux phase3-export-uapi-layout",
    "make -C zigux phase3-export-uapi-layout-test",
    "zig build phase3-abi-core-packet --build-file zigux/tests/build.zig",
    "zig build phase3-dump --build-file zigux/tests/build.zig",
    "make -C zigux phase3-dump",
    "zig build phase3-low-level-wrappers --build-file zigux/tests/build.zig",
    "make -C zigux phase3-low-level-wrappers",
    "zig build phase3-test --build-file zigux/tests/build.zig",
    "make -C zigux phase3-test",
    "make -C zigux phase3",
    "zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    "make -C zigux phase3-low-level-wrappers-test",
    "zig build phase3-bitmap-cpumask-starter-packet --build-file zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig",
    "zig build phase3-list-hlist-starter-packet --build-file zigux/tests/phase3_list_hlist_starter_packet_build.zig",
    "zig build phase3-list-hlist-dump --build-file zigux/tests/phase3_list_hlist_dump_build.zig",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _append_duplicate_list_entry_issues(
    label: str, values: list[object], issues: list[str]
) -> None:
    seen: dict[str, int] = {}
    for index, value in enumerate(values):
        key = repr(value)
        first_index = seen.get(key)
        if first_index is None:
            seen[key] = index
            continue
        issues.append(
            f"{label} duplicate entry: {value!r} (first index {first_index}, duplicate index {index})"
        )


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []

    validator_path = repo_root / VALIDATOR_PATH
    if not validator_path.is_file():
        issues.append(f"missing repo file: {VALIDATOR_PATH.as_posix()}")
    else:
        validator_text = _read(validator_path)
        for marker in REQUIRED_VALIDATOR_MARKERS:
            if marker not in validator_text:
                issues.append(
                    f"missing {VALIDATOR_PATH.as_posix()} marker: {marker}"
                )

    manifest_path = repo_root / MANIFEST_PATH
    if not manifest_path.is_file():
        issues.append(f"missing repo file: {MANIFEST_PATH.as_posix()}")
        return issues

    try:
        manifest = json.loads(_read(manifest_path))
    except json.JSONDecodeError as exc:
        issues.append(f"invalid JSON in {MANIFEST_PATH.as_posix()}: {exc}")
        return issues

    for field, expected in REQUIRED_MANIFEST_FIELDS.items():
        actual = manifest.get(field)
        if actual != expected:
            issues.append(
                f"phase3_abi_manifest.json wrong {field}: {actual!r} != {expected!r}"
            )

    packet_files = manifest.get("packet_files")
    if not isinstance(packet_files, list):
        issues.append("phase3_abi_manifest.json packet_files is not a list")
    else:
        _append_duplicate_list_entry_issues(
            "phase3_abi_manifest.json packet_files",
            packet_files,
            issues,
        )
        for entry in REQUIRED_PACKET_FILES:
            if entry not in packet_files:
                issues.append(f"phase3_abi_manifest.json missing packet_files entry: {entry}")

    replay_routes = manifest.get("replay_routes")
    if not isinstance(replay_routes, list):
        issues.append("phase3_abi_manifest.json replay_routes is not a list")
    else:
        _append_duplicate_list_entry_issues(
            "phase3_abi_manifest.json replay_routes",
            replay_routes,
            issues,
        )
        for route in REQUIRED_REPLAY_ROUTES:
            if route not in replay_routes:
                issues.append(f"phase3_abi_manifest.json missing replay route: {route}")

    repo_reality_gaps = manifest.get("repo_reality_gaps")
    if not isinstance(repo_reality_gaps, list):
        issues.append("phase3_abi_manifest.json repo_reality_gaps is not a list")
    elif repo_reality_gaps:
        issues.append(
            "phase3_abi_manifest.json repo_reality_gaps drifted from the current shared packet expectation"
        )

    return issues


def _sample_validator() -> str:
    lines = ["#!/usr/bin/env python3", "REQUIRED_MANIFEST_REPLAY_ROUTES = ("]
    lines.extend(f"    {marker}," for marker in REQUIRED_VALIDATOR_MARKERS)
    lines.extend([")", ""])
    return "\n".join(lines)


def _sample_manifest() -> str:
    manifest = {
        "phase": "Phase 3",
        "lane": "abi-runtime",
        "slug": "phase3-abi-packet",
        "status": "shared_abi_and_header_family_binding_surface_present",
        "scope": REQUIRED_MANIFEST_FIELDS["scope"],
        "packet_files": list(REQUIRED_PACKET_FILES),
        "replay_routes": list(REQUIRED_REPLAY_ROUTES),
        "repo_reality_gaps": [],
        "next_safe_step": CURRENT_NEXT_SAFE_STEP,
    }
    return json.dumps(manifest, indent=2) + "\n"


def _populate_repo(root: Path) -> None:
    _write(root / VALIDATOR_PATH, _sample_validator())
    _write(root / MANIFEST_PATH, _sample_manifest())


def _expect_issue(issues: list[str], expected: str) -> None:
    if expected not in issues:
        print("PHASE3_ABI_MANIFEST_REPLAY_ROUTES_SELF_TEST=fail")
        print(f"missing expected issue: {expected}")
        if issues:
            print("\n".join(issues))
        raise SystemExit(1)


def run_self_test() -> int:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_abi_manifest_routes_") as temp_dir:
        repo_root = Path(temp_dir)
        manifest_path = repo_root / MANIFEST_PATH
        validator_path = repo_root / VALIDATOR_PATH

        _populate_repo(repo_root)
        issues = validate_repo(repo_root)
        if issues:
            print("PHASE3_ABI_MANIFEST_REPLAY_ROUTES_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for marker in REQUIRED_VALIDATOR_MARKERS:
            _populate_repo(repo_root)
            current = _read(validator_path)
            needle = f"    {marker},\n"
            _write(validator_path, current.replace(needle, "", 1))
            issues = validate_repo(repo_root)
            _expect_issue(
                issues,
                f"missing {VALIDATOR_PATH.as_posix()} marker: {marker}",
            )
            cases += 1

        for entry in REQUIRED_PACKET_FILES:
            _populate_repo(repo_root)
            manifest = json.loads(_read(manifest_path))
            manifest["packet_files"].remove(entry)
            _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
            issues = validate_repo(repo_root)
            _expect_issue(
                issues,
                f"phase3_abi_manifest.json missing packet_files entry: {entry}",
            )
            cases += 1

        _populate_repo(repo_root)
        manifest = json.loads(_read(manifest_path))
        duplicate_packet_file = manifest["packet_files"][-1]
        first_packet_index = len(manifest["packet_files"]) - 1
        manifest["packet_files"].append(duplicate_packet_file)
        duplicate_packet_index = len(manifest["packet_files"]) - 1
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(repo_root)
        _expect_issue(
            issues,
            "phase3_abi_manifest.json packet_files duplicate entry: "
            f"{duplicate_packet_file!r} (first index {first_packet_index}, duplicate index {duplicate_packet_index})",
        )
        cases += 1

        for route in REQUIRED_REPLAY_ROUTES:
            _populate_repo(repo_root)
            manifest = json.loads(_read(manifest_path))
            manifest["replay_routes"].remove(route)
            _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
            issues = validate_repo(repo_root)
            _expect_issue(
                issues,
                f"phase3_abi_manifest.json missing replay route: {route}",
            )
            cases += 1

        _populate_repo(repo_root)
        manifest = json.loads(_read(manifest_path))
        duplicate_replay_route = manifest["replay_routes"][-1]
        first_route_index = len(manifest["replay_routes"]) - 1
        manifest["replay_routes"].append(duplicate_replay_route)
        duplicate_route_index = len(manifest["replay_routes"]) - 1
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(repo_root)
        _expect_issue(
            issues,
            "phase3_abi_manifest.json replay_routes duplicate entry: "
            f"{duplicate_replay_route!r} (first index {first_route_index}, duplicate index {duplicate_route_index})",
        )
        cases += 1

        for field, bad_value in (
            ("status", "stale-status"),
            ("scope", "stale-scope"),
            ("repo_reality_gaps", ["stale-gap"]),
            ("next_safe_step", "stale-next-step"),
            ("slug", "stale-slug"),
        ):
            _populate_repo(repo_root)
            manifest = json.loads(_read(manifest_path))
            manifest[field] = bad_value
            _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
            issues = validate_repo(repo_root)
            if field == "repo_reality_gaps":
                expected = (
                    "phase3_abi_manifest.json repo_reality_gaps drifted from the current shared packet expectation"
                )
            else:
                expected = (
                    f"phase3_abi_manifest.json wrong {field}: {bad_value!r} != "
                    f"{REQUIRED_MANIFEST_FIELDS[field]!r}"
                )
            _expect_issue(issues, expected)
            cases += 1

    print("PHASE3_ABI_MANIFEST_REPLAY_ROUTES_SELF_TEST=pass")
    print(f"PHASE3_ABI_MANIFEST_REPLAY_ROUTES_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the Phase 3 ABI manifest's shared replay routes."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the Phase 3 ABI validator and manifest",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_ABI_MANIFEST_REPLAY_ROUTES=fail")
        print("\n".join(issues))
        return 1

    print("PHASE3_ABI_MANIFEST_REPLAY_ROUTES=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
