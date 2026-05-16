#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent


REQUIRED_FILES = [
    "zigux/tests/phase7_rbtree_manifest.json",
    "lib/rbtree.zig",
]


REQUIRED_MARKERS = {
    "zigux/tests/phase7_rbtree_manifest.json": [
        '"linked-node teardown reconnects prev and next ownership together with leftmost continuity during eraseLinked()"',
        '"replaceNode() copies victim links onto replacement nodes before reconnecting parent and child ownership"',
        '"postorder traversal helpers treat cleared detached nodes as empty so stale parent walks do not leak past the reusable leaf packet"',
    ],
    "lib/rbtree.zig": [
        "pub fn eraseLinked(node: *NodeLinked, root: *RootLinked) bool {",
        "prev_link.next = node.next;",
        "root.leftmost = node.next;",
        "next_link.prev = node.prev;",
        "clearLinkedNode(node);",
        'test "rbtree linked helpers track leftmost and neighbour links" {',
        "try std.testing.expectEqual(@as(?*NodeLinked, &entries[2].linked), root.leftmost);",
        "try std.testing.expectEqual(@as(?*NodeLinked, &entries[0].linked), entries[2].linked.next);",
        "try std.testing.expectEqual(@as(?*NodeLinked, &entries[2].linked), entries[0].linked.prev);",
        "pub fn replaceNode(victim: *Node, new: *Node, root: *Root) void {",
        "new.* = victim.*;",
        "left.parent = new;",
        "right.parent = new;",
        "pub fn replaceNodeCached(victim: *Node, new: *Node, root: *RootCached) void {",
        "if (root.leftmost == victim) {",
        "root.leftmost = new;",
        'test "rbtree replaceNode copies victim links over dirty replacement nodes" {',
        "try std.testing.expectEqual(@as(?*Node, &replacement.node), prev(&root_entry.node));",
        "try std.testing.expectEqual(@as(?*Node, &root_entry.node), next(&replacement.node));",
        'test "rbtree replaceNodeCached keeps singleton cached roots aligned over dirty replacement nodes" {',
        "pub fn firstPostorder(root: *const Root) ?*Node {",
        "pub fn nextPostorder(node: ?*const Node) ?*Node {",
        "if (emptyNode(current)) {",
        "return leftDeepestNode(parent.?.right.?);",
        "return parent;",
    ],
}


def collect_missing_files(root: Path) -> list[str]:
    return [rel for rel in REQUIRED_FILES if not (root / rel).exists()]


def collect_missing_markers(root: Path) -> list[str]:
    missing: list[str] = []
    for rel, markers in REQUIRED_MARKERS.items():
        text = (root / rel).read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                missing.append(f"{rel}: {marker}")
    return missing


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return missing_files, []
    return [], collect_missing_markers(root)


def write_fixture_root(tmp_root: Path) -> None:
    fixture_text = {rel: "\n".join(markers) + "\n" for rel, markers in REQUIRED_MARKERS.items()}
    for rel in REQUIRED_FILES:
        path = tmp_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(fixture_text[rel], encoding="utf-8")


def expect_missing_file(case: str, tmp_root: Path, rel: str) -> None:
    missing_files, missing_markers = validate(tmp_root)
    assert missing_markers == [], case
    assert missing_files == [rel], case


def expect_missing_marker(case: str, tmp_root: Path, marker: str) -> None:
    missing_files, missing_markers = validate(tmp_root)
    assert missing_files == [], case
    assert missing_markers == [marker], case


def mutate_file(tmp_root: Path, rel: str, old: str, new: str, case: str) -> None:
    path = tmp_root / rel
    original = path.read_text(encoding="utf-8")
    updated = original.replace(old, new, 1)
    assert updated != original, case
    path.write_text(updated, encoding="utf-8")


def run_self_test() -> None:
    missing_file_cases = [
        ("missing_manifest", "zigux/tests/phase7_rbtree_manifest.json"),
        ("missing_helper", "lib/rbtree.zig"),
    ]

    marker_cases = [
        (
            "manifest_linked_ownership_marker",
            "zigux/tests/phase7_rbtree_manifest.json",
            '"linked-node teardown reconnects prev and next ownership together with leftmost continuity during eraseLinked()"',
            "",
            'zigux/tests/phase7_rbtree_manifest.json: "linked-node teardown reconnects prev and next ownership together with leftmost continuity during eraseLinked()"',
        ),
        (
            "manifest_replace_marker",
            "zigux/tests/phase7_rbtree_manifest.json",
            '"replaceNode() copies victim links onto replacement nodes before reconnecting parent and child ownership"',
            "",
            'zigux/tests/phase7_rbtree_manifest.json: "replaceNode() copies victim links onto replacement nodes before reconnecting parent and child ownership"',
        ),
        (
            "manifest_postorder_marker",
            "zigux/tests/phase7_rbtree_manifest.json",
            '"postorder traversal helpers treat cleared detached nodes as empty so stale parent walks do not leak past the reusable leaf packet"',
            "",
            'zigux/tests/phase7_rbtree_manifest.json: "postorder traversal helpers treat cleared detached nodes as empty so stale parent walks do not leak past the reusable leaf packet"',
        ),
        (
            "helper_erase_prev_link_marker",
            "lib/rbtree.zig",
            "prev_link.next = node.next;",
            "",
            "lib/rbtree.zig: prev_link.next = node.next;",
        ),
        (
            "helper_erase_leftmost_marker",
            "lib/rbtree.zig",
            "root.leftmost = node.next;",
            "",
            "lib/rbtree.zig: root.leftmost = node.next;",
        ),
        (
            "helper_erase_next_link_marker",
            "lib/rbtree.zig",
            "next_link.prev = node.prev;",
            "",
            "lib/rbtree.zig: next_link.prev = node.prev;",
        ),
        (
            "helper_linked_test_marker",
            "lib/rbtree.zig",
            'test "rbtree linked helpers track leftmost and neighbour links" {',
            "",
            'lib/rbtree.zig: test "rbtree linked helpers track leftmost and neighbour links" {',
        ),
        (
            "helper_linked_leftmost_assert_marker",
            "lib/rbtree.zig",
            "try std.testing.expectEqual(@as(?*NodeLinked, &entries[2].linked), root.leftmost);",
            "",
            "lib/rbtree.zig: try std.testing.expectEqual(@as(?*NodeLinked, &entries[2].linked), root.leftmost);",
        ),
        (
            "helper_replace_copy_marker",
            "lib/rbtree.zig",
            "new.* = victim.*;",
            "",
            "lib/rbtree.zig: new.* = victim.*;",
        ),
        (
            "helper_replace_parent_fixup_marker",
            "lib/rbtree.zig",
            "left.parent = new;",
            "",
            "lib/rbtree.zig: left.parent = new;",
        ),
        (
            "helper_replace_sibling_fixup_marker",
            "lib/rbtree.zig",
            "right.parent = new;",
            "",
            "lib/rbtree.zig: right.parent = new;",
        ),
        (
            "helper_replace_test_marker",
            "lib/rbtree.zig",
            'test "rbtree replaceNode copies victim links over dirty replacement nodes" {',
            "",
            'lib/rbtree.zig: test "rbtree replaceNode copies victim links over dirty replacement nodes" {',
        ),
        (
            "helper_replace_cached_leftmost_marker",
            "lib/rbtree.zig",
            "if (root.leftmost == victim) {",
            "",
            "lib/rbtree.zig: if (root.leftmost == victim) {",
        ),
        (
            "helper_replace_cached_assign_marker",
            "lib/rbtree.zig",
            "root.leftmost = new;",
            "",
            "lib/rbtree.zig: root.leftmost = new;",
        ),
        (
            "helper_postorder_empty_marker",
            "lib/rbtree.zig",
            "if (emptyNode(current)) {",
            "",
            "lib/rbtree.zig: if (emptyNode(current)) {",
        ),
        (
            "helper_postorder_right_branch_marker",
            "lib/rbtree.zig",
            "return leftDeepestNode(parent.?.right.?);",
            "",
            "lib/rbtree.zig: return leftDeepestNode(parent.?.right.?);",
        ),
    ]

    with tempfile.TemporaryDirectory(prefix="zigux_phase7_rbtree_ownership_focus_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        write_fixture_root(tmp_root)
        assert validate(tmp_root) == ([], [])

        for case, rel in missing_file_cases:
            (tmp_root / rel).unlink()
            expect_missing_file(case, tmp_root, rel)
            write_fixture_root(tmp_root)

        for case, rel, old, new, expected in marker_cases:
            mutate_file(tmp_root, rel, old, new, case)
            expect_missing_marker(case, tmp_root, expected)
            write_fixture_root(tmp_root)

        case_count = len(missing_file_cases) + len(marker_cases)
        print("PHASE7_RBTREE_OWNERSHIP_FOCUS_SELF_TEST=pass")
        print(f"PHASE7_RBTREE_OWNERSHIP_FOCUS_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed on concrete Phase 7 rbtree ownership-focus markers."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run checker self-tests without reading repo files.",
    )
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    missing_files, missing_markers = validate(ROOT)
    if missing_files:
        print("PHASE7_RBTREE_OWNERSHIP_FOCUS=fail")
        print("MISSING_PHASE7_RBTREE_OWNERSHIP_FOCUS_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE7_RBTREE_OWNERSHIP_FOCUS_FILES_END")
        return 1

    if missing_markers:
        print("PHASE7_RBTREE_OWNERSHIP_FOCUS=fail")
        print("MISSING_PHASE7_RBTREE_OWNERSHIP_FOCUS_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE7_RBTREE_OWNERSHIP_FOCUS_MARKERS_END")
        return 1

    print("PHASE7_RBTREE_OWNERSHIP_FOCUS=pass")
    print(f"PHASE7_RBTREE_OWNERSHIP_FOCUS_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE7_RBTREE_OWNERSHIP_FOCUS_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
