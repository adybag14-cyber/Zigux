#!/usr/bin/env python3
"""Guard the Phase 1 rbtree review packet against helper, fixture, smoke, and lane drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
HELPER_REL = Path("tools/lib/rbtree.zig")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
FIXTURE_REL = Path("zigux/tests/fixtures/phase1_helpers.json")
SMOKE_REL = Path("zigux/tests/phase1_host_tools_smoke.zig")
LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
CLOSURE_NOTE_REL = Path("Documentation/zigux/phase1-closure.md")


class DuplicateTrackingDict(dict[str, object]):
    def __init__(self, pairs: list[tuple[str, object]]) -> None:
        super().__init__()
        self.duplicate_keys: list[str] = []
        for key, value in pairs:
            if key in self and key not in self.duplicate_keys:
                self.duplicate_keys.append(key)
            self[key] = value


EXPECTED_SOURCE_SYMBOLS = [
    "pub fn insertColorCached(node: *Node, root: *RootCached, leftmost: bool) void {",
    "pub fn rb_insert_color_cached(node: *Node, root: *RootCached, leftmost: bool) void {",
    "pub fn addCached(node: *Node, root: *RootCached, less: LessFn) ?*Node {",
    "pub fn rb_add_cached(node: *Node, root: *RootCached, less: LessFn) ?*Node {",
    "pub fn findAddCached(node: *Node, root: *RootCached, cmp: CmpNodeFn) ?*Node {",
    "pub fn rb_find_add_cached(node: *Node, root: *RootCached, cmp: CmpNodeFn) ?*Node {",
    "pub fn eraseCached(node: *Node, root: *RootCached) ?*Node {",
    "pub fn rb_erase_cached(node: *Node, root: *RootCached) ?*Node {",
    "pub fn eraseInitCached(node: *Node, root: *RootCached) void {",
    "pub fn rb_erase_init_cached(node: *Node, root: *RootCached) void {",
    "pub fn firstCached(root: *const RootCached) ?*Node {",
    "pub fn rb_first_cached(root: *const RootCached) ?*Node {",
    "pub fn replaceNodeCached(victim: *Node, new: *Node, root: *RootCached) void {",
    "pub fn rb_replace_node_cached(victim: *Node, new: *Node, root: *RootCached) void {",
    "pub fn nextMatch(key: *const anyopaque, node: *const Node, cmp: CmpKeyFn) ?*Node {",
    "pub fn rb_next_match(key: *const anyopaque, node: *const Node, cmp: CmpKeyFn) ?*Node {",
    "pub fn matchIterator(key: *const anyopaque, root: *const Root, cmp: CmpKeyFn) MatchIterator {",
    "pub fn rb_match_iterator(key: *const anyopaque, root: *const Root, cmp: CmpKeyFn) MatchIterator {",
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
    "- `PHASE1_RBTREE_DIRECT_OWNER=rbtree keeps ordered Linux-style alias, low-level Linux-style alias, cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed anchors helper-local while the committed fixture still owns exact find(), findFirst(), nextMatch(), and matchIterator() duplicate-search fields and the shared host-tools smoke route keeps duplicate-range iteration plus the parked cached_leftmost_return_serials witness explicit`",
    "- `PHASE1_RBTREE_NEXT_SAFE_STEP=rbtree reopens only to keep the already-landed cached_leftmost_return_serials shared replay aligned across the manifest, direct-owner note, and any shared parity gates, or for drift inside the still-helper-local ordered Linux-style alias proof, dedicated low_level_alias_anchor, cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed anchors; do not batch a second widening into the same run`",
]

EXPECTED_LANE_PARAGRAPH = (
    "- `tools/lib/rbtree.zig` now keeps ordered Linux-style alias, low-level Linux-style alias, "
    "cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, "
    "detach, and reseed coverage helper-local while the committed fixture still owns exact "
    "`find()`, `findFirst()`, `nextMatch()`, and `matchIterator()` duplicate-search fields and "
    "the shared host-tools smoke route already keeps duplicate-range iteration plus the parked "
    "`cached_leftmost_return_serials` witness explicit. The dedicated `low_level_alias_anchor` "
    "and `cached_root_alias_anchor` entries in `zigux/tests/fixtures/phase1_helper_manifest.json` "
    "keep both Linux-style alias proofs named explicitly inside that same helper-local packet instead "
    "of leaving either alias path implied only by the broader helper test list. Until another committed "
    "cached-root replay field lands, leave the remaining cached-root anchors helper-local and do not "
    "batch a second widening into the same reopen step."
)

EXPECTED_CLOSURE_PARAGRAPH = (
    "A second current helper-family tie-breaker inside that packet is the `rbtree` direct-anchor route: "
    "keep `tools/lib/rbtree.zig` parked unless a fresh reread finds drift in the helper-local ordered "
    "Linux-style alias proof, the dedicated manifest-backed `low_level_alias_anchor`, the dedicated "
    "manifest-backed `cached_root_alias_anchor`, the cached-root insert-miss, leftmost-sync, cached-root "
    "alias, singleton-erase, replacement, detach, or reseed anchors, or drift in the already-committed "
    "duplicate-search replay fields or exact `cached_leftmost_return_serials` witness. Current `master` "
    "still keeps both Linux-style alias proofs named explicitly in `zigux/tests/fixtures/phase1_helper_manifest.json`, "
    "while the shared host-tools smoke route and committed Phase 1 fixture already recheck duplicate-range "
    "iteration plus the exact cached-leftmost-return packet, so leave rbtree parked unless one of those "
    "helper-local anchors or committed replay fields drifts and do not batch a second cached-root widening "
    "into the same reopen step."
)

EXPECTED_PARITY_FIXTURE_KEYS = [
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
]

EXPECTED_DUPLICATE_SEARCH_ANCHORS = [
    'test "rbtree findAdd keeps the first duplicate and inserts new keys"',
    'test "rbtree nextMatch walks the duplicate range in order"',
    'test "rbtree matchIterator walks the duplicate range in order"',
]

EXPECTED_MANIFEST_PACKET = {
    "phase1_helper_replay_anchor": 'test "phase1 host-tools smoke exercises live helper behavior"',
    "parity_fixture_keys": EXPECTED_PARITY_FIXTURE_KEYS,
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
    "cached_leftmost_fixture_keys": ["cached_leftmost_return_serials"],
    "cached_root_transition_fixture_keys": ["cached_root_transition_serials"],
    "cached_root_direct_review_summary": "cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed behavior remain owned by direct helper-local anchors, while the exact `cached_leftmost_return_serials` witness now stays aligned across the helper-local tests, the shared host-tools smoke replay, and the committed fixture",
    "ordered_alias_anchor": 'test "rbtree ordered Linux-style aliases mirror traversal and replacement helpers"',
    "low_level_alias_anchor": 'test "rbtree low-level Linux-style aliases mirror node-state helpers"',
    "duplicate_search_anchors": EXPECTED_DUPLICATE_SEARCH_ANCHORS,
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
    "find_found_key": 10,
    "find_missing": True,
    "find_first_serial": 0,
    "next_match_serials": [0, 2, 6],
    "match_iterator_serials": [0, 2, 6],
    "cached_leftmost_return_serials": [0, -1, 2, -1],
    "cached_root_transition_serials": [0, 0, 4, 2],
    "next_match_terminal_null": True,
}

EXPECTED_SMOKE_MARKERS = [
    'const rbtree = @import("rbtree");',
    'try std.testing.expect(@hasDecl(rbtree, "find"));',
    'try std.testing.expect(@hasDecl(rbtree, "matchIterator"));',
    "const found_duplicate = rbtree.find(&duplicate_key, &tree_root, RbtreeSmokeEntry.cmp) orelse return error.TestUnexpectedResult;",
    "const first_duplicate = rbtree.findFirst(&duplicate_key, &tree_root, RbtreeSmokeEntry.cmp) orelse return error.TestUnexpectedResult;",
    "const second_duplicate = rbtree.nextMatch(&duplicate_key, first_duplicate, RbtreeSmokeEntry.cmp) orelse return error.TestUnexpectedResult;",
    "try std.testing.expect(rbtree.nextMatch(&duplicate_key, third_duplicate, RbtreeSmokeEntry.cmp) == null);",
    "var iter = rbtree.matchIterator(&duplicate_key, &tree_root, RbtreeSmokeEntry.cmp);",
    "var cached_leftmost_return_serials: [4]i32 = undefined;",
    "try std.testing.expectEqualSlices(i32, &.{ 0, -1, 2, -1 }, &cached_leftmost_return_serials);",
    "var cached_root_transition_serials: [4]i32 = undefined;",
    "try std.testing.expectEqualSlices(i32, &.{ 0, 0, 4, 2 }, &cached_root_transition_serials);",
]


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json_with_duplicate_tracking(text: str) -> object:
    return json.loads(text, object_pairs_hook=DuplicateTrackingDict)


def load_json(root: Path, relative_path: Path) -> object:
    return load_json_with_duplicate_tracking(load_text(root, relative_path))

def load_json_failure(label: str, exc: json.JSONDecodeError) -> str:
    return f"{label}:invalid_json:{exc.msg}:line={exc.lineno}:column={exc.colno}"


def collect_duplicate_json_key_paths(data: object, prefix: tuple[str, ...] = ()) -> list[str]:
    paths: list[str] = []
    if isinstance(data, DuplicateTrackingDict):
        for key in data.duplicate_keys:
            paths.append(".".join(prefix + (key,)))
    if isinstance(data, dict):
        for key, value in data.items():
            paths.extend(collect_duplicate_json_key_paths(value, prefix + (key,)))
    elif isinstance(data, list):
        for item in data:
            paths.extend(collect_duplicate_json_key_paths(item, prefix))
    return paths


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

def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for relative_path in (
        HELPER_REL,
        MANIFEST_REL,
        FIXTURE_REL,
        SMOKE_REL,
        LANE_NOTE_REL,
        CLOSURE_NOTE_REL,
    ):
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    helper_text = load_text(root, HELPER_REL)
    smoke_text = load_text(root, SMOKE_REL)
    lane_text = load_text(root, LANE_NOTE_REL)
    closure_text = load_text(root, CLOSURE_NOTE_REL)
    try:
        manifest = load_json(root, MANIFEST_REL)
    except json.JSONDecodeError as exc:
        return [load_json_failure("manifest", exc)]
    try:
        fixture = load_json(root, FIXTURE_REL)
    except json.JSONDecodeError as exc:
        return [load_json_failure("fixture", exc)]

    if not isinstance(manifest, dict):
        return [f"manifest:expected=dict:actual={type(manifest).__name__}"]
    duplicate_manifest_paths = collect_duplicate_json_key_paths(manifest)
    if duplicate_manifest_paths:
        return [f"manifest:duplicate_json_key:{path}" for path in duplicate_manifest_paths]

    if not isinstance(fixture, dict):
        return [f"fixture:expected=dict:actual={type(fixture).__name__}"]
    duplicate_fixture_paths = collect_duplicate_json_key_paths(fixture)
    if duplicate_fixture_paths:
        return [f"fixture:duplicate_json_key:{path}" for path in duplicate_fixture_paths]

    for symbol in EXPECTED_SOURCE_SYMBOLS:
        failures.extend(require_exact_occurrence(helper_text, f"helper_symbol:{symbol}", symbol))

    for anchor in EXPECTED_HELPER_TEST_ANCHORS:
        failures.extend(require_exact_occurrence(helper_text, f"helper_anchor:{anchor}", anchor))

    for marker in EXPECTED_SMOKE_MARKERS:
        failures.extend(require_exact_occurrence(smoke_text, f"smoke_marker:{marker}", marker))

    for marker in EXPECTED_LANE_LINES:
        failures.extend(require_exact_occurrence(lane_text, f"lane_marker:{marker}", marker))
    failures.extend(require_exact_occurrence(lane_text, "lane_paragraph", EXPECTED_LANE_PARAGRAPH))
    failures.extend(require_exact_occurrence(closure_text, "closure_paragraph", EXPECTED_CLOSURE_PARAGRAPH))

    packet = nested_value(manifest, ("review_anchors", "tools/lib/rbtree.zig"))
    if not isinstance(packet, dict):
        return ["manifest:review_anchors.tools/lib/rbtree.zig:expected=dict"]
    failures.extend(
        require_exact_value(
            "manifest:review_anchors.tools/lib/rbtree.zig.helper_test_anchors",
            packet.get("helper_test_anchors"),
            EXPECTED_HELPER_TEST_ANCHORS,
        )
    )
    for key, expected in EXPECTED_MANIFEST_PACKET.items():
        failures.extend(
            require_exact_value(
                f"manifest:review_anchors.tools/lib/rbtree.zig.{key}",
                packet.get(key),
                expected,
            )
        )

    rbtree_fixture = fixture.get("rbtree")
    if not isinstance(rbtree_fixture, dict):
        return ["fixture:rbtree:expected=dict"]
    for key, expected in EXPECTED_FIXTURE_VALUES.items():
        failures.extend(
            require_exact_value(
                f"fixture:rbtree.{key}",
                rbtree_fixture.get(key),
                expected,
            )
        )

    return failures


def write_file(root: Path, relative_path: Path, text: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def sample_manifest() -> str:
    return (
        json.dumps(
            {
                "review_anchors": {
                    "tools/lib/rbtree.zig": {
                        "helper_test_anchors": EXPECTED_HELPER_TEST_ANCHORS,
                        **EXPECTED_MANIFEST_PACKET,
                    }
                }
            },
            indent=2,
        )
        + "\n"
    )


def sample_fixture() -> str:
    return json.dumps({"rbtree": EXPECTED_FIXTURE_VALUES}, indent=2) + "\n"


def build_sample_repo(root: Path) -> None:
    helper_lines = EXPECTED_SOURCE_SYMBOLS + [""] + EXPECTED_HELPER_TEST_ANCHORS
    write_file(root, HELPER_REL, "\n".join(helper_lines) + "\n")
    write_file(root, MANIFEST_REL, sample_manifest())
    write_file(root, FIXTURE_REL, sample_fixture())
    write_file(root, SMOKE_REL, "\n".join(EXPECTED_SMOKE_MARKERS) + "\n")
    write_file(root, LANE_NOTE_REL, "# sample\n\n" + "\n".join(EXPECTED_LANE_LINES + [EXPECTED_LANE_PARAGRAPH]) + "\n")
    write_file(root, CLOSURE_NOTE_REL, "# sample\n\n" + EXPECTED_CLOSURE_PARAGRAPH + "\n")


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


def insert_duplicate_json_line(
    root: Path,
    relative_path: Path,
    needle: str,
    duplicate_line: str,
) -> None:
    json_path = root / relative_path
    text = json_path.read_text(encoding="utf-8")
    json_path.write_text(
        text.replace(needle, duplicate_line + "\n" + needle, 1),
        encoding="utf-8",
    )


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

    mutation_specs: list[tuple[str, object, str]] = []
    mutation_specs.extend(
        (f"source_symbol_{idx}_{kind}", ("helper_text", symbol), kind)
        for idx, symbol in enumerate(EXPECTED_SOURCE_SYMBOLS)
        for kind in ("remove", "duplicate")
    )
    mutation_specs.extend(
        (f"helper_anchor_{idx}_{kind}", ("helper_text", anchor), kind)
        for idx, anchor in enumerate(EXPECTED_HELPER_TEST_ANCHORS)
        for kind in ("remove", "duplicate")
    )
    mutation_specs.extend(
        (f"smoke_marker_{idx}_{kind}", ("smoke_text", marker), kind)
        for idx, marker in enumerate(EXPECTED_SMOKE_MARKERS)
        for kind in ("remove", "duplicate")
    )
    mutation_specs.extend(
        (f"lane_marker_{idx}_{kind}", ("lane_text", marker), kind)
        for idx, marker in enumerate(EXPECTED_LANE_LINES + [EXPECTED_LANE_PARAGRAPH, EXPECTED_CLOSURE_PARAGRAPH])
        for kind in ("remove", "duplicate")
    )
    mutation_specs.extend(
        (f"manifest_{key}", ("manifest", ("review_anchors", "tools/lib/rbtree.zig", key)), "manifest")
        for key in ("helper_test_anchors", *EXPECTED_MANIFEST_PACKET.keys())
    )
    mutation_specs.extend(
        (f"fixture_{key}", ("fixture", ("rbtree", key)), "fixture")
        for key in EXPECTED_FIXTURE_VALUES
    )
    mutation_specs.append(
        (
            "manifest_duplicate_review_packet_summary",
            (
                "duplicate_json_text",
                MANIFEST_REL,
                '      "review_packet_summary": "the current shared host-tools smoke replay keeps duplicate-range iteration and the exact `cached_leftmost_return_serials` cached-root leftmost-return witness visible for rbtree, while the committed Phase 1 fixture still carries the exact traversal, detached-node, duplicate-search, and cached-leftmost-return witnesses; direct helper-local anchors continue to own cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed paths that the shared smoke route does not replay exactly",',
                '      "review_packet_summary": "drifted duplicate summary",',
            ),
            "duplicate_json_text",
        )
    )
    mutation_specs.append(
        (
            "fixture_duplicate_cached_leftmost_return_serials",
            (
                "duplicate_json_text",
                FIXTURE_REL,
                '    "cached_leftmost_return_serials": [',
                '    "cached_leftmost_return_serials": [],',
            ),
            "duplicate_json_text",
        )
    )
    mutation_specs.append(("manifest_missing_file", ("missing_file", MANIFEST_REL), "missing_file"))
    mutation_specs.append(("fixture_missing_file", ("missing_file", FIXTURE_REL), "missing_file"))
    mutation_specs.append(("smoke_missing_file", ("missing_file", SMOKE_REL), "missing_file"))
    mutation_specs.append(("lane_missing_file", ("missing_file", LANE_NOTE_REL), "missing_file"))
    mutation_specs.append(("closure_missing_file", ("missing_file", CLOSURE_NOTE_REL), "missing_file"))
    mutation_specs.append(("manifest_invalid_json", ("invalid_json", MANIFEST_REL), "invalid_json"))
    mutation_specs.append(("fixture_invalid_json", ("invalid_json", FIXTURE_REL), "invalid_json"))

    for name, target, kind in mutation_specs:
        safe_name = name.replace("/", "_")
        with tempfile.TemporaryDirectory(prefix=f"phase1-rbtree-review-{safe_name}-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)

            if isinstance(target, tuple) and target[0] in {"helper_text", "smoke_text", "lane_text"}:
                path_map = {
                    "helper_text": HELPER_REL,
                    "smoke_text": SMOKE_REL,
                    "lane_text": LANE_NOTE_REL if target[1] != EXPECTED_CLOSURE_PARAGRAPH else CLOSURE_NOTE_REL,
                }
                relative_path = path_map[target[0]]
                path = root / relative_path
                marker = target[1]
                text = path.read_text(encoding="utf-8")
                if kind == "remove":
                    text = text.replace(marker + "\n", "", 1)
                else:
                    text = text.replace(marker + "\n", marker + "\n" + marker + "\n", 1)
                path.write_text(text, encoding="utf-8")
            elif isinstance(target, tuple) and target[0] == "manifest":
                mutate_json_path(root, MANIFEST_REL, target[1])
            elif isinstance(target, tuple) and target[0] == "fixture":
                mutate_json_path(root, FIXTURE_REL, target[1])
            elif isinstance(target, tuple) and target[0] == "duplicate_json_text":
                insert_duplicate_json_line(root, target[1], target[2], target[3])
            elif isinstance(target, tuple) and target[0] == "invalid_json":
                (root / target[1]).write_text("{\n", encoding="utf-8")
            elif isinstance(target, tuple) and target[0] == "missing_file":
                (root / target[1]).unlink()
            else:
                raise AssertionError(f"unsupported mutation target: {target!r}")

            failures = collect_failures(root)
            if not failures:
                print(f"self-test:{name}:expected_failure_but_passed")
                return 1
            case_count += 1

    print(f"self-test:ok:{case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="Repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="Run built-in negative coverage tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        for failure in failures:
            print(failure)
        return 1
    print("phase1-rbtree-review-packet:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
