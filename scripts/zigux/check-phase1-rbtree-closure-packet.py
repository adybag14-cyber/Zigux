#!/usr/bin/env python3
"""Guard the current Phase 1 rbtree closure packet across helper, docs, fixture, smoke, and validator."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

HELPER_REL = Path("tools/lib/rbtree.zig")
LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
CLOSURE_NOTE_REL = Path("Documentation/zigux/phase1-closure.md")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
FIXTURE_REL = Path("zigux/tests/fixtures/phase1_helpers.json")
SMOKE_REL = Path("zigux/tests/phase1_host_tools_smoke.zig")
VALIDATOR_REL = Path("scripts/zigux/validate-phase1-closure.py")

REQUIRED_FILES = (
    HELPER_REL,
    LANE_NOTE_REL,
    CLOSURE_NOTE_REL,
    MANIFEST_REL,
    FIXTURE_REL,
    SMOKE_REL,
    VALIDATOR_REL,
)

HELPER_MARKERS = (
    'test "rbtree ordered Linux-style aliases mirror traversal and replacement helpers"',
    'test "rbtree low-level Linux-style aliases mirror node-state helpers"',
    'test "rbtree cached-root Linux-style aliases mirror the primary helpers"',
    'test "rbtree addCached returns the inserted node only when it becomes leftmost"',
    'test "rbtree eraseInitCached clears singleton cached roots before reseed"',
)

LANE_NOTE_MARKERS = (
    "- `PHASE1_RBTREE_DIRECT_OWNER=rbtree keeps ordered Linux-style alias, low-level Linux-style alias, cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed anchors helper-local while the committed fixture still owns exact find(), findFirst(), nextMatch(), and matchIterator() duplicate-search fields and the shared host-tools smoke route keeps duplicate-range iteration plus the parked cached_leftmost_return_serials witness explicit`",
    "- `PHASE1_RBTREE_NEXT_SAFE_STEP=rbtree reopens only to keep the already-landed cached_leftmost_return_serials shared replay aligned across the manifest, direct-owner note, and any shared parity gates, or for drift inside the still-helper-local ordered Linux-style alias proof, dedicated low_level_alias_anchor, cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed anchors; do not batch a second widening into the same run`",
)

CLOSURE_NOTE_MARKERS = (
    "- `PHASE1_RBTREE_REVIEW_GUARD=python3 scripts/zigux/check-phase1-rbtree-review-packet.py exact-checks helper-local rbtree anchors plus the committed duplicate-search and cached-leftmost replay packet across the helper, closure note, lane note, manifest, fixture, and shared smoke route`",
    "A second current helper-family tie-breaker inside that packet is the `rbtree` direct-anchor route: keep `tools/lib/rbtree.zig` parked unless a fresh reread finds drift in the helper-local ordered Linux-style alias proof, the dedicated manifest-backed `low_level_alias_anchor`, the dedicated manifest-backed `cached_root_alias_anchor`, the cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, or reseed anchors, or drift in the already-committed duplicate-search replay fields or exact `cached_leftmost_return_serials` witness.",
    "Current `master` also keeps the companion `cached_root_transition_serials` witness shared instead of helper-local only: `zigux/tests/fixtures/phase1_helpers.json` still records the exact cached-root erase, replacement, and detach transition packet, and `zigux/tests/phase1_host_tools_smoke.zig` already rechecks the same `[0, 0, 4, 2]` sequence beside the parked `cached_leftmost_return_serials` witness.",
)

SMOKE_MARKERS = (
    'const rbtree = @import("rbtree");',
    'try std.testing.expect(@hasDecl(rbtree, "find"));',
    'try std.testing.expect(@hasDecl(rbtree, "matchIterator"));',
    "var cached_leftmost_return_serials: [4]i32 = undefined;",
    "try std.testing.expectEqualSlices(i32, &.{ 0, -1, 2, -1 }, &cached_leftmost_return_serials);",
    "var cached_root_transition_serials: [4]i32 = undefined;",
    "try std.testing.expectEqualSlices(i32, &.{ 0, 0, 4, 2 }, &cached_root_transition_serials);",
)

VALIDATOR_MARKERS = (
    'RBTREE_REVIEW_CHECKER_REL = Path("scripts/zigux/check-phase1-rbtree-review-packet.py")',
    '"rbtree_review_guard": "`PHASE1_RBTREE_REVIEW_GUARD=python3 scripts/zigux/check-phase1-rbtree-review-packet.py exact-checks helper-local rbtree anchors plus the committed duplicate-search and cached-leftmost replay packet across the helper, closure note, lane note, manifest, fixture, and shared smoke route`",',
    'failures.extend(require_expected_mapping(f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/rbtree.zig", review_anchors.get("tools/lib/rbtree.zig"), EXPECTED_RBTREE_REVIEW_ANCHORS))',
)

EXPECTED_MANIFEST_FIELDS = {
    "phase1_helper_replay_anchor": 'test "phase1 host-tools smoke exercises live helper behavior"',
    "shared_replay_summary": "the committed Phase 1 fixture still carries traversal, detached-node, duplicate-search, and exact cached-leftmost-return witnesses for rbtree, while the current shared host-tools smoke replay now rechecks duplicate-range iteration plus the exact `cached_leftmost_return_serials` cached-root leftmost-return sequence on current master",
    "cached_leftmost_fixture_keys": ["cached_leftmost_return_serials"],
    "cached_root_transition_fixture_keys": ["cached_root_transition_serials"],
    "ordered_alias_anchor": 'test "rbtree ordered Linux-style aliases mirror traversal and replacement helpers"',
    "low_level_alias_anchor": 'test "rbtree low-level Linux-style aliases mirror node-state helpers"',
    "cached_root_alias_anchor": 'test "rbtree cached-root Linux-style aliases mirror the primary helpers"',
    "review_packet_summary": "the current shared host-tools smoke replay keeps duplicate-range iteration and the exact `cached_leftmost_return_serials` cached-root leftmost-return witness visible for rbtree, while the committed Phase 1 fixture still carries the exact traversal, detached-node, duplicate-search, and cached-leftmost-return witnesses; direct helper-local anchors continue to own cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed paths that the shared smoke route does not replay exactly",
    "next_safe_step_note": "If this helper lane reopens, keep the already-landed shared-replay promotion for `cached_leftmost_return_serials` aligned across the committed fixture, shared replay, and direct cached-root anchors; the ordered Linux-style alias proof, dedicated `low_level_alias_anchor`, and the remaining cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed behavior stay owned by direct helper-local anchors until another committed cached-root field lands.",
}

EXPECTED_FIXTURE_VALUES = {
    "next_match_serials": [0, 2, 4],
    "match_iterator_serials": [0, 2, 4],
    "cached_leftmost_return_serials": [0, -1, 2, -1],
    "cached_root_transition_serials": [0, 0, 4, 2],
    "next_match_terminal_null": True,
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


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json_with_duplicate_tracking(text: str) -> object:
    return json.loads(text, object_pairs_hook=DuplicateTrackingDict)


def collect_duplicate_json_key_paths(data: object, prefix: tuple[str, ...] = ()) -> list[str]:
    paths: list[str] = []
    if isinstance(data, DuplicateTrackingDict):
        for key in data.duplicate_keys:
            paths.append(".".join(prefix + (key,)))
    if isinstance(data, dict):
        for key, value in data.items():
            paths.extend(collect_duplicate_json_key_paths(value, prefix + (key,)))
    elif isinstance(data, list):
        for value in data:
            paths.extend(collect_duplicate_json_key_paths(value, prefix))
    return paths


def require_exact_occurrence(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_exact_value(label: str, actual: object, expected: object) -> list[str]:
    return [] if actual == expected else [f"{label}:expected={expected!r}:actual={actual!r}"]


def collect_failures(root: Path) -> list[str]:
    failures = [f"missing_file:{path.as_posix()}" for path in REQUIRED_FILES if not (root / path).is_file()]
    if failures:
        return failures

    for marker in HELPER_MARKERS:
        failures.extend(require_exact_occurrence(load_text(root, HELPER_REL), f"{HELPER_REL.as_posix()}:{marker}", marker))
    for marker in LANE_NOTE_MARKERS:
        failures.extend(require_exact_occurrence(load_text(root, LANE_NOTE_REL), f"{LANE_NOTE_REL.as_posix()}:{marker}", marker))
    for marker in CLOSURE_NOTE_MARKERS:
        failures.extend(require_exact_occurrence(load_text(root, CLOSURE_NOTE_REL), f"{CLOSURE_NOTE_REL.as_posix()}:{marker}", marker))
    for marker in SMOKE_MARKERS:
        failures.extend(require_exact_occurrence(load_text(root, SMOKE_REL), f"{SMOKE_REL.as_posix()}:{marker}", marker))
    for marker in VALIDATOR_MARKERS:
        failures.extend(require_exact_occurrence(load_text(root, VALIDATOR_REL), f"{VALIDATOR_REL.as_posix()}:{marker}", marker))

    try:
        manifest = load_json_with_duplicate_tracking(load_text(root, MANIFEST_REL))
        fixture = load_json_with_duplicate_tracking(load_text(root, FIXTURE_REL))
    except json.JSONDecodeError as exc:
        return [f"invalid_json:{exc.msg}:line={exc.lineno}:column={exc.colno}"]

    for path in collect_duplicate_json_key_paths(manifest):
        failures.append(f"{MANIFEST_REL.as_posix()}:duplicate_json_key:{path}")
    for path in collect_duplicate_json_key_paths(fixture):
        failures.append(f"{FIXTURE_REL.as_posix()}:duplicate_json_key:{path}")

    if not isinstance(manifest, dict):
        failures.append(f"{MANIFEST_REL.as_posix()}:expected=dict")
        return failures
    if not isinstance(fixture, dict):
        failures.append(f"{FIXTURE_REL.as_posix()}:expected=dict")
        return failures

    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        failures.append(f"{MANIFEST_REL.as_posix()}:review_anchors:expected=dict")
        return failures
    rbtree_packet = review_anchors.get("tools/lib/rbtree.zig")
    if not isinstance(rbtree_packet, dict):
        failures.append(f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/rbtree.zig:expected=dict")
        return failures

    for key, expected in EXPECTED_MANIFEST_FIELDS.items():
        failures.extend(require_exact_value(f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/rbtree.zig.{key}", rbtree_packet.get(key), expected))

    rbtree_fixture = fixture.get("rbtree")
    if not isinstance(rbtree_fixture, dict):
        failures.append(f"{FIXTURE_REL.as_posix()}:rbtree:expected=dict")
        return failures
    for key, expected in EXPECTED_FIXTURE_VALUES.items():
        failures.extend(require_exact_value(f"{FIXTURE_REL.as_posix()}:rbtree.{key}", rbtree_fixture.get(key), expected))

    return failures


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, data: object) -> None:
    write_text(path, json.dumps(data, indent=2) + "\n")


def sample_manifest() -> dict[str, object]:
    return {
        "review_anchors": {
            "tools/lib/rbtree.zig": {
                **EXPECTED_MANIFEST_FIELDS,
            }
        }
    }


def sample_fixture() -> dict[str, object]:
    return {
        "rbtree": {
            **EXPECTED_FIXTURE_VALUES,
        }
    }


def write_sample_root(root: Path) -> None:
    write_text(root / HELPER_REL, "\n".join(HELPER_MARKERS) + "\n")
    write_text(root / LANE_NOTE_REL, "\n".join(LANE_NOTE_MARKERS) + "\n")
    write_text(root / CLOSURE_NOTE_REL, "\n".join(CLOSURE_NOTE_MARKERS) + "\n")
    write_text(root / SMOKE_REL, "\n".join(SMOKE_MARKERS) + "\n")
    write_text(root / VALIDATOR_REL, "\n".join(VALIDATOR_MARKERS) + "\n")
    write_json(root / MANIFEST_REL, sample_manifest())
    write_json(root / FIXTURE_REL, sample_fixture())


def remove_text(path: Path, needle: str) -> None:
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(needle + "\n", "", 1).replace(needle, "", 1), encoding="utf-8")


def insert_duplicate_key(path: Path, needle: str, duplicate_line: str) -> None:
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(needle, duplicate_line + "\n" + needle, 1), encoding="utf-8")


def mutate_fixture_value(path: Path, key: str, value: object) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    data["rbtree"][key] = value
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def mutate_manifest_value(path: Path, key: str, value: object) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    data["review_anchors"]["tools/lib/rbtree.zig"][key] = value
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, object | None]] = [
        ("baseline", None),
        ("missing_helper_file", lambda root: (root / HELPER_REL).unlink()),
        ("missing_closure_marker", lambda root: remove_text(root / CLOSURE_NOTE_REL, CLOSURE_NOTE_MARKERS[0])),
        ("missing_transition_paragraph", lambda root: remove_text(root / CLOSURE_NOTE_REL, CLOSURE_NOTE_MARKERS[2])),
        ("missing_lane_next_step", lambda root: remove_text(root / LANE_NOTE_REL, LANE_NOTE_MARKERS[1])),
        ("missing_helper_anchor", lambda root: remove_text(root / HELPER_REL, HELPER_MARKERS[2])),
        ("missing_smoke_transition", lambda root: remove_text(root / SMOKE_REL, SMOKE_MARKERS[6])),
        ("missing_validator_guard", lambda root: remove_text(root / VALIDATOR_REL, VALIDATOR_MARKERS[1])),
        ("stale_manifest_summary", lambda root: mutate_manifest_value(root / MANIFEST_REL, "shared_replay_summary", "drifted summary")),
        ("stale_manifest_next_step", lambda root: mutate_manifest_value(root / MANIFEST_REL, "next_safe_step_note", "drifted note")),
        ("stale_fixture_leftmost", lambda root: mutate_fixture_value(root / FIXTURE_REL, "cached_leftmost_return_serials", [1, 2, 3, 4])),
        ("stale_fixture_transition", lambda root: mutate_fixture_value(root / FIXTURE_REL, "cached_root_transition_serials", [9, 9, 9, 9])),
        ("duplicate_fixture_key", lambda root: insert_duplicate_key(root / FIXTURE_REL, '    "cached_leftmost_return_serials": [', '    "cached_leftmost_return_serials": [9],')),
    ]

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-rbtree-closure-") as tmpdir:
            root = Path(tmpdir)
            write_sample_root(root)
            if mutate is not None:
                mutate(root)
            failures = collect_failures(root)
            if name == "baseline":
                if failures:
                    print(f"phase1-rbtree-closure-self-test:{name}:unexpected={failures}")
                    return 1
            elif not failures:
                print(f"phase1-rbtree-closure-self-test:{name}:expected_failure")
                return 1

    print("PHASE1_RBTREE_CLOSURE_PACKET_SELF_TEST=pass")
    print(f"PHASE1_RBTREE_CLOSURE_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-test")
    parser.add_argument("--write-sample-root", help="write a passing sample tree to the given path")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        write_sample_root(Path(args.write_sample_root).resolve())
        return 0

    failures = collect_failures(repo_root(args.root))
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_RBTREE_CLOSURE_PACKET=pass")
    print(f"PHASE1_RBTREE_CLOSURE_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print("PHASE1_RBTREE_CLOSURE_PACKET_REQUIRED_MARKER_COUNT=20")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
