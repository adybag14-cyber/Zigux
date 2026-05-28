#!/usr/bin/env python3
"""Guard the Phase 1 lane-sequencing packet against split drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
DOCS_ROOT_REL = Path("Documentation/zigux/README.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
TESTS_README_REL = Path("zigux/tests/README.md")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")

REQUIRED_FILES = (
    LANE_NOTE_REL,
    DOCS_ROOT_REL,
    SCRIPTS_README_REL,
    TESTS_README_REL,
    MANIFEST_REL,
)


class DuplicateTrackingDict(dict[str, object]):
    def __init__(self, pairs: list[tuple[str, object]]) -> None:
        super().__init__()
        self.duplicate_keys: list[str] = []
        for key, value in pairs:
            if key in self and key not in self.duplicate_keys:
                self.duplicate_keys.append(key)
            self[key] = value


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

EXPECTED_FIND_BIT_ANDNOT_SCAN_ENTRYPOINTS = [
    "findFirstAndNotBit",
    "find_first_andnot_bit",
    "_find_first_andnot_bit",
    "findNextAndNotBit",
    "find_next_andnot_bit",
    "_find_next_andnot_bit",
]

EXPECTED_STRING_COUNTED_SEARCH_REVIEW_ANCHORS = [
    'test "strchr mirrors full-length C-string searches"',
    'test "strrchr finds the last in-range match with C-string semantics"',
    'test "strpbrk finds the first accepted byte with C-string semantics"',
    'test "strspn counts the accepted prefix with C-string semantics"',
    'test "strcspn counts until the first rejected byte with C-string semantics"',
    'test "strnchr honors count and C-string boundaries"',
    'test "strnlen honors count and C-string boundaries"',
    'test "strnchrNul returns the first match, NUL, or count boundary"',
    'test "strchrNul and strchrnul return the first match or terminator boundary"',
]

EXPECTED_REQUIRED_LINES = {
    LANE_NOTE_REL: [
        "- `PHASE1_SHARED_REPLAY_PARKED_HELPERS=tools/lib/argv_split.zig,tools/lib/cmdline.zig,tools/lib/ctype.zig,tools/lib/hweight.zig,tools/lib/list_sort.zig,tools/lib/slab.zig,tools/lib/str_error_r.zig,tools/lib/vsprintf.zig,tools/lib/zalloc.zig`",
        "- `PHASE1_DIRECT_ANCHOR_FOLLOWUP_HELPERS=tools/lib/bitmap.zig,tools/lib/find_bit.zig,tools/lib/rbtree.zig,tools/lib/string.zig`",
        "- `PHASE1_LANE_RULE_SUMMARY=Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, while bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local follow-up anchors on current master.`",
        "- `PHASE1_LANE_ANTI_OVERLAP_RULE=Do not reopen Phase 1 by batching helpers across those two sets in one lane; shared-replay parked helpers reopen only for packet drift, while direct-anchor helpers reopen only for their existing helper-local anchors or already-committed shared fixture keys.`",
        "- `PHASE1_BITMAP_NEXT_SAFE_STEP=bitmap stays parked unless a fresh reread finds new direct-anchor drift or committed shared replay drift; do not reopen older closure-side or validator-route cue names by default`",
        "- `PHASE1_FIND_BIT_NEXT_SAFE_STEP=find_bit reopens only for direct-anchor drift inside same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, getValue8(), findLastBit(), underscore-alias or Linux-style alias coverage including the shipped andnot scan entry points, or tail-word skip anchors, or for committed tail-clamped or tail-inclusive-boundary replay drift; do not reopen older saved validator cues or neighboring helper families`",
        "- `PHASE1_RBTREE_NEXT_SAFE_STEP=rbtree reopens only to keep the already-landed cached_leftmost_return_serials shared replay aligned across the manifest, direct-owner note, and any shared parity gates, or for drift inside the still-helper-local ordered Linux-style alias proof, dedicated low_level_alias_anchor, cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed anchors; do not batch a second widening into the same run`",
        "- `PHASE1_STRING_NEXT_SAFE_STEP=string reopens only for direct-anchor drift inside strscpy()/strscpyPad() copy-and-pad semantics, memparse, matched-prefix-length or suffix boundary, sysfs newline-aware equality or lookup order, matchString()/match_string() C-string list lookup, counted-search and search-length anchors through strpbrk(), strspn(), strcspn(), strnchr(), strnchrNul() or strnchrnul(), strchr(), strrchr(), strlen(), and strnlen(), embedded-NUL trim, or moving-earliest-dirty-byte memchrInv coverage, or for committed replaceChar or current string fixture drift; keep the helper-local sysfs review anchors aligned across the string review packet and this lane note unless dedicated shared sysfs fixture keys land; do not reopen missing closure-side validator names by default`",
    ],
    DOCS_ROOT_REL: [
        "* keep the helper-family split explicit here too: the nine shared-replay parked helpers reopen only for packet drift, while bitmap, find_bit, rbtree, and string keep the only bounded direct-anchor follow-up anchors on current master.",
    ],
    SCRIPTS_README_REL: [
        "- the current direct-anchor tie-breakers stay helper-local: bitmap, find_bit, rbtree, and string reopen only inside their existing helper-local anchors or already-committed shared fixture keys, while the other nine closed helpers stay parked unless the shared replay or reminder packet drifts",
    ],
    TESTS_README_REL: [
        "* keep the Phase 1 tests-root reminder truthful: the thirteen helper ports remain closed through the committed manifest, the nine shared-replay parked helpers reopen only for packet or fixture drift, and only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers on current `master`",
    ],
}

EXPECTED_MANIFEST_VALUES = {
    ("phase",): "Phase 1",
    ("status",): "closed",
    ("helper_count",): len(EXPECTED_HELPERS),
    ("helpers",): EXPECTED_HELPERS,
    ("lane_sequencing", "shared_replay_parked_helpers"): EXPECTED_SHARED_REPLAY_PARKED_HELPERS,
    ("lane_sequencing", "direct_anchor_followup_helpers"): EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS,
    ("lane_sequencing", "rule_summary"): EXPECTED_RULE_SUMMARY,
    ("lane_sequencing", "anti_overlap_rule"): EXPECTED_ANTI_OVERLAP_RULE,
    (
        "review_anchors",
        "tools/lib/bitmap.zig",
        "next_safe_step_note",
    ): (
        "If this helper lane reopens, keep bitmap parked unless a fresh reread finds new direct-anchor "
        "drift inside the current helper-local packet or committed shared replay drift in the bitmap copy, "
        "logical, range, allocation, formatting, or partial-window parity fields; current master still "
        "ships direct fill-tail clamp, raw copy alias, cross-word scnprintf, exact-word-boundary equality "
        "fast-path masking, caller-window xor and or clamp, weighted tail-count clamp, empty-buffer, "
        "allocator-reset, zero-bit logical short-circuit, and Linux-style alias mirror anchors here; do "
        "not reopen older closure-side or validator-route cue names by default."
    ),
    (
        "review_anchors",
        "tools/lib/find_bit.zig",
        "andnot_scan_entrypoints",
    ): EXPECTED_FIND_BIT_ANDNOT_SCAN_ENTRYPOINTS,
    (
        "review_anchors",
        "tools/lib/find_bit.zig",
        "next_safe_step_note",
    ): (
        "If this helper lane reopens, keep find_bit parked unless a fresh reread finds drift in the "
        "manifest-backed same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, "
        "past-nbits, clump8, getValue8(), findLastBit(), underscore-alias, Linux-style alias coverage "
        "including the shipped andnot scan entry points, or tail-word skip anchors, or committed shared "
        "replay drift in the live `bits_per_long`, `first`, `next_after_6`, `next_after_word`, "
        "`first_zero`, `next_zero`, `first_and`, `next_and`, or `last` fixture keys; do not reopen older "
        "saved validator cues or neighboring helper families."
    ),
    (
        "review_anchors",
        "tools/lib/rbtree.zig",
        "cached_leftmost_fixture_keys",
    ): ["cached_leftmost_return_serials"],
    (
        "review_anchors",
        "tools/lib/rbtree.zig",
        "next_safe_step_note",
    ): (
        "If this helper lane reopens, keep the already-landed shared-replay promotion for "
        "`cached_leftmost_return_serials` aligned across the committed fixture, shared replay, and "
        "direct cached-root anchors; the ordered Linux-style alias proof, dedicated "
        "`low_level_alias_anchor`, and the remaining cached-root insert-miss, leftmost-sync, "
        "cached-root alias, singleton-erase, replacement, detach, and reseed behavior stay owned by "
        "direct helper-local anchors until another committed cached-root field lands."
    ),
    (
        "review_anchors",
        "tools/lib/string.zig",
        "counted_search_review_anchors",
    ): EXPECTED_STRING_COUNTED_SEARCH_REVIEW_ANCHORS,
    (
        "review_anchors",
        "tools/lib/string.zig",
        "next_safe_step_note",
    ): (
        "If this helper lane reopens, keep the helper-local strlcat, sysfs, case-insensitive compare, "
        "and match-or-terminator review anchors aligned across the string review packet and this lane "
        "note unless dedicated shared fixture keys land; do not reopen missing closure-side validator "
        "names by default."
    ),
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json(root: Path, relative_path: Path) -> object:
    return json.loads(load_text(root, relative_path), object_pairs_hook=DuplicateTrackingDict)


def collect_duplicate_json_key_paths(data: object, prefix: tuple[str, ...] = ()) -> list[str]:
    paths: list[str] = []
    if isinstance(data, DuplicateTrackingDict):
        for key in data.duplicate_keys:
            paths.append(".".join(prefix + (key,)))
    if isinstance(data, dict):
        for key, value in data.items():
            paths.extend(collect_duplicate_json_key_paths(value, prefix + (key,)))
    elif isinstance(data, list):
        for item in data:
            paths.extend(collect_duplicate_json_key_paths(item, prefix))
    return paths


def nested_value(data: object, path: tuple[str, ...]) -> object:
    current = data
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def require_exact_line(text: str, label: str, line: str) -> list[str]:
    expected = line.strip()
    count = sum(1 for current in text.splitlines() if current.strip() == expected)
    return [] if count == 1 else [f"{label}:expected_once:actual_count={count}"]


def require_exact_value(label: str, actual: object, expected: object) -> list[str]:
    return [] if actual == expected else [f"{label}:expected={expected!r}:actual={actual!r}"]


def collect_failures(root: Path) -> list[str]:
    failures = [f"missing_file:{path.as_posix()}" for path in REQUIRED_FILES if not (root / path).is_file()]
    if failures:
        return failures

    for relative_path, lines in EXPECTED_REQUIRED_LINES.items():
        text = load_text(root, relative_path)
        for index, line in enumerate(lines):
            failures.extend(require_exact_line(text, f"{relative_path.as_posix()}:line_{index}", line))

    try:
        manifest = load_json(root, MANIFEST_REL)
    except json.JSONDecodeError as exc:
        return [f"{MANIFEST_REL.as_posix()}:invalid_json:{exc.msg}:line={exc.lineno}:column={exc.colno}"]

    if not isinstance(manifest, dict):
        return [f"{MANIFEST_REL.as_posix()}:expected=dict:actual={type(manifest).__name__}"]

    duplicate_paths = collect_duplicate_json_key_paths(manifest)
    if duplicate_paths:
        return [f"{MANIFEST_REL.as_posix()}:duplicate_json_key:{path}" for path in duplicate_paths]

    for path, expected in EXPECTED_MANIFEST_VALUES.items():
        failures.extend(
            require_exact_value(
                f"{MANIFEST_REL.as_posix()}:{'.'.join(path)}",
                nested_value(manifest, path),
                expected,
            )
        )

    return failures


def write_text(root: Path, relative_path: Path, text: str) -> None:
    target = root / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def sample_manifest_text() -> str:
    data = {
        "phase": "Phase 1",
        "status": "closed",
        "helper_count": len(EXPECTED_HELPERS),
        "helpers": EXPECTED_HELPERS,
        "lane_sequencing": {
            "shared_replay_parked_helpers": EXPECTED_SHARED_REPLAY_PARKED_HELPERS,
            "direct_anchor_followup_helpers": EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS,
            "rule_summary": EXPECTED_RULE_SUMMARY,
            "anti_overlap_rule": EXPECTED_ANTI_OVERLAP_RULE,
        },
        "review_anchors": {
            "tools/lib/bitmap.zig": {
                "next_safe_step_note": EXPECTED_MANIFEST_VALUES[("review_anchors", "tools/lib/bitmap.zig", "next_safe_step_note")],
            },
            "tools/lib/find_bit.zig": {
                "andnot_scan_entrypoints": EXPECTED_FIND_BIT_ANDNOT_SCAN_ENTRYPOINTS,
                "next_safe_step_note": EXPECTED_MANIFEST_VALUES[("review_anchors", "tools/lib/find_bit.zig", "next_safe_step_note")],
            },
            "tools/lib/rbtree.zig": {
                "cached_leftmost_fixture_keys": ["cached_leftmost_return_serials"],
                "next_safe_step_note": EXPECTED_MANIFEST_VALUES[("review_anchors", "tools/lib/rbtree.zig", "next_safe_step_note")],
            },
            "tools/lib/string.zig": {
                "counted_search_review_anchors": EXPECTED_STRING_COUNTED_SEARCH_REVIEW_ANCHORS,
                "next_safe_step_note": EXPECTED_MANIFEST_VALUES[("review_anchors", "tools/lib/string.zig", "next_safe_step_note")],
            },
        },
    }
    return json.dumps(data, indent=2) + "\n"


def write_sample_root(root: Path) -> None:
    for relative_path, lines in EXPECTED_REQUIRED_LINES.items():
        write_text(root, relative_path, "# sample\n\n" + "\n".join(lines) + "\n")
    write_text(root, MANIFEST_REL, sample_manifest_text())


def mutate_manifest(root: Path, path: tuple[str, ...]) -> None:
    manifest_path = root / MANIFEST_REL
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    current = manifest
    for key in path[:-1]:
        current = current[key]
    final_key = path[-1]
    value = current[final_key]
    if isinstance(value, list):
        current[final_key] = value[:-1]
    elif isinstance(value, int):
        current[final_key] = value + 1
    else:
        current[final_key] = f"{value} drift"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def insert_duplicate_manifest_key(root: Path) -> None:
    manifest_path = root / MANIFEST_REL
    text = manifest_path.read_text(encoding="utf-8")
    needle = '    "tools/lib/string.zig": {\n'
    replacement = '    "tools/lib/string.zig": {},\n' + needle
    manifest_path.write_text(text.replace(needle, replacement, 1), encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, str, object | None]] = [("baseline", "none", None)]

    for relative_path in REQUIRED_FILES:
        cases.append((f"missing_file:{relative_path.as_posix()}", "remove_file", relative_path))

    for relative_path, lines in EXPECTED_REQUIRED_LINES.items():
        for line in lines:
            cases.append((f"missing_line:{relative_path.as_posix()}", "remove_line", (relative_path, line)))
            cases.append((f"duplicate_line:{relative_path.as_posix()}", "duplicate_line", (relative_path, line)))

    for path in EXPECTED_MANIFEST_VALUES:
        cases.append((f"manifest_drift:{'.'.join(path)}", "mutate_manifest", path))

    cases.append(("duplicate_manifest_key", "duplicate_manifest_key", None))

    for name, mode, payload in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-lane-sequencing-") as tmpdir:
            root = Path(tmpdir)
            write_sample_root(root)

            if mode == "remove_file" and isinstance(payload, Path):
                (root / payload).unlink()
            elif mode == "remove_line" and isinstance(payload, tuple):
                relative_path, line = payload
                target = root / relative_path
                keep = [current for current in target.read_text(encoding="utf-8").splitlines() if current.strip() != line.strip()]
                target.write_text("\n".join(keep) + ("\n" if keep else ""), encoding="utf-8")
            elif mode == "duplicate_line" and isinstance(payload, tuple):
                relative_path, line = payload
                target = root / relative_path
                lines = target.read_text(encoding="utf-8").splitlines()
                for index, current in enumerate(lines):
                    if current.strip() == line.strip():
                        lines.insert(index + 1, current)
                        break
                target.write_text("\n".join(lines) + "\n", encoding="utf-8")
            elif mode == "mutate_manifest" and isinstance(payload, tuple):
                mutate_manifest(root, payload)
            elif mode == "duplicate_manifest_key":
                insert_duplicate_manifest_key(root)

            failures = collect_failures(root)
            if name == "baseline":
                if failures:
                    print(f"self-test:{name}:unexpected_failures")
                    for failure in failures:
                        print(failure)
                    return 1
            elif not failures:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("PHASE1_LANE_SEQUENCING_SELF_TEST=pass")
    print(f"PHASE1_LANE_SEQUENCING_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run checker self-tests")
    parser.add_argument("--write-sample-root", help="write a current-like sample repo root")
    args = parser.parse_args()

    if args.write_sample_root:
        write_sample_root(Path(args.write_sample_root).resolve())
        print("PHASE1_LANE_SEQUENCING_SAMPLE_ROOT=written")
        return 0

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_LANE_SEQUENCING=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_LANE_SEQUENCING=pass")
    print(f"PHASE1_LANE_SEQUENCING_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE1_LANE_SEQUENCING_REQUIRED_LINE_COUNT={sum(len(lines) for lines in EXPECTED_REQUIRED_LINES.values())}")
    print(f"PHASE1_LANE_SEQUENCING_DIRECT_ANCHOR_HELPER_COUNT={len(EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS)}")
    print(f"PHASE1_LANE_SEQUENCING_SHARED_REPLAY_HELPER_COUNT={len(EXPECTED_SHARED_REPLAY_PARKED_HELPERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
