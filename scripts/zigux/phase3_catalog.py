#!/usr/bin/env python3
"""Inventory the current bounded Phase 3 ABI support packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

PHASE3_CATALOG_PHASE = "Phase 3"
PHASE3_CATALOG_SCOPE = "abi-runtime"
PHASE3_CATALOG_SLUG = "phase3-abi-packet"
PHASE3_CATALOG_STATUS = "shared_abi_and_header_family_binding_surface_present"
PHASE3_CATALOG_MANIFEST_SCOPE = (
    "shared ABI bindings, directly coupled helper decoding, header-family "
    "follow-through, notifier layouts, export-status layout, and "
    "header-compatibility replay"
)
PHASE3_CATALOG_NEXT_SAFE_STEP = (
    "keep the shared Phase 3 policy, export/UAPI, and low-level wrapper packet "
    "aligned with the dedicated replay routes and only reopen this manifest if the "
    "checker, focused builds, or reminder surfaces drift again"
)
MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_abi_manifest.json")

EXPECTED_PACKET_FILES = (
    "Documentation/zigux/phase3-abi-slice.md",
    "Documentation/zigux/phase3-abi-header-family-survey.md",
    "Documentation/zigux/phase3-abi-h-boundary-next-step.md",
    "Documentation/zigux/phase3-policy-slice.md",
    "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md",
    "Documentation/zigux/phase3-export-uapi-boundary-survey.md",
    "Documentation/zigux/phase3-kernel-export-shim-governance.md",
    "Documentation/zigux/phase3-linux-zigux-header-governance.md",
    "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md",
    "Documentation/zigux/phase3-validator-support-surface.md",
    "Documentation/zigux/phase3-shared-reminder-gap.md",
    "include/zigux/abi.h",
    "include/zigux/dev_t.h",
    "include/linux/zigux.h",
    "zigux/uapi/dev_t.zig",
    "zigux/uapi/version.zig",
    "zigux/bindings/abi.zig",
    "zigux/bindings/dev_t.zig",
    "zigux/bindings/version.zig",
    "zigux/bindings/header_family.zig",
    "zigux/bindings/notifier_abi.zig",
    "zigux/helpers/layout_assert.zig",
    "zigux/helpers/panic_policy.zig",
    "zigux/helpers/allocator_policy.zig",
    "zigux/helpers/unsafe_policy.zig",
    "zigux/helpers/atomic.zig",
    "zigux/helpers/barrier.zig",
    "zigux/helpers/mmio.zig",
    "zigux/kernel/export_shim.zig",
    "zigux/unsafe/narrow.zig",
    "scripts/zigux/validate-phase3.py",
    "scripts/zigux/check-phase3-abi.py",
    "scripts/zigux/check-phase3-abi-manifest-replay-routes.py",
    "scripts/zigux/check-phase3-abi-support-packet.py",
    "scripts/zigux/check-phase3-catalog-selftest.py",
    "scripts/zigux/check-phase3-readme-tooling-inventory.py",
    "scripts/zigux/check-phase3-dev-t-starter-packet.py",
    "scripts/zigux/check-phase3-errptr-xarray-starter-packet.py",
    "scripts/zigux/check-phase3-xarray-slot-starter-packet.py",
    "scripts/zigux/check-phase3-xarray-slot.py",
    "scripts/zigux/check-phase3-export-uapi-c-header-smoke.py",
    "scripts/zigux/check-phase3-policy-dump.py",
    "scripts/zigux/check-phase3-policy-starter-packet.py",
    "scripts/zigux/check-phase3-selftest-surface.py",
    "scripts/zigux/check-phase3-shared-tests-routes.py",
    "scripts/zigux/check-phase3-wrapper-templates.py",
    "scripts/zigux/generate-phase3-check-wrappers.py",
    "scripts/zigux/phase3_catalog.py",
    "scripts/zigux/validate-phase3-policy-unsafe-survey.py",
    "scripts/zigux/validate-phase3-validator-support-surface.py",
    "scripts/zigux/validate-phase3-export-uapi-survey.py",
    "scripts/zigux/validate-phase3-abi-header-family-survey.py",
    "scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    "scripts/zigux/validate-phase3-linux-zigux-header-governance.py",
    "scripts/zigux/run-phase3-checks.py",
    "scripts/zigux/validate_phase3_selftest.py",
    "scripts/zigux/README.md",
    "zigux/tests/build.zig",
    "zigux/tests/README.md",
    "zigux/tests/phase3_abi.zig",
    "zigux/tests/phase3_abi_dump_current.zig",
    "zigux/tests/fixtures/phase3_abi_manifest.json",
    "Documentation/zigux/phase3-errptr-xarray-slice.md",
    "zigux/helpers/err_ptr.zig",
    "zigux/helpers/xa_value.zig",
    "zigux/tests/phase3_errptr_xarray_starter_packet.zig",
    "zigux/tests/phase3_errptr_xarray_starter_packet_build.zig",
    "zigux/tests/phase3_errptr_xarray_starter_packet_manifest.json",
    "zigux/tests/phase3_errptr_xarray_dump.zig",
    "zigux/tests/phase3_errptr_xarray_dump_build.zig",
    "Documentation/zigux/phase3-xarray-slot-slice.md",
    "zigux/helpers/xarray_slot_view.zig",
    "zigux/tests/phase3_xarray_slot_starter_packet.zig",
    "zigux/tests/phase3_xarray_slot_starter_packet_build.zig",
    "zigux/tests/phase3_xarray_slot_dump.zig",
    "zigux/tests/phase3_xarray_slot_dump_build.zig",
    "zigux/tests/fixtures/phase3_xarray_slot/phase3_xarray_slot_c_harness.c",
    "zigux/tests/fixtures/phase3_xarray_slot/expected.json",
    "zigux/tests/fixtures/phase3_xarray_slot_manifest.json",
    "Documentation/zigux/phase3-idr-slot-slice.md",
    "zigux/helpers/idr_slot_view.zig",
    "zigux/tests/phase3_idr_slot_starter_packet.zig",
    "zigux/tests/phase3_idr_slot_starter_packet_build.zig",
    "zigux/tests/phase3_idr_slot_dump.zig",
    "zigux/tests/phase3_idr_slot_dump_build.zig",
    "zigux/tests/fixtures/phase3_idr_slot/phase3_idr_slot_c_harness.c",
    "zigux/tests/fixtures/phase3_idr_slot/expected.json",
    "zigux/tests/fixtures/phase3_idr_slot_manifest.json",
    "scripts/zigux/check-phase3-idr-slot-starter-packet.py",
    "scripts/zigux/check-phase3-idr-slot.py",
    "zigux/tests/phase3_dev_t_starter_packet.zig",
    "zigux/tests/phase3_dev_t_starter_packet_build.zig",
    "zigux/tests/phase3_dev_t_starter_packet_manifest.json",
    "zigux/tests/phase3_policy_starter_packet.zig",
    "zigux/tests/phase3_policy_starter_packet_build.zig",
    "zigux/tests/phase3_policy_starter_packet_manifest.json",
    "zigux/tests/phase3_policy_dump.zig",
    "zigux/tests/phase3_policy_dump_build.zig",
    "zigux/tests/fixtures/phase3_policy_dump_expected.txt",
    "zigux/tests/phase3_export_uapi_c_header_smoke.c",
    "zigux/tests/phase3_export_uapi_layout.zig",
    "zigux/tests/phase3_export_uapi_layout_build.zig",
    "zigux/tests/phase3_export_shim_build.zig",
    "zigux/tests/phase3_low_level_wrappers.zig",
    "zigux/tests/phase3_low_level_wrappers_build.zig",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
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
    "zigux/tests/phase3_list_hlist_dump.zig",
    "zigux/tests/phase3_list_hlist_dump_build.zig",
    "zigux/tests/fixtures/phase3_list_hlist/phase3_list_hlist_c_harness.c",
    "zigux/tests/fixtures/phase3_list_hlist/expected.json",
    "zigux/tests/fixtures/phase3_list_hlist_manifest.json",
    "scripts/zigux/check-phase3-list-hlist-starter-packet.py",
    "scripts/zigux/check-phase3-list-hlist.py",
)

EXPECTED_REPLAY_ROUTES = (
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
    "zig build phase3-idr-slot-starter-packet-test --build-file zigux/tests/phase3_idr_slot_starter_packet_build.zig",
    "zig build phase3-idr-slot-dump --build-file zigux/tests/phase3_idr_slot_dump_build.zig",
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

FORBIDDEN_PACKET_FILES = (
    "zigux/tests/phase3_abi_dump.zig",
)

FORBIDDEN_REPLAY_ROUTE_MARKERS = (
    "phase3_abi_dump.zig",
    "phase3_abi_dump_build.zig",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _append_duplicate_list_entry_issues(label: str, values: list[object], issues: list[str]) -> None:
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


def _load_manifest(repo_root: Path) -> tuple[dict[str, object] | None, list[str]]:
    manifest_path = repo_root / MANIFEST_PATH
    try:
        manifest = json.loads(_read(manifest_path))
    except FileNotFoundError:
        return None, [f"missing repo file: {MANIFEST_PATH.as_posix()}"]
    except json.JSONDecodeError as exc:
        return None, [f"invalid JSON in {MANIFEST_PATH.as_posix()}: {exc}"]
    return manifest, []


def _packet_paths(manifest: dict[str, object]) -> list[str]:
    packet_files = manifest.get("packet_files")
    if not isinstance(packet_files, list):
        raise TypeError("phase3_abi_manifest.json packet_files is not a list")
    return [str(value) for value in packet_files]


def _replay_routes(manifest: dict[str, object]) -> list[str]:
    replay_routes = manifest.get("replay_routes")
    if not isinstance(replay_routes, list):
        raise TypeError("phase3_abi_manifest.json replay_routes is not a list")
    return [str(value) for value in replay_routes]


def _is_doc(path: str) -> bool:
    return path.startswith("Documentation/") or path == "scripts/zigux/README.md"


def _is_header(path: str) -> bool:
    return path.startswith("include/")


def _is_binding(path: str) -> bool:
    return path.startswith("zigux/uapi/") or path.startswith("zigux/bindings/")


def _is_helper(path: str) -> bool:
    return (
        path.startswith("zigux/helpers/")
        or path.startswith("zigux/kernel/")
        or path.startswith("zigux/unsafe/")
    )


def _is_validator(path: str) -> bool:
    return path.startswith("scripts/zigux/") and path != "scripts/zigux/README.md"


def _is_test(path: str) -> bool:
    return path.startswith("zigux/tests/") or path == "zigux/Makefile" or path.startswith(".github/")


def _categorize(packet_files: list[str]) -> dict[str, list[str]]:
    return {
        "docs": [path for path in packet_files if _is_doc(path)],
        "headers": [path for path in packet_files if _is_header(path)],
        "bindings": [path for path in packet_files if _is_binding(path)],
        "helpers": [path for path in packet_files if _is_helper(path)],
        "validators": [path for path in packet_files if _is_validator(path)],
        "tests": [path for path in packet_files if _is_test(path)],
    }


def validate_repo(repo_root: Path) -> list[str]:
    manifest, issues = _load_manifest(repo_root)
    if manifest is None:
        return issues

    if manifest.get("phase") != PHASE3_CATALOG_PHASE:
        issues.append(
            "phase3_abi_manifest.json wrong phase: "
            f"{manifest.get('phase')!r} != {PHASE3_CATALOG_PHASE!r}"
        )
    if manifest.get("lane") != PHASE3_CATALOG_SCOPE:
        issues.append(
            "phase3_abi_manifest.json wrong lane: "
            f"{manifest.get('lane')!r} != {PHASE3_CATALOG_SCOPE!r}"
        )
    if manifest.get("slug") != PHASE3_CATALOG_SLUG:
        issues.append(
            "phase3_abi_manifest.json wrong slug: "
            f"{manifest.get('slug')!r} != {PHASE3_CATALOG_SLUG!r}"
        )
    if manifest.get("status") != PHASE3_CATALOG_STATUS:
        issues.append(
            "phase3_abi_manifest.json wrong status: "
            f"{manifest.get('status')!r} != {PHASE3_CATALOG_STATUS!r}"
        )
    if manifest.get("scope") != PHASE3_CATALOG_MANIFEST_SCOPE:
        issues.append(
            "phase3_abi_manifest.json wrong scope: "
            f"{manifest.get('scope')!r} != {PHASE3_CATALOG_MANIFEST_SCOPE!r}"
        )
    if manifest.get("next_safe_step") != PHASE3_CATALOG_NEXT_SAFE_STEP:
        issues.append(
            "phase3_abi_manifest.json wrong next_safe_step: "
            f"{manifest.get('next_safe_step')!r} != {PHASE3_CATALOG_NEXT_SAFE_STEP!r}"
        )

    try:
        packet_files = _packet_paths(manifest)
        replay_routes = _replay_routes(manifest)
    except TypeError as exc:
        issues.append(str(exc))
        return issues

    if not packet_files:
        issues.append("phase3_abi_manifest.json packet_files must not be empty")
    if not replay_routes:
        issues.append("phase3_abi_manifest.json replay_routes must not be empty")

    _append_duplicate_list_entry_issues("phase3_abi_manifest.json packet_files", packet_files, issues)
    _append_duplicate_list_entry_issues("phase3_abi_manifest.json replay_routes", replay_routes, issues)

    for legacy_path in FORBIDDEN_PACKET_FILES:
        if legacy_path in packet_files:
            issues.append(f"forbidden stale packet file entry: {legacy_path}")
    for route in replay_routes:
        for legacy_marker in FORBIDDEN_REPLAY_ROUTE_MARKERS:
            if legacy_marker in route:
                issues.append(f"forbidden stale replay-route marker: {legacy_marker} in {route}")

    for relative_path in packet_files:
        if not (repo_root / relative_path).is_file():
            issues.append(f"missing repo file: {relative_path}")

    for expected_path in EXPECTED_PACKET_FILES:
        if expected_path not in packet_files:
            issues.append(f"phase3_abi_manifest.json missing packet_files entry: {expected_path}")
    for relative_path in packet_files:
        if relative_path not in EXPECTED_PACKET_FILES:
            issues.append(
                "phase3_abi_manifest.json unexpected packet_files entry outside "
                f"phase3_catalog inventory: {relative_path}"
            )

    for expected_route in EXPECTED_REPLAY_ROUTES:
        if expected_route not in replay_routes:
            issues.append(f"phase3_abi_manifest.json missing replay route: {expected_route}")
    for route in replay_routes:
        if route not in EXPECTED_REPLAY_ROUTES:
            issues.append(
                "phase3_abi_manifest.json unexpected replay route outside "
                f"phase3_catalog inventory: {route}"
            )

    categories = _categorize(packet_files)
    categorized_count = sum(len(values) for values in categories.values())
    if categorized_count != len(packet_files):
        categorized = {value for values in categories.values() for value in values}
        for path in packet_files:
            if path not in categorized:
                issues.append(f"uncategorized packet file: {path}")

    return issues


def build_catalog(repo_root: Path) -> dict[str, object]:
    manifest, issues = _load_manifest(repo_root)
    if manifest is None:
        raise ValueError("\n".join(issues))

    packet_files = _packet_paths(manifest)
    replay_routes = _replay_routes(manifest)
    categories = _categorize(packet_files)
    return {
        "phase": manifest.get("phase", PHASE3_CATALOG_PHASE),
        "scope": manifest.get("lane", PHASE3_CATALOG_SCOPE),
        "docs": categories["docs"],
        "headers": categories["headers"],
        "bindings": categories["bindings"],
        "helpers": categories["helpers"],
        "validators": categories["validators"],
        "tests": categories["tests"],
        "commands": replay_routes,
    }


def _manifest_payload() -> dict[str, object]:
    return {
        "phase": PHASE3_CATALOG_PHASE,
        "lane": PHASE3_CATALOG_SCOPE,
        "slug": PHASE3_CATALOG_SLUG,
        "status": PHASE3_CATALOG_STATUS,
        "scope": PHASE3_CATALOG_MANIFEST_SCOPE,
        "packet_files": list(EXPECTED_PACKET_FILES),
        "replay_routes": list(EXPECTED_REPLAY_ROUTES),
        "repo_reality_gaps": [],
        "next_safe_step": PHASE3_CATALOG_NEXT_SAFE_STEP,
    }


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_catalog_") as tmp_dir:
        root = Path(tmp_dir)
        for relative_path in EXPECTED_PACKET_FILES:
            _write(root / relative_path, "// self-test\n")
        _write(root / MANIFEST_PATH, json.dumps(_manifest_payload(), indent=2) + "\n")

        issues = validate_repo(root)
        if issues:
            print("PHASE3_CATALOG_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        catalog = build_catalog(root)
        expected_categories = _categorize(list(EXPECTED_PACKET_FILES))
        for key, values in expected_categories.items():
            if len(catalog[key]) != len(values):
                print("PHASE3_CATALOG_SELF_TEST=fail")
                print(f"unexpected {key} count: {len(catalog[key])} != {len(values)}")
                return 1
        if len(catalog["commands"]) != len(EXPECTED_REPLAY_ROUTES):
            print("PHASE3_CATALOG_SELF_TEST=fail")
            print(
                "unexpected commands count: "
                f"{len(catalog['commands'])} != {len(EXPECTED_REPLAY_ROUTES)}"
            )
            return 1

        missing_probe = root / EXPECTED_PACKET_FILES[-1]
        missing_probe.unlink()
        issues = validate_repo(root)
        expected_missing = f"missing repo file: {EXPECTED_PACKET_FILES[-1]}"
        if expected_missing not in issues:
            print("PHASE3_CATALOG_SELF_TEST=fail")
            print("expected missing packet member was not reported")
            return 1

        _write(root / MANIFEST_PATH, json.dumps({**_manifest_payload(), "packet_files": "oops"}, indent=2) + "\n")
        issues = validate_repo(root)
        expected_list_issue = "phase3_abi_manifest.json packet_files is not a list"
        if expected_list_issue not in issues:
            print("PHASE3_CATALOG_SELF_TEST=fail")
            print("expected non-list packet_files issue was not reported")
            return 1

        _write(
            root / MANIFEST_PATH,
            json.dumps(
                {
                    **_manifest_payload(),
                    "replay_routes": [EXPECTED_REPLAY_ROUTES[0], EXPECTED_REPLAY_ROUTES[0]],
                },
                indent=2,
            )
            + "\n",
        )
        issues = validate_repo(root)
        expected_duplicate = "phase3_abi_manifest.json replay_routes duplicate entry:"
        if not any(issue.startswith(expected_duplicate) for issue in issues):
            print("PHASE3_CATALOG_SELF_TEST=fail")
            print("expected duplicate replay route was not reported")
            return 1

        manifest_with_legacy_packet = _manifest_payload()
        manifest_with_legacy_packet["packet_files"] = list(EXPECTED_PACKET_FILES) + [
            FORBIDDEN_PACKET_FILES[0],
        ]
        _write(root / MANIFEST_PATH, json.dumps(manifest_with_legacy_packet, indent=2) + "\n")
        issues = validate_repo(root)
        expected_legacy_packet = f"forbidden stale packet file entry: {FORBIDDEN_PACKET_FILES[0]}"
        if expected_legacy_packet not in issues:
            print("PHASE3_CATALOG_SELF_TEST=fail")
            print("expected stale dump packet-file drift was not reported")
            return 1

        manifest_with_legacy_route = _manifest_payload()
        manifest_with_legacy_route["replay_routes"] = list(EXPECTED_REPLAY_ROUTES) + [
            "zig build phase3-dump --build-file zigux/tests/phase3_abi_dump_build.zig",
        ]
        _write(root / MANIFEST_PATH, json.dumps(manifest_with_legacy_route, indent=2) + "\n")
        issues = validate_repo(root)
        expected_legacy_route = (
            "forbidden stale replay-route marker: phase3_abi_dump_build.zig "
            "in zig build phase3-dump --build-file zigux/tests/phase3_abi_dump_build.zig"
        )
        if expected_legacy_route not in issues:
            print("PHASE3_CATALOG_SELF_TEST=fail")
            print("expected stale dump replay-route drift was not reported")
            return 1

        manifest_with_untracked_packet = _manifest_payload()
        manifest_with_untracked_packet["packet_files"] = list(EXPECTED_PACKET_FILES) + [
            "zigux/tests/phase3_untracked_probe.zig",
        ]
        _write(root / "zigux/tests/phase3_untracked_probe.zig", "// self-test\n")
        _write(root / MANIFEST_PATH, json.dumps(manifest_with_untracked_packet, indent=2) + "\n")
        issues = validate_repo(root)
        expected_untracked_packet = (
            "phase3_abi_manifest.json unexpected packet_files entry outside "
            "phase3_catalog inventory: zigux/tests/phase3_untracked_probe.zig"
        )
        if expected_untracked_packet not in issues:
            print("PHASE3_CATALOG_SELF_TEST=fail")
            print("expected untracked packet-file drift was not reported")
            return 1

        manifest_with_untracked_route = _manifest_payload()
        manifest_with_untracked_route["replay_routes"] = list(EXPECTED_REPLAY_ROUTES) + [
            "python3 scripts/zigux/check-phase3-untracked.py",
        ]
        _write(root / MANIFEST_PATH, json.dumps(manifest_with_untracked_route, indent=2) + "\n")
        issues = validate_repo(root)
        expected_untracked_route = (
            "phase3_abi_manifest.json unexpected replay route outside "
            "phase3_catalog inventory: python3 scripts/zigux/check-phase3-untracked.py"
        )
        if expected_untracked_route not in issues:
            print("PHASE3_CATALOG_SELF_TEST=fail")
            print("expected untracked replay-route drift was not reported")
            return 1

        _write(root / MANIFEST_PATH, json.dumps({**_manifest_payload(), "scope": "stale scope"}, indent=2) + "\n")
        issues = validate_repo(root)
        expected_scope_issue = "phase3_abi_manifest.json wrong scope: 'stale scope' != "
        if not any(issue.startswith(expected_scope_issue) for issue in issues):
            print("PHASE3_CATALOG_SELF_TEST=fail")
            print("expected stale scope drift was not reported")
            return 1

        _write(
            root / MANIFEST_PATH,
            json.dumps({**_manifest_payload(), "next_safe_step": "stale next step"}, indent=2) + "\n",
        )
        issues = validate_repo(root)
        expected_next_step_issue = "phase3_abi_manifest.json wrong next_safe_step: 'stale next step' != "
        if not any(issue.startswith(expected_next_step_issue) for issue in issues):
            print("PHASE3_CATALOG_SELF_TEST=fail")
            print("expected stale next-safe-step drift was not reported")
            return 1

    print("PHASE3_CATALOG_SELF_TEST=pass")
    print("PHASE3_CATALOG_SELF_TEST_CASE_COUNT=11")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Inventory the current bounded Phase 3 ABI support packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the current Phase 3 ABI support packet",
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
