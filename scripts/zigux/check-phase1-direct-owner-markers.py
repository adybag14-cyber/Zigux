#!/usr/bin/env python3

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent
LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")

REQUIRED_MARKERS = [
    "- `PHASE1_BITMAP_DIRECT_OWNER=bitmap helper-local anchors plus the committed bitmap replay keys and the already-landed shared closure-validator bitmap review markers it already owns`",
    "- `PHASE1_FIND_BIT_DIRECT_OWNER=find_bit helper-local anchors plus the committed find_bit replay fields already emitted by the shared C harness and consumed by the shared fixture`",
    "- `PHASE1_RBTREE_DIRECT_OWNER=rbtree iterator and cached-root coverage stay helper-local until exactly one dedicated shared iterator or cached-root leftmost-return fixture key lands`",
    "- `PHASE1_STRING_DIRECT_OWNER=string already has shared helper-manifest anchor validation in validate-phase1-closure.py, so reopen only for direct anchor drift or committed shared replay drift`",
]


def repo_root(root_arg: str | None) -> Path:
    return DEFAULT_ROOT if root_arg is None else Path(root_arg).resolve()


def lane_note_path(root: Path) -> Path:
    return root / LANE_NOTE_REL


def collect_missing_files(root: Path) -> list[str]:
    return [str(LANE_NOTE_REL)] if not lane_note_path(root).exists() else []


def collect_missing_markers(root: Path) -> list[str]:
    text = lane_note_path(root).read_text(encoding="utf-8")
    missing: list[str] = []
    for marker in REQUIRED_MARKERS:
        count = text.count(marker)
        if count != 1:
            missing.append(f"phase1_direct_owner_marker:{marker}:expected=1:actual={count}")
    return missing


def make_fixture_root(root: Path) -> None:
    path = lane_note_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(REQUIRED_MARKERS) + "\n", encoding="utf-8")


def run_self_test() -> None:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_direct_owner_") as tmp_dir:
        root = Path(tmp_dir)
        make_fixture_root(root)
        assert collect_missing_files(root) == []
        assert collect_missing_markers(root) == []
        case_count += 1

        lane_note_path(root).unlink()
        assert collect_missing_files(root) == [str(LANE_NOTE_REL)]
        case_count += 1
        make_fixture_root(root)

        for marker in REQUIRED_MARKERS:
            note_path = lane_note_path(root)
            baseline = note_path.read_text(encoding="utf-8")
            note_path.write_text(baseline.replace(marker + "\n", "", 1), encoding="utf-8")
            assert f"phase1_direct_owner_marker:{marker}:expected=1:actual=0" in collect_missing_markers(root)
            case_count += 1
            make_fixture_root(root)

        for marker in REQUIRED_MARKERS:
            note_path = lane_note_path(root)
            baseline = note_path.read_text(encoding="utf-8")
            note_path.write_text(baseline + marker + "\n", encoding="utf-8")
            assert f"phase1_direct_owner_marker:{marker}:expected=1:actual=2" in collect_missing_markers(root)
            case_count += 1
            make_fixture_root(root)

    print("PHASE1_DIRECT_OWNER_MARKER_CHECK_SELF_TEST=pass")
    print(f"PHASE1_DIRECT_OWNER_MARKER_CHECK_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Exact-check the Phase 1 direct-owner markers in the lane note."
    )
    parser.add_argument("--root", help="Validate an alternate Zigux tree root.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in self-tests.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    root = repo_root(args.root)
    missing_files = collect_missing_files(root)
    if missing_files:
        print("PHASE1_DIRECT_OWNER_MARKER_CHECK=fail")
        print("MISSING_PHASE1_DIRECT_OWNER_MARKER_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE1_DIRECT_OWNER_MARKER_FILES_END")
        return 1

    missing_markers = collect_missing_markers(root)
    if missing_markers:
        print("PHASE1_DIRECT_OWNER_MARKER_CHECK=fail")
        print("MISSING_PHASE1_DIRECT_OWNER_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE1_DIRECT_OWNER_MARKERS_END")
        return 1

    print("PHASE1_DIRECT_OWNER_MARKER_CHECK=pass")
    print(f"PHASE1_DIRECT_OWNER_MARKER_REQUIRED_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
