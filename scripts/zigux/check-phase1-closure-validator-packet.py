#!/usr/bin/env python3
"""Guard the current Phase 1 closure-validator packet against reminder-surface drift."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
PHASE1_LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
VALIDATOR_REL = Path("scripts/zigux/validate-phase1-closure.py")
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")

REQUIRED_FILES = (
    PHASE1_CLOSURE_REL,
    PHASE1_LANE_NOTE_REL,
    SCRIPTS_README_REL,
    VALIDATOR_REL,
    WORKFLOW_REL,
    MANIFEST_REL,
)

EXPECTED_CLOSURE_MARKERS = (
    "`PHASE1_STATUS=parked`",
    "`PHASE1_CLOSURE_RESTORE_STATE=docs_plus_validator`",
    "`PHASE1_FIND_BIT_REVIEW_GUARD=python3 scripts/zigux/check-phase1-find-bit-review-packet.py exact-checks helper-local find_bit anchors plus the committed tail-clamped and tail-inclusive-boundary replay packet across the helper, closure note, lane note, manifest, and fixture`",
    "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
    "`PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`",
    "`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    "`PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`",
    "`PHASE1_FIND_BIT_BENCH_GUARD=scripts/zigux/check-phase1-bench.py still hard-codes PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS=20000 and PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS=20000 and still requires PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM and PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM when the broader expectations packet returns`",
    "`PHASE1_RBTREE_BENCH_GUARD=scripts/zigux/check-phase1-bench.py now hard-codes PHASE1_BENCH_RBTREE_ITERATIONS=4000 and exact-checks PHASE1_BENCH_RBTREE_CHECKSUM, PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM, PHASE1_BENCH_FIND_ADD_CHECKSUM, PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM, and PHASE1_BENCH_RBTREE_CACHED_CHECKSUM when the broader expectations packet returns`",
    "`PHASE1_FIND_BIT_BENCH_ANCHOR_GUARD=python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py exact-checks inclusive-boundary, past-nbits no-read, clump8 past-end no-read, and findLastBit tail-clamp anchors directly in tools/lib/find_bit.zig`",
    "`PHASE1_BITMAP_DIRECT_REVIEW=helper-local bitmap direct anchors stay explicit through the closure packet because the shared Phase 1 replay still only owns allocator sizing, zero-filled allocation words, scnprintf output, truncation, tiny-buffer handling, and partial-window xor replay, so current master keeps fill-tail clamp, raw copy alias, tail-clearing and extension semantics, zero and aligned copyAndExtend handling, zero-sized destination-view no-op coverage, zero-bit logical short-circuit coverage, exact-word-boundary equality fast-path masking, tail-masked predicate behavior, caller-window xor and or clamping, multiword-tail xor and or clamp witnesses, weighted tail-count clamping, complement-tail masking, terminator-only and zero-length caller-view formatting, empty-bitmap caller-buffer preservation, Linux-style alias mirror coverage, and allocator optional-reset coverage review-visible at the helper surface`",
    "`PHASE1_STRING_SYSFS_REVIEW=helper-local string sysfs newline-aware equality and lookup-order anchors stay explicit through the direct string tests and the Phase 1 helper manifest because the shared Phase 1 replay still carries no dedicated sysfs fixture keys`",
    "`PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface or one helper-family tie-breaker against the restored closure note, the closure validator, the shared tests-root smoke route, and the helper-specific next_safe_step_note entries in the committed manifest rather than widening back into the older validator-first or replay-side closure stack.`",
)

OPTIONAL_RBTREE_DIRECT_ANCHOR_CLOSURE_MARKER = (
    "`PHASE1_RBTREE_DIRECT_ANCHOR_GUARD=python3 "
    "scripts/zigux/check-phase1-rbtree-direct-anchors.py exact-checks ordered Linux-style alias, "
    "low-level alias, and cached-root insert-miss, leftmost-sync, alias, replacement, "
    "singleton-erase, detach, reseed, and direct entry-point anchors directly in "
    "tools/lib/rbtree.zig`"
)

EXPECTED_VALIDATOR_MARKERS = (
    'PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")',
    'PHASE1_LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")',
    'SCRIPTS_README_REL = Path("scripts/zigux/README.md")',
    'STRING_REVIEW_CHECKER_REL = Path("scripts/zigux/check-phase1-string-review-packet.py")',
    'FIND_BIT_REVIEW_CHECKER_REL = Path("scripts/zigux/check-phase1-find-bit-review-packet.py")',
    'RBTREE_REVIEW_CHECKER_REL = Path("scripts/zigux/check-phase1-rbtree-review-packet.py")',
    'DIRECT_OWNER_CHECKER_REL = Path("scripts/zigux/check-phase1-direct-owner-markers.py")',
    'ROUTE_SUMMARY_CHECKER_REL = Path("scripts/zigux/check-phase1-route-summary-counts.py")',
    'BENCH_CHECKER_REL = Path("scripts/zigux/check-phase1-bench.py")',
    'FIND_BIT_BENCH_ANCHOR_CHECKER_REL = Path("scripts/zigux/check-phase1-find-bit-bench-anchors.py")',
    'BITMAP_DIRECT_ANCHOR_CHECKER_REL = Path("scripts/zigux/check-phase1-bitmap-direct-anchors.py")',
    'SHARED_REMINDER_CHECKER_REL = Path("scripts/zigux/check-phase1-shared-reminder-packet.py")',
    'WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")',
    'MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")',
    '"find_bit_review_guard": "`PHASE1_FIND_BIT_REVIEW_GUARD=python3 scripts/zigux/check-phase1-find-bit-review-packet.py exact-checks helper-local find_bit anchors plus the committed tail-clamped and tail-inclusive-boundary replay packet across the helper, closure note, lane note, manifest, and fixture`",',
    '"closure_validator": "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",',
    '"route_summary_guard": "`PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`",',
    '"shared_tests_route": "`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",',
    '"validator_state": "`PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`",',
    '"find_bit_bench_guard": "`PHASE1_FIND_BIT_BENCH_GUARD=scripts/zigux/check-phase1-bench.py still hard-codes PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS=20000 and PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS=20000 and still requires PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM and PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM when the broader expectations packet returns`",',
    '"rbtree_bench_guard": "`PHASE1_RBTREE_BENCH_GUARD=scripts/zigux/check-phase1-bench.py now hard-codes PHASE1_BENCH_RBTREE_ITERATIONS=4000 and exact-checks PHASE1_BENCH_RBTREE_CHECKSUM, PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM, PHASE1_BENCH_FIND_ADD_CHECKSUM, PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM, and PHASE1_BENCH_RBTREE_CACHED_CHECKSUM when the broader expectations packet returns`",',
    '"find_bit_bench_anchor_guard": "`PHASE1_FIND_BIT_BENCH_ANCHOR_GUARD=python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py exact-checks inclusive-boundary, past-nbits no-read, clump8 past-end no-read, and findLastBit tail-clamp anchors directly in tools/lib/find_bit.zig`",',
    '"bitmap_direct_review": "`PHASE1_BITMAP_DIRECT_REVIEW=helper-local bitmap direct anchors stay explicit through the closure packet because the shared Phase 1 replay still only owns allocator sizing, zero-filled allocation words, scnprintf output, truncation, tiny-buffer handling, and partial-window xor replay, so current master keeps fill-tail clamp, raw copy alias, tail-clearing and extension semantics, zero and aligned copyAndExtend handling, zero-sized destination-view no-op coverage, zero-bit logical short-circuit coverage, exact-word-boundary equality fast-path masking, tail-masked predicate behavior, caller-window xor and or clamping, multiword-tail xor and or clamp witnesses, weighted tail-count clamping, complement-tail masking, terminator-only and zero-length caller-view formatting, empty-bitmap caller-buffer preservation, Linux-style alias mirror coverage, and allocator optional-reset coverage review-visible at the helper surface`",',
    '"string_sysfs_review": "`PHASE1_STRING_SYSFS_REVIEW=helper-local string sysfs newline-aware equality and lookup-order anchors stay explicit through the direct string tests and the Phase 1 helper manifest because the shared Phase 1 replay still carries no dedicated sysfs fixture keys`",',
    '"next_step": "`PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface or one helper-family tie-breaker against the restored closure note, the closure validator, the shared tests-root smoke route, and the helper-specific next_safe_step_note entries in the committed manifest rather than widening back into the older validator-first or replay-side closure stack.`",',
    '(STRING_REVIEW_CHECKER_REL, "phase1-string-review-packet"),',
    '(FIND_BIT_REVIEW_CHECKER_REL, "phase1-find-bit-review-packet"),',
    '(RBTREE_REVIEW_CHECKER_REL, "phase1-rbtree-review-packet"),',
    '(DIRECT_OWNER_CHECKER_REL, "phase1-direct-owner-markers"),',
    '(ROUTE_SUMMARY_CHECKER_REL, "phase1-route-summary-counts"),',
    '(BENCH_CHECKER_REL, "phase1-bench"),',
    '(FIND_BIT_BENCH_ANCHOR_CHECKER_REL, "phase1-find-bit-bench-anchors"),',
    '(BITMAP_DIRECT_ANCHOR_CHECKER_REL, "phase1-bitmap-direct-anchors"),',
    '(SHARED_REMINDER_CHECKER_REL, "phase1-shared-reminder-packet"),',
)

OPTIONAL_RBTREE_DIRECT_ANCHOR_VALIDATOR_MARKERS = (
    'RBTREE_DIRECT_ANCHOR_CHECKER_REL = Path("scripts/zigux/check-phase1-rbtree-direct-anchors.py")',
    '"rbtree_direct_anchor_guard": "`PHASE1_RBTREE_DIRECT_ANCHOR_GUARD=python3 scripts/zigux/check-phase1-rbtree-direct-anchors.py exact-checks ordered Linux-style alias, low-level alias, and cached-root insert-miss, leftmost-sync, alias, replacement, singleton-erase, detach, reseed, and direct entry-point anchors directly in tools/lib/rbtree.zig`",',
    '(RBTREE_DIRECT_ANCHOR_CHECKER_REL, "phase1-rbtree-direct-anchors"),',
)

EXPECTED_README_MARKERS = (
    "- `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the shipped bounded Phase 1 reminder checks, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` replays the shipped shared tests-root smoke route",
    "- `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, and `scripts/zigux/validate-phase1-closure.py` keep the shipped string-review, direct-owner, bench, shared-reminder, and closure-validator packet explicit from the scripts root",
    "- `scripts/zigux/check-phase1-route-summary-counts.py`, `make -C zigux phase1-route-summary`, and `.github/workflows/zigux-bootstrap.yml` keep the adjacent Phase 1 route-summary guard explicit beside the narrower reminder packet, so scripts-root follow-through can verify the returned non-Phase-1 Makefile route inventory without promoting the older Phase 1 wrappers back into shipped proof",
    "- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `zigux/tests/build.zig`, `zigux/tests/phase1_host_tools_smoke.zig`, and `scripts/zigux/README.md` remain the current reminder-surface companions for that packet",
    "- `Documentation/zigux/phase1-closure.md` and `scripts/zigux/validate-phase1-closure.py` are back on current `master`, so bitmap-side follow-through can use that restored closure packet as live reminder evidence instead of replaying older missing validator-first or make-route names by default",
    "- current `master` does ship `scripts/zigux/check-phase1-bench.py`, and `.github/workflows/zigux-bootstrap.yml` self-tests it, so keep the remaining shared reminder follow-through focused on the broader docs-root, checklist, and tests-root bench wording instead of treating the bench checker itself as a repo-reality gap here",
)

EXPECTED_WORKFLOW_MARKERS = (
    "- name: Self-test current Phase 1 direct-owner checker",
    "run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
    "- name: Check current Phase 1 direct-owner markers",
    "- name: Self-test current Phase 1 direct-anchor manifest gate",
    "run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py --self-test",
    "- name: Check current Phase 1 direct-anchor manifest gate",
    "- name: Self-test current Phase 1 string review checker",
    "- name: Self-test current Phase 1 find-bit review checker",
    "- name: Self-test current Phase 1 route summary checker",
    "- name: Self-test current Phase 1 bench checker",
    "- name: Self-test current Phase 1 find-bit bench anchor checker",
    "- name: Self-test current Phase 1 shared reminder checker",
    "- name: Self-test current Phase 1 closure validator",
    "- name: Check current Phase 1 closure packet",
    "run: python3 scripts/zigux/validate-phase1-closure.py",
    "- name: Run current Phase 1 shared tests-root smoke",
    "run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
)

EXPECTED_LANE_NOTE_MARKERS = (
    "`PHASE1_DIRECT_OWNER_SHARED_REMINDER_GAPS=the shared reminder packet now keeps scripts/zigux/check-phase1-bench.py explicit across Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, zigux/tests/README.md, and scripts/zigux/README.md, while the older installer-backed, validator-first, bench-route, and replay names stay historical packet members until they reread cleanly on current master`",
    "`PHASE1_DIRECT_OWNER_SHARED_REMINDER_ACTIVE_PACKET=Documentation/zigux/README.md,Documentation/zigux/phase1-closure.md,Documentation/zigux/review-checklist.md,zigux/tests/README.md,scripts/zigux/README.md,scripts/zigux/validate-phase1-closure.py,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py`",
    "`PHASE1_DIRECT_OWNER_SHARED_REMINDER_ROUTE_SPLIT=Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, zigux/tests/README.md, and scripts/zigux/README.md now all carry the shipped bench-checker wording, while Documentation/zigux/phase1-closure.md plus scripts/zigux/validate-phase1-closure.py keep the restored closure-side packet explicit and the broader installer-backed, validator-first, bench-route, and replay names remain historical packet members until direct current-master rereads restore them`",
    "`PHASE1_RBTREE_DIRECT_OWNER=rbtree keeps ordered Linux-style alias, low-level Linux-style alias, cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed anchors helper-local while the committed fixture still owns exact find(), findFirst(), nextMatch(), and matchIterator() duplicate-search fields and the shared host-tools smoke route keeps duplicate-range iteration plus the parked cached_leftmost_return_serials witness explicit`",
    "`PHASE1_DIRECT_OWNER_SHARED_REMINDER_NEXT_STEP=leave the shared bench-checker wording and shared-reminder checker packet parked unless a fresh reread finds drift across Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, zigux/tests/README.md, scripts/zigux/README.md, Documentation/zigux/phase1-closure.md, scripts/zigux/validate-phase1-closure.py, scripts/zigux/check-phase1-bench.py, or scripts/zigux/check-phase1-shared-reminder-packet.py; otherwise prefer the smaller helper-specific next-safe-step markers below before reopening any shared reminder surface`",
)

FORBIDDEN_MARKERS = (
    "`PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master`",
    "`PHASE1_NEXT_SAFE_STEP=restore the missing phase1 closure note first`",
    "`PHASE1_DIRECT_OWNER_SHARED_REMINDER_GAPS=none`",
)


def repo_root(root_arg: str | None) -> Path:
    return Path(root_arg).resolve() if root_arg else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_once(text: str, label: str, needle: str) -> list[str]:
    count = text.count(needle)
    return [] if count == 1 else [f"{label}:expected_once:actual_count={count}:{needle}"]


def require_absent(text: str, label: str, needle: str) -> list[str]:
    count = text.count(needle)
    return [] if count == 0 else [f"{label}:forbidden_marker:actual_count={count}:{needle}"]


def optional_marker_state(text: str, label: str, needle: str) -> tuple[bool, list[str]]:
    count = text.count(needle)
    if count > 1:
        return False, [f"{label}:expected_at_most_once:actual_count={count}:{needle}"]
    return count == 1, []


def require_optional_packet_coherence(
    closure_text: str,
    validator_text: str,
) -> list[str]:
    failures: list[str] = []

    closure_present, closure_failures = optional_marker_state(
        closure_text,
        PHASE1_CLOSURE_REL.as_posix(),
        OPTIONAL_RBTREE_DIRECT_ANCHOR_CLOSURE_MARKER,
    )
    failures.extend(closure_failures)

    validator_present = True
    for marker in OPTIONAL_RBTREE_DIRECT_ANCHOR_VALIDATOR_MARKERS:
        present, marker_failures = optional_marker_state(
            validator_text,
            VALIDATOR_REL.as_posix(),
            marker,
        )
        failures.extend(marker_failures)
        validator_present = validator_present and present

    validator_any_present = any(
        validator_text.count(marker) == 1 for marker in OPTIONAL_RBTREE_DIRECT_ANCHOR_VALIDATOR_MARKERS
    )

    if validator_any_present and not validator_present:
        failures.append(
            f"{VALIDATOR_REL.as_posix()}:optional_rbtree_direct_anchor_packet:partial_validator_packet"
        )

    if closure_present != validator_present:
        failures.append(
            "phase1-closure-validator-packet:optional_rbtree_direct_anchor_packet:"
            f"closure_present={closure_present}:validator_present={validator_present}"
        )

    return failures


def collect_failures(root: Path) -> list[str]:
    failures = [f"missing_file:{path.as_posix()}" for path in REQUIRED_FILES if not (root / path).is_file()]
    if failures:
        return failures

    closure_text = load_text(root, PHASE1_CLOSURE_REL)
    validator_text = load_text(root, VALIDATOR_REL)
    readme_text = load_text(root, SCRIPTS_README_REL)
    workflow_text = load_text(root, WORKFLOW_REL)
    lane_note_text = load_text(root, PHASE1_LANE_NOTE_REL)

    for marker in EXPECTED_CLOSURE_MARKERS:
        failures.extend(require_once(closure_text, PHASE1_CLOSURE_REL.as_posix(), marker))
    for marker in EXPECTED_VALIDATOR_MARKERS:
        failures.extend(require_once(validator_text, VALIDATOR_REL.as_posix(), marker))
    failures.extend(require_optional_packet_coherence(closure_text, validator_text))
    for marker in EXPECTED_README_MARKERS:
        failures.extend(require_once(readme_text, SCRIPTS_README_REL.as_posix(), marker))
    for marker in EXPECTED_WORKFLOW_MARKERS:
        failures.extend(require_once(workflow_text, WORKFLOW_REL.as_posix(), marker))
    for marker in EXPECTED_LANE_NOTE_MARKERS:
        failures.extend(require_once(lane_note_text, PHASE1_LANE_NOTE_REL.as_posix(), marker))
    for marker in FORBIDDEN_MARKERS:
        failures.extend(require_absent(closure_text, PHASE1_CLOSURE_REL.as_posix(), marker))
        failures.extend(require_absent(readme_text, SCRIPTS_README_REL.as_posix(), marker))
        failures.extend(require_absent(lane_note_text, PHASE1_LANE_NOTE_REL.as_posix(), marker))

    return failures


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_sample_root(root: Path, include_optional_rbtree_direct_anchor: bool = False) -> None:
    closure_markers = list(EXPECTED_CLOSURE_MARKERS)
    validator_markers = list(EXPECTED_VALIDATOR_MARKERS)
    if include_optional_rbtree_direct_anchor:
        closure_markers.insert(9, OPTIONAL_RBTREE_DIRECT_ANCHOR_CLOSURE_MARKER)
        validator_markers.extend(OPTIONAL_RBTREE_DIRECT_ANCHOR_VALIDATOR_MARKERS)

    write_text(root / PHASE1_CLOSURE_REL, "# Phase 1 Closure\n\n" + "\n".join(closure_markers) + "\n")
    write_text(root / VALIDATOR_REL, "\n".join(validator_markers) + "\n")
    write_text(root / SCRIPTS_README_REL, "# scripts/zigux\n\n## Phase 1\n\n" + "\n".join(EXPECTED_README_MARKERS) + "\n")
    write_text(root / WORKFLOW_REL, "jobs:\n  bootstrap:\n    steps:\n" + "\n".join(f"      {marker}" for marker in EXPECTED_WORKFLOW_MARKERS) + "\n")
    write_text(root / PHASE1_LANE_NOTE_REL, "# Phase 1 Host-Helper Lane Sequencing\n\n" + "\n".join(EXPECTED_LANE_NOTE_MARKERS) + "\n")
    write_text(root / MANIFEST_REL, '{\n  "phase": "Phase 1"\n}\n')


def run_self_test() -> int:
    cases: list[tuple[str, object | None]] = [
        ("baseline", None),
        ("expanded_rbtree_direct_anchor_packet", lambda root: write_sample_root(root, include_optional_rbtree_direct_anchor=True)),
        ("missing_closure_status", lambda root: write_text(root / PHASE1_CLOSURE_REL, load_text(root, PHASE1_CLOSURE_REL).replace(EXPECTED_CLOSURE_MARKERS[0] + "\n", "", 1))),
        ("missing_find_bit_review_guard", lambda root: write_text(root / PHASE1_CLOSURE_REL, load_text(root, PHASE1_CLOSURE_REL).replace(EXPECTED_CLOSURE_MARKERS[2] + "\n", "", 1))),
        ("missing_bitmap_direct_review", lambda root: write_text(root / PHASE1_CLOSURE_REL, load_text(root, PHASE1_CLOSURE_REL).replace(EXPECTED_CLOSURE_MARKERS[10] + "\n", "", 1))),
        ("closure_only_optional_rbtree_direct_anchor", lambda root: write_text(root / PHASE1_CLOSURE_REL, load_text(root, PHASE1_CLOSURE_REL) + OPTIONAL_RBTREE_DIRECT_ANCHOR_CLOSURE_MARKER + "\n")),
        ("validator_only_optional_rbtree_direct_anchor", lambda root: write_text(root / VALIDATOR_REL, load_text(root, VALIDATOR_REL) + "\n".join(OPTIONAL_RBTREE_DIRECT_ANCHOR_VALIDATOR_MARKERS) + "\n")),
        ("partial_validator_optional_rbtree_direct_anchor", lambda root: write_text(root / VALIDATOR_REL, load_text(root, VALIDATOR_REL) + OPTIONAL_RBTREE_DIRECT_ANCHOR_VALIDATOR_MARKERS[0] + "\n")),
        ("missing_validator_delegate", lambda root: write_text(root / VALIDATOR_REL, load_text(root, VALIDATOR_REL).replace(EXPECTED_VALIDATOR_MARKERS[26] + "\n", "", 1))),
        ("missing_validator_next_step", lambda root: write_text(root / VALIDATOR_REL, load_text(root, VALIDATOR_REL).replace(EXPECTED_VALIDATOR_MARKERS[24] + "\n", "", 1))),
        ("missing_readme_validator_line", lambda root: write_text(root / SCRIPTS_README_REL, load_text(root, SCRIPTS_README_REL).replace(EXPECTED_README_MARKERS[1] + "\n", "", 1))),
        ("missing_readme_restored_closure_line", lambda root: write_text(root / SCRIPTS_README_REL, load_text(root, SCRIPTS_README_REL).replace(EXPECTED_README_MARKERS[4] + "\n", "", 1))),
        ("missing_workflow_direct_anchor_gate", lambda root: write_text(root / WORKFLOW_REL, load_text(root, WORKFLOW_REL).replace(f"      {EXPECTED_WORKFLOW_MARKERS[4]}\n", "", 1))),
        ("missing_workflow_closure_check", lambda root: write_text(root / WORKFLOW_REL, load_text(root, WORKFLOW_REL).replace(f"      {EXPECTED_WORKFLOW_MARKERS[14]}\n", "", 1))),
        ("missing_lane_active_packet", lambda root: write_text(root / PHASE1_LANE_NOTE_REL, load_text(root, PHASE1_LANE_NOTE_REL).replace(EXPECTED_LANE_NOTE_MARKERS[1] + "\n", "", 1))),
        ("missing_lane_next_step", lambda root: write_text(root / PHASE1_LANE_NOTE_REL, load_text(root, PHASE1_LANE_NOTE_REL).replace(EXPECTED_LANE_NOTE_MARKERS[4] + "\n", "", 1))),
        ("forbidden_old_validator_state", lambda root: write_text(root / PHASE1_CLOSURE_REL, load_text(root, PHASE1_CLOSURE_REL) + FORBIDDEN_MARKERS[0] + "\n")),
        ("forbidden_old_gaps_marker", lambda root: write_text(root / PHASE1_LANE_NOTE_REL, load_text(root, PHASE1_LANE_NOTE_REL) + FORBIDDEN_MARKERS[2] + "\n")),
        ("missing_manifest", lambda root: (root / MANIFEST_REL).unlink()),
    ]

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-closure-validator-packet-") as tmp:
            root = Path(tmp)
            write_sample_root(root)
            if mutate is not None:
                mutate(root)
            failures = collect_failures(root)
            if name in {"baseline", "expanded_rbtree_direct_anchor_packet"}:
                if failures:
                    print(f"phase1-closure-validator-packet-self-test:{name}:unexpected={failures}")
                    return 1
            elif not failures:
                print(f"phase1-closure-validator-packet-self-test:{name}:expected_failure")
                return 1

    print("PHASE1_CLOSURE_VALIDATOR_PACKET_SELF_TEST=pass")
    print(f"PHASE1_CLOSURE_VALIDATOR_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-tests")
    parser.add_argument("--write-sample-root", help="write a current-like sample root")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        destination = Path(args.write_sample_root).resolve()
        write_sample_root(destination)
        print(f"PHASE1_CLOSURE_VALIDATOR_PACKET_SAMPLE_ROOT={destination}")
        return 0

    failures = collect_failures(repo_root(args.root))
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_CLOSURE_VALIDATOR_PACKET=pass")
    print(f"PHASE1_CLOSURE_VALIDATOR_PACKET_REQUIRED_PATH_COUNT={len(REQUIRED_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
