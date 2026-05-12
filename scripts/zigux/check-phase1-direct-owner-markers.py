#!/usr/bin/env python3

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SELF_PATH.parents[3] if len(SELF_PATH.parents) >= 4 else SELF_PATH.parent
LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")

EXPECTED_MARKERS = [
    "PHASE1_BITMAP_DIRECT_OWNER=bitmap helper-local anchors plus the committed bitmap replay keys and the already-landed shared closure-validator bitmap review markers it already owns",
    "PHASE1_FIND_BIT_DIRECT_OWNER=find_bit helper-local anchors plus the committed find_bit replay fields already emitted by the shared C harness and consumed by the shared fixture",
    "PHASE1_RBTREE_DIRECT_OWNER=rbtree iterator and cached-root coverage stay helper-local until exactly one dedicated shared iterator or cached-root leftmost-return fixture key lands",
    "PHASE1_STRING_DIRECT_OWNER=string already has shared helper-manifest anchor validation in validate-phase1-closure.py, so reopen only for direct anchor drift or committed shared replay drift",
]


def repo_root(root_arg: str | None) -> Path:
    return DEFAULT_ROOT if root_arg is None else Path(root_arg).resolve()


def lane_note_path(root: Path) -> Path:
    return root / LANE_NOTE_REL


def collect_missing_markers(text: str) -> list[str]:
    missing: list[str] = []
    for marker in EXPECTED_MARKERS:
        count = text.count(marker)
        if count != 1:
            missing.append(f"{marker}:expected=1:actual={count}")
    return missing


def make_fixture_root(root: Path) -> None:
    lane_note = lane_note_path(root)
    lane_note.parent.mkdir(parents=True, exist_ok=True)
    lane_note.write_text("\n".join(f"- `{marker}`" for marker in EXPECTED_MARKERS) + "\n", encoding="utf-8")


def run_self_test() -> int:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="zigux_phase1_direct_owner_") as tmp_dir:
        root = Path(tmp_dir)
        make_fixture_root(root)

        lane_note = lane_note_path(root)
        text = lane_note.read_text(encoding="utf-8")
        assert collect_missing_markers(text) == []
        case_count += 1

        lane_note.unlink()
        assert not lane_note.exists()
        case_count += 1
        make_fixture_root(root)

        text = lane_note.read_text(encoding="utf-8")
        lane_note.write_text(text.replace(EXPECTED_MARKERS[0], "", 1), encoding="utf-8")
        assert f"{EXPECTED_MARKERS[0]}:expected=1:actual=0" in collect_missing_markers(
            lane_note.read_text(encoding="utf-8")
        )
        case_count += 1
        make_fixture_root(root)

        text = lane_note.read_text(encoding="utf-8")
        lane_note.write_text(text + f"- `{EXPECTED_MARKERS[1]}`\n", encoding="utf-8")
        assert f"{EXPECTED_MARKERS[1]}:expected=1:actual=2" in collect_missing_markers(
            lane_note.read_text(encoding="utf-8")
        )
        case_count += 1

    print("PHASE1_DIRECT_OWNER_MARKERS_SELF_TEST=pass")
    print(f"PHASE1_DIRECT_OWNER_MARKERS_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the four Phase 1 direct-owner markers in the host-helper lane note."
    )
    parser.add_argument("--root", help="Validate an alternate Zigux tree root.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker self-tests.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    root = repo_root(args.root)
    lane_note = lane_note_path(root)
    if not lane_note.exists():
        print("PHASE1_DIRECT_OWNER_MARKERS=fail")
        print("MISSING_FILES_START")
        print(LANE_NOTE_REL.as_posix())
        print("MISSING_FILES_END")
        return 1

    missing = collect_missing_markers(lane_note.read_text(encoding="utf-8"))
    if missing:
        print("PHASE1_DIRECT_OWNER_MARKERS=fail")
        print("MISSING_MARKERS_START")
        for item in missing:
            print(item)
        print("MISSING_MARKERS_END")
        return 1

    print("PHASE1_DIRECT_OWNER_MARKERS=pass")
    print(f"PHASE1_DIRECT_OWNER_MARKER_COUNT={len(EXPECTED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
