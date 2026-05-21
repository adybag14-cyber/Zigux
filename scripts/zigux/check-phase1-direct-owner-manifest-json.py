#!/usr/bin/env python3
"""Guard the Phase 1 direct-owner manifest against duplicate-key drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[1] if len(HERE.parents) > 1 else HERE.parent
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")


class DuplicateTrackingDict(dict[str, object]):
    def __init__(self, pairs: list[tuple[str, object]]) -> None:
        super().__init__()
        self.duplicate_keys: list[str] = []
        for key, value in pairs:
            if key in self and key not in self.duplicate_keys:
                self.duplicate_keys.append(key)
            self[key] = value


EXPECTED_DIRECT_HELPERS = [
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
]

EXPECTED_PATHS: dict[tuple[str, ...], object] = {
    ("lane_sequencing", "direct_anchor_followup_helpers"): EXPECTED_DIRECT_HELPERS,
    ("review_anchors", "tools/lib/bitmap.zig", "or_window_anchor"): 'test "bitmap or keeps caller-selected bit window"',
    ("review_anchors", "tools/lib/bitmap.zig", "weighted_tail_count_anchor"): 'test "bitmap weighted or and xor clamp counts to the declared tail window"',
    ("review_anchors", "tools/lib/find_bit.zig", "andnot_scan_entrypoint_contract"): "The shipped public, Linux-style, and underscore andnot scan entry points stay owned by the direct find_bit packet instead of being left implicit under generic alias wording.",
    ("review_anchors", "tools/lib/find_bit.zig", "tail_inclusive_boundary_fixture_keys"): [
        "tail_inclusive_boundary_next",
        "tail_inclusive_boundary_zero",
        "tail_inclusive_boundary_and",
    ],
    ("review_anchors", "tools/lib/rbtree.zig", "low_level_alias_anchor"): 'test "rbtree low-level Linux-style aliases mirror node-state helpers"',
    ("review_anchors", "tools/lib/rbtree.zig", "cached_leftmost_fixture_keys"): [
        "cached_leftmost_return_serials",
    ],
    ("review_anchors", "tools/lib/string.zig", "sysfs_review_summary"): "helper-local string sysfs newline-aware equality and lookup-order anchors stay explicit through the direct string tests because the shared Phase 1 replay still carries no dedicated sysfs fixture keys, so sysfsStreq and sysfs_streq plus sysfsMatchString and sysfs_match_string remain review-visible at the helper surface",
    ("review_anchors", "tools/lib/string.zig", "strnchrnul_review_anchor"): 'test "strnchrNul returns the first match, NUL, or count boundary"',
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json_with_duplicates(root: Path, relative_path: Path) -> object:
    return json.loads(
        load_text(root, relative_path),
        object_pairs_hook=DuplicateTrackingDict,
    )


def collect_duplicate_paths(data: object, prefix: tuple[str, ...] = ()) -> list[str]:
    paths: list[str] = []
    if isinstance(data, DuplicateTrackingDict):
        for key in data.duplicate_keys:
            paths.append(".".join(prefix + (key,)))
    if isinstance(data, dict):
        for key, value in data.items():
            paths.extend(collect_duplicate_paths(value, prefix + (key,)))
    elif isinstance(data, list):
        for item in data:
            paths.extend(collect_duplicate_paths(item, prefix))
    return paths


def nested_value(data: object, path: tuple[str, ...]) -> object:
    current = data
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def collect_failures(root: Path) -> list[str]:
    manifest_path = root / MANIFEST_REL
    if not manifest_path.is_file():
        return [f"missing_file:{MANIFEST_REL.as_posix()}"]

    try:
        manifest = load_json_with_duplicates(root, MANIFEST_REL)
    except json.JSONDecodeError as exc:
        return [
            f"{MANIFEST_REL.as_posix()}:invalid_json:{exc.msg}:line={exc.lineno}:column={exc.colno}"
        ]

    if not isinstance(manifest, dict):
        return [f"{MANIFEST_REL.as_posix()}:expected=dict:actual={type(manifest).__name__}"]

    duplicate_paths = collect_duplicate_paths(manifest)
    if duplicate_paths:
        return [
            f"{MANIFEST_REL.as_posix()}:duplicate_json_key:{path}" for path in duplicate_paths
        ]

    failures: list[str] = []
    for path, expected in EXPECTED_PATHS.items():
        actual = nested_value(manifest, path)
        if actual != expected:
            failures.append(
                f"{MANIFEST_REL.as_posix()}:{'.'.join(path)}:expected={expected!r}:actual={actual!r}"
            )
    return failures


def sample_manifest() -> str:
    return """{
  \"phase\": \"Phase 1\",
  \"status\": \"closed\",
  \"lane_sequencing\": {
    \"direct_anchor_followup_helpers\": [
      \"tools/lib/bitmap.zig\",
      \"tools/lib/find_bit.zig\",
      \"tools/lib/rbtree.zig\",
      \"tools/lib/string.zig\"
    ]
  },
  \"review_anchors\": {
    \"tools/lib/bitmap.zig\": {
      \"or_window_anchor\": \"test \\\"bitmap or keeps caller-selected bit window\\\"\",
      \"weighted_tail_count_anchor\": \"test \\\"bitmap weighted or and xor clamp counts to the declared tail window\\\"\"
    },
    \"tools/lib/find_bit.zig\": {
      \"andnot_scan_entrypoint_contract\": \"The shipped public, Linux-style, and underscore andnot scan entry points stay owned by the direct find_bit packet instead of being left implicit under generic alias wording.\",
      \"tail_inclusive_boundary_fixture_keys\": [
        \"tail_inclusive_boundary_next\",
        \"tail_inclusive_boundary_zero\",
        \"tail_inclusive_boundary_and\"
      ]
    },
    \"tools/lib/rbtree.zig\": {
      \"low_level_alias_anchor\": \"test \\\"rbtree low-level Linux-style aliases mirror node-state helpers\\\"\",
      \"cached_leftmost_fixture_keys\": [
        \"cached_leftmost_return_serials\"
      ]
    },
    \"tools/lib/string.zig\": {
      \"sysfs_review_summary\": \"helper-local string sysfs newline-aware equality and lookup-order anchors stay explicit through the direct string tests because the shared Phase 1 replay still carries no dedicated sysfs fixture keys, so sysfsStreq and sysfs_streq plus sysfsMatchString and sysfs_match_string remain review-visible at the helper surface\",
      \"strnchrnul_review_anchor\": \"test \\\"strnchrNul returns the first match, NUL, or count boundary\\\"\"
    }
  }
}
"""


def write_manifest(root: Path, text: str) -> None:
    manifest_path = root / MANIFEST_REL
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(text, encoding="utf-8")


def mutate_nested_value(root: Path, path: tuple[str, ...]) -> None:
    manifest_path = root / MANIFEST_REL
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    current = manifest
    for key in path[:-1]:
        current = current[key]
    final_key = path[-1]
    value = current[final_key]
    if isinstance(value, list):
        current[final_key] = value[1:]
    else:
        current[final_key] = f"{value} drift"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def run_self_test() -> int:
    cases = 1
    with tempfile.TemporaryDirectory(prefix="phase1-direct-owner-manifest-json-ok-") as tmpdir:
        root = Path(tmpdir)
        write_manifest(root, sample_manifest())
        failures = collect_failures(root)
        if failures:
            print("self-test:success:unexpected_failures")
            for failure in failures:
                print(failure)
            return 1

    duplicate_cases = [
        ("duplicate_top_level", '{"phase":"Phase 1","phase":"Phase 1","lane_sequencing":{"direct_anchor_followup_helpers":["tools/lib/bitmap.zig","tools/lib/find_bit.zig","tools/lib/rbtree.zig","tools/lib/string.zig"]},"review_anchors":{"tools/lib/bitmap.zig":{"or_window_anchor":"test \\\"bitmap or keeps caller-selected bit window\\\"","weighted_tail_count_anchor":"test \\\"bitmap weighted or and xor clamp counts to the declared tail window\\\""},"tools/lib/find_bit.zig":{"andnot_scan_entrypoint_contract":"The shipped public, Linux-style, and underscore andnot scan entry points stay owned by the direct find_bit packet instead of being left implicit under generic alias wording.","tail_inclusive_boundary_fixture_keys":["tail_inclusive_boundary_next","tail_inclusive_boundary_zero","tail_inclusive_boundary_and"]},"tools/lib/rbtree.zig":{"low_level_alias_anchor":"test \\\"rbtree low-level Linux-style aliases mirror node-state helpers\\\"","cached_leftmost_fixture_keys":["cached_leftmost_return_serials"]},"tools/lib/string.zig":{"sysfs_review_summary":"helper-local string sysfs newline-aware equality and lookup-order anchors stay explicit through the direct string tests because the shared Phase 1 replay still carries no dedicated sysfs fixture keys, so sysfsStreq and sysfs_streq plus sysfsMatchString and sysfs_match_string remain review-visible at the helper surface","strnchrnul_review_anchor":"test \\\"strnchrNul returns the first match, NUL, or count boundary\\\""}}}'),
        ("duplicate_nested", '{"phase":"Phase 1","status":"closed","lane_sequencing":{"direct_anchor_followup_helpers":["tools/lib/bitmap.zig","tools/lib/find_bit.zig","tools/lib/rbtree.zig","tools/lib/string.zig"]},"review_anchors":{"tools/lib/bitmap.zig":{"or_window_anchor":"test \\\"bitmap or keeps caller-selected bit window\\\"","weighted_tail_count_anchor":"test \\\"bitmap weighted or and xor clamp counts to the declared tail window\\\""},"tools/lib/find_bit.zig":{"andnot_scan_entrypoint_contract":"The shipped public, Linux-style, and underscore andnot scan entry points stay owned by the direct find_bit packet instead of being left implicit under generic alias wording.","tail_inclusive_boundary_fixture_keys":["tail_inclusive_boundary_next","tail_inclusive_boundary_zero","tail_inclusive_boundary_and"]},"tools/lib/rbtree.zig":{"low_level_alias_anchor":"test \\\"rbtree low-level Linux-style aliases mirror node-state helpers\\\"","cached_leftmost_fixture_keys":["cached_leftmost_return_serials"]},"tools/lib/string.zig":{"sysfs_review_summary":"helper-local string sysfs newline-aware equality and lookup-order anchors stay explicit through the direct string tests because the shared Phase 1 replay still carries no dedicated sysfs fixture keys, so sysfsStreq and sysfs_streq plus sysfsMatchString and sysfs_match_string remain review-visible at the helper surface","strnchrnul_review_anchor":"test \\\"strnchrNul returns the first match, NUL, or count boundary\\\"","strnchrnul_review_anchor":"test \\\"strnchrNul returns the first match, NUL, or count boundary\\\" drift"}}}'),
    ]
    for name, text in duplicate_cases:
        cases += 1
        with tempfile.TemporaryDirectory(prefix=f"phase1-direct-owner-manifest-json-{name}-") as tmpdir:
            root = Path(tmpdir)
            write_manifest(root, text)
            if not collect_failures(root):
                print(f"self-test:{name}:expected_failure")
                return 1

    for path in EXPECTED_PATHS:
        cases += 1
        with tempfile.TemporaryDirectory(prefix="phase1-direct-owner-manifest-json-drift-") as tmpdir:
            root = Path(tmpdir)
            write_manifest(root, sample_manifest())
            mutate_nested_value(root, path)
            if not collect_failures(root):
                print(f"self-test:drift:{'.'.join(path)}:expected_failure")
                return 1

    cases += 2
    with tempfile.TemporaryDirectory(prefix="phase1-direct-owner-manifest-json-invalid-") as tmpdir:
        root = Path(tmpdir)
        write_manifest(root, "{\n")
        if not collect_failures(root):
            print("self-test:invalid_json:expected_failure")
            return 1

    with tempfile.TemporaryDirectory(prefix="phase1-direct-owner-manifest-json-missing-") as tmpdir:
        root = Path(tmpdir)
        if not collect_failures(root):
            print("self-test:missing_file:expected_failure")
            return 1

    print("PHASE1_DIRECT_OWNER_MANIFEST_JSON_SELF_TEST=pass")
    print(f"PHASE1_DIRECT_OWNER_MANIFEST_JSON_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_DIRECT_OWNER_MANIFEST_JSON=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
