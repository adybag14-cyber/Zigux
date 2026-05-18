#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import tempfile


MANIFEST_PATH = Path("zigux/tests/phase9_runtime_pilot_shared_packet_manifest.json")
ROOT_MARKER = Path("Documentation/zigux/review-checklist.md")
LANE_KEY = "P9-L11"
PHASE = "Phase 9"

SHARED_REVIEW_SURFACES = [
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md",
    "scripts/zigux/README.md",
    "samples/zigux/README.md",
    "zigux/tests/README.md",
    "scripts/zigux/check-phase9-review-checklist-phase-boundaries.py",
    "scripts/zigux/check-phase9-trace-events-runtime-packet.py",
]

DIRECT_RUNTIME_PACKET = [
    "samples/zigux/runtime_trace_events.zig",
    "samples/zigux/runtime_trace_events_unregistered_gate.zig",
    "samples/zigux/runtime_trace_events_exit_rollback_guard.zig",
    "samples/zigux/runtime_trace_events_registration_reentry_gate.zig",
]

ADJACENT_FAMILY_LOCAL_SURFACES = [
    "Documentation/zigux/phase9-runtime-trace-events-module-slice.md",
    "Documentation/zigux/phase9-runtime-trace-events-survey.md",
    "zigux/tests/runtime_trace_events_manifest.json",
    "zigux/tests/runtime_trace_events_survey.zig",
]

ABSENT_BACKLOG_FILES = [
    "zigux/tests/phase9_build.zig",
    "zigux/kernel/runtime_loader.zig",
    "zigux/kernel/runtime_loader_contract.zig",
    "samples/zigux/runtime_trace_events_loader.zig",
]

NON_OWNER_BOUNDARIES = {
    "phase2_config_surface": [
        "scripts/zigux/kconfig/conf_bridge.zig",
        "scripts/zigux/kconfig/confdata_bridge.zig",
    ],
    "phase3_export_boundary": [
        "rust/exports.c",
        "zigux/kernel/export_shim.zig",
    ],
    "freeze_map_anchors": [
        "Documentation/zigux/freeze-map.md",
        "Documentation/zigux/phase15-study-only-anchor-accounting.md",
        "kernel/workqueue.c",
        "kernel/trace/ring_buffer.c",
    ],
}

OWNERSHIP_MAP = {
    "Documentation/zigux/README.md": "P9-L11",
    "Documentation/zigux/review-checklist.md": "P9-L11",
    "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md": "P9-L11",
    "scripts/zigux/README.md": "P9-L11",
    "samples/zigux/README.md": "P9-L11",
    "zigux/tests/README.md": "P9-L11",
    "scripts/zigux/check-phase9-review-checklist-phase-boundaries.py": "P9-L11",
    "scripts/zigux/check-phase9-trace-events-runtime-packet.py": "P9-L11",
    ".github/workflows/zigux-bootstrap.yml": "P9-L11",
    "Documentation/zigux/phase9-runtime-trace-events-module-slice.md": "P9-L09",
    "Documentation/zigux/phase9-runtime-trace-events-survey.md": "P9-L09",
    "zigux/tests/runtime_trace_events_manifest.json": "P9-L09",
    "zigux/tests/runtime_trace_events_survey.zig": "P9-L09",
}


def infer_repo_root() -> Path:
    self_path = Path(__file__).resolve()
    for candidate in [self_path.parent, *self_path.parents]:
        if (candidate / ROOT_MARKER).exists():
            return candidate
    return self_path.parent


def read_manifest(root: Path) -> dict:
    return json.loads((root / MANIFEST_PATH).read_text(encoding="utf-8"))


def ensure_list(
    failures: list[str],
    manifest: dict,
    key: str,
    expected: list[str],
) -> None:
    catalog = manifest.get("catalog", {})
    actual = catalog.get(key)
    if actual != expected:
        failures.append(f"mismatch:catalog:{key}")


def ensure_boundary_map(failures: list[str], manifest: dict) -> None:
    catalog = manifest.get("catalog", {})
    actual = catalog.get("non_owner_boundaries")
    if actual != NON_OWNER_BOUNDARIES:
        failures.append("mismatch:catalog:non_owner_boundaries")


def ensure_counts(failures: list[str], manifest: dict) -> None:
    counts = manifest.get("catalog_counts", {})
    expected_counts = {
        "shared_review_surfaces": len(SHARED_REVIEW_SURFACES),
        "direct_runtime_packet": len(DIRECT_RUNTIME_PACKET),
        "adjacent_family_local_surfaces": len(ADJACENT_FAMILY_LOCAL_SURFACES),
        "absent_backlog_files": len(ABSENT_BACKLOG_FILES),
        "ownership_entries": len(OWNERSHIP_MAP),
    }
    if counts != expected_counts:
        failures.append("mismatch:catalog_counts")


def ensure_ownership(failures: list[str], manifest: dict) -> None:
    ownership_entries = manifest.get("ownership_map")
    if not isinstance(ownership_entries, list):
        failures.append("invalid:ownership_map")
        return

    actual = {}
    for entry in ownership_entries:
        surface = entry.get("surface")
        owner = entry.get("owner")
        if surface and owner:
            actual[surface] = owner
    if actual != OWNERSHIP_MAP:
        failures.append("mismatch:ownership_map")


def ensure_present_paths(failures: list[str], root: Path) -> None:
    for rel_path in (
        SHARED_REVIEW_SURFACES
        + DIRECT_RUNTIME_PACKET
        + ADJACENT_FAMILY_LOCAL_SURFACES
        + list(OWNERSHIP_MAP.keys())
        + NON_OWNER_BOUNDARIES["phase2_config_surface"]
        + NON_OWNER_BOUNDARIES["phase3_export_boundary"]
        + NON_OWNER_BOUNDARIES["freeze_map_anchors"]
    ):
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")


def ensure_absent_paths(failures: list[str], root: Path) -> None:
    for rel_path in ABSENT_BACKLOG_FILES:
        if (root / rel_path).exists():
            failures.append(f"unexpected_present:{rel_path}")


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    manifest_path = root / MANIFEST_PATH
    if not manifest_path.exists():
        return [f"missing_file:{MANIFEST_PATH.as_posix()}"]

    manifest = read_manifest(root)
    if manifest.get("lane_key") != LANE_KEY:
        failures.append("mismatch:lane_key")
    if manifest.get("phase") != PHASE:
        failures.append("mismatch:phase")
    if "scope" not in manifest:
        failures.append("missing:scope")
    if "roadmap_anchor" not in manifest:
        failures.append("missing:roadmap_anchor")
    if "next_gate" not in manifest:
        failures.append("missing:next_gate")

    ensure_list(failures, manifest, "shared_review_surfaces", SHARED_REVIEW_SURFACES)
    ensure_list(failures, manifest, "direct_runtime_packet", DIRECT_RUNTIME_PACKET)
    ensure_list(
        failures,
        manifest,
        "adjacent_family_local_surfaces",
        ADJACENT_FAMILY_LOCAL_SURFACES,
    )
    ensure_list(failures, manifest, "absent_backlog_files", ABSENT_BACKLOG_FILES)
    ensure_boundary_map(failures, manifest)
    ensure_counts(failures, manifest)
    ensure_ownership(failures, manifest)
    ensure_present_paths(failures, root)
    ensure_absent_paths(failures, root)
    return failures


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def seed_fixture_tree(base: Path) -> None:
    manifest = {
        "lane_key": LANE_KEY,
        "phase": PHASE,
        "scope": "manifest, catalog, and ownership map tighten delivery-discipline evidence for existing work",
        "roadmap_anchor": {
            "primary_goal": "enter runtime kernels through tests and samples, not production pressure",
            "linux_anchor": "samples/trace_events/trace-events-sample.c",
            "required_features": [
                "first loadable Zigux runtime modules",
                "selftest hooks",
                "runtime module lifecycle parity",
            ],
            "recommended_destinations": [
                "zigux/tests/runtime_*",
                "samples/zigux/runtime_*",
            ],
        },
        "catalog": {
            "shared_review_surfaces": SHARED_REVIEW_SURFACES,
            "direct_runtime_packet": DIRECT_RUNTIME_PACKET,
            "adjacent_family_local_surfaces": ADJACENT_FAMILY_LOCAL_SURFACES,
            "absent_backlog_files": ABSENT_BACKLOG_FILES,
            "non_owner_boundaries": NON_OWNER_BOUNDARIES,
        },
        "catalog_counts": {
            "shared_review_surfaces": len(SHARED_REVIEW_SURFACES),
            "direct_runtime_packet": len(DIRECT_RUNTIME_PACKET),
            "adjacent_family_local_surfaces": len(ADJACENT_FAMILY_LOCAL_SURFACES),
            "absent_backlog_files": len(ABSENT_BACKLOG_FILES),
            "ownership_entries": len(OWNERSHIP_MAP),
        },
        "ownership_map": [
            {"surface": surface, "owner": owner, "role": "fixture"}
            for surface, owner in OWNERSHIP_MAP.items()
        ],
        "next_gate": "fixture",
    }
    write_text(base / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")

    for rel_path in (
        SHARED_REVIEW_SURFACES
        + DIRECT_RUNTIME_PACKET
        + ADJACENT_FAMILY_LOCAL_SURFACES
        + list(OWNERSHIP_MAP.keys())
        + NON_OWNER_BOUNDARIES["phase2_config_surface"]
        + NON_OWNER_BOUNDARIES["phase3_export_boundary"]
        + NON_OWNER_BOUNDARIES["freeze_map_anchors"]
    ):
        write_text(base / rel_path, "fixture\n")


def run_self_test() -> int:
    temp_root = Path(tempfile.mkdtemp(prefix="phase9-shared-packet-manifest-"))
    try:
        seed_fixture_tree(temp_root)
        failures = validate(temp_root)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        broken_manifest = read_manifest(temp_root)
        broken_manifest["catalog_counts"]["ownership_entries"] = 0
        write_text(
            temp_root / MANIFEST_PATH,
            json.dumps(broken_manifest, indent=2) + "\n",
        )
        failures = validate(temp_root)
        if "mismatch:catalog_counts" not in failures:
            raise SystemExit(f"expected catalog count failure, got: {failures!r}")

        seed_fixture_tree(temp_root)
        (temp_root / "Documentation/zigux/README.md").unlink()
        failures = validate(temp_root)
        if "missing_file:Documentation/zigux/README.md" not in failures:
            raise SystemExit(f"expected missing file failure, got: {failures!r}")

        seed_fixture_tree(temp_root)
        write_text(temp_root / "zigux/tests/phase9_build.zig", "unexpected\n")
        failures = validate(temp_root)
        if "unexpected_present:zigux/tests/phase9_build.zig" not in failures:
            raise SystemExit(f"expected unexpected present failure, got: {failures!r}")
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)

    print("PHASE9_SHARED_PACKET_MANIFEST_SELF_TEST=pass")
    print(f"PHASE9_SHARED_PACKET_MANIFEST_SHARED_SURFACE_COUNT={len(SHARED_REVIEW_SURFACES)}")
    print(f"PHASE9_SHARED_PACKET_MANIFEST_DIRECT_PACKET_COUNT={len(DIRECT_RUNTIME_PACKET)}")
    print(
        "PHASE9_SHARED_PACKET_MANIFEST_ADJACENT_SURFACE_COUNT="
        f"{len(ADJACENT_FAMILY_LOCAL_SURFACES)}"
    )
    print(f"PHASE9_SHARED_PACKET_MANIFEST_OWNERSHIP_COUNT={len(OWNERSHIP_MAP)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the Phase 9 shared reminder packet manifest, catalog counts, ownership map, live shared-review surfaces, and explicitly absent backlog files."
    )
    parser.add_argument("--repo-root", type=Path, default=infer_repo_root())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.repo_root)
    if failures:
        for failure in failures:
            print(f"PHASE9_SHARED_PACKET_MANIFEST_ERROR={failure}")
        return 1

    print("PHASE9_SHARED_PACKET_MANIFEST=pass")
    print(f"PHASE9_SHARED_PACKET_MANIFEST_SHARED_SURFACE_COUNT={len(SHARED_REVIEW_SURFACES)}")
    print(f"PHASE9_SHARED_PACKET_MANIFEST_DIRECT_PACKET_COUNT={len(DIRECT_RUNTIME_PACKET)}")
    print(
        "PHASE9_SHARED_PACKET_MANIFEST_ADJACENT_SURFACE_COUNT="
        f"{len(ADJACENT_FAMILY_LOCAL_SURFACES)}"
    )
    print(f"PHASE9_SHARED_PACKET_MANIFEST_OWNERSHIP_COUNT={len(OWNERSHIP_MAP)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
