#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys
import tempfile

SELF_PATH = Path(__file__).resolve()
MANIFEST_PATH = Path("zigux/tests/phase12_libbpf_manifest.json")

EXPECTED_LANE_KEY = "P12-L16"
EXPECTED_PHASE = "Phase 12"
EXPECTED_SURVEYED_COMMIT = "c0ae127363e3d4e5feeb36efb665a12ece3392c7"
EXPECTED_STATUS_COUNTS = {
    "starter_landed": 13,
    "ready_next": 0,
    "blocked_on_object_model": 1,
    "deferred_high_risk": 4,
}
EXPECTED_BRIDGE_AND_RISK_GAPS = {
    "phase12-libbpf-file-path-handle-helper-foundation": {
        "status": "starter_landed",
        "kind": "helper_first",
        "zigux_destination": "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
    },
    "phase12-libbpf-map-reuse-compatibility-helper-foundation": {
        "status": "starter_landed",
        "kind": "helper_first",
        "zigux_destination": "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
    },
    "phase12-libbpf-file-path-and-handle-bridge-boundary": {
        "status": "deferred_high_risk",
        "kind": "resource_boundary",
        "zigux_destination": "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
    },
    "phase12-libbpf-perf-buffer-online-cpu-routing-boundary": {
        "status": "deferred_high_risk",
        "kind": "interrupt_routing",
        "zigux_destination": "tools/lib/bpf/zigux_segments/cpu_mask.zig",
    },
    "phase12-libbpf-skeleton-population": {
        "status": "blocked_on_object_model",
        "kind": "object_adjacent",
        "zigux_destination": "tools/lib/bpf/zigux_segments/skeleton.zig",
    },
    "phase12-libbpf-object-and-elf-loader": {
        "status": "deferred_high_risk",
        "kind": "core_loader",
        "zigux_destination": "tools/lib/bpf/zigux_segments/object_loader.zig",
    },
    "phase12-libbpf-btf-relocation-and-program-load": {
        "status": "deferred_high_risk",
        "kind": "verifier_facing",
        "zigux_destination": "tools/lib/bpf/zigux_segments/relocation.zig",
    },
}


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / MANIFEST_PATH).exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()


def read_manifest(root: Path) -> dict:
    return json.loads((root / MANIFEST_PATH).read_text(encoding="utf-8"))


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    manifest_path = root / MANIFEST_PATH
    if not manifest_path.exists():
        return [f"missing_file:{MANIFEST_PATH.as_posix()}"]

    manifest = read_manifest(root)
    if manifest.get("lane_key") != EXPECTED_LANE_KEY:
        failures.append(f"lane_key:{manifest.get('lane_key')!r}")
    if manifest.get("phase") != EXPECTED_PHASE:
        failures.append(f"phase:{manifest.get('phase')!r}")
    if manifest.get("surveyed_commit") != EXPECTED_SURVEYED_COMMIT:
        failures.append(f"surveyed_commit:{manifest.get('surveyed_commit')!r}")

    gaps = manifest.get("gaps")
    if not isinstance(gaps, list):
        failures.append("gaps:not_list")
        return failures

    if len(gaps) != 18:
        failures.append(f"gaps_len:{len(gaps)}")

    seen_ids: set[str] = set()
    status_counts = {key: 0 for key in EXPECTED_STATUS_COUNTS}

    for gap in gaps:
        if not isinstance(gap, dict):
            failures.append("gap:not_object")
            continue
        gap_id = gap.get("id")
        if not isinstance(gap_id, str):
            failures.append("gap_id:not_string")
            continue
        if gap_id in seen_ids:
            failures.append(f"duplicate_gap:{gap_id}")
        seen_ids.add(gap_id)

        status = gap.get("status")
        if status in status_counts:
            status_counts[status] += 1

        expected = EXPECTED_BRIDGE_AND_RISK_GAPS.get(gap_id)
        if expected is None:
            continue
        for field, expected_value in expected.items():
            actual = gap.get(field)
            if actual != expected_value:
                failures.append(f"{gap_id}:{field}:{actual!r}")

    for status, expected_count in EXPECTED_STATUS_COUNTS.items():
        actual_count = status_counts.get(status, 0)
        if actual_count != expected_count:
            failures.append(f"status_count:{status}:{actual_count}")

    for gap_id in EXPECTED_BRIDGE_AND_RISK_GAPS:
        if gap_id not in seen_ids:
            failures.append(f"missing_gap:{gap_id}")

    return failures


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def build_fixture_manifest() -> dict:
    starter_prefix = [
        {
            "id": "phase12-build-gate",
            "status": "starter_landed",
            "kind": "validation",
            "zigux_destination": "zigux/tests/phase12_build.zig",
        },
        {
            "id": "phase12-make-target",
            "status": "starter_landed",
            "kind": "validation",
            "zigux_destination": "zigux/Makefile",
        },
        {
            "id": "phase12-libbpf-segment-manifest-foundation",
            "status": "starter_landed",
            "kind": "segmented_rollout",
            "zigux_destination": "tools/lib/bpf/zigux_segments/manifest.json",
        },
        {
            "id": "phase12-libbpf-type-name-helper-foundation",
            "status": "starter_landed",
            "kind": "helper_first",
            "zigux_destination": "tools/lib/bpf/zigux_segments/type_names.zig",
        },
        {
            "id": "phase12-libbpf-cpu-mask-helper-foundation",
            "status": "starter_landed",
            "kind": "helper_first",
            "zigux_destination": "tools/lib/bpf/zigux_segments/cpu_mask.zig",
        },
        {
            "id": "phase12-libbpf-perf-buffer-poll-helper-foundation",
            "status": "starter_landed",
            "kind": "helper_first",
            "zigux_destination": "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
        },
        {
            "id": "phase12-libbpf-survey-gate",
            "status": "starter_landed",
            "kind": "validation",
            "zigux_destination": "zigux/tests/phase12_libbpf_segments.zig",
        },
        {
            "id": "phase12-libbpf-reviewability-gate",
            "status": "starter_landed",
            "kind": "validation",
            "zigux_destination": "zigux/tests/phase12_libbpf_reviewability.zig",
        },
        {
            "id": "phase12-libbpf-survey-note",
            "status": "starter_landed",
            "kind": "documentation",
            "zigux_destination": "Documentation/zigux/phase12-libbpf-segment-survey.md",
        },
        {
            "id": "phase12-libbpf-logging-helper-foundation",
            "status": "starter_landed",
            "kind": "helper_first",
            "zigux_destination": "tools/lib/bpf/zigux_segments/logging.zig",
        },
        {
            "id": "phase12-libbpf-pin-path-helper-foundation",
            "status": "starter_landed",
            "kind": "helper_first",
            "zigux_destination": "tools/lib/bpf/zigux_segments/pin_path.zig",
        },
    ]
    return {
        "lane_key": EXPECTED_LANE_KEY,
        "phase": EXPECTED_PHASE,
        "surveyed_commit": EXPECTED_SURVEYED_COMMIT,
        "gaps": starter_prefix
        + [
            {
                "id": gap_id,
                **fields,
                "why_now": "fixture",
            }
            for gap_id, fields in EXPECTED_BRIDGE_AND_RISK_GAPS.items()
        ],
    }


def run_self_test() -> int:
    temp_root = Path(tempfile.mkdtemp(prefix="phase12-libbpf-bridge-buckets-"))
    try:
        manifest_path = temp_root / MANIFEST_PATH
        fixture = build_fixture_manifest()
        write_json(manifest_path, fixture)

        failures = validate(temp_root)
        if failures:
            raise SystemExit(f"fixture should pass: {failures!r}")

        broken = build_fixture_manifest()
        broken["lane_key"] = "P12-L17"
        write_json(manifest_path, broken)
        assert any(item.startswith("lane_key:") for item in validate(temp_root))

        broken = build_fixture_manifest()
        broken["gaps"][11]["id"] = "phase12-libbpf-file-path-handle-helper-ready-next"
        write_json(manifest_path, broken)
        failures = validate(temp_root)
        assert "missing_gap:phase12-libbpf-file-path-handle-helper-foundation" in failures

        broken = build_fixture_manifest()
        broken["gaps"][12]["status"] = "ready_next"
        write_json(manifest_path, broken)
        failures = validate(temp_root)
        assert "phase12-libbpf-map-reuse-compatibility-helper-foundation:status:'ready_next'" in failures
        assert "status_count:starter_landed:12" in failures
        assert "status_count:ready_next:1" in failures

        broken = build_fixture_manifest()
        broken["gaps"][13]["kind"] = "helper_first"
        write_json(manifest_path, broken)
        assert "phase12-libbpf-file-path-and-handle-bridge-boundary:kind:'helper_first'" in validate(temp_root)

        broken = build_fixture_manifest()
        broken["gaps"][16]["zigux_destination"] = "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig"
        write_json(manifest_path, broken)
        assert "phase12-libbpf-object-and-elf-loader:zigux_destination:'tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig'" in validate(temp_root)

        broken = build_fixture_manifest()
        broken["gaps"] = broken["gaps"][:-1]
        write_json(manifest_path, broken)
        failures = validate(temp_root)
        assert "gaps_len:17" in failures
        assert "status_count:deferred_high_risk:3" in failures
        assert "missing_gap:phase12-libbpf-btf-relocation-and-program-load" in failures

        print("PHASE12_LIBBPF_BRIDGE_BUCKETS_SELF_TEST=pass")
        print("PHASE12_LIBBPF_BRIDGE_BUCKETS_SELF_TEST_CASE_COUNT=6")
        return 0
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the current Phase 12 libbpf bridge and heavy-risk manifest bucket packet."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to inspect. Defaults to the root inferred from this script.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the synthetic self-test.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        print("PHASE12_LIBBPF_BRIDGE_BUCKETS=fail")
        print("PHASE12_LIBBPF_BRIDGE_BUCKETS_FAILURES_START")
        for failure in failures:
            print(failure)
        print("PHASE12_LIBBPF_BRIDGE_BUCKETS_FAILURES_END")
        return 1

    print("PHASE12_LIBBPF_BRIDGE_BUCKETS=pass")
    print(f"PHASE12_LIBBPF_BRIDGE_BUCKET_COUNT={len(EXPECTED_BRIDGE_AND_RISK_GAPS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
