#!/usr/bin/env python3
"""Guard the Phase 1 rbtree direct-anchor packet against helper-local drift."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
RBTREE_REL = Path("tools/lib/rbtree.zig")

REQUIRED_TEST_MARKERS = {
    "ordered_alias_anchor": 'test "rbtree ordered Linux-style aliases mirror traversal and replacement helpers" {',
    "low_level_alias_anchor": 'test "rbtree low-level Linux-style aliases mirror node-state helpers" {',
    "cached_add_leftmost": 'test "rbtree addCached returns the inserted node only when it becomes leftmost" {',
    "cached_find_add_leftmost": 'test "rbtree findAddCached keeps cached leftmost stable while inserting misses" {',
    "cached_leftmost_sync": 'test "rbtree cached root keeps the leftmost pointer in sync" {',
    "cached_root_alias_anchor": 'test "rbtree cached-root Linux-style aliases mirror the primary helpers" {',
    "cached_replace_non_leftmost": 'test "rbtree replaceNodeCached keeps non-leftmost leftmost unchanged" {',
    "cached_singleton_erase": 'test "rbtree eraseCached returns null for a singleton cached tree" {',
    "cached_detach": 'test "rbtree eraseInitCached detaches nodes while keeping cached leftmost aligned" {',
    "cached_reseed": 'test "rbtree eraseInitCached clears singleton cached roots before reseed" {',
}

REQUIRED_SOURCE_MARKERS = {
    "insert_color_cached": "pub fn insertColorCached(node: *Node, root: *RootCached, leftmost: bool) void {",
    "rb_insert_color_cached": "pub fn rb_insert_color_cached(node: *Node, root: *RootCached, leftmost: bool) void {",
    "add_cached": "pub fn addCached(node: *Node, root: *RootCached, less: LessFn) ?*Node {",
    "rb_add_cached": "pub fn rb_add_cached(node: *Node, root: *RootCached, less: LessFn) ?*Node {",
    "find_add_cached": "pub fn findAddCached(node: *Node, root: *RootCached, cmp: CmpNodeFn) ?*Node {",
    "rb_find_add_cached": "pub fn rb_find_add_cached(node: *Node, root: *RootCached, cmp: CmpNodeFn) ?*Node {",
    "erase_cached": "pub fn eraseCached(node: *Node, root: *RootCached) ?*Node {",
    "rb_erase_cached": "pub fn rb_erase_cached(node: *Node, root: *RootCached) ?*Node {",
    "erase_init_cached": "pub fn eraseInitCached(node: *Node, root: *RootCached) void {",
    "rb_erase_init_cached": "pub fn rb_erase_init_cached(node: *Node, root: *RootCached) void {",
    "first_cached": "pub fn firstCached(root: *const RootCached) ?*Node {",
    "rb_first_cached": "pub fn rb_first_cached(root: *const RootCached) ?*Node {",
    "replace_node_cached": "pub fn replaceNodeCached(victim: *Node, new: *Node, root: *RootCached) void {",
    "rb_replace_node_cached": "pub fn rb_replace_node_cached(victim: *Node, new: *Node, root: *RootCached) void {",
}


def repo_root(override: str | None) -> Path:
    return Path(override).resolve() if override else DEFAULT_ROOT.resolve()


def collect_marker_count_failures(text: str, markers: dict[str, str]) -> list[str]:
    failures: list[str] = []
    for label, marker in markers.items():
        count = text.count(marker)
        if count != 1:
            failures.append(f"{label}:expected=1:actual={count}")
    return failures


def validate_rbtree_source(text: str) -> tuple[str, object]:
    test_failures = collect_marker_count_failures(text, REQUIRED_TEST_MARKERS)
    if test_failures:
        return ("invalid_test_marker_counts", test_failures)

    source_failures = collect_marker_count_failures(text, REQUIRED_SOURCE_MARKERS)
    if source_failures:
        return ("invalid_source_marker_counts", source_failures)

    return ("pass", None)


def load_rbtree_source(root: Path) -> tuple[str, object]:
    path = root / RBTREE_REL
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ("missing_file", path)
    return validate_rbtree_source(text)


def build_sample_source(omit_label: str | None = None, duplicate_label: str | None = None) -> str:
    lines = list(REQUIRED_TEST_MARKERS.values()) + list(REQUIRED_SOURCE_MARKERS.values())

    if omit_label is not None:
        marker = REQUIRED_TEST_MARKERS.get(omit_label, REQUIRED_SOURCE_MARKERS.get(omit_label))
        assert marker is not None
        lines = [line for line in lines if line != marker]

    if duplicate_label is not None:
        marker = REQUIRED_TEST_MARKERS.get(duplicate_label, REQUIRED_SOURCE_MARKERS.get(duplicate_label))
        assert marker is not None
        for idx, line in enumerate(lines):
            if line == marker:
                lines.insert(idx + 1, line)
                break

    return "\n".join(lines) + "\n"


def run_self_test() -> None:
    case_count = 0

    kind, payload = validate_rbtree_source(build_sample_source())
    assert kind == "pass", (kind, payload)
    case_count += 1

    for label in REQUIRED_TEST_MARKERS:
        kind, payload = validate_rbtree_source(build_sample_source(omit_label=label))
        assert kind == "invalid_test_marker_counts", (label, kind, payload)
        assert payload == [f"{label}:expected=1:actual=0"], (label, payload)
        case_count += 1

    for label in REQUIRED_SOURCE_MARKERS:
        kind, payload = validate_rbtree_source(build_sample_source(omit_label=label))
        assert kind == "invalid_source_marker_counts", (label, kind, payload)
        assert payload == [f"{label}:expected=1:actual=0"], (label, payload)
        case_count += 1

    for label in REQUIRED_TEST_MARKERS:
        kind, payload = validate_rbtree_source(build_sample_source(duplicate_label=label))
        assert kind == "invalid_test_marker_counts", (label, kind, payload)
        assert payload == [f"{label}:expected=1:actual=2"], (label, payload)
        case_count += 1

    for label in REQUIRED_SOURCE_MARKERS:
        kind, payload = validate_rbtree_source(build_sample_source(duplicate_label=label))
        assert kind == "invalid_source_marker_counts", (label, kind, payload)
        assert payload == [f"{label}:expected=1:actual=2"], (label, payload)
        case_count += 1

    with tempfile.TemporaryDirectory(prefix="phase1-rbtree-direct-anchors-") as tmp:
        root = Path(tmp)
        kind, payload = load_rbtree_source(root)
        assert kind == "missing_file", (kind, payload)
        assert payload == root / RBTREE_REL
        case_count += 1

        path = root / RBTREE_REL
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(build_sample_source(), encoding="utf-8")
        kind, payload = load_rbtree_source(root)
        assert kind == "pass", (kind, payload)
        case_count += 1

    print("PHASE1_RBTREE_DIRECT_ANCHORS_SELF_TEST=pass")
    print(f"PHASE1_RBTREE_DIRECT_ANCHORS_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run self-test cases")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    kind, payload = load_rbtree_source(repo_root(args.root))
    if kind != "pass":
        print("PHASE1_RBTREE_DIRECT_ANCHORS=fail")
        if isinstance(payload, list):
            print("PHASE1_RBTREE_DIRECT_ANCHORS_REASON=" + kind)
            for failure in payload:
                print(failure)
        else:
            print(f"PHASE1_RBTREE_DIRECT_ANCHORS_REASON={kind}")
            print(payload)
        return 1

    print("PHASE1_RBTREE_DIRECT_ANCHORS=pass")
    print(f"PHASE1_RBTREE_DIRECT_ANCHORS_HELPER={RBTREE_REL.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())