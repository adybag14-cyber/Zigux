#!/usr/bin/env python3
"""Guard the Phase 1 rbtree review packet against helper, fixture, manifest, and lane-note drift."""

from __future__ import annotations

import argparse
import copy
import json
import tempfile
from pathlib import Path
from typing import Any


DEFAULT_ROOT = Path(__file__).resolve().parent / "phase1_rbtree_review_sample"
RBTREE_HELPER_REL = Path("tools/lib/rbtree.zig")
LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
FIXTURE_REL = Path("zigux/tests/fixtures/phase1_helpers.json")

EXPECTED_DIRECT_OWNER_LINE = (
    "- `PHASE1_RBTREE_DIRECT_OWNER=rbtree keeps ordered Linux-style alias, "
    "low-level Linux-style alias, cached-root insert-miss, leftmost-sync, "
    "cached-root alias, singleton-erase, replacement, detach, and reseed "
    "anchors helper-local while the committed shared replay already owns "
    "duplicate-search parity through find(), findFirst(), nextMatch(), and "
    "matchIterator() plus the parked cached_leftmost_return_serials witness`"
)

EXPECTED_NEXT_SAFE_STEP_LINE = (
    "- `PHASE1_RBTREE_NEXT_SAFE_STEP=rbtree reopens only to keep the already-"
    "landed cached_leftmost_return_serials shared replay aligned across the "
    "manifest, direct-owner note, and any shared parity gates, or for drift "
    "inside the still-helper-local cached-root insert-miss, leftmost-sync, "
    "cached-root alias, singleton-erase, replacement, detach, and reseed "
    "anchors; do not batch a second widening into the same run`"
)

EXPECTED_DIRECT_OWNER_NOTE = (
    "- `tools/lib/rbtree.zig` now keeps ordered Linux-style alias, low-level "
    "Linux-style alias, cached-root insert-miss, leftmost-sync, cached-root "
    "alias, singleton-erase, replacement, detach, and reseed coverage "
    "helper-local while the committed shared replay owns duplicate-search "
    "parity through `matchIterator()` as well as `find()`, `findFirst()`, and "
    "`nextMatch()`, and current `master` already consumes "
    "`cached_leftmost_return_serials` as shared cached-root leftmost-return "
    "evidence. The dedicated `low_level_alias_anchor` in "
    "`zigux/tests/fixtures/phase1_helper_manifest.json` also keeps the "
    "low-level Linux-style alias proof named explicitly inside that same "
    "helper-local packet instead of leaving it implied only by the broader "
    "helper test list. Until another committed cached-root replay field lands, "
    "leave the remaining cached-root anchors helper-local and do not batch a "
    "second widening into the same reopen step.`"
)

EXPECTED_FIXTURE_CACHED_LEFTMOST = [0, -1, 2, -1]

EXPECTED_RBTREE_PACKET = {
    "helper_test_anchors": [
        'test "rbtree inserts and traverses in sorted order"',
        'test "rbtree erase and replace keep traversal consistent"',
        'test "rbtree ordered Linux-style aliases mirror traversal and replacement helpers"',
        'test "rbtree low-level Linux-style aliases mirror node-state helpers"',
        'test "rbtree eraseInit detaches erased node"',
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
    ],
    "phase1_helper_replay_anchor": 'test "phase 1 helper ports match committed parity fixture"',
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
    "shared_replay_summary": (
        "shared traversal, detached-node, duplicate-search, and iterator replay "
        "stay explicit through the Phase 1 fixture and replay, while current "
        "master also carries the parked `cached_leftmost_return_serials` parity-"
        "only witness in the committed shared fixture beside the direct cached-"
        "root packet"
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
        "cached-root insert-miss, leftmost-sync, cached-root alias, singleton-"
        "erase, replacement, detach, and reseed behavior remain owned by direct "
        "helper-local anchors, while current master already ships and the shared "
        "Zig replay already consumes the parked `cached_leftmost_return_serials` "
        "witness as shared cached-root leftmost-return evidence"
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
        "shared find, first-match, next-match, and match-iterator duplicate-"
        "search parity stays explicit through the Phase 1 fixture and replay, "
        "and current master already consumes `cached_leftmost_return_serials` "
        "as shared cached-root leftmost-return evidence, while the remaining "
        "cached-root insert-miss, leftmost-sync, cached-root alias, singleton-"
        "erase, replacement, detach, and reseed review anchors stay explicit at "
        "the helper surface for any paths the shared replay still does not cover"
    ),
    "next_safe_step_note": (
        "If this helper lane reopens, keep the already-landed shared-replay "
        "promotion for `cached_leftmost_return_serials` aligned across the "
        "committed fixture, shared replay, and direct cached-root anchors; "
        "until another committed cached-root field lands, insert-miss, leftmost-"
        "sync, cached-root alias, singleton-erase, replacement, detach, and "
        "reseed behavior stay owned by direct helper-local anchors."
    ),
}

LIST_FIELDS = (
    "helper_test_anchors",
    "parity_fixture_keys",
    "cached_leftmost_fixture_keys",
    "traversal_replay_keys",
    "duplicate_search_replay_keys",
    "duplicate_search_anchors",
    "cached_root_followup_anchors",
)

SCALAR_FIELDS = (
    "phase1_helper_replay_anchor",
    "shared_replay_summary",
    "cached_root_direct_review_summary",
    "ordered_alias_anchor",
    "low_level_alias_anchor",
    "cached_root_alias_anchor",
    "review_packet_summary",
    "next_safe_step_note",
)


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
    if actual != expected:
        return [f"{label}:expected_current_packet"]
    return []


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for relative_path in (RBTREE_HELPER_REL, LANE_NOTE_REL, MANIFEST_REL, FIXTURE_REL):
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    helper_text = load_text(root, RBTREE_HELPER_REL)
    lane_note_text = load_text(root, LANE_NOTE_REL)
    manifest = load_json(root, MANIFEST_REL)
    fixture = load_json(root, FIXTURE_REL)

    failures.extend(
        require_exact_occurrence(
            lane_note_text,
            "lane_note:rbtree_direct_owner",
            EXPECTED_DIRECT_OWNER_LINE,
        )
    )
    failures.extend(
        require_exact_occurrence(
            lane_note_text,
            "lane_note:rbtree_next_safe_step",
            EXPECTED_NEXT_SAFE_STEP_LINE,
        )
    )
    failures.extend(
        require_exact_occurrence(
            lane_note_text,
            "lane_note:rbtree_direct_owner_note",
            EXPECTED_DIRECT_OWNER_NOTE,
        )
    )

    review_anchors = manifest.get("review_anchors") if isinstance(manifest, dict) else None
    if not isinstance(review_anchors, dict):
        return ["manifest:review_anchors"]
    rbtree_packet = review_anchors.get("tools/lib/rbtree.zig")
    if not isinstance(rbtree_packet, dict):
        return ["manifest:tools/lib/rbtree.zig"]

    for field in LIST_FIELDS:
        failures.extend(
            require_exact_value(
                f"manifest:{field}",
                rbtree_packet.get(field),
                EXPECTED_RBTREE_PACKET[field],
            )
        )
    for field in SCALAR_FIELDS:
        failures.extend(
            require_exact_value(
                f"manifest:{field}",
                rbtree_packet.get(field),
                EXPECTED_RBTREE_PACKET[field],
            )
        )

    rbtree_fixture = fixture.get("rbtree") if isinstance(fixture, dict) else None
    if not isinstance(rbtree_fixture, dict):
        return ["fixture:rbtree"]
    failures.extend(
        require_exact_value(
            "fixture:cached_leftmost_return_serials",
            rbtree_fixture.get("cached_leftmost_return_serials"),
            EXPECTED_FIXTURE_CACHED_LEFTMOST,
        )
    )

    for anchor in EXPECTED_RBTREE_PACKET["helper_test_anchors"]:
        failures.extend(
            require_exact_occurrence(helper_text, f"helper:{anchor}", anchor)
        )

    return failures


def write_text(root: Path, relative_path: Path, text: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    write_text(root, RBTREE_HELPER_REL, "\n".join(EXPECTED_RBTREE_PACKET["helper_test_anchors"]) + "\n")
    write_text(
        root,
        LANE_NOTE_REL,
        "# sample\n\n"
        + EXPECTED_DIRECT_OWNER_NOTE
        + "\n"
        + EXPECTED_DIRECT_OWNER_LINE
        + "\n"
        + EXPECTED_NEXT_SAFE_STEP_LINE
        + "\n",
    )
    write_text(
        root,
        MANIFEST_REL,
        json.dumps(
            {"review_anchors": {"tools/lib/rbtree.zig": copy.deepcopy(EXPECTED_RBTREE_PACKET)}},
            indent=2,
        )
        + "\n",
    )
    write_text(
        root,
        FIXTURE_REL,
        json.dumps({"rbtree": {"cached_leftmost_return_serials": EXPECTED_FIXTURE_CACHED_LEFTMOST}}) + "\n",
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase1-rbtree-review-ok-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        failures = collect_failures(root)
        if failures:
            print("self-test:success:unexpected_failures")
            for item in failures:
                print(item)
            return 1

    mutations = [
        ("remove_direct_owner_line", "line", EXPECTED_DIRECT_OWNER_LINE, "remove"),
        ("duplicate_direct_owner_line", "line", EXPECTED_DIRECT_OWNER_LINE, "duplicate"),
        ("remove_next_safe_step_line", "line", EXPECTED_NEXT_SAFE_STEP_LINE, "remove"),
        ("remove_direct_owner_note", "line", EXPECTED_DIRECT_OWNER_NOTE, "remove"),
        ("fixture_cached_leftmost", "fixture", "cached_leftmost_return_serials", "mutate"),
        ("helper_anchor_removed", "helper", EXPECTED_RBTREE_PACKET["helper_test_anchors"][0], "remove"),
    ]
    mutations.extend((f"manifest_{field}", "manifest", field, "mutate") for field in LIST_FIELDS)
    mutations.extend((f"manifest_{field}", "manifest", field, "mutate") for field in SCALAR_FIELDS)

    for name, target, needle, mode in mutations:
        with tempfile.TemporaryDirectory(prefix=f"phase1-rbtree-review-{name}-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)

            if target == "line":
                path = root / LANE_NOTE_REL
                text = path.read_text(encoding="utf-8")
                if mode == "remove":
                    text = text.replace(needle + "\n", "", 1)
                else:
                    text = text.replace(needle, needle + "\n" + needle, 1)
                path.write_text(text, encoding="utf-8")
            elif target == "helper":
                path = root / RBTREE_HELPER_REL
                text = path.read_text(encoding="utf-8")
                text = text.replace(needle + "\n", "", 1)
                path.write_text(text, encoding="utf-8")
            elif target == "fixture":
                path = root / FIXTURE_REL
                fixture = json.loads(path.read_text(encoding="utf-8"))
                fixture["rbtree"][needle] = [0, -1, 2]
                path.write_text(json.dumps(fixture) + "\n", encoding="utf-8")
            else:
                path = root / MANIFEST_REL
                manifest = json.loads(path.read_text(encoding="utf-8"))
                packet = manifest["review_anchors"]["tools/lib/rbtree.zig"]
                if isinstance(packet[needle], list):
                    packet[needle] = packet[needle][1:]
                else:
                    packet[needle] = packet[needle] + " drift"
                path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

            failures = collect_failures(root)
            if not failures:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("self-test:ok")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run built-in checker self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        for item in failures:
            print(item)
        return 1

    print("phase1-rbtree-review-packet:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
