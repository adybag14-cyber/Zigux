#!/usr/bin/env python3
"""Guard the Phase 1 shared-reminder route split and helper-family tie-breakers."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
DOCS_ROOT_REL = Path("Documentation/zigux/README.md")
REVIEW_CHECKLIST_REL = Path("Documentation/zigux/review-checklist.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
PHASE1_CLOSURE_VALIDATOR_REL = Path("scripts/zigux/validate-phase1-closure.py")
SHARED_REMINDER_CHECKER_REL = Path("scripts/zigux/check-phase1-shared-reminder-packet.py")
ROUTE_SUMMARY_CHECKER_REL = Path("scripts/zigux/check-phase1-route-summary-counts.py")
DIRECT_OWNER_CHECKER_REL = Path("scripts/zigux/check-phase1-direct-owner-markers.py")
BENCH_CHECKER_REL = Path("scripts/zigux/check-phase1-bench.py")
TESTS_README_REL = Path("zigux/tests/README.md")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
MAKEFILE_REL = Path("zigux/Makefile")

REQUIRED_FILES = (
    LANE_NOTE_REL,
    DOCS_ROOT_REL,
    REVIEW_CHECKLIST_REL,
    SCRIPTS_README_REL,
    PHASE1_CLOSURE_REL,
    PHASE1_CLOSURE_VALIDATOR_REL,
    SHARED_REMINDER_CHECKER_REL,
    ROUTE_SUMMARY_CHECKER_REL,
    DIRECT_OWNER_CHECKER_REL,
    BENCH_CHECKER_REL,
    TESTS_README_REL,
    MANIFEST_REL,
    MAKEFILE_REL,
)

EXPECTED_SHARED_REPLAY_PARKED_HELPERS = [
    "tools/lib/argv_split.zig",
    "tools/lib/cmdline.zig",
    "tools/lib/ctype.zig",
    "tools/lib/hweight.zig",
    "tools/lib/list_sort.zig",
    "tools/lib/slab.zig",
    "tools/lib/str_error_r.zig",
    "tools/lib/vsprintf.zig",
    "tools/lib/zalloc.zig",
]

EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS = [
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
]

EXPECTED_ROUTE_SPLIT_LINES = {
    "shared_reminder_gaps": (
        "the shared reminder packet now keeps scripts/zigux/check-phase1-bench.py explicit "
        "across Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, "
        "zigux/tests/README.md, and scripts/zigux/README.md, while the older installer-backed, "
        "validator-first, bench-route, and replay names stay historical packet members until they "
        "reread cleanly on current master"
    ),
    "shared_reminder_active_packet": (
        "Documentation/zigux/README.md,Documentation/zigux/phase1-closure.md,"
        "Documentation/zigux/review-checklist.md,zigux/tests/README.md,scripts/zigux/README.md,"
        "scripts/zigux/validate-phase1-closure.py,scripts/zigux/check-phase1-string-review-packet.py,"
        "scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-bench.py,"
        "scripts/zigux/check-phase1-shared-reminder-packet.py"
    ),
    "shared_reminder_route_split": (
        "Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, "
        "zigux/tests/README.md, and scripts/zigux/README.md now all carry the shipped "
        "bench-checker wording, while Documentation/zigux/phase1-closure.md plus "
        "scripts/zigux/validate-phase1-closure.py keep the restored closure-side packet explicit "
        "and the broader installer-backed, validator-first, bench-route, and replay names remain "
        "historical packet members until direct current-master rereads restore them"
    ),
    "shared_reminder_next_step": (
        "leave the shared bench-checker wording and shared-reminder checker packet parked unless "
        "a fresh reread finds drift across Documentation/zigux/README.md, "
        "Documentation/zigux/review-checklist.md, zigux/tests/README.md, scripts/zigux/README.md, "
        "Documentation/zigux/phase1-closure.md, scripts/zigux/validate-phase1-closure.py, "
        "scripts/zigux/check-phase1-bench.py, or scripts/zigux/check-phase1-shared-reminder-packet.py; "
        "otherwise prefer the smaller helper-specific next-safe-step markers below before reopening "
        "any shared reminder surface"
    ),
}

EXPECTED_NEXT_SAFE_STEP_LINES = {
    "bitmap": (
        "bitmap stays parked unless a fresh reread finds new direct-anchor drift or committed "
        "shared replay drift; do not reopen older closure-side or validator-route cue names by default"
    ),
    "find_bit": (
        "find_bit reopens only for direct-anchor drift inside same-word start-mask, "
        "inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, "
        "getValue8(), findLastBit(), underscore-alias or Linux-style alias coverage including "
        "the shipped andnot scan entry points, or tail-word skip anchors, or for committed "
        "tail-clamped or tail-inclusive-boundary replay drift; do not reopen older saved "
        "validator cues or neighboring helper families"
    ),
    "rbtree": (
        "rbtree reopens only to keep the already-landed cached_leftmost_return_serials shared "
        "replay aligned across the manifest, direct-owner note, and any shared parity gates, or "
        "for drift inside the still-helper-local ordered Linux-style alias proof, dedicated "
        "low_level_alias_anchor, cached-root insert-miss, leftmost-sync, cached-root alias, "
        "singleton-erase, replacement, detach, and reseed anchors; do not batch a second "
        "widening into the same run"
    ),
    "string": (
        "string reopens only for direct-anchor drift inside strscpy()/strscpyPad() copy-and-pad "
        "semantics, memparse, matched-prefix-length or suffix boundary, sysfs newline-aware "
        "equality or lookup order, matchString()/match_string() C-string list lookup, "
        "counted-search and search-length anchors through strpbrk(), strspn(), strcspn(), "
        "strnchr(), strnchrNul() or strnchrnul(), strchr(), strrchr(), strlen(), and strnlen(), "
        "embedded-NUL trim, or moving-earliest-dirty-byte memchrInv coverage, or for committed "
        "replaceChar or current string fixture drift; keep the helper-local sysfs review anchors "
        "aligned across the string review packet and this lane note unless dedicated shared sysfs "
        "fixture keys land; do not reopen missing closure-side validator names by default"
    ),
}

EXPECTED_DOCS_MARKERS = (
    "keep the live owner map, the restored closure note and closure validator, the adjacent "
    "route-summary guard, the parked shared-replay-versus-direct-anchor split, the shipped "
    "bench checker, and the current Phase 1 reminder packet explicit from the docs root without "
    "rebuilding the broader host-tools closure stack from older missing validator and replay surfaces.",
    "keep the helper-family split explicit here too: the nine shared-replay parked helpers reopen "
    "only for packet drift, while bitmap, find_bit, rbtree, and string keep the only bounded "
    "direct-anchor follow-up anchors on current master.",
)

EXPECTED_REVIEW_MARKERS = (
    "keep `scripts/zigux/check-phase1-route-summary-counts.py`, `make -C zigux phase1-route-summary`, "
    "and `zigux/Makefile` explicit as the adjacent Phase 1 route-summary evidence for the returned "
    "Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14 route families, while "
    "the older validator-first, parity, bench-route, and replay names stay framed as historical "
    "packet members until current `master` materializes them again?",
)

EXPECTED_SCRIPTS_MARKERS = (
    "`scripts/zigux/check-phase1-route-summary-counts.py`, `make -C zigux phase1-route-summary`, "
    "and `.github/workflows/zigux-bootstrap.yml` keep the adjacent Phase 1 route-summary guard "
    "explicit beside the narrower reminder packet, so scripts-root follow-through can verify the "
    "returned non-Phase-1 Makefile route inventory without promoting the older Phase 1 wrappers "
    "back into shipped proof",
    "the current direct-anchor tie-breakers stay helper-local: bitmap, find_bit, rbtree, and "
    "string reopen only inside their existing helper-local anchors or already-committed shared "
    "fixture keys, while the other nine closed helpers stay parked unless the shared replay or "
    "reminder packet drifts",
)

FORBIDDEN_FRAGMENTS = (
    "Phase 1 helper follow-up defaults back to the older validator-first closure stack",
    "promote the older validator-first closure stack back into the default shared reminder route",
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def require_exact_occurrence(text: str, label: str, needle: str) -> list[str]:
    count = text.count(needle)
    return [] if count == 1 else [f"{label}:expected_once:actual_count={count}"]


def require_absent(text: str, label: str, needle: str) -> list[str]:
    count = text.count(needle)
    return [] if count == 0 else [f"{label}:expected_absent:actual_count={count}"]


def require_exact_value(label: str, actual: object, expected: object) -> list[str]:
    return [] if actual == expected else [f"{label}:expected={expected!r}:actual={actual!r}"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).is_file():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    lane_note = read_text(root, LANE_NOTE_REL)
    for label, marker in EXPECTED_ROUTE_SPLIT_LINES.items():
        failures.extend(
            require_exact_occurrence(
                lane_note,
                f"{LANE_NOTE_REL.as_posix()}:{label}",
                marker,
            )
        )
    for label, marker in EXPECTED_NEXT_SAFE_STEP_LINES.items():
        failures.extend(
            require_exact_occurrence(
                lane_note,
                f"{LANE_NOTE_REL.as_posix()}:next_safe_step:{label}",
                marker,
            )
        )

    docs_root = read_text(root, DOCS_ROOT_REL)
    for marker in EXPECTED_DOCS_MARKERS:
        failures.extend(require_exact_occurrence(docs_root, DOCS_ROOT_REL.as_posix(), marker))

    review = read_text(root, REVIEW_CHECKLIST_REL)
    for marker in EXPECTED_REVIEW_MARKERS:
        failures.extend(require_exact_occurrence(review, REVIEW_CHECKLIST_REL.as_posix(), marker))

    scripts_readme = read_text(root, SCRIPTS_README_REL)
    for marker in EXPECTED_SCRIPTS_MARKERS:
        failures.extend(
            require_exact_occurrence(scripts_readme, SCRIPTS_README_REL.as_posix(), marker)
        )

    for relative_path in (
        LANE_NOTE_REL,
        DOCS_ROOT_REL,
        REVIEW_CHECKLIST_REL,
        SCRIPTS_README_REL,
    ):
        text = read_text(root, relative_path)
        for fragment in FORBIDDEN_FRAGMENTS:
            failures.extend(require_absent(text, relative_path.as_posix(), fragment))

    manifest = json.loads(read_text(root, MANIFEST_REL))
    lane_sequencing = manifest.get("lane_sequencing", {})
    failures.extend(
        require_exact_value(
            f"{MANIFEST_REL.as_posix()}:lane_sequencing.shared_replay_parked_helpers",
            lane_sequencing.get("shared_replay_parked_helpers"),
            EXPECTED_SHARED_REPLAY_PARKED_HELPERS,
        )
    )
    failures.extend(
        require_exact_value(
            f"{MANIFEST_REL.as_posix()}:lane_sequencing.direct_anchor_followup_helpers",
            lane_sequencing.get("direct_anchor_followup_helpers"),
            EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS,
        )
    )

    review_anchors = manifest.get("review_anchors", {})
    helper_paths = {
        "bitmap": "tools/lib/bitmap.zig",
        "find_bit": "tools/lib/find_bit.zig",
        "rbtree": "tools/lib/rbtree.zig",
        "string": "tools/lib/string.zig",
    }
    for key, helper_path in helper_paths.items():
        helper_note = review_anchors.get(helper_path, {})
        failures.extend(
            require_exact_value(
                f"{MANIFEST_REL.as_posix()}:review_anchors.{helper_path}.next_safe_step_note",
                helper_note.get("next_safe_step_note"),
                "If this helper lane reopens, keep "
                + (
                    "bitmap parked unless a fresh reread finds new direct-anchor drift inside the current helper-local packet or committed shared replay drift in the bitmap parity fields; current master still ships direct fill-tail clamp, copy-alias, truncation, cross-word scnprintf, exact-word-boundary equality fast-path masking, caller-window xor and or clamp, weighted tail-count clamp, empty-buffer, allocator-reset, zero-bit logical short-circuit, and Linux-style alias mirror anchors here; do not reopen older closure-side or validator-route cue names by default."
                    if key == "bitmap"
                    else "find_bit parked unless a fresh reread finds direct-anchor drift inside same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, getValue8(), findLastBit(), underscore-alias, Linux-style alias coverage including the shipped andnot scan entry points, or tail-word skip anchors, or committed tail-clamped or tail-inclusive-boundary replay drift; do not reopen older saved validator cues or neighboring helper families."
                    if key == "find_bit"
                    else "the already-landed shared-replay promotion for `cached_leftmost_return_serials` aligned across the committed fixture, shared replay, and direct cached-root anchors; the ordered Linux-style alias proof, dedicated `low_level_alias_anchor`, and the remaining cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed behavior stay owned by direct helper-local anchors until another committed cached-root field lands."
                    if key == "rbtree"
                    else "the helper-local sysfs review anchors aligned across the string review packet and this lane note unless dedicated shared sysfs fixture keys land; do not reopen missing closure-side validator names by default."
                ),
            )
        )

    return failures


def build_sample_repo(root: Path) -> None:
    marker_join = "\n".join

    lane_note_lines = [
        f"- `PHASE1_SHARED_REPLAY_PARKED_HELPERS={','.join(EXPECTED_SHARED_REPLAY_PARKED_HELPERS)}`",
        f"- `PHASE1_DIRECT_ANCHOR_FOLLOWUP_HELPERS={','.join(EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS)}`",
        f"- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_GAPS={EXPECTED_ROUTE_SPLIT_LINES['shared_reminder_gaps']}`",
        f"- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_ACTIVE_PACKET={EXPECTED_ROUTE_SPLIT_LINES['shared_reminder_active_packet']}`",
        f"- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_ROUTE_SPLIT={EXPECTED_ROUTE_SPLIT_LINES['shared_reminder_route_split']}`",
        f"- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_NEXT_STEP={EXPECTED_ROUTE_SPLIT_LINES['shared_reminder_next_step']}`",
        f"- `PHASE1_BITMAP_NEXT_SAFE_STEP={EXPECTED_NEXT_SAFE_STEP_LINES['bitmap']}`",
        f"- `PHASE1_FIND_BIT_NEXT_SAFE_STEP={EXPECTED_NEXT_SAFE_STEP_LINES['find_bit']}`",
        f"- `PHASE1_RBTREE_NEXT_SAFE_STEP={EXPECTED_NEXT_SAFE_STEP_LINES['rbtree']}`",
        f"- `PHASE1_STRING_NEXT_SAFE_STEP={EXPECTED_NEXT_SAFE_STEP_LINES['string']}`",
    ]
    write_text(root / LANE_NOTE_REL, marker_join(lane_note_lines) + "\n")
    write_text(root / DOCS_ROOT_REL, marker_join(EXPECTED_DOCS_MARKERS) + "\n")
    write_text(root / REVIEW_CHECKLIST_REL, marker_join(EXPECTED_REVIEW_MARKERS) + "\n")
    write_text(root / SCRIPTS_README_REL, marker_join(EXPECTED_SCRIPTS_MARKERS) + "\n")

    for rel in (
        PHASE1_CLOSURE_REL,
        PHASE1_CLOSURE_VALIDATOR_REL,
        SHARED_REMINDER_CHECKER_REL,
        ROUTE_SUMMARY_CHECKER_REL,
        DIRECT_OWNER_CHECKER_REL,
        BENCH_CHECKER_REL,
        TESTS_README_REL,
        MAKEFILE_REL,
    ):
        write_text(root / rel, f"fixture for {rel.as_posix()}\n")

    manifest = {
        "lane_sequencing": {
            "shared_replay_parked_helpers": EXPECTED_SHARED_REPLAY_PARKED_HELPERS,
            "direct_anchor_followup_helpers": EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS,
        },
        "review_anchors": {
            "tools/lib/bitmap.zig": {
                "next_safe_step_note": "If this helper lane reopens, keep bitmap parked unless a fresh reread finds new direct-anchor drift inside the current helper-local packet or committed shared replay drift in the bitmap parity fields; current master still ships direct fill-tail clamp, copy-alias, truncation, cross-word scnprintf, exact-word-boundary equality fast-path masking, caller-window xor and or clamp, weighted tail-count clamp, empty-buffer, allocator-reset, zero-bit logical short-circuit, and Linux-style alias mirror anchors here; do not reopen older closure-side or validator-route cue names by default.",
            },
            "tools/lib/find_bit.zig": {
                "next_safe_step_note": "If this helper lane reopens, keep find_bit parked unless a fresh reread finds direct-anchor drift inside same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, getValue8(), findLastBit(), underscore-alias, Linux-style alias coverage including the shipped andnot scan entry points, or tail-word skip anchors, or committed tail-clamped or tail-inclusive-boundary replay drift; do not reopen older saved validator cues or neighboring helper families.",
            },
            "tools/lib/rbtree.zig": {
                "next_safe_step_note": "If this helper lane reopens, keep the already-landed shared-replay promotion for `cached_leftmost_return_serials` aligned across the committed fixture, shared replay, and direct cached-root anchors; the ordered Linux-style alias proof, dedicated `low_level_alias_anchor`, and the remaining cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed behavior stay owned by direct helper-local anchors until another committed cached-root field lands.",
            },
            "tools/lib/string.zig": {
                "next_safe_step_note": "If this helper lane reopens, keep the helper-local sysfs review anchors aligned across the string review packet and this lane note unless dedicated shared sysfs fixture keys land; do not reopen missing closure-side validator names by default.",
            },
        },
    }
    write_text(root / MANIFEST_REL, json.dumps(manifest, indent=2) + "\n")


def mutate_remove(root: Path, rel: Path, marker: str) -> None:
    text = read_text(root, rel)
    write_text(root / rel, text.replace(marker + "\n", "", 1).replace(marker, "", 1))


def mutate_duplicate(root: Path, rel: Path, marker: str) -> None:
    text = read_text(root, rel)
    write_text(root / rel, text.replace(marker, marker + "\n" + marker, 1))


def mutate_manifest_note(root: Path, helper_path: str) -> None:
    manifest_path = root / MANIFEST_REL
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["review_anchors"][helper_path]["next_safe_step_note"] = "drifted helper note"
    write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")


def write_sample_root(destination: Path) -> None:
    build_sample_repo(destination)


def run_self_test() -> int:
    cases: list[tuple[str, object | None]] = [
        ("baseline", None),
        ("missing_lane_note_line", ("remove", LANE_NOTE_REL, f"- `PHASE1_BITMAP_NEXT_SAFE_STEP={EXPECTED_NEXT_SAFE_STEP_LINES['bitmap']}`")),
        ("duplicate_docs_marker", ("duplicate", DOCS_ROOT_REL, EXPECTED_DOCS_MARKERS[0])),
        ("missing_review_marker", ("remove", REVIEW_CHECKLIST_REL, EXPECTED_REVIEW_MARKERS[0])),
        ("duplicate_scripts_marker", ("duplicate", SCRIPTS_README_REL, EXPECTED_SCRIPTS_MARKERS[1])),
        ("forbidden_lane_note_fragment", ("forbidden", LANE_NOTE_REL, FORBIDDEN_FRAGMENTS[0])),
        ("drift_bitmap_manifest_note", ("manifest", "tools/lib/bitmap.zig")),
        ("drift_find_bit_manifest_note", ("manifest", "tools/lib/find_bit.zig")),
        ("drift_rbtree_manifest_note", ("manifest", "tools/lib/rbtree.zig")),
        ("drift_string_manifest_note", ("manifest", "tools/lib/string.zig")),
    ]

    for name, mutation in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-route-split-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            if mutation is not None:
                kind = mutation[0]
                if kind == "remove":
                    _, rel, marker = mutation
                    mutate_remove(root, rel, marker)
                elif kind == "duplicate":
                    _, rel, marker = mutation
                    mutate_duplicate(root, rel, marker)
                elif kind == "forbidden":
                    _, rel, marker = mutation
                    text = read_text(root, rel)
                    write_text(root / rel, text + marker + "\n")
                elif kind == "manifest":
                    _, helper = mutation
                    mutate_manifest_note(root, helper)
            failures = collect_failures(root)
            if name == "baseline":
                if failures:
                    print(f"phase1-route-split:self-test:{name}:unexpected={failures}")
                    return 1
            elif not failures:
                print(f"phase1-route-split:self-test:{name}:expected_failure")
                return 1

    print("PHASE1_SHARED_REMINDER_ROUTE_SPLIT_SELF_TEST=pass")
    print(f"PHASE1_SHARED_REMINDER_ROUTE_SPLIT_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-tests")
    parser.add_argument(
        "--write-sample-root",
        help="write a synthetic current-like sample root for validation replay",
    )
    args = parser.parse_args()

    if args.write_sample_root:
        write_sample_root(Path(args.write_sample_root).resolve())
        return 0
    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_SHARED_REMINDER_ROUTE_SPLIT=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_SHARED_REMINDER_ROUTE_SPLIT=pass")
    print(f"PHASE1_SHARED_REMINDER_ROUTE_SPLIT_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_SHARED_REMINDER_ROUTE_SPLIT_REQUIRED_HELPER_COUNT="
        f"{len(EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
