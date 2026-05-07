#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile

_SELF_PATH = Path(__file__).resolve()
ROOT = _SELF_PATH.parents[2] if len(_SELF_PATH.parents) >= 3 else _SELF_PATH.parent

CLOSURE_PATH = Path("Documentation/zigux/phase1-closure.md")
MANIFEST_PATH = Path("zigux/tests/fixtures/phase1_helper_manifest.json")

REQUIRED_CLOSURE_MARKERS = [
    "PHASE1_FIND_BIT_UNDERSCORE_ALIAS_REVIEW",
    "PHASE1_BITMAP_RAW_COPY_ALIAS_REVIEW",
    "PHASE1_BITMAP_ZERO_BIT_NOOP_REVIEW",
    'test "rbtree addCached returns the inserted node only when it becomes leftmost"',
    'test "rbtree eraseInitCached detaches nodes while keeping cached leftmost aligned"',
    'test "rbtree eraseInitCached clears singleton cached roots before reseed"',
    'test "strreplace mirrors replaceChar C-string semantics"',
    'test "strstarts mirrors the header-level prefix helper"',
    'test "strEndsWith honors C-string boundaries"',
    'test "memparse keeps signed values and their trailing rest aligned"',
    "replace_char_cstr_bytes",
]

EXPECTED_MANIFEST_FIELDS = {
    "tools/lib/bitmap.zig": {
        "copy_raw_alias_anchor": 'test "bitmap copy alias preserves raw source words without tail clearing"',
        "zero_bit_noop_anchor": 'test "bitmap zero-bit helpers stay explicit no-ops"',
        "first_word_boundary_anchor": 'test "bitmap range helpers honor exact first-word boundaries"',
    },
    "tools/lib/find_bit.zig": {
        "underscore_alias_anchor": 'test "low-level underscore aliases mirror the primary find helpers"',
    },
    "tools/lib/rbtree.zig": {
        "helper_test_anchors": [
            'test "rbtree addCached returns the inserted node only when it becomes leftmost"',
            'test "rbtree eraseInitCached detaches nodes while keeping cached leftmost aligned"',
            'test "rbtree eraseInitCached clears singleton cached roots before reseed"',
        ],
    },
    "tools/lib/string.zig": {
        "prefix_suffix_review_anchors": [
            'test "strHasPrefix honors C-string boundaries"',
            'test "strstarts mirrors the header-level prefix helper"',
            'test "strEndsWith honors C-string boundaries"',
        ],
        "memparse_review_anchors": [
            'test "memparse keeps original rest when sign is not followed by digits"',
            'test "memparse saturates signed overflow instead of trapping"',
            'test "memparse keeps signed values and their trailing rest aligned"',
            'test "memparse consumes suffix after saturation"',
        ],
        "shared_replace_char_cstr_review_summary": (
            "the shared Phase 1 string replay now exercises strtobool, strlcpy, "
            "skipSpaces, trimSpaces, removeSpaces, replaceChar, and memchrInv fixture "
            "parity, while the dedicated embedded-NUL replaceChar follow-up keeps the "
            "first-terminator stop rule explicit without widening helper-local memparse ownership"
        ),
    },
}


def read_text(root: Path, relpath: Path) -> str:
    return (root / relpath).read_text(encoding="utf-8")


def collect_closure_marker_failures(root: Path) -> list[str]:
    text = read_text(root, CLOSURE_PATH)
    failures: list[str] = []
    for marker in REQUIRED_CLOSURE_MARKERS:
        count = text.count(marker)
        if count != 1:
            failures.append(
                f"closure_marker:{marker}:expected=1:actual={count}"
            )
    return failures


def collect_manifest_failures(root: Path) -> list[str]:
    manifest = json.loads(read_text(root, MANIFEST_PATH))
    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        return ["manifest:review_anchors:expected=dict:actual=missing"]

    failures: list[str] = []
    for helper, expected_fields in EXPECTED_MANIFEST_FIELDS.items():
        helper_entry = review_anchors.get(helper)
        if not isinstance(helper_entry, dict):
            failures.append(f"manifest:{helper}:expected=dict:actual=missing")
            continue
        for field, expected in expected_fields.items():
            actual = helper_entry.get(field)
            if actual != expected:
                failures.append(f"manifest:{helper}:{field}:expected={expected!r}:actual={actual!r}")
    return failures


def validate(root: Path) -> list[str]:
    failures = collect_closure_marker_failures(root)
    failures.extend(collect_manifest_failures(root))
    return failures


def write_fixture_tree(root: Path) -> None:
    (root / CLOSURE_PATH.parent).mkdir(parents=True, exist_ok=True)
    (root / MANIFEST_PATH.parent).mkdir(parents=True, exist_ok=True)
    closure_text = "\n".join(REQUIRED_CLOSURE_MARKERS) + "\n"
    (root / CLOSURE_PATH).write_text(closure_text, encoding="utf-8")
    manifest = {
        "review_anchors": {
            helper: fields for helper, fields in EXPECTED_MANIFEST_FIELDS.items()
        }
    }
    (root / MANIFEST_PATH).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        write_fixture_tree(root)
        assert not validate(root)

        write_fixture_tree(root)
        (root / CLOSURE_PATH).write_text("\n".join(REQUIRED_CLOSURE_MARKERS[:-1]) + "\n", encoding="utf-8")
        failures = validate(root)
        assert "closure_marker:replace_char_cstr_bytes:expected=1:actual=0" in failures

        write_fixture_tree(root)
        manifest = json.loads((root / MANIFEST_PATH).read_text(encoding="utf-8"))
        del manifest["review_anchors"]["tools/lib/find_bit.zig"]["underscore_alias_anchor"]
        (root / MANIFEST_PATH).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        failures = validate(root)
        expected = (
            "manifest:tools/lib/find_bit.zig:underscore_alias_anchor:expected="
            + repr('test "low-level underscore aliases mirror the primary find helpers"')
            + ":actual=None"
        )
        assert expected in failures

        write_fixture_tree(root)
        manifest = json.loads((root / MANIFEST_PATH).read_text(encoding="utf-8"))
        manifest["review_anchors"]["tools/lib/string.zig"]["memparse_review_anchors"] = (
            manifest["review_anchors"]["tools/lib/string.zig"]["memparse_review_anchors"][:-1]
        )
        (root / MANIFEST_PATH).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        failures = validate(root)
        assert any(
            failure.startswith("manifest:tools/lib/string.zig:memparse_review_anchors:")
            for failure in failures
        )

    print("PHASE1_REVIEW_ANCHOR_PACKET_SELF_TEST=pass")
    print("PHASE1_REVIEW_ANCHOR_PACKET_SELF_TEST_CASE_COUNT=4")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the current Phase 1 closure note and helper manifest still "
            "carry the newer bitmap, find_bit, rbtree, and string review-anchor packet."
        )
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker tests.")
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to validate. Defaults to the script directory parent.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.root.resolve())
    if failures:
        print("PHASE1_REVIEW_ANCHOR_PACKET=fail")
        print("PHASE1_REVIEW_ANCHOR_PACKET_FAILURES_START")
        for failure in failures:
            print(failure)
        print("PHASE1_REVIEW_ANCHOR_PACKET_FAILURES_END")
        return 1

    print("PHASE1_REVIEW_ANCHOR_PACKET=pass")
    print(f"PHASE1_REVIEW_ANCHOR_PACKET_CLOSURE_MARKER_COUNT={len(REQUIRED_CLOSURE_MARKERS)}")
    print(f"PHASE1_REVIEW_ANCHOR_PACKET_MANIFEST_HELPER_COUNT={len(EXPECTED_MANIFEST_FIELDS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
