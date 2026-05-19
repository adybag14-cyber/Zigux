#!/usr/bin/env python3
"""Guard the Phase 1 helper-specific next-safe-step packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")

REQUIRED_FILES = (
    PHASE1_CLOSURE_REL,
    LANE_NOTE_REL,
    MANIFEST_REL,
)

EXPECTED_CLOSURE_LINE = (
    "- `PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface or one helper-family "
    "tie-breaker against the restored closure note, the closure validator, the shared tests-root "
    "smoke route, and the helper-specific next_safe_step_note entries in the committed manifest "
    "rather than widening back into the older validator-first or replay-side closure stack.`"
)

EXPECTED_LANE_NOTE_LINES = (
    "- `zigux/tests/fixtures/phase1_helper_manifest.json` now records helper-local "
    "`next_safe_step_note` entries for `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, "
    "`tools/lib/rbtree.zig`, and `tools/lib/string.zig`; treat those helper-specific "
    "manifest notes plus the `PHASE1_*_NEXT_SAFE_STEP` lines below as the authoritative "
    "tie-breakers instead of reopening a helper family from older saved cues or missing "
    "shared-validator paths.`",
    "- `PHASE1_BITMAP_NEXT_SAFE_STEP=bitmap stays parked unless a fresh reread finds "
    "new direct-anchor drift or committed shared replay drift; do not reopen older "
    "closure-side or validator-route cue names by default`",
    "- `PHASE1_FIND_BIT_NEXT_SAFE_STEP=find_bit reopens only for direct-anchor drift "
    "inside same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, "
    "past-nbits, clump8, getValue8(), findLastBit(), underscore-alias or Linux-style alias "
    "coverage including the shipped andnot scan entry points, or tail-word skip anchors, or "
    "for committed tail-clamped replay drift; do not reopen older saved validator cues or "
    "neighboring helper families`",
    "- `PHASE1_RBTREE_NEXT_SAFE_STEP=rbtree reopens only to keep the already-landed "
    "cached_leftmost_return_serials shared replay aligned across the manifest, direct-owner "
    "note, and any shared parity gates, or for drift inside the still-helper-local cached-root "
    "insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and "
    "reseed anchors; do not batch a second widening into the same run`",
    "- `PHASE1_STRING_NEXT_SAFE_STEP=string reopens only for direct-anchor drift inside "
    "strscpy()/strscpyPad() copy-and-pad semantics, memparse, matched-prefix-length or suffix "
    "boundary, sysfs newline-aware equality or lookup order, matchString()/match_string() "
    "C-string list lookup, counted-search strnchr, embedded-NUL trim, or moving-earliest-dirty-byte "
    "memchrInv coverage, or for committed replaceChar or current string fixture drift; keep the "
    "helper-local sysfs review anchors aligned across the string review packet and this lane note "
    "unless dedicated shared sysfs fixture keys land; do not reopen missing closure-side validator "
    "names by default`",
)

EXPECTED_MANIFEST_DIRECT_ANCHOR_HELPERS = [
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
]

EXPECTED_NEXT_SAFE_STEP_NOTES = {
    "tools/lib/bitmap.zig": (
        "If this helper lane reopens, keep bitmap parked unless a fresh reread finds new "
        "direct-anchor drift inside the current helper-local packet or committed shared replay "
        "drift in the bitmap parity fields; current master still ships direct fill-tail clamp, "
        "copy-alias, truncation, cross-word scnprintf, empty-buffer, and allocator-reset anchors "
        "here, while zero-bit and Linux-style alias follow-through no longer live in the "
        "helper-local packet, and if the separate bitmap closure-validator anchor-sync repair is "
        "still outstanding, treat that as the only other bitmap follow-through."
    ),
    "tools/lib/find_bit.zig": (
        "If this helper lane reopens, keep find_bit parked unless a fresh reread finds "
        "direct-anchor drift inside same-word start-mask, inclusive-boundary, zero-window, "
        "zero-sized short-circuit, past-nbits, clump8, getValue8(), findLastBit(), underscore-alias, "
        "Linux-style alias, or tail-word skip anchors, or committed tail-clamped replay drift; "
        "do not reopen older saved validator cues or neighboring helper families."
    ),
    "tools/lib/rbtree.zig": (
        "If this helper lane reopens, keep the already-landed shared-replay promotion for "
        "`cached_leftmost_return_serials` aligned across the committed fixture, shared replay, "
        "and direct cached-root anchors; until another committed cached-root field lands, "
        "insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, "
        "and reseed behavior stay owned by direct helper-local anchors."
    ),
    "tools/lib/string.zig": (
        "If this helper lane reopens, keep the helper-local sysfs review anchors aligned across "
        "the string review packet and this lane note unless dedicated shared sysfs fixture keys "
        "land; do not reopen missing closure-side validator names by default."
    ),
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json(root: Path, relative_path: Path) -> object:
    return json.loads(load_text(root, relative_path))


def require_exact_line(text: str, label: str, marker: str) -> list[str]:
    count = sum(1 for line in text.splitlines() if line.strip() == marker)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def nested_value(data: object, path: tuple[str, ...]) -> object:
    current = data
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    closure_text = load_text(root, PHASE1_CLOSURE_REL)
    failures.extend(
        require_exact_line(
            closure_text,
            f"{PHASE1_CLOSURE_REL.as_posix()}:{EXPECTED_CLOSURE_LINE}",
            EXPECTED_CLOSURE_LINE,
        )
    )

    lane_note_text = load_text(root, LANE_NOTE_REL)
    for marker in EXPECTED_LANE_NOTE_LINES:
        failures.extend(
            require_exact_line(
                lane_note_text,
                f"{LANE_NOTE_REL.as_posix()}:{marker}",
                marker,
            )
        )

    manifest = load_json(root, MANIFEST_REL)
    if not isinstance(manifest, dict):
        return [f"{MANIFEST_REL.as_posix()}:expected=dict:actual={type(manifest).__name__}"]

    direct_anchor_helpers = nested_value(
        manifest, ("lane_sequencing", "direct_anchor_followup_helpers")
    )
    if direct_anchor_helpers != EXPECTED_MANIFEST_DIRECT_ANCHOR_HELPERS:
        failures.append(
            f"{MANIFEST_REL.as_posix()}:lane_sequencing.direct_anchor_followup_helpers:"
            f"expected={EXPECTED_MANIFEST_DIRECT_ANCHOR_HELPERS!r}:actual={direct_anchor_helpers!r}"
        )

    for helper, expected_note in EXPECTED_NEXT_SAFE_STEP_NOTES.items():
        actual_note = nested_value(manifest, ("review_anchors", helper, "next_safe_step_note"))
        if actual_note != expected_note:
            failures.append(
                f"{MANIFEST_REL.as_posix()}:review_anchors.{helper}.next_safe_step_note:"
                f"expected={expected_note!r}:actual={actual_note!r}"
            )

    return failures


def write_text(root: Path, relative_path: Path, text: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def sample_manifest() -> str:
    payload = {
        "lane_sequencing": {
            "direct_anchor_followup_helpers": EXPECTED_MANIFEST_DIRECT_ANCHOR_HELPERS,
        },
        "review_anchors": {
            helper: {"next_safe_step_note": note}
            for helper, note in EXPECTED_NEXT_SAFE_STEP_NOTES.items()
        },
    }
    return json.dumps(payload, indent=2) + "\n"


def build_sample_repo(root: Path) -> None:
    write_text(root, PHASE1_CLOSURE_REL, "# sample\n\n" + EXPECTED_CLOSURE_LINE + "\n")
    write_text(root, LANE_NOTE_REL, "# sample\n\n" + "\n".join(EXPECTED_LANE_NOTE_LINES) + "\n")
    write_text(root, MANIFEST_REL, sample_manifest())


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise ValueError(f"missing expected marker: {old}")
    return text.replace(old, new, 1)


def run_self_test() -> int:
    cases = [
        ("baseline", None, True),
        (
            "missing_closure_line",
            lambda root: write_text(
                root,
                PHASE1_CLOSURE_REL,
                replace_once(load_text(root, PHASE1_CLOSURE_REL), EXPECTED_CLOSURE_LINE + "\n", ""),
            ),
            False,
        ),
        (
            "duplicate_lane_note_line",
            lambda root: write_text(
                root,
                LANE_NOTE_REL,
                replace_once(
                    load_text(root, LANE_NOTE_REL),
                    EXPECTED_LANE_NOTE_LINES[1],
                    EXPECTED_LANE_NOTE_LINES[1] + "\n" + EXPECTED_LANE_NOTE_LINES[1],
                ),
            ),
            False,
        ),
        (
            "missing_manifest_helper",
            lambda root: write_text(
                root,
                MANIFEST_REL,
                json.dumps(
                    {
                        **json.loads(load_text(root, MANIFEST_REL)),
                        "lane_sequencing": {
                            "direct_anchor_followup_helpers": EXPECTED_MANIFEST_DIRECT_ANCHOR_HELPERS[:-1]
                        },
                    },
                    indent=2,
                )
                + "\n",
            ),
            False,
        ),
        (
            "wrong_bitmap_note",
            lambda root: write_text(
                root,
                MANIFEST_REL,
                json.dumps(
                    {
                        **json.loads(load_text(root, MANIFEST_REL)),
                        "review_anchors": {
                            **json.loads(load_text(root, MANIFEST_REL))["review_anchors"],
                            "tools/lib/bitmap.zig": {
                                "next_safe_step_note": "bitmap drift note changed"
                            },
                        },
                    },
                    indent=2,
                )
                + "\n",
            ),
            False,
        ),
        (
            "missing_required_file",
            lambda root: (root / MANIFEST_REL).unlink(),
            False,
        ),
    ]

    for name, mutate, expect_ok in cases:
        with tempfile.TemporaryDirectory(prefix=f"phase1-next-safe-step-{name}-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            if mutate is not None:
                mutate(root)
            failures = collect_failures(root)
            ok = not failures
            if ok != expect_ok:
                print(f"phase1-next-safe-step-self-test:{name}:unexpected={failures}")
                return 1

    print("PHASE1_NEXT_SAFE_STEP_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE1_NEXT_SAFE_STEP_ALIGNMENT_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_NEXT_SAFE_STEP_ALIGNMENT=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_NEXT_SAFE_STEP_ALIGNMENT=pass")
    print(f"PHASE1_NEXT_SAFE_STEP_ALIGNMENT_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_NEXT_SAFE_STEP_ALIGNMENT_REQUIRED_MARKER_COUNT="
        f"{1 + len(EXPECTED_LANE_NOTE_LINES) + len(EXPECTED_NEXT_SAFE_STEP_NOTES)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
