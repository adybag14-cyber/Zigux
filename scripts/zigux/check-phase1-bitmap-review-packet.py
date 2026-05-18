#!/usr/bin/env python3
"""Guard the Phase 1 bitmap review packet against manifest and helper drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any


DEFAULT_ROOT = Path(__file__).resolve().parents[2]
BITMAP_HELPER_REL = Path("tools/lib/bitmap.zig")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")

EXPECTED_BITMAP_PACKET = {
    "helper_test_anchors": [
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
        'test "bitmap scnprintf truncates and keeps a terminator slot"',
        'test "bitmap scnprintf handles terminator-only and zero-length caller views"',
        'test "bitmap scnprintf leaves the caller buffer untouched for an empty bitmap"',
        'test "bitmap allocation helpers size zero fill and reset optionals"',
    ],
    "first_word_boundary_anchor": 'test "bitmap range helpers preserve edges across whole-word spans"',
    "final_partial_word_anchor": 'test "bitmap range helpers preserve edges across whole-word spans"',
    "fill_tail_clamp_anchor": 'test "bitmap full empty and weight ignore out-of-range tail bits"',
    "predicate_tail_mask_anchor": 'test "bitmap tail-masked helpers ignore out-of-range differences"',
    "phase1_helper_replay_anchor": 'test "phase 1 helper ports match committed parity fixture"',
    "review_packet_summary": (
        "shared Phase 1 fixture keys now own bitmap allocator sizing, zero-filled allocation words, "
        "scnprintf output, truncation, tiny-buffer, and partial-window xor replay, while current "
        "master keeps the direct helper-local bitmap packet bounded to whole-word range edges, raw "
        "copy alias behavior, tail-clearing and extension semantics, zero and aligned copyAndExtend "
        "handling, zero-sized destination-view no-op coverage, tail-masked predicate behavior, "
        "out-of-range tail-bit full or empty or weight masking, caller-window xor clamping, "
        "terminator-only and zero-length caller-view formatting, empty-bitmap caller-buffer "
        "preservation, and allocator optional-reset coverage."
    ),
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
    "scnprintf_cross_word_anchor": 'test "bitmap scnprintf keeps contiguous ranges merged across word boundaries"',
    "scnprintf_truncation_anchor": 'test "bitmap scnprintf truncates and keeps a terminator slot"',
    "empty_buffer_anchor": 'test "bitmap scnprintf leaves the caller buffer untouched for an empty bitmap"',
    "copy_alias_anchor": 'test "bitmap copy aliases preserve tail clearing and extension semantics"',
    "copy_raw_alias_anchor": 'test "bitmap copy alias preserves raw source words without tail clearing"',
    "copy_zero_and_aligned_anchors": [
        'test "bitmap copy and extend handles zero and aligned counts"',
        'test "bitmap copy helpers keep zero-sized destination views untouched"',
    ],
    "zero_bit_noop_anchor": "",
    "zero_bit_binary_identity_anchor": "",
    "linux_alias_anchor": "",
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

LIST_FIELDS = (
    "helper_test_anchors",
    "parity_fixture_keys",
    "partial_xor_review_fields",
    "copy_zero_and_aligned_anchors",
)

SCALAR_FIELDS = (
    "first_word_boundary_anchor",
    "final_partial_word_anchor",
    "fill_tail_clamp_anchor",
    "predicate_tail_mask_anchor",
    "phase1_helper_replay_anchor",
    "review_packet_summary",
    "scnprintf_cross_word_anchor",
    "scnprintf_truncation_anchor",
    "empty_buffer_anchor",
    "copy_alias_anchor",
    "copy_raw_alias_anchor",
    "zero_bit_noop_anchor",
    "zero_bit_binary_identity_anchor",
    "linux_alias_anchor",
    "next_safe_step_note",
)

SOURCE_ANCHOR_FIELDS = (
    "scnprintf_cross_word_anchor",
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json(root: Path, relative_path: Path) -> Any:
    return json.loads(load_text(root, relative_path))


def require_exact_occurrence(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_exact_value(label: str, actual: object, expected: object) -> list[str]:
    return [] if actual == expected else [f"{label}:expected={expected!r}:actual={actual!r}"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for relative_path in (BITMAP_HELPER_REL, MANIFEST_REL):
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

    bitmap_packet = review_anchors.get("tools/lib/bitmap.zig")
    if not isinstance(bitmap_packet, dict):
        return [
            f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/bitmap.zig:expected=dict:actual={type(bitmap_packet).__name__}"
        ]

    for field in LIST_FIELDS:
        failures.extend(
            require_exact_value(
                f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/bitmap.zig:{field}",
                bitmap_packet.get(field),
                EXPECTED_BITMAP_PACKET[field],
            )
        )
    for field in SCALAR_FIELDS:
        failures.extend(
            require_exact_value(
                f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/bitmap.zig:{field}",
                bitmap_packet.get(field),
                EXPECTED_BITMAP_PACKET[field],
            )
        )

    helper_text = load_text(root, BITMAP_HELPER_REL)
    for anchor in EXPECTED_BITMAP_PACKET["helper_test_anchors"]:
        failures.extend(
            require_exact_occurrence(
                helper_text,
                f"{BITMAP_HELPER_REL.as_posix()}:helper_test_anchor",
                anchor,
            )
        )
    for field in SOURCE_ANCHOR_FIELDS:
        failures.extend(
            require_exact_occurrence(
                helper_text,
                f"{BITMAP_HELPER_REL.as_posix()}:{field}",
                EXPECTED_BITMAP_PACKET[field],
            )
        )

    return failures


def write_file(root: Path, relative_path: Path, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    write_file(
        root,
        BITMAP_HELPER_REL,
        "\n".join(
            EXPECTED_BITMAP_PACKET["helper_test_anchors"]
            + [EXPECTED_BITMAP_PACKET["scnprintf_cross_word_anchor"]]
        )
        + "\n",
    )
    write_file(
        root,
        MANIFEST_REL,
        json.dumps(
            {"review_anchors": {"tools/lib/bitmap.zig": EXPECTED_BITMAP_PACKET}},
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase1-bitmap-review-ok-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        failures = collect_failures(root)
        if failures:
            print("self-test:success:unexpected_failures")
            for item in failures:
                print(item)
            return 1

    mutation_specs = [
        ("missing_helper_file", "helper_file", "remove"),
        ("missing_manifest_file", "manifest_file", "remove"),
        ("missing_helper_anchor", "helper_anchor", "remove"),
        ("missing_cross_word_anchor", "cross_word_anchor", "remove"),
        ("duplicate_helper_anchor", "helper_anchor", "duplicate"),
        ("scalar_field_drift", "first_word_boundary_anchor", "manifest"),
        ("list_field_drift", "parity_fixture_keys", "manifest"),
        ("next_step_drift", "next_safe_step_note", "manifest"),
    ]

    for name, target, kind in mutation_specs:
        with tempfile.TemporaryDirectory(prefix=f"phase1-bitmap-review-{name}-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)

            if kind == "remove":
                if target == "helper_file":
                    (root / BITMAP_HELPER_REL).unlink()
                elif target == "manifest_file":
                    (root / MANIFEST_REL).unlink()
                else:
                    path = root / BITMAP_HELPER_REL
                    marker = (
                        EXPECTED_BITMAP_PACKET["helper_test_anchors"][0] + "\n"
                        if target == "helper_anchor"
                        else EXPECTED_BITMAP_PACKET["scnprintf_cross_word_anchor"] + "\n"
                    )
                    path.write_text(path.read_text(encoding="utf-8").replace(marker, "", 1), encoding="utf-8")
            elif kind == "duplicate":
                path = root / BITMAP_HELPER_REL
                marker = EXPECTED_BITMAP_PACKET["helper_test_anchors"][0] + "\n"
                text = path.read_text(encoding="utf-8")
                path.write_text(text.replace(marker, marker + marker, 1), encoding="utf-8")
            else:
                path = root / MANIFEST_REL
                manifest = json.loads(path.read_text(encoding="utf-8"))
                packet = manifest["review_anchors"]["tools/lib/bitmap.zig"]
                value = packet[target]
                if isinstance(value, list):
                    packet[target] = value[1:]
                else:
                    packet[target] = f"{value} drift"
                path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

            failures = collect_failures(root)
            if not failures:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("self-test:ok")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        for item in failures:
            print(item)
        return 1

    print("phase1-bitmap-review-packet:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
