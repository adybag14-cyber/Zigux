#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
PHASE1_LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
BENCH_CHECKER_REL = Path("scripts/zigux/check-phase1-bench.py")

REQUIRED_FILES = (
    PHASE1_CLOSURE_REL,
    PHASE1_LANE_NOTE_REL,
    MANIFEST_REL,
    BENCH_CHECKER_REL,
)

EXPECTED_CLOSURE_MARKERS = (
    "`PHASE1_RBTREE_BENCH_GUARD=scripts/zigux/check-phase1-bench.py now hard-codes PHASE1_BENCH_RBTREE_ITERATIONS=4000 and exact-checks PHASE1_BENCH_RBTREE_CHECKSUM, PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM, PHASE1_BENCH_FIND_ADD_CHECKSUM, PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM, and PHASE1_BENCH_RBTREE_CACHED_CHECKSUM when the broader expectations packet returns`",
)

EXPECTED_LANE_MARKERS = (
    "`PHASE1_RBTREE_DIRECT_OWNER=rbtree keeps ordered Linux-style alias, low-level Linux-style alias, cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed anchors helper-local while the committed fixture still owns exact find(), findFirst(), nextMatch(), and matchIterator() duplicate-search fields and the shared host-tools smoke route keeps duplicate-range iteration plus the parked cached_leftmost_return_serials witness explicit`",
    "`PHASE1_RBTREE_NEXT_SAFE_STEP=rbtree reopens only to keep the already-landed cached_leftmost_return_serials shared replay aligned across the manifest, direct-owner note, and any shared parity gates, or for drift inside the still-helper-local ordered Linux-style alias proof, dedicated low_level_alias_anchor, cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed anchors; do not batch a second widening into the same run`",
)

EXPECTED_MANIFEST_MAPPING = {
    "shared_replay_summary": "the committed Phase 1 fixture still carries traversal, detached-node, duplicate-search, and exact cached-leftmost-return witnesses for rbtree, while the current shared host-tools smoke replay now rechecks duplicate-range iteration plus the exact `cached_leftmost_return_serials` cached-root leftmost-return sequence on current master",
    "cached_leftmost_fixture_keys": ["cached_leftmost_return_serials"],
    "cached_root_direct_review_summary": "cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed behavior remain owned by direct helper-local anchors, while the exact `cached_leftmost_return_serials` witness now stays aligned across the helper-local tests, the shared host-tools smoke replay, and the committed fixture",
    "ordered_alias_anchor": 'test "rbtree ordered Linux-style aliases mirror traversal and replacement helpers"',
    "low_level_alias_anchor": 'test "rbtree low-level Linux-style aliases mirror node-state helpers"',
    "cached_root_alias_anchor": 'test "rbtree cached-root Linux-style aliases mirror the primary helpers"',
    "review_packet_summary": "the current shared host-tools smoke replay keeps duplicate-range iteration and the exact `cached_leftmost_return_serials` cached-root leftmost-return witness visible for rbtree, while the committed Phase 1 fixture still carries the exact traversal, detached-node, duplicate-search, and cached-leftmost-return witnesses; direct helper-local anchors continue to own cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed paths that the shared smoke route does not replay exactly",
    "next_safe_step_note": "If this helper lane reopens, keep the already-landed shared-replay promotion for `cached_leftmost_return_serials` aligned across the committed fixture, shared replay, and direct cached-root anchors; the ordered Linux-style alias proof, dedicated `low_level_alias_anchor`, and the remaining cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed behavior stay owned by direct helper-local anchors until another committed cached-root field lands.",
}

EXPECTED_BENCH_MARKERS = (
    '"PHASE1_BENCH_RBTREE_ITERATIONS": 4000,',
    '"PHASE1_BENCH_RBTREE_CHECKSUM",',
    '"PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM",',
    '"PHASE1_BENCH_FIND_ADD_CHECKSUM",',
    '"PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM",',
    '"PHASE1_BENCH_RBTREE_CACHED_CHECKSUM",',
    'RBTREE_REQUIRED_ITERATIONS = {"PHASE1_BENCH_RBTREE_ITERATIONS"}',
    'RBTREE_REQUIRED_EXACT_CHECKSUMS = {',
    '"rbtree_bench_fn": "fn rbtreeBench() struct { checksum: u64 } {",',
    '"rbtree_postorder_safe_fn": "fn rbtreePostorderSafeBench() struct { checksum: u64 } {",',
    '"rbtree_find_add_fn": "fn rbtreeFindAddBench() struct { checksum: u64 } {",',
    '"rbtree_duplicate_fn": "fn rbtreeDuplicateBench() struct { checksum: u64 } {",',
    '"rbtree_cached_fn": "fn rbtreeCachedBench() struct { checksum: u64 } {",',
    '"rbtree_iterations_print": \'try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_ITERATIONS={d}\\n", .{iterations_rbtree});\'',
    '"rbtree_checksum_print": \'try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_CHECKSUM={d}\\n", .{rbtree_result.checksum});\'',
    '"rbtree_postorder_safe_print": \'try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM={d}\\n", .{rbtree_postorder_safe_result.checksum});\'',
    '"rbtree_find_add_print": \'try stdout_writer.interface.print("PHASE1_BENCH_FIND_ADD_CHECKSUM={d}\\n", .{rbtree_find_add_result.checksum});\'',
    '"rbtree_duplicate_print": \'try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM={d}\\n", .{rbtree_duplicate_result.checksum});\'',
    '"rbtree_cached_print": \'try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_CACHED_CHECKSUM={d}\\n", .{rbtree_cached_result.checksum});\'',
    'return ("expectations_missing_rbtree_iterations", missing_rbtree_iterations)',
    'return ("expectations_checksums_rbtree_exact_required", key)',
    'return ("missing_rbtree_iterations", [key])',
    'return ("rbtree_iteration_mismatch", (key, expected, actual))',
    'return ("missing_rbtree_exact_checksums", missing_exact)',
)


class DuplicateTrackingDict(dict[str, object]):
    def __init__(self, pairs: list[tuple[str, object]]) -> None:
        super().__init__()
        self.duplicate_keys: list[str] = []
        for key, value in pairs:
            if key in self and key not in self.duplicate_keys:
                self.duplicate_keys.append(key)
            self[key] = value


def repo_root(override: str | None) -> Path:
    return Path(override).resolve() if override else DEFAULT_ROOT


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json_text(text: str) -> object:
    return json.loads(text, object_pairs_hook=DuplicateTrackingDict)


def require_exact_occurrence(text: str, label: str, needle: str) -> list[str]:
    count = text.count(needle)
    return [] if count == 1 else [f"{label}:expected_once:actual_count={count}:{needle}"]


def require_present(text: str, label: str, needle: str) -> list[str]:
    count = text.count(needle)
    return [] if count >= 1 else [f"{label}:missing:{needle}"]


def require_expected_mapping(prefix: str, actual: object, expected: dict[str, object]) -> list[str]:
    if not isinstance(actual, dict):
        return [f"{prefix}:expected=dict:actual={type(actual).__name__}"]
    failures: list[str] = []
    for key, expected_value in expected.items():
        actual_value = actual.get(key)
        if actual_value != expected_value:
            failures.append(f"{prefix}.{key}:expected={expected_value!r}:actual={actual_value!r}")
    return failures


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


def collect_failures(root: Path) -> list[str]:
    failures = [f"missing_file:{path.as_posix()}" for path in REQUIRED_FILES if not (root / path).is_file()]
    if failures:
        return failures

    closure_text = load_text(root, PHASE1_CLOSURE_REL)
    for marker in EXPECTED_CLOSURE_MARKERS:
        failures.extend(require_exact_occurrence(closure_text, f"{PHASE1_CLOSURE_REL.as_posix()}:rbtree_bench_guard", marker))

    lane_text = load_text(root, PHASE1_LANE_NOTE_REL)
    for index, marker in enumerate(EXPECTED_LANE_MARKERS, start=1):
        failures.extend(require_exact_occurrence(lane_text, f"{PHASE1_LANE_NOTE_REL.as_posix()}:lane_marker_{index}", marker))

    try:
        manifest = load_json_text(load_text(root, MANIFEST_REL))
    except json.JSONDecodeError as exc:
        return [f"{MANIFEST_REL.as_posix()}:invalid_json:{exc.msg}:line={exc.lineno}:column={exc.colno}"]

    if not isinstance(manifest, dict):
        return [f"{MANIFEST_REL.as_posix()}:expected=dict:actual={type(manifest).__name__}"]

    duplicate_paths = collect_duplicate_json_key_paths(manifest)
    if duplicate_paths:
        return [f"{MANIFEST_REL.as_posix()}:duplicate_json_key:{path}" for path in duplicate_paths]

    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        return [f"{MANIFEST_REL.as_posix()}:review_anchors:expected=dict:actual={type(review_anchors).__name__}"]

    failures.extend(
        require_expected_mapping(
            f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/rbtree.zig",
            review_anchors.get("tools/lib/rbtree.zig"),
            EXPECTED_MANIFEST_MAPPING,
        )
    )

    bench_text = load_text(root, BENCH_CHECKER_REL)
    for index, marker in enumerate(EXPECTED_BENCH_MARKERS, start=1):
        failures.extend(require_present(bench_text, f"{BENCH_CHECKER_REL.as_posix()}:marker_{index}", marker))

    return failures


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_fixture_tree(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        write_text(root / relative_path, f"fixture for {relative_path.as_posix()}\n")

    write_text(root / PHASE1_CLOSURE_REL, "# Phase 1 Closure\n\n" + "\n".join(EXPECTED_CLOSURE_MARKERS) + "\n")
    write_text(root / PHASE1_LANE_NOTE_REL, "# Phase 1 Host-Helper Lane Sequencing\n\n" + "\n".join(EXPECTED_LANE_MARKERS) + "\n")
    write_text(
        root / MANIFEST_REL,
        json.dumps(
            {
                "phase": "Phase 1",
                "status": "closed",
                "review_anchors": {
                    "tools/lib/rbtree.zig": EXPECTED_MANIFEST_MAPPING,
                },
            },
            indent=2,
        )
        + "\n",
    )
    write_text(root / BENCH_CHECKER_REL, "\n".join(EXPECTED_BENCH_MARKERS) + "\n")


def mutate_manifest_key(root: Path, key: str, value: object | None, *, remove: bool = False) -> None:
    path = root / MANIFEST_REL
    payload = json.loads(path.read_text(encoding="utf-8"))
    anchors = payload["review_anchors"]["tools/lib/rbtree.zig"]
    if remove:
        del anchors[key]
    else:
        anchors[key] = value
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, object | None]] = [
        ("baseline", None),
        ("missing_closure_guard", lambda root: write_text(root / PHASE1_CLOSURE_REL, "# Phase 1 Closure\n")),
        ("missing_lane_direct_owner", lambda root: write_text(root / PHASE1_LANE_NOTE_REL, "# Phase 1 Host-Helper Lane Sequencing\n\n" + EXPECTED_LANE_MARKERS[1] + "\n")),
        ("missing_lane_next_step", lambda root: write_text(root / PHASE1_LANE_NOTE_REL, "# Phase 1 Host-Helper Lane Sequencing\n\n" + EXPECTED_LANE_MARKERS[0] + "\n")),
        ("missing_manifest_cached_root_alias_anchor", lambda root: mutate_manifest_key(root, "cached_root_alias_anchor", None, remove=True)),
        ("stale_manifest_review_summary", lambda root: mutate_manifest_key(root, "review_packet_summary", "drifted value")),
        ("missing_bench_rbtree_iterations_marker", lambda root: write_text(root / BENCH_CHECKER_REL, load_text(root, BENCH_CHECKER_REL).replace(EXPECTED_BENCH_MARKERS[0] + "\n", "", 1))),
        ("missing_bench_rbtree_exact_reason", lambda root: write_text(root / BENCH_CHECKER_REL, load_text(root, BENCH_CHECKER_REL).replace(EXPECTED_BENCH_MARKERS[-1] + "\n", "", 1))),
        ("duplicate_manifest_key", lambda root: write_text(root / MANIFEST_REL, '{\n  "review_anchors": {\n    "tools/lib/rbtree.zig": {\n      "shared_replay_summary": "a",\n      "shared_replay_summary": "b"\n    }\n  }\n}\n')),
    ]

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-rbtree-bench-guard-") as tmp:
            root = Path(tmp)
            make_fixture_tree(root)
            if mutate is not None:
                mutate(root)
            failures = collect_failures(root)
            if name == "baseline":
                if failures:
                    print(f"phase1-rbtree-bench-guard-self-test:{name}:unexpected={failures}")
                    return 1
            elif not failures:
                print(f"phase1-rbtree-bench-guard-self-test:{name}:expected_failure")
                return 1

    print("PHASE1_RBTREE_BENCH_GUARD_SELF_TEST=pass")
    print(f"PHASE1_RBTREE_BENCH_GUARD_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the current Phase 1 rbtree bench packet across the live Lane 16 reminder surfaces.")
    parser.add_argument("--root", help="Override the repository root for validation.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker self-tests.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_RBTREE_BENCH_GUARD=fail")
        print("PHASE1_RBTREE_BENCH_GUARD_FAILURES_START")
        for failure in failures:
            print(failure)
        print("PHASE1_RBTREE_BENCH_GUARD_FAILURES_END")
        return 1

    print("PHASE1_RBTREE_BENCH_GUARD=pass")
    print(f"PHASE1_RBTREE_BENCH_GUARD_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_RBTREE_BENCH_GUARD_REQUIRED_MARKER_COUNT="
        f"{len(EXPECTED_CLOSURE_MARKERS) + len(EXPECTED_LANE_MARKERS) + len(EXPECTED_MANIFEST_MAPPING) + len(EXPECTED_BENCH_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
