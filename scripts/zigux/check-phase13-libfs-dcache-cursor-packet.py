#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()

DOC_PATH = "Documentation/zigux/phase13-libfs-dcache-cursor-planner.md"
HELPER_PATH = "fs/libfs_dcache_cursor.zig"
REPLAY_PATH = "zigux/tests/phase13_libfs_dcache_cursor.zig"
MANIFEST_PATH = "zigux/tests/phase13_libfs_dcache_cursor_manifest.json"

EXPECTED_GAPS = {
    "phase13-libfs-dcache-dir-open-precondition-planner": "starter_landed",
    "phase13-libfs-dcache-readdir-precondition-planner": "starter_landed",
    "phase13-libfs-dcache-cursor-review-packet": "starter_landed",
    "phase13-build-gate": "missing_on_current_master",
    "phase13-libfs-live-cursor-traversal": "blocked_on_dcache_state",
}

DOC_MARKERS = [
    "`fs/libfs.c`",
    "`fs/libfs_dcache_cursor.zig`",
    "`zigux/tests/phase13_libfs_dcache_cursor.zig`",
    "`zigux/tests/phase13_libfs_dcache_cursor_manifest.json`",
    "`scripts/zigux/check-phase13-libfs-dcache-cursor-packet.py`",
    "`dcache_dir_open()`",
    "`dcache_readdir()`",
    "shared Phase 13 build route",
    "`dcache_dir_close()` cursor release planner",
]

HELPER_MARKERS = [
    "pub const DcacheCursorPacketDescriptor",
    ".provides_dcache_dir_open_planning = true",
    ".provides_dcache_readdir_preconditions = true",
    ".claims_live_cursor_dentry_traversal = false",
    "pub fn planDcacheDirOpen(",
    "pub fn planDcacheReaddir(",
    "ready_at_end_of_directory",
    "missing_private_cursor",
]

REPLAY_MARKERS = [
    "dcache dir open planner keeps cursor private and skips sibling mutation claims",
    "dcache readdir planner stays on preconditions and end-of-directory gating",
    "missing_private_cursor",
    "ready_at_end_of_directory",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def require_file(root: Path, rel: str, errors: list[str]) -> Path | None:
    path = root / rel
    if not path.is_file():
        errors.append(f"missing:{rel}")
        return None
    return path


def require_markers(source: str, prefix: str, markers: list[str], errors: list[str]) -> None:
    for marker in markers:
        if marker not in source:
            errors.append(f"{prefix}:missing_marker:{marker}")


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    doc_path = require_file(root, DOC_PATH, errors)
    helper_path = require_file(root, HELPER_PATH, errors)
    replay_path = require_file(root, REPLAY_PATH, errors)
    manifest_path = require_file(root, MANIFEST_PATH, errors)
    if errors:
        return errors

    doc_text = read_text(doc_path)
    helper_text = read_text(helper_path)
    replay_text = read_text(replay_path)

    try:
        manifest = json.loads(read_text(manifest_path))
    except json.JSONDecodeError as exc:
        return [f"manifest:json_decode:{exc.msg}"]

    gaps = manifest.get("gaps")
    if not isinstance(gaps, list):
        errors.append("manifest:gaps_missing")
        gaps = []
    seen = {gap.get("id"): gap.get("status") for gap in gaps if isinstance(gap, dict)}
    if len(seen) != len(EXPECTED_GAPS):
        errors.append(f"manifest:gaps_count_mismatch:{len(seen)}")
    for gap_id, status in EXPECTED_GAPS.items():
        if seen.get(gap_id) != status:
            errors.append(f"manifest:gap_status_mismatch:{gap_id}:{seen.get(gap_id)}")

    require_markers(doc_text, "doc", DOC_MARKERS, errors)
    require_markers(helper_text, "helper", HELPER_MARKERS, errors)
    require_markers(replay_text, "replay", REPLAY_MARKERS, errors)
    return errors


def seed_fixture_tree(root: Path) -> None:
    write_text(root / DOC_PATH, "\n".join(DOC_MARKERS) + "\n")
    write_text(root / HELPER_PATH, "\n".join(HELPER_MARKERS) + "\n")
    write_text(root / REPLAY_PATH, "\n".join(REPLAY_MARKERS) + "\n")
    manifest = {
        "gaps": [{"id": gap_id, "status": status} for gap_id, status in EXPECTED_GAPS.items()],
    }
    write_text(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")


def assert_only(actual: list[str], expected: list[str], label: str) -> None:
    if actual != expected:
        raise SystemExit(f"{label}:expected={expected}:actual={actual}")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase13_libfs_dcache_cursor_") as temp_dir:
        root = Path(temp_dir)

        seed_fixture_tree(root)
        assert_only(validate(root), [], "baseline_failed")
        case_count += 1

        seed_fixture_tree(root)
        (root / HELPER_PATH).unlink()
        assert_only(validate(root), [f"missing:{HELPER_PATH}"], "missing_helper_failed")
        case_count += 1

        seed_fixture_tree(root)
        manifest = json.loads(read_text(root / MANIFEST_PATH))
        manifest["gaps"] = manifest["gaps"][:-1]
        write_text(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        assert_only(
            validate(root),
            [
                "manifest:gaps_count_mismatch:4",
                "manifest:gap_status_mismatch:phase13-libfs-live-cursor-traversal:None",
            ],
            "manifest_gap_count_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(root / DOC_PATH, "broken\n")
        expected = [f"doc:missing_marker:{marker}" for marker in DOC_MARKERS]
        assert_only(validate(root), expected, "doc_marker_failed")
        case_count += 1

    print("PHASE13_LIBFS_DCACHE_CURSOR_PACKET_SELF_TEST=pass")
    print(f"PHASE13_LIBFS_DCACHE_CURSOR_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 13 libfs dcache cursor packet stays aligned with its helper, replay, manifest, and note."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    parser.add_argument("--self-test", action="store_true", help="Run checker self-tests.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = validate(args.root)
    if errors:
        for error in errors:
            print(error)
        return 1

    print("PHASE13_LIBFS_DCACHE_CURSOR_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
