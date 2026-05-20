#!/usr/bin/env python3
"""Validate the current Phase 1 closure note against the live reminder packet."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
PHASE1_LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
DOCS_ROOT_REL = Path("Documentation/zigux/README.md")
REVIEW_CHECKLIST_REL = Path("Documentation/zigux/review-checklist.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
STRING_REVIEW_CHECKER_REL = Path("scripts/zigux/check-phase1-string-review-packet.py")
DIRECT_OWNER_CHECKER_REL = Path("scripts/zigux/check-phase1-direct-owner-markers.py")
BENCH_CHECKER_REL = Path("scripts/zigux/check-phase1-bench.py")
SHARED_REMINDER_CHECKER_REL = Path("scripts/zigux/check-phase1-shared-reminder-packet.py")
TESTS_README_REL = Path("zigux/tests/README.md")
TESTS_BUILD_REL = Path("zigux/tests/build.zig")
PHASE1_SMOKE_REL = Path("zigux/tests/phase1_host_tools_smoke.zig")
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
BITMAP_HELPER_REL = Path("tools/lib/bitmap.zig")
FIND_BIT_HELPER_REL = Path("tools/lib/find_bit.zig")
RBTREE_HELPER_REL = Path("tools/lib/rbtree.zig")
STRING_HELPER_REL = Path("tools/lib/string.zig")

REQUIRED_FILES = (
    PHASE1_CLOSURE_REL,
    PHASE1_LANE_NOTE_REL,
    DOCS_ROOT_REL,
    REVIEW_CHECKLIST_REL,
    SCRIPTS_README_REL,
    STRING_REVIEW_CHECKER_REL,
    DIRECT_OWNER_CHECKER_REL,
    BENCH_CHECKER_REL,
    SHARED_REMINDER_CHECKER_REL,
    TESTS_README_REL,
    TESTS_BUILD_REL,
    PHASE1_SMOKE_REL,
    WORKFLOW_REL,
    MANIFEST_REL,
    BITMAP_HELPER_REL,
    FIND_BIT_HELPER_REL,
    RBTREE_HELPER_REL,
    STRING_HELPER_REL,
)

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

EXPECTED_RBTREE_REVIEW_ANCHORS = {
    "phase1_helper_replay_anchor": 'test "phase1 host-tools smoke exercises live helper behavior"',
    "parity_fixture_keys": [
        "empty_root",
        "insert_order",
        "reverse_order",
        "replace_order",
        "erase_init_order",
        "postorder_count",
        "erase_init_node_empty",
        "cleared_node_empty",
        "find_found_key",
        "find_missing",
        "find_first_serial",
        "next_match_serials",
        "match_iterator_serials",
        "next_match_terminal_null",
    ],
    "cached_leftmost_fixture_keys": [
        "cached_leftmost_return_serials",
    ],
    "shared_replay_summary": "the committed Phase 1 fixture still carries traversal, detached-node, duplicate-search, and exact cached-leftmost-return witnesses for rbtree, while the current shared host-tools smoke replay now rechecks duplicate-range iteration plus the exact `cached_leftmost_return_serials` cached-root leftmost-return sequence on current master",
    "traversal_replay_keys": [
        "empty_root",
        "insert_order",
        "reverse_order",
        "replace_order",
        "erase_init_order",
        "postorder_count",
        "erase_init_node_empty",
        "cleared_node_empty",
    ],
    "duplicate_search_replay_keys": [
        "find_found_key",
        "find_missing",
        "find_first_serial",
        "next_match_serials",
        "match_iterator_serials",
        "next_match_terminal_null",
    ],
    "cached_root_direct_review_summary": "cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed behavior remain owned by direct helper-local anchors, while the exact `cached_leftmost_return_serials` witness now stays aligned across the helper-local tests, the shared host-tools smoke replay, and the committed fixture",
    "ordered_alias_anchor": 'test "rbtree ordered Linux-style aliases mirror traversal and replacement helpers"',
    "low_level_alias_anchor": 'test "rbtree low-level Linux-style aliases mirror node-state helpers"',
    "duplicate_search_anchors": [
        'test "rbtree findAdd keeps the first duplicate and inserts new keys"',
        'test "rbtree nextMatch walks the duplicate range in order"',
        'test "rbtree matchIterator walks the duplicate range in order"',
    ],
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
    "review_packet_summary": "the current shared host-tools smoke replay keeps duplicate-range iteration and the exact `cached_leftmost_return_serials` cached-root leftmost-return witness visible for rbtree, while the committed Phase 1 fixture still carries the exact traversal, detached-node, duplicate-search, and cached-leftmost-return witnesses; direct helper-local anchors continue to own cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed paths that the shared smoke route does not replay exactly",
    "next_safe_step_note": "If this helper lane reopens, keep the already-landed shared-replay promotion for `cached_leftmost_return_serials` aligned across the committed fixture, shared replay, and direct cached-root anchors; the ordered Linux-style alias proof, dedicated `low_level_alias_anchor`, and the remaining cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed behavior stay owned by direct helper-local anchors until another committed cached-root field lands.",
}

EXPECTED_FIND_BIT_REVIEW_ANCHORS = {
    "helper_test_anchors": [
        'test "find first and next set bits across words, with andnot gaps explicit"',
        'test "find zero bits respects the declared bit count"',
        'test "find and bit returns the first shared set bit"',
        'test "underscore entry points reuse the public helper behavior"',
        'test "single-word next scans honor start masks"',
        'test "single-word first scans clamp to the declared bit window"',
        'test "single-word next scans clamp partial windows before returning nbits"',
        'test "word-boundary next scans start fresh on the next word"',
        'test "zero-bit windows return without reading bitmap words"',
        'test "zero-sized scans ignore populated backing words"',
        'test "next scans past nbits return without reading bitmap words"',
        'test "tail mask ignores set bits beyond nbits"',
        'test "tail mask ignores zero bits beyond nbits"',
        'test "tail mask ignores shared bits beyond nbits"',
        'test "tail-word next set scans skip earlier in-range matches before clamping"',
        'test "clump8 scans align to the containing byte and return its value"',
        'test "clump8 scans keep tail bytes reachable from partial final words"',
        'test "clump8 scans mask tail bits beyond nbits"',
        'test "clump8 scans leave the caller byte untouched when no set bit remains"',
        'test "clump8 zero-bit and past-end windows leave the caller byte untouched"',
        'test "getValue8 reads aligned bytes from bitmap words"',
        'test "head-word boundary scans keep the last in-range bit reachable from an inclusive start"',
        'test "tail-word boundary scans keep the last in-range bit reachable from an inclusive start"',
        'test "find last bit scans backward across words"',
        'test "find last bit ignores storage beyond an exact word boundary"',
        'test "find last bit clamps tail words to nbits"',
        'test "find last bit returns nbits when no set bits remain"',
        'test "tail-word next zero and shared scans skip earlier in-range matches before clamping"',
        'test "low-level underscore aliases mirror the primary find helpers, including andnot"',
        'test "Linux-style aliases mirror the primary find helpers, including andnot"',
    ],
    "same_word_start_masks": 'test "single-word next scans honor start masks"',
    "inclusive_boundary_start": 'test "head-word boundary scans keep the last in-range bit reachable from an inclusive start"',
    "tail_word_inclusive_boundary_anchor": 'test "tail-word boundary scans keep the last in-range bit reachable from an inclusive start"',
    "tail_word_inclusive_boundary_contract": "Direct Zig unit coverage keeps tail-clamped set, zero, and shared-bit scans aligned when the inclusive start lands on the last in-range bit of the final partial word, while later starts still return nbits instead of leaking the out-of-range tail.",
    "zero_bit_window": 'test "zero-bit windows return without reading bitmap words"',
    "zero_sized_short_circuit_anchor": 'test "zero-sized scans ignore populated backing words"',
    "past_nbits_short_circuit": 'test "next scans past nbits return without reading bitmap words"',
    "underscore_alias_anchor": 'test "low-level underscore aliases mirror the primary find helpers, including andnot"',
    "linux_alias_anchor": 'test "Linux-style aliases mirror the primary find helpers, including andnot"',
    "andnot_scan_entrypoints": [
        "findFirstAndNotBit",
        "find_first_andnot_bit",
        "_find_first_andnot_bit",
        "findNextAndNotBit",
        "find_next_andnot_bit",
        "_find_next_andnot_bit",
    ],
    "andnot_scan_entrypoint_contract": "The shipped public, Linux-style, and underscore andnot scan entry points stay owned by the direct find_bit packet instead of being left implicit under generic alias wording.",
    "tail_word_set_skip_anchor": 'test "tail-word next set scans skip earlier in-range matches before clamping"',
    "tail_word_skip_anchor": 'test "tail-word next zero and shared scans skip earlier in-range matches before clamping"',
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
    "review_packet_summary": "shared Phase 1 fixture keys own the exact tail-clamped find_bit replay, while helper-local anchors keep same-word start-mask, head-word and tail-word inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, tail-word set or zero or shared skip, clump8, getValue8(), findLastBit(), underscore-alias, and Linux-style alias behavior review-visible on current master",
    "next_safe_step_note": "If this helper lane reopens, keep find_bit parked unless a fresh reread finds direct-anchor drift inside same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, getValue8(), findLastBit(), underscore-alias, Linux-style alias coverage including the shipped andnot scan entry points, or tail-word skip anchors, or committed tail-clamped replay drift; do not reopen older saved validator cues or neighboring helper families.",
}

EXPECTED_MARKERS = {
    "status": "`PHASE1_STATUS=parked`",
    "restore_state": "`PHASE1_CLOSURE_RESTORE_STATE=docs_plus_validator`",
    "helper_count": "`PHASE1_HELPER_COUNT=13`",
    "reminder_packet": (
        "`PHASE1_CURRENT_REMINDER_PACKET=Documentation/zigux/phase1-closure.md,"
        "Documentation/zigux/phase1-host-helper-lane-sequencing.md,Documentation/zigux/README.md,"
        "Documentation/zigux/review-checklist.md,scripts/zigux/README.md,"
        "scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,"
        "scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py,"
        "scripts/zigux/validate-phase1-closure.py,zigux/tests/README.md,"
        "zigux/tests/build.zig,zigux/tests/phase1_host_tools_smoke.zig,.github/workflows/zigux-bootstrap.yml,"
        "zigux/tests/fixtures/phase1_helper_manifest.json`"
    ),
    "gap_packet": (
        "`PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,"
        "zigux/tests/phase1_helpers.zig,zigux/tests/phase1_bench.zig,"
        "zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/fixtures/phase1_helpers_c_harness.c`"
    ),
    "closure_validator": "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
    "shared_tests_route": "`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    "validator_state": "`PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`",
    "next_step": (
        "`PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface or one helper-family tie-breaker "
        "against the restored closure note, the closure validator, the shared tests-root smoke "
        "route, and the helper-specific next_safe_step_note entries in the committed manifest "
        "rather than widening back into the older validator-first or replay-side closure stack.`"
    ),
}

FORBIDDEN_MARKERS = {
    "`PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master`",
    "`PHASE1_NEXT_SAFE_STEP=restore the missing phase1 closure note first`",
}

DELEGATED_CHECKERS = (
    (STRING_REVIEW_CHECKER_REL, "phase1-string-review-packet"),
    (DIRECT_OWNER_CHECKER_REL, "phase1-direct-owner-markers"),
    (BENCH_CHECKER_REL, "phase1-bench"),
    (SHARED_REMINDER_CHECKER_REL, "phase1-shared-reminder-packet"),
)


def repo_root(override: str | None) -> Path:
    return Path(override).resolve() if override else DEFAULT_ROOT


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_exact_occurrence(text: str, label: str, needle: str) -> list[str]:
    count = text.count(needle)
    return [] if count == 1 else [f"{label}:expected_once:actual_count={count}:{needle}"]


def require_exact_value(label: str, actual: object, expected: object) -> list[str]:
    return [] if actual == expected else [f"{label}:expected={expected!r}:actual={actual!r}"]


def require_expected_mapping(prefix: str, actual: object, expected: dict[str, object]) -> list[str]:
    if not isinstance(actual, dict):
        return [f"{prefix}:expected=dict:actual={type(actual).__name__}"]

    failures: list[str] = []
    for key, expected_value in expected.items():
        failures.extend(require_exact_value(f"{prefix}.{key}", actual.get(key), expected_value))
    return failures


def run_checker(root: Path, script_rel: Path, label: str) -> list[str]:
    script_path = root / script_rel
    proc = subprocess.run(
        [sys.executable, str(script_path), "--root", str(root)],
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode == 0:
        return []
    lines = []
    output = (proc.stdout + proc.stderr).splitlines()
    if not output:
        output = [f"{label}:checker_failed:returncode={proc.returncode}"]
    for line in output:
        lines.append(f"delegated:{label}:{line}")
    return lines


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).is_file():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    closure_text = load_text(root, PHASE1_CLOSURE_REL)
    for label, marker in EXPECTED_MARKERS.items():
        failures.extend(
            require_exact_occurrence(closure_text, f"{PHASE1_CLOSURE_REL.as_posix()}:{label}", marker)
        )
    for marker in FORBIDDEN_MARKERS:
        count = closure_text.count(marker)
        if count:
            failures.append(
                f"{PHASE1_CLOSURE_REL.as_posix()}:forbidden_marker:actual_count={count}:{marker}"
            )

    manifest = json.loads(load_text(root, MANIFEST_REL))
    if not isinstance(manifest, dict):
        return [f"{MANIFEST_REL.as_posix()}:expected=dict:actual={type(manifest).__name__}"]

    failures.extend(require_exact_value(f"{MANIFEST_REL.as_posix()}:phase", manifest.get("phase"), "Phase 1"))
    failures.extend(require_exact_value(f"{MANIFEST_REL.as_posix()}:status", manifest.get("status"), "closed"))
    failures.extend(
        require_exact_value(f"{MANIFEST_REL.as_posix()}:helper_count", manifest.get("helper_count"), len(EXPECTED_HELPERS))
    )
    failures.extend(require_exact_value(f"{MANIFEST_REL.as_posix()}:helpers", manifest.get("helpers"), EXPECTED_HELPERS))

    lane_sequencing = manifest.get("lane_sequencing")
    if not isinstance(lane_sequencing, dict):
        failures.append(f"{MANIFEST_REL.as_posix()}:lane_sequencing:expected=dict:actual={type(lane_sequencing).__name__}")
        return failures
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

    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        failures.append(f"{MANIFEST_REL.as_posix()}:review_anchors:expected=dict:actual={type(review_anchors).__name__}")
        return failures
    for helper in ("tools/lib/bitmap.zig", "tools/lib/find_bit.zig", "tools/lib/rbtree.zig", "tools/lib/string.zig"):
        if not isinstance(review_anchors.get(helper), dict):
            failures.append(f"{MANIFEST_REL.as_posix()}:review_anchors.{helper}:expected=dict")

    failures.extend(
        require_expected_mapping(
            f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib.find_bit.zig",
            review_anchors.get("tools/lib/find_bit.zig"),
            EXPECTED_FIND_BIT_REVIEW_ANCHORS,
        )
    )
    failures.extend(
        require_expected_mapping(
            f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib.rbtree.zig",
            review_anchors.get("tools/lib/rbtree.zig"),
            EXPECTED_RBTREE_REVIEW_ANCHORS,
        )
    )

    for script_rel, label in DELEGATED_CHECKERS:
        failures.extend(run_checker(root, script_rel, label))

    return failures


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_checker_stub(path: Path, ok: bool = True) -> None:
    marker = "stub:ok" if ok else "stub:failure"
    body = (
        "#!/usr/bin/env python3\n"
        "import sys\n"
        "if '--root' in sys.argv:\n"
        "    pass\n"
        f"print({marker!r})\n"
        f"raise SystemExit({0 if ok else 1})\n"
    )
    write_text(path, body)


def make_fixture_tree(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        write_text(root / relative_path, f"fixture for {relative_path.as_posix()}\n")

    write_text(
        root / PHASE1_CLOSURE_REL,
        "\n".join(
            [
                "# Phase 1 Closure",
                "",
                EXPECTED_MARKERS["status"],
                EXPECTED_MARKERS["restore_state"],
                EXPECTED_MARKERS["helper_count"],
                EXPECTED_MARKERS["reminder_packet"],
                EXPECTED_MARKERS["gap_packet"],
                EXPECTED_MARKERS["closure_validator"],
                EXPECTED_MARKERS["shared_tests_route"],
                EXPECTED_MARKERS["validator_state"],
                EXPECTED_MARKERS["next_step"],
                "",
            ]
        ),
    )

    write_text(
        root / MANIFEST_REL,
        json.dumps(
            {
                "phase": "Phase 1",
                "status": "closed",
                "helper_count": len(EXPECTED_HELPERS),
                "helpers": EXPECTED_HELPERS,
                "lane_sequencing": {
                    "shared_replay_parked_helpers": EXPECTED_SHARED_REPLAY_PARKED_HELPERS,
                    "direct_anchor_followup_helpers": EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS,
                },
                "review_anchors": {
                    "tools/lib/bitmap.zig": {},
                    "tools/lib/find_bit.zig": EXPECTED_FIND_BIT_REVIEW_ANCHORS,
                    "tools/lib/rbtree.zig": EXPECTED_RBTREE_REVIEW_ANCHORS,
                    "tools/lib/string.zig": {},
                },
            },
            indent=2,
        )
        + "\n",
    )

    make_checker_stub(root / STRING_REVIEW_CHECKER_REL)
    make_checker_stub(root / DIRECT_OWNER_CHECKER_REL)
    make_checker_stub(root / BENCH_CHECKER_REL)
    make_checker_stub(root / SHARED_REMINDER_CHECKER_REL)


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise ValueError(f"missing expected marker: {old}")
    return text.replace(old, new, 1)


def run_self_test() -> int:
    cases = [
        ("baseline", None),
        (
            "missing_restore_state",
            lambda root: write_text(
                root / PHASE1_CLOSURE_REL,
                replace_once(load_text(root, PHASE1_CLOSURE_REL), EXPECTED_MARKERS["restore_state"], "`PHASE1_CLOSURE_RESTORE_STATE=docs_only`"),
            ),
        ),
        (
            "old_next_step_marker",
            lambda root: write_text(
                root / PHASE1_CLOSURE_REL,
                replace_once(
                    load_text(root, PHASE1_CLOSURE_REL),
                    EXPECTED_MARKERS["next_step"],
                    "`PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface against the restored closure note and closure validator`",
                ),
            ),
        ),
        (
            "bad_helper_count",
            lambda root: write_text(
                root / MANIFEST_REL,
                json.dumps({**json.loads(load_text(root, MANIFEST_REL)), "helper_count": 99}, indent=2) + "\n",
            ),
        ),
        (
            "missing_find_bit_andnot_contract",
            lambda root: write_text(
                root / MANIFEST_REL,
                json.dumps(
                    {
                        **json.loads(load_text(root, MANIFEST_REL)),
                        "review_anchors": {
                            **json.loads(load_text(root, MANIFEST_REL))["review_anchors"],
                            "tools/lib/find_bit.zig": {
                                key: value
                                for key, value in json.loads(load_text(root, MANIFEST_REL))["review_anchors"]["tools/lib/find_bit.zig"].items()
                                if key != "andnot_scan_entrypoint_contract"
                            },
                        },
                    },
                    indent=2,
                )
                + "\n",
            ),
        ),
        (
            "stale_find_bit_review_summary",
            lambda root: write_text(
                root / MANIFEST_REL,
                json.dumps(
                    {
                        **json.loads(load_text(root, MANIFEST_REL)),
                        "review_anchors": {
                            **json.loads(load_text(root, MANIFEST_REL))["review_anchors"],
                            "tools/lib/find_bit.zig": {
                                **json.loads(load_text(root, MANIFEST_REL))["review_anchors"]["tools/lib/find_bit.zig"],
                                "review_packet_summary": "older find_bit review summary",
                            },
                        },
                    },
                    indent=2,
                )
                + "\n",
            ),
        ),
        (
            "missing_rbtree_cached_root_alias_anchor",
            lambda root: write_text(
                root / MANIFEST_REL,
                json.dumps(
                    {
                        **json.loads(load_text(root, MANIFEST_REL)),
                        "review_anchors": {
                            **json.loads(load_text(root, MANIFEST_REL))["review_anchors"],
                            "tools/lib/rbtree.zig": {
                                key: value
                                for key, value in json.loads(load_text(root, MANIFEST_REL))["review_anchors"]["tools/lib/rbtree.zig"].items()
                                if key != "cached_root_alias_anchor"
                            },
                        },
                    },
                    indent=2,
                )
                + "\n",
            ),
        ),
        (
            "stale_rbtree_shared_replay_summary",
            lambda root: write_text(
                root / MANIFEST_REL,
                json.dumps(
                    {
                        **json.loads(load_text(root, MANIFEST_REL)),
                        "review_anchors": {
                            **json.loads(load_text(root, MANIFEST_REL))["review_anchors"],
                            "tools/lib/rbtree.zig": {
                                **json.loads(load_text(root, MANIFEST_REL))["review_anchors"]["tools/lib/rbtree.zig"],
                                "shared_replay_summary": "older rbtree replay summary",
                            },
                        },
                    },
                    indent=2,
                )
                + "\n",
            ),
        ),
        (
            "missing_string_checker",
            lambda root: (root / STRING_REVIEW_CHECKER_REL).unlink(),
        ),
        (
            "failing_direct_owner_checker",
            lambda root: make_checker_stub(root / DIRECT_OWNER_CHECKER_REL, ok=False),
        ),
        (
            "missing_bench_checker",
            lambda root: (root / BENCH_CHECKER_REL).unlink(),
        ),
        (
            "failing_bench_checker",
            lambda root: make_checker_stub(root / BENCH_CHECKER_REL, ok=False),
        ),
        (
            "missing_shared_reminder_checker",
            lambda root: (root / SHARED_REMINDER_CHECKER_REL).unlink(),
        ),
        (
            "failing_shared_reminder_checker",
            lambda root: make_checker_stub(root / SHARED_REMINDER_CHECKER_REL, ok=False),
        ),
        (
            "forbidden_old_marker",
            lambda root: write_text(
                root / PHASE1_CLOSURE_REL,
                load_text(root, PHASE1_CLOSURE_REL) + "`PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master`\n",
            ),
        ),
    ]

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-closure-selftest-") as tmp:
            root = Path(tmp)
            make_fixture_tree(root)
            if mutate is not None:
                mutate(root)
            failures = collect_failures(root)
            if name == "baseline":
                if failures:
                    print(f"phase1-closure-self-test:{name}:unexpected={failures}")
                    return 1
            elif not failures:
                print(f"phase1-closure-self-test:{name}:expected_failure")
                return 1

    print("PHASE1_CLOSURE_SELF_TEST=pass")
    print(f"PHASE1_CLOSURE_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run validator self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_CLOSURE_VALIDATION=pass")
    print("PHASE1_CLOSURE_MODE=current-master-safe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
