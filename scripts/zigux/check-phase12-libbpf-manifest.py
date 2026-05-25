#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parent.parent.parent if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent
MANIFEST_PATH = Path("tools/lib/bpf/zigux_segments/manifest.json")

EXPECTED_LANE_KEY = "P8-L13"
EXPECTED_PHASE = "Phase 8"
EXPECTED_ANCHOR = "tools/lib/bpf/libbpf.c"
EXPECTED_COMPANION_C_PATHS = [
    "tools/lib/bpf/bpf.c",
    "tools/lib/bpf/btf.c",
    "tools/lib/bpf/features.c",
    "tools/lib/bpf/libbpf_utils.c",
    "tools/lib/bpf/linker.c",
    "tools/lib/bpf/netlink.c",
    "tools/lib/bpf/nlattr.c",
    "tools/lib/bpf/ringbuf.c",
]
EXPECTED_SEGMENTS = [
    ("logging-version-and-errno", "starter_landed", "tools/lib/bpf/zigux_segments/logging.zig"),
    ("pin-path-helpers", "starter_landed", "tools/lib/bpf/zigux_segments/pin_path.zig"),
    ("cpu-mask-parsing", "starter_landed", "tools/lib/bpf/zigux_segments/cpu_mask.zig"),
    ("type-name-helpers", "starter_landed", "tools/lib/bpf/zigux_segments/type_names.zig"),
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
        "tools/lib/bpf/zigux_segments/online_cpu_routing.zig",
    ),
    ("skeleton-population", "blocked_on_object_model", "tools/lib/bpf/zigux_segments/skeleton.zig"),
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
    (
        "perf-buffer-poll-bookkeeping",
        "starter_landed",
        "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
    ),
]
EXPECTED_SEGMENTATION_NOTE_DESTINATION = "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig"
EXPECTED_SEGMENTATION_NOTE_LANDED_SCOPE_COUNT = 12
EXPECTED_SEGMENTATION_NOTE_QUEUED_SCOPE_COUNT = 2
SELF_TEST_CASE_COUNT = 8


def is_hex_sha(value: object) -> bool:
    return isinstance(value, str) and len(value) == 40 and all(ch in "0123456789abcdef" for ch in value)


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, packet: dict[str, object]) -> None:
    path.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")


def collect_missing(root: Path) -> list[str]:
    manifest_path = root / MANIFEST_PATH
    if not manifest_path.exists():
        return [f"missing_file:{MANIFEST_PATH.as_posix()}"]

    packet = load_json(manifest_path)
    missing: list[str] = []

    if packet.get("lane_key") != EXPECTED_LANE_KEY:
        missing.append(f"lane_key:{EXPECTED_LANE_KEY}")
    if packet.get("phase") != EXPECTED_PHASE:
        missing.append(f"phase:{EXPECTED_PHASE}")
    if packet.get("anchor") != EXPECTED_ANCHOR:
        missing.append(f"anchor:{EXPECTED_ANCHOR}")
    if not is_hex_sha(packet.get("surveyed_commit")):
        missing.append("surveyed_commit:sha1")

    survey_summary = packet.get("survey_summary")
    if not isinstance(survey_summary, dict):
        missing.append("survey_summary:shape")
    else:
        if survey_summary.get("preexisting_zigux_segments_present") is not True:
            missing.append("survey_summary:preexisting_zigux_segments_present:true")
        if survey_summary.get("preexisting_phase8_libbpf_note_present") is not True:
            missing.append("survey_summary:preexisting_phase8_libbpf_note_present:true")

        companion_c_files = survey_summary.get("companion_c_files")
        if not isinstance(companion_c_files, list):
            missing.append("survey_summary:companion_c_files:list")
        else:
            actual_paths = [entry.get("path") for entry in companion_c_files if isinstance(entry, dict)]
            if actual_paths != EXPECTED_COMPANION_C_PATHS:
                missing.append("survey_summary:companion_c_files:exact_order")

    segments = packet.get("segments")
    if not isinstance(segments, list):
        missing.append("segments:list")
    else:
        actual_segments = [
            (entry.get("slug"), entry.get("status"), entry.get("zigux_destination"))
            for entry in segments
            if isinstance(entry, dict)
        ]
        if actual_segments != EXPECTED_SEGMENTS:
            missing.append("segments:exact_triplets")

    segmentation_notes = packet.get("segmentation_notes")
    if not isinstance(segmentation_notes, list) or len(segmentation_notes) != 1:
        missing.append("segmentation_notes:shape")
    elif not isinstance(segmentation_notes[0], dict):
        missing.append("segmentation_notes:shape")
    else:
        note = segmentation_notes[0]
        if note.get("destination") != EXPECTED_SEGMENTATION_NOTE_DESTINATION:
            missing.append(
                f"segmentation_notes:destination:{EXPECTED_SEGMENTATION_NOTE_DESTINATION}"
            )

        landed_scope = note.get("landed_scope")
        if not isinstance(landed_scope, list) or len(landed_scope) != EXPECTED_SEGMENTATION_NOTE_LANDED_SCOPE_COUNT:
            missing.append(
                f"segmentation_notes:landed_scope:length:{EXPECTED_SEGMENTATION_NOTE_LANDED_SCOPE_COUNT}"
            )

        queued_scope = note.get("queued_scope")
        if not isinstance(queued_scope, list) or len(queued_scope) != EXPECTED_SEGMENTATION_NOTE_QUEUED_SCOPE_COUNT:
            missing.append(
                f"segmentation_notes:queued_scope:length:{EXPECTED_SEGMENTATION_NOTE_QUEUED_SCOPE_COUNT}"
            )

    return missing


def build_fixture_tree(root: Path) -> None:
    manifest_path = root / MANIFEST_PATH
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    packet = {
        "lane_key": EXPECTED_LANE_KEY,
        "phase": EXPECTED_PHASE,
        "surveyed_commit": "3fbd40a49963769118cb15f2aadfc175540c833d",
        "anchor": EXPECTED_ANCHOR,
        "survey_summary": {
            "libbpf_c_lines": 14771,
            "preexisting_zigux_segments_present": True,
            "preexisting_phase8_libbpf_note_present": True,
            "companion_c_files": [
                {"path": path, "lines": index + 1}
                for index, path in enumerate(EXPECTED_COMPANION_C_PATHS)
            ],
        },
        "segments": [
            {
                "id": f"P8-L13-S{index + 1:02d}",
                "slug": slug,
                "status": status,
                "zigux_destination": destination,
            }
            for index, (slug, status, destination) in enumerate(EXPECTED_SEGMENTS)
        ],
        "segmentation_notes": [
            {
                "destination": EXPECTED_SEGMENTATION_NOTE_DESTINATION,
                "landed_scope": [f"scope-{index}" for index in range(EXPECTED_SEGMENTATION_NOTE_LANDED_SCOPE_COUNT)],
                "queued_scope": [f"queued-{index}" for index in range(EXPECTED_SEGMENTATION_NOTE_QUEUED_SCOPE_COUNT)],
            }
        ],
    }
    write_json(manifest_path, packet)


def expect_case(tmp_root: Path, expected_item: str, case_name: str) -> None:
    missing = collect_missing(tmp_root)
    if expected_item not in missing:
        raise SystemExit(f"phase12-libbpf-manifest:self-test:{case_name}:{missing}")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase12_libbpf_manifest_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        build_fixture_tree(tmp_root)

        if collect_missing(tmp_root) != []:
            raise SystemExit("phase12-libbpf-manifest:self-test:clean_fixture")

        manifest_path = tmp_root / MANIFEST_PATH

        packet = load_json(manifest_path)
        packet["lane_key"] = "P8-X13"
        write_json(manifest_path, packet)
        expect_case(tmp_root, f"lane_key:{EXPECTED_LANE_KEY}", "lane_key")
        build_fixture_tree(tmp_root)

        packet = load_json(manifest_path)
        packet["phase"] = "Phase 99"
        write_json(manifest_path, packet)
        expect_case(tmp_root, f"phase:{EXPECTED_PHASE}", "phase")
        build_fixture_tree(tmp_root)

        packet = load_json(manifest_path)
        packet["anchor"] = "tools/lib/bpf/other.c"
        write_json(manifest_path, packet)
        expect_case(tmp_root, f"anchor:{EXPECTED_ANCHOR}", "anchor")
        build_fixture_tree(tmp_root)

        packet = load_json(manifest_path)
        packet["surveyed_commit"] = "not-a-sha"
        write_json(manifest_path, packet)
        expect_case(tmp_root, "surveyed_commit:sha1", "surveyed_commit")
        build_fixture_tree(tmp_root)

        packet = load_json(manifest_path)
        packet["survey_summary"]["companion_c_files"][-1]["path"] = "tools/lib/bpf/ringbuf_other.c"
        write_json(manifest_path, packet)
        expect_case(tmp_root, "survey_summary:companion_c_files:exact_order", "companion_c_files")
        build_fixture_tree(tmp_root)

        packet = load_json(manifest_path)
        packet["segments"][-1]["slug"] = "perf-buffer-poll-other"
        write_json(manifest_path, packet)
        expect_case(tmp_root, "segments:exact_triplets", "segments")
        build_fixture_tree(tmp_root)

        packet = load_json(manifest_path)
        packet["segmentation_notes"][0]["destination"] = "tools/lib/bpf/zigux_segments/other.zig"
        write_json(manifest_path, packet)
        expect_case(
            tmp_root,
            f"segmentation_notes:destination:{EXPECTED_SEGMENTATION_NOTE_DESTINATION}",
            "segmentation_destination",
        )
        build_fixture_tree(tmp_root)

        packet = load_json(manifest_path)
        packet["segmentation_notes"][0]["queued_scope"] = ["queued-0"]
        write_json(manifest_path, packet)
        expect_case(
            tmp_root,
            f"segmentation_notes:queued_scope:length:{EXPECTED_SEGMENTATION_NOTE_QUEUED_SCOPE_COUNT}",
            "queued_scope_length",
        )

    print("PHASE12_LIBBPF_MANIFEST_SELF_TEST=pass")
    print(f"PHASE12_LIBBPF_MANIFEST_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed when the historical libbpf helper manifest drifts."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker self-tests.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    missing = collect_missing(args.root)
    if missing:
        print("PHASE12_LIBBPF_MANIFEST=fail")
        print("PHASE12_LIBBPF_MANIFEST_MISSING_START")
        for item in missing:
            print(item)
        print("PHASE12_LIBBPF_MANIFEST_MISSING_END")
        return 1

    print("PHASE12_LIBBPF_MANIFEST=pass")
    print(f"PHASE12_LIBBPF_MANIFEST_SEGMENT_COUNT={len(EXPECTED_SEGMENTS)}")
    print(
        "PHASE12_LIBBPF_MANIFEST_COMPANION_C_FILE_COUNT="
        f"{len(EXPECTED_COMPANION_C_PATHS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
