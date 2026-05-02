#!/usr/bin/env python3
"""Report whether the Phase 1 rbtree alias surface is still open or fully closed.

This checker is intentionally lane-scoped to the existing host-tools `rbtree`
packet. It treats the current manifest note as a real state that should remain
internally consistent until a later bounded alias-repair lands.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]

RBTREE_PATH = ROOT / "tools/lib/rbtree.zig"
MANIFEST_PATH = ROOT / "zigux/tests/fixtures/phase1_helper_manifest.json"

REQUIRED_ALIAS_MARKERS = (
    "pub const rb_node = Node;",
    "pub const rb_root = Root;",
    "pub const rb_root_cached = RootCached;",
    "pub fn RB_EMPTY_ROOT(root: *const Root) bool {",
    "pub fn RB_EMPTY_NODE(node: *const Node) bool {",
    "pub fn RB_CLEAR_NODE(node: *Node) void {",
    "pub fn rb_link_node(node: *Node, parent: ?*Node, link: *?*Node) void {",
    "pub fn rb_insert_color(node: *Node, root: *Root) void {",
    "pub fn rb_first(root: *const Root) ?*Node {",
    "pub fn rb_last(root: *const Root) ?*Node {",
    "pub fn rb_next(node: *const Node) ?*Node {",
    "pub fn rb_prev(node: *const Node) ?*Node {",
    "pub fn rb_replace_node(victim: *Node, new: *Node, root: *Root) void {",
    "pub fn rb_erase(node: *Node, root: *Root) void {",
    "pub fn rb_erase_init(node: *Node, root: *Root) void {",
    "pub fn rb_first_postorder(root: *const Root) ?*Node {",
    "pub fn rb_next_postorder(node: *const Node) ?*Node {",
    "pub fn rb_first_cached(root: *const RootCached) ?*Node {",
    "pub fn rb_insert_color_cached(node: *Node, root: *RootCached, leftmost: bool) void {",
    "pub fn rb_erase_cached(node: *Node, root: *RootCached) void {",
    "pub fn rb_replace_node_cached(victim: *Node, new: *Node, root: *RootCached) void {",
    "pub fn rb_add_cached(node: *Node, root: *RootCached, less: LessFn) ?*Node {",
    "pub fn rb_find_add_cached(node: *Node, root: *RootCached, cmp: CmpNodeFn) ?*Node {",
)

OPEN_STATE_SUMMARY = (
    "Committed C-backed parity coverage includes ordered forward and reverse traversal "
    "plus replaceNode, eraseInit, postorder traversal, and detached-node state checks, "
    "while Linux-style rb_* alias parity remains explicitly out of scope for this "
    "closed Phase 1 tranche."
)

OPEN_STATE_ALIAS_GAP_NOTE = (
    "Linux-style rb_* alias surface parity is still missing for the already-ported "
    "entry points, and that remaining surface stays explicitly out of scope for the "
    "closed Phase 1 tranche until a later bounded repair lands."
)


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_manifest_note() -> dict[str, object]:
    manifest = json.loads(load_text(MANIFEST_PATH))
    notes = manifest.get("helper_review_notes")
    if not isinstance(notes, dict):
        raise ValueError("phase1 helper manifest is missing helper_review_notes")

    note = notes.get("tools/lib/rbtree.zig")
    if not isinstance(note, dict):
        raise ValueError("phase1 helper manifest is missing the rbtree review note")

    return note


def classify_alias_surface(rbtree_text: str) -> tuple[str, list[str]]:
    missing = [marker for marker in REQUIRED_ALIAS_MARKERS if marker not in rbtree_text]
    if not missing:
        return ("closed", [])
    if len(missing) == len(REQUIRED_ALIAS_MARKERS):
        return ("gap_open", missing)
    return ("partial", missing)


def validate_state(require_closed: bool) -> int:
    rbtree_text = load_text(RBTREE_PATH)
    note = load_manifest_note()
    state, missing = classify_alias_surface(rbtree_text)

    summary = note.get("summary")
    alias_gap_note = note.get("alias_gap_note")

    if state == "partial":
        print("PHASE1_RBTREE_ALIAS_SURFACE=fail")
        print("PHASE1_RBTREE_ALIAS_REASON=partial_surface")
        print(f"PHASE1_RBTREE_ALIAS_PRESENT_COUNT={len(REQUIRED_ALIAS_MARKERS) - len(missing)}")
        print(f"PHASE1_RBTREE_ALIAS_MISSING_COUNT={len(missing)}")
        for marker in missing:
            print(f"PHASE1_RBTREE_ALIAS_MISSING={marker}")
        return 1

    if state == "gap_open":
        if summary != OPEN_STATE_SUMMARY:
            print("PHASE1_RBTREE_ALIAS_SURFACE=fail")
            print("PHASE1_RBTREE_ALIAS_REASON=missing_open_state_summary")
            return 1
        if alias_gap_note != OPEN_STATE_ALIAS_GAP_NOTE:
            print("PHASE1_RBTREE_ALIAS_SURFACE=fail")
            print("PHASE1_RBTREE_ALIAS_REASON=missing_alias_gap_note")
            return 1

        print("PHASE1_RBTREE_ALIAS_SURFACE=gap_open")
        print(f"PHASE1_RBTREE_ALIAS_MISSING_COUNT={len(missing)}")
        for marker in missing:
            print(f"PHASE1_RBTREE_ALIAS_MISSING={marker}")
        print(
            "PHASE1_RBTREE_ALIAS_NEXT_STEP=land the Linux-style rb_* aliases in tools/lib/rbtree.zig "
            "and retire the manifest gap note in the same bounded packet"
        )
        return 1 if require_closed else 0

    if summary == OPEN_STATE_SUMMARY:
        print("PHASE1_RBTREE_ALIAS_SURFACE=fail")
        print("PHASE1_RBTREE_ALIAS_REASON=stale_open_state_summary")
        return 1
    if alias_gap_note is not None:
        print("PHASE1_RBTREE_ALIAS_SURFACE=fail")
        print("PHASE1_RBTREE_ALIAS_REASON=stale_alias_gap_note")
        return 1

    print("PHASE1_RBTREE_ALIAS_SURFACE=closed")
    print(f"PHASE1_RBTREE_ALIAS_MARKER_COUNT={len(REQUIRED_ALIAS_MARKERS)}")
    return 0


def run_self_test() -> int:
    missing = list(REQUIRED_ALIAS_MARKERS)
    state, unresolved = classify_alias_surface("")
    assert state == "gap_open"
    assert unresolved == missing

    closed_text = "\n".join(REQUIRED_ALIAS_MARKERS)
    state, unresolved = classify_alias_surface(closed_text)
    assert state == "closed"
    assert unresolved == []

    partial_text = "\n".join(REQUIRED_ALIAS_MARKERS[:5])
    state, unresolved = classify_alias_surface(partial_text)
    assert state == "partial"
    assert unresolved == list(REQUIRED_ALIAS_MARKERS[5:])

    print("PHASE1_RBTREE_ALIAS_SELF_TEST=pass")
    print(f"PHASE1_RBTREE_ALIAS_REQUIRED_MARKER_COUNT={len(REQUIRED_ALIAS_MARKERS)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--require-closed",
        action="store_true",
        help="exit non-zero unless the full Linux-style rb_* alias surface is present",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run internal checker tests instead of reading repository files",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    try:
        return validate_state(require_closed=args.require_closed)
    except FileNotFoundError as exc:
        print("PHASE1_RBTREE_ALIAS_SURFACE=fail")
        print(f"PHASE1_RBTREE_ALIAS_REASON=missing_file:{exc.filename}")
        return 1
    except ValueError as exc:
        print("PHASE1_RBTREE_ALIAS_SURFACE=fail")
        print(f"PHASE1_RBTREE_ALIAS_REASON={exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
