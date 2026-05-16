#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

SNAPSHOT_PATH = "zigux/tests/fixtures/phase12_libbpf_snapshot.json"
SURVEY_PATH = "Documentation/zigux/phase12-libbpf-segment-survey.md"
VERIFY_PATH = "Documentation/zigux/phase12-libbpf-verify-shard-note.md"
SEQUENCING_PATH = "Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md"
COORDINATION_PATH = "Documentation/zigux/phase12-release-coordination-matrix.md"
MANIFEST_PATH = "tools/lib/bpf/zigux_segments/manifest.json"
CHECKER_PATH = "scripts/zigux/check-phase12-libbpf-snapshot.py"

EXPECTED_SUPPORTING_NOTES = [
    SURVEY_PATH,
    VERIFY_PATH,
    SEQUENCING_PATH,
    COORDINATION_PATH,
]

PRESENT_HELPER_FILES = [
    "tools/lib/bpf/zigux_segments/logging.zig",
    "tools/lib/bpf/zigux_segments/cpu_mask.zig",
    "tools/lib/bpf/zigux_segments/type_names.zig",
    "tools/lib/bpf/zigux_segments/online_cpu_routing.zig",
    "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
    MANIFEST_PATH,
]

PARKED_ABSENT_BOUNDARIES = [
    "tools/lib/bpf/zigux_segments/pin_path.zig",
    "zigux/tests/phase12_libbpf_manifest.json",
    "zigux/tests/phase12_libbpf_segments.zig",
    "zigux/tests/phase12_libbpf_reviewability.zig",
    "tools/lib/bpf/zigux_segments/verify.zig",
    "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
]

REQUIRED_MARKERS = {
    SURVEY_PATH: [
        SNAPSHOT_PATH,
        "parked reviewability packet visible",
        f"`{CHECKER_PATH}`",
        "`tools/lib/bpf/zigux_segments/manifest.json` catalog",
        "tools/lib/bpf/zigux_segments/verify.zig",
        "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
    ],
    VERIFY_PATH: [
        SNAPSHOT_PATH,
        "`surveyed_commit`",
        "historical reproducibility evidence",
        "tools/lib/bpf/zigux_segments/verify.zig",
        "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
    ],
    SEQUENCING_PATH: [
        SNAPSHOT_PATH,
        f"`{CHECKER_PATH}`",
        "parked note-owned boundaries",
        "tools/lib/bpf/zigux_segments/verify.zig",
        "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
    ],
    COORDINATION_PATH: [
        SNAPSHOT_PATH,
        "parked reviewability packet visible",
        "tools/lib/bpf/zigux_segments/manifest.json",
    ],
    MANIFEST_PATH: [
        "\"zigux_destination\": \"tools/lib/bpf/zigux_segments/pin_path.zig\"",
        "\"zigux_destination\": \"tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig\"",
    ],
}


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("utf-8")
    return hashlib.sha1(header + data).hexdigest()


def load_snapshot(root: Path) -> dict:
    return json.loads((root / SNAPSHOT_PATH).read_text(encoding="utf-8"))


def validate_snapshot_metadata(root: Path) -> list[str]:
    errors: list[str] = []
    packet = load_snapshot(root)

    if packet.get("lane_key") != "P12-Y04":
        errors.append("invalid snapshot lane key")
    if packet.get("phase") != "Phase 12":
        errors.append("invalid snapshot phase")
    if packet.get("snapshot_scope") != "parked Phase 12 libbpf note packet on current master":
        errors.append("invalid snapshot scope")

    supporting_notes = packet.get("supporting_notes")
    if supporting_notes != EXPECTED_SUPPORTING_NOTES:
        errors.append("invalid supporting note list")

    if packet.get("parked_absent_boundaries") != PARKED_ABSENT_BOUNDARIES:
        errors.append("invalid parked absent boundary list")

    files = packet.get("files")
    if not isinstance(files, list):
        errors.append("invalid file packet")
        return errors

    tracked_count = packet.get("tracked_file_count")
    if tracked_count != len(EXPECTED_SUPPORTING_NOTES):
        errors.append("invalid tracked file count")
    if len(files) != len(EXPECTED_SUPPORTING_NOTES):
        errors.append("invalid tracked file list length")

    file_paths = [entry.get("path") for entry in files if isinstance(entry, dict)]
    if file_paths != EXPECTED_SUPPORTING_NOTES:
        errors.append("invalid tracked file path order")

    for entry in files:
        if not isinstance(entry, dict):
            errors.append("invalid tracked file packet entry")
            continue
        sha = entry.get("blob_sha")
        if not isinstance(sha, str) or len(sha) != 40 or any(c not in "0123456789abcdef" for c in sha):
            errors.append(f"invalid blob sha for {entry.get('path', '<unknown>')}")
    return errors


def collect_missing_files(root: Path) -> list[str]:
    required = [SNAPSHOT_PATH, *EXPECTED_SUPPORTING_NOTES, *PRESENT_HELPER_FILES]
    return [rel for rel in required if not (root / rel).exists()]


def collect_unexpected_files(root: Path) -> list[str]:
    return [rel for rel in PARKED_ABSENT_BOUNDARIES if (root / rel).exists()]


def collect_drift_markers(root: Path) -> list[str]:
    drift: list[str] = []
    for rel, markers in REQUIRED_MARKERS.items():
        text = (root / rel).read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                drift.append(f"{rel}: {marker}")

    packet = load_snapshot(root)
    survey_text = (root / SURVEY_PATH).read_text(encoding="utf-8")
    for entry in packet["files"]:
        rel = entry["path"]
        current_sha = git_blob_sha(root / rel)
        if current_sha == entry["blob_sha"]:
            continue
        if rel == COORDINATION_PATH and "parked reviewability packet visible" in survey_text:
            continue
        drift.append(f"{SNAPSHOT_PATH}: blob sha drift for {rel}")
    return drift


def validate(root: Path) -> tuple[list[str], list[str], list[str]]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return missing_files, [], []

    metadata_errors = validate_snapshot_metadata(root)
    marker_errors = collect_drift_markers(root)
    if metadata_errors or marker_errors:
        return [], metadata_errors + marker_errors, []

    unexpected_files = collect_unexpected_files(root)
    return [], [], unexpected_files


FIXTURE_TEXT = {
    SURVEY_PATH: "\n".join(REQUIRED_MARKERS[SURVEY_PATH]) + "\n",
    VERIFY_PATH: "\n".join(REQUIRED_MARKERS[VERIFY_PATH]) + "\n",
    SEQUENCING_PATH: "\n".join(REQUIRED_MARKERS[SEQUENCING_PATH]) + "\n",
    COORDINATION_PATH: "\n".join(REQUIRED_MARKERS[COORDINATION_PATH]) + "\n",
    MANIFEST_PATH: "\n".join(REQUIRED_MARKERS[MANIFEST_PATH]) + "\n",
}


def write_fixture_root(tmp_root: Path) -> None:
    packet = {
        "lane_key": "P12-Y04",
        "phase": "Phase 12",
        "surveyed_commit": "e6b1a0e361fe11926c1e788fc93da66e92db9669",
        "snapshot_scope": "parked Phase 12 libbpf note packet on current master",
        "tracked_file_count": 4,
        "supporting_notes": EXPECTED_SUPPORTING_NOTES,
        "parked_absent_boundaries": PARKED_ABSENT_BOUNDARIES,
        "files": [],
    }

    for rel, text in FIXTURE_TEXT.items():
        path = tmp_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    for rel in PRESENT_HELPER_FILES:
        if rel in FIXTURE_TEXT:
            continue
        path = tmp_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("// fixture\n", encoding="utf-8")

    for rel in EXPECTED_SUPPORTING_NOTES:
        packet["files"].append({"path": rel, "blob_sha": git_blob_sha(tmp_root / rel)})

    snapshot_path = tmp_root / SNAPSHOT_PATH
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    snapshot_path.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")


def expect_marker_error(case: str, tmp_root: Path, expected: str) -> None:
    missing_files, marker_errors, unexpected_files = validate(tmp_root)
    assert missing_files == [], case
    assert unexpected_files == [], case
    assert expected in marker_errors, case


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase12_libbpf_snapshot_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        write_fixture_root(tmp_root)
        assert validate(tmp_root) == ([], [], [])

        (tmp_root / SNAPSHOT_PATH).unlink()
        missing_files, marker_errors, unexpected_files = validate(tmp_root)
        assert missing_files == [SNAPSHOT_PATH]
        assert marker_errors == []
        assert unexpected_files == []
        write_fixture_root(tmp_root)

        packet = load_snapshot(tmp_root)
        packet["tracked_file_count"] = 3
        (tmp_root / SNAPSHOT_PATH).write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
        expect_marker_error("invalid_tracked_file_count", tmp_root, "invalid tracked file count")
        write_fixture_root(tmp_root)

        text = (tmp_root / VERIFY_PATH).read_text(encoding="utf-8") + "\n"
        (tmp_root / VERIFY_PATH).write_text(text, encoding="utf-8")
        expect_marker_error(
            "verify_blob_sha_drift",
            tmp_root,
            f"{SNAPSHOT_PATH}: blob sha drift for {VERIFY_PATH}",
        )
        write_fixture_root(tmp_root)

        text = (tmp_root / SURVEY_PATH).read_text(encoding="utf-8").replace(
            "parked reviewability packet visible",
            "reviewability packet visible",
            1,
        )
        (tmp_root / SURVEY_PATH).write_text(text, encoding="utf-8")
        expect_marker_error(
            "missing_survey_snapshot_marker",
            tmp_root,
            f"{SURVEY_PATH}: parked reviewability packet visible",
        )
        write_fixture_root(tmp_root)

        text = (tmp_root / SURVEY_PATH).read_text(encoding="utf-8").replace(
            f"`{CHECKER_PATH}`",
            "`scripts/zigux/check-phase12-libbpf-snapshot-missing.py`",
            1,
        )
        (tmp_root / SURVEY_PATH).write_text(text, encoding="utf-8")
        expect_marker_error(
            "missing_survey_checker_marker",
            tmp_root,
            f"{SURVEY_PATH}: `{CHECKER_PATH}`",
        )
        write_fixture_root(tmp_root)

        text = (tmp_root / SEQUENCING_PATH).read_text(encoding="utf-8").replace(
            f"`{CHECKER_PATH}`",
            "`scripts/zigux/check-phase12-libbpf-snapshot-missing.py`",
            1,
        )
        (tmp_root / SEQUENCING_PATH).write_text(text, encoding="utf-8")
        expect_marker_error(
            "missing_sequencing_checker_marker",
            tmp_root,
            f"{SEQUENCING_PATH}: `{CHECKER_PATH}`",
        )
        write_fixture_root(tmp_root)

        text = (tmp_root / COORDINATION_PATH).read_text(encoding="utf-8").replace(
            "tools/lib/bpf/zigux_segments/manifest.json",
            "tools/lib/bpf/zigux_segments/manifest_missing.json",
            1,
        )
        (tmp_root / COORDINATION_PATH).write_text(text, encoding="utf-8")
        expect_marker_error(
            "missing_coordination_manifest_marker",
            tmp_root,
            f"{COORDINATION_PATH}: tools/lib/bpf/zigux_segments/manifest.json",
        )
        write_fixture_root(tmp_root)

        text = (tmp_root / MANIFEST_PATH).read_text(encoding="utf-8").replace(
            "\"zigux_destination\": \"tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig\"",
            "\"zigux_destination\": \"tools/lib/bpf/zigux_segments/file_path_handle_bridge_missing.zig\"",
            1,
        )
        (tmp_root / MANIFEST_PATH).write_text(text, encoding="utf-8")
        expect_marker_error(
            "missing_manifest_file_path_handle_bridge_marker",
            tmp_root,
            f"{MANIFEST_PATH}: \"zigux_destination\": \"tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig\"",
        )
        write_fixture_root(tmp_root)

        (tmp_root / "tools/lib/bpf/zigux_segments/verify.zig").parent.mkdir(parents=True, exist_ok=True)
        (tmp_root / "tools/lib/bpf/zigux_segments/verify.zig").write_text("// unexpected\n", encoding="utf-8")
        missing_files, marker_errors, unexpected_files = validate(tmp_root)
        assert missing_files == []
        assert marker_errors == []
        assert unexpected_files == ["tools/lib/bpf/zigux_segments/verify.zig"]
        write_fixture_root(tmp_root)

        (tmp_root / "tools/lib/bpf/zigux_segments/logging.zig").unlink()
        missing_files, marker_errors, unexpected_files = validate(tmp_root)
        assert missing_files == ["tools/lib/bpf/zigux_segments/logging.zig"]
        assert marker_errors == []
        assert unexpected_files == []

    print("PHASE12_LIBBPF_SNAPSHOT_SELF_TEST=pass")
    print("PHASE12_LIBBPF_SNAPSHOT_SELF_TEST_CASE_COUNT=10")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the Phase 12 libbpf historical snapshot packet, its note owners, the "
            "legacy helper catalog boundary, and the present-versus-parked helper split."
        )
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run synthetic snapshot packet self-tests.",
    )
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    missing_files, marker_errors, unexpected_files = validate(ROOT)
    if missing_files:
        print("PHASE12_LIBBPF_SNAPSHOT_CHECK=fail")
        print("MISSING_PHASE12_LIBBPF_SNAPSHOT_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE12_LIBBPF_SNAPSHOT_FILES_END")
        return 1

    if marker_errors:
        print("PHASE12_LIBBPF_SNAPSHOT_CHECK=fail")
        print("PHASE12_LIBBPF_SNAPSHOT_MARKER_ERRORS_START")
        for item in marker_errors:
            print(item)
        print("PHASE12_LIBBPF_SNAPSHOT_MARKER_ERRORS_END")
        return 1

    if unexpected_files:
        print("PHASE12_LIBBPF_SNAPSHOT_CHECK=fail")
        print("UNEXPECTED_PHASE12_LIBBPF_SNAPSHOT_FILES_START")
        for item in unexpected_files:
            print(item)
        print("UNEXPECTED_PHASE12_LIBBPF_SNAPSHOT_FILES_END")
        return 1

    print("PHASE12_LIBBPF_SNAPSHOT_CHECK=pass")
    print(f"PHASE12_LIBBPF_SNAPSHOT_TRACKED_FILE_COUNT={len(EXPECTED_SUPPORTING_NOTES)}")
    print(f"PHASE12_LIBBPF_SNAPSHOT_PRESENT_HELPER_COUNT={len(PRESENT_HELPER_FILES)}")
    print(f"PHASE12_LIBBPF_SNAPSHOT_PARKED_ABSENT_COUNT={len(PARKED_ABSENT_BOUNDARIES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())