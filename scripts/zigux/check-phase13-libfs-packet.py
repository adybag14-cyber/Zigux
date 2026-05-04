#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path


SURVEYED_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")

REQUIRED_FILES = [
    "fs/libfs.zig",
    "zigux/tests/phase13_libfs.zig",
    "zigux/tests/phase13_libfs_reviewability.zig",
    "zigux/tests/phase13_libfs_manifest.json",
    "zigux/tests/phase13_build.zig",
    "zigux/Makefile",
    "Documentation/zigux/phase13-libfs-slice.md",
    "Documentation/zigux/phase13-libfs-survey.md",
    "Documentation/zigux/phase13-roadmap-traceability.md",
]

LIBFS_MARKERS = [
    "provides_directory_cursor_preconditions = true",
    "provides_directory_cursor_reposition_planning = true",
    "provides_directory_close_planning = true",
    "provides_transaction_read_release_planning = true",
    "provides_open_private_data_planning = true",
    "provides_addressability_planning = true",
    "pub fn dcacheDirClosePlan(has_private_data: bool) DirectoryClosePlan",
    "pub fn simpleOpenPlan(inode_has_private_data: bool) SimpleOpenPlan",
    "pub fn genericCheckAddressablePlan(blocksize_bits: u6, num_blocks: u64, limits: AddressabilityLimits) AddressabilityPlan",
]

TEST_MARKERS = [
    'test "phase13 libfs close planning keeps release bookkeeping explicit without claiming teardown"',
    'test "phase13 libfs transaction read planning stays pure around private-data presence"',
    'test "phase13 libfs simple open planning keeps inode-private handoff explicit"',
    'test "phase13 libfs generic_check_addressable planning keeps empty and valid filesystems explicit"',
    'test "phase13 libfs generic_check_addressable planning rejects invalid bits and tiny synthetic limits"',
]

REVIEWABILITY_MARKERS = [
    'expected_surveyed_commit = "',
    "phase13-libfs-addressability-helper",
    "generic_check_addressable()",
    "phase13-libfs-dcache-dir-close-release-bookkeeping",
    "phase13-libfs-simple-open-private-data-planning",
    "phase13-libfs-dcache-cursor-helpers",
    "phase13-libfs-inode-and-pseudofs-lifecycle",
]

SURVEY_MARKERS = [
    "PHASE13_STATUS=active",
    "PHASE13_SLICE=libfs-helper-reviewability",
    "landed `phase13-build-gate`",
    "landed `phase13-make-target`",
    "landed `phase13-libfs-starter`",
    "landed `phase13-libfs-tests`",
    "landed `phase13-libfs-addressability-helper`",
    "generic_check_addressable()",
    "phase13-libfs-dcache-dir-close-release-bookkeeping",
    "phase13-libfs-simple-open-private-data-planning",
    "python3 scripts/zigux/check-phase13-libfs-packet.py",
]

SLICE_MARKERS = [
    "dcache_dir_close() release planner",
    "simple_open() planner",
    "The next honest bounded step in this same lane is a pure `generic_check_addressable()` addressability planner",
    "After that, the remaining cursor-backed helpers plus inode and pseudo-filesystem lifecycle work stay blocked on live VFS state.",
]

TRACEABILITY_MARKERS = [
    "### `fs/libfs.c`",
    "implementation anchor: `fs/libfs.zig`",
    "landed `phase13-build-gate`",
    "landed `phase13-make-target`",
    "landed `phase13-libfs-starter`",
    "landed `phase13-libfs-tests`",
    "landed `phase13-libfs-addressability-helper`",
    "generic_check_addressable()",
    "phase13-libfs-dcache-dir-close-release-bookkeeping",
    "phase13-libfs-simple-open-private-data-planning",
    "phase13-libfs-dcache-cursor-helpers",
    "phase13-libfs-inode-and-pseudofs-lifecycle",
]

MAKE_MARKERS = [
    "phase13-validate:",
    "scripts/zigux/check-phase13-libfs-packet.py --self-test",
    "scripts/zigux/check-phase13-libfs-packet.py",
    "scripts/zigux/validate-phase13-release.py",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _require_markers(missing: list[str], label: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            missing.append(f"{label}:{marker}")


def _check_repo(root: Path) -> list[str]:
    missing: list[str] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            missing.append(f"missing_file:{rel}")

    if missing:
        return missing

    libfs_text = _read(root / "fs/libfs.zig")
    tests_text = _read(root / "zigux/tests/phase13_libfs.zig")
    reviewability_text = _read(root / "zigux/tests/phase13_libfs_reviewability.zig")
    survey_text = _read(root / "Documentation/zigux/phase13-libfs-survey.md")
    slice_text = _read(root / "Documentation/zigux/phase13-libfs-slice.md")
    traceability_text = _read(root / "Documentation/zigux/phase13-roadmap-traceability.md")
    make_text = _read(root / "zigux/Makefile")

    _require_markers(missing, "libfs", libfs_text, LIBFS_MARKERS)
    _require_markers(missing, "tests", tests_text, TEST_MARKERS)
    _require_markers(missing, "reviewability", reviewability_text, REVIEWABILITY_MARKERS)
    _require_markers(missing, "survey", survey_text, SURVEY_MARKERS)
    _require_markers(missing, "slice", slice_text, SLICE_MARKERS)
    _require_markers(missing, "traceability", traceability_text, TRACEABILITY_MARKERS)
    _require_markers(missing, "make", make_text, MAKE_MARKERS)

    manifest = json.loads(_read(root / "zigux/tests/phase13_libfs_manifest.json"))
    if manifest.get("lane_key") != "P13-L04":
        missing.append("manifest:lane_key")
    if manifest.get("phase") != "Phase 13":
        missing.append("manifest:phase")
    if manifest.get("anchor") != "fs/libfs.c":
        missing.append("manifest:anchor")
    surveyed_commit = manifest.get("surveyed_commit")
    if not isinstance(surveyed_commit, str) or not SURVEYED_COMMIT_RE.fullmatch(surveyed_commit):
        missing.append("manifest:surveyed_commit")
    else:
        if f"PHASE13_SURVEYED_COMMIT={surveyed_commit}" not in survey_text:
            missing.append("survey:surveyed_commit")
        if surveyed_commit not in reviewability_text:
            missing.append("reviewability:surveyed_commit")
        if surveyed_commit not in traceability_text:
            missing.append("traceability:surveyed_commit")

    gaps = manifest.get("gaps")
    if not isinstance(gaps, list):
        missing.append("manifest:gaps")
        return missing

    blocked_ids = {
        gap.get("id")
        for gap in gaps
        if isinstance(gap, dict) and gap.get("status") == "blocked_on_vfs_state"
    }
    if blocked_ids != {
        "phase13-libfs-dcache-cursor-helpers",
        "phase13-libfs-inode-and-pseudofs-lifecycle",
    }:
        missing.append("manifest:blocked_gap_set")

    ready_next_ids = {
        gap.get("id")
        for gap in gaps
        if isinstance(gap, dict) and gap.get("status") == "ready_next"
    }
    if ready_next_ids:
        missing.append("manifest:ready_next_gap_set")

    landed_ids = {
        gap.get("id")
        for gap in gaps
        if isinstance(gap, dict) and gap.get("status") == "starter_landed"
    }
    for expected in (
        "phase13-build-gate",
        "phase13-make-target",
        "phase13-libfs-starter",
        "phase13-libfs-tests",
        "phase13-libfs-dcache-dir-close-release-bookkeeping",
        "phase13-libfs-simple-open-private-data-planning",
        "phase13-libfs-addressability-helper",
    ):
        if expected not in landed_ids:
            missing.append(f"manifest:missing_landed_gap:{expected}")

    return missing


def _run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for rel in (
            "fs",
            "zigux/tests",
            "zigux",
            "Documentation/zigux",
        ):
            (root / rel).mkdir(parents=True, exist_ok=True)

        surveyed_commit = "949994db4046ec70abf044d1b2ea874fde9bc4a6"
        (root / "fs/libfs.zig").writeText("\n".join(LIBFS_MARKERS) + "\n", encoding="utf-8")
        (root / "zigux/tests/phase13_libfs.zig").writeText("\n".join(TEST_MARKERS) + "\n", encoding="utf-8")
        (root / "zigux/tests/phase13_libfs_reviewability.zig").writeText(
            'expected_surveyed_commit = "' + surveyed_commit + '"\n' + "\n".join(REVIEWABILITY_MARKERS[1:]) + "\n",
            encoding="utf-8",
        )
        (root / "Documentation/zigux/phase13-libfs-survey.md").writeText(
            f"PHASE13_SURVEYED_COMMIT={surveyed_commit}\n" + "\n".join(SURVEY_MARKERS) + "\n",
            encoding="utf-8",
        )
        (root / "Documentation/zigux/phase13-libfs-slice.md").writeText("\n".join(SLICE_MARKERS) + "\n", encoding="utf-8")
        (root / "Documentation/zigux/phase13-roadmap-traceability.md").writeText(
            f"manifest `surveyed_commit`: `{surveyed_commit}`\n" + "\n".join(TRACEABILITY_MARKERS) + "\n",
            encoding="utf-8",
        )
        (root / "zigux/Makefile").writeText("\n".join(MAKE_MARKERS) + "\n", encoding="utf-8")
        (root / "zigux/tests/phase13_build.zig").writeText("placeholder\n", encoding="utf-8")
        manifest = {
            "lane_key": "P13-L04",
            "phase": "Phase 13",
            "surveyed_commit": surveyed_commit,
            "anchor": "fs/libfs.c",
            "gaps": [
                {"id": "phase13-build-gate", "status": "starter_landed"},
                {"id": "phase13-make-target", "status": "starter_landed"},
                {"id": "phase13-libfs-starter", "status": "starter_landed"},
                {"id": "phase13-libfs-tests", "status": "starter_landed"},
                {"id": "phase13-libfs-dcache-dir-close-release-bookkeeping", "status": "starter_landed"},
                {"id": "phase13-libfs-simple-open-private-data-planning", "status": "starter_landed"},
                {"id": "phase13-libfs-addressability-helper", "status": "starter_landed"},
                {"id": "phase13-libfs-dcache-cursor-helpers", "status": "blocked_on_vfs_state"},
                {"id": "phase13-libfs-inode-and-pseudofs-lifecycle", "status": "blocked_on_vfs_state"},
            ],
        }
        (root / "zigux/tests/phase13_libfs_manifest.json").writeText(
            json.dumps(manifest, indent=2) + "\n",
            encoding="utf-8",
        )

        missing = _check_repo(root)
        if missing:
            print("PHASE13_LIBFS_PACKET_SELF_TEST=fail")
            for item in missing:
                print(item)
            return 1

    print("PHASE13_LIBFS_PACKET_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()

    if args.self_test:
        return _run_self_test()

    missing = _check_repo(Path(args.root).resolve())
    if missing:
        print("PHASE13_LIBFS_PACKET=fail")
        print("PHASE13_LIBFS_PACKET_MISSING_START")
        for item in missing:
            print(item)
        print("PHASE13_LIBFS_PACKET_MISSING_END")
        return 1

    print("PHASE13_LIBFS_PACKET=pass")
    print(f"PHASE13_LIBFS_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE13_LIBFS_MARKER_COUNT="
        f"{len(LIBFS_MARKERS) + len(TEST_MARKERS) + len(REVIEWABILITY_MARKERS) + len(SURVEY_MARKERS) + len(SLICE_MARKERS) + len(TRACEABILITY_MARKERS) + len(MAKE_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
