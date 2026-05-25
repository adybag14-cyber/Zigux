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
    '"python3 scripts/zigux/check-phase3-abi.py --self-test"',
    '"python3 scripts/zigux/check-phase3-abi.py"',
    '"python3 scripts/zigux/check-phase3-abi-manifest-replay-routes.py --self-test"',
    '"python3 scripts/zigux/check-phase3-abi-manifest-replay-routes.py"',
    '"python3 scripts/zigux/check-phase3-abi-support-packet.py --self-test"',
    '"python3 scripts/zigux/check-phase3-abi-support-packet.py"',
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
    '"zig build phase3-dev-t-starter-packet-test --build-file zigux/tests/phase3_dev_t_starter_packet_build.zig --summary all"',
    '"zig build phase3-xarray-slot-starter-packet-test --build-file zigux/tests/phase3_xarray_slot_starter_packet_build.zig"',
    '"zig build phase3-xarray-slot-dump --build-file zigux/tests/phase3_xarray_slot_dump_build.zig"',
    '"zig build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig"',
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
    "zigux/tests/phase3_dev_t_starter_packet.zig",
    "zigux/tests/phase3_dev_t_starter_packet_build.zig",
    "zigux/tests/phase3_dev_t_starter_packet_manifest.json",
    "zigux/tests/phase3_export_uapi_layout.zig",
    "zigux/tests/phase3_export_uapi_layout_build.zig",
    "zigux/tests/phase3_export_shim_build.zig",
    "zigux/tests/phase3_policy_dump.zig",
    "zigux/tests/phase3_policy_dump_build.zig",
    "zigux/tests/fixtures/phase3_policy_dump_expected.txt",
    "scripts/zigux/check-phase3-policy-dump.py",
    "scripts/zigux/validate_phase3_selftest.py",
    "scripts/zigux/run-phase3-checks.py",
)

REQUIRED_REPLAY_ROUTES = (
    "python3 scripts/zigux/check-phase3-abi.py --self-test",
    "python3 scripts/zigux/check-phase3-abi.py",
    "python3 scripts/zigux/check-phase3-abi-manifest-replay-routes.py --self-test",
    "python3 scripts/zigux/check-phase3-abi-manifest-replay-routes.py",
    "python3 scripts/zigux/check-phase3-abi-support-packet.py --self-test",
    "python3 scripts/zigux/check-phase3-abi-support-packet.py",
    "python3 scripts/zigux/validate-phase3.py --self-test",
    "python3 scripts/zigux/validate-phase3.py",
    "python3 scripts/zigux/check-phase3-selftest-surface.py --self-test",
    "python3 scripts/zigux/check-phase3-selftest-surface.py",
    "python3 scripts/zigux/validate-phase3-validator-support-surface.py --self-test",
    "python3 scripts/zigux/validate-phase3-validator-support-surface.py",
    "python3 scripts/zigux/validate-phase3-export-uapi-survey.py --self-test",
    "python3 scripts/zigux/validate-phase3-export-uapi-survey.py",
    "python3 scripts/zigux/check-phase3-export-uapi-c-header-smoke.py --self-test",
    "python3 scripts/zigux/check-phase3-export-uapi-c-header-smoke.py",
    "python3 scripts/zigux/validate-phase3-policy-unsafe-survey.py --self-test",
    "python3 scripts/zigux/validate-phase3-policy-unsafe-survey.py",
    "python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test",
    "python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    "python3 scripts/zigux/validate-phase3-linux-zigux-header-governance.py --self-test",
    "python3 scripts/zigux/validate-phase3-linux-zigux-header-governance.py",
    "python3 scripts/zigux/check-phase3-policy-starter-packet.py --self-test",
    "python3 scripts/zigux/check-phase3-policy-starter-packet.py",
    "python3 scripts/zigux/check-phase3-policy-dump.py --self-test",
    "python3 scripts/zigux/check-phase3-policy-dump.py",
    "python3 scripts/zigux/check-phase3-dev-t-starter-packet.py --self-test",
    "python3 scripts/zigux/check-phase3-dev-t-starter-packet.py",
    "python3 scripts/zigux/check-phase3-errptr-xarray-starter-packet.py --self-test",
    "python3 scripts/zigux/check-phase3-errptr-xarray-starter-packet.py",
    "python3 scripts/zigux/check-phase3-xarray-slot-starter-packet.py --self-test",
    "python3 scripts/zigux/check-phase3-xarray-slot-starter-packet.py",
    "python3 scripts/zigux/check-phase3-xarray-slot.py --self-test",
    "python3 scripts/zigux/check-phase3-xarray-slot.py",
    "python3 scripts/zigux/check-phase3-shared-tests-routes.py --self-test",
    "python3 scripts/zigux/check-phase3-shared-tests-routes.py",
    "python3 scripts/zigux/check-phase3-catalog-selftest.py --self-test",
    "python3 scripts/zigux/check-phase3-catalog-selftest.py",
    "python3 scripts/zigux/validate-phase3-abi-header-family-survey.py --self-test",
    "python3 scripts/zigux/validate-phase3-abi-header-family-survey.py",
    "python3 scripts/zigux/validate_phase3_selftest.py",
    "python3 scripts/zigux/run-phase3-checks.py",
    "zig build phase3-dev-t-starter-packet-test --build-file zigux/tests/phase3_dev_t_starter_packet_build.zig --summary all",
    "zig build phase3-xarray-slot-starter-packet-test --build-file zigux/tests/phase3_xarray_slot_starter_packet_build.zig",
    "zig build phase3-xarray-slot-dump --build-file zigux/tests/phase3_xarray_slot_dump_build.zig",
    "zig build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig",
    "zig build phase3-abi-core-packet --build-file zigux/tests/build.zig",
    "zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig",
    "zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
    "zig build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig",
    "make -C zigux phase3-export-shim-test",
    "zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig",
    "make -C zigux phase3-policy-dump",
    "zig build phase3-dump --build-file zigux/tests/build.zig",
    "make -C zigux phase3-dump",
    "zig build phase3-low-level-wrappers --build-file zigux/tests/build.zig",
    "make -C zigux phase3-low-level-wrappers",
    "zig build phase3-test --build-file zigux/tests/build.zig",
    "make -C zigux phase3-test",
    "make -C zigux phase3",
    "zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    "make -C zigux phase3-export-uapi-layout",
    "make -C zigux phase3-export-uapi-layout-test",
    "make -C zigux phase3-low-level-wrappers-test",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


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
        for entry in REQUIRED_PACKET_FILES:
            if entry not in packet_files:
                issues.append(f"phase3_abi_manifest.json missing packet_files entry: {entry}")

    replay_routes = manifest.get("replay_routes")
    if not isinstance(replay_routes, list):
        issues.append("phase3_abi_manifest.json replay_routes is not a list")
        return issues

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


def _remove_validator_marker(repo_root: Path, marker: str) -> None:
    validator_path = repo_root / VALIDATOR_PATH
    current = _read(validator_path)
    needle = f"    {marker},\n"
    _write(validator_path, current.replace(needle, "", 1))


def _expect_issue(issues: list[str], expected: str, failure_message: str) -> None:
    if expected not in issues:
        print("PHASE3_ABI_MANIFEST_REPLAY_ROUTES_SELF_TEST=fail")
        print(failure_message)
        raise SystemExit(1)


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_abi_manifest_routes_") as temp_dir:
        repo_root = Path(temp_dir)
        _populate_repo(repo_root)

        issues = validate_repo(repo_root)
        if issues:
            print("PHASE3_ABI_MANIFEST_REPLAY_ROUTES_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        validator_cases = (
            ('"scripts/zigux/check-phase3-abi-manifest-replay-routes.py"', "expected validator packet-file marker drift was not reported"),
            ('"scripts/zigux/check-phase3-abi-support-packet.py"', "expected support-packet validator file-marker drift was not reported"),
            ('"python3 scripts/zigux/check-phase3-abi.py --self-test"', "expected shared ABI self-test validator-route drift was not reported"),
            ('"python3 scripts/zigux/check-phase3-abi.py"', "expected shared ABI direct validator-route drift was not reported"),
            ('"python3 scripts/zigux/check-phase3-abi-manifest-replay-routes.py --self-test"', "expected validator self-test route drift was not reported"),
            ('"python3 scripts/zigux/check-phase3-abi-manifest-replay-routes.py"', "expected validator direct route drift was not reported"),
            ('"python3 scripts/zigux/check-phase3-abi-support-packet.py --self-test"', "expected support-packet self-test validator-route drift was not reported"),
            ('"python3 scripts/zigux/check-phase3-abi-support-packet.py"', "expected support-packet direct validator-route drift was not reported"),
            ('"python3 scripts/zigux/validate-phase3.py --self-test"', "expected validate-phase3 self-test validator-route drift was not reported"),
            ('"python3 scripts/zigux/validate-phase3.py"', "expected validate-phase3 direct validator-route drift was not reported"),
            ('"python3 scripts/zigux/check-phase3-selftest-surface.py --self-test"', "expected selftest-surface self-test validator-route drift was not reported"),
            ('"python3 scripts/zigux/check-phase3-selftest-surface.py"', "expected validator-route drift was not reported"),
            ('"python3 scripts/zigux/validate-phase3-validator-support-surface.py --self-test"', "expected validator-support self-test validator-route drift was not reported"),
            ('"python3 scripts/zigux/validate-phase3-validator-support-surface.py"', "expected validator-support direct validator-route drift was not reported"),
            ('"python3 scripts/zigux/validate-phase3-export-uapi-survey.py --self-test"', "expected export-uapi survey self-test validator-route drift was not reported"),
            ('"python3 scripts/zigux/validate-phase3-export-uapi-survey.py"', "expected export-uapi survey direct validator-route drift was not reported"),
            ('"python3 scripts/zigux/check-phase3-export-uapi-c-header-smoke.py --self-test"', "expected export-uapi c-header smoke self-test validator-route drift was not reported"),
            ('"python3 scripts/zigux/check-phase3-export-uapi-c-header-smoke.py"', "expected export-uapi c-header smoke validator-route drift was not reported"),
            ('"zig build phase3-abi-core-packet --build-file zigux/tests/build.zig"', "expected shared ABI core build validator-route drift was not reported"),
            ('"zig build phase3-xarray-slot-starter-packet-test --build-file zigux/tests/phase3_xarray_slot_starter_packet_build.zig"', "expected xarray slot starter build validator-route drift was not reported"),
            ('"zig build phase3-xarray-slot-dump --build-file zigux/tests/phase3_xarray_slot_dump_build.zig"', "expected xarray slot dump build validator-route drift was not reported"),
            ('"zig build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig"', "expected policy-starter build validator-route drift was not reported"),
            ('"zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig"', "expected export-uapi layout build validator-route drift was not reported"),
            ('"zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig"', "expected export-uapi layout test validator-route drift was not reported"),
            ('"zig build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig"', "expected export-shim validator-route drift was not reported"),
            ('"make -C zigux phase3-export-shim-test"', "expected export-shim make-route drift was not reported"),
            ('"python3 scripts/zigux/validate-phase3-policy-unsafe-survey.py --self-test"', "expected policy-unsafe self-test validator-route drift was not reported"),
            ('"python3 scripts/zigux/validate-phase3-policy-unsafe-survey.py"', "expected policy-unsafe direct validator-route drift was not reported"),
            ('"python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test"', "expected low-level-wrapper self-test validator-route drift was not reported"),
            ('"python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py"', "expected low-level-wrapper direct validator-route drift was not reported"),
            ('"python3 scripts/zigux/validate-phase3-linux-zigux-header-governance.py --self-test"', "expected header-governance self-test validator-route drift was not reported"),
            ('"python3 scripts/zigux/validate-phase3-linux-zigux-header-governance.py"', "expected header-governance direct validator-route drift was not reported"),
            ('"python3 scripts/zigux/check-phase3-policy-starter-packet.py --self-test"', "expected policy-starter self-test validator-route drift was not reported"),
            ('"python3 scripts/zigux/check-phase3-policy-starter-packet.py"', "expected policy-starter direct validator-route drift was not reported"),
            ('"python3 scripts/zigux/check-phase3-policy-dump.py --self-test"', "expected policy-dump self-test validator-route drift was not reported"),
            ('"python3 scripts/zigux/check-phase3-policy-dump.py"', "expected policy-dump direct validator-route drift was not reported"),
            ('"python3 scripts/zigux/check-phase3-dev-t-starter-packet.py --self-test"', "expected dev-t starter self-test validator-route drift was not reported"),
            ('"python3 scripts/zigux/check-phase3-dev-t-starter-packet.py"', "expected dev-t starter direct validator-route drift was not reported"),
            ('"python3 scripts/zigux/check-phase3-errptr-xarray-starter-packet.py --self-test"', "expected errptr-xarray starter self-test validator-route drift was not reported"),
            ('"python3 scripts/zigux/check-phase3-errptr-xarray-starter-packet.py"', "expected errptr-xarray starter direct validator-route drift was not reported"),
            ('"python3 scripts/zigux/check-phase3-xarray-slot-starter-packet.py --self-test"', "expected xarray slot starter self-test validator-route drift was not reported"),
            ('"python3 scripts/zigux/check-phase3-xarray-slot-starter-packet.py"', "expected xarray slot starter direct validator-route drift was not reported"),
            ('"python3 scripts/zigux/check-phase3-xarray-slot.py --self-test"', "expected xarray slot self-test validator-route drift was not reported"),
            ('"python3 scripts/zigux/check-phase3-xarray-slot.py"', "expected xarray slot direct validator-route drift was not reported"),
            ('"python3 scripts/zigux/check-phase3-shared-tests-routes.py --self-test"', "expected shared-tests-routes self-test validator-route drift was not reported"),
            ('"python3 scripts/zigux/check-phase3-shared-tests-routes.py"', "expected shared-tests-routes direct validator-route drift was not reported"),
            ('"python3 scripts/zigux/check-phase3-catalog-selftest.py --self-test"', "expected catalog-selftest self-test validator-route drift was not reported"),
            ('"python3 scripts/zigux/check-phase3-catalog-selftest.py"', "expected catalog-selftest direct validator-route drift was not reported"),
            ('"python3 scripts/zigux/validate-phase3-abi-header-family-survey.py --self-test"', "expected abi-header-family survey self-test validator-route drift was not reported"),
            ('"python3 scripts/zigux/validate-phase3-abi-header-family-survey.py"', "expected abi-header-family survey direct validator-route drift was not reported"),
            ('"python3 scripts/zigux/validate_phase3_selftest.py"', "expected selftest-driver validator-route drift was not reported"),
            ('"python3 scripts/zigux/run-phase3-checks.py"', "expected runner validator-route drift was not reported"),
            ('"zig build phase3-dev-t-starter-packet-test --build-file zigux/tests/phase3_dev_t_starter_packet_build.zig --summary all"', "expected dev-t starter build validator-route drift was not reported"),
            ('"zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig"', "expected policy-dump build validator-route drift was not reported"),
            ('"make -C zigux phase3-policy-dump"', "expected policy-dump make-route drift was not reported"),
            ('"zig build phase3-dump --build-file zigux/tests/build.zig"', "expected shared ABI dump build validator-route drift was not reported"),
            ('"make -C zigux phase3-dump"', "expected shared ABI dump make-route drift was not reported"),
            ('"zig build phase3-low-level-wrappers --build-file zigux/tests/build.zig"', "expected low-level-wrapper shared build validator-route drift was not reported"),
            ('"make -C zigux phase3-low-level-wrappers"', "expected low-level-wrapper shared make-route drift was not reported"),
            ('"zig build phase3-test --build-file zigux/tests/build.zig"', "expected shared ABI aggregate build validator-route drift was not reported"),
            ('"make -C zigux phase3-test"', "expected shared ABI aggregate make-route drift was not reported"),
            ('"make -C zigux phase3"', "expected shared ABI top-level make-route drift was not reported"),
            ('"zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig"', "expected low-level-wrapper focused build validator-route drift was not reported"),
            ('"make -C zigux phase3-low-level-wrappers-test"', "expected low-level-wrapper focused make-route drift was not reported"),
            ('"make -C zigux phase3-export-uapi-layout"', "expected export-uapi shared make route drift was not reported"),
            ('"make -C zigux phase3-export-uapi-layout-test"', "expected export-uapi dedicated make route drift was not reported"),
        )
        for marker, failure_message in validator_cases:
            _populate_repo(repo_root)
            _remove_validator_marker(repo_root, marker)
            issues = validate_repo(repo_root)
            expected = f"missing {VALIDATOR_PATH.as_posix()} marker: {marker}"
            _expect_issue(issues, expected, failure_message)

        packet_file_cases = (
            ("scripts/zigux/check-phase3-abi-manifest-replay-routes.py", "expected checker packet-file drift was not reported"),
            ("scripts/zigux/check-phase3-abi-support-packet.py", "expected support-packet packet-file drift was not reported"),
            ("Documentation/zigux/phase3-export-uapi-boundary-survey.md", "expected export-uapi survey note packet-file drift was not reported"),
            ("scripts/zigux/validate-phase3-export-uapi-survey.py", "expected export-uapi survey validator packet-file drift was not reported"),
            ("Documentation/zigux/phase3-validator-support-surface.md", "expected validator-support note packet-file drift was not reported"),
            ("scripts/zigux/validate-phase3-validator-support-surface.py", "expected validator-support validator packet-file drift was not reported"),
            ("Documentation/zigux/phase3-policy-unsafe-boundary-survey.md", "expected policy-unsafe note packet-file drift was not reported"),
            ("scripts/zigux/validate-phase3-policy-unsafe-survey.py", "expected policy-unsafe validator packet-file drift was not reported"),
            ("Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md", "expected low-level-wrapper note packet-file drift was not reported"),
            ("scripts/zigux/validate-phase3-low-level-wrapper-survey.py", "expected low-level-wrapper validator packet-file drift was not reported"),
            ("Documentation/zigux/phase3-linux-zigux-header-governance.md", "expected header-governance note packet-file drift was not reported"),
            ("scripts/zigux/validate-phase3-linux-zigux-header-governance.py", "expected header-governance validator packet-file drift was not reported"),
            ("include/zigux/dev_t.h", "expected dev_t header packet-file drift was not reported"),
            ("zigux/uapi/dev_t.zig", "expected dev_t uapi packet-file drift was not reported"),
            ("zigux/bindings/dev_t.zig", "expected dev_t binding packet-file drift was not reported"),
            ("scripts/zigux/check-phase3-dev-t-starter-packet.py", "expected dev-t starter checker packet-file drift was not reported"),
            ("Documentation/zigux/phase3-errptr-xarray-slice.md", "expected errptr-xarray note packet-file drift was not reported"),
            ("zigux/helpers/err_ptr.zig", "expected err_ptr helper packet-file drift was not reported"),
            ("zigux/helpers/xa_value.zig", "expected xa_value helper packet-file drift was not reported"),
            ("scripts/zigux/check-phase3-errptr-xarray-starter-packet.py", "expected errptr-xarray starter checker packet-file drift was not reported"),
            ("zigux/tests/phase3_errptr_xarray_starter_packet.zig", "expected errptr-xarray starter packet-file drift was not reported"),
            ("zigux/tests/phase3_errptr_xarray_starter_packet_build.zig", "expected errptr-xarray starter build packet-file drift was not reported"),
            ("zigux/tests/phase3_errptr_xarray_starter_packet_manifest.json", "expected errptr-xarray starter manifest packet-file drift was not reported"),
            ("Documentation/zigux/phase3-xarray-slot-slice.md", "expected xarray slot note packet-file drift was not reported"),
            ("zigux/helpers/xarray_slot_view.zig", "expected xarray slot helper packet-file drift was not reported"),
            ("scripts/zigux/check-phase3-xarray-slot-starter-packet.py", "expected xarray slot starter checker packet-file drift was not reported"),
            ("scripts/zigux/check-phase3-xarray-slot.py", "expected xarray slot checker packet-file drift was not reported"),
            ("zigux/tests/phase3_xarray_slot_starter_packet.zig", "expected xarray slot starter packet-file drift was not reported"),
            ("zigux/tests/phase3_xarray_slot_starter_packet_build.zig", "expected xarray slot starter build packet-file drift was not reported"),
            ("zigux/tests/phase3_xarray_slot_dump.zig", "expected xarray slot dump packet-file drift was not reported"),
            ("zigux/tests/phase3_xarray_slot_dump_build.zig", "expected xarray slot dump build packet-file drift was not reported"),
            ("zigux/tests/fixtures/phase3_xarray_slot/phase3_xarray_slot_c_harness.c", "expected xarray slot C harness packet-file drift was not reported"),
            ("zigux/tests/fixtures/phase3_xarray_slot/expected.json", "expected xarray slot expected-json packet-file drift was not reported"),
            ("zigux/tests/fixtures/phase3_xarray_slot_manifest.json", "expected xarray slot manifest packet-file drift was not reported"),
            ("zigux/tests/phase3_export_uapi_c_header_smoke.c", "expected export-uapi c-header smoke packet-file drift was not reported"),
            ("scripts/zigux/check-phase3-export-uapi-c-header-smoke.py", "expected export-uapi c-header smoke checker packet-file drift was not reported"),
            ("zigux/tests/phase3_dev_t_starter_packet.zig", "expected dev-t starter replay packet-file drift was not reported"),
            ("zigux/tests/phase3_dev_t_starter_packet_build.zig", "expected dev-t starter build packet-file drift was not reported"),
            ("zigux/tests/phase3_dev_t_starter_packet_manifest.json", "expected dev-t starter manifest packet-file drift was not reported"),
            ("zigux/tests/phase3_export_uapi_layout.zig", "expected export-uapi layout replay packet-file drift was not reported"),
            ("zigux/tests/phase3_export_uapi_layout_build.zig", "expected export-uapi layout build packet-file drift was not reported"),
            ("zigux/tests/phase3_export_shim_build.zig", "expected export-shim build packet-file drift was not reported"),
            ("zigux/tests/phase3_policy_dump.zig", "expected policy-dump packet-file drift was not reported"),
            ("scripts/zigux/validate_phase3_selftest.py", "expected selftest-driver packet-file drift was not reported"),
            ("scripts/zigux/run-phase3-checks.py", "expected runner packet-file drift was not reported"),
        )
        manifest_path = repo_root / MANIFEST_PATH
        for entry, failure_message in packet_file_cases:
            _populate_repo(repo_root)
            manifest = json.loads(_read(manifest_path))
            manifest["packet_files"].remove(entry)
            _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
            issues = validate_repo(repo_root)
            expected = f"phase3_abi_manifest.json missing packet_files entry: {entry}"
            _expect_issue(issues, expected, failure_message)

        replay_route_cases = (
            ("python3 scripts/zigux/check-phase3-abi.py --self-test", "expected shared ABI self-test route drift was not reported"),
            ("python3 scripts/zigux/check-phase3-abi.py", "expected shared ABI direct route drift was not reported"),
            ("python3 scripts/zigux/check-phase3-abi-manifest-replay-routes.py --self-test", "expected checker self-test route drift was not reported"),
            ("python3 scripts/zigux/check-phase3-abi-manifest-replay-routes.py", "expected checker direct route drift was not reported"),
            ("python3 scripts/zigux/check-phase3-abi-support-packet.py --self-test", "expected support-packet self-test route drift was not reported"),
            ("python3 scripts/zigux/check-phase3-abi-support-packet.py", "expected support-packet direct route drift was not reported"),
            ("python3 scripts/zigux/validate-phase3.py --self-test", "expected validate-phase3 self-test route drift was not reported"),
            ("python3 scripts/zigux/validate-phase3.py", "expected validate-phase3 direct route drift was not reported"),
            ("python3 scripts/zigux/check-phase3-selftest-surface.py --self-test", "expected selftest-surface self-test route drift was not reported"),
            ("python3 scripts/zigux/check-phase3-selftest-surface.py", "expected selftest-surface direct route drift was not reported"),
            ("python3 scripts/zigux/validate-phase3-validator-support-surface.py --self-test", "expected validator-support self-test route drift was not reported"),
            ("python3 scripts/zigux/validate-phase3-validator-support-surface.py", "expected validator-support direct route drift was not reported"),
            ("python3 scripts/zigux/validate-phase3-export-uapi-survey.py --self-test", "expected export-uapi survey self-test route drift was not reported"),
            ("python3 scripts/zigux/validate-phase3-export-uapi-survey.py", "expected export-uapi survey direct route drift was not reported"),
            ("python3 scripts/zigux/check-phase3-export-uapi-c-header-smoke.py --self-test", "expected export-uapi c-header smoke self-test route drift was not reported"),
            ("python3 scripts/zigux/check-phase3-export-uapi-c-header-smoke.py", "expected export-uapi c-header smoke route drift was not reported"),
            ("python3 scripts/zigux/validate-phase3-policy-unsafe-survey.py --self-test", "expected policy-unsafe self-test route drift was not reported"),
            ("python3 scripts/zigux/validate-phase3-policy-unsafe-survey.py", "expected policy-unsafe direct route drift was not reported"),
            ("python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test", "expected low-level-wrapper self-test route drift was not reported"),
            ("python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py", "expected low-level-wrapper direct route drift was not reported"),
            ("python3 scripts/zigux/validate-phase3-linux-zigux-header-governance.py --self-test", "expected header-governance self-test route drift was not reported"),
            ("python3 scripts/zigux/validate-phase3-linux-zigux-header-governance.py", "expected header-governance direct route drift was not reported"),
            ("python3 scripts/zigux/check-phase3-policy-starter-packet.py --self-test", "expected policy-starter self-test route drift was not reported"),
            ("python3 scripts/zigux/check-phase3-policy-starter-packet.py", "expected policy-starter direct route drift was not reported"),
            ("python3 scripts/zigux/check-phase3-policy-dump.py", "expected policy-dump direct route drift was not reported"),
            ("python3 scripts/zigux/check-phase3-dev-t-starter-packet.py --self-test", "expected dev-t starter self-test route drift was not reported"),
            ("python3 scripts/zigux/check-phase3-dev-t-starter-packet.py", "expected dev-t starter direct route drift was not reported"),
            ("python3 scripts/zigux/check-phase3-errptr-xarray-starter-packet.py --self-test", "expected errptr-xarray starter self-test route drift was not reported"),
            ("python3 scripts/zigux/check-phase3-errptr-xarray-starter-packet.py", "expected errptr-xarray starter direct route drift was not reported"),
            ("python3 scripts/zigux/check-phase3-xarray-slot-starter-packet.py --self-test", "expected xarray slot starter self-test route drift was not reported"),
            ("python3 scripts/zigux/check-phase3-xarray-slot-starter-packet.py", "expected xarray slot starter direct route drift was not reported"),
            ("python3 scripts/zigux/check-phase3-xarray-slot.py --self-test", "expected xarray slot self-test route drift was not reported"),
            ("python3 scripts/zigux/check-phase3-xarray-slot.py", "expected xarray slot direct route drift was not reported"),
            ("python3 scripts/zigux/check-phase3-shared-tests-routes.py --self-test", "expected shared-tests-routes self-test route drift was not reported"),
            ("python3 scripts/zigux/check-phase3-shared-tests-routes.py", "expected shared-tests-routes direct route drift was not reported"),
            ("python3 scripts/zigux/check-phase3-catalog-selftest.py --self-test", "expected catalog-selftest self-test route drift was not reported"),
            ("python3 scripts/zigux/check-phase3-catalog-selftest.py", "expected catalog-selftest direct route drift was not reported"),
            ("python3 scripts/zigux/validate-phase3-abi-header-family-survey.py --self-test", "expected abi-header-family survey self-test route drift was not reported"),
            ("python3 scripts/zigux/validate-phase3-abi-header-family-survey.py", "expected abi-header-family survey direct route drift was not reported"),
            ("python3 scripts/zigux/validate_phase3_selftest.py", "expected selftest-driver route drift was not reported"),
            ("python3 scripts/zigux/run-phase3-checks.py", "expected runner route drift was not reported"),
            ("zig build phase3-dev-t-starter-packet-test --build-file zigux/tests/phase3_dev_t_starter_packet_build.zig --summary all", "expected dev-t starter build route drift was not reported"),
            ("zig build phase3-xarray-slot-starter-packet-test --build-file zigux/tests/phase3_xarray_slot_starter_packet_build.zig", "expected xarray slot starter build route drift was not reported"),
            ("zig build phase3-xarray-slot-dump --build-file zigux/tests/phase3_xarray_slot_dump_build.zig", "expected xarray slot dump route drift was not reported"),
            ("zig build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig", "expected policy-starter build route drift was not reported"),
            ("zig build phase3-abi-core-packet --build-file zigux/tests/build.zig", "expected shared ABI core build route drift was not reported"),
            ("zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig", "expected export-uapi layout build route drift was not reported"),
            ("zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig", "expected export-uapi layout test route drift was not reported"),
            ("zig build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig", "expected export-shim build route drift was not reported"),
            ("make -C zigux phase3-export-shim-test", "expected export-shim make route drift was not reported"),
            ("zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig", "expected policy-dump build route drift was not reported"),
            ("make -C zigux phase3-policy-dump", "expected policy-dump make route drift was not reported"),
            ("zig build phase3-dump --build-file zigux/tests/build.zig", "expected shared ABI dump build route drift was not reported"),
            ("make -C zigux phase3-dump", "expected shared ABI dump make route drift was not reported"),
            ("zig build phase3-low-level-wrappers --build-file zigux/tests/build.zig", "expected low-level-wrapper shared build route drift was not reported"),
            ("make -C zigux phase3-low-level-wrappers", "expected low-level-wrapper shared make route drift was not reported"),
            ("zig build phase3-test --build-file zigux/tests/build.zig", "expected shared ABI aggregate build route drift was not reported"),
            ("make -C zigux phase3-test", "expected shared ABI aggregate make route drift was not reported"),
            ("make -C zigux phase3", "expected shared ABI top-level make route drift was not reported"),
            ("zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig", "expected low-level-wrapper focused build route drift was not reported"),
            ("make -C zigux phase3-export-uapi-layout", "expected export-uapi shared make route drift was not reported"),
            ("make -C zigux phase3-export-uapi-layout-test", "expected export-uapi dedicated make route drift was not reported"),
            ("make -C zigux phase3-low-level-wrappers-test", "expected low-level-wrapper focused make route drift was not reported"),
        )
        for route, failure_message in replay_route_cases:
            _populate_repo(repo_root)
            manifest = json.loads(_read(manifest_path))
            manifest["replay_routes"].remove(route)
            _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
            issues = validate_repo(repo_root)
            expected = f"phase3_abi_manifest.json missing replay route: {route}"
            _expect_issue(issues, expected, failure_message)

        _populate_repo(repo_root)
        manifest = json.loads(_read(manifest_path))
        manifest["status"] = "stale-status"
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(repo_root)
        _expect_issue(
            issues,
            "phase3_abi_manifest.json wrong status: 'stale-status' != 'shared_abi_and_header_family_binding_surface_present'",
            "expected status drift was not reported",
        )

        _populate_repo(repo_root)
        manifest = json.loads(_read(manifest_path))
        manifest["scope"] = "stale-scope"
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(repo_root)
        _expect_issue(
            issues,
            "phase3_abi_manifest.json wrong scope: 'stale-scope' != 'shared ABI bindings, directly coupled helper decoding, header-family follow-through, notifier layouts, export-status layout, and header-compatibility replay'",
            "expected scope drift was not reported",
        )

        _populate_repo(repo_root)
        manifest = json.loads(_read(manifest_path))
        manifest["repo_reality_gaps"] = ["stale-gap"]
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(repo_root)
        _expect_issue(
            issues,
            "phase3_abi_manifest.json repo_reality_gaps drifted from the current shared packet expectation",
            "expected repo_reality_gaps drift was not reported",
        )

        _populate_repo(repo_root)
        manifest = json.loads(_read(manifest_path))
        manifest["next_safe_step"] = "stale-next-step"
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(repo_root)
        _expect_issue(
            issues,
            "phase3_abi_manifest.json wrong next_safe_step: 'stale-next-step' != 'keep the shared Phase 3 policy, export/UAPI, and low-level wrapper packet aligned with the dedicated replay routes and only reopen this manifest if the checker, focused builds, or reminder surfaces drift again'",
            "expected next_safe_step drift was not reported",
        )

        _populate_repo(repo_root)
        manifest = json.loads(_read(manifest_path))
        manifest["slug"] = "stale-slug"
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(repo_root)
        _expect_issue(
            issues,
            "phase3_abi_manifest.json wrong slug: 'stale-slug' != 'phase3-abi-packet'",
            "expected slug drift was not reported",
        )

    print("PHASE3_ABI_MANIFEST_REPLAY_ROUTES_SELF_TEST=pass")
    print("PHASE3_ABI_MANIFEST_REPLAY_ROUTES_SELF_TEST_CASE_COUNT=177")
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
