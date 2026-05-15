#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import tempfile


def repo_root() -> Path:
    resolved = Path(__file__).resolve()
    return resolved.parents[2] if len(resolved.parents) >= 3 else resolved.parent


ROOT = repo_root()
SNAPSHOT_PATH = "zigux/tests/fixtures/phase12_libbpf_snapshot.json"
SURVEY_PATH = "Documentation/zigux/phase12-libbpf-segment-survey.md"
VERIFY_NOTE_PATH = "Documentation/zigux/phase12-libbpf-verify-shard-note.md"
MANIFEST_PATH = "tools/lib/bpf/zigux_segments/manifest.json"

SUPPORTING_NOTES = [
    "Documentation/zigux/phase12-libbpf-segment-survey.md",
    "Documentation/zigux/phase12-libbpf-verify-shard-note.md",
    "Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md",
    "Documentation/zigux/phase12-release-coordination-matrix.md",
]

PIN_PATH = "tools/lib/bpf/zigux_segments/pin_path.zig"
ABSENT_BOUNDARY_MARKERS = [
    PIN_PATH,
    "zigux/tests/phase12_libbpf_manifest.json",
    "zigux/tests/phase12_libbpf_segments.zig",
    "zigux/tests/phase12_libbpf_reviewability.zig",
    "tools/lib/bpf/zigux_segments/verify.zig",
    "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
]

SURVEY_MARKERS = [
    "the older `pin_path.zig` helper now survives only as historical catalog evidence",
    "it no longer exposes `tools/lib/bpf/zigux_segments/pin_path.zig` as a directly readable current-`master` file.",
]

VERIFY_MARKERS = [
    "the earlier note shape assumed imports from `logging.zig`, `pin_path.zig`, `cpu_mask.zig`, `type_names.zig`, `file_path_handle_bridge.zig`, and `perf_buffer_poll.zig`",
    "while `pin_path.zig`, the direct `phase12_libbpf_*` replay files, `tools/lib/bpf/zigux_segments/verify.zig`, and `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` are still absent from current `master`",
]

MANIFEST_MARKERS = [
    '"slug": "pin-path-helpers"',
    f'"zigux_destination": "{PIN_PATH}"',
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(root: Path, rel_path: str, content: str) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def check_alignment(root: Path) -> list[str]:
    missing: list[str] = []
    for rel_path in [SNAPSHOT_PATH, SURVEY_PATH, VERIFY_NOTE_PATH, MANIFEST_PATH]:
        if not (root / rel_path).exists():
            return [f"missing_file:{rel_path}"]

    snapshot = json.loads(read_text(root, SNAPSHOT_PATH))
    supporting_notes = snapshot.get("supporting_notes")
    files = snapshot.get("files")
    absent_boundaries = snapshot.get("parked_absent_boundaries")

    if supporting_notes != SUPPORTING_NOTES:
        missing.append("snapshot:supporting_notes")

    if not isinstance(files, list):
        missing.append("snapshot:files")
        files = []

    if snapshot.get("tracked_file_count") != len(files):
        missing.append("snapshot:tracked_file_count")

    file_paths = [entry.get("path") for entry in files if isinstance(entry, dict)]
    if file_paths != SUPPORTING_NOTES:
        missing.append("snapshot:files_paths")

    if not isinstance(absent_boundaries, list):
        missing.append("snapshot:parked_absent_boundaries")
        absent_boundaries = []

    for marker in ABSENT_BOUNDARY_MARKERS:
        if marker not in absent_boundaries:
            missing.append(f"snapshot:parked_absent_boundaries:{marker}")

    survey = read_text(root, SURVEY_PATH)
    for marker in SURVEY_MARKERS:
        if marker not in survey:
            missing.append(f"survey:{marker}")

    verify = read_text(root, VERIFY_NOTE_PATH)
    for marker in VERIFY_MARKERS:
        if marker not in verify:
            missing.append(f"verify:{marker}")

    manifest = read_text(root, MANIFEST_PATH)
    for marker in MANIFEST_MARKERS:
        if marker not in manifest:
            missing.append(f"manifest:{marker}")

    return missing


def build_self_test_tree(root: Path) -> None:
    write_text(
        root,
        SNAPSHOT_PATH,
        json.dumps(
            {
                "lane_key": "P12-Y04",
                "phase": "Phase 12",
                "surveyed_commit": "6726fdd9da4eef55498fb06c38815317a684bcbf",
                "snapshot_scope": "parked Phase 12 libbpf note packet on current master",
                "tracked_file_count": 4,
                "supporting_notes": SUPPORTING_NOTES,
                "parked_absent_boundaries": ABSENT_BOUNDARY_MARKERS,
                "files": [
                    {"path": note, "blob_sha": f"sha-{index}"}
                    for index, note in enumerate(SUPPORTING_NOTES, start=1)
                ],
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        root,
        SURVEY_PATH,
        "\n".join(
            [
                "# Phase 12 Libbpf Segment Survey",
                SURVEY_MARKERS[0],
                SURVEY_MARKERS[1],
                "",
            ]
        ),
    )
    write_text(
        root,
        VERIFY_NOTE_PATH,
        "\n".join(
            [
                "# Phase 12 Libbpf Verify Shard Note",
                VERIFY_MARKERS[0],
                VERIFY_MARKERS[1],
                "",
            ]
        ),
    )
    write_text(
        root,
        MANIFEST_PATH,
        "\n".join(
            [
                "{",
                '  "segments": [',
                '    {',
                f'      {MANIFEST_MARKERS[0]},',
                f'      {MANIFEST_MARKERS[1]}',
                "    }",
                "  ]",
                "}",
                "",
            ]
        ),
    )


def expect_contains(label: str, items: list[str], expected: str) -> None:
    if expected not in items:
        raise SystemExit(f"phase12-libbpf-snapshot-packet:self-test:{label}:{expected}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase12_libbpf_snapshot_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_tree(root)
        if check_alignment(root):
            raise SystemExit("phase12-libbpf-snapshot-packet:self-test:baseline")

        build_self_test_tree(root)
        (root / SNAPSHOT_PATH).unlink()
        expect_contains(
            "missing_snapshot",
            check_alignment(root),
            f"missing_file:{SNAPSHOT_PATH}",
        )

        build_self_test_tree(root)
        snapshot = json.loads(read_text(root, SNAPSHOT_PATH))
        snapshot["tracked_file_count"] = 3
        write_text(root, SNAPSHOT_PATH, json.dumps(snapshot, indent=2) + "\n")
        expect_contains(
            "tracked_file_count_drift",
            check_alignment(root),
            "snapshot:tracked_file_count",
        )

        build_self_test_tree(root)
        snapshot = json.loads(read_text(root, SNAPSHOT_PATH))
        snapshot["parked_absent_boundaries"] = [
            item for item in snapshot["parked_absent_boundaries"] if item != PIN_PATH
        ]
        write_text(root, SNAPSHOT_PATH, json.dumps(snapshot, indent=2) + "\n")
        expect_contains(
            "pin_path_absent_boundary_drift",
            check_alignment(root),
            f"snapshot:parked_absent_boundaries:{PIN_PATH}",
        )

        build_self_test_tree(root)
        snapshot = json.loads(read_text(root, SNAPSHOT_PATH))
        snapshot["supporting_notes"] = SUPPORTING_NOTES[:-1]
        write_text(root, SNAPSHOT_PATH, json.dumps(snapshot, indent=2) + "\n")
        expect_contains(
            "supporting_notes_drift",
            check_alignment(root),
            "snapshot:supporting_notes",
        )

        build_self_test_tree(root)
        write_text(root, SURVEY_PATH, "# Phase 12 Libbpf Segment Survey\n")
        expect_contains(
            "survey_marker_drift",
            check_alignment(root),
            f"survey:{SURVEY_MARKERS[0]}",
        )

        build_self_test_tree(root)
        write_text(root, VERIFY_NOTE_PATH, "# Phase 12 Libbpf Verify Shard Note\n")
        expect_contains(
            "verify_marker_drift",
            check_alignment(root),
            f"verify:{VERIFY_MARKERS[0]}",
        )

        build_self_test_tree(root)
        write_text(root, MANIFEST_PATH, "{}\n")
        expect_contains(
            "manifest_marker_drift",
            check_alignment(root),
            f"manifest:{MANIFEST_MARKERS[0]}",
        )

    print("PHASE12_LIBBPF_SNAPSHOT_PACKET_SELF_TEST=pass")
    print("PHASE12_LIBBPF_SNAPSHOT_PACKET_SELF_TEST_CASE_COUNT=7")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the Phase 12 libbpf snapshot packet still records the current "
            "pin_path absence boundary and the paired survey, verify-note, and legacy "
            "manifest markers."
        )
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run synthetic snapshot-packet drift checks.",
    )
    parser.add_argument(
        "--root",
        default=str(ROOT),
        help="Repository root to inspect.",
    )
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()

    missing = check_alignment(Path(args.root))
    if missing:
        print("PHASE12_LIBBPF_SNAPSHOT_PACKET=fail")
        print("PHASE12_LIBBPF_SNAPSHOT_PACKET_MISSING_START")
        for item in missing:
            print(item)
        print("PHASE12_LIBBPF_SNAPSHOT_PACKET_MISSING_END")
        return 1

    print("PHASE12_LIBBPF_SNAPSHOT_PACKET=pass")
    print(
        "PHASE12_LIBBPF_SNAPSHOT_PACKET_TRACKED_FILES="
        f"{','.join([SNAPSHOT_PATH, SURVEY_PATH, VERIFY_NOTE_PATH, MANIFEST_PATH])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())