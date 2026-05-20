#!/usr/bin/env python3
"""Guard the current Phase 1 bitmap/find_bit direct-anchor packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
BITMAP_REL = Path("tools/lib/bitmap.zig")
FIND_BIT_REL = Path("tools/lib/find_bit.zig")

REQUIRED_FILES = (
    MANIFEST_REL,
    BITMAP_REL,
    FIND_BIT_REL,
)

EXPECTED_BITMAP_NEXT_SAFE_STEP_NOTE = (
    "If this helper lane reopens, keep bitmap parked unless a fresh reread finds new "
    "direct-anchor drift inside the current helper-local packet or committed shared replay "
    "drift in the bitmap parity fields; current master still ships direct fill-tail clamp, "
    "copy-alias, truncation, cross-word scnprintf, empty-buffer, and allocator-reset anchors "
    "here, while zero-bit and Linux-style alias follow-through no longer live in the "
    "helper-local packet, and if the separate bitmap closure-validator anchor-sync repair is "
    "still outstanding, treat that as the only other bitmap follow-through."
)

EXPECTED_FIND_BIT_HELPER_TEST_ANCHORS = [
    'test "find first and next set bits across words, with andnot gaps explicit"',
    'test "low-level underscore aliases mirror the primary find helpers, including andnot"',
    'test "Linux-style aliases mirror the primary find helpers, including andnot"',
]

EXPECTED_FIND_BIT_REVIEW_FIELDS = {
    "underscore_alias_anchor": 'test "low-level underscore aliases mirror the primary find helpers, including andnot"',
    "linux_alias_anchor": 'test "Linux-style aliases mirror the primary find helpers, including andnot"',
    "next_safe_step_note": (
        "If this helper lane reopens, keep find_bit parked unless a fresh reread finds "
        "direct-anchor drift inside same-word start-mask, inclusive-boundary, zero-window, "
        "zero-sized short-circuit, past-nbits, clump8, getValue8(), findLastBit(), "
        "underscore-alias, Linux-style alias coverage including the shipped andnot scan entry "
        "points, or tail-word skip anchors, or committed tail-clamped replay drift; do not "
        "reopen older saved validator cues or neighboring helper families."
    ),
}

EXPECTED_FIND_BIT_SOURCE_SYMBOLS = [
    "pub fn findFirstAndNotBit(addr1: []const Word, addr2: []const Word, nbits: usize) usize {",
    "pub fn find_first_andnot_bit(addr1: []const Word, addr2: []const Word, nbits: usize) usize {",
    "pub fn _find_first_andnot_bit(addr1: []const Word, addr2: []const Word, nbits: usize) usize {",
    "pub fn findNextAndNotBit(addr1: []const Word, addr2: []const Word, nbits: usize, start: usize) usize {",
    "pub fn find_next_andnot_bit(addr1: []const Word, addr2: []const Word, nbits: usize, start: usize) usize {",
    "pub fn _find_next_andnot_bit(addr1: []const Word, addr2: []const Word, nbits: usize, start: usize) usize {",
]


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json(root: Path, relative_path: Path) -> object:
    return json.loads(load_text(root, relative_path))


def require_exact_occurrence(text: str, label: str, needle: str) -> list[str]:
    count = text.count(needle)
    return [] if count == 1 else [f"{label}:expected_once:actual_count={count}:{needle}"]


def require_exact_value(label: str, actual: object, expected: object) -> list[str]:
    return [] if actual == expected else [f"{label}:expected={expected!r}:actual={actual!r}"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).is_file():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    manifest = load_json(root, MANIFEST_REL)
    if not isinstance(manifest, dict):
        return [f"{MANIFEST_REL.as_posix()}:expected=dict:actual={type(manifest).__name__}"]

    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        return [f"{MANIFEST_REL.as_posix()}:review_anchors:expected=dict:actual={type(review_anchors).__name__}"]

    bitmap_review = review_anchors.get("tools/lib/bitmap.zig")
    if not isinstance(bitmap_review, dict):
        return [f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/bitmap.zig:expected=dict:actual={type(bitmap_review).__name__}"]
    failures.extend(
        require_exact_value(
            f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/bitmap.zig:next_safe_step_note",
            bitmap_review.get("next_safe_step_note"),
            EXPECTED_BITMAP_NEXT_SAFE_STEP_NOTE,
        )
    )

    find_bit_review = review_anchors.get("tools/lib/find_bit.zig")
    if not isinstance(find_bit_review, dict):
        return [f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/find_bit.zig:expected=dict:actual={type(find_bit_review).__name__}"]

    helper_test_anchors = find_bit_review.get("helper_test_anchors")
    if not isinstance(helper_test_anchors, list):
        failures.append(
            f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/find_bit.zig:helper_test_anchors:"
            f"expected=list:actual={type(helper_test_anchors).__name__}"
        )
    else:
        for anchor in EXPECTED_FIND_BIT_HELPER_TEST_ANCHORS:
            failures.extend(
                require_exact_value(
                    f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/find_bit.zig:helper_test_anchor",
                    helper_test_anchors.count(anchor),
                    1,
                )
            )

    for key, expected in EXPECTED_FIND_BIT_REVIEW_FIELDS.items():
        failures.extend(
            require_exact_value(
                f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/find_bit.zig:{key}",
                find_bit_review.get(key),
                expected,
            )
        )

    bitmap_text = load_text(root, BITMAP_REL)
    failures.extend(
        require_exact_occurrence(
            bitmap_text,
            f"{BITMAP_REL.as_posix()}:allocator_reset_anchor",
            'test "bitmap allocation helpers size zero fill and reset optionals"',
        )
    )

    find_bit_text = load_text(root, FIND_BIT_REL)
    seen: set[str] = set()
    for anchor in EXPECTED_FIND_BIT_HELPER_TEST_ANCHORS:
        if anchor not in seen:
            failures.extend(
                require_exact_occurrence(
                    find_bit_text,
                    f"{FIND_BIT_REL.as_posix()}:helper_test_anchor",
                    anchor,
                )
            )
            seen.add(anchor)
    for symbol in EXPECTED_FIND_BIT_SOURCE_SYMBOLS:
        failures.extend(
            require_exact_occurrence(
                find_bit_text,
                f"{FIND_BIT_REL.as_posix()}:source_symbol",
                symbol,
            )
        )

    return failures


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def mutate_manifest(root: Path, mutate) -> None:
    manifest_path = root / MANIFEST_REL
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    mutate(manifest)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    write_text(
        root / MANIFEST_REL,
        json.dumps(
            {
                "review_anchors": {
                    "tools/lib/bitmap.zig": {
                        "next_safe_step_note": EXPECTED_BITMAP_NEXT_SAFE_STEP_NOTE,
                    },
                    "tools/lib/find_bit.zig": {
                        "helper_test_anchors": EXPECTED_FIND_BIT_HELPER_TEST_ANCHORS,
                        **EXPECTED_FIND_BIT_REVIEW_FIELDS,
                    },
                },
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        root / BITMAP_REL,
        'test "bitmap allocation helpers size zero fill and reset optionals"\n',
    )
    write_text(
        root / FIND_BIT_REL,
        "\n".join(EXPECTED_FIND_BIT_SOURCE_SYMBOLS + EXPECTED_FIND_BIT_HELPER_TEST_ANCHORS) + "\n",
    )


def run_self_test() -> int:
    cases = [
        ("baseline", None),
        ("missing_manifest", lambda root: (root / MANIFEST_REL).unlink()),
        (
            "bad_bitmap_note",
            lambda root: mutate_manifest(
                root,
                lambda manifest: manifest["review_anchors"]["tools/lib/bitmap.zig"].__setitem__(
                    "next_safe_step_note",
                    manifest["review_anchors"]["tools/lib/bitmap.zig"]["next_safe_step_note"].replace(
                        "allocator-reset anchors here, while zero-bit and Linux-style alias",
                        "allocator-reset anchors here, while zero-bit logical and Linux-style alias",
                        1,
                    ),
                ),
            ),
        ),
        (
            "bad_find_bit_title",
            lambda root: mutate_manifest(
                root,
                lambda manifest: manifest["review_anchors"]["tools/lib/find_bit.zig"].__setitem__(
                    "helper_test_anchors",
                    [
                        'test "find first and next set bits across words"',
                        *manifest["review_anchors"]["tools/lib/find_bit.zig"]["helper_test_anchors"][1:],
                    ],
                ),
            ),
        ),
        (
            "bad_find_bit_note",
            lambda root: mutate_manifest(
                root,
                lambda manifest: manifest["review_anchors"]["tools/lib/find_bit.zig"].__setitem__(
                    "next_safe_step_note",
                    manifest["review_anchors"]["tools/lib/find_bit.zig"]["next_safe_step_note"].replace(
                        "coverage including the shipped andnot scan entry points",
                        "alias",
                        1,
                    ),
                ),
            ),
        ),
        (
            "missing_find_bit_anchor",
            lambda root: write_text(
                root / FIND_BIT_REL,
                load_text(root, FIND_BIT_REL).replace(EXPECTED_FIND_BIT_HELPER_TEST_ANCHORS[2] + "\n", "", 1),
            ),
        ),
        (
            "missing_andnot_symbol",
            lambda root: write_text(
                root / FIND_BIT_REL,
                load_text(root, FIND_BIT_REL).replace(EXPECTED_FIND_BIT_SOURCE_SYMBOLS[0] + "\n", "", 1),
            ),
        ),
    ]

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix=f"phase1-bitmap-find-bit-{name}-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            if mutate is not None:
                mutate(root)
            failures = collect_failures(root)
            if name == "baseline":
                if failures:
                    print(f"self-test:{name}:unexpected={failures}")
                    return 1
            elif not failures:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("PHASE1_BITMAP_FIND_BIT_CURRENT_PACKET_SELF_TEST=pass")
    print(f"PHASE1_BITMAP_FIND_BIT_CURRENT_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run the built-in self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_BITMAP_FIND_BIT_CURRENT_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_BITMAP_FIND_BIT_CURRENT_PACKET=pass")
    print(f"PHASE1_BITMAP_FIND_BIT_CURRENT_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_BITMAP_FIND_BIT_CURRENT_PACKET_REQUIRED_FIND_BIT_ANCHOR_COUNT="
        f"{len(EXPECTED_FIND_BIT_HELPER_TEST_ANCHORS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
