#!/usr/bin/env python3
"""Guard the current Phase 1 bootstrap packet across reminder surfaces and workflow order."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

DOCS_ROOT_REL = Path("Documentation/zigux/README.md")
PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
LANE_SEQUENCING_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
REVIEW_CHECKLIST_REL = Path("Documentation/zigux/review-checklist.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
TESTS_README_REL = Path("zigux/tests/README.md")
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
TESTS_BUILD_REL = Path("zigux/tests/build.zig")
PHASE1_SMOKE_REL = Path("zigux/tests/phase1_host_tools_smoke.zig")
PHASE1_MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
MAKEFILE_REL = Path("zigux/Makefile")

STRING_REVIEW_CHECKER_REL = Path("scripts/zigux/check-phase1-string-review-packet.py")
DIRECT_OWNER_CHECKER_REL = Path("scripts/zigux/check-phase1-direct-owner-markers.py")
DIRECT_ANCHOR_MANIFEST_GATE_REL = Path("scripts/zigux/check-phase1-direct-anchor-manifest-gate.py")
ROUTE_SUMMARY_CHECKER_REL = Path("scripts/zigux/check-phase1-route-summary-counts.py")
BENCH_CHECKER_REL = Path("scripts/zigux/check-phase1-bench.py")
SHARED_REMINDER_CHECKER_REL = Path("scripts/zigux/check-phase1-shared-reminder-packet.py")
CLOSURE_VALIDATOR_REL = Path("scripts/zigux/validate-phase1-closure.py")

REQUIRED_FILES = (
    DOCS_ROOT_REL,
    PHASE1_CLOSURE_REL,
    LANE_SEQUENCING_REL,
    REVIEW_CHECKLIST_REL,
    SCRIPTS_README_REL,
    TESTS_README_REL,
    WORKFLOW_REL,
    TESTS_BUILD_REL,
    PHASE1_SMOKE_REL,
    PHASE1_MANIFEST_REL,
    MAKEFILE_REL,
    STRING_REVIEW_CHECKER_REL,
    DIRECT_OWNER_CHECKER_REL,
    DIRECT_ANCHOR_MANIFEST_GATE_REL,
    ROUTE_SUMMARY_CHECKER_REL,
    BENCH_CHECKER_REL,
    SHARED_REMINDER_CHECKER_REL,
    CLOSURE_VALIDATOR_REL,
)

WORKFLOW_PACKET_STEPS = (
    (
        "Self-test current Phase 1 direct-owner checker",
        "python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
    ),
    (
        "Check current Phase 1 direct-owner markers",
        "python3 scripts/zigux/check-phase1-direct-owner-markers.py",
    ),
    (
        "Self-test current Phase 1 direct-anchor manifest gate",
        "python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py --self-test",
    ),
    (
        "Check current Phase 1 direct-anchor manifest gate",
        "python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
    ),
    (
        "Self-test current Phase 1 string review checker",
        "python3 scripts/zigux/check-phase1-string-review-packet.py --self-test",
    ),
    (
        "Check current Phase 1 string review packet",
        "python3 scripts/zigux/check-phase1-string-review-packet.py",
    ),
    (
        "Self-test current Phase 1 route summary checker",
        "python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
    ),
    (
        "Check current Phase 1 route summary packet",
        "python3 scripts/zigux/check-phase1-route-summary-counts.py",
    ),
    (
        "Self-test current Phase 1 bench checker",
        "python3 scripts/zigux/check-phase1-bench.py --self-test",
    ),
    (
        "Self-test current Phase 1 shared reminder checker",
        "python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
    ),
    (
        "Check current Phase 1 shared reminder packet",
        "python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
    ),
    (
        "Self-test current Phase 1 closure validator",
        "python3 scripts/zigux/validate-phase1-closure.py --self-test",
    ),
    (
        "Check current Phase 1 closure packet",
        "python3 scripts/zigux/validate-phase1-closure.py",
    ),
    (
        "Self-test current Phase 3 interop packet",
        "python3 scripts/zigux/validate_phase3_selftest.py",
    ),
    (
        "Check current Phase 3 interop packet",
        "python3 scripts/zigux/run-phase3-checks.py",
    ),
    (
        "Run current Phase 3 export/UAPI layout replay",
        "zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
    ),
    (
        "Run current Phase 3 policy starter-packet replay",
        "make -C zigux phase3-policy-starter-packet-test",
    ),
    (
        "Run current Phase 3 policy dump replay",
        "zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig",
    ),
    (
        "Self-test current Phase 3 low-level wrapper survey validator",
        "python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test",
    ),
    (
        "Check current Phase 3 low-level wrapper survey packet",
        "python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    ),
    (
        "Run current Phase 3 low-level wrapper replay",
        "zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    ),
    (
        "Run current Phase 3 shared tests-root packet",
        "zig build phase3-test --build-file zigux/tests/build.zig",
    ),
    (
        "Run current Phase 3 ABI dump replay",
        "zig build phase3-dump --build-file zigux/tests/build.zig",
    ),
    (
        "Run current Phase 1 shared tests-root smoke",
        "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    ),
)

OPTIONAL_WORKFLOW_PACKET_STEPS = (
    (
        "Self-test current Phase 1 bootstrap packet alignment checker",
        "python3 scripts/zigux/check-phase1-bootstrap-packet-alignment.py --self-test",
    ),
    (
        "Check current Phase 1 bootstrap packet alignment",
        "python3 scripts/zigux/check-phase1-bootstrap-packet-alignment.py",
    ),
)

PHASE1_PACKET_PREDECESSOR = (
    "Validate current Phase 2 tool packet",
    "python3 scripts/zigux/validate-phase2.py",
)
PHASE1_PACKET_SUCCESSOR = (
    "Self-test current Phase 4 repo-reality warning checker",
    "python3 scripts/zigux/check-phase4-repo-reality-warning.py --self-test",
)

FORBIDDEN_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase1-bench.py",
)

REQUIRED_MARKERS = {
    DOCS_ROOT_REL: (
        "* `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the bounded current reminder checks, while the live checker routes guard the shipped Phase 1 packet without widening it back into the older closure-side or installer-companion stack.",
        "* keep the helper-family split explicit here too: the nine shared-replay parked helpers reopen only for packet drift, while bitmap, find_bit, rbtree, and string keep the only bounded direct-anchor follow-up anchors on current master.",
    ),
    PHASE1_CLOSURE_REL: (
        "The current bootstrap workflow also keeps the adjacent Phase 1 route-summary guard wired beside that same live reminder packet: `.github/workflows/zigux-bootstrap.yml` self-tests the directly readable Phase 1 direct-owner, direct-anchor manifest, string-review, route-summary, bench, shared-reminder, and closure-validator checks, replays the direct-anchor manifest gate, route-summary, direct-owner, string-review, shared-reminder, closure-validator, and shared tests-root smoke steps on current `master`, and currently keeps the bench checker at self-test coverage only.",
        "- `PHASE1_FIND_BIT_BENCH_GUARD=scripts/zigux/check-phase1-bench.py still hard-codes PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS=20000 and PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS=20000 and still requires PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM and PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM when the broader expectations packet returns`",
        "- `PHASE1_RBTREE_BENCH_GUARD=scripts/zigux/check-phase1-bench.py now hard-codes PHASE1_BENCH_RBTREE_ITERATIONS=4000 and exact-checks PHASE1_BENCH_RBTREE_CHECKSUM, PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM, PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM, PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM, and PHASE1_BENCH_RBTREE_CACHED_CHECKSUM when the broader expectations packet returns`",
        "- `PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`",
        "- `PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
        "- `PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`",
        "- `PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface or one helper-family tie-breaker against the restored closure note, the closure validator, the shared tests-root smoke route, and the helper-specific next_safe_step_note entries in the committed manifest rather than widening back into the older validator-first or replay-side closure stack.`",
    ),
    LANE_SEQUENCING_REL: (
        "- `PHASE1_LANE_RULE_SUMMARY=Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, while bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local follow-up anchors on current master.`",
        "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_ACTIVE_PACKET=Documentation/zigux/README.md,Documentation/zigux/phase1-closure.md,Documentation/zigux/review-checklist.md,zigux/tests/README.md,scripts/zigux/README.md,scripts/zigux/validate-phase1-closure.py,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py`",
        "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_ROUTE_SPLIT=Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, zigux/tests/README.md, and scripts/zigux/README.md now all carry the shipped bench-checker wording, while Documentation/zigux/phase1-closure.md plus scripts/zigux/validate-phase1-closure.py keep the restored closure-side packet explicit and the broader installer-backed, validator-first, bench-route, and replay names remain historical packet members until direct current-master rereads restore them`",
    ),
    REVIEW_CHECKLIST_REL: (
        "* if the change touches the shared Phase 1 host-tools closure packet, do `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, `zigux/tests/README.md`, `zigux/tests/build.zig`, `zigux/tests/phase1_host_tools_smoke.zig`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/fixtures/phase1_helper_manifest.json`, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` still agree on the current closed-helper reminder packet, keep `scripts/zigux/check-phase1-route-summary-counts.py`, `make -C zigux phase1-route-summary`, and `zigux/Makefile` explicit as the adjacent Phase 1 route-summary evidence for the returned Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14 route families, while the older validator-first, parity, bench-route, and replay names stay framed as historical packet members until current `master` materializes them again?`",
    ),
    SCRIPTS_README_REL: (
        "- `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the shipped bounded Phase 1 reminder checks, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` replays the shipped shared tests-root smoke route",
        "- `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, and `scripts/zigux/validate-phase1-closure.py` keep the shipped string-review, direct-owner, bench, shared-reminder, and closure-validator packet explicit from the scripts root",
        "- `scripts/zigux/check-phase1-route-summary-counts.py`, `make -C zigux phase1-route-summary`, and `.github/workflows/zigux-bootstrap.yml` keep the adjacent Phase 1 route-summary guard explicit beside the narrower reminder packet, so scripts-root follow-through can verify the returned non-Phase-1 Makefile route inventory without promoting the older Phase 1 wrappers back into shipped proof",
        "- the current direct-anchor tie-breakers stay helper-local: bitmap, find_bit, rbtree, and string reopen only inside their existing helper-local anchors or already-committed shared fixture keys, while the other nine closed helpers stay parked unless the shared replay or reminder packet drifts",
    ),
    TESTS_README_REL: (
        "- `scripts/zigux/check-phase1-direct-anchor-manifest-gate.py`",
        "  * current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
        "  * keep the Phase 1 tests-root reminder truthful: the thirteen helper ports remain closed through the committed manifest, the nine shared-replay parked helpers reopen only for packet or fixture drift, and only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers on current `master`",
    ),
    CLOSURE_VALIDATOR_REL: (
        'DIRECT_ANCHOR_MANIFEST_GATE_REL = Path("scripts/zigux/check-phase1-direct-anchor-manifest-gate.py")',
        'FIND_BIT_REVIEW_CHECKER_REL = Path("scripts/zigux/check-phase1-find-bit-review-packet.py")',
        'FIND_BIT_BENCH_ANCHOR_CHECKER_REL = Path("scripts/zigux/check-phase1-find-bit-bench-anchors.py")',
        '    "direct_anchor_manifest_gate": "`PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py exact-checks the current direct-anchor helper manifest packet for bitmap, find_bit, rbtree, and string and then reruns the dedicated rbtree direct-anchor checker`",',
        '    "find_bit_bench_anchor_guard": "`PHASE1_FIND_BIT_BENCH_ANCHOR_GUARD=python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py exact-checks inclusive-boundary, past-nbits no-read, clump8 past-end no-read, and findLastBit tail-clamp anchors directly in tools/lib/find_bit.zig`",',
        '    "route_summary_guard": "`PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`",',
        '    "shared_tests_route": "`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",',
        '    "validator_state": "`PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`",',
        '    (DIRECT_ANCHOR_MANIFEST_GATE_REL, "phase1-direct-anchor-manifest-gate"),',
        '    (FIND_BIT_REVIEW_CHECKER_REL, "phase1-find-bit-review-packet"),',
        '    (FIND_BIT_BENCH_ANCHOR_CHECKER_REL, "phase1-find-bit-bench-anchors"),',
    ),
}

REQUIRED_BUILD_MARKERS = (
    'const phase1_step = b.step(',
    '"phase1-host-tools-smoke",',
    '"Run the shared Phase 1 host-tools smoke anchor from zigux/tests",',
    'phase1_step.dependOn(&phase1_host_tools_smoke.step);',
    'const smoke_step = b.step(',
    'smoke_step.dependOn(&phase1_host_tools_smoke.step);',
    'const test_step = b.step(',
    'test_step.dependOn(&phase1_host_tools_smoke.step);',
)

REQUIRED_PHASE1_SMOKE_MARKERS = (
    'test "phase1 host-tools smoke imports the live helper modules" {',
    'test "phase1 host-tools smoke exercises live helper behavior" {',
    'test "phase1 host-tools smoke keeps find_bit andnot and clump anchors aligned" {',
    'test "phase1 host-tools smoke keeps bitmap alias zero-size and empty-format edges aligned" {',
)

REQUIRED_MANIFEST_MARKERS = (
    '"phase": "Phase 1"',
    '"status": "closed"',
    '"helper_count": 13',
    '"rule_summary": "Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, while bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local follow-up anchors on current master."',
    '"anti_overlap_rule": "Do not reopen Phase 1 by batching helpers across those two sets in one lane; shared-replay parked helpers reopen only for packet drift, while direct-anchor helpers reopen only for their existing helper-local anchors or already-committed shared fixture keys."',
)

REQUIRED_MAKEFILE_MARKERS = (
    ".PHONY: phase1-route-summary phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2 phase3-validate phase3",
    "phase1-route-summary:",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-route-summary-counts.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-route-summary-counts.py",
    "phase3-validate:",
    "phase3: phase3-validate phase3-export-uapi-layout phase3-low-level-wrappers phase3-test phase3-policy-dump phase3-dump",
    "phase4-validate:",
    "phase6-validate:",
    "phase8-validate:",
    "phase10-validate:",
    "phase12-validate:",
    "phase14-validate:",
)

FORBIDDEN_MAKEFILE_MARKERS = (
    ".PHONY: phase1-validate",
    ".PHONY: phase1-test",
    ".PHONY: phase1-bench",
    ".PHONY: phase1 ",
    "\nphase1-validate:",
    "\nphase1-test:",
    "\nphase1-bench:",
    "\nphase1:",
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_exact_occurrence(text: str, label: str, needle: str) -> list[str]:
    count = text.count(needle)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_absent_occurrence(text: str, label: str, needle: str) -> list[str]:
    count = sum(1 for current in text.splitlines() if current.strip() == needle)
    return [] if count == 0 else [f"{label}:expected=0:actual={count}"]


def require_exact_line_occurrence(text: str, label: str, needle: str) -> list[str]:
    count = sum(1 for current in text.splitlines() if current == needle)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_substring_absent(text: str, label: str, needle: str) -> list[str]:
    count = text.count(needle)
    return [] if count == 0 else [f"{label}:expected=0:actual={count}"]


def workflow_name_line(step_name: str) -> str:
    return f"- name: {step_name}"


def workflow_run_line(run_command: str) -> str:
    return f"run: {run_command}"


def workflow_step_block(step_name: str, run_command: str) -> str:
    return f"      - name: {step_name}\n        run: {run_command}"


def workflow_step_names(text: str) -> list[str]:
    prefix = "      - name: "
    return [line[len(prefix) :] for line in text.splitlines() if line.startswith(prefix)]


def contains_adjacent_chain(names: list[str], expected_chain: tuple[str, ...]) -> bool:
    chain_length = len(expected_chain)
    max_start = len(names) - chain_length + 1
    for start in range(max_start):
        if tuple(names[start : start + chain_length]) == expected_chain:
            return True
    return False


def collect_workflow_order_failures(text: str) -> list[str]:
    failures: list[str] = []

    for boundary_label, (step_name, run_command) in (
        ("predecessor", PHASE1_PACKET_PREDECESSOR),
        ("successor", PHASE1_PACKET_SUCCESSOR),
    ):
        name_line = workflow_name_line(step_name)
        run_line = workflow_run_line(run_command)
        block = workflow_step_block(step_name, run_command)
        name_count = sum(1 for current in text.splitlines() if current.strip() == name_line)
        run_count = sum(1 for current in text.splitlines() if current.strip() == run_line)
        pair_count = text.count(block)
        if name_count != 1:
            failures.append(f"workflow_boundary_{boundary_label}_step:{step_name}:expected=1:actual={name_count}")
        if run_count != 1:
            failures.append(f"workflow_boundary_{boundary_label}_run:{run_command}:expected=1:actual={run_count}")
        if pair_count != 1:
            failures.append(f"workflow_boundary_{boundary_label}_pair:{step_name}:expected=1:actual={pair_count}")
    if failures:
        return failures

    position_map: dict[str, int] = {}
    for step_name, run_command in WORKFLOW_PACKET_STEPS:
        name_line = workflow_name_line(step_name)
        run_line = workflow_run_line(run_command)
        block = workflow_step_block(step_name, run_command)
        name_count = sum(1 for current in text.splitlines() if current.strip() == name_line)
        run_count = sum(1 for current in text.splitlines() if current.strip() == run_line)
        pair_count = text.count(block)
        if name_count != 1:
            failures.append(f"workflow_step:{step_name}:expected=1:actual={name_count}")
        if run_count != 1:
            failures.append(f"workflow_run:{run_command}:expected=1:actual={run_count}")
        if pair_count != 1:
            failures.append(f"workflow_pair:{step_name}:expected=1:actual={pair_count}")
            continue
        position_map[step_name] = text.index(block)
    if failures:
        return failures

    ordered_positions = [position_map[step_name] for step_name, _ in WORKFLOW_PACKET_STEPS]
    if ordered_positions != sorted(ordered_positions):
        failures.append("workflow:phase1_packet_order:expected=strictly_increasing:actual=out_of_order")
        return failures

    optional_counts: dict[str, tuple[int, int]] = {}
    optional_pair_counts: dict[str, int] = {}
    optional_positions: list[int] = []
    for step_name, run_command in OPTIONAL_WORKFLOW_PACKET_STEPS:
        name_line = workflow_name_line(step_name)
        run_line = workflow_run_line(run_command)
        optional_counts[step_name] = (
            sum(1 for current in text.splitlines() if current.strip() == name_line),
            sum(1 for current in text.splitlines() if current.strip() == run_line),
        )
        pair_count = text.count(workflow_step_block(step_name, run_command))
        optional_pair_counts[step_name] = pair_count
        if pair_count == 1:
            optional_positions.append(text.index(workflow_step_block(step_name, run_command)))
    present_optional = [
        step_name
        for step_name, counts in optional_counts.items()
        if counts != (0, 0) or optional_pair_counts[step_name] != 0
    ]
    if present_optional and len(present_optional) != len(OPTIONAL_WORKFLOW_PACKET_STEPS):
        for step_name, run_command in OPTIONAL_WORKFLOW_PACKET_STEPS:
            name_count, run_count = optional_counts[step_name]
            pair_count = optional_pair_counts[step_name]
            if name_count != 1:
                failures.append(f"workflow_optional_step:{step_name}:expected=1:actual={name_count}")
            if run_count != 1:
                failures.append(f"workflow_optional_run:{run_command}:expected=1:actual={run_count}")
            if pair_count != 1:
                failures.append(f"workflow_optional_pair:{step_name}:expected=1:actual={pair_count}")
        return failures

    if present_optional:
        for step_name, run_command in OPTIONAL_WORKFLOW_PACKET_STEPS:
            name_count, run_count = optional_counts[step_name]
            pair_count = optional_pair_counts[step_name]
            if name_count != 1:
                failures.append(f"workflow_optional_step:{step_name}:expected=1:actual={name_count}")
            if run_count != 1:
                failures.append(f"workflow_optional_run:{run_command}:expected=1:actual={run_count}")
            if pair_count != 1:
                failures.append(f"workflow_optional_pair:{step_name}:expected=1:actual={pair_count}")
        if failures:
            return failures
        if optional_positions != sorted(optional_positions):
            failures.append("workflow:phase1_bootstrap_optional_pair:expected=strictly_increasing:actual=out_of_order")
            return failures
        route_summary_check_pos = position_map["Check current Phase 1 route summary packet"]
        bench_self_test_pos = position_map["Self-test current Phase 1 bench checker"]
        if not all(route_summary_check_pos < pos < bench_self_test_pos for pos in optional_positions):
            failures.append(
                "workflow:phase1_bootstrap_optional_pair:expected=between_route_summary_check_and_bench_self_test:actual=outside_slot"
            )
            return failures
        optional_pair_block = "\n".join(
            workflow_step_block(step_name, run_command)
            for step_name, run_command in OPTIONAL_WORKFLOW_PACKET_STEPS
        )
        if text.count(optional_pair_block) != 1:
            failures.append(
                "workflow:phase1_bootstrap_optional_pair:expected=adjacent_self_test_then_check:actual=split_or_misordered"
            )
            return failures

    phase1_core_chain = tuple(step_name for step_name, _ in WORKFLOW_PACKET_STEPS)
    if present_optional:
        route_summary_index = phase1_core_chain.index("Check current Phase 1 route summary packet") + 1
        phase1_core_chain = (
            phase1_core_chain[:route_summary_index]
            + tuple(step_name for step_name, _ in OPTIONAL_WORKFLOW_PACKET_STEPS)
            + phase1_core_chain[route_summary_index:]
        )

    workflow_names = workflow_step_names(text)
    if not contains_adjacent_chain(workflow_names, phase1_core_chain):
        failures.append("workflow:phase1_core_packet:expected=adjacent_without_insertions:actual=split_or_interleaved")

    boundary_chain = (PHASE1_PACKET_PREDECESSOR[0],) + phase1_core_chain + (PHASE1_PACKET_SUCCESSOR[0],)
    if not contains_adjacent_chain(workflow_names, boundary_chain):
        failures.append(
            "workflow:phase1_bootstrap_packet_slot:expected=adjacent_between_phase2_tail_and_phase4_head:actual=split_or_shifted"
        )

    return failures


def collect_surface_failures(root: Path) -> list[str]:
    failures: list[str] = []

    tests_build_text = load_text(root, TESTS_BUILD_REL)
    for marker in REQUIRED_BUILD_MARKERS:
        failures.extend(
            require_exact_line_occurrence(
                tests_build_text,
                f"{TESTS_BUILD_REL.as_posix()}:{marker}",
                marker,
            )
        )

    phase1_smoke_text = load_text(root, PHASE1_SMOKE_REL)
    for marker in REQUIRED_PHASE1_SMOKE_MARKERS:
        failures.extend(
            require_exact_line_occurrence(
                phase1_smoke_text,
                f"{PHASE1_SMOKE_REL.as_posix()}:{marker}",
                marker,
            )
        )

    manifest_text = load_text(root, PHASE1_MANIFEST_REL)
    for marker in REQUIRED_MANIFEST_MARKERS:
        failures.extend(
            require_exact_line_occurrence(
                manifest_text,
                f"{PHASE1_MANIFEST_REL.as_posix()}:{marker}",
                marker,
            )
        )

    makefile_text = load_text(root, MAKEFILE_REL)
    for marker in REQUIRED_MAKEFILE_MARKERS:
        failures.extend(
            require_exact_line_occurrence(
                makefile_text,
                f"{MAKEFILE_REL.as_posix()}:{marker}",
                marker,
            )
        )
    for marker in FORBIDDEN_MAKEFILE_MARKERS:
        failures.extend(
            require_substring_absent(
                makefile_text,
                f"{MAKEFILE_REL.as_posix()}:{marker}",
                marker,
            )
        )

    return failures


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).is_file():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    for relative_path, markers in REQUIRED_MARKERS.items():
        text = load_text(root, relative_path)
        for marker in markers:
            failures.extend(
                require_exact_occurrence(
                    text,
                    f"{relative_path.as_posix()}:{marker}",
                    marker,
                )
            )

    workflow_text = load_text(root, WORKFLOW_REL)
    failures.extend(collect_workflow_order_failures(workflow_text))
    for line in FORBIDDEN_WORKFLOW_LINES:
        failures.extend(
            require_absent_occurrence(
                workflow_text,
                f"{WORKFLOW_REL.as_posix()}:{line}",
                line,
            )
        )
    failures.extend(collect_surface_failures(root))
    return failures


def write_text(root: Path, relative_path: Path, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        write_text(root, relative_path, "sample\n")

    for relative_path, markers in REQUIRED_MARKERS.items():
        write_text(root, relative_path, "\n".join(markers) + "\n")

    write_text(root, TESTS_BUILD_REL, "\n".join(REQUIRED_BUILD_MARKERS) + "\n")
    write_text(root, PHASE1_SMOKE_REL, "\n".join(REQUIRED_PHASE1_SMOKE_MARKERS) + "\n")
    write_text(root, PHASE1_MANIFEST_REL, "\n".join(REQUIRED_MANIFEST_MARKERS) + "\n")
    write_text(root, MAKEFILE_REL, "\n".join(REQUIRED_MAKEFILE_MARKERS) + "\n")

    sample_steps = [workflow_step_block(*PHASE1_PACKET_PREDECESSOR)]
    sample_steps.extend(workflow_step_block(step_name, run_command) for step_name, run_command in WORKFLOW_PACKET_STEPS)
    sample_steps.append(workflow_step_block(*PHASE1_PACKET_SUCCESSOR))
    write_text(root, WORKFLOW_REL, "\n".join(sample_steps) + "\n")


def remove_marker(root: Path, relative_path: Path, marker: str) -> None:
    text = load_text(root, relative_path)
    write_text(root, relative_path, text.replace(marker + "\n", "", 1))


def duplicate_marker(root: Path, relative_path: Path, marker: str) -> None:
    text = load_text(root, relative_path)
    write_text(root, relative_path, text.replace(marker, marker + "\n" + marker, 1))


def reorder_workflow(root: Path) -> None:
    steps = list(WORKFLOW_PACKET_STEPS)
    steps[0], steps[1] = steps[1], steps[0]
    blocks = [workflow_step_block(*PHASE1_PACKET_PREDECESSOR)]
    blocks.extend(workflow_step_block(step_name, run_command) for step_name, run_command in steps)
    blocks.append(workflow_step_block(*PHASE1_PACKET_SUCCESSOR))
    write_text(root, WORKFLOW_REL, "\n".join(blocks) + "\n")


def add_forbidden_workflow_line(root: Path) -> None:
    text = load_text(root, WORKFLOW_REL)
    write_text(root, WORKFLOW_REL, text + "        " + FORBIDDEN_WORKFLOW_LINES[0] + "\n")


def add_optional_workflow_pair(root: Path, reversed_pair: bool = False) -> None:
    workflow_text = load_text(root, WORKFLOW_REL)
    blocks = workflow_text.rstrip("\n").splitlines()
    joined_blocks: list[str] = []
    index = 0
    while index < len(blocks):
        if index + 1 < len(blocks) and blocks[index].startswith("      - name: ") and blocks[index + 1].startswith("        run: "):
            joined_blocks.append(blocks[index] + "\n" + blocks[index + 1])
            index += 2
            continue
        joined_blocks.append(blocks[index])
        index += 1
    blocks = joined_blocks
    bench_step = next(
        step for step in WORKFLOW_PACKET_STEPS if step[0] == "Self-test current Phase 1 bench checker"
    )
    bench_block = workflow_step_block(*bench_step)
    bench_index = blocks.index(bench_block)
    pair_blocks = [workflow_step_block(step_name, run_command) for step_name, run_command in OPTIONAL_WORKFLOW_PACKET_STEPS]
    if reversed_pair:
        pair_blocks = list(reversed(pair_blocks))
    blocks[bench_index:bench_index] = pair_blocks
    write_text(root, WORKFLOW_REL, "\n".join(blocks) + "\n")


def add_forbidden_makefile_marker(root: Path, marker: str) -> None:
    text = load_text(root, MAKEFILE_REL)
    write_text(root, MAKEFILE_REL, text + marker)


def run_self_test() -> int:
    cases: list[tuple[str, object | None]] = [("success", None), ("optional_pair_present", ("optional", False))]

    for relative_path in REQUIRED_FILES:
        cases.append((f"missing_file:{relative_path.as_posix()}", ("missing_file", relative_path)))

    for relative_path, markers in REQUIRED_MARKERS.items():
        for marker in markers:
            cases.append((f"missing_marker:{relative_path.as_posix()}", ("remove", relative_path, marker)))
            cases.append((f"duplicate_marker:{relative_path.as_posix()}", ("duplicate", relative_path, marker)))

    for marker in REQUIRED_BUILD_MARKERS:
        cases.append((f"missing_build_marker:{marker}", ("remove", TESTS_BUILD_REL, marker)))
    for marker in REQUIRED_PHASE1_SMOKE_MARKERS:
        cases.append((f"missing_smoke_marker:{marker}", ("remove", PHASE1_SMOKE_REL, marker)))
    for marker in REQUIRED_MANIFEST_MARKERS:
        cases.append((f"missing_manifest_marker:{marker}", ("remove", PHASE1_MANIFEST_REL, marker)))
    for marker in REQUIRED_MAKEFILE_MARKERS:
        cases.append((f"missing_makefile_marker:{marker}", ("remove", MAKEFILE_REL, marker)))
    for marker in FORBIDDEN_MAKEFILE_MARKERS:
        cases.append((f"forbidden_makefile_marker:{marker}", ("forbidden_makefile", marker)))

    cases.extend(
        [
            ("workflow_reordered", ("reorder_workflow",)),
            ("workflow_forbidden_line", ("forbidden_workflow",)),
            ("workflow_optional_pair_reversed", ("optional", True)),
        ]
    )

    for name, mutation in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-bootstrap-packet-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            if mutation:
                kind = mutation[0]
                if kind == "missing_file":
                    (root / mutation[1]).unlink()
                elif kind == "remove":
                    remove_marker(root, mutation[1], mutation[2])
                elif kind == "duplicate":
                    duplicate_marker(root, mutation[1], mutation[2])
                elif kind == "reorder_workflow":
                    reorder_workflow(root)
                elif kind == "forbidden_workflow":
                    add_forbidden_workflow_line(root)
                elif kind == "optional":
                    add_optional_workflow_pair(root, mutation[1])
                elif kind == "forbidden_makefile":
                    add_forbidden_makefile_marker(root, mutation[1])
            failures = collect_failures(root)
            if name in {"success", "optional_pair_present"}:
                if failures:
                    print(f"self-test:{name}:unexpected_failures")
                    for failure in failures:
                        print(failure)
                    return 1
            elif not failures:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("PHASE1_BOOTSTRAP_PACKET_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE1_BOOTSTRAP_PACKET_ALIGNMENT_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_BOOTSTRAP_PACKET_ALIGNMENT=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_BOOTSTRAP_PACKET_ALIGNMENT=pass")
    print(f"PHASE1_BOOTSTRAP_PACKET_ALIGNMENT_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE1_BOOTSTRAP_PACKET_ALIGNMENT_REQUIRED_WORKFLOW_STEP_COUNT={len(WORKFLOW_PACKET_STEPS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
