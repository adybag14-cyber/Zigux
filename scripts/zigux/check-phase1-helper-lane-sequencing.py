#!/usr/bin/env python3
"""Guard the current Phase 1 helper-lane sequencing packet."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

LANE_NOTE = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
DOCS_ROOT = Path("Documentation/zigux/README.md")
PHASE1_CLOSURE = Path("Documentation/zigux/phase1-closure.md")
REVIEW_CHECKLIST = Path("Documentation/zigux/review-checklist.md")
SCRIPTS_ROOT = Path("scripts/zigux/README.md")
TESTS_ROOT = Path("zigux/tests/README.md")
MANIFEST = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
DIRECT_OWNER_CHECKER = Path("scripts/zigux/check-phase1-direct-owner-markers.py")
STRING_REVIEW_CHECKER = Path("scripts/zigux/check-phase1-string-review-packet.py")
SHARED_REMINDER_CHECKER = Path("scripts/zigux/check-phase1-shared-reminder-packet.py")
CLOSURE_VALIDATOR = Path("scripts/zigux/validate-phase1-closure.py")

REQUIRED_FILES = (
    LANE_NOTE,
    DOCS_ROOT,
    PHASE1_CLOSURE,
    REVIEW_CHECKLIST,
    SCRIPTS_ROOT,
    TESTS_ROOT,
    MANIFEST,
    DIRECT_OWNER_CHECKER,
    STRING_REVIEW_CHECKER,
    SHARED_REMINDER_CHECKER,
    CLOSURE_VALIDATOR,
)

EXPECTED_SHARED_HELPERS = [
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

EXPECTED_DIRECT_HELPERS = [
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
]

EXPECTED_RULE_SUMMARY = (
    "Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, "
    "while bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local "
    "follow-up anchors on current master."
)
EXPECTED_ANTI_OVERLAP_RULE = (
    "Do not reopen Phase 1 by batching helpers across those two sets in one lane; "
    "shared-replay parked helpers reopen only for packet drift, while direct-anchor helpers "
    "reopen only for their existing helper-local anchors or already-committed shared fixture keys."
)

REQUIRED_MARKERS = {
    LANE_NOTE: (
        "- `PHASE1_SHARED_REPLAY_PARKED_HELPERS=tools/lib/argv_split.zig,tools/lib/cmdline.zig,tools/lib/ctype.zig,tools/lib/hweight.zig,tools/lib/list_sort.zig,tools/lib/slab.zig,tools/lib/str_error_r.zig,tools/lib/vsprintf.zig,tools/lib/zalloc.zig`",
        "- `PHASE1_DIRECT_ANCHOR_FOLLOWUP_HELPERS=tools/lib/bitmap.zig,tools/lib/find_bit.zig,tools/lib/rbtree.zig,tools/lib/string.zig`",
        "- `PHASE1_LANE_RULE_SUMMARY=Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, while bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local follow-up anchors on current master.`",
        "- `PHASE1_LANE_ANTI_OVERLAP_RULE=Do not reopen Phase 1 by batching helpers across those two sets in one lane; shared-replay parked helpers reopen only for packet drift, while direct-anchor helpers reopen only for their existing helper-local anchors or already-committed shared fixture keys.`",
        "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_ACTIVE_PACKET=Documentation/zigux/README.md,Documentation/zigux/phase1-closure.md,Documentation/zigux/review-checklist.md,zigux/tests/README.md,scripts/zigux/README.md,scripts/zigux/validate-phase1-closure.py,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py`",
        "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_NEXT_STEP=leave the shared bench-checker wording and shared-reminder checker packet parked unless a fresh reread finds drift across Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, zigux/tests/README.md, scripts/zigux/README.md, Documentation/zigux/phase1-closure.md, scripts/zigux/validate-phase1-closure.py, scripts/zigux/check-phase1-bench.py, or scripts/zigux/check-phase1-shared-reminder-packet.py; otherwise prefer the smaller helper-specific next-safe-step markers below before reopening any shared reminder surface`",
        "- `PHASE1_BITMAP_NEXT_SAFE_STEP=bitmap stays parked unless a fresh reread finds new direct-anchor drift or committed shared replay drift; do not reopen older closure-side or validator-route cue names by default`",
        "- `PHASE1_FIND_BIT_NEXT_SAFE_STEP=find_bit reopens only for direct-anchor drift inside same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, getValue8(), findLastBit(), underscore-alias or Linux-style alias coverage including the shipped andnot scan entry points, or tail-word skip anchors, or for committed tail-clamped or tail-inclusive-boundary replay drift; do not reopen older saved validator cues or neighboring helper families`",
        "- `PHASE1_RBTREE_NEXT_SAFE_STEP=rbtree reopens only to keep the already-landed cached_leftmost_return_serials shared replay aligned across the manifest, direct-owner note, and any shared parity gates, or for drift inside the still-helper-local ordered Linux-style alias proof, dedicated low_level_alias_anchor, cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed anchors; do not batch a second widening into the same run`",
        "- `PHASE1_STRING_NEXT_SAFE_STEP=string reopens only for direct-anchor drift inside strscpy()/strscpyPad() copy-and-pad semantics, memparse, matched-prefix-length or suffix boundary, sysfs newline-aware equality or lookup order, matchString()/match_string() C-string list lookup, counted-search strnchr, embedded-NUL trim, or moving-earliest-dirty-byte memchrInv coverage, or for committed replaceChar or current string fixture drift; keep the helper-local sysfs review anchors aligned across the string review packet and this lane note unless dedicated shared sysfs fixture keys land; do not reopen missing closure-side validator names by default`",
    ),
    DOCS_ROOT: (
        "* keep the helper-family split explicit here too: the nine shared-replay parked helpers reopen only for packet drift, while bitmap, find_bit, rbtree, and string keep the only bounded direct-anchor follow-up anchors on current master.",
        "* the current docs-root Phase 1 reminder packet should stay parked on the live owner-map, restored closure-side, string-review, direct-owner, and bench guards: `Documentation/zigux/phase1-closure.md` and `scripts/zigux/validate-phase1-closure.py` keep the current-master-safe closure packet explicit, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, and `scripts/zigux/check-phase1-bench.py` are the shipped direct checks, while `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/README.md` keep the same historical-warning wording aligned around the broader missing installer, validator-first, bench-route, and replay surfaces.",
    ),
    PHASE1_CLOSURE: (
        "- `PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
        "- `PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
        "- `PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface or one helper-family tie-breaker against the restored closure note, the closure validator, the shared tests-root smoke route, and the helper-specific next_safe_step_note entries in the committed manifest rather than widening back into the older validator-first or replay-side closure stack.`",
    ),
    REVIEW_CHECKLIST: (
        "* if the change touches the shared Phase 1 host-tools closure packet, do `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, `zigux/tests/README.md`, `zigux/tests/build.zig`, `zigux/tests/phase1_host_tools_smoke.zig`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/fixtures/phase1_helper_manifest.json`, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` still agree on the current closed-helper reminder packet, keep `zigux/Makefile` explicit as current repo evidence for the returned non-Phase-1 route families, while the older validator-first, parity, bench-route, and replay names stay framed as historical packet members until current `master` materializes them again?",
    ),
    SCRIPTS_ROOT: (
        "- `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, and `scripts/zigux/validate-phase1-closure.py` keep the shipped string-review, direct-owner, bench, shared-reminder, and closure-validator packet explicit from the scripts root",
        "- the current direct-anchor tie-breakers stay helper-local: bitmap, find_bit, rbtree, and string reopen only inside their existing helper-local anchors or already-committed shared fixture keys, while the other nine closed helpers stay parked unless the shared replay or reminder packet drifts",
    ),
    TESTS_ROOT: (
        "Tests-root reviewer prompt:",
        "- Does the bounded Phase 1 reminder keep the restored closure note, the workflow-backed closure-validator and shipped checker packet, the shared tests-root smoke route, the manifest-backed owner map, the broader-companion wording for the validator-first, parity, bench-replay, and helper-replay family, and the historical-gap wording for the missing Phase 1 Makefile routes aligned without widening back into the older full closure stack?",
    ),
    DIRECT_OWNER_CHECKER: (
        "EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS = [",
        "EXPECTED_RULE_SUMMARY = (",
        "EXPECTED_ANTI_OVERLAP_RULE = (",
        'print("phase1-direct-owner-markers:ok")',
    ),
    STRING_REVIEW_CHECKER: (
        "EXPECTED_HELPER_TEST_ANCHORS = [",
        'print("phase1-string-review-packet:ok")',
    ),
    SHARED_REMINDER_CHECKER: (
        '"""Guard the current shared Phase 1 reminder packet across docs, tests, scripts, and workflow."""',
        'print("PHASE1_SHARED_REMINDER_PACKET=pass")',
    ),
    CLOSURE_VALIDATOR: (
        "PHASE1_CLOSURE_VALIDATION=pass",
        "PHASE1_CLOSURE_SELF_TEST=pass",
    ),
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, rel: Path) -> str:
    path = root / rel
    if path.is_dir():
        raise IsADirectoryError(rel.as_posix())
    return path.read_text(encoding="utf-8")


def load_manifest(root: Path) -> dict:
    path = root / MANIFEST
    if path.is_dir():
        raise IsADirectoryError(MANIFEST.as_posix())
    return json.loads(path.read_text(encoding="utf-8"))


def count_exact(text: str, marker: str) -> int:
    return text.count(marker)


def collect_missing_files(root: Path) -> list[str]:
    missing: list[str] = []
    for rel in REQUIRED_FILES:
        path = root / rel
        if not path.exists():
            missing.append(f"missing_file:{rel.as_posix()}")
        elif path.is_dir():
            missing.append(f"directory_path:{rel.as_posix()}")
    return missing


def collect_marker_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for rel, markers in REQUIRED_MARKERS.items():
        text = read_text(root, rel)
        for marker in markers:
            count = count_exact(text, marker)
            if count != 1:
                failures.append(
                    f"marker:{rel.as_posix()}:expected=1:actual={count}:{marker}"
                )
    return failures


def manifest_get(manifest: dict, path: tuple[str, ...]):
    value = manifest
    for key in path:
        value = value[key]
    return value


def collect_manifest_failures(root: Path) -> list[str]:
    manifest = load_manifest(root)
    failures: list[str] = []

    expected_paths = {
        ("lane_sequencing", "shared_replay_parked_helpers"): EXPECTED_SHARED_HELPERS,
        ("lane_sequencing", "direct_anchor_followup_helpers"): EXPECTED_DIRECT_HELPERS,
        ("lane_sequencing", "rule_summary"): EXPECTED_RULE_SUMMARY,
        ("lane_sequencing", "anti_overlap_rule"): EXPECTED_ANTI_OVERLAP_RULE,
        ("review_anchors", "tools/lib/bitmap.zig", "next_safe_step_note"): (
            "If this helper lane reopens, keep bitmap parked unless a fresh reread finds new direct-anchor drift inside the current helper-local packet or committed shared replay drift in the bitmap parity fields; current master still ships direct fill-tail clamp, copy-alias, truncation, cross-word scnprintf, exact-word-boundary equality fast-path masking, caller-window xor and or clamp, weighted tail-count clamp, empty-buffer, allocator-reset, zero-bit logical short-circuit, and Linux-style alias mirror anchors here; do not reopen older closure-side or validator-route cue names by default."
        ),
        ("review_anchors", "tools/lib/find_bit.zig", "next_safe_step_note"): (
            "If this helper lane reopens, keep find_bit parked unless a fresh reread finds direct-anchor drift inside same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, getValue8(), findLastBit(), underscore-alias, Linux-style alias coverage including the shipped andnot scan entry points, or tail-word skip anchors, or committed tail-clamped or tail-inclusive-boundary replay drift; do not reopen older saved validator cues or neighboring helper families."
        ),
        ("review_anchors", "tools/lib/rbtree.zig", "next_safe_step_note"): (
            "If this helper lane reopens, keep the already-landed shared-replay promotion for `cached_leftmost_return_serials` aligned across the committed fixture, shared replay, and direct cached-root anchors; the ordered Linux-style alias proof, dedicated `low_level_alias_anchor`, and the remaining cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed behavior stay owned by direct helper-local anchors until another committed cached-root field lands."
        ),
        ("review_anchors", "tools/lib/string.zig", "next_safe_step_note"): (
            "If this helper lane reopens, keep string parked unless a fresh reread finds drift in the committed `replaceChar` parity bytes or current string fixture keys, or in helper-local copy-and-pad, memparse, matched-prefix, suffix-boundary, sysfs lookup-order, counted-search, embedded-NUL trim, or memchrInv anchors; keep the helper-local sysfs review anchors aligned across the string review packet and this lane note unless dedicated shared sysfs fixture keys land; do not reopen missing closure-side validator names by default."
        ),
    }

    for path, expected in expected_paths.items():
        actual = manifest_get(manifest, path)
        if actual != expected:
            failures.append(f"manifest:{'.'.join(path)}")

    return failures


def collect_failures(root: Path) -> list[str]:
    failures = collect_missing_files(root)
    if failures:
        return failures
    try:
        failures.extend(collect_marker_failures(root))
        failures.extend(collect_manifest_failures(root))
    except (KeyError, json.JSONDecodeError, IsADirectoryError) as exc:
        failures.append(f"exception:{type(exc).__name__}:{exc}")
    return failures


def write_text(root: Path, rel: Path, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_sample_root(root: Path) -> None:
    for rel, markers in REQUIRED_MARKERS.items():
        write_text(root, rel, "\n".join(markers) + "\n")

    manifest = {
        "lane_sequencing": {
            "shared_replay_parked_helpers": EXPECTED_SHARED_HELPERS,
            "direct_anchor_followup_helpers": EXPECTED_DIRECT_HELPERS,
            "rule_summary": EXPECTED_RULE_SUMMARY,
            "anti_overlap_rule": EXPECTED_ANTI_OVERLAP_RULE,
        },
        "review_anchors": {
            "tools/lib/bitmap.zig": {
                "next_safe_step_note": "If this helper lane reopens, keep bitmap parked unless a fresh reread finds new direct-anchor drift inside the current helper-local packet or committed shared replay drift in the bitmap parity fields; current master still ships direct fill-tail clamp, copy-alias, truncation, cross-word scnprintf, exact-word-boundary equality fast-path masking, caller-window xor and or clamp, weighted tail-count clamp, empty-buffer, allocator-reset, zero-bit logical short-circuit, and Linux-style alias mirror anchors here; do not reopen older closure-side or validator-route cue names by default."
            },
            "tools/lib/find_bit.zig": {
                "next_safe_step_note": "If this helper lane reopens, keep find_bit parked unless a fresh reread finds direct-anchor drift inside same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, getValue8(), findLastBit(), underscore-alias, Linux-style alias coverage including the shipped andnot scan entry points, or tail-word skip anchors, or committed tail-clamped or tail-inclusive-boundary replay drift; do not reopen older saved validator cues or neighboring helper families."
            },
            "tools/lib/rbtree.zig": {
                "next_safe_step_note": "If this helper lane reopens, keep the already-landed shared-replay promotion for `cached_leftmost_return_serials` aligned across the committed fixture, shared replay, and direct cached-root anchors; the ordered Linux-style alias proof, dedicated `low_level_alias_anchor`, and the remaining cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed behavior stay owned by direct helper-local anchors until another committed cached-root field lands."
            },
            "tools/lib/string.zig": {
                "next_safe_step_note": "If this helper lane reopens, keep string parked unless a fresh reread finds drift in the committed `replaceChar` parity bytes or current string fixture keys, or in helper-local copy-and-pad, memparse, matched-prefix, suffix-boundary, sysfs lookup-order, counted-search, embedded-NUL trim, or memchrInv anchors; keep the helper-local sysfs review anchors aligned across the string review packet and this lane note unless dedicated shared sysfs fixture keys land; do not reopen missing closure-side validator names by default."
            },
        },
    }
    write_text(root, MANIFEST, json.dumps(manifest, indent=2, sort_keys=True) + "\n")


def mutate_remove_marker(root: Path, rel: Path, marker: str) -> None:
    text = read_text(root, rel)
    (root / rel).write_text(text.replace(marker + "\n", "", 1), encoding="utf-8")


def mutate_duplicate_marker(root: Path, rel: Path, marker: str) -> None:
    text = read_text(root, rel)
    (root / rel).write_text(
        text.replace(marker, marker + "\n" + marker, 1), encoding="utf-8"
    )


def mutate_manifest_value(root: Path, path: tuple[str, ...], value) -> None:
    manifest = load_manifest(root)
    target = manifest
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    write_text(root, MANIFEST, json.dumps(manifest, indent=2, sort_keys=True) + "\n")


def run_self_test() -> int:
    cases: list[tuple[str, tuple | None]] = [("success", None)]
    cases.append(("missing_file", ("unlink", TESTS_ROOT)))
    cases.append(("directory_path", ("mkdir", DIRECT_OWNER_CHECKER)))
    cases.append(("lane_note_missing_marker", ("remove", LANE_NOTE, REQUIRED_MARKERS[LANE_NOTE][0])))
    cases.append(("lane_note_duplicate_marker", ("duplicate", LANE_NOTE, REQUIRED_MARKERS[LANE_NOTE][1])))
    cases.append(("docs_root_missing_marker", ("remove", DOCS_ROOT, REQUIRED_MARKERS[DOCS_ROOT][0])))
    cases.append(("scripts_root_missing_marker", ("remove", SCRIPTS_ROOT, REQUIRED_MARKERS[SCRIPTS_ROOT][1])))
    cases.append(("manifest_direct_helpers_drift", ("manifest", ("lane_sequencing", "direct_anchor_followup_helpers"), ["tools/lib/bitmap.zig"])))
    cases.append(("manifest_shared_helpers_drift", ("manifest", ("lane_sequencing", "shared_replay_parked_helpers"), ["tools/lib/slab.zig"])))
    cases.append(("manifest_string_note_drift", ("manifest", ("review_anchors", "tools/lib/string.zig", "next_safe_step_note"), "drift")))
    cases.append(("manifest_invalid_json", ("raw_manifest", "{not json\n")))

    for name, mutation in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-helper-lane-") as tmpdir:
            root = Path(tmpdir)
            write_sample_root(root)
            if mutation:
                kind = mutation[0]
                if kind == "unlink":
                    (root / mutation[1]).unlink()
                elif kind == "mkdir":
                    target = root / mutation[1]
                    target.unlink()
                    target.mkdir(parents=True)
                elif kind == "remove":
                    mutate_remove_marker(root, mutation[1], mutation[2])
                elif kind == "duplicate":
                    mutate_duplicate_marker(root, mutation[1], mutation[2])
                elif kind == "manifest":
                    mutate_manifest_value(root, mutation[1], mutation[2])
                elif kind == "raw_manifest":
                    write_text(root, MANIFEST, mutation[1])
            failures = collect_failures(root)
            if name == "success":
                if failures:
                    print("self-test:success:unexpected-failure")
                    for failure in failures:
                        print(failure)
                    return 1
            elif not failures:
                print(f"self-test:{name}:expected-failure")
                return 1

    print("PHASE1_HELPER_LANE_SEQUENCING_SELF_TEST=pass")
    print(f"PHASE1_HELPER_LANE_SEQUENCING_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-test")
    parser.add_argument("--write-sample-root", help="write a current-like sample packet root")
    args = parser.parse_args()

    if args.write_sample_root:
        sample_root = Path(args.write_sample_root).resolve()
        if sample_root.exists():
            shutil.rmtree(sample_root)
        write_sample_root(sample_root)
        print(f"PHASE1_HELPER_LANE_SEQUENCING_SAMPLE_ROOT={sample_root}")
        return 0

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_HELPER_LANE_SEQUENCING=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_HELPER_LANE_SEQUENCING=pass")
    print(f"PHASE1_HELPER_LANE_SEQUENCING_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_HELPER_LANE_SEQUENCING_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    print(f"PHASE1_HELPER_LANE_SEQUENCING_SHARED_HELPER_COUNT={len(EXPECTED_SHARED_HELPERS)}")
    print(f"PHASE1_HELPER_LANE_SEQUENCING_DIRECT_HELPER_COUNT={len(EXPECTED_DIRECT_HELPERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
