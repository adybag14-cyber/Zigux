#!/usr/bin/env python3
"""Guard the shipped Phase 13 libfs helper packet and its next bounded step."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path


SURVEY_PATH = Path("Documentation/zigux/phase13-libfs-survey.md")
MANIFEST_PATH = Path("zigux/tests/phase13_libfs_manifest.json")
TEST_PATH = Path("zigux/tests/phase13_libfs.zig")
REVIEWABILITY_PATH = Path("zigux/tests/phase13_libfs_reviewability.zig")

SURVEY_MARKERS = (
    "PHASE13_SLICE=libfs-helper-filesystem-boundary-survey",
    "phase13-libfs-addressability-helper",
    "phase13-libfs-reviewability-gate",
    "blocked `phase13-build-gate`",
    "blocked `phase13-libfs-live-dcache-mutation`",
    "blocked `phase13-libfs-live-inode-state`",
    "offset-map lifecycle helper such as destroy planning",
    "Keep verification-only published-tree replays on `P13-L03`.",
)

TEST_MARKERS = (
    'test "offset add planning keeps busy-remap and managed-offset boundaries explicit"',
    'test "offset remove planning keeps zero-offset noop and managed-slot erase explicit"',
    '"id": "phase13-libfs-addressability-helper"',
    '"id": "phase13-libfs-reviewability-gate"',
    '"id": "phase13-build-gate"',
    '"id": "phase13-libfs-live-dcache-mutation"',
    '"id": "phase13-libfs-live-inode-state"',
    "simple_offset_add()",
    "simple_offset_remove()",
    "generic_check_addressable()",
)

REVIEWABILITY_MARKERS = (
    'test "offset add and rename helpers stay reviewable as managed-slot planners rather than live directory mutation"',
    'test "offset remove planning stays reviewable as erase-only lifecycle bookkeeping"',
    "planSimpleOffsetAdd",
    "planSimpleOffsetRemove",
)

MANIFEST_EXPECTATIONS = {
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


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def require_markers(path: Path, text: str, markers: tuple[str, ...], errors: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            errors.append(f"{path}: missing marker {marker!r}")


def collect_manifest_statuses(node: object, statuses: dict[str, str]) -> None:
    if isinstance(node, dict):
        node_id = node.get("id")
        node_status = node.get("status")
        if isinstance(node_id, str) and isinstance(node_status, str):
            statuses[node_id] = node_status
        for value in node.values():
            collect_manifest_statuses(value, statuses)
    elif isinstance(node, list):
        for value in node:
            collect_manifest_statuses(value, statuses)


def validate_manifest(path: Path, errors: list[str]) -> None:
    try:
        payload = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        errors.append(f"{path}: invalid JSON: {exc}")
        return

    statuses: dict[str, str] = {}
    collect_manifest_statuses(payload, statuses)

    for item_id, expected_status in MANIFEST_EXPECTATIONS.items():
        actual_status = statuses.get(item_id)
        if actual_status != expected_status:
            errors.append(
                f"{path}: expected {item_id!r} to have status {expected_status!r}, got {actual_status!r}"
            )


def validate_repo(repo_root: Path) -> list[str]:
    errors: list[str] = []

    survey_path = repo_root / SURVEY_PATH
    manifest_path = repo_root / MANIFEST_PATH
    test_path = repo_root / TEST_PATH
    reviewability_path = repo_root / REVIEWABILITY_PATH

    for path in (survey_path, manifest_path, test_path, reviewability_path):
        if not path.is_file():
            errors.append(f"missing required file: {path}")
    if errors:
        return errors

    require_markers(survey_path, read_text(survey_path), SURVEY_MARKERS, errors)
    require_markers(test_path, read_text(test_path), TEST_MARKERS, errors)
    require_markers(reviewability_path, read_text(reviewability_path), REVIEWABILITY_MARKERS, errors)
    validate_manifest(manifest_path, errors)
    return errors


def write_fixture(root: Path, relpath: Path, text: str) -> None:
    path = root / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase13-libfs-packet-") as temp_dir:
        root = Path(temp_dir)
        write_fixture(
            root,
            SURVEY_PATH,
            """# Phase 13 libfs Survey
PHASE13_SLICE=libfs-helper-filesystem-boundary-survey
phase13-libfs-addressability-helper
phase13-libfs-reviewability-gate
blocked `phase13-build-gate`
blocked `phase13-libfs-live-dcache-mutation`
blocked `phase13-libfs-live-inode-state`
offset-map lifecycle helper such as destroy planning
Keep verification-only published-tree replays on `P13-L03`.
""",
        )
        write_fixture(
            root,
            TEST_PATH,
            """test "offset add planning keeps busy-remap and managed-offset boundaries explicit" {}
test "offset remove planning keeps zero-offset noop and managed-slot erase explicit" {}
"id": "phase13-libfs-addressability-helper"
"id": "phase13-libfs-reviewability-gate"
"id": "phase13-build-gate"
"id": "phase13-libfs-live-dcache-mutation"
"id": "phase13-libfs-live-inode-state"
simple_offset_add()
simple_offset_remove()
generic_check_addressable()
""",
        )
        write_fixture(
            root,
            REVIEWABILITY_PATH,
            """test "offset add and rename helpers stay reviewable as managed-slot planners rather than live directory mutation" {}
test "offset remove planning stays reviewable as erase-only lifecycle bookkeeping" {}
planSimpleOffsetAdd
planSimpleOffsetRemove
""",
        )
        write_fixture(
            root,
            MANIFEST_PATH,
            json.dumps(
                {
                    "items": [
                        {"id": item_id, "status": status}
                        for item_id, status in MANIFEST_EXPECTATIONS.items()
                    ]
                },
                indent=2,
            ),
        )

        errors = validate_repo(root)
        if errors:
            print("PHASE13_LIBFS_PACKET_CONTINUITY_SELF_TEST=fail")
            for error in errors:
                print(error)
            return 1

        broken_survey = root / SURVEY_PATH
        broken_survey.write_text(
            broken_survey.read_text(encoding="utf-8").replace(
                "offset-map lifecycle helper such as destroy planning",
                "offset-map lifecycle helper placeholder",
            ),
            encoding="utf-8",
        )
        broken_errors = validate_repo(root)
        if not any("destroy planning" in error for error in broken_errors):
            print("PHASE13_LIBFS_PACKET_CONTINUITY_SELF_TEST=fail")
            print("self-test did not detect a missing destroy-planning marker")
            return 1

    print("PHASE13_LIBFS_PACKET_CONTINUITY_SELF_TEST=pass")
    print("PHASE13_LIBFS_PACKET_CONTINUITY_SELF_TEST_CASES=2")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the shipped Phase 13 libfs helper packet and its next bounded follow-up."
    )
    parser.add_argument("--repo-root", default=".", help="Path to the Zigux repository root")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = validate_repo(Path(args.repo_root))
    if errors:
        print("PHASE13_LIBFS_PACKET_CONTINUITY=fail")
        for error in errors:
            print(error)
        return 1

    print("PHASE13_LIBFS_PACKET_CONTINUITY=pass")
    print(f"PHASE13_LIBFS_PACKET_CONTINUITY_FILES=4")
    print(
        "PHASE13_LIBFS_PACKET_CONTINUITY_NEXT_STEP=phase13-libfs-offset-map-destroy-planning"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
