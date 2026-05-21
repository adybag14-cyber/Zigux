#!/usr/bin/env python3
"""Guard the Phase 1 rbtree review packet against helper, manifest, fixture, and lane-note drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[3] if len(HERE.parents) > 3 else HERE.parent
RBTREE_HELPER_REL = Path("tools/lib/rbtree.zig")
RBTREE_MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
RBTREE_FIXTURE_REL = Path("zigux/tests/fixtures/phase1_helpers.json")
RBTREE_LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")

EXPECTED_RBTREE_SOURCE_SYMBOLS = [
    "pub fn addCached(node: *Node, root: *RootCached, less: LessFn) ?*Node {",
    "pub fn rb_add_cached(node: *Node, root: *RootCached, less: LessFn) ?*Node {",
    "pub fn findAdd(node: *Node, root: *Root, cmp: CmpNodeFn) ?*Node {",
    "pub fn rb_find_add(node: *Node, root: *Root, cmp: CmpNodeFn) ?*Node {",
    "pub fn findAddCached(node: *Node, root: *RootCached, cmp: CmpNodeFn) ?*Node {",
    "pub fn rb_find_add_cached(node: *Node, root: *RootCached, cmp: CmpNodeFn) ?*Node {",
    "pub fn find(key: *const anyopaque, root: *const Root, cmp: CmpKeyFn) ?*Node {",
    "pub fn rb_find(key: *const anyopaque, root: *const Root, cmp: CmpKeyFn) ?*Node {",
    "pub fn findFirst(key: *const anyopaque, root: *const Root, cmp: CmpKeyFn) ?*Node {",
    "pub fn rb_find_first(key: *const anyopaque, root: *const Root, cmp: CmpKeyFn) ?*Node {",
    "pub fn nextMatch(key: *const anyopaque, node: *const Node, cmp: CmpKeyFn) ?*Node {",
    "pub fn rb_next_match(key: *const anyopaque, node: *const Node, cmp: CmpKeyFn) ?*Node {",
    "pub fn matchIterator(key: *const anyopaque, root: *const Root, cmp: CmpKeyFn) MatchIterator {",
    "pub fn rb_match_iterator(key: *const anyopaque, root: *const Root, cmp: CmpKeyFn) MatchIterator {",
    "pub fn eraseCached(node: *Node, root: *RootCached) ?*Node {",
    "pub fn rb_erase_cached(node: *Node, root: *RootCached) ?*Node {",
    "pub fn eraseInitCached(node: *Node, root: *RootCached) void {",
    "pub fn rb_erase_init_cached(node: *Node, root: *RootCached) void {",
    "pub fn firstCached(root: *const RootCached) ?*Node {",
    "pub fn rb_first_cached(root: *const RootCached) ?*Node {",
    "pub fn replaceNodeCached(victim: *Node, new: *Node, root: *RootCached) void {",
    "pub fn rb_replace_node_cached(victim: *Node, new: *Node, root: *RootCached) void {",
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

EXPECTED_RBTREE_PACKET = {
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
    "cached_leftmost_fixture_keys": [
        "cached_leftmost_return_serials",
    ],
    "shared_replay_summary": (
        "the committed Phase 1 fixture still carries traversal, detached-node, duplicate-search, "
        "and exact cached-leftmost-return witnesses for rbtree, while the current shared host-tools "
        "smoke replay now rechecks duplicate-range iteration plus the exact "
        "`cached_leftmost_return_serials` cached-root leftmost-return sequence on current master"
    ),
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
    "cached_root_direct_review_summary": (
        "cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, "
        "detach, and reseed behavior remain owned by direct helper-local anchors, while the exact "
        "`cached_leftmost_return_serials` witness now stays aligned across the helper-local tests, "
        "the shared host-tools smoke replay, and the committed fixture"
    ),
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
    "review_packet_summary": (
        "the current shared host-tools smoke replay keeps duplicate-range iteration and the exact "
        "`cached_leftmost_return_serials` cached-root leftmost-return witness visible for rbtree, "
        "while the committed Phase 1 fixture still carries the exact traversal, detached-node, "
        "duplicate-search, and cached-leftmost-return witnesses; direct helper-local anchors continue "
        "to own cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, "
        "replacement, detach, and reseed paths that the shared smoke route does not replay exactly"
    ),
    "next_safe_step_note": (
        "If this helper lane reopens, keep the already-landed shared-replay promotion for "
        "`cached_leftmost_return_serials` aligned across the committed fixture, shared replay, and "
        "direct cached-root anchors; the ordered Linux-style alias proof, dedicated "
        "`low_level_alias_anchor`, and the remaining cached-root insert-miss, leftmost-sync, "
        "cached-root alias, singleton-erase, replacement, detach, and reseed behavior stay owned by "
        "direct helper-local anchors until another committed cached-root field lands."
    ),
}

EXPECTED_RBTREE_FIXTURE_VALUES = {
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

EXPECTED_RBTREE_LANE_MARKERS = [
    (
        "lane_direct_owner",
        "`PHASE1_RBTREE_DIRECT_OWNER=rbtree keeps ordered Linux-style alias, low-level Linux-style "
        "alias, cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, "
        "replacement, detach, and reseed anchors helper-local while the committed fixture still owns "
        "exact find(), findFirst(), nextMatch(), and matchIterator() duplicate-search fields and the "
        "shared host-tools smoke route keeps duplicate-range iteration plus the parked "
        "cached_leftmost_return_serials witness explicit`",
    ),
    (
        "lane_next_safe_step",
        "`PHASE1_RBTREE_NEXT_SAFE_STEP=rbtree reopens only to keep the already-landed "
        "cached_leftmost_return_serials shared replay aligned across the manifest, direct-owner "
        "note, and any shared parity gates, or for drift inside the still-helper-local cached-root "
        "insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and "
        "reseed anchors; do not batch a second widening into the same run`",
    ),
]


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json(root: Path, relative_path: Path) -> object:
    return json.loads(load_text(root, relative_path))


def require_exact_occurrence(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    if count != 1:
        return [f"{label}:expected=1:actual={count}"]
    return []


def require_exact_value(label: str, actual: object, expected: object) -> list[str]:
    return [] if actual == expected else [f"{label}:expected={expected!r}:actual={actual!r}"]


def nested_value(data: object, path: tuple[str, ...]) -> object:
    current = data
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def iter_anchor_strings(expected: object) -> list[str]:
    anchors: list[str] = []
    if isinstance(expected, str):
        if expected.startswith('test "'):
            anchors.append(expected)
    elif isinstance(expected, list):
        for item in expected:
            if isinstance(item, str) and item.startswith('test "'):
                anchors.append(item)
    return anchors


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for relative_path in (
        RBTREE_HELPER_REL,
        RBTREE_MANIFEST_REL,
        RBTREE_FIXTURE_REL,
        RBTREE_LANE_NOTE_REL,
    ):
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    helper_text = load_text(root, RBTREE_HELPER_REL)
    lane_text = load_text(root, RBTREE_LANE_NOTE_REL)
    manifest = load_json(root, RBTREE_MANIFEST_REL)
    fixture = load_json(root, RBTREE_FIXTURE_REL)
    if not isinstance(manifest, dict):
        return [f"manifest:expected=dict:actual={type(manifest).__name__}"]
    if not isinstance(fixture, dict):
        return [f"fixture:expected=dict:actual={type(fixture).__name__}"]

    for symbol in EXPECTED_RBTREE_SOURCE_SYMBOLS:
        failures.extend(
            require_exact_occurrence(helper_text, f"rbtree_source:{symbol}", symbol)
        )

    seen_helper_anchors = set(EXPECTED_HELPER_TEST_ANCHORS)
    for anchor in EXPECTED_HELPER_TEST_ANCHORS:
        failures.extend(
            require_exact_occurrence(helper_text, f"rbtree_helper:{anchor}", anchor)
        )

    for key, expected in EXPECTED_RBTREE_PACKET.items():
        if key == "helper_test_anchors":
            continue
        for anchor in iter_anchor_strings(expected):
            if anchor in seen_helper_anchors:
                continue
            failures.extend(
                require_exact_occurrence(helper_text, f"rbtree_helper_packet:{key}", anchor)
            )
            seen_helper_anchors.add(anchor)

    for label, marker in EXPECTED_RBTREE_LANE_MARKERS:
        failures.extend(
            require_exact_occurrence(
                lane_text,
                f"rbtree_lane:{label}",
                marker,
            )
        )

    failures.extend(
        require_exact_value(
            "rbtree_manifest:review_anchors.tools/lib.rbtree.zig.helper_test_anchors",
            nested_value(manifest, ("review_anchors", "tools/lib/rbtree.zig", "helper_test_anchors")),
            EXPECTED_HELPER_TEST_ANCHORS,
        )
    )

    for key, expected in EXPECTED_RBTREE_PACKET.items():
        if key == "helper_test_anchors":
            continue
        failures.extend(
            require_exact_value(
                f"rbtree_manifest:review_anchors.tools/lib.rbtree.zig.{key}",
                nested_value(manifest, ("review_anchors", "tools/lib/rbtree.zig", key)),
                expected,
            )
        )

    rbtree_fixture = fixture.get("rbtree")
    if not isinstance(rbtree_fixture, dict):
        return ["rbtree_fixture:expected=dict:actual=missing"]
    for key, expected in EXPECTED_RBTREE_FIXTURE_VALUES.items():
        failures.extend(
            require_exact_value(
                f"rbtree_fixture:{key}",
                rbtree_fixture.get(key),
                expected,
            )
        )

    return failures


def write_file(root: Path, relative_path: Path, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def sample_manifest() -> str:
    return (
        json.dumps(
            {
                "review_anchors": {
                    "tools/lib/rbtree.zig": EXPECTED_RBTREE_PACKET,
                }
            },
            indent=2,
        )
        + "\n"
    )


def sample_fixture() -> str:
    return json.dumps({"rbtree": EXPECTED_RBTREE_FIXTURE_VALUES}, indent=2) + "\n"


def sample_lane_note() -> str:
    return "\n".join(marker for _, marker in EXPECTED_RBTREE_LANE_MARKERS) + "\n"


def build_sample_repo(root: Path) -> None:
    helper_lines = list(EXPECTED_RBTREE_SOURCE_SYMBOLS)
    seen = set(helper_lines)
    for anchor in EXPECTED_HELPER_TEST_ANCHORS:
        if anchor not in seen:
            helper_lines.append(anchor)
            seen.add(anchor)
    for key, expected in EXPECTED_RBTREE_PACKET.items():
        if key == "helper_test_anchors":
            continue
        for anchor in iter_anchor_strings(expected):
            if anchor not in seen:
                helper_lines.append(anchor)
                seen.add(anchor)

    write_file(
        root,
        RBTREE_HELPER_REL,
        "\n".join(helper_lines) + "\n",
    )
    write_file(root, RBTREE_MANIFEST_REL, sample_manifest())
    write_file(root, RBTREE_FIXTURE_REL, sample_fixture())
    write_file(root, RBTREE_LANE_NOTE_REL, sample_lane_note())


def write_sample_root(destination: Path) -> None:
    build_sample_repo(destination)


def mutate_json_path(root: Path, relative_path: Path, path: tuple[str, ...]) -> None:
    json_path = root / relative_path
    data = json.loads(json_path.read_text(encoding="utf-8"))
    current = data
    for key in path[:-1]:
        current = current[key]
    final_key = path[-1]
    value = current[final_key]
    if isinstance(value, list):
        current[final_key] = value[1:]
    elif isinstance(value, bool):
        current[final_key] = not value
    elif isinstance(value, int):
        current[final_key] = value + 1
    else:
        current[final_key] = f"{value} drift"
    json_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase1-rbtree-review-ok-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        failures = collect_failures(root)
        if failures:
            print("self-test:success:unexpected_failures")
            for item in failures:
                print(item)
            return 1
        case_count += 1

    mutation_specs = []
    mutation_specs.extend(
        (f"source_symbol_{idx}_{kind}", ("source_symbol", symbol), kind)
        for idx, symbol in enumerate(EXPECTED_RBTREE_SOURCE_SYMBOLS)
        for kind in ("remove", "duplicate")
    )
    mutationSpecs_end = None
    mutation_specs.extend(
        (f"helper_anchor_{idx}_{kind}", ("helper_anchor", anchor), kind)
        for idx, anchor in enumerate(EXPECTED_HELPER_TEST_ANCHORS)
        for kind in ("remove", "duplicate")
    )
    mutation_specs.extend(
        (
            f"packet_anchor_phase1_helper_replay_{kind}",
            ("packet_anchor", EXPECTED_RBTREE_PACKET["phase1_helper_replay_anchor"]),
            kind,
        )
        for kind in ("remove", "duplicate")
    )
    mutation_specs.extend(
        (
            f"lane_marker_{idx}_{kind}",
            ("lane_marker", marker),
            kind,
        )
        for idx, (_, marker) in enumerate(EXPECTED_RBTREE_LANE_MARKERS)
        for kind in ("remove", "duplicate")
    )
    mutation_specs.extend(
        (
            f"manifest_{key}",
            ("manifest", ("review_anchors", "tools/lib/rbtree.zig", key)),
            "manifest",
        )
        for key in EXPECTED_RBTREE_PACKET
    )
    mutation_specs.extend(
        (
            f"fixture_{key}",
            ("fixture", ("rbtree", key)),
            "fixture",
        )
        for key in EXPECTED_RBTREE_FIXTURE_VALUES
    )
    mutation_specs.append(("manifest_missing_file", ("missing_file", RBTREE_MANIFEST_REL), "missing_file"))
    mutation_specs.append(("fixture_missing_file", ("missing_file", RBTREE_FIXTURE_REL), "missing_file"))
    mutation_specs.append(("lane_note_missing_file", ("missing_file", RBTREE_LANE_NOTE_REL), "missing_file"))

    for name, target, kind in mutation_specs:
        safe_name = name.replace("/", "_")
        with tempfile.TemporaryDirectory(prefix=f"phase1-rbtree-review-{safe_name}-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)

            if isinstance(target, tuple) and target[0] == "source_symbol":
                path = root / RBTREE_HELPER_REL
                marker = target[1]
                text = path.read_text(encoding="utf-8")
                if kind == "remove":
                    text = text.replace(marker + "\n", "", 1)
                else:
                    text = text.replace(marker + "\n", marker + "\n" + marker + "\n", 1)
                path.write_text(text, encoding="utf-8")
            elif isinstance(target, tuple) and target[0] == "helper_anchor":
                path = root / RBTREE_HELPER_REL
                marker = target[1]
                text = path.read_text(encoding="utf-8")
                if kind == "remove":
                    text = text.replace(marker + "\n", "", 1)
                else:
                    text = text.replace(marker + "\n", marker + "\n" + marker + "\n", 1)
                path.write_text(text, encoding="utf-8")
            elif isinstance(target, tuple) and target[0] == "packet_anchor":
                path = root / RBTREE_HELPER_REL
                marker = target[1]
                text = path.read_text(encoding="utf-8")
                if kind == "remove":
                    text = text.replace(marker + "\n", "", 1)
                else:
                    text = text.replace(marker + "\n", marker + "\n" + marker + "\n", 1)
                path.write_text(text, encoding="utf-8")
            elif isinstance(target, tuple) and target[0] == "lane_marker":
                path = root / RBTREE_LANE_NOTE_REL
                marker = target[1]
                text = path.read_text(encoding="utf-8")
                if kind == "remove":
                    text = text.replace(marker + "\n", "", 1)
                else:
                    text = text.replace(marker + "\n", marker + "\n" + marker + "\n", 1)
                path.write_text(text, encoding="utf-8")
            elif isinstance(target, tuple) and target[0] == "manifest":
                mutate_json_path(root, RBTREE_MANIFEST_REL, target[1])
            elif isinstance(target, tuple) and target[0] == "fixture":
                mutate_json_path(root, RBTREE_FIXTURE_REL, target[1])
            else:
                (root / target[1]).unlink()

            failures = collect_failures(root)
            if not failures:
                print(f"self-test:{name}:expected_failure")
                return 1
            case_count += 1

    print("PHASE1_RBTREE_REVIEW_PACKET_SELF_TEST=pass")
    print(f"PHASE1_RBTREE_REVIEW_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test")
    parser.add_argument(
        "--write-sample-root",
        help="write a minimal passing sample repository root to the given path",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        write_sample_root(Path(args.write_sample_root).resolve())
        return 0

    failures = collect_failures(repo_root(args.root))
    if failures:
        for item in failures:
            print(item)
        return 1

    print("phase1-rbtree-review-packet:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
