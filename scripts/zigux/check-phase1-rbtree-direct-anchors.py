#!/usr/bin/env python3
"""Fail-close the Phase 1 rbtree direct-anchor packet against helper or manifest drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
HELPER_REL = Path("tools/lib/rbtree.zig")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")

HELPER_TEST_LINES = [
    'test "rbtree inserts and traverses in sorted order" {',
    'test "rbtree erase and replace keep traversal consistent" {',
    'test "rbtree ordered Linux-style aliases mirror traversal and replacement helpers" {',
    'test "rbtree low-level Linux-style aliases mirror node-state helpers" {',
    'test "rbtree eraseInit detaches erased node" {',
    'test "rbtree eraseInit clears singleton roots before reseed" {',
    'test "rbtree postorder and empty node helpers behave" {',
    'test "rbtree findAdd keeps the first duplicate and inserts new keys" {',
    'test "rbtree nextMatch walks the duplicate range in order" {',
    'test "rbtree matchIterator walks the duplicate range in order" {',
    'test "rbtree addCached returns the inserted node only when it becomes leftmost" {',
    'test "rbtree findAddCached keeps cached leftmost stable while inserting misses" {',
    'test "rbtree cached root keeps the leftmost pointer in sync" {',
    'test "rbtree cached-root Linux-style aliases mirror the primary helpers" {',
    'test "rbtree replaceNodeCached keeps non-leftmost leftmost unchanged" {',
    'test "rbtree eraseCached returns null for a singleton cached tree" {',
    'test "rbtree eraseInitCached detaches nodes while keeping cached leftmost aligned" {',
    'test "rbtree eraseInitCached clears singleton cached roots before reseed" {',
]

HELPER_FUNCTION_LINES = [
    "pub fn addCached(node: *Node, root: *RootCached, less: LessFn) ?*Node {",
    "pub fn findAddCached(node: *Node, root: *RootCached, cmp: CmpNodeFn) ?*Node {",
    "pub fn eraseCached(node: *Node, root: *RootCached) ?*Node {",
    "pub fn eraseInitCached(node: *Node, root: *RootCached) void {",
    "pub fn replaceNodeCached(victim: *Node, new: *Node, root: *RootCached) void {",
    "pub fn rb_add_cached(node: *Node, root: *RootCached, less: LessFn) ?*Node {",
    "pub fn rb_find_add_cached(node: *Node, root: *RootCached, cmp: CmpNodeFn) ?*Node {",
    "pub fn rb_erase_cached(node: *Node, root: *RootCached) ?*Node {",
    "pub fn rb_erase_init_cached(node: *Node, root: *RootCached) void {",
    "pub fn rb_replace_node_cached(victim: *Node, new: *Node, root: *RootCached) void {",
]

EXPECTED_REVIEW_ANCHORS = {
    "helper_test_anchors": [
        "test \"rbtree inserts and traverses in sorted order\"",
        "test \"rbtree erase and replace keep traversal consistent\"",
        "test \"rbtree ordered Linux-style aliases mirror traversal and replacement helpers\"",
        "test \"rbtree low-level Linux-style aliases mirror node-state helpers\"",
        "test \"rbtree eraseInit detaches erased node\"",
        "test \"rbtree eraseInit clears singleton roots before reseed\"",
        "test \"rbtree postorder and empty node helpers behave\"",
        "test \"rbtree findAdd keeps the first duplicate and inserts new keys\"",
        "test \"rbtree nextMatch walks the duplicate range in order\"",
        "test \"rbtree matchIterator walks the duplicate range in order\"",
        "test \"rbtree addCached returns the inserted node only when it becomes leftmost\"",
        "test \"rbtree findAddCached keeps cached leftmost stable while inserting misses\"",
        "test \"rbtree cached root keeps the leftmost pointer in sync\"",
        "test \"rbtree cached-root Linux-style aliases mirror the primary helpers\"",
        "test \"rbtree replaceNodeCached keeps non-leftmost leftmost unchanged\"",
        "test \"rbtree eraseCached returns null for a singleton cached tree\"",
        "test \"rbtree eraseInitCached detaches nodes while keeping cached leftmost aligned\"",
        "test \"rbtree eraseInitCached clears singleton cached roots before reseed\"",
    ],
    "ordered_alias_anchor": "test \"rbtree ordered Linux-style aliases mirror traversal and replacement helpers\"",
    "low_level_alias_anchor": "test \"rbtree low-level Linux-style aliases mirror node-state helpers\"",
    "duplicate_search_anchors": [
        "test \"rbtree findAdd keeps the first duplicate and inserts new keys\"",
        "test \"rbtree nextMatch walks the duplicate range in order\"",
        "test \"rbtree matchIterator walks the duplicate range in order\"",
    ],
    "cached_root_followup_anchors": [
        "test \"rbtree addCached returns the inserted node only when it becomes leftmost\"",
        "test \"rbtree findAddCached keeps cached leftmost stable while inserting misses\"",
        "test \"rbtree cached root keeps the leftmost pointer in sync\"",
        "test \"rbtree cached-root Linux-style aliases mirror the primary helpers\"",
        "test \"rbtree replaceNodeCached keeps non-leftmost leftmost unchanged\"",
        "test \"rbtree eraseCached returns null for a singleton cached tree\"",
        "test \"rbtree eraseInitCached detaches nodes while keeping cached leftmost aligned\"",
        "test \"rbtree eraseInitCached clears singleton cached roots before reseed\"",
    ],
    "cached_root_alias_anchor": "test \"rbtree cached-root Linux-style aliases mirror the primary helpers\"",
    "next_safe_step_note": "If this helper lane reopens, keep the already-landed shared-replay promotion for `cached_leftmost_return_serials` aligned across the committed fixture, shared replay, and direct cached-root anchors; until another committed cached-root field lands, insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed behavior stay owned by direct helper-local anchors.",
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json(root: Path, relative_path: Path) -> object:
    return json.loads(load_text(root, relative_path))


def require_exact_line(text: str, label: str, line: str) -> list[str]:
    count = sum(1 for current in text.splitlines() if current.strip() == line.strip())
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_value(label: str, actual: object, expected: object) -> list[str]:
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
    for relative_path in (HELPER_REL, MANIFEST_REL):
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    helper_text = load_text(root, HELPER_REL)
    for line in HELPER_TEST_LINES:
        failures.extend(require_exact_line(helper_text, f"{HELPER_REL.as_posix()}:helper_test", line))
    for line in HELPER_FUNCTION_LINES:
        failures.extend(require_exact_line(helper_text, f"{HELPER_REL.as_posix()}:helper_fn", line))

    manifest = load_json(root, MANIFEST_REL)
    if not isinstance(manifest, dict):
        return [f"{MANIFEST_REL.as_posix()}:expected=dict:actual={type(manifest).__name__}"]

    base_path = ("review_anchors", "tools/lib/rbtree.zig")
    for field, expected in EXPECTED_REVIEW_ANCHORS.items():
        failures.extend(
            require_value(
                f"{MANIFEST_REL.as_posix()}:{'.'.join(base_path + (field,))}",
                nested_value(manifest, base_path + (field,)),
                expected,
            )
        )

    return failures


def write_file(root: Path, relative_path: Path, text: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def sample_helper_text() -> str:
    return "\n".join(HELPER_FUNCTION_LINES + [""] + HELPER_TEST_LINES) + "\n"


def sample_manifest() -> str:
    return json.dumps(
        {
            "review_anchors": {
                "tools/lib/rbtree.zig": EXPECTED_REVIEW_ANCHORS,
            }
        },
        indent=2,
    ) + "\n"


def build_sample_repo(root: Path) -> None:
    write_file(root, HELPER_REL, sample_helper_text())
    write_file(root, MANIFEST_REL, sample_manifest())


def run_self_test() -> int:
    cases: list[tuple[str, str, str | tuple[str, ...] | None, str]] = [
        ("success", "none", None, "none"),
        ("missing_helper_file", HELPER_REL.as_posix(), None, "missing_file"),
        ("missing_manifest_file", MANIFEST_REL.as_posix(), None, "missing_file"),
        ("remove_helper_test", HELPER_REL.as_posix(), HELPER_TEST_LINES[12], "remove"),
        ("duplicate_helper_test", HELPER_REL.as_posix(), HELPER_TEST_LINES[12], "duplicate"),
        ("remove_helper_fn", HELPER_REL.as_posix(), HELPER_FUNCTION_LINES[4], "remove"),
        (
            "manifest_cached_followups",
            MANIFEST_REL.as_posix(),
            ("review_anchors", "tools/lib/rbtree.zig", "cached_root_followup_anchors"),
            "mutate_manifest",
        ),
        (
            "manifest_next_safe_step",
            MANIFEST_REL.as_posix(),
            ("review_anchors", "tools/lib/rbtree.zig", "next_safe_step_note"),
            "mutate_manifest",
        ),
    ]

    for name, relative_path, needle, operation in cases:
        with tempfile.TemporaryDirectory(prefix=f"phase1_rbtree_direct_{name}_") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)

            if operation == "missing_file":
                (root / Path(relative_path)).unlink()
            elif operation == "remove":
                path = root / Path(relative_path)
                text = path.read_text(encoding="utf-8")
                path.write_text(text.replace(str(needle) + "\n", "", 1), encoding="utf-8")
            elif operation == "duplicate":
                path = root / Path(relative_path)
                text = path.read_text(encoding="utf-8")
                marker = str(needle) + "\n"
                path.write_text(text.replace(marker, marker + marker, 1), encoding="utf-8")
            elif operation == "mutate_manifest":
                path = root / MANIFEST_REL
                data = json.loads(path.read_text(encoding="utf-8"))
                cursor = data
                for key in needle[:-1]:
                    cursor = cursor[key]
                final_key = needle[-1]
                value = cursor[final_key]
                cursor[final_key] = value[1:] if isinstance(value, list) else f"{value} drift"
                path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

            failures = collect_failures(root)
            if name == "success":
                if failures:
                    raise AssertionError(f"{name} unexpectedly failed: {failures}")
            elif not failures:
                raise AssertionError(f"{name} unexpectedly passed")

    print("PHASE1_RBTREE_DIRECT_ANCHORS_SELF_TEST=pass")
    print(f"PHASE1_RBTREE_DIRECT_ANCHORS_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=None, help="repo root to validate")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_RBTREE_DIRECT_ANCHORS=fail")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("PHASE1_RBTREE_DIRECT_ANCHORS=pass")
    print(f"PHASE1_RBTREE_DIRECT_ANCHORS_HELPER_TEST_COUNT={len(HELPER_TEST_LINES)}")
    print(f"PHASE1_RBTREE_DIRECT_ANCHORS_HELPER_FN_COUNT={len(HELPER_FUNCTION_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
