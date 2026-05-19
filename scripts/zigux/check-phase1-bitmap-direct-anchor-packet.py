#!/usr/bin/env python3
"""Validate the bounded Phase 1 bitmap direct-anchor reminder packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
BITMAP_HELPER_REL = Path("tools/lib/bitmap.zig")

REQUIRED_FILES = (
    PHASE1_CLOSURE_REL,
    MANIFEST_REL,
    BITMAP_HELPER_REL,
)

EXPECTED_PHASE = "Phase 1"
EXPECTED_STATUS = "closed"

EXPECTED_DIRECT_ANCHOR_HELPERS = [
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
]

EXPECTED_CLOSURE_MARKERS = [
    "The current smallest helper-family tie-breaker inside that packet is the bitmap direct-anchor route:",
    "drift in the live caller-window or multiword-tail `orBits()` clamp proofs",
]

EXPECTED_BITMAP_SOURCE_SYMBOLS = [
    "pub fn orBits(dst: []Word, src1: []const Word, src2: []const Word, nbits: usize) void {",
    "pub fn bitmap_or(dst: []Word, src1: []const Word, src2: []const Word, nbits: usize) void {",
]

EXPECTED_BITMAP_DIRECT_TEST_ANCHORS = [
    'test "bitmap range helpers preserve edges across whole-word spans"',
    'test "bitmap copy alias preserves raw source words without tail clearing"',
    'test "bitmap copy aliases preserve tail clearing and extension semantics"',
    'test "bitmap copy and extend handles zero and aligned counts"',
    'test "bitmap copy helpers keep zero-sized destination views untouched"',
    'test "bitmap zero-bit logical helpers stay explicit"',
    'test "bitmap full empty and weight ignore out-of-range tail bits"',
    'test "bitmap or keeps caller-selected bit window"',
    'test "bitmap or across a multiword tail still lets callers clamp the last word"',
    'test "bitmap scnprintf keeps contiguous ranges merged across word boundaries"',
    'test "bitmap scnprintf truncates and keeps a terminator slot"',
    'test "bitmap scnprintf handles terminator-only and zero-length caller views"',
    'test "bitmap scnprintf leaves the caller buffer untouched for an empty bitmap"',
    'test "bitmap Linux-style aliases mirror copy logical range and format helpers"',
    'test "bitmap Linux-style aliases mirror size state and allocation helpers"',
]


def repo_root(override: str | None) -> Path:
    return Path(override).resolve() if override else DEFAULT_ROOT


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_exact_occurrence(text: str, label: str, needle: str) -> list[str]:
    count = text.count(needle)
    return [] if count == 1 else [f"{label}:expected_once:actual_count={count}:{needle}"]


def require_exact_value(label: str, actual: object, expected: object) -> list[str]:
    return [] if actual == expected else [f"{label}:expected={expected!r}:actual={actual!r}"]


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise ValueError(f"missing expected marker: {old}")
    return text.replace(old, new, 1)


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).is_file():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    closure_text = load_text(root, PHASE1_CLOSURE_REL)
    for marker in EXPECTED_CLOSURE_MARKERS:
        failures.extend(
            require_exact_occurrence(
                closure_text,
                f"{PHASE1_CLOSURE_REL.as_posix()}:closure_marker",
                marker,
            )
        )

    manifest = json.loads(load_text(root, MANIFEST_REL))
    if not isinstance(manifest, dict):
        return [f"{MANIFEST_REL.as_posix()}:expected=dict:actual={type(manifest).__name__}"]

    failures.extend(
        require_exact_value(
            f"{MANIFEST_REL.as_posix()}:phase",
            manifest.get("phase"),
            EXPECTED_PHASE,
        )
    )
    failures.extend(
        require_exact_value(
            f"{MANIFEST_REL.as_posix()}:status",
            manifest.get("status"),
            EXPECTED_STATUS,
        )
    )

    lane_sequencing = manifest.get("lane_sequencing")
    if not isinstance(lane_sequencing, dict):
        return [
            f"{MANIFEST_REL.as_posix()}:lane_sequencing:expected=dict:actual={type(lane_sequencing).__name__}"
        ]

    failures.extend(
        require_exact_value(
            f"{MANIFEST_REL.as_posix()}:lane_sequencing.direct_anchor_followup_helpers",
            lane_sequencing.get("direct_anchor_followup_helpers"),
            EXPECTED_DIRECT_ANCHOR_HELPERS,
        )
    )

    helper_text = load_text(root, BITMAP_HELPER_REL)
    seen: set[str] = set()
    for symbol in EXPECTED_BITMAP_SOURCE_SYMBOLS:
        failures.extend(
            require_exact_occurrence(
                helper_text,
                f"{BITMAP_HELPER_REL.as_posix()}:source_symbol",
                symbol,
            )
        )
        seen.add(symbol)

    for anchor in EXPECTED_BITMAP_DIRECT_TEST_ANCHORS:
        if anchor in seen:
            continue
        failures.extend(
            require_exact_occurrence(
                helper_text,
                f"{BITMAP_HELPER_REL.as_posix()}:direct_test_anchor",
                anchor,
            )
        )
        seen.add(anchor)

    return failures


def make_fixture_tree(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        write_text(root / relative_path, f"fixture for {relative_path.as_posix()}\n")

    write_text(
        root / PHASE1_CLOSURE_REL,
        "\n".join(
            [
                "# Phase 1 Closure",
                "",
                EXPECTED_CLOSURE_MARKERS[0],
                "Keep bitmap parked unless a fresh reread finds "
                + EXPECTED_CLOSURE_MARKERS[1]
                + ", drift in empty-buffer formatting coverage, or committed replay drift.",
                "",
            ]
        ),
    )

    write_text(
        root / MANIFEST_REL,
        json.dumps(
            {
                "phase": EXPECTED_PHASE,
                "status": EXPECTED_STATUS,
                "lane_sequencing": {
                    "direct_anchor_followup_helpers": EXPECTED_DIRECT_ANCHOR_HELPERS,
                },
            },
            indent=2,
        )
        + "\n",
    )

    helper_lines = []
    helper_lines.extend(EXPECTED_BITMAP_SOURCE_SYMBOLS)
    helper_lines.extend(EXPECTED_BITMAP_DIRECT_TEST_ANCHORS)
    write_text(root / BITMAP_HELPER_REL, "\n".join(helper_lines) + "\n")


def run_self_test() -> int:
    cases = [
        ("baseline", None),
        (
            "missing_closure_marker",
            lambda root: write_text(
                root / PHASE1_CLOSURE_REL,
                replace_once(
                    load_text(root, PHASE1_CLOSURE_REL),
                    EXPECTED_CLOSURE_MARKERS[0] + "\n",
                    "",
                ),
            ),
        ),
        (
            "missing_direct_anchor_helper",
            lambda root: write_text(
                root / MANIFEST_REL,
                json.dumps(
                    {
                        "phase": EXPECTED_PHASE,
                        "status": EXPECTED_STATUS,
                        "lane_sequencing": {
                            "direct_anchor_followup_helpers": EXPECTED_DIRECT_ANCHOR_HELPERS[1:],
                        },
                    },
                    indent=2,
                )
                + "\n",
            ),
        ),
        (
            "missing_bitmap_source_symbol",
            lambda root: write_text(
                root / BITMAP_HELPER_REL,
                replace_once(
                    load_text(root, BITMAP_HELPER_REL),
                    EXPECTED_BITMAP_SOURCE_SYMBOLS[0] + "\n",
                    "",
                ),
            ),
        ),
        (
            "missing_bitmap_direct_test_anchor",
            lambda root: write_text(
                root / BITMAP_HELPER_REL,
                replace_once(
                    load_text(root, BITMAP_HELPER_REL),
                    EXPECTED_BITMAP_DIRECT_TEST_ANCHORS[7] + "\n",
                    "",
                ),
            ),
        ),
        (
            "duplicate_bitmap_direct_test_anchor",
            lambda root: write_text(
                root / BITMAP_HELPER_REL,
                load_text(root, BITMAP_HELPER_REL) + EXPECTED_BITMAP_DIRECT_TEST_ANCHORS[7] + "\n",
            ),
        ),
    ]

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-bitmap-direct-anchor-") as tmp:
            root = Path(tmp)
            make_fixture_tree(root)
            if mutate is not None:
                mutate(root)
            failures = collect_failures(root)
            if name == "baseline":
                if failures:
                    print(f"phase1-bitmap-direct-anchor-self-test:{name}:unexpected={failures}")
                    return 1
            elif not failures:
                print(f"phase1-bitmap-direct-anchor-self-test:{name}:expected_failure")
                return 1

    print("PHASE1_BITMAP_DIRECT_ANCHOR_SELF_TEST=pass")
    print(f"PHASE1_BITMAP_DIRECT_ANCHOR_SELF_TEST_CASE_COUNT={len(cases)}")
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

    print("PHASE1_BITMAP_DIRECT_ANCHOR_CHECK=pass")
    print("PHASE1_BITMAP_DIRECT_ANCHOR_MODE=current-master-safe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
