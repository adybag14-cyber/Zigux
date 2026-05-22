#!/usr/bin/env python3
"""Guard the remaining Phase 1 closure-note helper-family tie-break prose."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

CLOSURE_NOTE_REL = Path("Documentation/zigux/phase1-closure.md")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")

RBTREE_KEY = "tools/lib/rbtree.zig"
STRING_KEY = "tools/lib/string.zig"

EXPECTED_RBTREE_CLOSURE_NOTE = (
    "A second current helper-family tie-breaker inside that packet is the `rbtree` "
    "direct-anchor route: keep `tools/lib/rbtree.zig` parked unless a fresh reread "
    "finds drift in the helper-local ordered Linux-style alias proof, the dedicated "
    "manifest-backed `low_level_alias_anchor`, the cached-root insert-miss, "
    "leftmost-sync, cached-root alias, singleton-erase, replacement, detach, or "
    "reseed anchors, or drift in the already-committed duplicate-search replay fields "
    "or exact `cached_leftmost_return_serials` witness. Current `master` still keeps "
    "that low-level Linux-style alias proof named explicitly in "
    "`zigux/tests/fixtures/phase1_helper_manifest.json`, while the shared host-tools "
    "smoke route and committed Phase 1 fixture already recheck duplicate-range "
    "iteration plus the exact cached-leftmost-return packet, so leave rbtree parked "
    "unless one of those helper-local anchors or committed replay fields drifts and "
    "do not batch a second cached-root widening into the same reopen step."
)

EXPECTED_STRING_CLOSURE_NOTE = (
    "A third current helper-family tie-breaker inside that packet is the `string` "
    "direct-anchor route: keep `tools/lib/string.zig` parked unless a fresh reread "
    "finds drift in the helper-local `strscpy()` or `strscpyPad()` copy-and-pad "
    "anchors, memparse safety anchors, matched-prefix-length or suffix-boundary "
    "anchors, sysfs newline-aware equality or lookup-order anchors through "
    "`sysfsStreq()`, `sysfs_streq()`, `sysfsMatchString()`, and `sysfs_match_string()`, "
    "C-string list lookup anchors through `matchString()` and `match_string()`, "
    "lexical-compare and search-or-length boundary anchors through `strcmp()`, "
    "`strlen()`, `strnlen()`, `strchr()`, `strrchr()`, `strchrNul()`, and "
    "`strchrnul()`, counted-search anchors through `strpbrk()`, `strcspn()`, "
    "`strnchr()`, `strnchrNul()` or `strnchrnul()`, and `strspn()`, embedded-NUL "
    "trim preservation, or moving-earliest-dirty-byte `memchrInv()` coverage, or "
    "unless committed `replaceChar` parity bytes or current string fixture keys drift; "
    "do not reopen missing closure-side validator names by default. Current `master` "
    "still keeps that broader string review packet explicit in `tools/lib/string.zig`, "
    "the committed manifest, `scripts/zigux/check-phase1-string-review-packet.py`, and "
    "`Documentation/zigux/phase1-host-helper-lane-sequencing.md`, so leave string "
    "parked unless those direct string review surfaces drift, committed `replaceChar` "
    "parity bytes drift, or dedicated shared string fixture keys land."
)

EXPECTED_STRING_SYSFS_MARKER = (
    "`PHASE1_STRING_SYSFS_REVIEW=helper-local string sysfs newline-aware equality "
    "and lookup-order anchors stay explicit through the direct string tests and the "
    "Phase 1 helper manifest because the shared Phase 1 replay still carries no "
    "dedicated sysfs fixture keys`"
)

EXPECTED_RBTREE_LOW_LEVEL_ALIAS = (
    'test "rbtree low-level Linux-style aliases mirror node-state helpers"'
)
EXPECTED_RBTREE_CACHED_ROOT_ALIAS = (
    'test "rbtree cached-root Linux-style aliases mirror the primary helpers"'
)
EXPECTED_RBTREE_NEXT_SAFE_STEP = (
    "If this helper lane reopens, keep the already-landed shared-replay promotion "
    "for `cached_leftmost_return_serials` aligned across the committed fixture, "
    "shared replay, and direct cached-root anchors; the ordered Linux-style alias "
    "proof, dedicated `low_level_alias_anchor`, and the remaining cached-root "
    "insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, "
    "detach, and reseed behavior stay owned by direct helper-local anchors until "
    "another committed cached-root field lands."
)

EXPECTED_STRING_SYSFS_REVIEW_SUMMARY = (
    "helper-local string sysfs newline-aware equality and lookup-order anchors stay "
    "explicit through the direct string tests because the shared Phase 1 replay still "
    "carries no dedicated sysfs fixture keys, so sysfsStreq and sysfs_streq plus "
    "sysfsMatchString and sysfs_match_string remain review-visible at the helper "
    "surface"
)
EXPECTED_STRING_NEXT_SAFE_STEP = (
    "If this helper lane reopens, keep the helper-local sysfs review anchors aligned "
    "across the string review packet and this lane note unless dedicated shared "
    "sysfs fixture keys land; do not reopen missing closure-side validator names by "
    "default."
)
EXPECTED_STRING_COUNTED_SEARCH_REVIEW_SUMMARY = (
    "the direct counted-search and C-string search-length follow-up stays explicit "
    "because the shared Phase 1 replay still does not carry dedicated counted-search "
    "or search-length fixture keys, so strchr() or strrchr() full-length C-string "
    "searches, strpbrk() first-accepted-byte scanning, strspn() accepted-prefix "
    "scanning, strcspn() rejected-byte scanning, strnchr() count-limited scanning, "
    "strnlen() count-clamped length, and strnchrNul() or strnchrnul() match-or-NUL "
    "boundary behavior remain owned by the helper-local anchors"
)
EXPECTED_STRING_COUNTED_SEARCH_REVIEW_ANCHORS = [
    'test "strchr mirrors full-length C-string searches"',
    'test "strrchr finds the last in-range match with C-string semantics"',
    'test "strpbrk finds the first accepted byte with C-string semantics"',
    'test "strspn counts the accepted prefix with C-string semantics"',
    'test "strcspn counts until the first rejected byte with C-string semantics"',
    'test "strnchr honors count and C-string boundaries"',
    'test "strnlen honors count and C-string boundaries"',
    'test "strnchrNul returns the first match, NUL, or count boundary"',
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


def mutate_manifest(root: Path, mutate) -> None:
    manifest_path = root / MANIFEST_REL
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    mutate(manifest)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in (CLOSURE_NOTE_REL, MANIFEST_REL):
        if not (root / relative_path).is_file():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    closure_text = load_text(root, CLOSURE_NOTE_REL)
    for label, needle in (
        ("rbtree_tiebreak_note", EXPECTED_RBTREE_CLOSURE_NOTE),
        ("string_tiebreak_note", EXPECTED_STRING_CLOSURE_NOTE),
        ("string_sysfs_marker", EXPECTED_STRING_SYSFS_MARKER),
    ):
        failures.extend(
            require_exact_occurrence(
                closure_text,
                f"{CLOSURE_NOTE_REL.as_posix()}:{label}",
                needle,
            )
        )

    manifest = json.loads(load_text(root, MANIFEST_REL))
    if not isinstance(manifest, dict):
        return [f"{MANIFEST_REL.as_posix()}:expected=dict:actual={type(manifest).__name__}"]

    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        return [
            f"{MANIFEST_REL.as_posix()}:review_anchors:expected=dict:actual={type(review_anchors).__name__}"
        ]

    rbtree_review = review_anchors.get(RBTREE_KEY)
    if not isinstance(rbtree_review, dict):
        return [
            f"{MANIFEST_REL.as_posix()}:review_anchors.{RBTREE_KEY}:expected=dict:actual={type(rbtree_review).__name__}"
        ]

    string_review = review_anchors.get(STRING_KEY)
    if not isinstance(string_review, dict):
        return [
            f"{MANIFEST_REL.as_posix()}:review_anchors.{STRING_KEY}:expected=dict:actual={type(string_review).__name__}"
        ]

    failures.extend(
        require_exact_value(
            f"{MANIFEST_REL.as_posix()}:review_anchors.{RBTREE_KEY}:low_level_alias_anchor",
            rbtree_review.get("low_level_alias_anchor"),
            EXPECTED_RBTREE_LOW_LEVEL_ALIAS,
        )
    )
    failures.extend(
        require_exact_value(
            f"{MANIFEST_REL.as_posix()}:review_anchors.{RBTREE_KEY}:cached_root_alias_anchor",
            rbtree_review.get("cached_root_alias_anchor"),
            EXPECTED_RBTREE_CACHED_ROOT_ALIAS,
        )
    )
    failures.extend(
        require_exact_value(
            f"{MANIFEST_REL.as_posix()}:review_anchors.{RBTREE_KEY}:next_safe_step_note",
            rbtree_review.get("next_safe_step_note"),
            EXPECTED_RBTREE_NEXT_SAFE_STEP,
        )
    )
    failures.extend(
        require_exact_value(
            f"{MANIFEST_REL.as_posix()}:review_anchors.{STRING_KEY}:sysfs_review_summary",
            string_review.get("sysfs_review_summary"),
            EXPECTED_STRING_SYSFS_REVIEW_SUMMARY,
        )
    )
    failures.extend(
        require_exact_value(
            f"{MANIFEST_REL.as_posix()}:review_anchors.{STRING_KEY}:next_safe_step_note",
            string_review.get("next_safe_step_note"),
            EXPECTED_STRING_NEXT_SAFE_STEP,
        )
    )
    failures.extend(
        require_exact_value(
            f"{MANIFEST_REL.as_posix()}:review_anchors.{STRING_KEY}:counted_search_review_summary",
            string_review.get("strnchr_review_summary"),
            EXPECTED_STRING_COUNTED_SEARCH_REVIEW_SUMMARY,
        )
    )
    failures.extend(
        require_exact_value(
            f"{MANIFEST_REL.as_posix()}:review_anchors.{STRING_KEY}:counted_search_review_anchors",
            string_review.get("counted_search_review_anchors"),
            EXPECTED_STRING_COUNTED_SEARCH_REVIEW_ANCHORS,
        )
    )
    failures.extend(
        require_exact_value(
            f"{MANIFEST_REL.as_posix()}:review_anchors.{STRING_KEY}:strnchrnul_review_anchor",
            string_review.get("strnchrnul_review_anchor"),
            'test "strnchrNul returns the first match, NUL, or count boundary"',
        )
    )

    return failures


def make_fixture_tree(root: Path) -> None:
    write_text(
        root / CLOSURE_NOTE_REL,
        "\n".join(
            [
                "# Phase 1 Closure",
                "",
                EXPECTED_RBTREE_CLOSURE_NOTE,
                "",
                EXPECTED_STRING_CLOSURE_NOTE,
                "",
                f"- {EXPECTED_STRING_SYSFS_MARKER}",
                "",
            ]
        ),
    )

    write_text(
        root / MANIFEST_REL,
        json.dumps(
            {
                "review_anchors": {
                    RBTREE_KEY: {
                        "low_level_alias_anchor": EXPECTED_RBTREE_LOW_LEVEL_ALIAS,
                        "cached_root_alias_anchor": EXPECTED_RBTREE_CACHED_ROOT_ALIAS,
                        "next_safe_step_note": EXPECTED_RBTREE_NEXT_SAFE_STEP,
                    },
                    STRING_KEY: {
                        "sysfs_review_summary": EXPECTED_STRING_SYSFS_REVIEW_SUMMARY,
                        "next_safe_step_note": EXPECTED_STRING_NEXT_SAFE_STEP,
                        "strnchr_review_summary": EXPECTED_STRING_COUNTED_SEARCH_REVIEW_SUMMARY,
                        "counted_search_review_anchors": EXPECTED_STRING_COUNTED_SEARCH_REVIEW_ANCHORS,
                        "strnchrnul_review_anchor": 'test "strnchrNul returns the first match, NUL, or count boundary"',
                    },
                }
            },
            indent=2,
        )
        + "\n",
    )


def write_sample_root(root: Path) -> None:
    make_fixture_tree(root)


def run_self_test() -> int:
    cases = [
        ("baseline", None),
        (
            "missing_rbtree_closure_note",
            lambda root: write_text(
                root / CLOSURE_NOTE_REL,
                load_text(root, CLOSURE_NOTE_REL).replace(EXPECTED_RBTREE_CLOSURE_NOTE + "\n\n", "", 1),
            ),
        ),
        (
            "stale_rbtree_closure_note",
            lambda root: write_text(
                root / CLOSURE_NOTE_REL,
                load_text(root, CLOSURE_NOTE_REL).replace(
                    "manifest-backed `low_level_alias_anchor`",
                    "older helper-local alias cue",
                    1,
                ),
            ),
        ),
        (
            "missing_string_sysfs_marker",
            lambda root: write_text(
                root / CLOSURE_NOTE_REL,
                load_text(root, CLOSURE_NOTE_REL).replace(f"- {EXPECTED_STRING_SYSFS_MARKER}\n", "", 1),
            ),
        ),
        (
            "stale_string_closure_note",
            lambda root: write_text(
                root / CLOSURE_NOTE_REL,
                load_text(root, CLOSURE_NOTE_REL).replace(
                    "`strspn()`",
                    "`strspnOld()`",
                    1,
                ),
            ),
        ),
        (
            "bad_rbtree_manifest_alias_anchor",
            lambda root: mutate_manifest(
                root,
                lambda manifest: manifest["review_anchors"][RBTREE_KEY].__setitem__(
                    "low_level_alias_anchor",
                    'test "rbtree low-level aliases mirror helper state"',
                ),
            ),
        ),
        (
            "bad_rbtree_manifest_next_step",
            lambda root: mutate_manifest(
                root,
                lambda manifest: manifest["review_anchors"][RBTREE_KEY].__setitem__(
                    "next_safe_step_note",
                    "drifted rbtree note",
                ),
            ),
        ),
        (
            "bad_string_manifest_sysfs_summary",
            lambda root: mutate_manifest(
                root,
                lambda manifest: manifest["review_anchors"][STRING_KEY].__setitem__(
                    "sysfs_review_summary",
                    "older string sysfs summary",
                ),
            ),
        ),
        (
            "bad_string_manifest_next_step",
            lambda root: mutate_manifest(
                root,
                lambda manifest: manifest["review_anchors"][STRING_KEY].__setitem__(
                    "next_safe_step_note",
                    "drifted string note",
                ),
            ),
        ),
        (
            "bad_string_manifest_counted_search_summary",
            lambda root: mutate_manifest(
                root,
                lambda manifest: manifest["review_anchors"][STRING_KEY].__setitem__(
                    "strnchr_review_summary",
                    "drifted counted-search summary",
                ),
            ),
        ),
        (
            "bad_string_manifest_counted_search_anchor_list",
            lambda root: mutate_manifest(
                root,
                lambda manifest: manifest["review_anchors"][STRING_KEY].__setitem__(
                    "counted_search_review_anchors",
                    EXPECTED_STRING_COUNTED_SEARCH_REVIEW_ANCHORS[:-1],
                ),
            ),
        ),
        (
            "bad_string_manifest_match_or_nul_anchor",
            lambda root: mutate_manifest(
                root,
                lambda manifest: manifest["review_anchors"][STRING_KEY].__setitem__(
                    "strnchrnul_review_anchor",
                    'test "strnchrNul drifts"',
                ),
            ),
        ),
    ]

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-closure-helper-family-tiebreaks-") as tmp:
            root = Path(tmp)
            make_fixture_tree(root)
            if mutate is not None:
                mutate(root)
            failures = collect_failures(root)
            if name == "baseline":
                if failures:
                    print(f"phase1-closure-helper-family-tiebreaks:{name}:unexpected={failures}")
                    return 1
            elif not failures:
                print(f"phase1-closure-helper-family-tiebreaks:{name}:expected_failure")
                return 1

    print("PHASE1_CLOSURE_HELPER_FAMILY_TIEBREAKS_SELF_TEST=pass")
    print(f"PHASE1_CLOSURE_HELPER_FAMILY_TIEBREAKS_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run checker self-tests")
    parser.add_argument(
        "--write-sample-root",
        help="write a sample root that matches the current helper-family tie-break packet",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        write_sample_root(Path(args.write_sample_root).resolve())
        return 0

    failures = collect_failures(repo_root(args.root))
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_CLOSURE_HELPER_FAMILY_TIEBREAKS=pass")
    print("PHASE1_CLOSURE_HELPER_FAMILY_TIEBREAKS_PACKET=rbtree_and_string")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
