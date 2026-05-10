#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent
MANIFEST_PATH = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
HELPER_KEY = "tools/lib/rbtree.zig"

EXPECTED_RBTREE_REVIEW_PACKET = {
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
        "next_match_terminal_null",
    ],
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
        "shared find, first-match, and next-match duplicate-search parity stays explicit through "
        "the Phase 1 fixture and replay, while match-iterator coverage plus cached-root insert-miss, "
        "leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed behavior "
        "remain owned by direct helper-local anchors until master ships dedicated shared iterator or "
        "cached-root fixture keys"
    ),
}


def repo_root_from_arg(root_arg: str | None) -> Path:
    if root_arg:
        return Path(root_arg).resolve()
    return DEFAULT_ROOT


def load_manifest(root: Path) -> object:
    return json.loads((root / MANIFEST_PATH).read_text(encoding="utf-8"))


def validate_manifest(manifest: object) -> tuple[str, object]:
    if not isinstance(manifest, dict):
        return ("manifest_type", type(manifest).__name__)

    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        return ("review_anchors_type", type(review_anchors).__name__)

    rbtree_packet = review_anchors.get(HELPER_KEY)
    if not isinstance(rbtree_packet, dict):
        return ("rbtree_packet_type", type(rbtree_packet).__name__)

    for key, expected_value in EXPECTED_RBTREE_REVIEW_PACKET.items():
        actual_value = rbtree_packet.get(key)
        if actual_value != expected_value:
            return ("rbtree_packet_field", (key, expected_value, actual_value))

    return ("pass", None)


def write_fixture(root: Path, packet: dict[str, object]) -> None:
    manifest_path = root / MANIFEST_PATH
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        "phase": "Phase 1",
        "status": "closed",
        "helper_count": 13,
        "helpers": [],
        "review_anchors": {
            HELPER_KEY: packet,
        },
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def run_self_test() -> None:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_rbtree_packet_") as tmp:
        root = Path(tmp)

        write_fixture(root, dict(EXPECTED_RBTREE_REVIEW_PACKET))
        kind, payload = validate_manifest(load_manifest(root))
        assert kind == "pass", (kind, payload)
        case_count += 1

        broken_packet = dict(EXPECTED_RBTREE_REVIEW_PACKET)
        broken_packet["duplicate_search_anchors"] = ['test "bad duplicate packet"']
        write_fixture(root, broken_packet)
        kind, payload = validate_manifest(load_manifest(root))
        assert kind == "rbtree_packet_field", (kind, payload)
        assert payload[0] == "duplicate_search_anchors", payload
        case_count += 1

        broken_packet = dict(EXPECTED_RBTREE_REVIEW_PACKET)
        broken_packet["cached_root_followup_anchors"] = ['test "bad cached packet"']
        write_fixture(root, broken_packet)
        kind, payload = validate_manifest(load_manifest(root))
        assert kind == "rbtree_packet_field", (kind, payload)
        assert payload[0] == "cached_root_followup_anchors", payload
        case_count += 1

    print("PHASE1_RBTREE_REVIEW_PACKET_SELF_TEST=pass")
    print(f"PHASE1_RBTREE_REVIEW_PACKET_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the bounded Phase 1 rbtree manifest review packet."
    )
    parser.add_argument("--root", help="Validate an alternate repository root.")
    parser.add_argument("--self-test", action="store_true", help="Run checker self-tests.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    root = repo_root_from_arg(args.root)
    manifest_file = root / MANIFEST_PATH
    if not manifest_file.exists():
        print("PHASE1_RBTREE_REVIEW_PACKET=fail")
        print(f"MISSING_MANIFEST={manifest_file}")
        return 1

    kind, payload = validate_manifest(load_manifest(root))
    if kind != "pass":
        print("PHASE1_RBTREE_REVIEW_PACKET=fail")
        print(f"PHASE1_RBTREE_REVIEW_PACKET_REASON={kind}")
        print(payload)
        return 1

    print("PHASE1_RBTREE_REVIEW_PACKET=pass")
    print(f"PHASE1_RBTREE_REVIEW_PACKET_MANIFEST={manifest_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
