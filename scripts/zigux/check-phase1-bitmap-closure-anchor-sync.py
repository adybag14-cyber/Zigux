#!/usr/bin/env python3
"""Guard the Phase 1 bitmap closure-anchor packet against manifest/source drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
BITMAP_HELPER_REL = Path("tools/lib/bitmap.zig")

EXPECTED_HELPERS = [
    "tools/lib/argv_split.zig",
    "tools/lib/bitmap.zig",
    "tools/lib/cmdline.zig",
    "tools/lib/ctype.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/hweight.zig",
    "tools/lib/list_sort.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/slab.zig",
    "tools/lib/str_error_r.zig",
    "tools/lib/string.zig",
    "tools/lib/vsprintf.zig",
    "tools/lib/zalloc.zig",
]

EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS = [
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
]

EXPECTED_BITMAP_HELPER_TEST_ANCHORS = [
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
]

EXPECTED_BITMAP_NEXT_SAFE_STEP_NOTE = (
    "If this helper lane reopens, keep bitmap parked unless a fresh reread finds new "
    "direct-anchor drift inside the current helper-local packet or committed shared "
    "replay drift in the bitmap parity fields; current master still ships direct "
    "fill-tail clamp, copy-alias, truncation, cross-word scnprintf, empty-buffer, and "
    "allocator-reset anchors here, while zero-bit and Linux-style alias follow-through "
    "no longer live in the helper-local packet, and if the separate bitmap "
    "closure-validator anchor-sync repair is still outstanding, treat that as the only "
    "other bitmap follow-through."
)


def repo_root(override: str | None) -> Path:
    return Path(override).resolve() if override else DEFAULT_ROOT


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json(root: Path, relative_path: Path) -> Any:
    return json.loads(load_text(root, relative_path))


def require_exact_value(label: str, actual: object, expected: object) -> list[str]:
    if actual == expected:
        return []
    return [f"{label}:expected={expected!r}:actual={actual!r}"]


def require_exact_occurrence(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    if count == 1:
        return []
    return [f"{label}:expected_once:actual_count={count}:{marker}"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in (MANIFEST_REL, BITMAP_HELPER_REL):
        if not (root / relative_path).is_file():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    try:
        manifest = load_json(root, MANIFEST_REL)
    except json.JSONDecodeError as exc:
        return [f"{MANIFEST_REL.as_posix()}:json_decode_error:{exc}"]
    if not isinstance(manifest, dict):
        return [f"{MANIFEST_REL.as_posix()}:expected=dict:actual={type(manifest).__name__}"]

    failures.extend(
        require_exact_value(f"{MANIFEST_REL.as_posix()}:phase", manifest.get("phase"), "Phase 1")
    )
    failures.extend(
        require_exact_value(f"{MANIFEST_REL.as_posix()}:status", manifest.get("status"), "closed")
    )
    failures.extend(
        require_exact_value(
            f"{MANIFEST_REL.as_posix()}:helper_count",
            manifest.get("helper_count"),
            len(EXPECTED_HELPERS),
        )
    )
    failures.extend(
        require_exact_value(
            f"{MANIFEST_REL.as_posix()}:helpers",
            manifest.get("helpers"),
            EXPECTED_HELPERS,
        )
    )

    lane_sequencing = manifest.get("lane_sequencing")
    if not isinstance(lane_sequencing, dict):
        return [f"{MANIFEST_REL.as_posix()}:lane_sequencing:expected=dict"]
    failures.extend(
        require_exact_value(
            f"{MANIFEST_REL.as_posix()}:lane_sequencing.direct_anchor_followup_helpers",
            lane_sequencing.get("direct_anchor_followup_helpers"),
            EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS,
        )
    )

    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        return [f"{MANIFEST_REL.as_posix()}:review_anchors:expected=dict"]
    bitmap_review = review_anchors.get("tools/lib/bitmap.zig")
    if not isinstance(bitmap_review, dict):
        return [f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/bitmap.zig:expected=dict"]

    failures.extend(
        require_exact_value(
            f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/bitmap.zig.helper_test_anchors",
            bitmap_review.get("helper_test_anchors"),
            EXPECTED_BITMAP_HELPER_TEST_ANCHORS,
        )
    )
    failures.extend(
        require_exact_value(
            f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/bitmap.zig.next_safe_step_note",
            bitmap_review.get("next_safe_step_note"),
            EXPECTED_BITMAP_NEXT_SAFE_STEP_NOTE,
        )
    )

    bitmap_text = load_text(root, BITMAP_HELPER_REL)
    for anchor in EXPECTED_BITMAP_HELPER_TEST_ANCHORS:
        failures.extend(
            require_exact_occurrence(
                bitmap_text,
                f"{BITMAP_HELPER_REL.as_posix()}:helper_test_anchor",
                anchor,
            )
        )

    return failures


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise ValueError(f"missing expected marker: {old}")
    return text.replace(old, new, 1)


def build_fixture_tree(root: Path) -> None:
    write_text(
        root / MANIFEST_REL,
        json.dumps(
            {
                "phase": "Phase 1",
                "status": "closed",
                "helper_count": len(EXPECTED_HELPERS),
                "helpers": EXPECTED_HELPERS,
                "lane_sequencing": {
                    "direct_anchor_followup_helpers": EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS,
                },
                "review_anchors": {
                    "tools/lib/bitmap.zig": {
                        "helper_test_anchors": EXPECTED_BITMAP_HELPER_TEST_ANCHORS,
                        "next_safe_step_note": EXPECTED_BITMAP_NEXT_SAFE_STEP_NOTE,
                    },
                },
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        root / BITMAP_HELPER_REL,
        "\n".join(EXPECTED_BITMAP_HELPER_TEST_ANCHORS) + "\n",
    )


def run_self_test() -> int:
    cases: list[tuple[str, object, bool]] = [
        ("baseline", None, True),
        ("missing_bitmap_file", "missing_bitmap_file", False),
        ("bad_helper_count", "bad_helper_count", False),
        ("bad_direct_anchor_list", "bad_direct_anchor_list", False),
        ("bad_bitmap_note", "bad_bitmap_note", False),
        ("bad_bitmap_anchor_list", "bad_bitmap_anchor_list", False),
        ("missing_source_anchor", ("source_anchor", "remove"), False),
        ("duplicate_source_anchor", ("source_anchor", "duplicate"), False),
    ]

    for name, mutation, expect_ok in cases:
        with tempfile.TemporaryDirectory(prefix=f"phase1-bitmap-anchor-{name}-") as tmpdir:
            root = Path(tmpdir)
            build_fixture_tree(root)

            if mutation == "missing_bitmap_file":
                (root / BITMAP_HELPER_REL).unlink()
            elif mutation == "bad_helper_count":
                manifest = load_json(root, MANIFEST_REL)
                manifest["helper_count"] = 12
                write_text(root / MANIFEST_REL, json.dumps(manifest, indent=2) + "\n")
            elif mutation == "bad_direct_anchor_list":
                manifest = load_json(root, MANIFEST_REL)
                manifest["lane_sequencing"]["direct_anchor_followup_helpers"] = ["tools/lib/bitmap.zig"]
                write_text(root / MANIFEST_REL, json.dumps(manifest, indent=2) + "\n")
            elif mutation == "bad_bitmap_note":
                manifest = load_json(root, MANIFEST_REL)
                manifest["review_anchors"]["tools/lib/bitmap.zig"]["next_safe_step_note"] = "drift"
                write_text(root / MANIFEST_REL, json.dumps(manifest, indent=2) + "\n")
            elif mutation == "bad_bitmap_anchor_list":
                manifest = load_json(root, MANIFEST_REL)
                manifest["review_anchors"]["tools/lib/bitmap.zig"]["helper_test_anchors"] = ["drift"]
                write_text(root / MANIFEST_REL, json.dumps(manifest, indent=2) + "\n")
            elif isinstance(mutation, tuple):
                text = load_text(root, BITMAP_HELPER_REL)
                anchor = EXPECTED_BITMAP_HELPER_TEST_ANCHORS[3]
                if mutation[1] == "remove":
                    text = replace_once(text, anchor + "\n", "")
                else:
                    text = replace_once(text, anchor + "\n", anchor + "\n" + anchor + "\n")
                write_text(root / BITMAP_HELPER_REL, text)

            failures = collect_failures(root)
            ok = not failures
            if ok != expect_ok:
                print(f"phase1-bitmap-closure-anchor-sync-self-test:{name}:unexpected={failures}")
                return 1

    print("PHASE1_BITMAP_CLOSURE_ANCHOR_SYNC_SELF_TEST=pass")
    print(f"PHASE1_BITMAP_CLOSURE_ANCHOR_SYNC_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run built-in checker self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("phase1-bitmap-closure-anchor-sync:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
