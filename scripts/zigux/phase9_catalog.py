#!/usr/bin/env python3
"""Inventory the current bounded Phase 9 runtime pilot packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

PHASE9_CATALOG_PHASE = "Phase 9"
PHASE9_CATALOG_LANE = "P9-L11"
MANIFEST_PATH = Path("zigux/tests/runtime_pilot_manifest.json")
OWNERSHIP_MAP_PATH = Path("Documentation/zigux/phase9-runtime-pilot-ownership-map.md")

EXPECTED_PACKET_FILES = (
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md",
    "Documentation/zigux/phase9-runtime-pilot-ownership-map.md",
    "Documentation/zigux/phase9-runtime-bitmap-survey.md",
    "Documentation/zigux/phase9-runtime-bitmap-module-slice.md",
    "Documentation/zigux/phase9-runtime-trace-events-survey.md",
    "Documentation/zigux/phase9-runtime-trace-events-module-slice.md",
    "samples/zigux/README.md",
    "scripts/zigux/README.md",
    "scripts/zigux/phase9_catalog.py",
    "scripts/zigux/check-phase9-catalog-selftest.py",
    "scripts/zigux/check-phase9-atomic64-runtime-packet.py",
    "scripts/zigux/check-phase9-review-checklist-phase-boundaries.py",
    "scripts/zigux/check-phase9-freeze-map-study-boundaries.py",
    "scripts/zigux/check-phase9-trace-events-runtime-packet.py",
    "scripts/zigux/check-phase9-trace-events-direct-summary.py",
    "scripts/zigux/check-phase9-trace-events-summary-preservation.py",
    "zigux/kernel/runtime_loader.zig",
    "zigux/kernel/runtime_loader_contract.zig",
    "zigux/kernel/runtime_loader_command_env_boundary_guard.zig",
    "zigux/tests/README.md",
    "zigux/tests/phase9_build.zig",
    "zigux/tests/runtime_pilot_manifest.json",
    "zigux/tests/runtime_loader_allocator_init_flow.zig",
    "zigux/tests/runtime_loader_allocator_init_flow_build.zig",
    "zigux/tests/runtime_atomic64_diff.zig",
    "zigux/tests/runtime_atomic64_module.zig",
    "zigux/tests/runtime_bitmap_manifest.json",
    "zigux/tests/runtime_bitmap_survey.zig",
    "zigux/tests/runtime_bitmap_module.zig",
    "zigux/tests/runtime_bitmap_diff.zig",
    "zigux/tests/runtime_trace_events_manifest.json",
    "zigux/tests/runtime_trace_events_survey.zig",
    "zigux/tests/runtime_trace_events_module.zig",
    "zigux/tests/runtime_kretprobe_survey.zig",
    "zigux/tests/runtime_kretprobe_module.zig",
    "zigux/tests/runtime_first_loadable_parity_behavior.zig",
    "samples/zigux/runtime_atomic64.zig",
    "samples/zigux/runtime_atomic64_loader.zig",
    "samples/zigux/runtime_trace_events.zig",
    "samples/zigux/runtime_trace_events_unregistered_gate.zig",
    "samples/zigux/runtime_trace_events_exit_rollback_guard.zig",
    "samples/zigux/runtime_trace_events_registration_reentry_gate.zig",
    "samples/zigux/runtime_trace_events_reinit_rollback_guard.zig",
    "samples/zigux/runtime_trace_events_reinit_reexit_guard.zig",
    "samples/zigux/runtime_bitmap.zig",
    "samples/zigux/runtime_bitmap_direct_init_contract.zig",
    "samples/zigux/runtime_bitmap_loader.zig",
    "samples/zigux/runtime_bitmap_cold_stage_guard.zig",
    "samples/zigux/runtime_bitmap_top_bit_contract.zig",
    "samples/zigux/runtime_kretprobe.zig",
    "samples/zigux/runtime_kretprobe_loader.zig",
    "samples/zigux/runtime_kretprobe_initialized_snapshot_guard.zig",
    "samples/zigux/runtime_kretprobe_registration_reentry_gate.zig",
)

EXPECTED_REPLAY_ROUTES = (
    "python3 scripts/zigux/check-phase9-catalog-selftest.py --self-test",
    "python3 scripts/zigux/check-phase9-catalog-selftest.py",
    "python3 scripts/zigux/phase9_catalog.py --pretty",
    "python3 scripts/zigux/check-phase9-atomic64-runtime-packet.py --self-test",
    "python3 scripts/zigux/check-phase9-atomic64-runtime-packet.py",
    "python3 scripts/zigux/check-phase9-review-checklist-phase-boundaries.py --self-test",
    "python3 scripts/zigux/check-phase9-freeze-map-study-boundaries.py --self-test",
    "python3 scripts/zigux/check-phase9-trace-events-runtime-packet.py --self-test",
    "python3 scripts/zigux/check-phase9-trace-events-direct-summary.py --self-test",
    "python3 scripts/zigux/check-phase9-trace-events-summary-preservation.py --self-test",
    "zig build phase9-runtime-atomic64-tests --build-file zigux/tests/phase9_build.zig",
    "zig build test --build-file zigux/tests/runtime_loader_allocator_init_flow_build.zig",
    "zig build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig",
    "zig build phase9-runtime-bitmap-tests --build-file zigux/tests/phase9_build.zig",
    "zig build phase9-runtime-trace-events-tests --build-file zigux/tests/phase9_build.zig",
    "zig build phase9-runtime-kretprobe-tests --build-file zigux/tests/phase9_build.zig",
    "zig build phase9-first-loadable-runtime-module-parity-behavior-tests --build-file zigux/tests/phase9_build.zig",
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
        raise TypeError("runtime_pilot_manifest.json packet_files is not a list")
    return [str(value) for value in packet_files]


def _replay_routes(manifest: dict[str, object]) -> list[str]:
    replay_routes = manifest.get("replay_routes")
    if not isinstance(replay_routes, list):
        raise TypeError("runtime_pilot_manifest.json replay_routes is not a list")
    return [str(value) for value in replay_routes]


def _is_doc(path: str) -> bool:
    return path.startswith("Documentation/")


def _is_script(path: str) -> bool:
    return path.startswith("scripts/zigux/")


def _is_kernel(path: str) -> bool:
    return path.startswith("zigux/kernel/")


def _is_test(path: str) -> bool:
    return path.startswith("zigux/tests/")


def _is_sample(path: str) -> bool:
    return path.startswith("samples/zigux/")


def _categorize(packet_files: list[str]) -> dict[str, list[str]]:
    return {
        "docs": [path for path in packet_files if _is_doc(path)],
        "scripts": [path for path in packet_files if _is_script(path)],
        "kernel": [path for path in packet_files if _is_kernel(path)],
        "tests": [path for path in packet_files if _is_test(path)],
        "samples": [path for path in packet_files if _is_sample(path)],
    }


def validate_repo(repo_root: Path) -> list[str]:
    manifest, issues = _load_manifest(repo_root)
    if manifest is None:
        return issues

    if manifest.get("phase") != PHASE9_CATALOG_PHASE:
        issues.append(
            "runtime_pilot_manifest.json wrong phase: "
            f"{manifest.get('phase')!r} != {PHASE9_CATALOG_PHASE!r}"
        )
    if manifest.get("lane_key") != PHASE9_CATALOG_LANE:
        issues.append(
            "runtime_pilot_manifest.json wrong lane_key: "
            f"{manifest.get('lane_key')!r} != {PHASE9_CATALOG_LANE!r}"
        )
    if manifest.get("ownership_map_path") != OWNERSHIP_MAP_PATH.as_posix():
        issues.append(
            "runtime_pilot_manifest.json wrong ownership_map_path: "
            f"{manifest.get('ownership_map_path')!r} != {OWNERSHIP_MAP_PATH.as_posix()!r}"
        )

    try:
        packet_files = _packet_paths(manifest)
        replay_routes = _replay_routes(manifest)
    except TypeError as exc:
        issues.append(str(exc))
        return issues

    if not packet_files:
        issues.append("runtime_pilot_manifest.json packet_files must not be empty")
    if not replay_routes:
        issues.append("runtime_pilot_manifest.json replay_routes must not be empty")

    _append_duplicate_list_entry_issues("runtime_pilot_manifest.json packet_files", packet_files, issues)
    _append_duplicate_list_entry_issues("runtime_pilot_manifest.json replay_routes", replay_routes, issues)

    for relative_path in packet_files:
        if not (repo_root / relative_path).is_file():
            issues.append(f"missing repo file: {relative_path}")

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
        "phase": manifest.get("phase", PHASE9_CATALOG_PHASE),
        "lane_key": manifest.get("lane_key", PHASE9_CATALOG_LANE),
        "ownership_map_path": manifest.get("ownership_map_path", OWNERSHIP_MAP_PATH.as_posix()),
        "docs": categories["docs"],
        "scripts": categories["scripts"],
        "kernel": categories["kernel"],
        "tests": categories["tests"],
        "samples": categories["samples"],
        "commands": replay_routes,
        "repo_reality_gaps": manifest.get("repo_reality_gaps", []),
    }


def _manifest_payload() -> dict[str, object]:
    return {
        "phase": PHASE9_CATALOG_PHASE,
        "lane_key": PHASE9_CATALOG_LANE,
        "slug": "phase9-runtime-pilot-shared-packet",
        "status": "shared_runtime_pilot_delivery_evidence_present",
        "scope": "shared reminder, manifest, catalog, and ownership surfaces for the atomic64 pilot packet, the shipped trace-events packet, the narrower shared runtime-loader packet, the bounded runtime bitmap packet, and the returned runtime kretprobe packet without blocked publication claims",
        "ownership_map_path": OWNERSHIP_MAP_PATH.as_posix(),
        "packet_files": list(EXPECTED_PACKET_FILES),
        "replay_routes": list(EXPECTED_REPLAY_ROUTES),
        "repo_reality_gaps": [
            "no dedicated shared validate-phase9.py rerun path on current master",
            "blocked publication and install-root vocabulary remains historical rather than direct shipped proof",
        ],
        "next_safe_step": "tighten one stale shared reminder surface at a time when it undercounts the atomic64, returned kretprobe, or shared loader packet, and keep the shared manifest aligned without widening runtime behavior claims",
    }


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase9_catalog_") as tmp_dir:
        root = Path(tmp_dir)
        for relative_path in EXPECTED_PACKET_FILES:
            _write(root / relative_path, "// self-test\n")
        _write(root / MANIFEST_PATH, json.dumps(_manifest_payload(), indent=2) + "\n")

        issues = validate_repo(root)
        if issues:
            print("PHASE9_CATALOG_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        catalog = build_catalog(root)
        expected_categories = _categorize(list(EXPECTED_PACKET_FILES))
        for key, values in expected_categories.items():
            if len(catalog[key]) != len(values):
                print("PHASE9_CATALOG_SELF_TEST=fail")
                print(f"unexpected {key} count: {len(catalog[key])} != {len(values)}")
                return 1
        if len(catalog["commands"]) != len(EXPECTED_REPLAY_ROUTES):
            print("PHASE9_CATALOG_SELF_TEST=fail")
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
            print("PHASE9_CATALOG_SELF_TEST=fail")
            print("expected missing packet member was not reported")
            return 1

        _write(root / MANIFEST_PATH, json.dumps({**_manifest_payload(), "packet_files": "oops"}, indent=2) + "\n")
        issues = validate_repo(root)
        expected_list_issue = "runtime_pilot_manifest.json packet_files is not a list"
        if expected_list_issue not in issues:
            print("PHASE9_CATALOG_SELF_TEST=fail")
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
        expected_duplicate = "runtime_pilot_manifest.json replay_routes duplicate entry:"
        if not any(issue.startswith(expected_duplicate) for issue in issues):
            print("PHASE9_CATALOG_SELF_TEST=fail")
            print("expected duplicate replay route was not reported")
            return 1

    print("PHASE9_CATALOG_SELF_TEST=pass")
    print("PHASE9_CATALOG_SELF_TEST_CASE_COUNT=5")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Inventory the current bounded Phase 9 runtime pilot packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the current Phase 9 runtime pilot packet",
    )
    parser.add_argument("--pretty", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE9_CATALOG=fail")
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