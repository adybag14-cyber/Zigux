#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[0]

MANIFEST_PATH = "tools/lib/bpf/zigux_segments/manifest.json"
BRIDGE_SLICE_PATH = "Documentation/zigux/phase8-file-path-handle-bridge-slice.md"
BRIDGE_HELPER_PATH = "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig"
FOCUSED_BUILD_PATH = "zigux/tests/phase8_file_path_handle_bridge_only_build.zig"
SHARED_BUILD_PATH = "zigux/tests/phase8_build.zig"

REQUIRED_FILES = [
    MANIFEST_PATH,
    BRIDGE_SLICE_PATH,
    BRIDGE_HELPER_PATH,
    FOCUSED_BUILD_PATH,
    SHARED_BUILD_PATH,
]

REQUIRED_MARKERS = {
    MANIFEST_PATH: [
        '"id": "P8-L15-S05"',
        '"slug": "fdinfo-map-info-helpers"',
        '"id": "P8-L15-S06"',
        '"slug": "map-reuse-compatibility"',
        '"id": "P8-L15-S07"',
        '"slug": "file-path-and-handle-bridge"',
        '"kind": "resource_boundary"',
        '"status": "deferred_high_risk"',
        '"zigux_destination": "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig"',
    ],
    BRIDGE_SLICE_PATH: [
        "PHASE8_SLICE=libbpf-file-path-handle-bridge",
        '"/proc/%d/fdinfo/%d"',
        "map_extra",
        "mapReuseObservationFromFdinfo()",
        "resolveReusePinnedMapAttempt()",
        "planTokenPreparation()",
        "make -C zigux phase8-file-path-handle-bridge-test",
        "zig build test --build-file zigux/tests/phase8_file_path_handle_bridge_only_build.zig --summary all",
        "make -C zigux phase8-test",
        "no direct procfs reads",
        "no `bpf_obj_get()` reopen flow",
    ],
    BRIDGE_HELPER_PATH: [
        "pub fn buildProcFdinfoPath",
        "pub fn parseFdinfoMapInfo",
        "pub fn summarizeFdinfoMapInfo",
        "pub fn mapReuseObservationFromFdinfo",
        "pub fn summarizeMapReuseCompatibility",
        "pub fn resolveReusePinnedMapAttempt",
        "pub fn planTokenPreparation",
        "map_extra",
        "ready_for_reopen_attempt",
        "ready_for_token_open_attempt",
    ],
    FOCUSED_BUILD_PATH: [
        "../../tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
        "phase8_file_path_handle_bridge.zig",
        "phase8-file-path-handle-bridge-tests",
    ],
    SHARED_BUILD_PATH: [
        "../../tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
        "phase8_file_path_handle_bridge.zig",
        "phase8-file-path-handle-bridge-tests",
    ],
}


def collect_missing_files(root: Path) -> list[str]:
    return [rel for rel in REQUIRED_FILES if not (root / rel).exists()]


def collect_missing_markers(root: Path) -> list[str]:
    missing: list[str] = []
    for rel, markers in REQUIRED_MARKERS.items():
        text = (root / rel).read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                missing.append(f"{rel}: {marker}")
    return missing


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return missing_files, []
    return [], collect_missing_markers(root)


def write_fixture_root(tmp_root: Path) -> None:
    for rel, markers in REQUIRED_MARKERS.items():
        path = tmp_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(markers) + "\n", encoding="utf-8")


def expect_missing_file(case: str, tmp_root: Path, rel: str) -> None:
    missing_files, missing_markers = validate(tmp_root)
    assert missing_markers == [], case
    assert missing_files == [rel], case


def expect_missing_marker(case: str, tmp_root: Path, marker: str) -> None:
    missing_files, missing_markers = validate(tmp_root)
    assert missing_files == [], case
    assert missing_markers == [marker], case


def mutate_file(tmp_root: Path, rel: str, old: str, new: str, case: str) -> None:
    path = tmp_root / rel
    original = path.read_text(encoding="utf-8")
    updated = original.replace(old, new, 1)
    assert updated != original, case
    path.write_text(updated, encoding="utf-8")


def run_self_test() -> None:
    missing_file_cases = [
        ("missing_manifest", MANIFEST_PATH),
        ("missing_bridge_slice", BRIDGE_SLICE_PATH),
        ("missing_bridge_helper", BRIDGE_HELPER_PATH),
        ("missing_focused_build", FOCUSED_BUILD_PATH),
        ("missing_shared_build", SHARED_BUILD_PATH),
    ]
    marker_cases = [
        (
            "manifest_fdinfo_slug",
            MANIFEST_PATH,
            '"slug": "fdinfo-map-info-helpers"',
            '"slug": "fdinfo-map-fields"',
            f'{MANIFEST_PATH}: "slug": "fdinfo-map-info-helpers"',
        ),
        (
            "manifest_resource_boundary_kind",
            MANIFEST_PATH,
            '"kind": "resource_boundary"',
            '"kind": "helper_first"',
            f'{MANIFEST_PATH}: "kind": "resource_boundary"',
        ),
        (
            "bridge_slice_gate_route",
            BRIDGE_SLICE_PATH,
            "make -C zigux phase8-file-path-handle-bridge-test",
            "make -C zigux phase8-file-path-handle-test",
            f"{BRIDGE_SLICE_PATH}: make -C zigux phase8-file-path-handle-bridge-test",
        ),
        (
            "bridge_slice_reopen_marker",
            BRIDGE_SLICE_PATH,
            "no `bpf_obj_get()` reopen flow",
            "no reopen flow",
            f"{BRIDGE_SLICE_PATH}: no `bpf_obj_get()` reopen flow",
        ),
        (
            "bridge_helper_token_planning",
            BRIDGE_HELPER_PATH,
            "pub fn planTokenPreparation",
            "fn planTokenPreparation",
            f"{BRIDGE_HELPER_PATH}: pub fn planTokenPreparation",
        ),
        (
            "bridge_helper_token_disposition",
            BRIDGE_HELPER_PATH,
            "ready_for_token_open_attempt",
            "ready_for_token_open",
            f"{BRIDGE_HELPER_PATH}: ready_for_token_open_attempt",
        ),
        (
            "focused_build_route",
            FOCUSED_BUILD_PATH,
            "phase8-file-path-handle-bridge-tests",
            "phase8-file-path-handle-tests",
            f"{FOCUSED_BUILD_PATH}: phase8-file-path-handle-bridge-tests",
        ),
        (
            "shared_build_route",
            SHARED_BUILD_PATH,
            "phase8-file-path-handle-bridge-tests",
            "phase8-file-path-handle-tests",
            f"{SHARED_BUILD_PATH}: phase8-file-path-handle-bridge-tests",
        ),
    ]

    with tempfile.TemporaryDirectory(prefix="zigux_phase8_file_path_bridge_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        write_fixture_root(tmp_root)
        assert validate(tmp_root) == ([], [])

        for case, rel in missing_file_cases:
            (tmp_root / rel).unlink()
            expect_missing_file(case, tmp_root, rel)
            write_fixture_root(tmp_root)

        for case, rel, old, new, expected in marker_cases:
            mutate_file(tmp_root, rel, old, new, case)
            expect_missing_marker(case, tmp_root, expected)
            write_fixture_root(tmp_root)

    case_count = len(missing_file_cases) + len(marker_cases)
    print("PHASE8_FILE_PATH_HANDLE_BRIDGE_PACKET_SELF_TEST=pass")
    print(f"PHASE8_FILE_PATH_HANDLE_BRIDGE_PACKET_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 8 file-path handle bridge packet."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run checker self-test cases without reading repo files.",
    )
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    missing_files, missing_markers = validate(ROOT)
    if missing_files:
        print("PHASE8_FILE_PATH_HANDLE_BRIDGE_PACKET=fail")
        print("MISSING_PHASE8_FILE_PATH_HANDLE_BRIDGE_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE8_FILE_PATH_HANDLE_BRIDGE_FILES_END")
        return 1

    if missing_markers:
        print("PHASE8_FILE_PATH_HANDLE_BRIDGE_PACKET=fail")
        print("MISSING_PHASE8_FILE_PATH_HANDLE_BRIDGE_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE8_FILE_PATH_HANDLE_BRIDGE_MARKERS_END")
        return 1

    print("PHASE8_FILE_PATH_HANDLE_BRIDGE_PACKET=pass")
    print(f"PHASE8_FILE_PATH_HANDLE_BRIDGE_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE8_FILE_PATH_HANDLE_BRIDGE_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
