#!/usr/bin/env python3
"""Guard the live Phase 1 rbtree bench packet on current master."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

BENCH_CHECKER_REL = Path("scripts/zigux/check-phase1-bench.py")
CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
SMOKE_REL = Path("zigux/tests/phase1_host_tools_smoke.zig")


class DuplicateTrackingDict(dict[str, object]):
    def __init__(self, pairs: list[tuple[str, object]]) -> None:
        super().__init__()
        self.duplicate_keys: list[str] = []
        for key, value in pairs:
            if key in self and key not in self.duplicate_keys:
                self.duplicate_keys.append(key)
            self[key] = value


EXPECTED_CLOSURE_LINE = (
    "- `PHASE1_RBTREE_BENCH_GUARD=scripts/zigux/check-phase1-bench.py now hard-codes "
    "PHASE1_BENCH_RBTREE_ITERATIONS=4000 and exact-checks PHASE1_BENCH_RBTREE_CHECKSUM, "
    "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM, PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM, "
    "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM, and PHASE1_BENCH_RBTREE_CACHED_CHECKSUM when "
    "the broader expectations packet returns`"
)

EXPECTED_BENCH_MARKERS = [
    '    "PHASE1_BENCH_RBTREE_ITERATIONS": 4000,',
    '    "PHASE1_BENCH_RBTREE_CHECKSUM",',
    '    "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM",',
    '    "PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM",',
    '    "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM",',
    '    "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM",',
    '    "rbtree_bench_fn": "fn rbtreeBench() struct { checksum: u64 } {",',
    '    "rbtree_postorder_safe_fn": "fn rbtreePostorderSafeBench() struct { checksum: u64 } {",',
    '    "rbtree_find_add_fn": "fn rbtreeFindAddBench() struct { checksum: u64 } {",',
    '    "rbtree_duplicate_fn": "fn rbtreeDuplicateBench() struct { checksum: u64 } {",',
    '    "rbtree_cached_fn": "fn rbtreeCachedBench() struct { checksum: u64 } {",',
    '    "rbtree_insert": "rbtree.add(&entry.node, &root, less);",',
    '    "rbtree_postorder": "var node = rbtree.firstPostorder(&root);",',
    '    "rbtree_find_add": "const existing = rbtree.findAdd(&probe.node, &root, cmp);",',
    '    "rbtree_duplicate_range": "var iter = rbtree.matchIterator(&duplicate_key, &root, key_cmp);",',
    '    "rbtree_cached_leftmost": "const promoted_leftmost = rbtree.eraseCached(&entries[1].node, &cached_root);",',
    '        return ("expectations_missing_rbtree_iterations", missing_rbtree_iterations)',
    '                return ("expectations_checksums_rbtree_exact_required", key)',
    '            return ("missing_rbtree_iterations", [key])',
    '            return ("missing_rbtree_exact_checksums", missing_exact)',
]

EXPECTED_SMOKE_MARKERS = [
    "var iter = rbtree.matchIterator(&duplicate_key, &tree_root, RbtreeSmokeEntry.cmp);",
    "var cached_leftmost_return_serials: [4]i32 = undefined;",
    "try std.testing.expectEqualSlices(i32, &.{ 0, -1, 2, -1 }, &cached_leftmost_return_serials);",
]

EXPECTED_MANIFEST_VALUES = {
    "cached_leftmost_fixture_keys": ["cached_leftmost_return_serials"],
    "cached_root_alias_anchor": 'test "rbtree cached-root Linux-style aliases mirror the primary helpers"',
    "shared_replay_summary": (
        "the committed Phase 1 fixture still carries traversal, detached-node, duplicate-search, "
        "and exact cached-leftmost-return witnesses for rbtree, while the current shared host-tools "
        "smoke replay now rechecks duplicate-range iteration plus the exact `cached_leftmost_return_serials` "
        "cached-root leftmost-return sequence on current master"
    ),
    "cached_root_direct_review_summary": (
        "cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, "
        "detach, and reseed behavior remain owned by direct helper-local anchors, while the exact "
        "`cached_leftmost_return_serials` witness now stays aligned across the helper-local tests, "
        "the shared host-tools smoke replay, and the committed fixture"
    ),
    "review_packet_summary": (
        "the current shared host-tools smoke replay keeps duplicate-range iteration and the exact "
        "`cached_leftmost_return_serials` cached-root leftmost-return witness visible for rbtree, while "
        "the committed Phase 1 fixture still carries the exact traversal, detached-node, duplicate-search, "
        "and cached-leftmost-return witnesses; direct helper-local anchors continue to own cached-root "
        "insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed "
        "paths that the shared smoke route does not replay exactly"
    ),
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json(root: Path, relative_path: Path) -> object:
    return json.loads(
        load_text(root, relative_path),
        object_pairs_hook=DuplicateTrackingDict,
    )


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


def require_once(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    return [] if count == 1 else [f"{label}:expected_once:actual_count={count}"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for relative_path in (BENCH_CHECKER_REL, CLOSURE_REL, MANIFEST_REL, SMOKE_REL):
        if not (root / relative_path).is_file():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    bench_text = load_text(root, BENCH_CHECKER_REL)
    closure_text = load_text(root, CLOSURE_REL)
    smoke_text = load_text(root, SMOKE_REL)
    manifest = load_json(root, MANIFEST_REL)

    if not isinstance(manifest, dict):
        return [f"{MANIFEST_REL.as_posix()}:expected=dict:actual={type(manifest).__name__}"]

    duplicate_paths = collect_duplicate_json_key_paths(manifest)
    if duplicate_paths:
        return [f"{MANIFEST_REL.as_posix()}:duplicate_json_key:{path}" for path in duplicate_paths]

    failures.extend(require_once(closure_text, "closure:rbtree_bench_guard", EXPECTED_CLOSURE_LINE))

    for marker in EXPECTED_BENCH_MARKERS:
        failures.extend(require_once(bench_text, f"bench:{marker}", marker))

    for marker in EXPECTED_SMOKE_MARKERS:
        failures.extend(require_once(smoke_text, f"smoke:{marker}", marker))

    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        return [f"{MANIFEST_REL.as_posix()}:review_anchors:expected=dict"]

    rbtree_packet = review_anchors.get("tools/lib/rbtree.zig")
    if not isinstance(rbtree_packet, dict):
        return [f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/rbtree.zig:expected=dict"]

    for key, expected in EXPECTED_MANIFEST_VALUES.items():
        actual = rbtree_packet.get(key)
        if actual != expected:
            failures.append(
                f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/rbtree.zig.{key}:"
                f"expected={expected!r}:actual={actual!r}"
            )

    return failures


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    write_text(root / BENCH_CHECKER_REL, "\n".join(EXPECTED_BENCH_MARKERS) + "\n")
    write_text(root / CLOSURE_REL, "# sample\n\n" + EXPECTED_CLOSURE_LINE + "\n")
    write_text(root / SMOKE_REL, "\n".join(EXPECTED_SMOKE_MARKERS) + "\n")
    write_text(
        root / MANIFEST_REL,
        json.dumps(
            {
                "review_anchors": {
                    "tools/lib/rbtree.zig": dict(EXPECTED_MANIFEST_VALUES),
                }
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="phase1-rbtree-bench-guard-ok-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        failures = collect_failures(root)
        if failures:
            print("PHASE1_RBTREE_BENCH_GUARD_SELF_TEST=fail")
            for failure in failures:
                print(failure)
            return 1
        case_count += 1

    mutations = [
        ("missing_closure_line", CLOSURE_REL, EXPECTED_CLOSURE_LINE + "\n", ""),
        ("duplicate_closure_line", CLOSURE_REL, EXPECTED_CLOSURE_LINE + "\n", EXPECTED_CLOSURE_LINE + "\n" + EXPECTED_CLOSURE_LINE + "\n"),
        ("missing_bench_marker", BENCH_CHECKER_REL, EXPECTED_BENCH_MARKERS[0] + "\n", ""),
        ("duplicate_bench_marker", BENCH_CHECKER_REL, EXPECTED_BENCH_MARKERS[-1] + "\n", EXPECTED_BENCH_MARKERS[-1] + "\n" + EXPECTED_BENCH_MARKERS[-1] + "\n"),
        ("missing_smoke_marker", SMOKE_REL, EXPECTED_SMOKE_MARKERS[0] + "\n", ""),
        ("manifest_value_drift", MANIFEST_REL, '"cached_leftmost_fixture_keys": [\n        "cached_leftmost_return_serials"\n      ]', '"cached_leftmost_fixture_keys": []'),
        ("manifest_duplicate_key", MANIFEST_REL, '      "cached_root_alias_anchor": "test \\"rbtree cached-root Linux-style aliases mirror the primary helpers\\"",', '      "cached_root_alias_anchor": "drifted",\n      "cached_root_alias_anchor": "test \\"rbtree cached-root Linux-style aliases mirror the primary helpers\\"",'),
        ("missing_manifest_file", MANIFEST_REL, None, None),
    ]

    for name, relative_path, before, after in mutations:
        with tempfile.TemporaryDirectory(prefix=f"phase1-rbtree-bench-guard-{name}-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            target = root / relative_path
            if name == "missing_manifest_file":
                target.unlink()
            else:
                text = target.read_text(encoding="utf-8")
                target.write_text(text.replace(before, after, 1), encoding="utf-8")
            failures = collect_failures(root)
            if not failures:
                print(f"PHASE1_RBTREE_BENCH_GUARD_SELF_TEST_CASE_FAILED={name}")
                return 1
            case_count += 1

    print("PHASE1_RBTREE_BENCH_GUARD_SELF_TEST=pass")
    print(f"PHASE1_RBTREE_BENCH_GUARD_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="Repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="Run built-in self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_RBTREE_BENCH_GUARD=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_RBTREE_BENCH_GUARD=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())