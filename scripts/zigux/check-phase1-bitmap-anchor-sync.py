#!/usr/bin/env python3
"""Validate the current-master Phase 1 bitmap review packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
BITMAP_REL = Path("tools/lib/bitmap.zig")

BITMAP_HELPER = "tools/lib/bitmap.zig"

EXPECTED_HELPER_TEST_ANCHORS = [
    'test "bitmap set clear weight and empty full helpers"',
    'test "bitmap range helpers preserve edges across whole-word spans"',
    'test "bitmap copy alias preserves raw source words without tail clearing"',
    'test "bitmap copy aliases preserve tail clearing and extension semantics"',
    'test "bitmap copy and extend handles zero and aligned counts"',
    'test "bitmap copy helpers keep zero-sized destination views untouched"',
    'test "bitmap and andnot equal intersects subset"',
    'test "bitmap tail-masked helpers ignore out-of-range differences"',
    'test "bitmap full empty and weight ignore out-of-range tail bits"',
    'test "bitmap xor keeps caller-selected bit window"',
    'test "bitmap xor across a multiword tail still lets callers clamp the last word"',
    'test "bitmap scnprintf collapses contiguous ranges"',
    'test "bitmap scnprintf keeps contiguous ranges merged across word boundaries"',
    'test "bitmap scnprintf truncates and keeps a terminator slot"',
    'test "bitmap scnprintf handles terminator-only and zero-length caller views"',
    'test "bitmap scnprintf leaves the caller buffer untouched for an empty bitmap"',
    'test "bitmap allocation helpers size zero fill and reset optionals"',
]

EXPECTED_FIELDS = {
    "fill_tail_clamp_anchor": 'test "bitmap full empty and weight ignore out-of-range tail bits"',
    "predicate_tail_mask_anchor": 'test "bitmap tail-masked helpers ignore out-of-range differences"',
    "scnprintf_cross_word_anchor": 'test "bitmap scnprintf keeps contiguous ranges merged across word boundaries"',
    "scnprintf_truncation_anchor": 'test "bitmap scnprintf truncates and keeps a terminator slot"',
    "empty_buffer_anchor": 'test "bitmap scnprintf leaves the caller buffer untouched for an empty bitmap"',
    "copy_alias_anchor": 'test "bitmap copy aliases preserve tail clearing and extension semantics"',
    "copy_raw_alias_anchor": 'test "bitmap copy alias preserves raw source words without tail clearing"',
    "copy_zero_and_aligned_anchors": [
        'test "bitmap copy and extend handles zero and aligned counts"',
        'test "bitmap copy helpers keep zero-sized destination views untouched"',
    ],
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
    "next_safe_step_note": (
        "If this helper lane reopens, keep bitmap parked unless a fresh reread finds new "
        "direct-anchor drift inside the current helper-local packet or committed shared replay "
        "drift in the bitmap parity fields; current master still ships direct fill-tail clamp, "
        "copy-alias, truncation, cross-word scnprintf, empty-buffer, and allocator-reset anchors "
        "here, while zero-bit and Linux-style alias follow-through no longer live in the "
        "helper-local packet, and if the separate bitmap closure-validator anchor-sync repair is "
        "still outstanding, treat that as the only other bitmap follow-through."
    ),
}

CLOSURE_NEEDLE = (
    "current master still ships direct fill-tail clamp, copy-alias, truncation, cross-word "
    "scnprintf, empty-buffer, and allocator-reset anchors here"
)


def repo_root(override: str | None) -> Path:
    return Path(override).resolve() if override else DEFAULT_ROOT


def require_once(text: str, label: str, needle: str) -> list[str]:
    count = text.count(needle)
    return [] if count == 1 else [f"{label}:expected_once:actual_count={count}:{needle}"]


def require_value(label: str, actual: object, expected: object) -> list[str]:
    return [] if actual == expected else [f"{label}:expected={expected!r}:actual={actual!r}"]


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for rel in (MANIFEST_REL, CLOSURE_REL, BITMAP_REL):
        if not (root / rel).is_file():
            failures.append(f"missing_file:{rel.as_posix()}")
    if failures:
        return failures

    manifest = json.loads(load_text(root, MANIFEST_REL))
    review = manifest.get("review_anchors", {}).get(BITMAP_HELPER)
    if not isinstance(review, dict):
        return [f"{MANIFEST_REL.as_posix()}:review_anchors.{BITMAP_HELPER}:expected=dict"]

    failures.extend(
        require_value(
            f"{MANIFEST_REL.as_posix()}:{BITMAP_HELPER}:helper_test_anchors",
            review.get("helper_test_anchors"),
            EXPECTED_HELPER_TEST_ANCHORS,
        )
    )

    for key, expected in EXPECTED_FIELDS.items():
        failures.extend(
            require_value(
                f"{MANIFEST_REL.as_posix()}:{BITMAP_HELPER}:{key}",
                review.get(key),
                expected,
            )
        )

    closure_text = load_text(root, CLOSURE_REL)
    failures.extend(require_once(closure_text, f"{CLOSURE_REL.as_posix()}:bitmap_packet", CLOSURE_NEEDLE))

    helper_text = load_text(root, BITMAP_REL)
    seen: set[str] = set()
    for anchor in EXPECTED_HELPER_TEST_ANCHORS:
        if anchor not in seen:
            failures.extend(require_once(helper_text, f"{BITMAP_REL.as_posix()}:helper_test_anchor", anchor))
            seen.add(anchor)

    for value in EXPECTED_FIELDS.values():
        anchors = [value] if isinstance(value, str) else value if isinstance(value, list) else []
        for anchor in anchors:
            if isinstance(anchor, str) and anchor.startswith('test "') and anchor not in seen:
                failures.extend(require_once(helper_text, f"{BITMAP_REL.as_posix()}:named_anchor", anchor))
                seen.add(anchor)

    return failures


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise ValueError(f"missing expected marker: {old}")
    return text.replace(old, new, 1)


def make_fixture_tree(root: Path) -> None:
    manifest = {
        "review_anchors": {
            BITMAP_HELPER: {
                "helper_test_anchors": EXPECTED_HELPER_TEST_ANCHORS,
                **EXPECTED_FIELDS,
            }
        }
    }
    write_text(root / MANIFEST_REL, json.dumps(manifest, indent=2) + "\n")
    write_text(root / CLOSURE_REL, f"# Phase 1 Closure\n\n{CLOSURE_NEEDLE}\n")
    write_text(root / BITMAP_REL, "\n".join(EXPECTED_HELPER_TEST_ANCHORS) + "\n")


def mutate_manifest(root: Path, field: str, value: object) -> None:
    manifest_path = root / MANIFEST_REL
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["review_anchors"][BITMAP_HELPER][field] = value
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def run_self_test() -> int:
    cases = [
        ("baseline", None),
        ("missing_cross_word_anchor", lambda root: mutate_manifest(root, "helper_test_anchors", EXPECTED_HELPER_TEST_ANCHORS[:-5] + EXPECTED_HELPER_TEST_ANCHORS[-4:])),
        ("bad_named_field", lambda root: mutate_manifest(root, "scnprintf_cross_word_anchor", "drift")),
        ("missing_closure_note", lambda root: write_text(root / CLOSURE_REL, "# Phase 1 Closure\n\nno bitmap cue here\n")),
        (
            "missing_source_anchor",
            lambda root: write_text(
                root / BITMAP_REL,
                replace_once(load_text(root, BITMAP_REL), EXPECTED_FIELDS["scnprintf_cross_word_anchor"] + "\n", ""),
            ),
        ),
    ]

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-bitmap-anchor-") as tmp:
            root = Path(tmp)
            make_fixture_tree(root)
            if mutate is not None:
                mutate(root)
            failures = collect_failures(root)
            if name == "baseline":
                if failures:
                    print(f"phase1-bitmap-anchor-self-test:{name}:unexpected={failures}")
                    return 1
            elif not failures:
                print(f"phase1-bitmap-anchor-self-test:{name}:expected_failure")
                return 1

    print("PHASE1_BITMAP_ANCHOR_SELF_TEST=pass")
    print(f"PHASE1_BITMAP_ANCHOR_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run checker self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_BITMAP_ANCHOR_SYNC=pass")
    print("PHASE1_BITMAP_ANCHOR_MODE=current-master-safe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
