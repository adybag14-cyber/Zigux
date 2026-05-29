#!/usr/bin/env python3
"""Validate the Phase 3 ABI/export parity scoreboard evidence."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_abi_manifest.json")

REQUIRED_PACKET_FILES = (
    "include/zigux/abi.h",
    "include/zigux/dev_t.h",
    "include/linux/zigux.h",
    "zigux/bindings/abi.zig",
    "zigux/bindings/dev_t.zig",
    "zigux/bindings/version.zig",
    "zigux/bindings/header_family.zig",
    "zigux/kernel/export_shim.zig",
    "zigux/uapi/dev_t.zig",
    "zigux/uapi/version.zig",
    "zigux/tests/phase3_abi.zig",
    "zigux/tests/phase3_abi_dump_current.zig",
    "zigux/tests/phase3_export_uapi_c_header_smoke.c",
    "zigux/tests/phase3_export_uapi_layout.zig",
    "zigux/tests/phase3_export_uapi_layout_build.zig",
    "zigux/tests/phase3_export_shim_build.zig",
    "scripts/zigux/check-phase3-export-uapi-c-header-smoke.py",
    "scripts/zigux/validate-phase3-export-uapi-survey.py",
)

REQUIRED_REPLAY_ROUTES = (
    "python3 scripts/zigux/check-phase3-export-uapi-c-header-smoke.py --self-test",
    "python3 scripts/zigux/check-phase3-export-uapi-c-header-smoke.py",
    "python3 scripts/zigux/validate-phase3-export-uapi-survey.py --self-test",
    "python3 scripts/zigux/validate-phase3-export-uapi-survey.py",
    "zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig",
    "zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
    "zig build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig",
    "make -C zigux phase3-export-shim-test",
    "make -C zigux phase3-export-uapi-layout",
    "make -C zigux phase3-export-uapi-layout-test",
    "zig build phase3-abi-export --build-file zigux/tests/build.zig",
    "make -C zigux phase3-abi-export",
)

RETIRED_GENERATED_PATHS = (
    "zigux/tests/phase3_abi_dump.zig",
    "zigux/tests/fixtures/phase3_abi/expected.json",
)


def _read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _require_list(manifest: dict[str, object], field: str, issues: list[str]) -> list[object]:
    value = manifest.get(field)
    if not isinstance(value, list):
        issues.append(f"phase3_abi_manifest.json {field} is not a list")
        return []
    return value


def _check_required(label: str, actual: list[object], required: tuple[str, ...], issues: list[str]) -> None:
    for entry in required:
        if entry not in actual:
            issues.append(f"phase3 ABI/export parity scoreboard missing {label}: {entry}")


def _check_retired_absent(packet_files: list[object], replay_routes: list[object], issues: list[str]) -> None:
    for retired_path in RETIRED_GENERATED_PATHS:
        if retired_path in packet_files:
            issues.append(f"phase3 ABI/export parity scoreboard includes retired packet file: {retired_path}")
        if retired_path in replay_routes:
            issues.append(f"phase3 ABI/export parity scoreboard includes retired replay route: {retired_path}")


def validate_manifest(manifest: object) -> list[str]:
    issues: list[str] = []
    if not isinstance(manifest, dict):
        return ["phase3_abi_manifest.json root is not an object"]
    if manifest.get("phase") != "Phase 3":
        issues.append("phase3 ABI/export parity scoreboard is not attached to Phase 3")
    if manifest.get("lane") != "abi-runtime":
        issues.append("phase3 ABI/export parity scoreboard is not attached to abi-runtime")
    packet_files = _require_list(manifest, "packet_files", issues)
    replay_routes = _require_list(manifest, "replay_routes", issues)
    _check_required("packet file", packet_files, REQUIRED_PACKET_FILES, issues)
    _check_required("replay route", replay_routes, REQUIRED_REPLAY_ROUTES, issues)
    _check_retired_absent(packet_files, replay_routes, issues)
    return issues


def validate_repo(repo_root: Path) -> list[str]:
    manifest_path = repo_root / MANIFEST_PATH
    if not manifest_path.is_file():
        return [f"missing repo file: {MANIFEST_PATH.as_posix()}"]
    try:
        manifest = _read_json(manifest_path)
    except json.JSONDecodeError as exc:
        return [f"invalid JSON in {MANIFEST_PATH.as_posix()}: {exc}"]
    return validate_manifest(manifest)


def _sample_manifest() -> dict[str, object]:
    return {
        "phase": "Phase 3",
        "lane": "abi-runtime",
        "packet_files": list(REQUIRED_PACKET_FILES),
        "replay_routes": list(REQUIRED_REPLAY_ROUTES),
    }


def _require_issue(issues: list[str], expected: str) -> None:
    if expected not in issues:
        print("PHASE3_ABI_EXPORT_PARITY_SCOREBOARD_SELF_TEST=fail")
        print(f"missing expected issue: {expected}")
        print("\n".join(issues))
        raise SystemExit(1)


def run_self_test() -> int:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_abi_export_scoreboard_") as temp_dir:
        root = Path(temp_dir)
        manifest_path = root / MANIFEST_PATH
        _write(manifest_path, json.dumps(_sample_manifest(), indent=2) + "\n")
        issues = validate_repo(root)
        if issues:
            print("PHASE3_ABI_EXPORT_PARITY_SCOREBOARD_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        checks = [
            (
                lambda m: m.update(phase="Phase 4"),
                "phase3 ABI/export parity scoreboard is not attached to Phase 3",
            ),
            (
                lambda m: m.update(lane="other"),
                "phase3 ABI/export parity scoreboard is not attached to abi-runtime",
            ),
            (
                lambda m: m["packet_files"].remove("zigux/kernel/export_shim.zig"),
                "phase3 ABI/export parity scoreboard missing packet file: zigux/kernel/export_shim.zig",
            ),
            (
                lambda m: m["replay_routes"].remove("make -C zigux phase3-abi-export"),
                "phase3 ABI/export parity scoreboard missing replay route: make -C zigux phase3-abi-export",
            ),
            (
                lambda m: m["packet_files"].append(RETIRED_GENERATED_PATHS[0]),
                "phase3 ABI/export parity scoreboard includes retired packet file: zigux/tests/phase3_abi_dump.zig",
            ),
            (
                lambda m: m["replay_routes"].append(RETIRED_GENERATED_PATHS[1]),
                "phase3 ABI/export parity scoreboard includes retired replay route: zigux/tests/fixtures/phase3_abi/expected.json",
            ),
        ]
        for mutate, expected in checks:
            manifest = _sample_manifest()
            mutate(manifest)
            _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
            _require_issue(validate_repo(root), expected)
            cases += 1

    print("PHASE3_ABI_EXPORT_PARITY_SCOREBOARD_SELF_TEST=pass")
    print(f"PHASE3_ABI_EXPORT_PARITY_SCOREBOARD_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the Phase 3 ABI/export parity scoreboard evidence.")
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="repository root")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_ABI_EXPORT_PARITY_SCOREBOARD=fail")
        print("\n".join(issues))
        return 1
    print("PHASE3_ABI_EXPORT_PARITY_SCOREBOARD=pass")
    print(f"PHASE3_ABI_EXPORT_PARITY_SCOREBOARD_PACKET_FILES={len(REQUIRED_PACKET_FILES)}")
    print(f"PHASE3_ABI_EXPORT_PARITY_SCOREBOARD_REPLAY_ROUTES={len(REQUIRED_REPLAY_ROUTES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
