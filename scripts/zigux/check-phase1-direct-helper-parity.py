#!/usr/bin/env python3
"""Check current-master-safe Phase 1 parity anchors for bitmap, find_bit, string, and rbtree."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
FIXTURE_REL = Path("zigux/tests/fixtures/phase1_helpers.json")
SMOKE_REL = Path("zigux/tests/phase1_host_tools_smoke.zig")

REQUIRED_FILES = (
    MANIFEST_REL,
    FIXTURE_REL,
    SMOKE_REL,
)

EXPECTED_DIRECT_HELPERS = [
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
]

EXPECTED_BITMAP_FIXTURE_KEYS = [
    "alloc_words",
    "zalloc_words",
    "zalloc_values",
    "scnprintf",
    "truncated_scnprintf_len",
    "truncated_scnprintf",
    "terminator_only_scnprintf_len",
    "terminator_only_nul",
    "zero_length_scnprintf_len",
]

EXPECTED_FIND_BIT_TAIL_CLAMP_KEYS = [
    "tail_clamped_first",
    "tail_clamped_next",
    "tail_zero_clamped_first",
    "tail_zero_clamped_next",
    "tail_and_clamped_first",
    "tail_and_clamped_next",
    "tail_clamped_last",
    "tail_clamped_empty_last",
]

EXPECTED_FIND_BIT_TAIL_BOUNDARY_KEYS = [
    "tail_inclusive_boundary_next",
    "tail_inclusive_boundary_zero",
    "tail_inclusive_boundary_and",
]

EXPECTED_STRING_FIXTURE_KEYS = [
    "strtobool_y",
    "strtobool_on",
    "strtobool_zero",
    "strtobool_off",
    "strtobool_invalid",
    "strlcpy_len",
    "strlcpy_buffer",
    "skip_spaces",
    "trim_spaces",
    "remove_spaces",
    "replace_char",
    "replace_char_end",
    "replace_char_cstr_end",
    "replace_char_cstr_bytes",
    "memchr_inv_index",
    "memchr_inv_none",
]

EXPECTED_RBTREE_FIXTURE_KEYS = [
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

EXPECTED_RBTREE_CACHED_KEYS = [
    "cached_leftmost_return_serials",
]

SMOKE_MARKERS = (
    'test "phase1 host-tools smoke exercises live helper behavior" {',
    'const nbits = word_bits + 5;',
    "find_bit.findLastBit(&map, nbits)",
    "bitmap.scnprintf(&map, nbits, &rendered)",
    'string.sysfsMatchString(&sysfs, "auto")',
    "string.strnchrNul(&counted, counted.len, 'z')",
    "rbtree.matchIterator(&duplicate_key, &tree_root, RbtreeSmokeEntry.cmp)",
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json(root: Path, relative_path: Path) -> object:
    return json.loads(load_text(root, relative_path))


def require_exact_value(label: str, actual: object, expected: object) -> list[str]:
    return [] if actual == expected else [f"{label}:expected={expected!r}:actual={actual!r}"]


def require_key_set(
    failures: list[str],
    helper_name: str,
    actual_keys: object,
    expected_keys: list[str],
) -> None:
    failures.extend(
        require_exact_value(
            f"{helper_name}.keys",
            actual_keys,
            expected_keys,
        )
    )


def require_fixture_members(
    failures: list[str],
    section_name: str,
    section: object,
    required_keys: list[str],
) -> None:
    if not isinstance(section, dict):
        failures.append(f"{section_name}:expected=dict:actual={type(section).__name__}")
        return
    for key in required_keys:
        if key not in section:
            failures.append(f"{section_name}:missing_fixture_key:{key}")


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path}")
    if failures:
        return failures

    manifest = load_json(root, MANIFEST_REL)
    fixture = load_json(root, FIXTURE_REL)
    smoke_text = load_text(root, SMOKE_REL)

    if not isinstance(manifest, dict):
        failures.append(f"manifest:expected=dict:actual={type(manifest).__name__}")
        return failures
    if not isinstance(fixture, dict):
        failures.append(f"fixture:expected=dict:actual={type(fixture).__name__}")
        return failures

    lane = manifest.get("lane_sequencing")
    if not isinstance(lane, dict):
        failures.append(f"lane_sequencing:expected=dict:actual={type(lane).__name__}")
    else:
        failures.extend(
            require_exact_value(
                "lane_sequencing.direct_anchor_followup_helpers",
                lane.get("direct_anchor_followup_helpers"),
                EXPECTED_DIRECT_HELPERS,
            )
        )

    anchors = manifest.get("review_anchors")
    if not isinstance(anchors, dict):
        failures.append(f"review_anchors:expected=dict:actual={type(anchors).__name__}")
        return failures

    bitmap_anchor = anchors.get("tools/lib/bitmap.zig")
    find_bit_anchor = anchors.get("tools/lib/find_bit.zig")
    string_anchor = anchors.get("tools/lib/string.zig")
    rbtree_anchor = anchors.get("tools/lib/rbtree.zig")

    if not isinstance(bitmap_anchor, dict):
        failures.append("tools/lib/bitmap.zig:expected=dict")
    else:
        require_key_set(
            failures,
            "tools/lib/bitmap.zig.parity_fixture_keys",
            bitmap_anchor.get("parity_fixture_keys"),
            EXPECTED_BITMAP_FIXTURE_KEYS,
        )

    if not isinstance(find_bit_anchor, dict):
        failures.append("tools/lib/find_bit.zig:expected=dict")
    else:
        require_key_set(
            failures,
            "tools/lib/find_bit.zig.tail_clamp_fixture_keys",
            find_bit_anchor.get("tail_clamp_fixture_keys"),
            EXPECTED_FIND_BIT_TAIL_CLAMP_KEYS,
        )
        require_key_set(
            failures,
            "tools/lib/find_bit.zig.tail_inclusive_boundary_fixture_keys",
            find_bit_anchor.get("tail_inclusive_boundary_fixture_keys"),
            EXPECTED_FIND_BIT_TAIL_BOUNDARY_KEYS,
        )

    if not isinstance(string_anchor, dict):
        failures.append("tools/lib/string.zig:expected=dict")
    else:
        require_key_set(
            failures,
            "tools/lib/string.zig.parity_fixture_keys",
            string_anchor.get("parity_fixture_keys"),
            EXPECTED_STRING_FIXTURE_KEYS,
        )

    if not isinstance(rbtree_anchor, dict):
        failures.append("tools/lib/rbtree.zig:expected=dict")
    else:
        require_key_set(
            failures,
            "tools/lib/rbtree.zig.parity_fixture_keys",
            rbtree_anchor.get("parity_fixture_keys"),
            EXPECTED_RBTREE_FIXTURE_KEYS,
        )
        require_key_set(
            failures,
            "tools/lib/rbtree.zig.cached_leftmost_fixture_keys",
            rbtree_anchor.get("cached_leftmost_fixture_keys"),
            EXPECTED_RBTREE_CACHED_KEYS,
        )

    require_fixture_members(failures, "fixture.bitmap", fixture.get("bitmap"), EXPECTED_BITMAP_FIXTURE_KEYS)
    require_fixture_members(
        failures,
        "fixture.find_bit",
        fixture.get("find_bit"),
        EXPECTED_FIND_BIT_TAIL_CLAMP_KEYS + EXPECTED_FIND_BIT_TAIL_BOUNDARY_KEYS,
    )
    require_fixture_members(failures, "fixture.string", fixture.get("string"), EXPECTED_STRING_FIXTURE_KEYS)
    require_fixture_members(
        failures,
        "fixture.rbtree",
        fixture.get("rbtree"),
        EXPECTED_RBTREE_FIXTURE_KEYS + EXPECTED_RBTREE_CACHED_KEYS,
    )

    for marker in SMOKE_MARKERS:
        count = smoke_text.count(marker)
        if count != 1:
            failures.append(f"smoke_marker:expected=1:actual={count}:{marker}")

    return failures


def write_text(root: Path, relative_path: Path, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    manifest = {
        "lane_sequencing": {
            "direct_anchor_followup_helpers": EXPECTED_DIRECT_HELPERS,
        },
        "review_anchors": {
            "tools/lib/bitmap.zig": {
                "parity_fixture_keys": EXPECTED_BITMAP_FIXTURE_KEYS,
            },
            "tools/lib/find_bit.zig": {
                "tail_clamp_fixture_keys": EXPECTED_FIND_BIT_TAIL_CLAMP_KEYS,
                "tail_inclusive_boundary_fixture_keys": EXPECTED_FIND_BIT_TAIL_BOUNDARY_KEYS,
            },
            "tools/lib/string.zig": {
                "parity_fixture_keys": EXPECTED_STRING_FIXTURE_KEYS,
            },
            "tools/lib/rbtree.zig": {
                "parity_fixture_keys": EXPECTED_RBTREE_FIXTURE_KEYS,
                "cached_leftmost_fixture_keys": EXPECTED_RBTREE_CACHED_KEYS,
            },
        },
    }
    fixture = {
        "bitmap": {key: 1 for key in EXPECTED_BITMAP_FIXTURE_KEYS},
        "find_bit": {key: 1 for key in EXPECTED_FIND_BIT_TAIL_CLAMP_KEYS + EXPECTED_FIND_BIT_TAIL_BOUNDARY_KEYS},
        "string": {key: 1 for key in EXPECTED_STRING_FIXTURE_KEYS},
        "rbtree": {key: 1 for key in EXPECTED_RBTREE_FIXTURE_KEYS + EXPECTED_RBTREE_CACHED_KEYS},
    }
    smoke = "\n".join(SMOKE_MARKERS) + "\n"
    write_text(root, MANIFEST_REL, json.dumps(manifest, indent=2) + "\n")
    write_text(root, FIXTURE_REL, json.dumps(fixture, indent=2) + "\n")
    write_text(root, SMOKE_REL, smoke)


def remove_text(root: Path, relative_path: Path, target: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(target, "", 1), encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, tuple[str, str] | None]] = [
        ("success", None),
        ("missing_smoke_marker", ("text", "rbtree.matchIterator(&duplicate_key, &tree_root, RbtreeSmokeEntry.cmp)")),
        ("missing_bitmap_fixture_key", ("text", '"truncated_scnprintf_len": 1,')),
        ("wrong_direct_helpers", ("text", '"tools/lib/string.zig"\n    ]')),
    ]

    for name, mutation in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-direct-helper-parity-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            if mutation is not None:
                relative_text_target = mutation[1]
                if name == "missing_smoke_marker":
                    remove_text(root, SMOKE_REL, relative_text_target)
                elif name == "missing_bitmap_fixture_key":
                    remove_text(root, FIXTURE_REL, relative_text_target)
                elif name == "wrong_direct_helpers":
                    text = (root / MANIFEST_REL).read_text(encoding="utf-8")
                    replacement = '"tools/lib/string.zig",\n      "tools/lib/slab.zig"\n    ]'
                    (root / MANIFEST_REL).write_text(
                        text.replace(relative_text_target, replacement, 1),
                        encoding="utf-8",
                    )
            failures = collect_failures(root)
            if name == "success":
                if failures:
                    print("self-test:success:unexpected_failures")
                    for failure in failures:
                        print(failure)
                    return 1
            elif not failures:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("PHASE1_DIRECT_HELPER_PARITY_SELF_TEST=pass")
    print(f"PHASE1_DIRECT_HELPER_PARITY_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_DIRECT_HELPER_PARITY=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_DIRECT_HELPER_PARITY=pass")
    print(f"PHASE1_DIRECT_HELPER_PARITY_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE1_DIRECT_HELPER_PARITY_DIRECT_HELPER_COUNT={len(EXPECTED_DIRECT_HELPERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
