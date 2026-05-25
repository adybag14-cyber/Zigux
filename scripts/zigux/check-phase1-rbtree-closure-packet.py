#!/usr/bin/env python3
"""Guard the current Phase 1 rbtree closure packet against helper and reminder drift."""

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
LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
CLOSURE_NOTE_REL = Path("Documentation/zigux/phase1-closure.md")
VALIDATOR_REL = Path("scripts/zigux/validate-phase1-closure.py")

HELPER_MARKERS = [
    'test "rbtree ordered Linux-style aliases mirror traversal and replacement helpers"',
    'test "rbtree low-level Linux-style aliases mirror node-state helpers"',
    'test "rbtree addCached returns the inserted node only when it becomes leftmost"',
    'test "rbtree findAddCached keeps cached leftmost stable while inserting misses"',
    'test "rbtree cached root keeps the leftmost pointer in sync"',
    'test "rbtree cached-root Linux-style aliases mirror the primary helpers"',
    'test "rbtree replaceNodeCached keeps non-leftmost leftmost unchanged"',
    'test "rbtree eraseCached returns null for a singleton cached tree"',
    'test "rbtree eraseInitCached detaches nodes while keeping cached leftmost aligned"',
    'test "rbtree eraseInitCached clears singleton cached roots before reseed"',
]

LANE_LINES = [
    "- `PHASE1_RBTREE_DIRECT_OWNER=rbtree keeps ordered Linux-style alias, low-level Linux-style alias, cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed anchors helper-local while the committed fixture still owns exact find(), findFirst(), nextMatch(), and matchIterator() duplicate-search fields and the shared host-tools smoke route keeps duplicate-range iteration plus the parked cached_leftmost_return_serials witness explicit`",
    "- `PHASE1_RBTREE_NEXT_SAFE_STEP=rbtree reopens only to keep the already-landed cached_leftmost_return_serials shared replay aligned across the manifest, direct-owner note, and any shared parity gates, or for drift inside the still-helper-local ordered Linux-style alias proof, dedicated low_level_alias_anchor, cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed anchors; do not batch a second widening into the same run`",
]

CLOSURE_PARAGRAPH = (
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

VALIDATOR_MARKERS = [
    'RBTREE_REVIEW_CHECKER_REL = Path("scripts/zigux/check-phase1-rbtree-review-packet.py")',
    'RBTREE_HELPER_REL = Path("tools/lib/rbtree.zig")',
    '(RBTREE_REVIEW_CHECKER_REL, "phase1-rbtree-review-packet"),',
]

MANIFEST_EXPECTATIONS = {
    ("lane_sequencing", "direct_anchor_followup_helpers"): [
        "tools/lib/bitmap.zig",
        "tools/lib/find_bit.zig",
        "tools/lib/rbtree.zig",
        "tools/lib/string.zig",
    ],
    ("review_anchors", "tools/lib/rbtree.zig", "shared_replay_summary"): "the committed Phase 1 fixture still carries traversal, detached-node, duplicate-search, and exact cached-leftmost-return witnesses for rbtree, while the current shared host-tools smoke replay now rechecks duplicate-range iteration plus the exact `cached_leftmost_return_serials` cached-root leftmost-return sequence on current master",
    ("review_anchors", "tools/lib/rbtree.zig", "duplicate_search_replay_keys"): [
        "find_found_key",
        "find_missing",
        "find_first_serial",
        "next_match_serials",
        "match_iterator_serials",
        "next_match_terminal_null",
    ],
    ("review_anchors", "tools/lib/rbtree.zig", "cached_leftmost_fixture_keys"): [
        "cached_leftmost_return_serials"
    ],
    ("review_anchors", "tools/lib/rbtree.zig", "cached_root_direct_review_summary"): "cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed behavior remain owned by direct helper-local anchors, while the exact `cached_leftmost_return_serials` witness now stays aligned across the helper-local tests, the shared host-tools smoke replay, and the committed fixture",
    ("review_anchors", "tools/lib/rbtree.zig", "ordered_alias_anchor"): 'test "rbtree ordered Linux-style aliases mirror traversal and replacement helpers"',
    ("review_anchors", "tools/lib/rbtree.zig", "low_level_alias_anchor"): 'test "rbtree low-level Linux-style aliases mirror node-state helpers"',
    ("review_anchors", "tools/lib/rbtree.zig", "cached_root_followup_anchors"): [
        'test "rbtree addCached returns the inserted node only when it becomes leftmost"',
        'test "rbtree findAddCached keeps cached leftmost stable while inserting misses"',
        'test "rbtree cached root keeps the leftmost pointer in sync"',
        'test "rbtree cached-root Linux-style aliases mirror the primary helpers"',
        'test "rbtree replaceNodeCached keeps non-leftmost leftmost unchanged"',
        'test "rbtree eraseCached returns null for a singleton cached tree"',
        'test "rbtree eraseInitCached detaches nodes while keeping cached leftmost aligned"',
        'test "rbtree eraseInitCached clears singleton cached roots before reseed"',
    ],
    ("review_anchors", "tools/lib/rbtree.zig", "cached_root_alias_anchor"): 'test "rbtree cached-root Linux-style aliases mirror the primary helpers"',
    ("review_anchors", "tools/lib/rbtree.zig", "review_packet_summary"): "the current shared host-tools smoke replay keeps duplicate-range iteration and the exact `cached_leftmost_return_serials` cached-root leftmost-return witness visible for rbtree, while the committed Phase 1 fixture still carries the exact traversal, detached-node, duplicate-search, and cached-leftmost-return witnesses; direct helper-local anchors continue to own cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed paths that the shared smoke route does not replay exactly",
    ("review_anchors", "tools/lib/rbtree.zig", "next_safe_step_note"): "If this helper lane reopens, keep the already-landed shared-replay promotion for `cached_leftmost_return_serials` aligned across the committed fixture, shared replay, and direct cached-root anchors; the ordered Linux-style alias proof, dedicated `low_level_alias_anchor`, and the remaining cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed behavior stay owned by direct helper-local anchors until another committed cached-root field lands.",
}

FIXTURE_EXPECTATIONS = {
    ("rbtree", "empty_root"): True,
    ("rbtree", "find_found_key"): 15,
    ("rbtree", "find_missing"): True,
    ("rbtree", "find_first_serial"): 0,
    ("rbtree", "next_match_serials"): [0, 2, 4],
    ("rbtree", "match_iterator_serials"): [0, 2, 4],
    ("rbtree", "cached_leftmost_return_serials"): [0, -1, 2, -1],
    ("rbtree", "next_match_terminal_null"): True,
}


class DuplicateTrackingDict(dict[str, object]):
    def __init__(self, pairs: list[tuple[str, object]]) -> None:
        super().__init__()
        self.duplicate_keys: list[str] = []
        for key, value in pairs:
            if key in self and key not in self.duplicate_keys:
                self.duplicate_keys.append(key)
            self[key] = value


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json(root: Path, relative_path: Path) -> object:
    return json.loads(read_text(root, relative_path), object_pairs_hook=DuplicateTrackingDict)


def duplicate_paths(data: object, prefix: tuple[str, ...] = ()) -> list[str]:
    paths: list[str] = []
    if isinstance(data, DuplicateTrackingDict):
        for key in data.duplicate_keys:
            paths.append(".".join(prefix + (key,)))
    if isinstance(data, dict):
        for key, value in data.items():
            paths.extend(duplicate_paths(value, prefix + (key,)))
    elif isinstance(data, list):
        for value in data:
            paths.extend(duplicate_paths(value, prefix))
    return paths


def nested_value(data: object, path: tuple[str, ...]) -> object:
    current = data
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def exact_count(text: str, needle: str) -> int:
    return text.count(needle)


def exact_line_count(text: str, needle: str) -> int:
    want = needle.strip()
    return sum(1 for line in text.splitlines() if line.strip() == want)


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    required = (
        HELPER_REL,
        MANIFEST_REL,
        FIXTURE_REL,
        LANE_NOTE_REL,
        CLOSURE_NOTE_REL,
        VALIDATOR_REL,
    )
    for relative_path in required:
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    helper_text = read_text(root, HELPER_REL)
    lane_text = read_text(root, LANE_NOTE_REL)
    closure_text = read_text(root, CLOSURE_NOTE_REL)
    validator_text = read_text(root, VALIDATOR_REL)

    for marker in HELPER_MARKERS:
        count = exact_count(helper_text, marker)
        if count != 1:
            failures.append(f"helper:{marker}:expected=1:actual={count}")
    for line in LANE_LINES:
        count = exact_line_count(lane_text, line)
        if count != 1:
            failures.append(f"lane:{line}:expected=1:actual={count}")
    count = exact_count(closure_text, CLOSURE_PARAGRAPH)
    if count != 1:
        failures.append(f"closure:rbtree_tie_breaker:expected=1:actual={count}")
    for marker in VALIDATOR_MARKERS:
        count = exact_count(validator_text, marker)
        if count != 1:
            failures.append(f"validator:{marker}:expected=1:actual={count}")

    try:
        manifest = load_json(root, MANIFEST_REL)
    except json.JSONDecodeError as exc:
        return [f"manifest:invalid_json:{exc.msg}:line={exc.lineno}:column={exc.colno}"]
    dup_manifest = duplicate_paths(manifest)
    if dup_manifest:
        return [f"manifest:duplicate_json_key:{path}" for path in dup_manifest]
    for path, expected in MANIFEST_EXPECTATIONS.items():
        actual = nested_value(manifest, path)
        if actual != expected:
            failures.append(f"manifest:{'.'.join(path)}")

    try:
        fixture = load_json(root, FIXTURE_REL)
    except json.JSONDecodeError as exc:
        return [f"fixture:invalid_json:{exc.msg}:line={exc.lineno}:column={exc.colno}"]
    dup_fixture = duplicate_paths(fixture)
    if dup_fixture:
        return [f"fixture:duplicate_json_key:{path}" for path in dup_fixture]
    for path, expected in FIXTURE_EXPECTATIONS.items():
        actual = nested_value(fixture, path)
        if actual != expected:
            failures.append(f"fixture:{'.'.join(path)}")

    return failures


def write_file(root: Path, relative_path: Path, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    write_file(root, HELPER_REL, "\n".join(HELPER_MARKERS) + "\n")

    manifest: dict[str, object] = {"lane_sequencing": {}, "review_anchors": {"tools/lib/rbtree.zig": {}}}
    for path, value in MANIFEST_EXPECTATIONS.items():
        current = manifest
        for key in path[:-1]:
            current = current.setdefault(key, {})  # type: ignore[assignment]
        current[path[-1]] = value
    write_file(root, MANIFEST_REL, json.dumps(manifest, indent=2) + "\n")

    fixture: dict[str, object] = {"rbtree": {}}
    for path, value in FIXTURE_EXPECTATIONS.items():
        current = fixture
        for key in path[:-1]:
            current = current.setdefault(key, {})  # type: ignore[assignment]
        current[path[-1]] = value
    write_file(root, FIXTURE_REL, json.dumps(fixture, indent=2) + "\n")

    write_file(root, LANE_NOTE_REL, "# sample\n\n" + "\n".join(LANE_LINES) + "\n")
    write_file(root, CLOSURE_NOTE_REL, "# sample\n\n" + CLOSURE_PARAGRAPH + "\n")
    write_file(root, VALIDATOR_REL, "\n".join(VALIDATOR_MARKERS) + "\n")


def run_self_test() -> int:
    cases = [
        "baseline",
        "missing_helper_marker",
        "missing_lane_line",
        "missing_closure_paragraph",
        "missing_validator_marker",
        "manifest_drift",
        "fixture_drift",
        "manifest_duplicate_key",
        "fixture_invalid_json",
    ]

    with tempfile.TemporaryDirectory(prefix="phase1-rbtree-closure-packet-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        if collect_failures(root):
            print("PHASE1_RBTREE_CLOSURE_PACKET_SELF_TEST=fail")
            return 1

        (root / HELPER_REL).write_text("\n".join(HELPER_MARKERS[1:]) + "\n", encoding="utf-8")
        if not collect_failures(root):
            print("self-test:missing_helper_marker:expected_failure")
            return 1

        build_sample_repo(root)
        (root / LANE_NOTE_REL).writeText = None
        (root / LANE_NOTE_REL).write_text("# sample\n\n" + LANE_LINES[1] + "\n", encoding="utf-8")
        if not collect_failures(root):
            print("self-test:missing_lane_line:expected_failure")
            return 1

        build_sample_repo(root)
        (root / CLOSURE_NOTE_REL).write_text("# sample\n\n", encoding="utf-8")
        if not collect_failures(root):
            print("self-test:missing_closure_paragraph:expected_failure")
            return 1

        build_sample_repo(root)
        (root / VALIDATOR_REL).write_text("\n".join(VALIDATOR_MARKERS[1:]) + "\n", encoding="utf-8")
        if not collect_failures(root):
            print("self-test:missing_validator_marker:expected_failure")
            return 1

        build_sample_repo(root)
        manifest = json.loads((root / MANIFEST_REL).read_text(encoding="utf-8"))
        manifest["review_anchors"]["tools/lib/rbtree.zig"]["cached_root_alias_anchor"] = "drift"
        (root / MANIFEST_REL).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        if not collect_failures(root):
            print("self-test:manifest_drift:expected_failure")
            return 1

        build_sample_repo(root)
        fixture = json.loads((root / FIXTURE_REL).read_text(encoding="utf-8"))
        fixture["rbtree"]["cached_leftmost_return_serials"] = [0]
        (root / FIXTURE_REL).write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        if not collect_failures(root):
            print("self-test:fixture_drift:expected_failure")
            return 1

        build_sample_repo(root)
        manifest_text = (root / MANIFEST_REL).read_text(encoding="utf-8")
        (root / MANIFEST_REL).write_text(
            manifest_text.replace(
                '      "cached_root_alias_anchor": "test \\"rbtree cached-root Linux-style aliases mirror the primary helpers\\"",',
                '      "cached_root_alias_anchor": "drift",\n      "cached_root_alias_anchor": "test \\"rbtree cached-root Linux-style aliases mirror the primary helpers\\"",',
                1,
            ),
            encoding="utf-8",
        )
        if not collect_failures(root):
            print("self-test:manifest_duplicate_key:expected_failure")
            return 1

        build_sample_repo(root)
        (root / FIXTURE_REL).write_text("{\n", encoding="utf-8")
        if not collect_failures(root):
            print("self-test:fixture_invalid_json:expected_failure")
            return 1

    print("PHASE1_RBTREE_CLOSURE_PACKET_SELF_TEST=pass")
    print(f"PHASE1_RBTREE_CLOSURE_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument(
        "--write-sample-root",
        help="write a sample marker-faithful repo root for focused replay",
    )
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        build_sample_repo(Path(args.write_sample_root).resolve())
        print(f"PHASE1_RBTREE_CLOSURE_PACKET_SAMPLE_ROOT={Path(args.write_sample_root).resolve()}")
        return 0

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_RBTREE_CLOSURE_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_RBTREE_CLOSURE_PACKET=pass")
    print(f"PHASE1_RBTREE_CLOSURE_PACKET_HELPER={HELPER_REL.as_posix()}")
    print(f"PHASE1_RBTREE_CLOSURE_PACKET_MANIFEST={MANIFEST_REL.as_posix()}")
    print(f"PHASE1_RBTREE_CLOSURE_PACKET_FIXTURE={FIXTURE_REL.as_posix()}")
    print(f"PHASE1_RBTREE_CLOSURE_PACKET_LANE_NOTE={LANE_NOTE_REL.as_posix()}")
    print(f"PHASE1_RBTREE_CLOSURE_PACKET_CLOSURE_NOTE={CLOSURE_NOTE_REL.as_posix()}")
    print(f"PHASE1_RBTREE_CLOSURE_PACKET_VALIDATOR={VALIDATOR_REL.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())