#!/usr/bin/env python3
"""Guard the Phase 1 rbtree review packet against helper, fixture, manifest, and lane-note drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
HELPER_REL = Path("tools/lib/rbtree.zig")
LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
FIXTURE_REL = Path("zigux/tests/fixtures/phase1_helpers.json")

EXPECTED_SOURCE_SYMBOLS = [
    "pub fn insertColorCached(node: *Node, root: *RootCached, leftmost: bool) void {",
    "pub fn rb_insert_color_cached(node: *Node, root: *RootCached, leftmost: bool) void {",
    "pub fn addCached(node: *Node, root: *RootCached, less: LessFn) ?*Node {",
    "pub fn rb_add_cached(node: *Node, root: *RootCached, less: LessFn) ?*Node {",
    "pub fn find(key: *const anyopaque, root: *const Root, cmp: CmpKeyFn) ?*Node {",
    "pub fn rb_find(key: *const anyopaque, root: *const Root, cmp: CmpKeyFn) ?*Node {",
    "pub fn findFirst(key: *const anyopaque, root: *const Root, cmp: CmpKeyFn) ?*Node {",
    "pub fn rb_find_first(key: *const anyopaque, root: *const Root, cmp: CmpKeyFn) ?*Node {",
    "pub fn nextMatch(key: *const anyopaque, node: *const Node, cmp: CmpKeyFn) ?*Node {",
    "pub fn rb_next_match(key: *const anyopaque, node: *const Node, cmp: CmpKeyFn) ?*Node {",
    "pub fn matchIterator(key: *const anyopaque, root: *const Root, cmp: CmpKeyFn) MatchIterator {",
    "pub fn rb_match_iterator(key: *const anyopaque, root: *const Root, cmp: CmpKeyFn) MatchIterator {",
    "pub fn findAddCached(node: *Node, root: *RootCached, cmp: CmpNodeFn) ?*Node {",
    "pub fn rb_find_add_cached(node: *Node, root: *RootCached, cmp: CmpNodeFn) ?*Node {",
    "pub fn eraseCached(node: *Node, root: *RootCached) ?*Node {",
    "pub fn rb_erase_cached(node: *Node, root: *RootCached) ?*Node {",
    "pub fn firstCached(root: *const RootCached) ?*Node {",
    "pub fn rb_first_cached(root: *const RootCached) ?*Node {",
    "pub fn replaceNodeCached(victim: *Node, new: *Node, root: *RootCached) void {",
    "pub fn rb_replace_node_cached(victim: *Node, new: *Node, root: *RootCached) void {",
    "pub fn eraseInitCached(node: *Node, root: *RootCached) void {",
    "pub fn rb_erase_init_cached(node: *Node, root: *RootCached) void {",
]

EXPECTED_HELPER_TEST_ANCHORS = [
    'test "rbtree inserts and traverses in sorted order"',
    'test "rbtree erase and replace keep traversal consistent"',
    'test "rbtree ordered Linux-style aliases mirror traversal and replacement helpers"',
    'test "rbtree low-level Linux-style aliases mirror node-state helpers"',
    'test "rbtree eraseInit detaches erased node"',
    'test "rbtree eraseInit clears singleton roots before reseed"',
    'test "rbtree postorder and empty node helpers behave"',
    'test "rbtree findAdd keeps the first duplicate and inserts new keys"',
    'test "rbtree nextMatch walks the duplicate range in order"',
    'test "rbtree matchIterator walks the duplicate range in order"',
    'test "rbtree addCached returns the inserted node only when it becomes leftmost"',
    'test "rbtree findAddCached keeps cached leftmost stable while inserting misses"',
    'test "rbtree cached root keeps the leftmost pointer in sync"',
    'test "rbtree cached-root Linux-style aliases mirror the primary helpers"',
    'test "rbtree replaceNodeCached keeps non-leftmost leftmost unchanged"',
    'test "rbtree eraseCached returns null for a singleton cached tree"',
    'test "rbtree eraseInitCached detaches nodes while keeping cached leftmost aligned"',
    'test "rbtree eraseInitCached clears singleton cached roots before reseed"',
]

EXPECTED_LANE_LINES = [
    "- `tools/lib/rbtree.zig` now keeps ordered Linux-style alias, low-level Linux-style alias, cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed coverage helper-local while the committed fixture still owns exact `find()`, `findFirst()`, `nextMatch()`, and `matchIterator()` duplicate-search fields and the shared host-tools smoke route already keeps duplicate-range iteration plus the parked `cached_leftmost_return_serials` witness explicit. The dedicated `low_level_alias_anchor` in `zigux/tests/fixtures/phase1_helper_manifest.json` also keeps the low-level Linux-style alias proof named explicitly inside that same helper-local packet instead of leaving it implied only by the broader helper test list. Until another committed cached-root replay field lands, leave the remaining cached-root anchors helper-local and do not batch a second widening into the same reopen step.",
    "- `PHASE1_RBTREE_DIRECT_OWNER=rbtree keeps ordered Linux-style alias, low-level Linux-style alias, cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed anchors helper-local while the committed fixture still owns exact find(), findFirst(), nextMatch(), and matchIterator() duplicate-search fields and the shared host-tools smoke route keeps duplicate-range iteration plus the parked cached_leftmost_return_serials witness explicit`",
    "- `PHASE1_RBTREE_NEXT_SAFE_STEP=rbtree reopens only to keep the already-landed cached_leftmost_return_serials shared replay aligned across the manifest, direct-owner note, and any shared parity gates, or for drift inside the still-helper-local cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed anchors; do not batch a second widening into the same run`",
]

EXPECTED_MANIFEST_PACKET = {
    "helper_test_anchors": EXPECTED_HELPER_TEST_ANCHORS,
    "phase1_helper_replay_anchor": 'test "phase1 host-tools smoke exercises live helper behavior"',
    "parity_fixture_keys": [
        "empty_root",
        "insert_order",
        "reverse_order",
        "replace_order",
        "erase_init_order",
        "postorder_count",
        "erase_init_node_empty",
        "cleared_node_empty",
        "find_found_key",
        "find_missing",
        "find_first_serial",
        "next_match_serials",
        "match_iterator_serials",
        "next_match_terminal_null",
    ],
    "cached_leftmost_fixture_keys": ["cached_leftmost_return_serials"],
    "shared_replay_summary": "the committed Phase 1 fixture still carries traversal, detached-node, duplicate-search, and exact cached-leftmost-return witnesses for rbtree, while the current shared host-tools smoke replay now rechecks duplicate-range iteration plus the exact `cached_leftmost_return_serials` cached-root leftmost-return sequence on current master",
    "traversal_replay_keys": [
        "empty_root",
        "insert_order",
        "reverse_order",
        "replace_order",
        "erase_init_order",
        "postorder_count",
        "erase_init_node_empty",
        "cleared_node_empty",
    ],
    "duplicate_search_replay_keys": [
        "find_found_key",
        "find_missing",
        "find_first_serial",
        "next_match_serials",
        "match_iterator_serials",
        "next_match_terminal_null",
    ],
    "cached_root_direct_review_summary": "cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed behavior remain owned by direct helper-local anchors, while the exact `cached_leftmost_return_serials` witness now stays aligned across the helper-local tests, the shared host-tools smoke replay, and the committed fixture",
    "ordered_alias_anchor": 'test "rbtree ordered Linux-style aliases mirror traversal and replacement helpers"',
    "low_level_alias_anchor": 'test "rbtree low-level Linux-style aliases mirror node-state helpers"',
    "duplicate_search_anchors": [
        'test "rbtree findAdd keeps the first duplicate and inserts new keys"',
        'test "rbtree nextMatch walks the duplicate range in order"',
        'test "rbtree matchIterator walks the duplicate range in order"',
    ],
    "cached_root_followup_anchors": [
        'test "rbtree addCached returns the inserted node only when it becomes leftmost"',
        'test "rbtree findAddCached keeps cached leftmost stable while inserting misses"',
        'test "rbtree cached root keeps the leftmost pointer in sync"',
        'test "rbtree cached-root Linux-style aliases mirror the primary helpers"',
        'test "rbtree replaceNodeCached keeps non-leftmost leftmost unchanged"',
        'test "rbtree eraseCached returns null for a singleton cached tree"',
        'test "rbtree eraseInitCached detaches nodes while keeping cached leftmost aligned"',
        'test "rbtree eraseInitCached clears singleton cached roots before reseed"',
    ],
    "cached_root_alias_anchor": 'test "rbtree cached-root Linux-style aliases mirror the primary helpers"',
    "review_packet_summary": "the current shared host-tools smoke replay keeps duplicate-range iteration and the exact `cached_leftmost_return_serials` cached-root leftmost-return witness visible for rbtree, while the committed Phase 1 fixture still carries the exact traversal, detached-node, duplicate-search, and cached-leftmost-return witnesses; direct helper-local anchors continue to own cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed paths that the shared smoke route does not replay exactly",
    "next_safe_step_note": "If this helper lane reopens, keep the already-landed shared-replay promotion for `cached_leftmost_return_serials` aligned across the committed fixture, shared replay, and direct cached-root anchors; the ordered Linux-style alias proof, dedicated `low_level_alias_anchor`, and the remaining cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed behavior stay owned by direct helper-local anchors until another committed cached-root field lands.",
}

EXPECTED_FIXTURE_VALUES = {
    "empty_root": True,
    "insert_order": [5, 10, 15, 20, 25],
    "reverse_order": [25, 20, 15, 10, 5],
    "replace_order": [5, 10, 15, 25],
    "erase_init_order": [5, 15, 25],
    "postorder_count": 3,
    "erase_init_node_empty": True,
    "cleared_node_empty": True,
    "find_found_key": 15,
    "find_missing": True,
    "find_first_serial": 0,
    "next_match_serials": [0, 2, 4],
    "match_iterator_serials": [0, 2, 4],
    "cached_leftmost_return_serials": [0, -1, 2, -1],
    "next_match_terminal_null": True,
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json(root: Path, relative_path: Path) -> Any:
    return json.loads(load_text(root, relative_path))


def require_exact_occurrence(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    if count != 1:
        return [f"{label}:expected=1:actual={count}"]
    return []


def require_exact_value(label: str, actual: Any, expected: Any) -> list[str]:
    return [] if actual == expected else [f"{label}:expected_current_packet"]


def nested_value(data: object, path: tuple[str, ...]) -> object:
    current = data
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for relative_path in (HELPER_REL, LANE_NOTE_REL, MANIFEST_REL, FIXTURE_REL):
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    helper_text = load_text(root, HELPER_REL)
    lane_text = load_text(root, LANE_NOTE_REL)
    manifest = load_json(root, MANIFEST_REL)
    fixture = load_json(root, FIXTURE_REL)

    for symbol in EXPECTED_SOURCE_SYMBOLS:
        failures.extend(require_exact_occurrence(helper_text, f"helper_symbol:{symbol}", symbol))

    for anchor in EXPECTED_HELPER_TEST_ANCHORS:
        failures.extend(require_exact_occurrence(helper_text, f"helper_anchor:{anchor}", anchor))

    for lane_line in EXPECTED_LANE_LINES:
        failures.extend(require_exact_occurrence(lane_text, f"lane_line:{lane_line}", lane_line))

    for field, expected in EXPECTED_MANIFEST_PACKET.items():
        failures.extend(
            require_exact_value(
                f"manifest:{field}",
                nested_value(manifest, ("review_anchors", "tools/lib/rbtree.zig", field)),
                expected,
            )
        )

    rbtree_fixture = fixture.get("rbtree") if isinstance(fixture, dict) else None
    if not isinstance(rbtree_fixture, dict):
        return ["fixture:rbtree"]

    for field, expected in EXPECTED_FIXTURE_VALUES.items():
        failures.extend(require_exact_value(f"fixture:{field}", rbtree_fixture.get(field), expected))

    return failures


def write_text(root: Path, relative_path: Path, text: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    helper_text = "\n".join(EXPECTED_SOURCE_SYMBOLS + [""] + EXPECTED_HELPER_TEST_ANCHORS) + "\n"
    write_text(root, HELPER_REL, helper_text)
    write_text(root, LANE_NOTE_REL, "# sample\n\n" + "\n".join(EXPECTED_LANE_LINES) + "\n")
    write_text(
        root,
        MANIFEST_REL,
        json.dumps({"review_anchors": {"tools/lib/rbtree.zig": EXPECTED_MANIFEST_PACKET}}, indent=2) + "\n",
    )
    write_text(root, FIXTURE_REL, json.dumps({"rbtree": EXPECTED_FIXTURE_VALUES}, indent=2) + "\n")


def run_self_test() -> int:
    cases = [
        ("missing_helper", "missing_file:tools/lib/rbtree.zig"),
        ("missing_lane_line", f"lane_line:{EXPECTED_LANE_LINES[1]}:expected=1:actual=0"),
        ("missing_symbol", f"helper_symbol:{EXPECTED_SOURCE_SYMBOLS[0]}:expected=1:actual=0"),
        ("missing_anchor", f"helper_anchor:{EXPECTED_HELPER_TEST_ANCHORS[5]}:expected=1:actual=0"),
        ("manifest_drift", "manifest:review_packet_summary:expected_current_packet"),
        ("fixture_drift", "fixture:cached_leftmost_return_serials:expected_current_packet"),
        ("duplicate_anchor", f"helper_anchor:{EXPECTED_HELPER_TEST_ANCHORS[5]}:expected=1:actual=2"),
    ]

    with tempfile.TemporaryDirectory(prefix="zigux_phase1_rbtree_review_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        if cases[0][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-rbtree-review:self-test:missing_helper")

        build_sample_repo(tmp_root)
        if collect_failures(tmp_root):
            raise SystemExit("phase1-rbtree-review:self-test:baseline")

        lane_text = load_text(tmp_root, LANE_NOTE_REL).replace(EXPECTED_LANE_LINES[1] + "\n", "", 1)
        write_text(tmp_root, LANE_NOTE_REL, lane_text)
        if cases[1][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-rbtree-review:self-test:missing_lane_line")

        build_sample_repo(tmp_root)
        helper_text = load_text(tmp_root, HELPER_REL).replace(EXPECTED_SOURCE_SYMBOLS[0] + "\n", "", 1)
        write_text(tmp_root, HELPER_REL, helper_text)
        if cases[2][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-rbtree-review:self-test:missing_symbol")

        build_sample_repo(tmp_root)
        helper_text = load_text(tmp_root, HELPER_REL).replace(EXPECTED_HELPER_TEST_ANCHORS[5] + "\n", "", 1)
        write_text(tmp_root, HELPER_REL, helper_text)
        if cases[3][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-rbtree-review:self-test:missing_anchor")

        build_sample_repo(tmp_root)
        manifest = load_json(tmp_root, MANIFEST_REL)
        manifest["review_anchors"]["tools/lib/rbtree.zig"]["review_packet_summary"] = "drift"
        write_text(tmp_root, MANIFEST_REL, json.dumps(manifest, indent=2) + "\n")
        if cases[4][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-rbtree-review:self-test:manifest_drift")

        build_sampleRepo = build_sample_repo
        build_sampleRepo(tmp_root)
        fixture = load_json(tmp_root, FIXTURE_REL)
        fixture["rbtree"]["cached_leftmost_return_serials"] = [0, -1, 2]
        write_text(tmp_root, FIXTURE_REL, json.dumps(fixture, indent=2) + "\n")
        if cases[5][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-rbtree-review:self-test:fixture_drift")

        build_sampleRepo(tmp_root)
        helper_text = load_text(tmp_root, HELPER_REL)
        duplicated = EXPECTED_HELPER_TEST_ANCHORS[5]
        helper_text = helper_text.replace(duplicated + "\n", duplicated + "\n" + duplicated + "\n", 1)
        write_text(tmp_root, HELPER_REL, helper_text)
        if cases[6][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-rbtree-review:self-test:duplicate_anchor")

    print("PHASE1_RBTREE_REVIEW_PACKET_SELF_TEST=pass")
    print("PHASE1_RBTREE_REVIEW_PACKET_SELF_TEST_CASE_COUNT=7")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="Repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="Run checker self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_RBTREE_REVIEW_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_RBTREE_REVIEW_PACKET=pass")
    print(f"PHASE1_RBTREE_REVIEW_PACKET_HELPER={HELPER_REL.as_posix()}")
    print(f"PHASE1_RBTREE_REVIEW_PACKET_MANIFEST={MANIFEST_REL.as_posix()}")
    print(f"PHASE1_RBTREE_REVIEW_PACKET_FIXTURE={FIXTURE_REL.as_posix()}")
    print(f"PHASE1_RBTREE_REVIEW_PACKET_LANE_NOTE={LANE_NOTE_REL.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
