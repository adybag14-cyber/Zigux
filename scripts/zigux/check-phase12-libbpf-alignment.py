#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parent.parent.parent

MANIFEST_PATH = Path("zigux/tests/phase12_libbpf_manifest.json")
SNAPSHOT_PATH = Path("zigux/tests/fixtures/phase12_libbpf_snapshot.json")
REVIEWABILITY_PATH = Path("zigux/tests/phase12_libbpf_reviewability.zig")
SURVEY_PATH = Path("Documentation/zigux/phase12-libbpf-segment-survey.md")
LEGACY_MANIFEST_PATH = Path("tools/lib/bpf/zigux_segments/manifest.json")

EXPECTED_TRACKED_PATHS = [
    str(MANIFEST_PATH),
    "zigux/tests/phase12_libbpf_segments.zig",
    str(REVIEWABILITY_PATH),
    str(SURVEY_PATH),
    str(LEGACY_MANIFEST_PATH),
]

REQUIRED_GAP_IDS = [
    "phase12-libbpf-segment-manifest-foundation",
    "phase12-libbpf-type-name-helper-foundation",
    "phase12-libbpf-cpu-mask-helper-foundation",
    "phase12-libbpf-logging-helper-foundation",
    "phase12-libbpf-pin-path-helper-foundation",
    "phase12-libbpf-file-path-handle-helper-foundation",
    "phase12-libbpf-map-reuse-compatibility-helper-foundation",
    "phase12-libbpf-file-path-and-handle-bridge-boundary",
    "phase12-libbpf-perf-buffer-online-cpu-routing-boundary",
    "phase12-libbpf-skeleton-population",
    "phase12-libbpf-object-and-elf-loader",
    "phase12-libbpf-btf-relocation-and-program-load",
]

STALE_GAP_IDS = [
    "phase12-libbpf-fdinfo-map-info-helper-ready-next",
    "phase12-libbpf-map-reuse-compatibility-ready-next",
    "phase12-libbpf-file-path-and-handle-bridge",
    "phase12-libbpf-perf-buffer-online-cpu-routing",
    "phase12-libbpf-object-loader-and-program-load",
]


def gap_marker(gap_id: str) -> str:
    return f'"{gap_id}"'


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def check_alignment(root: Path) -> list[str]:
    missing: list[str] = []
    manifest = load_json(root / MANIFEST_PATH)
    snapshot = load_json(root / SNAPSHOT_PATH)
    reviewability_text = (root / REVIEWABILITY_PATH).read_text(encoding="utf-8")

    if manifest.get("lane_key") != "P12-L16":
        missing.append("manifest:lane_key")
    if manifest.get("phase") != "Phase 12":
        missing.append("manifest:phase")

    if snapshot.get("lane_key") != manifest.get("lane_key"):
        missing.append("snapshot:lane_key")
    if snapshot.get("phase") != manifest.get("phase"):
        missing.append("snapshot:phase")
    if snapshot.get("surveyed_commit") != manifest.get("surveyed_commit"):
        missing.append("snapshot:surveyed_commit")

    files = snapshot.get("files")
    if not isinstance(files, list):
        missing.append("snapshot:files")
    else:
        if snapshot.get("tracked_file_count") != len(EXPECTED_TRACKED_PATHS):
            missing.append("snapshot:tracked_file_count")
        if len(files) != len(EXPECTED_TRACKED_PATHS):
            missing.append("snapshot:file_count")
        for index, expected_path in enumerate(EXPECTED_TRACKED_PATHS):
            if index >= len(files):
                break
            entry = files[index]
            if not isinstance(entry, dict):
                missing.append(f"snapshot:file:{index}:shape")
                continue
            if entry.get("path") != expected_path:
                missing.append(f"snapshot:file:{index}:path")
            sha256 = entry.get("sha256")
            if not isinstance(sha256, str) or len(sha256) != 64:
                missing.append(f"snapshot:file:{index}:sha256")

    manifest_gaps = manifest.get("gaps")
    if not isinstance(manifest_gaps, list):
        missing.append("manifest:gaps")
        manifest_gap_ids: set[str] = set()
    else:
        manifest_gap_ids = {
            gap.get("id")
            for gap in manifest_gaps
            if isinstance(gap, dict) and isinstance(gap.get("id"), str)
        }

    for gap_id in REQUIRED_GAP_IDS:
        if gap_id not in manifest_gap_ids:
            missing.append(f"manifest_gap:{gap_id}")
        if gap_marker(gap_id) not in reviewability_text:
            missing.append(f"reviewability_gap:{gap_id}")

    for gap_id in STALE_GAP_IDS:
        if gap_marker(gap_id) in reviewability_text:
            missing.append(f"reviewability_stale_gap:{gap_id}")

    return missing


def build_fixture_tree(root: Path) -> None:
    (root / MANIFEST_PATH.parent).mkdir(parents=True, exist_ok=True)
    (root / SNAPSHOT_PATH.parent).mkdir(parents=True, exist_ok=True)
    (root / REVIEWABILITY_PATH.parent).mkdir(parents=True, exist_ok=True)
    (root / SURVEY_PATH.parent).mkdir(parents=True, exist_ok=True)
    (root / LEGACY_MANIFEST_PATH.parent).mkdir(parents=True, exist_ok=True)

    manifest = {
        "lane_key": "P12-L16",
        "phase": "Phase 12",
        "surveyed_commit": "deadbeef" * 5,
        "gaps": [{"id": gap_id} for gap_id in REQUIRED_GAP_IDS],
    }
    snapshot = {
        "lane_key": "P12-L16",
        "phase": "Phase 12",
        "surveyed_commit": "deadbeef" * 5,
        "tracked_file_count": len(EXPECTED_TRACKED_PATHS),
        "files": [
            {"path": path, "bytes": 1, "sha256": "a" * 64}
            for path in EXPECTED_TRACKED_PATHS
        ],
    }
    reviewability = "\n".join(gap_marker(gap_id) for gap_id in REQUIRED_GAP_IDS) + "\n"

    (root / MANIFEST_PATH).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (root / SNAPSHOT_PATH).write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
    (root / REVIEWABILITY_PATH).write_text(reviewability, encoding="utf-8")
    (root / SURVEY_PATH).write_text("# fixture\n", encoding="utf-8")
    (root / LEGACY_MANIFEST_PATH).write_text("{\"segments\": []}\n", encoding="utf-8")


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    updated = text.replace(old, new, 1)
    if updated == text:
        raise SystemExit(f"failed to mutate fixture: {path}:{old}")
    path.write_text(updated, encoding="utf-8")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase12_libbpf_alignment_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        build_fixture_tree(tmp_root)

        if check_alignment(tmp_root) != []:
            raise SystemExit("phase12-libbpf-alignment:self-test:clean_fixture")

        replace_once(tmp_root / MANIFEST_PATH, '"lane_key": "P12-L16"', '"lane_key": "P12-L99"')
        if check_alignment(tmp_root) != ["manifest:lane_key", "snapshot:lane_key"]:
            raise SystemExit("phase12-libbpf-alignment:self-test:lane_key_detection")
        build_fixture_tree(tmp_root)

        replace_once(
            tmp_root / SNAPSHOT_PATH,
            '"path": "zigux/tests/phase12_libbpf_reviewability.zig"',
            '"path": "zigux/tests/phase12_libbpf_reviewability_old.zig"',
        )
        if "snapshot:file:2:path" not in check_alignment(tmp_root):
            raise SystemExit("phase12-libbpf-alignment:self-test:snapshot_path_detection")
        build_fixture_tree(tmp_root)

        replace_once(
            tmp_root / REVIEWABILITY_PATH,
            gap_marker("phase12-libbpf-map-reuse-compatibility-helper-foundation"),
            gap_marker("phase12-libbpf-map-reuse-compatibility-ready-next"),
        )
        missing = check_alignment(tmp_root)
        if "reviewability_gap:phase12-libbpf-map-reuse-compatibility-helper-foundation" not in missing:
            raise SystemExit("phase12-libbpf-alignment:self-test:required_gap_detection")
        if "reviewability_stale_gap:phase12-libbpf-map-reuse-compatibility-ready-next" not in missing:
            raise SystemExit("phase12-libbpf-alignment:self-test:stale_gap_detection")

    print("PHASE12_LIBBPF_ALIGNMENT_SELF_TEST=pass")
    print("PHASE12_LIBBPF_ALIGNMENT_SELF_TEST_CASE_COUNT=3")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed on Phase 12 libbpf snapshot and reviewability alignment drift."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker self-tests.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    missing = check_alignment(args.root)
    if missing:
        print("PHASE12_LIBBPF_ALIGNMENT=fail")
        print("PHASE12_LIBBPF_ALIGNMENT_MISSING_START")
        for item in missing:
            print(item)
        print("PHASE12_LIBBPF_ALIGNMENT_MISSING_END")
        return 1

    print("PHASE12_LIBBPF_ALIGNMENT=pass")
    print(f"PHASE12_LIBBPF_ALIGNMENT_REQUIRED_GAP_COUNT={len(REQUIRED_GAP_IDS)}")
    print(f"PHASE12_LIBBPF_ALIGNMENT_STALE_GAP_COUNT={len(STALE_GAP_IDS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
