#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
BITMAP_DIRECT_ANCHOR_CHECKER_REL = Path("scripts/zigux/check-phase1-bitmap-direct-anchors.py")
FIND_BIT_REVIEW_CHECKER_REL = Path("scripts/zigux/check-phase1-find-bit-review-packet.py")
RBTREE_DIRECT_ANCHOR_CHECKER_REL = Path("scripts/zigux/check-phase1-rbtree-direct-anchors.py")
RBTREE_REVIEW_CHECKER_REL = Path("scripts/zigux/check-phase1-rbtree-review-packet.py")
STRING_REVIEW_CHECKER_REL = Path("scripts/zigux/check-phase1-string-review-packet.py")


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

EXPECTED_RBTREE_HELPER_TEST_ANCHORS = [
    'test "rbtree inserts and traverses in sorted order"',
    'test "rbtree erase and replace keep traversal consistent"',
    'test "rbtree ordered Linux-style aliases mirror traversal and replacement helpers"',
    'test "rbtree low-level Linux-style aliases mirror node-state helpers"',
    'test "rbtree eraseInit detaches erased node"',
    'test "rbtree eraseInit clears singleton roots before reseed"',
    'test "rbtree postorder and empty node helpers behave"',
    'test "rbtree findAdd keeps the first duplicate and inserts new keys"',
    'test "rbtree nextMatch walks the duplicate range in order"',
    'test "rbtree matchIterator walks the duplicate range in order"',
    'test "rbtree addCached returns the inserted node only when it becomes leftmost"',
    'test "rbtree findAddCached keeps cached leftmost stable while inserting misses"',
    'test "rbtree cached root keeps the leftmost pointer in sync"',
    'test "rbtree cached-root Linux-style aliases mirror the primary helpers"',
    'test "rbtree replaceNodeCached keeps non-leftmost leftmost unchanged"',
    'test "rbtree eraseCached returns null for a singleton cached tree"',
    'test "rbtree eraseInitCached detaches nodes while keeping cached leftmost aligned"',
    'test "rbtree eraseInitCached clears singleton cached roots before reseed"',
]

EXPECTED_REVIEW_FIELDS = {
    "tools/lib/bitmap.zig": {
        "copy_raw_alias_anchor": 'test "bitmap copy alias preserves raw source words without tail clearing"',
        "or_window_anchor": 'test "bitmap or keeps caller-selected bit window"',
        "or_multiword_tail_anchor": 'test "bitmap or across a multiword tail still lets callers clamp the last word"',
        "weighted_tail_count_anchor": 'test "bitmap weighted or and xor clamp counts to the declared tail window"',
        "empty_buffer_anchor": 'test "bitmap scnprintf leaves the caller buffer untouched for an empty bitmap"',
        "scnprintf_cross_word_anchor": 'test "bitmap scnprintf keeps contiguous ranges merged across word boundaries"',
        "zero_bit_noop_anchor": 'test "bitmap zero-bit logical helpers stay explicit"',
        "partial_xor_review_fields": ["partial_xor_nbits", "partial_xor_masked_values"],
        "review_packet_summary": (
            "shared Phase 1 fixture keys now own bitmap allocator sizing, zero-filled allocation words, copy/copy-clear-tail/copy-and-extend replay, scnprintf output, truncation, tiny-buffer handling, logical operator outputs, range set/clear/fill/zero outcomes, and partial-window xor replay, while current master keeps the direct helper-local bitmap packet bounded to whole-word range edges, raw copy alias behavior, tail-clearing and extension semantics, zero and aligned copyAndExtend handling, zero-sized destination-view no-op coverage, zero-bit logical short-circuit coverage, exact-word-boundary equality fast-path masking, tail-masked predicate behavior, out-of-range tail-bit full or empty or weight masking, caller-window xor and or clamping, multiword-tail xor and or clamp witnesses, weighted tail-count clamping, terminator-only and zero-length caller-view formatting, empty-bitmap caller-buffer preservation, Linux-style alias mirror coverage, and allocator optional-reset coverage."
        ),
        "next_safe_step_note": (
            "If this helper lane reopens, keep bitmap parked unless a fresh reread finds new direct-anchor drift inside the current helper-local packet or committed shared replay drift in the bitmap copy, logical, range, allocation, formatting, or partial-window parity fields; current master still ships direct fill-tail clamp, raw copy alias, cross-word scnprintf, exact-word-boundary equality fast-path masking, caller-window xor and or clamp, weighted tail-count clamp, empty-buffer, allocator-reset, zero-bit logical short-circuit, and Linux-style alias mirror anchors here; do not reopen older closure-side or validator-route cue names by default."
        ),
    },
    "tools/lib/find_bit.zig": {
        "helper_test_anchors": [
            'test "clump8 past-end scans return without reading bitmap words"',
            'test "low-level underscore aliases mirror the primary find helpers, including andnot"',
            'test "Linux-style aliases mirror the primary find helpers, including andnot"',
        ],
        "same_word_start_masks": 'test "single-word next scans honor start masks"',
        "andnot_scan_entrypoints": [
            "findFirstAndNotBit",
            "find_first_andnot_bit",
            "_find_first_andnot_bit",
            "findNextAndNotBit",
            "find_next_andnot_bit",
            "_find_next_andnot_bit",
        ],
        "andnot_scan_entrypoint_contract": (
            "The shipped public, Linux-style, and underscore andnot scan entry points stay owned by the direct find_bit packet instead of being left implicit under generic alias wording."
        ),
        "tail_clamp_fixture_keys": [
            "tail_clamped_first",
            "tail_clamped_next",
            "tail_zero_clamped_first",
            "tail_zero_clamped_next",
            "tail_and_clamped_first",
            "tail_and_clamped_next",
            "tail_clamped_last",
            "tail_clamped_empty_last",
        ],
        "tail_inclusive_boundary_fixture_keys": [
            "tail_inclusive_boundary_next",
            "tail_inclusive_boundary_zero",
            "tail_inclusive_boundary_and",
        ],
        "review_packet_summary": (
            "shared Phase 1 fixture keys own the exact tail-clamped and tail-inclusive-boundary find_bit replay, while helper-local anchors keep same-word start-mask, head-word and tail-word inclusive-boundary, single-word tail inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, tail-word set or zero or shared skip, clump8, getValue8(), findLastBit(), underscore-alias, and Linux-style alias behavior review-visible on current master"
        ),
        "next_safe_step_note": (
            "If this helper lane reopens, keep find_bit parked unless a fresh reread finds direct-anchor "
            "drift inside same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, "
            "past-nbits, clump8, getValue8(), findLastBit(), underscore-alias, Linux-style alias coverage "
            "including the shipped andnot scan entry points, or tail-word skip anchors, or committed "
            "tail-clamped or tail-inclusive-boundary replay drift; do not reopen older saved validator cues "
            "or neighboring helper families."
        ),
    },
    "tools/lib/rbtree.zig": {
        "helper_test_anchors": EXPECTED_RBTREE_HELPER_TEST_ANCHORS,
        "cached_root_followup_anchors": [
            'test "rbtree addCached returns the inserted node only when it becomes leftmost"',
            'test "rbtree findAddCached keeps cached leftmost stable while inserting misses"',
            'test "rbtree cached root keeps the leftmost pointer in sync"',
            'test "rbtree cached-root Linux-style aliases mirror the primary helpers"',
            'test "rbtree replaceNodeCached keeps non-leftmost leftmost unchanged"',
            'test "rbtree eraseCached returns null for a singleton cached tree"',
            'test "rbtree eraseInitCached detaches nodes while keeping cached leftmost aligned"',
            'test "rbtree eraseInitCached clears singleton cached roots before reseed"',
        ],
        "cached_root_alias_anchor": 'test "rbtree cached-root Linux-style aliases mirror the primary helpers"',
        "cached_root_transition_fixture_keys": ["cached_root_transition_serials"],
        "shared_replay_summary": (
            "the committed Phase 1 fixture still carries traversal, detached-node, duplicate-search, "
            "and exact cached-leftmost-return witnesses for rbtree, while the current shared host-tools "
            "smoke replay now rechecks duplicate-range iteration plus the exact `cached_leftmost_return_serials` "
            "cached-root leftmost-return sequence on current master"
        ),
        "next_safe_step_note": (
            "If this helper lane reopens, keep the already-landed shared-replay promotion for "
            "`cached_leftmost_return_serials` aligned across the committed fixture, shared replay, and "
            "direct cached-root anchors; the ordered Linux-style alias proof, dedicated "
            "`low_level_alias_anchor`, and the remaining cached-root insert-miss, leftmost-sync, "
            "cached-root alias, singleton-erase, replacement, detach, and reseed behavior stay owned by "
            "direct helper-local anchors until another committed cached-root field lands."
        ),
    },
    "tools/lib/string.zig": {
        "helper_test_anchors": [
            'test "memchr_inv mirrors memchrInv byte-search semantics"',
            'test "strcmp mirrors C-string lexical ordering"',
            'test "strcmp stops at embedded NULs and length mismatches"',
            'test "strspn counts the accepted prefix with C-string semantics"',
            'test "strnchrNul returns the first match, NUL, or count boundary"',
        ],
        "memparse_review_anchors": [
            'test "memparse handles decimal hexadecimal octal and suffixes"',
            'test "memparse keeps original rest when sign is not followed by digits"',
            'test "memparse saturates signed overflow instead of trapping"',
            'test "memparse clamps explicit positive signed overflow"',
            'test "memparse keeps signed values and their trailing rest aligned"',
            'test "memparse consumes suffix after saturation"',
            'test "memparse applies suffixes before signed clamping"',
        ],
        "strcmp_review_anchors": [
            'test "strcmp mirrors C-string lexical ordering"',
            'test "strcmp stops at embedded NULs and length mismatches"',
        ],
        "strcmp_review_summary": (
            "helper-local lexical-compare anchors stay explicit through the direct string tests because "
            "the shared Phase 1 replay still does not carry dedicated strcmp() fixture keys, so lexical "
            "ordering and embedded-NUL length-mismatch behavior remain review-visible at the helper surface"
        ),
        "counted_search_review_anchors": [
            'test "strchr mirrors full-length C-string searches"',
            'test "strrchr finds the last in-range match with C-string semantics"',
            'test "strpbrk finds the first accepted byte with C-string semantics"',
            'test "strspn counts the accepted prefix with C-string semantics"',
            'test "strcspn counts until the first rejected byte with C-string semantics"',
            'test "strnchr honors count and C-string boundaries"',
            'test "strnlen honors count and C-string boundaries"',
            'test "strnchrNul returns the first match, NUL, or count boundary"',
        ],
        "strnchr_review_summary": (
            "the direct counted-search and C-string search-length follow-up stays explicit because the "
            "shared Phase 1 replay still does not carry dedicated counted-search or search-length fixture "
            "keys, so strchr() or strrchr() full-length C-string searches, strpbrk() first-accepted-byte "
            "scanning, strspn() accepted-prefix scanning, strcspn() rejected-byte scanning, strnchr() "
            "count-limited scanning, strnlen() count-clamped length, and strnchrNul() or strnchrnul() "
            "match-or-NUL boundary behavior remain owned by the helper-local anchors"
        ),
        "next_safe_step_note": (
            "If this helper lane reopens, keep the helper-local sysfs review anchors aligned across "
            "the string review packet and this lane note unless dedicated shared sysfs fixture keys "
            "land; do not reopen missing closure-side validator names by default."
        ),
    },
}

DELEGATED_CHECKERS = (
    (
        BITMAP_DIRECT_ANCHOR_CHECKER_REL,
        "bitmap_direct_anchor_checker",
        "PHASE1_BITMAP_DIRECT_ANCHORS=pass",
        "PHASE1_BITMAP_DIRECT_ANCHOR_CHECKER=pass",
    ),
    (
        FIND_BIT_REVIEW_CHECKER_REL,
        "find_bit_review_checker",
        "phase1-find-bit-review-packet:ok",
        "PHASE1_FIND_BIT_REVIEW_CHECKER=pass",
    ),
    (
        RBTREE_DIRECT_ANCHOR_CHECKER_REL,
        "rbtree_direct_anchor_checker",
        "PHASE1_RBTREE_DIRECT_ANCHORS=pass",
        "PHASE1_RBTREE_DIRECT_ANCHOR_CHECKER=pass",
    ),
    (
        RBTREE_REVIEW_CHECKER_REL,
        "rbtree_review_checker",
        "phase1-rbtree-review-packet:ok",
        "PHASE1_RBTREE_REVIEW_CHECKER=pass",
    ),
    (
        STRING_REVIEW_CHECKER_REL,
        "string_review_checker",
        "phase1-string-review-packet:ok",
        "PHASE1_STRING_REVIEW_CHECKER=pass",
    ),
)


def repo_root(root_arg: str | None) -> Path:
    return Path(root_arg).resolve() if root_arg else DEFAULT_ROOT.resolve()


def load_json_with_duplicate_tracking(text: str) -> object:
    return json.loads(text, object_pairs_hook=DuplicateTrackingDict)


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


def load_manifest(root: Path) -> dict:
    data = load_json_with_duplicate_tracking((root / MANIFEST_REL).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"expected manifest dict, got {type(data).__name__}")
    return data


def write_manifest(root: Path, manifest: dict) -> None:
    path = root / MANIFEST_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def write_checker(root: Path, script_rel: Path, text: str) -> None:
    path = root / script_rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_stub_checkers(root: Path) -> None:
    for script_rel, _, success_stdout, _ in DELEGATED_CHECKERS:
        write_checker(root, script_rel, "#!/usr/bin/env python3\nprint(%r)\n" % success_stdout)


def write_zero_exit_wrong_output_checker(root: Path, script_rel: Path, stdout_line: str) -> None:
    write_checker(root, script_rel, "#!/usr/bin/env python3\nprint(%r)\n" % stdout_line)


def write_failing_checker(root: Path, script_rel: Path, stdout_line: str, stderr_line: str) -> None:
    write_checker(
        root,
        script_rel,
        "#!/usr/bin/env python3\n"
        "import sys\n"
        f"print({stdout_line!r})\n"
        f"print({stderr_line!r}, file=sys.stderr)\n"
        "raise SystemExit(1)\n",
    )


def sample_manifest() -> dict:
    return {
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
        "review_anchors": json.loads(json.dumps(EXPECTED_REVIEW_FIELDS)),
    }


def write_sample_root(root: Path) -> None:
    write_manifest(root, sample_manifest())
    write_stub_checkers(root)


def collect_issues(manifest: dict) -> list[str]:
    issues: list[str] = []
    duplicate_paths = collect_duplicate_json_key_paths(manifest)
    if duplicate_paths:
        return [f"manifest:duplicate_json_key:{path}" for path in duplicate_paths]

    if manifest.get("phase") != "Phase 1":
        issues.append("manifest:phase=Phase 1")
    if manifest.get("status") != "closed":
        issues.append("manifest:status=closed")
    if manifest.get("helper_count") != len(EXPECTED_HELPERS):
        issues.append("manifest:helper_count=13")
    if manifest.get("helpers") != EXPECTED_HELPERS:
        issues.append("manifest:helpers=expected_phase1_helper_list")

    lane = manifest.get("lane_sequencing")
    if not isinstance(lane, dict):
        issues.append("manifest:lane_sequencing=dict")
    else:
        if lane.get("shared_replay_parked_helpers") != EXPECTED_SHARED_REPLAY_PARKED_HELPERS:
            issues.append("manifest:lane_sequencing.shared_replay_parked_helpers")
        if lane.get("direct_anchor_followup_helpers") != EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS:
            issues.append("manifest:lane_sequencing.direct_anchor_followup_helpers")
        if lane.get("rule_summary") != EXPECTED_RULE_SUMMARY:
            issues.append("manifest:lane_sequencing.rule_summary")
        if lane.get("anti_overlap_rule") != EXPECTED_ANTI_OVERLAP_RULE:
            issues.append("manifest:lane_sequencing.anti_overlap_rule")

    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        issues.append("manifest:review_anchors=dict")
        return issues

    for helper, expected_fields in EXPECTED_REVIEW_FIELDS.items():
        actual = review_anchors.get(helper)
        if not isinstance(actual, dict):
            issues.append(f"manifest:missing_review_anchor={helper}")
            continue
        for field, expected in expected_fields.items():
            if actual.get(field) != expected:
                issues.append(f"manifest:review_anchor_value={helper}:{field}")

    return issues


def run_checker(root: Path, script_rel: Path, label: str, success_stdout: str) -> list[str]:
    proc = subprocess.run(
        [sys.executable, str(root / script_rel), "--root", str(root)],
        check=False,
        capture_output=True,
        text=True,
    )
    stdout_lines = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    stderr_lines = [line.strip() for line in proc.stderr.splitlines() if line.strip()]
    if proc.returncode == 0:
        if success_stdout in stdout_lines:
            return []
        issues = [f"{label}:missing_success_stdout:{success_stdout}"]
        issues.extend(f"{label}:stdout:{line}" for line in stdout_lines)
        issues.extend(f"{label}:stderr:{line}" for line in stderr_lines)
        return issues

    issues = [f"{label}:exit={proc.returncode}"]
    issues.extend(f"{label}:stdout:{line}" for line in stdout_lines)
    issues.extend(f"{label}:stderr:{line}" for line in stderr_lines)
    return issues


def insert_duplicate_manifest_line(root: Path, needle: str, duplicate_line: str) -> None:
    manifest_path = root / MANIFEST_REL
    text = manifest_path.read_text(encoding="utf-8")
    manifest_path.write_text(text.replace(needle, duplicate_line + "\n" + needle, 1), encoding="utf-8")


def drift_value(value: object) -> object:
    if isinstance(value, list):
        return value[1:]
    if isinstance(value, int):
        return value + 1
    return f"{value} drift"


def run_self_test() -> None:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_direct_anchor_manifest_gate_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)
        assert collect_issues(load_manifest(root)) == []
        case_count += 1

        manifest = sample_manifest()
        manifest["helper_count"] = 12
        write_manifest(root, manifest)
        assert "manifest:helper_count=13" in collect_issues(load_manifest(root))
        write_sample_root(root)
        case_count += 1

        manifest = sample_manifest()
        manifest["lane_sequencing"]["rule_summary"] = "drift"
        write_manifest(root, manifest)
        assert "manifest:lane_sequencing.rule_summary" in collect_issues(load_manifest(root))
        write_sample_root(root)
        case_count += 1

        manifest = sample_manifest()
        manifest["review_anchors"]["tools/lib/string.zig"]["strcmp_review_summary"] = "drift"
        write_manifest(root, manifest)
        assert "manifest:review_anchor_value=tools/lib/string.zig:strcmp_review_summary" in collect_issues(load_manifest(root))
        write_sample_root(root)
        case_count += 1

        manifest = sample_manifest()
        manifest["review_anchors"]["tools/lib/find_bit.zig"]["andnot_scan_entrypoints"] = ["findFirstAndNotBit"]
        write_manifest(root, manifest)
        assert "manifest:review_anchor_value=tools/lib/find_bit.zig:andnot_scan_entrypoints" in collect_issues(load_manifest(root))
        write_sample_root(root)
        case_count += 1

        insert_duplicate_manifest_line(
            root,
            '    "tools/lib/string.zig": {',
            '    "tools/lib/string.zig": {},',
        )
        assert "manifest:duplicate_json_key:review_anchors.tools/lib/string.zig" in collect_issues(load_manifest(root))
        write_sample_root(root)
        case_count += 1

        write_failing_checker(
            root,
            BITMAP_DIRECT_ANCHOR_CHECKER_REL,
            "PHASE1_BITMAP_DIRECT_ANCHORS=fail",
            "or_window_anchor:expected=1:actual=0",
        )
        assert run_checker(
            root,
            BITMAP_DIRECT_ANCHOR_CHECKER_REL,
            "bitmap_direct_anchor_checker",
            "PHASE1_BITMAP_DIRECT_ANCHORS=pass",
        ) == [
            "bitmap_direct_anchor_checker:exit=1",
            "bitmap_direct_anchor_checker:stdout:PHASE1_BITMAP_DIRECT_ANCHORS=fail",
            "bitmap_direct_anchor_checker:stderr:or_window_anchor:expected=1:actual=0",
        ]
        write_sample_root(root)
        case_count += 1

        write_failing_checker(
            root,
            FIND_BIT_REVIEW_CHECKER_REL,
            "PHASE1_FIND_BIT_REVIEW_PACKET=fail",
            "manifest:tail_inclusive_boundary_next:expected_current_packet",
        )
        assert run_checker(
            root,
            FIND_BIT_REVIEW_CHECKER_REL,
            "find_bit_review_checker",
            "phase1-find-bit-review-packet:ok",
        ) == [
            "find_bit_review_checker:exit=1",
            "find_bit_review_checker:stdout:PHASE1_FIND_BIT_REVIEW_PACKET=fail",
            "find_bit_review_checker:stderr:manifest:tail_inclusive_boundary_next:expected_current_packet",
        ]
        write_sample_root(root)
        case_count += 1

        write_failing_checker(
            root,
            RBTREE_DIRECT_ANCHOR_CHECKER_REL,
            "PHASE1_RBTREE_DIRECT_ANCHORS=fail",
            "cached_root_alias_anchor:expected=1:actual=0",
        )
        assert run_checker(
            root,
            RBTREE_DIRECT_ANCHOR_CHECKER_REL,
            "rbtree_direct_anchor_checker",
            "PHASE1_RBTREE_DIRECT_ANCHORS=pass",
        ) == [
            "rbtree_direct_anchor_checker:exit=1",
            "rbtree_direct_anchor_checker:stdout:PHASE1_RBTREE_DIRECT_ANCHORS=fail",
            "rbtree_direct_anchor_checker:stderr:cached_root_alias_anchor:expected=1:actual=0",
        ]
        write_sample_root(root)
        case_count += 1

        write_failing_checker(
            root,
            RBTREE_REVIEW_CHECKER_REL,
            "PHASE1_RBTREE_REVIEW_PACKET=fail",
            "fixture:rbtree.cached_leftmost_return_serials:expected_current_packet",
        )
        assert run_checker(
            root,
            RBTREE_REVIEW_CHECKER_REL,
            "rbtree_review_checker",
            "phase1-rbtree-review-packet:ok",
        ) == [
            "rbtree_review_checker:exit=1",
            "rbtree_review_checker:stdout:PHASE1_RBTREE_REVIEW_PACKET=fail",
            "rbtree_review_checker:stderr:fixture:rbtree.cached_leftmost_return_serials:expected_current_packet",
        ]
        write_sample_root(root)
        case_count += 1

        write_zero_exit_wrong_output_checker(
            root,
            STRING_REVIEW_CHECKER_REL,
            "phase1-string-review-packet:noop",
        )
        assert run_checker(
            root,
            STRING_REVIEW_CHECKER_REL,
            "string_review_checker",
            "phase1-string-review-packet:ok",
        ) == [
            "string_review_checker:missing_success_stdout:phase1-string-review-packet:ok",
            "string_review_checker:stdout:phase1-string-review-packet:noop",
        ]
        write_sample_root(root)
        case_count += 1

        missing_checker_path = root / STRING_REVIEW_CHECKER_REL
        missing_checker_path.unlink()
        missing_failures = run_checker(
            root,
            STRING_REVIEW_CHECKER_REL,
            "string_review_checker",
            "phase1-string-review-packet:ok",
        )
        assert missing_failures[0] == "string_review_checker:exit=2"
        write_sample_root(root)
        case_count += 1

        missing_bitmap_direct_checker = root / BITMAP_DIRECT_ANCHOR_CHECKER_REL
        missing_bitmap_direct_checker.unlink()
        missing_bitmap_direct_failures = run_checker(
            root,
            BITMAP_DIRECT_ANCHOR_CHECKER_REL,
            "bitmap_direct_anchor_checker",
            "PHASE1_BITMAP_DIRECT_ANCHORS=pass",
        )
        assert missing_bitmap_direct_failures[0] == "bitmap_direct_anchor_checker:exit=2"
        write_sample_root(root)
        case_count += 1

        missing_find_bit_review_checker = root / FIND_BIT_REVIEW_CHECKER_REL
        missing_find_bit_review_checker.unlink()
        missing_find_bit_review_failures = run_checker(
            root,
            FIND_BIT_REVIEW_CHECKER_REL,
            "find_bit_review_checker",
            "phase1-find-bit-review-packet:ok",
        )
        assert missing_find_bit_review_failures[0] == "find_bit_review_checker:exit=2"
        write_sample_root(root)
        case_count += 1

        missing_rbtree_direct_checker = root / RBTREE_DIRECT_ANCHOR_CHECKER_REL
        missing_rbtree_direct_checker.unlink()
        missing_rbtree_direct_failures = run_checker(
            root,
            RBTREE_DIRECT_ANCHOR_CHECKER_REL,
            "rbtree_direct_anchor_checker",
            "PHASE1_RBTREE_DIRECT_ANCHORS=pass",
        )
        assert missing_rbtree_direct_failures[0] == "rbtree_direct_anchor_checker:exit=2"
        write_sample_root(root)
        case_count += 1

        missing_rbtree_review_checker = root / RBTREE_REVIEW_CHECKER_REL
        missing_rbtree_review_checker.unlink()
        missing_rbtree_review_failures = run_checker(
            root,
            RBTREE_REVIEW_CHECKER_REL,
            "rbtree_review_checker",
            "phase1-rbtree-review-packet:ok",
        )
        assert missing_rbtree_review_failures[0] == "rbtree_review_checker:exit=2"
        write_sample_root(root)
        case_count += 1

        (root / MANIFEST_REL).write_text("{\n", encoding="utf-8")
        try:
            load_manifest(root)
        except json.JSONDecodeError:
            pass
        else:
            raise AssertionError("expected invalid JSON decode failure")
        case_count += 1

    print("PHASE1_DIRECT_ANCHOR_MANIFEST_GATE_SELF_TEST=pass")
    print(f"PHASE1_DIRECT_ANCHOR_MANIFEST_GATE_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the Phase 1 direct-anchor helper manifest packet for bitmap, find_bit, rbtree, and string."
    )
    parser.add_argument("--root", help="override the repository root")
    parser.add_argument("--self-test", action="store_true", help="run embedded self-tests")
    parser.add_argument("--write-sample-root", help="write a current-like sample repo root")
    args = parser.parse_args()

    if args.write_sample_root:
        write_sample_root(Path(args.write_sample_root).resolve())
        print("PHASE1_DIRECT_ANCHOR_MANIFEST_GATE_SAMPLE_ROOT=written")
        return 0

    if args.self_test:
        run_self_test()
        return 0

    root = repo_root(args.root)
    try:
        manifest = load_manifest(root)
    except json.JSONDecodeError as exc:
        print("PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=fail")
        print("PHASE1_DIRECT_ANCHOR_MANIFEST_GATE_ISSUES_START")
        print(f"manifest:invalid_json:{exc.msg}:line={exc.lineno}:column={exc.colno}")
        print("PHASE1_DIRECT_ANCHOR_MANIFEST_GATE_ISSUES_END")
        return 1
    except TypeError as exc:
        print("PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=fail")
        print("PHASE1_DIRECT_ANCHOR_MANIFEST_GATE_ISSUES_START")
        print(str(exc))
        print("PHASE1_DIRECT_ANCHOR_MANIFEST_GATE_ISSUES_END")
        return 1

    issues = collect_issues(manifest)
    if not issues:
        for script_rel, label, success_stdout, _ in DELEGATED_CHECKERS:
            issues.extend(run_checker(root, script_rel, label, success_stdout))
    if issues:
        print("PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=fail")
        print("PHASE1_DIRECT_ANCHOR_MANIFEST_GATE_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE1_DIRECT_ANCHOR_MANIFEST_GATE_ISSUES_END")
        return 1

    print("PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=pass")
    print(f"PHASE1_DIRECT_ANCHOR_HELPER_COUNT={len(EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS)}")
    print(f"PHASE1_DIRECT_ANCHOR_REVIEW_FIELD_COUNT={sum(len(fields) for fields in EXPECTED_REVIEW_FIELDS.values())}")
    print(f"PHASE1_DIRECT_ANCHOR_DELEGATED_CHECKER_COUNT={len(DELEGATED_CHECKERS)}")
    for _, _, _, status_line in DELEGATED_CHECKERS:
        print(status_line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())