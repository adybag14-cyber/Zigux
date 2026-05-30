#!/usr/bin/env python3
"""Guard the Phase 1 rbtree benchmark source and expectation anchors."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

BENCH_REL = Path("zigux/tests/phase1_bench.zig")
EXPECTATIONS_REL = Path("zigux/tests/fixtures/phase1_bench_expectations.json")

EXPECTED_RBTREE_ITERATION_KEY = "PHASE1_BENCH_RBTREE_ITERATIONS"
EXPECTED_RBTREE_ITERATIONS = 4000

EXPECTED_RBTREE_CHECKSUMS = [
    "PHASE1_BENCH_RBTREE_CHECKSUM",
    "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM",
    "PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM",
    "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM",
    "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM",
]

EXPECTED_SOURCE_MARKERS = {
    "iterations_constant": "const iterations_rbtree: u64 = 4000;",
    "rbtree_bench_fn": "fn rbtreeBench() struct { checksum: u64 } {",
    "postorder_safe_fn": "fn rbtreePostorderSafeBench() struct { checksum: u64 } {",
    "find_add_fn": "fn rbtreeFindAddBench() struct { checksum: u64 } {",
    "duplicate_fn": "fn rbtreeDuplicateBench() struct { checksum: u64 } {",
    "cached_fn": "fn rbtreeCachedBench() struct { checksum: u64 } {",
    "ordered_first": "var node = rbtree.first(&root);",
    "ordered_next": "while (node) |current| : (node = rbtree.next(current)) {",
    "postorder_first": "var node = rbtree.firstPostorder(&root);",
    "postorder_next": "while (node) |current| : (node = rbtree.nextPostorder(current)) {",
    "find_add_probe": "const existing = rbtree.findAdd(&probe.node, &root, TreeEntry.cmp);",
    "duplicate_iterator": "var iter = rbtree.matchIterator(&duplicate_key, &root, TreeEntry.keyCmp);",
    "cached_insert": "_ = rbtree.addCached(&entry.node, &cached_root, TreeEntry.less);",
    "cached_erase": "const promoted_leftmost = rbtree.eraseCached(&entries[1].node, &cached_root);",
    "bench_call": "const rbtree_result = rbtreeBench();",
    "postorder_safe_call": "const rbtree_postorder_safe_result = rbtreePostorderSafeBench();",
    "find_add_call": "const rbtree_find_add_result = rbtreeFindAddBench();",
    "duplicate_call": "const rbtree_duplicate_result = rbtreeDuplicateBench();",
    "cached_call": "const rbtree_cached_result = rbtreeCachedBench();",
    "iterations_print": 'try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_ITERATIONS={d}\\n", .{iterations_rbtree});',
    "checksum_print": 'try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_CHECKSUM={d}\\n", .{rbtree_result.checksum});',
    "postorder_safe_print": 'try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM={d}\\n", .{rbtree_postorder_safe_result.checksum});',
    "find_add_print": 'try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM={d}\\n", .{rbtree_find_add_result.checksum});',
    "duplicate_print": 'try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM={d}\\n", .{rbtree_duplicate_result.checksum});',
    "cached_print": 'try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_CACHED_CHECKSUM={d}\\n", .{rbtree_cached_result.checksum});',
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


def load_json(root: Path, relative_path: Path) -> object:
    return json.loads(load_text(root, relative_path), object_pairs_hook=DuplicateTrackingDict)


def duplicate_json_key_paths(data: object, prefix: tuple[str, ...] = ()) -> list[str]:
    paths: list[str] = []
    if isinstance(data, DuplicateTrackingDict):
        paths.extend(".".join(prefix + (key,)) for key in data.duplicate_keys)
    if isinstance(data, dict):
        for key, value in data.items():
            paths.extend(duplicate_json_key_paths(value, prefix + (key,)))
    return paths


def check_source(text: str) -> list[str]:
    failures: list[str] = []
    for label, marker in EXPECTED_SOURCE_MARKERS.items():
        count = text.count(marker)
        if count != 1:
            failures.append(f"bench_source:{label}:expected=1:actual={count}")
    return failures


def check_expectations(data: object) -> list[str]:
    if not isinstance(data, dict):
        return [f"expectations:expected=dict:actual={type(data).__name__}"]
    duplicate_paths = duplicate_json_key_paths(data)
    if duplicate_paths:
        return [f"expectations:duplicate_json_key:{path}" for path in duplicate_paths]

    failures: list[str] = []
    iterations = data.get("iterations")
    checksums = data.get("checksums")
    exact_checksums = data.get("exact_checksums")

    if not isinstance(iterations, dict):
        return [f"expectations.iterations:expected=dict:actual={type(iterations).__name__}"]
    if not isinstance(checksums, list):
        return [f"expectations.checksums:expected=list:actual={type(checksums).__name__}"]
    if not isinstance(exact_checksums, dict):
        return [f"expectations.exact_checksums:expected=dict:actual={type(exact_checksums).__name__}"]

    actual_iterations = iterations.get(EXPECTED_RBTREE_ITERATION_KEY)
    if actual_iterations != EXPECTED_RBTREE_ITERATIONS:
        failures.append(
            f"expectations.iterations.{EXPECTED_RBTREE_ITERATION_KEY}:"
            f"expected={EXPECTED_RBTREE_ITERATIONS}:actual={actual_iterations!r}"
        )

    expected_tail = EXPECTED_RBTREE_CHECKSUMS
    actual_tail = checksums[-len(expected_tail) :]
    if actual_tail != expected_tail:
        failures.append(f"expectations.checksums.rbtree_tail:expected={expected_tail!r}:actual={actual_tail!r}")

    for checksum_key in EXPECTED_RBTREE_CHECKSUMS:
        value = exact_checksums.get(checksum_key)
        if not isinstance(value, int) or value <= 0:
            failures.append(f"expectations.exact_checksums.{checksum_key}:expected=positive_int:actual={value!r}")

    return failures


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in (BENCH_REL, EXPECTATIONS_REL):
        if not (root / relative_path).is_file():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    failures.extend(check_source(load_text(root, BENCH_REL)))
    try:
        expectations = load_json(root, EXPECTATIONS_REL)
    except json.JSONDecodeError as exc:
        return [f"expectations:invalid_json:{exc.msg}:line={exc.lineno}:column={exc.colno}"]
    failures.extend(check_expectations(expectations))
    return failures


def write_file(root: Path, relative_path: Path, text: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def sample_bench_source() -> str:
    return "\n".join(EXPECTED_SOURCE_MARKERS.values()) + "\n"


def sample_expectations() -> str:
    return json.dumps(
        {
            "iterations": {EXPECTED_RBTREE_ITERATION_KEY: EXPECTED_RBTREE_ITERATIONS},
            "checksums": ["PHASE1_BENCH_LIST_SORT_CHECKSUM", *EXPECTED_RBTREE_CHECKSUMS],
            "exact_checksums": {key: index + 1 for index, key in enumerate(EXPECTED_RBTREE_CHECKSUMS)},
        },
        indent=2,
    ) + "\n"


def build_sample_repo(root: Path) -> None:
    write_file(root, BENCH_REL, sample_bench_source())
    write_file(root, EXPECTATIONS_REL, sample_expectations())


def run_self_test() -> int:
    case_count = 0
    mutations: list[tuple[str, object]] = [("baseline", None)]
    mutations.extend((f"missing_source_{label}", ("source", marker)) for label, marker in EXPECTED_SOURCE_MARKERS.items())
    mutations.extend(
        [
            ("bad_iteration_count", ("json", ("iterations", EXPECTED_RBTREE_ITERATION_KEY), 3999)),
            ("missing_tail_checksum", ("json", ("checksums",), ["PHASE1_BENCH_LIST_SORT_CHECKSUM"])),
            ("missing_exact_cached_checksum", ("json", ("exact_checksums", "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM"), None)),
            ("duplicate_exact_checksum_key", ("duplicate_json",)),
            ("invalid_expectations_json", ("invalid_json",)),
        ]
    )

    for name, mutation in mutations:
        with tempfile.TemporaryDirectory(prefix=f"phase1-rbtree-bench-{name}-") as tmp:
            root = Path(tmp)
            build_sample_repo(root)
            if isinstance(mutation, tuple) and mutation[0] == "source":
                marker = mutation[1]
                assert isinstance(marker, str)
                text = load_text(root, BENCH_REL).replace(marker + "\n", "", 1)
                write_file(root, BENCH_REL, text)
            elif isinstance(mutation, tuple) and mutation[0] == "json":
                data = json.loads(load_text(root, EXPECTATIONS_REL))
                path = mutation[1]
                value = mutation[2]
                assert isinstance(path, tuple)
                current = data
                for key in path[:-1]:
                    current = current[key]
                if value is None:
                    del current[path[-1]]
                else:
                    current[path[-1]] = value
                write_file(root, EXPECTATIONS_REL, json.dumps(data, indent=2) + "\n")
            elif isinstance(mutation, tuple) and mutation[0] == "duplicate_json":
                text = load_text(root, EXPECTATIONS_REL)
                write_file(root, EXPECTATIONS_REL, text.replace('    "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM": 5', '    "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM": 5,\n    "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM": 7', 1))
            elif isinstance(mutation, tuple) and mutation[0] == "invalid_json":
                write_file(root, EXPECTATIONS_REL, "{\n")

            failures = collect_failures(root)
            if name == "baseline":
                if failures:
                    print(f"self-test:{name}:unexpected={failures}")
                    return 1
            elif not failures:
                print(f"self-test:{name}:expected_failure")
                return 1
            case_count += 1

    print("PHASE1_RBTREE_BENCH_ANCHORS_SELF_TEST=pass")
    print(f"PHASE1_RBTREE_BENCH_ANCHORS_SELF_TEST_CASE_COUNT={case_count}")
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
    print("phase1-rbtree-bench-anchors:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
