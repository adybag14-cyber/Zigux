#!/usr/bin/env python3
"""Fail-closed guard for the current Phase 13 libfs offset-lifetime packet."""

from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path


REQUIRED_FILES = {
    "fs/libfs.zig": [
        "provides_offset_remove_planning",
        "offsetReaddirPlan",
        "offsetRenamePlan",
        "planSimpleOffsetRemove",
    ],
    "zigux/tests/phase13_libfs.zig": [
        "offset remove planning keeps zero-offset noop and managed-slot erase explicit",
        "offset-based rename planning keeps reserved slots and end-of-directory explicit",
    ],
    "zigux/tests/phase13_libfs_reviewability.zig": [
        "provides_offset_remove_planning",
        "offset remove planning stays reviewable as erase-only lifecycle bookkeeping",
        "offset-based rename planning stays reviewable without live directory mutation",
    ],
    "zigux/tests/phase13_libfs_manifest.json": [
        '"id": "phase13-libfs-offset-remove-planner"',
        '"id": "phase13-libfs-offset-rename-planner"',
        '"id": "phase13-libfs-reviewability-gate"',
    ],
    "Documentation/zigux/phase13-libfs-survey.md": [
        "landed `phase13-libfs-offset-remove-planner`",
        "prefer the next equally small offset-map lifecycle helper such as destroy planning",
        "Keep verification-only published-tree replays on `P13-L03`.",
    ],
}

REQUIRED_ABSENCES = {
    "fs/libfs.zig": [
        "planSimpleOffsetDestroy",
        "provides_offset_destroy_planning",
    ],
    "zigux/tests/phase13_libfs.zig": [
        "offset destroy planning keeps teardown lifetime discipline helper-only",
    ],
    "zigux/tests/phase13_libfs_reviewability.zig": [
        "offset destroy planning stays reviewable as teardown-only map release",
    ],
    "zigux/tests/phase13_libfs_manifest.json": [
        '"id": "phase13-libfs-offset-destroy-planner"',
    ],
    "Documentation/zigux/phase13-libfs-survey.md": [
        "landed `phase13-libfs-offset-destroy-planner`",
    ],
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def check_root(root: Path) -> tuple[int, int]:
    checked_files = 0
    checked_markers = 0

    for rel_path, markers in REQUIRED_FILES.items():
        file_path = root / rel_path
        if not file_path.is_file():
            raise SystemExit(f"missing required file: {rel_path}")
        text = read_text(file_path)
        checked_files += 1
        for marker in markers:
            if marker not in text:
                raise SystemExit(f"missing marker in {rel_path}: {marker}")
            checked_markers += 1

        for marker in REQUIRED_ABSENCES.get(rel_path, []):
            if marker in text:
                raise SystemExit(f"unexpected marker in {rel_path}: {marker}")

    return checked_files, checked_markers


def write_sample_root(root: Path) -> None:
    for rel_path, markers in REQUIRED_FILES.items():
        file_path = root / rel_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        lines = [f"# sample for {rel_path}"]
        lines.extend(markers)
        lines.append("# absent markers intentionally omitted from this sample")
        file_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="p13_libfs_offset_lifetime_") as tmp:
        root = Path(tmp)
        write_sample_root(root)
        checked_files, checked_markers = check_root(root)

        bad_root = root / "broken"
        shutil.copytree(root, bad_root)
        broken_manifest = bad_root / "zigux/tests/phase13_libfs_manifest.json"
        broken_manifest.write_text(
            read_text(broken_manifest) + '\n"id": "phase13-libfs-offset-destroy-planner"\n',
            encoding="utf-8",
        )
        try:
            check_root(bad_root)
        except SystemExit as exc:
            if "unexpected marker" not in str(exc):
                raise
        else:
            raise SystemExit("self-test expected unexpected-marker failure")

    print("PHASE13_LIBFS_OFFSET_LIFETIME_PACKET_SELF_TEST=pass")
    print("PHASE13_LIBFS_OFFSET_LIFETIME_PACKET_SELF_TEST_CASE_COUNT=2")
    print(f"PHASE13_LIBFS_OFFSET_LIFETIME_PACKET_REQUIRED_FILE_COUNT={checked_files}")
    print(f"PHASE13_LIBFS_OFFSET_LIFETIME_PACKET_REQUIRED_MARKER_COUNT={checked_markers}")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        return 0

    if args.self_test:
        return run_self_test()

    if args.root is None:
        raise SystemExit("expected --root, --self-test, or --write-sample-root")

    checked_files, checked_markers = check_root(args.root)
    print("PHASE13_LIBFS_OFFSET_LIFETIME_PACKET=pass")
    print(f"PHASE13_LIBFS_OFFSET_LIFETIME_PACKET_REQUIRED_FILE_COUNT={checked_files}")
    print(f"PHASE13_LIBFS_OFFSET_LIFETIME_PACKET_REQUIRED_MARKER_COUNT={checked_markers}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
