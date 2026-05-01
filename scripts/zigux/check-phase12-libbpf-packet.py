#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile


TRACKED_PATHS = [
    "zigux/tests/phase12_libbpf_manifest.json",
    "zigux/tests/phase12_libbpf_segments.zig",
    "zigux/tests/phase12_libbpf_reviewability.zig",
    "Documentation/zigux/phase12-libbpf-segment-survey.md",
    "tools/lib/bpf/zigux_segments/manifest.json",
]

MANIFEST_ROLLBACK_CONTRACT = {
    "owner": "BPF Tooling Lane",
    "rollback_owner": "BPF Tooling Lane",
    "fallback_path": "tools/lib/bpf/libbpf.c",
    "reversible_delivery_evidence": [
        "zigux/tests/phase12_libbpf_segments.zig",
        "zigux/tests/phase12_libbpf_reviewability.zig",
        "Documentation/zigux/phase12-libbpf-segment-survey.md",
    ],
    "rollback_drill": [
        "python3 scripts/zigux/check-phase12-build-inventory.py --self-test",
        "python3 scripts/zigux/check-phase12-build-inventory.py",
        "python3 scripts/zigux/check-phase12-libbpf-snapshot.py --self-test",
        "python3 scripts/zigux/check-phase12-libbpf-snapshot.py",
        "python3 scripts/zigux/check-phase12-libbpf-packet.py --self-test",
        "python3 scripts/zigux/check-phase12-libbpf-packet.py",
        "python3 scripts/zigux/validate-phase12.py",
        "make -C zigux phase12-validate",
        "zig build test --build-file zigux/tests/phase12_build.zig --summary all",
    ],
}

SURVEY_NOTE_MARKERS = [
    "## Rollback And Reversible Delivery",
    "owner: `BPF Tooling Lane`",
    "rollback owner: `BPF Tooling Lane`",
    "fallback path: keep `tools/lib/bpf/libbpf.c` as the source of truth",
    "python3 scripts/zigux/check-phase12-build-inventory.py --self-test",
    "python3 scripts/zigux/check-phase12-build-inventory.py",
    "python3 scripts/zigux/check-phase12-libbpf-snapshot.py --self-test",
    "python3 scripts/zigux/check-phase12-libbpf-snapshot.py",
    "python3 scripts/zigux/check-phase12-libbpf-packet.py --self-test",
    "python3 scripts/zigux/check-phase12-libbpf-packet.py",
    "python3 scripts/zigux/validate-phase12.py",
    "make -C zigux phase12-validate",
    "zig build test --build-file zigux/tests/phase12_build.zig --summary all",
    "automatic perf-buffer CPU-budget clamp explicit before any per-CPU buffer opens happen",
    "optional probes still degrade gracefully, mandatory probes still fail hard",
]

SEGMENT_TEST_MARKERS = [
    "current_surveyed_commit",
    "phase12-libbpf-reviewability-gate",
    "phase12-libbpf-skeleton-population",
    "phase12-libbpf-map-reuse-compatibility-helper-foundation",
]

REVIEWABILITY_MARKERS = [
    "phase12 libbpf reviewability gate pins the committed snapshot fixture packet",
    "phase12 libbpf reviewability gate matches the current zigux_segments file state",
    "phase12 libbpf reviewability gate still compiles the landed helper foundations",
    "phase12 libbpf reviewability gate cross-checks the legacy segment catalog",
]

PHASE12_GAP_SPECS = [
    (
        "phase12-libbpf-type-name-helper-foundation",
        "starter_landed",
        "tools/lib/bpf/zigux_segments/type_names.zig",
    ),
    (
        "phase12-libbpf-cpu-mask-helper-foundation",
        "starter_landed",
        "tools/lib/bpf/zigux_segments/cpu_mask.zig",
    ),
    (
        "phase12-libbpf-logging-helper-foundation",
        "starter_landed",
        "tools/lib/bpf/zigux_segments/logging.zig",
    ),
    (
        "phase12-libbpf-pin-path-helper-foundation",
        "starter_landed",
        "tools/lib/bpf/zigux_segments/pin_path.zig",
    ),
    (
        "phase12-libbpf-file-path-handle-helper-foundation",
        "starter_landed",
        "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
    ),
    (
        "phase12-libbpf-map-reuse-compatibility-helper-foundation",
        "starter_landed",
        "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
    ),
    (
        "phase12-libbpf-file-path-and-handle-bridge-boundary",
        "deferred_high_risk",
        "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
    ),
    (
        "phase12-libbpf-perf-buffer-online-cpu-routing-boundary",
        "deferred_high_risk",
        "tools/lib/bpf/zigux_segments/cpu_mask.zig",
    ),
    (
        "phase12-libbpf-skeleton-population",
        "blocked_on_object_model",
        "tools/lib/bpf/zigux_segments/skeleton.zig",
    ),
    (
        "phase12-libbpf-object-and-elf-loader",
        "deferred_high_risk",
        "tools/lib/bpf/zigux_segments/object_loader.zig",
    ),
    (
        "phase12-libbpf-btf-relocation-and-program-load",
        "deferred_high_risk",
        "tools/lib/bpf/zigux_segments/relocation.zig",
    ),
]

LEGACY_SEGMENT_SPECS = [
    (
        "logging-version-and-errno",
        "starter_landed",
        "tools/lib/bpf/zigux_segments/logging.zig",
    ),
    (
        "pin-path-helpers",
        "starter_landed",
        "tools/lib/bpf/zigux_segments/pin_path.zig",
    ),
    (
        "cpu-mask-parsing",
        "starter_landed",
        "tools/lib/bpf/zigux_segments/cpu_mask.zig",
    ),
    (
        "perf-buffer-poll-helper",
        "starter_landed",
        "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
    ),
    (
        "type-name-helpers",
        "starter_landed",
        "tools/lib/bpf/zigux_segments/type_names.zig",
    ),
    (
        "fdinfo-map-info-helpers",
        "starter_landed",
        "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
    ),
    (
        "map-reuse-compatibility",
        "starter_landed",
        "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
    ),
    (
        "file-path-and-handle-bridge",
        "deferred_high_risk",
        "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
    ),
    (
        "perf-buffer-online-cpu-routing",
        "deferred_high_risk",
        "tools/lib/bpf/zigux_segments/cpu_mask.zig",
    ),
    (
        "skeleton-population",
        "blocked_on_object_model",
        "tools/lib/bpf/zigux_segments/skeleton.zig",
    ),
    (
        "object-and-elf-loader",
        "deferred_high_risk",
        "tools/lib/bpf/zigux_segments/object_loader.zig",
    ),
    (
        "btf-relocation-and-program-load",
        "deferred_high_risk",
        "tools/lib/bpf/zigux_segments/relocation.zig",
    ),
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def load_json(root: Path, rel_path: str) -> dict[str, object]:
    return json.loads(read_text(root, rel_path))


def find_item(items: list[dict[str, object]], key: str, value: str) -> dict[str, object] | None:
    for item in items:
        if item.get(key) == value:
            return item
    return None


def has_valid_commit(value: object) -> bool:
    return isinstance(value, str) and len(value) == 40


def check_manifest_rollback_contract(rollback_contract: object, missing: list[str]) -> None:
    if not isinstance(rollback_contract, dict):
        missing.append("manifest:rollback_contract")
        return

    for key in ("owner", "rollback_owner", "fallback_path"):
        if rollback_contract.get(key) != MANIFEST_ROLLBACK_CONTRACT[key]:
            missing.append(f"manifest:rollback_contract:{key}")

    for key in ("reversible_delivery_evidence", "rollback_drill"):
        value = rollback_contract.get(key)
        if not isinstance(value, list) or value != MANIFEST_ROLLBACK_CONTRACT[key]:
            missing.append(f"manifest:rollback_contract:{key}")


def check_packet(root: Path) -> list[str]:
    missing: list[str] = []
    for rel_path in TRACKED_PATHS:
        if not (root / rel_path).exists():
            missing.append(f"missing_file:{rel_path}")

    if missing:
        return missing

    manifest = load_json(root, TRACKED_PATHS[0])
    snapshot = load_json(root, "zigux/tests/fixtures/phase12_libbpf_snapshot.json")
    legacy_manifest = load_json(root, TRACKED_PATHS[4])
    survey_note = read_text(root, TRACKED_PATHS[3])
    segment_test = read_text(root, TRACKED_PATHS[1])
    reviewability_test = read_text(root, TRACKED_PATHS[2])

    if manifest.get("lane_key") != "P12-L16":
        missing.append("manifest:lane_key")
    if manifest.get("phase") != "Phase 12":
        missing.append("manifest:phase")
    if manifest.get("anchor") != "tools/lib/bpf/libbpf.c":
        missing.append("manifest:anchor")
    check_manifest_rollback_contract(manifest.get("rollback_contract"), missing)
    surveyed_commit = manifest.get("surveyed_commit")
    if not has_valid_commit(surveyed_commit):
        missing.append("manifest:surveyed_commit")
        surveyed_commit = ""

    if legacy_manifest.get("lane_key") != "P8-L15":
        missing.append("legacy_manifest:lane_key")
    if legacy_manifest.get("phase") != "Phase 8":
        missing.append("legacy_manifest:phase")
    if legacy_manifest.get("anchor") != "tools/lib/bpf/libbpf.c":
        missing.append("legacy_manifest:anchor")
    if not has_valid_commit(legacy_manifest.get("surveyed_commit")):
        missing.append("legacy_manifest:surveyed_commit")

    if snapshot.get("lane_key") != manifest.get("lane_key"):
        missing.append("snapshot:lane_key")
    if snapshot.get("phase") != manifest.get("phase"):
        missing.append("snapshot:phase")
    if snapshot.get("surveyed_commit") != manifest.get("surveyed_commit"):
        missing.append("snapshot:surveyed_commit")

    if snapshot.get("tracked_file_count") != len(TRACKED_PATHS):
        missing.append("snapshot:tracked_file_count")
    files = snapshot.get("files")
    if not isinstance(files, list):
        missing.append("snapshot:files")
        files = []
    else:
        actual_paths = [entry.get("path") for entry in files if isinstance(entry, dict)]
        if actual_paths != TRACKED_PATHS:
            missing.append("snapshot:tracked_paths")

    if surveyed_commit:
        if surveyed_commit not in survey_note:
            missing.append("survey_note:surveyed_commit")
        if surveyed_commit not in segment_test:
            missing.append("segment_test:surveyed_commit")

    for marker in SURVEY_NOTE_MARKERS:
        if marker not in survey_note:
            missing.append(f"survey_note:{marker}")

    for marker in SEGMENT_TEST_MARKERS:
        if marker not in segment_test:
            missing.append(f"segment_test:{marker}")

    for marker in REVIEWABILITY_MARKERS:
        if marker not in reviewability_test:
            missing.append(f"reviewability_test:{marker}")

    manifest_gaps = manifest.get("gaps")
    if not isinstance(manifest_gaps, list):
        missing.append("manifest:gaps")
        manifest_gaps = []
    legacy_segments = legacy_manifest.get("segments")
    if not isinstance(legacy_segments, list):
        missing.append("legacy_manifest:segments")
        legacy_segments = []

    for gap_id, status, destination in PHASE12_GAP_SPECS:
        gap = find_item(manifest_gaps, "id", gap_id)
        if gap is None:
            missing.append(f"manifest_gap:{gap_id}")
            continue
        if gap.get("status") != status:
            missing.append(f"manifest_gap_status:{gap_id}")
        if gap.get("zigux_destination") != destination:
            missing.append(f"manifest_gap_destination:{gap_id}")

    for slug, status, destination in LEGACY_SEGMENT_SPECS:
        segment = find_item(legacy_segments, "slug", slug)
        if segment is None:
            missing.append(f"legacy_segment:{slug}")
            continue
        if segment.get("status") != status:
            missing.append(f"legacy_segment_status:{slug}")
        if segment.get("zigux_destination") != destination:
            missing.append(f"legacy_segment_destination:{slug}")

    return missing


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_self_test_tree(root: Path) -> None:
    surveyed_commit = "2df10deb8b6f2ab013ee2f289a49e6aa33180656"
    manifest = {
        "lane_key": "P12-L16",
        "phase": "Phase 12",
        "surveyed_commit": surveyed_commit,
        "anchor": "tools/lib/bpf/libbpf.c",
        "rollback_contract": MANIFEST_ROLLBACK_CONTRACT,
        "gaps": [
            {"id": gap_id, "status": status, "zigux_destination": destination}
            for gap_id, status, destination in PHASE12_GAP_SPECS
        ],
    }
    legacy_manifest = {
        "lane_key": "P8-L15",
        "phase": "Phase 8",
        "surveyed_commit": "36414e38da67a51209095d0c06170f81e80258eb",
        "anchor": "tools/lib/bpf/libbpf.c",
        "segments": [
            {"slug": slug, "status": status, "zigux_destination": destination}
            for slug, status, destination in LEGACY_SEGMENT_SPECS
        ],
    }
    snapshot = {
        "lane_key": "P12-L16",
        "phase": "Phase 12",
        "surveyed_commit": surveyed_commit,
        "tracked_file_count": len(TRACKED_PATHS),
        "files": [{"path": rel_path, "bytes": 1, "sha256": "0" * 64} for rel_path in TRACKED_PATHS],
    }
    survey_note = "\n".join(
        [
            f"surveyed head {surveyed_commit}",
            *SURVEY_NOTE_MARKERS,
        ]
    )
    segment_test = "\n".join([f'const current_surveyed_commit = "{surveyed_commit}";', *SEGMENT_TEST_MARKERS])
    reviewability_test = "\n".join(REVIEWABILITY_MARKERS)

    write(root / TRACKED_PATHS[0], json.dumps(manifest, indent=2) + "\n")
    write(root / "zigux/tests/fixtures/phase12_libbpf_snapshot.json", json.dumps(snapshot, indent=2) + "\n")
    write(root / TRACKED_PATHS[3], survey_note + "\n")
    write(root / TRACKED_PATHS[1], segment_test + "\n")
    write(root / TRACKED_PATHS[2], reviewability_test + "\n")
    write(root / TRACKED_PATHS[4], json.dumps(legacy_manifest, indent=2) + "\n")
    for rel_path in {
        destination for _, _, destination in PHASE12_GAP_SPECS if destination.endswith(".zig")
    } | {
        destination for _, _, destination in LEGACY_SEGMENT_SPECS if destination.endswith(".zig")
    }:
        if "skeleton.zig" in rel_path or "object_loader.zig" in rel_path or "relocation.zig" in rel_path:
            continue
        write(root / rel_path, "// synthetic helper\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase12_libbpf_packet_") as tmp_dir_str:
        root = Path(tmp_dir_str)
        build_self_test_tree(root)
        missing = check_packet(root)
        if missing:
            raise SystemExit(
                "phase12-libbpf-packet:self-test:unexpected_failures:" + ",".join(missing)
            )

        survey_note_path = root / TRACKED_PATHS[3]
        original = survey_note_path.read_text(encoding="utf-8")
        survey_note_path.write_text(
            original.replace(
                "python3 scripts/zigux/check-phase12-libbpf-packet.py --self-test",
                "python3 scripts/zigux/check-phase12-libbpf-packet.py",
            ),
            encoding="utf-8",
        )
        missing = check_packet(root)
        if "survey_note:python3 scripts/zigux/check-phase12-libbpf-packet.py --self-test" not in missing:
            raise SystemExit("phase12-libbpf-packet:self-test:missing_marker_detection")

        build_self_test_tree(root)
        survey_note_path = root / TRACKED_PATHS[3]
        original = survey_note_path.read_text(encoding="utf-8")
        survey_note_path.write_text(
            original.replace(
                "automatic perf-buffer CPU-budget clamp explicit before any per-CPU buffer opens happen\n",
                "",
            ),
            encoding="utf-8",
        )
        missing = check_packet(root)
        if (
            "survey_note:automatic perf-buffer CPU-budget clamp explicit before any per-CPU buffer opens happen"
            not in missing
        ):
            raise SystemExit("phase12-libbpf-packet:self-test:perf_buffer_clamp_marker_detection")

        build_self_test_tree(root)
        survey_note_path = root / TRACKED_PATHS[3]
        original = survey_note_path.read_text(encoding="utf-8")
        survey_note_path.write_text(
            original.replace(
                "optional probes still degrade gracefully, mandatory probes still fail hard\n",
                "",
            ),
            encoding="utf-8",
        )
        missing = check_packet(root)
        if (
            "survey_note:optional probes still degrade gracefully, mandatory probes still fail hard"
            not in missing
        ):
            raise SystemExit("phase12-libbpf-packet:self-test:recovery_split_marker_detection")

        build_self_test_tree(root)
        snapshot_path = root / "zigux/tests/fixtures/phase12_libbpf_snapshot.json"
        snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
        snapshot["tracked_file_count"] = len(TRACKED_PATHS) + 1
        snapshot_path.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
        missing = check_packet(root)
        if "snapshot:tracked_file_count" not in missing:
            raise SystemExit("phase12-libbpf-packet:self-test:tracked_count_detection")

        build_self_test_tree(root)
        manifest_path = root / TRACKED_PATHS[0]
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["lane_key"] = "P12-L99"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        missing = check_packet(root)
        if "manifest:lane_key" not in missing:
            raise SystemExit("phase12-libbpf-packet:self-test:manifest_lane_detection")

        build_self_test_tree(root)
        manifest_path = root / TRACKED_PATHS[0]
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["rollback_contract"]["fallback_path"] = "tools/lib/bpf/libbpf_alt.c"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        missing = check_packet(root)
        if "manifest:rollback_contract:fallback_path" not in missing:
            raise SystemExit("phase12-libbpf-packet:self-test:rollback_contract_detection")

        build_self_test_tree(root)
        legacy_manifest_path = root / TRACKED_PATHS[4]
        legacy_manifest = json.loads(legacy_manifest_path.read_text(encoding="utf-8"))
        for segment in legacy_manifest["segments"]:
            if segment["slug"] == "map-reuse-compatibility":
                segment["status"] = "deferred_high_risk"
                break
        legacy_manifest_path.write_text(
            json.dumps(legacy_manifest, indent=2) + "\n",
            encoding="utf-8",
        )
        missing = check_packet(root)
        if "legacy_segment_status:map-reuse-compatibility" not in missing:
            raise SystemExit("phase12-libbpf-packet:self-test:legacy_status_detection")

        build_self_test_tree(root)
        legacy_manifest_path = root / TRACKED_PATHS[4]
        legacy_manifest = json.loads(legacy_manifest_path.read_text(encoding="utf-8"))
        legacy_manifest["segments"] = [
            segment
            for segment in legacy_manifest["segments"]
            if segment["slug"] != "perf-buffer-poll-helper"
        ]
        legacy_manifest_path.write_text(
            json.dumps(legacy_manifest, indent=2) + "\n",
            encoding="utf-8",
        )
        missing = check_packet(root)
        if "legacy_segment:perf-buffer-poll-helper" not in missing:
            raise SystemExit("phase12-libbpf-packet:self-test:legacy_segment_presence_detection")

        build_self_test_tree(root)
        manifest_path = root / TRACKED_PATHS[0]
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["anchor"] = "tools/lib/bpf/libbpf_alt.c"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        missing = check_packet(root)
        if "manifest:anchor" not in missing:
            raise SystemExit("phase12-libbpf-packet:self-test:manifest_anchor_detection")

        build_self_test_tree(root)
        legacy_manifest_path = root / TRACKED_PATHS[4]
        legacy_manifest = json.loads(legacy_manifest_path.read_text(encoding="utf-8"))
        legacy_manifest["anchor"] = "tools/lib/bpf/libbpf_alt.c"
        legacy_manifest_path.write_text(
            json.dumps(legacy_manifest, indent=2) + "\n",
            encoding="utf-8",
        )
        missing = check_packet(root)
        if "legacy_manifest:anchor" not in missing:
            raise SystemExit("phase12-libbpf-packet:self-test:legacy_anchor_detection")

        build_self_test_tree(root)
        legacy_manifest_path = root / TRACKED_PATHS[4]
        legacy_manifest = json.loads(legacy_manifest_path.read_text(encoding="utf-8"))
        legacy_manifest["surveyed_commit"] = "deadbeef"
        legacy_manifest_path.write_text(
            json.dumps(legacy_manifest, indent=2) + "\n",
            encoding="utf-8",
        )
        missing = check_packet(root)
        if "legacy_manifest:surveyed_commit" not in missing:
            raise SystemExit("phase12-libbpf-packet:self-test:legacy_surveyed_commit_detection")

        print("PHASE12_LIBBPF_PACKET_SELF_TEST=pass")
        print("PHASE12_LIBBPF_PACKET_SELF_TEST_CASE_COUNT=12")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check the bounded Phase 12 libbpf packet across the manifest, survey note, snapshot fixture, and reviewability gates."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run a synthetic self-test for the bounded libbpf packet checker.",
    )
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()

    root = Path(__file__).resolve().parents[2]
    missing = check_packet(root)
    if missing:
        print("PHASE12_LIBBPF_PACKET_ALIGNMENT=fail")
        print("PHASE12_LIBBPF_PACKET_ALIGNMENT_MISSING_START")
        for item in missing:
            print(item)
        print("PHASE12_LIBBPF_PACKET_ALIGNMENT_MISSING_END")
        return 1

    print("PHASE12_LIBBPF_PACKET_ALIGNMENT=pass")
    print(f"PHASE12_LIBBPF_PACKET_TRACKED_FILE_COUNT={len(TRACKED_PATHS)}")
    print(f"PHASE12_LIBBPF_PACKET_GAP_COUNT={len(PHASE12_GAP_SPECS)}")
    print(f"PHASE12_LIBBPF_PACKET_LEGACY_SEGMENT_COUNT={len(LEGACY_SEGMENT_SPECS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
