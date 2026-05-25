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
RBTREE_DIRECT_ANCHOR_CHECKER_REL = Path("scripts/zigux/check-phase1-rbtree-direct-anchors.py")


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
            "shared Phase 1 fixture keys now own bitmap allocator sizing, zero-filled allocation words, "
            "scnprintf output, truncation, tiny-buffer, and partial-window xor replay, while current "
            "master keeps the direct helper-local bitmap packet bounded to whole-word range edges, raw "
            "copy alias behavior, tail-clearing and extension semantics, zero and aligned copyAndExtend "
            "handling, zero-sized destination-view no-op coverage, zero-bit logical short-circuit "
            "coverage, exact-word-boundary equality fast-path masking, tail-masked predicate behavior, "
            "out-of-range tail-bit full or empty or weight masking, caller-window xor and or clamping, "
            "multiword-tail xor and or clamp witnesses, weighted tail-count clamping, terminator-only "
            "and zero-length caller-view formatting, empty-bitmap caller-buffer preservation, Linux-style "
            "alias mirror coverage, and allocator optional-reset coverage."
        ),
        "next_safe_step_note": (
            "If this helper lane reopens, keep bitmap parked unless a fresh reread finds new direct-anchor "
            "drift inside the current helper-local packet or committed shared replay drift in the bitmap "
            "parity fields; current master still ships direct fill-tail clamp, copy-alias, truncation, "
            "cross-word scnprintf, exact-word-boundary equality fast-path masking, caller-window xor and "
            "or clamp, weighted tail-count clamp, empty-buffer, allocator-reset, zero-bit logical "
            "short-circuit, and Linux-style alias mirror anchors here; do not reopen older closure-side "
            "or validator-route cue names by default."
        ),
    },
    "tools/lib/find_bit.zig": {
        "helper_test_anchors": [
            'test "clump8 past-end scans return without reading bitmap words"',
            'test "low-level underscore aliases mirror the primary find helpers, including andnot"',
            'test "Linux-style aliases mirror the primary find helpers, including andnot"',
        ],
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


def write_stub_checker(root: Path) -> None:
    path = root / RBTREE_DIRECT_ANCHOR_CHECKER_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "#!/usr/bin/env python3\n"
        "print('PHASE1_RBTREE_DIRECT_ANCHORS=pass')\n",
        encoding="utf-8",
    )


def write_failing_checker(root: Path) -> None:
    path = root / RBTREE_DIRECT_ANCHOR_CHECKER_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "#!/usr/bin/env python3\n"
        "import sys\n"
        "print('PHASE1_RBTREE_DIRECT_ANCHORS=fail')\n"
        "print('cached_root_alias_anchor:expected=1:actual=0', file=sys.stderr)\n"
        "raise SystemExit(1)\n",
        encoding="utf-8",
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
        "review_anchors": EXPECTED_REVIEW_FIELDS,
    }


def write_sample_root(root: Path) -> None:
    write_manifest(root, sample_manifest())
    write_stub_checker(root)


def collect_issues(manifest: dict) -> list[str]:
    issues: list[str] = []

    duplicate_paths = collect_duplicate_json_key_paths(manifest)
    if duplicate_paths:
        issues.extend(f"manifest:duplicate_json_key:{path}" for path in duplicate_paths)
        return issues

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


def run_checker(root: Path, script_rel: Path, label: str) -> list[str]:
    proc = subprocess.run(
        [sys.executable, str(root / script_rel), "--root", str(root)],
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode == 0:
        return []

    issues: list[str] = [f"{label}:exit={proc.returncode}"]
    stdout = proc.stdout.strip()
    stderr = proc.stderr.strip()
    if stdout:
        issues.extend(f"{label}:stdout:{line}" for line in stdout.splitlines())
    if stderr:
        issues.extend(f"{label}:stderr:{line}" for line in stderr.splitlines())
    return issues


def assert_issue_case(root: Path, mutate, expected_issue: str) -> None:
    mutate()
    issues = collect_issues(load_manifest(root))
    assert expected_issue in issues, issues
    write_sample_root(root)


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


def mutate_manifest_path(manifest: dict, path: tuple[str, ...]) -> None:
    current = manifest
    for key in path[:-1]:
        current = current[key]
    final_key = path[-1]
    current[final_key] = drift_value(current[final_key])


def run_self_test() -> None:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_direct_anchor_manifest_gate_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)
        assert collect_issues(load_manifest(root)) == []

        manifest_path = root / MANIFEST_REL

        def load_current() -> dict:
            return json.loads(manifest_path.read_text(encoding="utf-8"))

        top_level_expectations = {
            ("phase",): "manifest:phase=Phase 1",
            ("status",): "manifest:status=closed",
            ("helper_count",): "manifest:helper_count=13",
            ("helpers",): "manifest:helpers=expected_phase1_helper_list",
            ("lane_sequencing", "shared_replay_parked_helpers"): "manifest:lane_sequencing.shared_replay_parked_helpers",
            ("lane_sequencing", "direct_anchor_followup_helpers"): "manifest:lane_sequencing.direct_anchor_followup_helpers",
            ("lane_sequencing", "rule_summary"): "manifest:lane_sequencing.rule_summary",
            ("lane_sequencing", "anti_overlap_rule"): "manifest:lane_sequencing.anti_overlap_rule",
        }

        for path, expected_issue in top_level_expectations.items():
            assert_issue_case(
                root,
                lambda path=path: (
                    lambda manifest: (
                        mutate_manifest_path(manifest, path),
                        write_manifest(root, manifest),
                    )
                )(load_current()),
                expected_issue,
            )
            case_count += 1

        for helper, expected_fields in EXPECTED_REVIEW_FIELDS.items():
            for field in expected_fields:
                assert_issue_case(
                    root,
                    lambda helper=helper, field=field: (
                        lambda manifest: (
                            manifest["review_anchors"][helper].__setitem__(
                                field,
                                drift_value(manifest["review_anchors"][helper][field]),
                            ),
                            write_manifest(root, manifest),
                        )
                    )(load_current()),
                    f"manifest:review_anchor_value={helper}:{field}",
                )
                case_count += 1

        insert_duplicate_manifest_line(
            root,
            '    "tools/lib/string.zig": {',
            '    "tools/lib/string.zig": {},',
        )
        issues = collect_issues(load_manifest(root))
        assert "manifest:duplicate_json_key:review_anchors.tools/lib/string.zig" in issues, issues
        write_sample_root(root)
        case_count += 1

        write_failing_checker(root)
        checker_failures = run_checker(root, RBTREE_DIRECT_ANCHOR_CHECKER_REL, "rbtree_direct_anchor_checker")
        assert checker_failures == [
            "rbtree_direct_anchor_checker:exit=1",
            "rbtree_direct_anchor_checker:stdout:PHASE1_RBTREE_DIRECT_ANCHORS=fail",
            "rbtree_direct_anchor_checker:stderr:cached_root_alias_anchor:expected=1:actual=0",
        ], checker_failures
        write_sample_root(root)
        case_count += 1

        manifest_path.write_text("{\n", encoding="utf-8")
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
        issues.extend(run_checker(root, RBTREE_DIRECT_ANCHOR_CHECKER_REL, "rbtree_direct_anchor_checker"))
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
    print("PHASE1_RBTREE_DIRECT_ANCHOR_CHECKER=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
