#!/usr/bin/env python3
"""Validate the current Phase 3 ida slot starter packet."""

from __future__ import annotations

import argparse
from pathlib import Path
import tempfile


HELPER_PATH = Path("zigux/helpers/ida_slot_view.zig")
TEST_PATH = Path("zigux/tests/phase3_ida_slot_starter_packet.zig")
BUILD_PATH = Path("zigux/tests/phase3_ida_slot_starter_packet_build.zig")
MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_ida_slot_manifest.json")

REQUIRED_MARKERS = {
    HELPER_PATH: (
        "pub const SlotKind = enum {",
        "pub fn fromInlineMask(mask: usize) MakeInlineMaskError!SlotView {",
        "pub fn fromBitmapPointer(pointer: usize) SlotView {",
    ),
    TEST_PATH: (
        'test "ida slot view keeps empty slots explicit" {',
        'test "ida slot view keeps inline mask lanes bounded to the helper-local packet" {',
    ),
    BUILD_PATH: (
        '.root_source_file = b.path("../helpers/ida_slot_view.zig"),',
        '"phase3-ida-slot-starter-packet-test"',
    ),
    MANIFEST_PATH: (
        '"slug": "phase3-ida-slot"',
        '"status": "starter_and_dump_packet_present"',
        '"zigux/tests/phase3_ida_slot_dump.zig"',
    ),
}


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    for relative_path, markers in REQUIRED_MARKERS.items():
        path = repo_root / relative_path
        if not path.exists():
            issues.append(f"missing repo file: {relative_path.as_posix()}")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                issues.append(f"missing {relative_path.as_posix()} marker: {marker}")
    return issues


def populate_repo(root: Path) -> None:
    for relative_path, markers in REQUIRED_MARKERS.items():
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(markers) + "\n", encoding="utf-8")


SELF_TEST_CASES = (
    (HELPER_PATH, "pub fn fromInlineMask(mask: usize) MakeInlineMaskError!SlotView {"),
    (TEST_PATH, 'test "ida slot view keeps inline mask lanes bounded to the helper-local packet" {'),
    (BUILD_PATH, '"phase3-ida-slot-starter-packet-test"'),
)


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_ida_slot_starter_") as temp_dir:
        root = Path(temp_dir)
        populate_repo(root)
        issues = validate_repo(root)
        if issues:
            print("PHASE3_IDA_SLOT_STARTER_PACKET_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for relative_path, marker in SELF_TEST_CASES:
            populate_repo(root)
            path = root / relative_path
            path.write_text(path.read_text(encoding="utf-8").replace(marker, "", 1), encoding="utf-8")
            issues = validate_repo(root)
            expected = f"missing {relative_path.as_posix()} marker: {marker}"
            if expected not in issues:
                print("PHASE3_IDA_SLOT_STARTER_PACKET_SELF_TEST=fail")
                print(f"expected missing marker was not reported: {expected}")
                return 1

    print("PHASE3_IDA_SLOT_STARTER_PACKET_SELF_TEST=pass")
    print(f"PHASE3_IDA_SLOT_STARTER_PACKET_SELF_TEST_CASES={len(SELF_TEST_CASES)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the current Phase 3 ida slot starter packet.")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_IDA_SLOT_STARTER_PACKET=fail")
        for issue in issues:
            print(issue)
        return 1

    print(f"validated {args.repo_root / HELPER_PATH}")
    print(f"validated {args.repo_root / TEST_PATH}")
    print(f"validated {args.repo_root / MANIFEST_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
