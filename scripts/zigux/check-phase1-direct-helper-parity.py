#!/usr/bin/env python3
"""Guard current-master-safe Phase 1 parity anchors for the direct helper packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[2]

MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
FIXTURE_REL = Path("zigux/tests/fixtures/phase1_helpers.json")
SMOKE_REL = Path("zigux/tests/phase1_host_tools_smoke.zig")
BITMAP_REL = Path("tools/lib/bitmap.zig")
FIND_BIT_REL = Path("tools/lib/find_bit.zig")
RBTREE_REL = Path("tools/lib/rbtree.zig")
STRING_REL = Path("tools/lib/string.zig")

REQUIRED_FILES = (
    MANIFEST_REL,
    FIXTURE_REL,
    SMOKE_REL,
    BITMAP_REL,
    FIND_BIT_REL,
    RBTREE_REL,
    STRING_REL,
)

EXPECTED_DIRECT_HELPERS = [
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
]

EXPECTED_MANIFEST_KEYS = {
    "tools/lib/bitmap.zig": {
        "parity_fixture_keys": [
            "alloc_words",
            "zalloc_words",
            "zalloc_values",
            "scnprintf",
            "truncated_scnprintf_len",
            "truncated_scnprintf",
            "terminator_only_scnprintf_len",
            "terminator_only_nul",
            "zero_length_scnprintf_len",
        ],
        "partial_xor_review_fields": [
            "partial_xor_nbits",
            "partial_xor_masked_values",
        ],
    },
    "tools/lib/find_bit.zig": {
        "tail_clamp_fixture_keys": [
            "tail_clamped_first",
            "tail_clamped_next",
            "tail_zero_clamped_first",
            "tail_zero_clamped_next",
            "tail_and_clamped_first",
            "tail_and_clamped_next",
            "tail_clamped_last",
            "tail_clamped_empty_last",
        ],
        "tail_inclusive_boundary_fixture_keys": [
            "tail_inclusive_boundary_next",
            "tail_inclusive_boundary_zero",
            "tail_inclusive_boundary_and",
        ],
    },
    "tools/lib/rbtree.zig": {
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
        "cached_leftmost_fixture_keys": [
            "cached_leftmost_return_serials",
        ],
    },
    "tools/lib/string.zig": {
        "parity_fixture_keys": [
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
        ],
    },
}

SMOKE_MARKERS = {
    "bitmap": (
        'test "phase1 host-tools smoke keeps bitmap alias zero-size and empty-format edges aligned" {',
        "bitmap.copy(",
        "bitmap.bitmap_copy(",
        "bitmap.copyClearTail(",
        "bitmap.bitmap_copy_clear_tail(",
        "bitmap.copyAndExtend(",
        "bitmap.bitmap_copy_and_extend(",
        "bitmap.scnprintf(",
        "bitmap.bitmap_scnprintf(",
    ),
    "find_bit": (
        'test "phase1 host-tools smoke keeps find_bit andnot and clump anchors aligned" {',
        "find_bit.findFirstAndNotBit(",
        "find_bit.find_next_andnot_bit(",
        "find_bit._find_next_andnot_bit(",
        "find_bit.findFirstClump8(",
        "find_bit.find_first_clump8(",
        "find_bit.find_next_clump8(",
        "find_bit._find_next_clump8(",
    ),
    "rbtree": (
        "rbtree.findFirst(",
        "rbtree.nextMatch(",
        "rbtree.matchIterator(",
        "cached_leftmost_return_serials",
        "rbtree.addCached(",
        "rbtree.eraseCached(",
        "rbtree.firstCached(",
    ),
    "string": (
        "string.sysfsMatchString(",
        "string.sysfs_streq(",
        "string.matchString(",
        "string.match_string(",
        "string.strnchr(",
        "string.strnchrNul(",
        "string.strnchrnul(",
        "string.strspn(",
    ),
}

SOURCE_MARKERS = {
    BITMAP_REL: (
        'test "bitmap copy alias preserves raw source words without tail clearing" {',
        'test "bitmap scnprintf leaves the caller buffer untouched for an empty bitmap" {',
        'test "bitmap Linux-style aliases mirror copy logical range and format helpers" {',
    ),
    FIND_BIT_REL: (
        'test "find first and next set bits across words, with andnot gaps explicit" {',
        'test "clump8 past-end scans return without reading bitmap words" {',
        'test "Linux-style aliases mirror the primary find helpers, including andnot" {',
    ),
    RBTREE_REL: (
        'test "rbtree nextMatch walks the duplicate range in order" {',
        'test "rbtree matchIterator walks the duplicate range in order" {',
        'test "rbtree cached-root Linux-style aliases mirror the primary helpers" {',
    ),
    STRING_REL: (
        'test "sysfsMatchString finds newline-aware matches and preserves first-match order" {',
        'test "strcmp mirrors C-string lexical ordering" {',
        'test "strnchrNul returns the first match, NUL, or count boundary" {',
    ),
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


def read_text(root: Path, rel: Path) -> str:
    return (root / rel).read_text(encoding="utf-8")


def read_manifest(root: Path) -> object:
    return json.loads(
        read_text(root, MANIFEST_REL),
        object_pairs_hook=DuplicateTrackingDict,
    )


def collect_failures(root: Path) -> list[str]:
    failures = [f"missing_file:{rel.as_posix()}" for rel in REQUIRED_FILES if not (root / rel).is_file()]
    if failures:
        return failures

    manifest = read_manifest(root)
    fixture = json.loads(read_text(root, FIXTURE_REL))
    if not isinstance(manifest, dict):
        return [f"{MANIFEST_REL.as_posix()}:expected=dict:actual={type(manifest).__name__}"]
    if isinstance(manifest, DuplicateTrackingDict) and manifest.duplicate_keys:
        return [
            f"{MANIFEST_REL.as_posix()}:duplicate_top_level_key:{key}"
            for key in manifest.duplicate_keys
        ]

    lane = manifest.get("lane_sequencing")
    if not isinstance(lane, dict):
        return [f"{MANIFEST_REL.as_posix()}:lane_sequencing:expected=dict"]
    direct = lane.get("direct_anchor_followup_helpers")
    if direct != EXPECTED_DIRECT_HELPERS:
        return [
            f"{MANIFEST_REL.as_posix()}:direct_anchor_followup_helpers:expected={EXPECTED_DIRECT_HELPERS!r}:actual={direct!r}"
        ]

    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        return [f"{MANIFEST_REL.as_posix()}:review_anchors:expected=dict"]
    if not isinstance(fixture, dict):
        return [f"{FIXTURE_REL.as_posix()}:expected=dict:actual={type(fixture).__name__}"]

    for helper, expectations in EXPECTED_MANIFEST_KEYS.items():
        actual = review_anchors.get(helper)
        if not isinstance(actual, dict):
            failures.append(f"{MANIFEST_REL.as_posix()}:review_anchors:{helper}:expected=dict")
            continue
        for key, expected_value in expectations.items():
            if actual.get(key) != expected_value:
                failures.append(
                    f"{MANIFEST_REL.as_posix()}:review_anchors:{helper}:{key}:expected={expected_value!r}:actual={actual.get(key)!r}"
                )

    fixture_sections = {
        "tools/lib/bitmap.zig": "bitmap",
        "tools/lib/find_bit.zig": "find_bit",
        "tools/lib/rbtree.zig": "rbtree",
        "tools/lib/string.zig": "string",
    }
    for helper, expectations in EXPECTED_MANIFEST_KEYS.items():
        section_name = fixture_sections[helper]
        section = fixture.get(section_name)
        if not isinstance(section, dict):
            failures.append(f"{FIXTURE_REL.as_posix()}:{section_name}:expected=dict")
            continue
        for key_name, key_list in expectations.items():
            if "fixture_keys" not in key_name:
                continue
            for key in key_list:
                if key not in section:
                    failures.append(f"{FIXTURE_REL.as_posix()}:{section_name}:missing_key:{key}")

    smoke_text = read_text(root, SMOKE_REL)
    for group, markers in SMOKE_MARKERS.items():
        for marker in markers:
            if marker not in smoke_text:
                failures.append(f"{SMOKE_REL.as_posix()}:{group}:missing_marker:{marker}")

    for rel, markers in SOURCE_MARKERS.items():
        source_text = read_text(root, rel)
        for marker in markers:
            if marker not in source_text:
                failures.append(f"{rel.as_posix()}:missing_marker:{marker}")

    return failures


def write_text(root: Path, rel: Path, text: str) -> None:
    destination = root / rel
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def sample_manifest() -> str:
    return json.dumps(
        {
            "phase": "Phase 1",
            "status": "closed",
            "lane_sequencing": {
                "direct_anchor_followup_helpers": EXPECTED_DIRECT_HELPERS,
            },
            "review_anchors": EXPECTED_MANIFEST_KEYS,
        },
        indent=2,
    ) + "\n"


def sample_smoke() -> str:
    lines: list[str] = []
    for markers in SMOKE_MARKERS.values():
        lines.extend(markers)
    return "\n".join(lines) + "\n"


def sample_source(rel: Path) -> str:
    return "\n".join(SOURCE_MARKERS[rel]) + "\n"


def build_sample_repo(root: Path) -> None:
    write_text(root, MANIFEST_REL, sample_manifest())
    fixture = {
        "bitmap": {key: 1 for key in EXPECTED_MANIFEST_KEYS["tools/lib/bitmap.zig"]["parity_fixture_keys"]},
        "find_bit": {
            key: 1
            for key in EXPECTED_MANIFEST_KEYS["tools/lib/find_bit.zig"]["tail_clamp_fixture_keys"]
            + EXPECTED_MANIFEST_KEYS["tools/lib/find_bit.zig"]["tail_inclusive_boundary_fixture_keys"]
        },
        "rbtree": {
            key: 1
            for key in EXPECTED_MANIFEST_KEYS["tools/lib/rbtree.zig"]["parity_fixture_keys"]
            + EXPECTED_MANIFEST_KEYS["tools/lib/rbtree.zig"]["cached_leftmost_fixture_keys"]
        },
        "string": {key: 1 for key in EXPECTED_MANIFEST_KEYS["tools/lib/string.zig"]["parity_fixture_keys"]},
    }
    write_text(root, FIXTURE_REL, json.dumps(fixture, indent=2) + "\n")
    write_text(root, SMOKE_REL, sample_smoke())
    for rel in SOURCE_MARKERS:
        write_text(root, rel, sample_source(rel))


def mutate_manifest(root: Path, callback) -> None:
    manifest_path = root / MANIFEST_REL
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    callback(manifest)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def run_self_test() -> int:
    cases = [
        ("baseline", None),
        (
            "missing_bitmap_smoke_marker",
            lambda root: write_text(
                root,
                SMOKE_REL,
                sample_smoke().replace("bitmap.bitmap_scnprintf(\n", "", 1),
            ),
        ),
        (
            "drifted_direct_helper_list",
            lambda root: mutate_manifest(
                root,
                lambda manifest: manifest["lane_sequencing"].__setitem__(
                    "direct_anchor_followup_helpers",
                    ["tools/lib/bitmap.zig"],
                ),
            ),
        ),
        (
            "missing_rbtree_manifest_key",
            lambda root: mutate_manifest(
                root,
                lambda manifest: manifest["review_anchors"]["tools/lib/rbtree.zig"].pop(
                    "cached_leftmost_fixture_keys"
                ),
            ),
        ),
        (
            "missing_string_source_anchor",
            lambda root: write_text(
                root,
                STRING_REL,
                sample_source(STRING_REL).replace(
                    'test "strcmp mirrors C-string lexical ordering" {\n',
                    "",
                    1,
                ),
            ),
        ),
        (
            "missing_find_bit_fixture_key",
            lambda root: write_text(
                root,
                FIXTURE_REL,
                json.dumps(
                    {
                        **json.loads((root / FIXTURE_REL).read_text(encoding="utf-8")),
                        "find_bit": {
                            key: value
                            for key, value in json.loads((root / FIXTURE_REL).read_text(encoding="utf-8"))["find_bit"].items()
                            if key != "tail_clamped_last"
                        },
                    },
                    indent=2,
                )
                + "\n",
            ),
        ),
    ]

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-direct-helper-parity-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            if mutate is not None:
                mutate(root)
            failures = collect_failures(root)
            if name == "baseline":
                if failures:
                    print(f"phase1-direct-helper-parity:{name}:unexpected={failures}")
                    return 1
            elif not failures:
                print(f"phase1-direct-helper-parity:{name}:expected_failure")
                return 1

    print("PHASE1_DIRECT_HELPER_PARITY_SELF_TEST=pass")
    print(f"PHASE1_DIRECT_HELPER_PARITY_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", help="override the repository root used for checks")
    parser.add_argument("--self-test", action="store_true", help="run checker self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.repo_root))
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_DIRECT_HELPER_PARITY=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
