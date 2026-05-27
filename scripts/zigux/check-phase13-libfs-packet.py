#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()

MANIFEST_PATH = "zigux/tests/phase13_libfs_manifest.json"
SURVEY_PATH = "Documentation/zigux/phase13-libfs-survey.md"
HELPER_PATH = "fs/libfs.zig"
REPLAY_PATH = "zigux/tests/phase13_libfs.zig"
REVIEWABILITY_PATH = "zigux/tests/phase13_libfs_reviewability.zig"

FIXTURE_LANE = "P13-Y01"
FIXTURE_COMMIT = "master-readback-2026-05-27"
EXPECTED_GAP_COUNT = 15
EXPECTED_STARTER_COUNT = 11
EXPECTED_BLOCKED_COUNT = 4

EXPECTED_GAPS = {
    "phase13-libfs-helper-starter": "starter_landed",
    "phase13-libfs-offset-add-planner": "starter_landed",
    "phase13-libfs-offset-remove-planner": "starter_landed",
    "phase13-libfs-offset-rename-planner": "starter_landed",
    "phase13-libfs-transaction-acquire-helper": "starter_landed",
    "phase13-libfs-transaction-release-helper": "starter_landed",
    "phase13-libfs-transaction-publish-helper": "starter_landed",
    "phase13-libfs-addressability-helper": "starter_landed",
    "phase13-libfs-reviewability-gate": "starter_landed",
    "phase13-libfs-survey-note": "starter_landed",
    "phase13-libfs-dcache-cursor-precondition-planner": "starter_landed",
    "phase13-build-gate": "blocked_on_shared_build_surface",
    "phase13-libfs-live-dcache-mutation": "blocked_on_dcache_state",
    "phase13-libfs-live-inode-state": "blocked_on_inode_state",
    "phase13-libfs-live-cursor-traversal": "blocked_on_dcache_state",
}

SURVEY_STATIC_MARKERS = [
    "`PHASE13_SLICE=libfs-helper-filesystem-boundary-survey`",
    "`fs/libfs.zig`",
    "`fs/libfs_dcache_cursor.zig`",
    "`zigux/tests/phase13_libfs.zig`",
    "`zigux/tests/phase13_libfs_reviewability.zig`",
    "`zigux/tests/phase13_libfs_dcache_cursor.zig`",
    "`zigux/tests/phase13_libfs_manifest.json`",
    "`zigux/tests/phase13_libfs_dcache_cursor_manifest.json`",
    "`Documentation/zigux/phase13-libfs-dcache-cursor-planner.md`",
    "`scripts/zigux/check-phase13-libfs-packet.py`",
    "`scripts/zigux/check-phase13-libfs-dcache-cursor-packet.py`",
    "simple_offset_add()",
    "simple_offset_remove()",
    "simple_transaction_get()",
    "simple_transaction_set()",
    "simple_transaction_release()",
    "generic_check_addressable()",
    "offset-based rename plus rename-exchange planning",
    "`dcache_dir_open()` and `dcache_readdir()` cursor preconditions reviewable",
    "shared `zigux/tests/phase13_build.zig` route",
]

HELPER_MARKERS = [
    ".provides_offset_add_planning = true",
    ".provides_offset_remove_planning = true",
    ".provides_offset_readdir_planning = true",
    ".provides_transaction_release_planning = true",
    ".provides_directory_scan_resched_planning = true",
    "pub const TransactionReleasePlan",
    "pub fn simpleTransactionReleasePlan(",
    "pub fn planSimpleOffsetAdd(",
    "pub fn planSimpleOffsetRemove(",
    "pub fn planSimpleOffsetRename(",
    "pub fn planSimpleOffsetRenameExchange(",
    "pub fn genericCheckAddressablePlan(",
    "pub fn planOffsetReaddir(",
]

REPLAY_STATIC_MARKERS = [
    "phase13 libfs manifest records the current helper-first filesystem packet",
    "\"phase13-libfs-offset-remove-planner\"",
    "\"phase13-libfs-offset-rename-planner\"",
    "\"phase13-libfs-transaction-release-helper\"",
    "\"phase13-libfs-addressability-helper\"",
    "simple_transaction_release()",
    "offset remove planning",
    "live dcache entry insertion",
]

REVIEWABILITY_MARKERS = [
    "descriptor keeps the current bounded helper surface explicit",
    "transaction release planner stays helper-only and unconditional-zero",
    "offset remove planning stays reviewable as erase-only lifecycle bookkeeping",
    "offset rename exchange planning keeps managed-slot swap and rollback expectations explicit",
    "addressability planner stays reviewable without implying live page-cache ownership",
]


def survey_markers(expected_commit: str, expected_lane: str) -> list[str]:
    return [
        expected_commit,
        *SURVEY_STATIC_MARKERS,
        f"helper-local governance for this family remains tracked under `{expected_lane}`",
    ]


def replay_markers(expected_lane: str) -> list[str]:
    return [
        *REPLAY_STATIC_MARKERS,
        f"\"lane_key\": \"{expected_lane}\"",
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
    manifest_path = require_file(root, MANIFEST_PATH, errors)
    survey_path = require_file(root, SURVEY_PATH, errors)
    helper_path = require_file(root, HELPER_PATH, errors)
    replay_path = require_file(root, REPLAY_PATH, errors)
    reviewability_path = require_file(root, REVIEWABILITY_PATH, errors)
    if errors:
        return errors

    manifest_text = read_text(manifest_path)
    survey_text = read_text(survey_path)
    helper_text = read_text(helper_path)
    replay_text = read_text(replay_path)
    reviewability_text = read_text(reviewability_path)

    try:
        manifest = json.loads(manifest_text)
    except json.JSONDecodeError as exc:
        return [f"manifest:json_decode:{exc.msg}"]

    lane_key = manifest.get("lane_key")
    if not isinstance(lane_key, str) or not lane_key:
        errors.append("manifest:lane_key_missing")
        lane_key = ""

    surveyed_commit = manifest.get("surveyed_commit")
    if not isinstance(surveyed_commit, str) or not surveyed_commit:
        errors.append("manifest:surveyed_commit_missing")
        surveyed_commit = ""

    gaps = manifest.get("gaps")
    if not isinstance(gaps, list):
        errors.append("manifest:gaps_missing")
        gaps = []
    if len(gaps) != EXPECTED_GAP_COUNT:
        errors.append(f"manifest:gaps_count_mismatch:{len(gaps)}")

    seen_gaps = {gap.get("id"): gap.get("status") for gap in gaps if isinstance(gap, dict)}
    for gap_id, status in EXPECTED_GAPS.items():
        if seen_gaps.get(gap_id) != status:
            errors.append(f"manifest:gap_status_mismatch:{gap_id}:{seen_gaps.get(gap_id)}")

    starter_count = sum(1 for value in seen_gaps.values() if value == "starter_landed")
    blocked_count = len(seen_gaps) - starter_count
    if starter_count != EXPECTED_STARTER_COUNT:
        errors.append(f"manifest:starter_count_mismatch:{starter_count}")
    if blocked_count != EXPECTED_BLOCKED_COUNT:
        errors.append(f"manifest:blocked_count_mismatch:{blocked_count}")

    if lane_key and surveyed_commit:
        require_markers(survey_text, "survey", survey_markers(surveyed_commit, lane_key), errors)
        require_markers(replay_text, "replay", replay_markers(lane_key), errors)
    require_markers(helper_text, "helper", HELPER_MARKERS, errors)
    require_markers(reviewability_text, "reviewability", REVIEWABILITY_MARKERS, errors)
    return errors


def render_manifest_fixture(lane_key: str = FIXTURE_LANE, surveyed_commit: str = FIXTURE_COMMIT) -> str:
    fixture = {
        "lane_key": lane_key,
        "surveyed_commit": surveyed_commit,
        "gaps": [{"id": gap_id, "status": status} for gap_id, status in EXPECTED_GAPS.items()],
    }
    return json.dumps(fixture, indent=2) + "\n"


def seed_fixture_tree(root: Path, lane_key: str = FIXTURE_LANE, surveyed_commit: str = FIXTURE_COMMIT) -> None:
    write_text(root / MANIFEST_PATH, render_manifest_fixture(lane_key, surveyed_commit))
    write_text(root / SURVEY_PATH, "\n".join(survey_markers(surveyed_commit, lane_key)) + "\n")
    write_text(root / HELPER_PATH, "\n".join(HELPER_MARKERS) + "\n")
    write_text(root / REPLAY_PATH, "\n".join(replay_markers(lane_key)) + "\n")
    write_text(root / REVIEWABILITY_PATH, "\n".join(REVIEWABILITY_MARKERS) + "\n")


def assert_only(actual: list[str], expected: list[str], label: str) -> None:
    if actual != expected:
        raise SystemExit(f"{label}:expected={expected}:actual={actual}")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase13_libfs_packet_") as temp_dir:
        root = Path(temp_dir)

        seed_fixture_tree(root)
        assert_only(validate(root), [], "baseline_failed")
        case_count += 1

        seed_fixture_tree(root)
        (root / REPLAY_PATH).unlink()
        assert_only(validate(root), [f"missing:{REPLAY_PATH}"], "missing_replay_failed")
        case_count += 1

        seed_fixture_tree(root)
        manifest = json.loads(read_text(root / MANIFEST_PATH))
        manifest["lane_key"] = "P13-L01"
        write_text(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        assert_only(
            validate(root),
            ['survey:missing_marker:helper-local governance for this family remains tracked under `P13-L01`', 'replay:missing_marker:"lane_key": "P13-L01"'],
            "manifest_lane_alignment_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        manifest = json.loads(read_text(root / MANIFEST_PATH))
        manifest["surveyed_commit"] = "master-readback-2026-05-18"
        write_text(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        assert_only(
            validate(root),
            ["survey:missing_marker:master-readback-2026-05-18"],
            "manifest_commit_alignment_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        manifest = json.loads(read_text(root / MANIFEST_PATH))
        manifest["gaps"] = manifest["gaps"][:-1]
        write_text(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        assert_only(
            validate(root),
            [
                "manifest:gaps_count_mismatch:14",
                "manifest:gap_status_mismatch:phase13-libfs-live-cursor-traversal:None",
                "manifest:blocked_count_mismatch:3",
            ],
            "manifest_gap_count_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        manifest = json.loads(read_text(root / MANIFEST_PATH))
        for gap in manifest["gaps"]:
            if gap["id"] == "phase13-build-gate":
                gap["status"] = "starter_landed"
        write_text(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        assert_only(
            validate(root),
            [
                "manifest:gap_status_mismatch:phase13-build-gate:starter_landed",
                "manifest:starter_count_mismatch:12",
                "manifest:blocked_count_mismatch:3",
            ],
            "manifest_build_gate_status_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(root / SURVEY_PATH, "broken\n")
        expected = [f"survey:missing_marker:{marker}" for marker in survey_markers(FIXTURE_COMMIT, FIXTURE_LANE)]
        assert_only(validate(root), expected, "survey_missing_markers_failed")
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / HELPER_PATH,
            "\n".join(marker for marker in HELPER_MARKERS if marker != "pub fn planSimpleOffsetRemove(") + "\n",
        )
        assert_only(
            validate(root),
            ["helper:missing_marker:pub fn planSimpleOffsetRemove("],
            "helper_missing_marker_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / HELPER_PATH,
            "\n".join(marker for marker in HELPER_MARKERS if marker != ".provides_transaction_release_planning = true") + "\n",
        )
        assert_only(
            validate(root),
            ["helper:missing_marker:.provides_transaction_release_planning = true"],
            "helper_release_flag_missing_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / HELPER_PATH,
            "\n".join(marker for marker in HELPER_MARKERS if marker != ".provides_directory_scan_resched_planning = true") + "\n",
        )
        assert_only(
            validate(root),
            ["helper:missing_marker:.provides_directory_scan_resched_planning = true"],
            "helper_scan_resched_flag_missing_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / REPLAY_PATH,
            "\n".join(marker for marker in replay_markers(FIXTURE_LANE) if marker != "\"phase13-libfs-offset-rename-planner\"") + "\n",
        )
        assert_only(
            validate(root),
            ['replay:missing_marker:"phase13-libfs-offset-rename-planner"'],
            "replay_rename_marker_failed",
        )
        case_count += 1

    print("PHASE13_LIBFS_PACKET_SELF_TEST=pass")
    print(f"PHASE13_LIBFS_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 13 libfs helper packet stays aligned with its survey, manifest, and reviewability replays."
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

    print("PHASE13_LIBFS_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
