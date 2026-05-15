#!/usr/bin/env python3
"""Fail closed on the current Phase 13 libfs packet surface."""

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

EXPECTED_LANE = "P13-Y01"
EXPECTED_COMMIT = "master-readback-2026-05-15"
EXPECTED_GAP_COUNT = 13
EXPECTED_STARTER_COUNT = 10
EXPECTED_BLOCKED_COUNT = 3

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
    "phase13-build-gate": "blocked_on_shared_build_surface",
    "phase13-libfs-live-dcache-mutation": "blocked_on_dcache_state",
    "phase13-libfs-live-inode-state": "blocked_on_inode_state",
}

SURVEY_MARKERS = (
    EXPECTED_COMMIT,
    "`fs/libfs.zig` still models positive-entry classification",
    "`simple_offset_add()` planning",
    "`simple_offset_remove()` planning",
    "`simple_transaction_get()`",
    "`simple_transaction_set()`",
    "`generic_check_addressable()`",
    "`zigux/tests/phase13_libfs.zig` replay",
    "blocked `phase13-build-gate`",
    "blocked `phase13-libfs-live-dcache-mutation`",
    "blocked `phase13-libfs-live-inode-state`",
)

HELPER_MARKERS = (
    '.name = "libfs_helper_lab"',
    ".provides_offset_add_planning = true",
    ".provides_offset_remove_planning = true",
    ".provides_offset_rename_planning = true",
    ".touches_live_dcache = false",
    ".touches_live_inode_state = false",
    "pub fn planSimpleOffsetAdd(",
    "pub fn planSimpleOffsetRemove(",
    "pub fn planSimpleOffsetRename(",
    "pub fn planSimpleOffsetRenameExchange(",
    "pub fn simpleTransactionGetPlan(",
    "pub fn simpleTransactionSetPlan(",
    "pub fn genericCheckAddressablePlan(",
)

REPLAY_MARKERS = (
    '@embedFile("phase13_libfs_manifest.json")',
    'test "offset add planning keeps busy-remap and managed-offset boundaries explicit" {',
    'test "offset remove planning keeps zero-offset noop and managed-slot erase explicit" {',
    'test "transaction publish planning validates response size and publish bookkeeping" {',
    'test "offset rename exchange planning keeps managed-slot swap and rollback expectations explicit" {',
)

REVIEWABILITY_MARKERS = (
    'test "descriptor keeps the current bounded helper surface explicit" {',
    'test "addressability planner stays reviewable without implying live page-cache ownership" {',
    'test "offset add and rename helpers stay reviewable as managed-slot planners rather than live directory mutation" {',
    'test "transaction acquire planner stays helper-only and page-bounded" {',
    'test "transaction release planner stays helper-only and unconditional-zero" {',
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def require_file(root: Path, rel_path: str, errors: list[str]) -> Path | None:
    path = root / rel_path
    if not path.is_file():
        errors.append(f"missing:{rel_path}")
        return None
    return path


def require_markers(text: str, label: str, markers: tuple[str, ...], errors: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            errors.append(f"{label}:missing_marker:{marker}")


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

    if manifest.get("lane_key") != EXPECTED_LANE:
        errors.append(f"manifest:lane_key_mismatch:{manifest.get('lane_key')}")
    if manifest.get("surveyed_commit") != EXPECTED_COMMIT:
        errors.append(f"manifest:surveyed_commit_mismatch:{manifest.get('surveyed_commit')}")

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

    require_markers(survey_text, "survey", SURVEY_MARKERS, errors)
    require_markers(helper_text, "helper", HELPER_MARKERS, errors)
    require_markers(replay_text, "replay", REPLAY_MARKERS, errors)
    require_markers(reviewability_text, "reviewability", REVIEWABILITY_MARKERS, errors)
    return errors


def seed_fixture_tree(root: Path) -> None:
    write_text(
        root / MANIFEST_PATH,
        json.dumps(
            {
                "lane_key": EXPECTED_LANE,
                "phase": "Phase 13",
                "surveyed_commit": EXPECTED_COMMIT,
                "anchor": "fs/libfs.c",
                "roadmap_destinations": ["fs/libfs.zig", "zigux/tests/", "Documentation/zigux/"],
                "survey_summary": {
                    "current_phase13_build_present": False,
                    "current_libfs_zig_present": True,
                    "current_phase13_libfs_test_present": True,
                    "current_phase13_libfs_reviewability_present": True,
                    "current_phase13_libfs_survey_present": True,
                    "current_phase13_libfs_manifest_present": True,
                },
                "gaps": [
                    {"id": gap_id, "status": status}
                    for gap_id, status in EXPECTED_GAPS.items()
                ],
            },
            indent=2,
        )
        + "\n",
    )
    write_text(root / SURVEY_PATH, "\n".join(SURVEY_MARKERS) + "\n")
    write_text(root / HELPER_PATH, "\n".join(HELPER_MARKERS) + "\n")
    write_text(root / REPLAY_PATH, "\n".join(REPLAY_MARKERS) + "\n")
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
        manifest["gaps"] = manifest["gaps"][:-1]
        write_text(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        assert_only(
            validate(root),
            [
                "manifest:gaps_count_mismatch:12",
                "manifest:gap_status_mismatch:phase13-libfs-live-inode-state:None",
                "manifest:blocked_count_mismatch:2",
            ],
            "manifest_gap_count_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(root / SURVEY_PATH, "broken\n")
        assert_only(
            validate(root),
            [f"survey:missing_marker:{marker}" for marker in SURVEY_MARKERS],
            "survey_missing_markers_failed",
        )
        case_count += 1

    print("PHASE13_LIBFS_PACKET_SELF_TEST=pass")
    print(f"PHASE13_LIBFS_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 13 libfs helper packet stays aligned with its manifest-backed survey and direct replays."
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
