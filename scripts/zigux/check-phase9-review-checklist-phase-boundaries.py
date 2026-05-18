#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile


SELF_PATH = Path(__file__).resolve()


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / "Documentation/zigux/review-checklist.md").exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()
DOCS_README_PATH = "Documentation/zigux/README.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
LANE_SEQUENCING_PATH = "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md"
MODULE_SLICE_PATH = "Documentation/zigux/phase9-runtime-trace-events-module-slice.md"
TESTS_README_PATH = "zigux/tests/README.md"
SCRIPTS_README_PATH = "scripts/zigux/README.md"
SAMPLES_README_PATH = "samples/zigux/README.md"

PHASE9_SHARED_PACKET_MARKER = "if the change touches the shared Phase 9 runtime-pilot packet"
PHASE9_SCRIPTS_PACKET_MARKER = "Phase 9 flow - the current shared runtime-pilot packet is narrow and review-first"
TRACE_EVENTS_PACKET_CHECKER_MARKER = "`scripts/zigux/check-phase9-trace-events-runtime-packet.py`"
PHASE9_BOUNDARY_CHECKER_MARKER = "`scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`"
PHASE2_CONF_BRIDGE_MARKER = "`scripts/zigux/kconfig/conf_bridge.zig`"
PHASE2_CONFDATA_BRIDGE_MARKER = "`scripts/zigux/kconfig/confdata_bridge.zig`"
PHASE3_EXPORTS_MARKER = "`rust/exports.c`"
PHASE3_EXPORT_SHIM_MARKER = "`zigux/kernel/export_shim.zig`"
PHASE2_BOUNDARY_MARKER = "remain Phase 2 config-surface bridge references"
PHASE3_BOUNDARY_MARKER = "remain Phase 3 export-boundary references rather than runtime-pilot evidence"

REVIEW_CHECKLIST_TRACE_EVENTS_SAMPLE_MARKER = "`samples/zigux/runtime_trace_events.zig`"
REVIEW_CHECKLIST_SELFTEST_HOOK_MARKER = "`.provides_selftest_hook = true`"
REVIEW_CHECKLIST_LIFECYCLE_MARKER = "initialized, selftest_complete, and exited lifecycle tracking"
REVIEW_CHECKLIST_UNREGISTERED_GATE_MARKER = "`samples/zigux/runtime_trace_events_unregistered_gate.zig`"
REVIEW_CHECKLIST_EXIT_ROLLBACK_GUARD_MARKER = "`samples/zigux/runtime_trace_events_exit_rollback_guard.zig`"
REVIEW_CHECKLIST_REENTRY_GATE_MARKER = "`samples/zigux/runtime_trace_events_registration_reentry_gate.zig`"
REVIEW_CHECKLIST_FAIL_CLOSED_MARKER = "unregistered function-thread failures fail-closed"
REVIEW_CHECKLIST_EXIT_ROLLBACK_COMPANION_MARKER = "failed-exit rollback explicit after reusable selftest replay"
REVIEW_CHECKLIST_REENTRY_COMPANION_MARKER = "balanced registration re-entry companion that keeps function-thread registration reusable before and after selftest"
REVIEW_CHECKLIST_BACKLOG_MARKER = "does not currently expose the broader shared runtime-loader packet"
REVIEW_CHECKLIST_PHASE9_BUILD_MARKER = "`zigux/tests/phase9_build.zig`"
REVIEW_CHECKLIST_RUNTIME_LOADER_MARKER = "`zigux/kernel/runtime_loader.zig`"
REVIEW_CHECKLIST_RUNTIME_LOADER_CONTRACT_MARKER = "`zigux/kernel/runtime_loader_contract.zig`"
REVIEW_CHECKLIST_WORKFLOW_MARKER = "`.github/workflows/zigux-bootstrap.yml`"
REVIEW_CHECKLIST_RUNTIME_LOADER_SCAFFOLD_MARKER = "`samples/zigux/runtime_*_loader.zig` scaffolds"
REVIEW_CHECKLIST_BITMAP_PHASE5_BOUNDARY_MARKER = "there is no standalone `samples/zigux/*bitmap*` reference sample"
REVIEW_CHECKLIST_BITMAP_HELPER_BOUNDARY_MARKER = "direct bitmap helper reviewability remains under `tools/lib/bitmap.zig`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, and `Documentation/zigux/phase4-reversible-delivery-evidence.md`"
REVIEW_CHECKLIST_BITMAP_RUNTIME_BACKLOG_MARKER = "runtime bitmap family stays framed as backlog-only Phase 9 support material in `samples/zigux/README.md`, `Documentation/zigux/README.md`, and `Documentation/zigux/review-checklist.md`"
REVIEW_CHECKLIST_BITMAP_RUNTIME_RETURN_MARKER = "unless a fresh repo reread proves `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `samples/zigux/runtime_bitmap_top_bit_contract.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, and `zigux/tests/phase9_build.zig` have returned on current `master`"
REVIEW_CHECKLIST_TRACE_EVENTS_ONLY_MARKER = "keep the current surviving Phase 9 packet trace-events-only so those historical runtime-bitmap backlog names do not get mistaken for present runtime proof or extra Phase 5 evidence"

LANE_SEQUENCING_SAMPLE_MARKER = "surviving direct runtime-module sample: `samples/zigux/runtime_trace_events.zig`"
LANE_SEQUENCING_SELFTEST_MARKER = "`.provides_selftest_hook = true` together with initialized, selftest_complete, and exited lifecycle tracking"
LANE_SEQUENCING_UNREGISTERED_GATE_MARKER = "surviving fail-closed runtime companion: `samples/zigux/runtime_trace_events_unregistered_gate.zig`"
LANE_SEQUENCING_REENTRY_GATE_MARKER = "surviving registration-reentry runtime companion: `samples/zigux/runtime_trace_events_registration_reentry_gate.zig`"
LANE_SEQUENCING_REENTRY_DETAIL_MARKER = "balanced registration re-entry replay in `samples/zigux/runtime_trace_events_registration_reentry_gate.zig` across both the initialized and selftest_complete stages"
LANE_SEQUENCING_BACKLOG_MARKER = "does not currently expose the broader shared runtime-loader packet"
LANE_SEQUENCING_FREEZE_BOUNDARY_MARKER = "keep the freeze-map study-only anchors explicit through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md`: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain cautionary non-owner context rather than proof of runtime-substrate or bridge readiness"
LANE_SEQUENCING_HISTORICAL_SURVEY_TRIO_MARKER = "the older wider-family reminder-survey trio `Documentation/zigux/phase9-runtime-loader-gap-survey.md`, `zigux/tests/runtime_loader_gap_manifest.json`, and `zigux/tests/runtime_loader_gap_survey.zig`"
LANE_SEQUENCING_HISTORICAL_VOCABULARY_MARKER = "may still preserve blocked `.modinfo`, `MODULE_ALIAS()`, `modules.alias`, and depmod-publication vocabulary"
LANE_SEQUENCING_NOT_OWNER_EVIDENCE_MARKER = "they no longer count as current shared-owner evidence for this narrow packet unless a fresh repo reread proves the broader loader family returned"
LANE_SEQUENCING_STALE_OVERCLAIM_BLOCKER_MARKER = "Treat stale reminder overclaim as the active blocker before reopening checker-local or runtime-behavior work."

TESTS_README_TRACE_EVENTS_SAMPLE_MARKER = "`samples/zigux/runtime_trace_events.zig`"
TESTS_README_SELFTEST_HOOK_MARKER = "`.provides_selftest_hook = true`"
TESTS_README_LIFECYCLE_MARKER = "initialized, selftest_complete, and exited lifecycle tracking"
TESTS_README_UNREGISTERED_GATE_MARKER = "`samples/zigux/runtime_trace_events_unregistered_gate.zig`"
TESTS_README_REENTRY_GATE_MARKER = "`samples/zigux/runtime_trace_events_registration_reentry_gate.zig`"
TESTS_README_FAIL_CLOSED_MARKER = "unregistered function-thread failures fail-closed"
TESTS_README_REENTRY_COMPANION_MARKER = "keeps balanced function-thread registration reusable before and after selftest"
TESTS_README_BACKLOG_MARKER = (
    "there is no shared `zigux/tests/runtime_*` replay packet, `zigux/tests/phase9_build.zig`, "
    "`make -C zigux phase9*` route family, or dedicated shared `validate-phase9.py` visible on current `master`"
)

DOCS_README_PHASE9_NOTES_MARKER = "Phase 9 notes - `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`"
DOCS_README_TRACE_EVENTS_SAMPLE_MARKER = "`samples/zigux/runtime_trace_events.zig`"
DOCS_README_SELFTEST_HOOK_MARKER = "`.provides_selftest_hook = true`"
DOCS_README_LIFECYCLE_MARKER = "initialized, selftest_complete, and exited lifecycle tracking"
DOCS_README_UNREGISTERED_GATE_MARKER = "`samples/zigux/runtime_trace_events_unregistered_gate.zig`"
DOCS_README_REENTRY_GATE_MARKER = "`samples/zigux/runtime_trace_events_registration_reentry_gate.zig`"
DOCS_README_FAIL_CLOSED_MARKER = "unregistered function-thread failures fail-closed"
DOCS_README_REENTRY_COMPANION_MARKER = "balanced function-thread registration reusable across the initialized and selftest_complete stages"
DOCS_README_BACKLOG_MARKER = "does not currently expose the broader shared runtime-loader packet"
DOCS_README_PHASE2_BOUNDARY_MARKER = "remain Phase 2 config-surface bridge references"
DOCS_README_PHASE3_BOUNDARY_MARKER = "remain Phase 3 export-boundary references rather than runtime-pilot evidence"

SCRIPTS_README_TRACE_EVENTS_SAMPLE_MARKER = "`samples/zigux/runtime_trace_events.zig`"
SCRIPTS_README_UNREGISTERED_GATE_MARKER = "`samples/zigux/runtime_trace_events_unregistered_gate.zig`"
SCRIPTS_README_REENTRY_GATE_MARKER = "`samples/zigux/runtime_trace_events_registration_reentry_gate.zig`"
SCRIPTS_README_SELFTEST_HOOK_MARKER = "`.provides_selftest_hook = true`"
SCRIPTS_README_LIFECYCLE_MARKER = "initialized, selftest_complete, and exited lifecycle tracking"
SCRIPTS_README_FAIL_CLOSED_MARKER = "unregistered function-thread failures fail-closed"
SCRIPTS_README_REENTRY_COMPANION_MARKER = "keeps balanced function-thread registration reusable before and after selftest"
SCRIPTS_README_BACKLOG_MARKER = "current `master` still does not materialize `zigux/tests/phase9_build.zig`"
SCRIPTS_README_BOUNDARY_SELF_TEST_MARKER = "`python3 scripts/zigux/check-phase9-review-checklist-phase-boundaries.py --self-test`"
SCRIPTS_README_PACKET_SELF_TEST_MARKER = "`python3 scripts/zigux/check-phase9-trace-events-runtime-packet.py --self-test`"
SCRIPTS_README_BOUNDARY_LIVE_MARKER = "`python3 scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`"
SCRIPTS_README_PACKET_LIVE_MARKER = "`python3 scripts/zigux/check-phase9-trace-events-runtime-packet.py`"
SCRIPTS_README_FREEZE_BOUNDARY_MARKER = "keep the freeze-map boundary explicit too: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only anchors through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` rather than Phase 9 runtime-substrate readiness cues"

SAMPLES_README_TRACE_EVENTS_SAMPLE_MARKER = "`samples/zigux/runtime_trace_events.zig`"
SAMPLES_README_SELFTEST_HOOK_MARKER = "`.provides_selftest_hook = true`"
SAMPLES_README_LIFECYCLE_MARKER = "initialized, selftest_complete, and exited lifecycle tracking"
SAMPLES_README_BACKLOG_MARKER = "does not currently expose the broader shared runtime-loader packet"
SAMPLES_README_UNREGISTERED_GATE_MARKER = "`samples/zigux/runtime_trace_events_unregistered_gate.zig`"
SAMPLES_README_REENTRY_GATE_MARKER = "`samples/zigux/runtime_trace_events_registration_reentry_gate.zig`"
SAMPLES_README_REENTRY_COMPANION_MARKER = "balanced function-thread registration reusable before and after selftest"
SAMPLES_README_REENTRY_DETAIL_MARKER = "balanced registration re-entry companion across the initialized and selftest_complete stages"
SAMPLES_README_POST_EXIT_REJECTION_MARKER = "post-exit invalid-lifecycle rejections"
SAMPLES_README_SUMMARY_STABILITY_MARKER = "initialized-before/after, selftest_complete-before/after, and exited-before/after summary-stability checks"

MODULE_SLICE_PHASE_BOUNDARY_HEADING = "Keep earlier-phase references in their own lanes:"
MODULE_SLICE_LIFECYCLE_MARKER = "initialized, selftest_complete, and exited sample-local lifecycle tracking"
MODULE_SLICE_PHASE2_BOUNDARY_MARKER = "remain Phase 2 references"
MODULE_SLICE_PHASE3_BOUNDARY_MARKER = "remain Phase 3 export-boundary references."

CHECKLIST_REQUIRED_MARKERS = [
    PHASE9_SHARED_PACKET_MARKER,
    TRACE_EVENTS_PACKET_CHECKER_MARKER,
    REVIEW_CHECKLIST_TRACE_EVENTS_SAMPLE_MARKER,
    REVIEW_CHECKLIST_SELFTEST_HOOK_MARKER,
    REVIEW_CHECKLIST_LIFECYCLE_MARKER,
    REVIEW_CHECKLIST_UNREGISTERED_GATE_MARKER,
    REVIEW_CHECKLIST_EXIT_ROLLBACK_GUARD_MARKER,
    REVIEW_CHECKLIST_REENTRY_GATE_MARKER,
    REVIEW_CHECKLIST_FAIL_CLOSED_MARKER,
    REVIEW_CHECKLIST_EXIT_ROLLBACK_COMPANION_MARKER,
    REVIEW_CHECKLIST_REENTRY_COMPANION_MARKER,
    REVIEW_CHECKLIST_BACKLOG_MARKER,
    REVIEW_CHECKLIST_PHASE9_BUILD_MARKER,
    REVIEW_CHECKLIST_RUNTIME_LOADER_MARKER,
    REVIEW_CHECKLIST_RUNTIME_LOADER_CONTRACT_MARKER,
    REVIEW_CHECKLIST_WORKFLOW_MARKER,
    REVIEW_CHECKLIST_RUNTIME_LOADER_SCAFFOLD_MARKER,
    REVIEW_CHECKLIST_BITMAP_PHASE5_BOUNDARY_MARKER,
    REVIEW_CHECKLIST_BITMAP_HELPER_BOUNDARY_MARKER,
    REVIEW_CHECKLIST_BITMAP_RUNTIME_BACKLOG_MARKER,
    REVIEW_CHECKLIST_BITMAP_RUNTIME_RETURN_MARKER,
    REVIEW_CHECKLIST_TRACE_EVENTS_ONLY_MARKER,
    PHASE2_CONF_BRIDGE_MARKER,
    PHASE2_CONFDATA_BRIDGE_MARKER,
    PHASE3_EXPORTS_MARKER,
    PHASE3_EXPORT_SHIM_MARKER,
    PHASE2_BOUNDARY_MARKER,
    PHASE3_BOUNDARY_MARKER,
]

LANE_SEQUENCING_REQUIRED_MARKERS = [
    TRACE_EVENTS_PACKET_CHECKER_MARKER,
    LANE_SEQUENCING_SAMPLE_MARKER,
    LANE_SEQUENCING_SELFTEST_MARKER,
    LANE_SEQUENCING_UNREGISTERED_GATE_MARKER,
    LANE_SEQUENCING_REENTRY_GATE_MARKER,
    LANE_SEQUENCING_REENTRY_DETAIL_MARKER,
    LANE_SEQUENCING_BACKLOG_MARKER,
    LANE_SEQUENCING_FREEZE_BOUNDARY_MARKER,
    LANE_SEQUENCING_HISTORICAL_SURVEY_TRIO_MARKER,
    LANE_SEQUENCING_HISTORICAL_VOCABULARY_MARKER,
    LANE_SEQUENCING_NOT_OWNER_EVIDENCE_MARKER,
    LANE_SEQUENCING_STALE_OVERCLAIM_BLOCKER_MARKER,
]

MODULE_SLICE_REQUIRED_MARKERS = [
    TRACE_EVENTS_PACKET_CHECKER_MARKER,
    TRACE_EVENTS_SAMPLE_MARKER,
    UNREGISTERED_GATE_SAMPLE_MARKER,
    REENTRY_GATE_SAMPLE_MARKER,
    SELFTEST_HOOK_MARKER,
    MODULE_SLICE_LIFECYCLE_MARKER,
    ABSENT_SHARED_LOADER_MARKER,
    PHASE2_CONF_BRIDGE_MARKER,
    PHASE2_CONFDATA_BRIDGE_MARKER,
    PHASE3_EXPORTS_MARKER,
    PHASE3_EXPORT_SHIM_MARKER,
    MODULE_SLICE_PHASE_BOUNDARY_HEADING,
    MODULE_SLICE_PHASE2_BOUNDARY_MARKER,
    MODULE_SLICE_PHASE3_BOUNDARY_MARKER,
]

TESTS_README_REQUIRED_MARKERS = [
    TESTS_README_TRACE_EVENTS_SAMPLE_MARKER,
    TESTS_README_UNREGISTERED_GATE_MARKER,
    TESTS_README_REENTRY_GATE_MARKER,
    TESTS_README_SELFTEST_HOOK_MARKER,
    TESTS_README_LIFECYCLE_MARKER,
    TESTS_README_FAIL_CLOSED_MARKER,
    TESTS_README_REENTRY_COMPANION_MARKER,
    TESTS_README_BACKLOG_MARKER,
]

DOCS_README_REQUIRED_MARKERS = [
    DOCS_README_PHASE9_NOTES_MARKER,
    TRACE_EVENTS_PACKET_CHECKER_MARKER,
    DOCS_README_TRACE_EVENTS_SAMPLE_MARKER,
    DOCS_README_SELFTEST_HOOK_MARKER,
    DOCS_README_LIFECYCLE_MARKER,
    DOCS_README_UNREGISTERED_GATE_MARKER,
    DOCS_README_REENTRY_GATE_MARKER,
    DOCS_README_FAIL_CLOSED_MARKER,
    DOCS_README_REENTRY_COMPANION_MARKER,
    DOCS_README_BACKLOG_MARKER,
    DOCS_README_PHASE2_BOUNDARY_MARKER,
    DOCS_README_PHASE3_BOUNDARY_MARKER,
]

SCRIPTS_README_REQUIRED_MARKERS = [
    PHASE9_SCRIPTS_PACKET_MARKER,
    PHASE9_BOUNDARY_CHECKER_MARKER,
    TRACE_EVENTS_PACKET_CHECKER_MARKER,
    SCRIPTS_README_BOUNDARY_SELF_TEST_MARKER,
    SCRIPTS_README_PACKET_SELF_TEST_MARKER,
    SCRIPTS_README_BOUNDARY_LIVE_MARKER,
    SCRIPTS_README_PACKET_LIVE_MARKER,
    SCRIPTS_README_TRACE_EVENTS_SAMPLE_MARKER,
    SCRIPTS_README_UNREGISTERED_GATE_MARKER,
    SCRIPTS_README_REENTRY_GATE_MARKER,
    SCRIPTS_README_SELFTEST_HOOK_MARKER,
    SCRIPTS_README_LIFECYCLE_MARKER,
    SCRIPTS_README_FAIL_CLOSED_MARKER,
    SCRIPTS_README_REENTRY_COMPANION_MARKER,
    SCRIPTS_README_BACKLOG_MARKER,
    SCRIPTS_README_FREEZE_BOUNDARY_MARKER,
    PHASE2_CONF_BRIDGE_MARKER,
    PHASE2_CONFDATA_BRIDGE_MARKER,
    PHASE3_EXPORTS_MARKER,
    PHASE3_EXPORT_SHIM_MARKER,
    PHASE2_BOUNDARY_MARKER,
    PHASE3_BOUNDARY_MARKER,
]

SAMPLES_README_REQUIRED_MARKERS = [
    PHASE9_BOUNDARY_CHECKER_MARKER,
    TRACE_EVENTS_PACKET_CHECKER_MARKER,
    SAMPLES_README_TRACE_EVENTS_SAMPLE_MARKER,
    SAMPLES_README_SELFTEST_HOOK_MARKER,
    SAMPLES_README_LIFECYCLE_MARKER,
    SAMPLES_README_BACKLOG_MARKER,
    SAMPLES_README_UNREGISTERED_GATE_MARKER,
    SAMPLES_README_POST_EXIT_REJECTION_MARKER,
    SAMPLES_README_SUMMARY_STABILITY_MARKER,
    SAMPLES_README_REENTRY_GATE_MARKER,
    SAMPLES_README_REENTRY_COMPANION_MARKER,
    SAMPLES_README_REENTRY_DETAIL_MARKER,
    PHASE2_CONF_BRIDGE_MARKER,
    PHASE2_CONFDATA_BRIDGE_MARKER,
    PHASE3_EXPORTS_MARKER,
    PHASE3_EXPORT_SHIM_MARKER,
    PHASE2_BOUNDARY_MARKER,
    PHASE3_BOUNDARY_MARKER,
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    docs_readme_path = root / DOCS_README_PATH
    checklist_path = root / REVIEW_CHECKLIST_PATH
    lane_sequencing_path = root / LANE_SEQUENCING_PATH
    module_slice_path = root / MODULE_SLICE_PATH
    tests_readme_path = root / TESTS_README_PATH
    scripts_readme_path = root / SCRIPTS_README_PATH
    samples_readme_path = root / SAMPLES_README_PATH
    if not docs_readme_path.exists():
        failures.append(f"missing_file:{DOCS_README_PATH}")
    if not checklist_path.exists():
        failures.append(f"missing_file:{REVIEW_CHECKLIST_PATH}")
    if not lane_sequencing_path.exists():
        failures.append(f"missing_file:{LANE_SEQUENCING_PATH}")
    if not module_slice_path.exists():
        failures.append(f"missing_file:{MODULE_SLICE_PATH}")
    if not tests_readme_path.exists():
        failures.append(f"missing_file:{TESTS_README_PATH}")
    if not scripts_readme_path.exists():
        failures.append(f"missing_file:{SCRIPTS_README_PATH}")
    if not samples_readme_path.exists():
        failures.append(f"missing_file:{SAMPLES_README_PATH}")
    if failures:
        return failures

    docs_readme = read_text(root, DOCS_README_PATH)
    for marker in DOCS_README_REQUIRED_MARKERS:
        if marker not in docs_readme:
            failures.append(f"missing_marker:{DOCS_README_PATH}:{marker}")

    checklist = read_text(root, REVIEW_CHECKLIST_PATH)
    for marker in CHECKLIST_REQUIRED_MARKERS:
        if marker not in checklist:
            failures.append(f"missing_marker:{REVIEW_CHECKLIST_PATH}:{marker}")

    lane_sequencing = read_text(root, LANE_SEQUENCING_PATH)
    for marker in LANE_SEQUENCING_REQUIRED_MARKERS:
        if marker not in lane_sequencing:
            failures.append(f"missing_marker:{LANE_SEQUENCING_PATH}:{marker}")

    module_slice = read_text(root, MODULE_SLICE_PATH)
    for marker in MODULE_SLICE_REQUIRED_MARKERS:
        if marker not in module_slice:
            failures.append(f"missing_marker:{MODULE_SLICE_PATH}:{marker}")

    tests_readme = read_text(root, TESTS_README_PATH)
    for marker in TESTS_README_REQUIRED_MARKERS:
        if marker not in tests_readme:
            failures.append(f"missing_marker:{TESTS_README_PATH}:{marker}")

    scripts_readme = read_text(root, SCRIPTS_README_PATH)
    for marker in SCRIPTS_README_REQUIRED_MARKERS:
        if marker not in scripts_readme:
            failures.append(f"missing_marker:{SCRIPTS_README_PATH}:{marker}")

    samples_readme = read_text(root, SAMPLES_README_PATH)
    for marker in SAMPLES_README_REQUIRED_MARKERS:
        if marker not in samples_readme:
            failures.append(f"missing_marker:{SAMPLES_README_PATH}:{marker}")

    return failures


def build_docs_readme_fixture_text() -> str:
    return f"""# Zigux Documentation

{DOCS_README_PHASE9_NOTES_MARKER} - `Documentation/zigux/review-checklist.md` - {PHASE9_BOUNDARY_CHECKER_MARKER} - {TRACE_EVENTS_PACKET_CHECKER_MARKER} - `zigux/tests/README.md` - {DOCS_README_TRACE_EVENTS_SAMPLE_MARKER} - {DOCS_README_UNREGISTERED_GATE_MARKER} - {DOCS_README_REENTRY_GATE_MARKER} now keep the current narrow runtime-pilot packet reviewable from the docs root: the surviving direct runtime-module sample still exposes {DOCS_README_SELFTEST_HOOK_MARKER} together with {DOCS_README_LIFECYCLE_MARKER}, while the shipped unregistered-gate companion keeps {DOCS_README_FAIL_CLOSED_MARKER}, the registration-reentry companion keeps {DOCS_README_REENTRY_COMPANION_MARKER}, and while current `master` {DOCS_README_BACKLOG_MARKER}.
- the same shared Phase 9 summary should keep the older non-owner boundaries explicit: {PHASE2_CONF_BRIDGE_MARKER} and {PHASE2_CONFDATA_BRIDGE_MARKER} {DOCS_README_PHASE2_BOUNDARY_MARKER}, while {PHASE3_EXPORTS_MARKER} and {PHASE3_EXPORT_SHIM_MARKER} {DOCS_README_PHASE3_BOUNDARY_MARKER}.
"""


def build_fixture_text() -> str:
    return f"""# Zigux Review Checklist

- {PHASE9_SHARED_PACKET_MARKER}
- the shared Phase 9 reminder should keep the surviving runtime packet explicit through {TRACE_EVENTS_PACKET_CHECKER_MARKER}, {REVIEW_CHECKLIST_TRACE_EVENTS_SAMPLE_MARKER}, {REVIEW_CHECKLIST_SELFTEST_HOOK_MARKER}, {REVIEW_CHECKLIST_LIFECYCLE_MARKER}, the fail-closed companion {REVIEW_CHECKLIST_UNREGISTERED_GATE_MARKER} with {REVIEW_CHECKLIST_FAIL_CLOSED_MARKER}, the exit-rollback companion {REVIEW_CHECKLIST_EXIT_ROLLBACK_GUARD_MARKER} with {REVIEW_CHECKLIST_EXIT_ROLLBACK_COMPANION_MARKER}, and the re-entry companion {REVIEW_CHECKLIST_REENTRY_GATE_MARKER} with the {REVIEW_CHECKLIST_REENTRY_COMPANION_MARKER}
- the same reminder should keep the backlog posture explicit: current `master` {REVIEW_CHECKLIST_BACKLOG_MARKER}, so {REVIEW_CHECKLIST_PHASE9_BUILD_MARKER}, the shared `zigux/tests/runtime_*` replay family, {REVIEW_CHECKLIST_RUNTIME_LOADER_MARKER}, {REVIEW_CHECKLIST_RUNTIME_LOADER_CONTRACT_MARKER}, `zigux/Makefile`, {REVIEW_CHECKLIST_WORKFLOW_MARKER}, and the older {REVIEW_CHECKLIST_RUNTIME_LOADER_SCAFFOLD_MARKER} stay absent backlog references unless a fresh repo reread proves they have returned
- the same shared checklist should keep the bitmap-specific Phase 5 versus Phase 9 boundary explicit too: {REVIEW_CHECKLIST_BITMAP_PHASE5_BOUNDARY_MARKER}, {REVIEW_CHECKLIST_BITMAP_HELPER_BOUNDARY_MARKER}, and {REVIEW_CHECKLIST_BITMAP_RUNTIME_BACKLOG_MARKER} {REVIEW_CHECKLIST_BITMAP_RUNTIME_RETURN_MARKER}, and {REVIEW_CHECKLIST_TRACE_EVENTS_ONLY_MARKER} rather than treating the runtime bitmap packet as shipped current-master evidence
- the shared Phase 9 reminder should also keep the older cross-phase non-owner boundaries explicit:
  {PHASE2_CONF_BRIDGE_MARKER} and {PHASE2_CONFDATA_BRIDGE_MARKER} {PHASE2_BOUNDARY_MARKER}, while
  {PHASE3_EXPORTS_MARKER} and {PHASE3_EXPORT_SHIM_MARKER} {PHASE3_BOUNDARY_MARKER}.
"""


def build_lane_sequencing_fixture_text() -> str:
    return f"""# Phase 9 Runtime Pilot Lane Sequencing

- surviving review surfaces: `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, {PHASE9_BOUNDARY_CHECKER_MARKER}, {TRACE_EVENTS_PACKET_CHECKER_MARKER}, and `zigux/tests/README.md`
- {LANE_SEQUENCING_SAMPLE_MARKER}
- surviving runtime-module evidence inside that sample: {LANE_SEQUENCING_SELFTEST_MARKER}
- {LANE_SEQUENCING_UNREGISTERED_GATE_MARKER}
- {LANE_SEQUENCING_REENTRY_GATE_MARKER}
- surviving companion boundaries inside the same narrow packet: the {LANE_SEQUENCING_REENTRY_DETAIL_MARKER}
- {LANE_SEQUENCING_FREEZE_BOUNDARY_MARKER}
- {LANE_SEQUENCING_HISTORICAL_SURVEY_TRIO_MARKER} {LANE_SEQUENCING_HISTORICAL_VOCABULARY_MARKER}, and {LANE_SEQUENCING_NOT_OWNER_EVIDENCE_MARKER}
- {LANE_SEQUENCING_STALE_OVERCLAIM_BLOCKER_MARKER}

Current `master` {LANE_SEQUENCING_BACKLOG_MARKER} that earlier reminder surfaces described.
"""


def build_module_slice_fixture_text() -> str:
    return f"""# Phase 9 Runtime Trace-Events Module Slice

Current `master` keeps a narrow direct trace-events runtime packet through {TRACE_EVENTS_SAMPLE_MARKER}, {UNREGISTERED_GATE_SAMPLE_MARKER}, {REENTRY_GATE_SAMPLE_MARKER}, and {TRACE_EVENTS_PACKET_CHECKER_MARKER}, with {SELFTEST_HOOK_MARKER} together with {MODULE_SLICE_LIFECYCLE_MARKER} while current `master` {ABSENT_SHARED_LOADER_MARKER} that older Phase 9 reminder surfaces described.

- {MODULE_SLICE_PHASE_BOUNDARY_HEADING} {PHASE2_CONF_BRIDGE_MARKER} and {PHASE2_CONFDATA_BRIDGE_MARKER} {MODULE_SLICE_PHASE2_BOUNDARY_MARKER}, while {PHASE3_EXPORTS_MARKER} and {PHASE3_EXPORT_SHIM_MARKER} {MODULE_SLICE_PHASE3_BOUNDARY_MARKER}
"""


def build_tests_readme_fixture_text() -> str:
    return f"""# zigux/tests

Phase 9 review packet
  * the surviving trace-events sample still keeps the roadmap-backed runtime pilot shape concrete by exposing {TESTS_README_SELFTEST_HOOK_MARKER} together with {TESTS_README_LIFECYCLE_MARKER} inside {TESTS_README_TRACE_EVENTS_SAMPLE_MARKER}, while {TESTS_README_UNREGISTERED_GATE_MARKER} keeps the same narrow packet's {TESTS_README_FAIL_CLOSED_MARKER} and {TESTS_README_REENTRY_GATE_MARKER} {TESTS_README_REENTRY_COMPANION_MARKER}, so reviewers can still inspect one real runtime-module and its companion boundary while the broader shared loader packet remains backlog
  * {TESTS_README_BACKLOG_MARKER}
"""


def build_scripts_readme_fixture_text() -> str:
    return f"""# scripts/zigux

## Phase 9

- {PHASE9_SCRIPTS_PACKET_MARKER}: `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, {PHASE9_BOUNDARY_CHECKER_MARKER}, {TRACE_EVENTS_PACKET_CHECKER_MARKER}, `zigux/tests/README.md`, {SCRIPTS_README_TRACE_EVENTS_SAMPLE_MARKER}, {SCRIPTS_README_UNREGISTERED_GATE_MARKER}, and {SCRIPTS_README_REENTRY_GATE_MARKER} keep the live reminder surface honest from the scripts root
- {SCRIPTS_README_BOUNDARY_SELF_TEST_MARKER}, {SCRIPTS_README_PACKET_SELF_TEST_MARKER}, {SCRIPTS_README_BOUNDARY_LIVE_MARKER}, and {SCRIPTS_README_PACKET_LIVE_MARKER} replay the shipped bounded Phase 9 reminder checks
- {SCRIPTS_README_TRACE_EVENTS_SAMPLE_MARKER} remains the surviving direct runtime-module sample and still exposes {SCRIPTS_README_SELFTEST_HOOK_MARKER} together with {SCRIPTS_README_LIFECYCLE_MARKER}, while {SCRIPTS_README_UNREGISTERED_GATE_MARKER} keeps the same narrow packet's {SCRIPTS_README_FAIL_CLOSED_MARKER} and {SCRIPTS_README_REENTRY_GATE_MARKER} {SCRIPTS_README_REENTRY_COMPANION_MARKER}
- {SCRIPTS_README_BACKLOG_MARKER}, the shared `zigux/tests/runtime_*` replay family, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, or the older `samples/zigux/runtime_*_loader.zig` scaffolds, so treat those loader, build, kernel, workflow, and sample paths as absent backlog evidence until a fresh reread proves they returned
- {SCRIPTS_README_FREEZE_BOUNDARY_MARKER}
- keep the older non-owner boundaries explicit here too: {PHASE2_CONF_BRIDGE_MARKER} and {PHASE2_CONFDATA_BRIDGE_MARKER} {PHASE2_BOUNDARY_MARKER}, while {PHASE3_EXPORTS_MARKER} and {PHASE3_EXPORT_SHIM_MARKER} {PHASE3_BOUNDARY_MARKER}
"""


def build_samples_readme_fixture_text() -> str:
    return f"""# samples/zigux

## Phase 9 runtime pilot family

Keep `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, {PHASE9_BOUNDARY_CHECKER_MARKER}, {TRACE_EVENTS_PACKET_CHECKER_MARKER}, and `zigux/tests/README.md` aligned with that surviving direct runtime-module sample instead of reviving the removed shared loader packet by implication.

Keep the current direct runtime-module evidence explicit here too: {SAMPLES_README_TRACE_EVENTS_SAMPLE_MARKER} still exposes {SAMPLES_README_SELFTEST_HOOK_MARKER} together with {SAMPLES_README_LIFECYCLE_MARKER}.

Keep saying clearly that current `master` {SAMPLES_README_BACKLOG_MARKER}, so `zigux/tests/phase9_build.zig`, the shared `zigux/tests/runtime_*` replay family, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, and the older `samples/zigux/runtime_*_loader.zig` scaffolds stay backlog references unless a fresh repo reread proves they have returned.

Keep older cross-phase non-owner boundaries explicit: {PHASE2_CONF_BRIDGE_MARKER} and {PHASE2_CONFDATA_BRIDGE_MARKER} {PHASE2_BOUNDARY_MARKER}, while {PHASE3_EXPORTS_MARKER} and {PHASE3_EXPORT_SHIM_MARKER} {PHASE3_BOUNDARY_MARKER}.

Treat {SAMPLES_README_UNREGISTERED_GATE_MARKER} as the same narrow runtime packet's fail-closed companion for unregistered function-thread failures and {SAMPLES_README_POST_EXIT_REJECTION_MARKER}, including the {SAMPLES_README_SUMMARY_STABILITY_MARKER}, and treat {SAMPLES_README_REENTRY_GATE_MARKER} as the same packet's {SAMPLES_README_REENTRY_DETAIL_MARKER} that keeps {SAMPLES_README_REENTRY_COMPANION_MARKER}, not as proof that the broader shared loader family has returned.
"""


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def seed_fixture_tree(base: Path) -> None:
    write_text(base / DOCS_README_PATH, build_docs_readme_fixture_text())
    write_text(base / REVIEW_CHECKLIST_PATH, build_fixture_text())
    write_text(base / LANE_SEQUENCING_PATH, build_lane_sequencing_fixture_text())
    write_text(base / MODULE_SLICE_PATH, build_module_slice_fixture_text())
    write_text(base / TESTS_README_PATH, build_tests_readme_fixture_text())
    write_text(base / SCRIPTS_README_PATH, build_scripts_readme_fixture_text())
    write_text(base / SAMPLES_README_PATH, build_samples_readme_fixture_text())


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase9-review-checklist-boundaries-"))
    try:
        seed_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        for marker in DOCS_README_REQUIRED_MARKERS:
            seed_fixture_tree(base)
            write_text(base / DOCS_README_PATH, build_docs_readme_fixture_text().replace(marker, ""))
            expect_failure(base, f"missing_marker:{DOCS_README_PATH}:{marker}")

        for marker in CHECKLIST_REQUIRED_MARKERS:
            seed_fixture_tree(base)
            write_text(base / REVIEW_CHECKLIST_PATH, build_fixture_text().replace(marker, ""))
            expect_failure(base, f"missing_marker:{REVIEW_CHECKLIST_PATH}:{marker}")

        for marker in LANE_SEQUENCING_REQUIRED_MARKERS:
            seed_fixture_tree(base)
            write_text(base / LANE_SEQUENCING_PATH, build_lane_sequencing_fixture_text().replace(marker, ""))
            expect_failure(base, f"missing_marker:{LANE_SEQUENCING_PATH}:{marker}")

        for marker in MODULE_SLICE_REQUIRED_MARKERS:
            seed_fixture_tree(base)
            write_text(base / MODULE_SLICE_PATH, build_module_slice_fixture_text().replace(marker, ""))
            expect_failure(base, f"missing_marker:{MODULE_SLICE_PATH}:{marker}")

        for marker in TESTS_README_REQUIRED_MARKERS:
            seed_fixture_tree(base)
            write_text(base / TESTS_README_PATH, build_tests_readme_fixture_text().replace(marker, ""))
            expect_failure(base, f"missing_marker:{TESTS_README_PATH}:{marker}")

        for marker in SCRIPTS_README_REQUIRED_MARKERS:
            seed_fixture_tree(base)
            write_text(base / SCRIPTS_README_PATH, build_scripts_readme_fixture_text().replace(marker, ""))
            expect_failure(base, f"missing_marker:{SCRIPTS_README_PATH}:{marker}")

        for marker in SAMPLES_README_REQUIRED_MARKERS:
            seed_fixture_tree(base)
            write_text(base / SAMPLES_README_PATH, build_samples_readme_fixture_text().replace(marker, ""))
            expect_failure(base, f"missing_marker:{SAMPLES_README_PATH}:{marker}")

        for rel_path in [
            DOCS_README_PATH,
            REVIEW_CHECKLIST_PATH,
            LANE_SEQUENCING_PATH,
            MODULE_SLICE_PATH,
            TESTS_README_PATH,
            SCRIPTS_README_PATH,
            SAMPLES_README_PATH,
        ]:
            seed_fixture_tree(base)
            (base / rel_path).unlink()
            expect_failure(base, f"missing_file:{rel_path}")
    finally:
        shutil.rmtree(base, ignore_errors=True)

    print("PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_SELF_TEST=pass")
    print(f"PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_DOCS_README_MARKER_COUNT={len(DOCS_README_REQUIRED_MARKERS)}")
    print(f"PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_CHECKLIST_MARKER_COUNT={len(CHECKLIST_REQUIRED_MARKERS)}")
    print(f"PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_LANE_SEQUENCING_MARKER_COUNT={len(LANE_SEQUENCING_REQUIRED_MARKERS)}")
    print(f"PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_MODULE_SLICE_MARKER_COUNT={len(MODULE_SLICE_REQUIRED_MARKERS)}")
    print(f"PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_TESTS_README_MARKER_COUNT={len(TESTS_README_REQUIRED_MARKERS)}")
    print(f"PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_SCRIPTS_README_MARKER_COUNT={len(SCRIPTS_README_REQUIRED_MARKERS)}")
    print(f"PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_SAMPLES_README_MARKER_COUNT={len(SAMPLES_README_REQUIRED_MARKERS)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 9 review checklist, docs-root summary, lane-sequencing summary, trace-events module-slice note, tests-root guide, scripts-root reminder, and samples-root reminder all keep the surviving trace-events runtime packet, fail-closed companion, balanced registration re-entry companion, backlog posture, the older runtime-loader survey trio's historical-only status, and older Phase 2 versus Phase 3 non-owner boundaries explicit."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=ROOT,
        help="repository root to inspect",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run the built-in checker self-test and exit",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.repo_root)
    if failures:
        for failure in failures:
            print(f"PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_ERROR={failure}")
        return 1

    print(f"PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_DOCS_README_MARKER_COUNT={len(DOCS_README_REQUIRED_MARKERS)}")
    print(f"PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_CHECKLIST_MARKER_COUNT={len(CHECKLIST_REQUIRED_MARKERS)}")
    print(f"PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_LANE_SEQUENCING_MARKER_COUNT={len(LANE_SEQUENCING_REQUIRED_MARKERS)}")
    print(f"PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_MODULE_SLICE_MARKER_COUNT={len(MODULE_SLICE_REQUIRED_MARKERS)}")
    print(f"PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_TESTS_README_MARKER_COUNT={len(TESTS_README_REQUIRED_MARKERS)}")
    print(f"PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_SCRIPTS_README_MARKER_COUNT={len(SCRIPTS_README_REQUIRED_MARKERS)}")
    print(f"PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_SAMPLES_README_MARKER_COUNT={len(SAMPLES_README_REQUIRED_MARKERS)}")
    print("PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
