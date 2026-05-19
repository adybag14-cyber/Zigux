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
MAKEFILE_PATH = "zigux/Makefile"

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
TESTS_README_EXIT_ROLLBACK_GUARD_MARKER = "`samples/zigux/runtime_trace_events_exit_rollback_guard.zig`"
TESTS_README_REENTRY_GATE_MARKER = "`samples/zigux/runtime_trace_events_registration_reentry_gate.zig`"
TESTS_README_FAIL_CLOSED_MARKER = "unregistered function-thread failures fail-closed"
TESTS_README_EXIT_ROLLBACK_COMPANION_MARKER = "failed-exit rollback explicit after reusable selftest replay"
TESTS_README_REENTRY_COMPANION_MARKER = "keeps balanced function-thread registration reusable before and after selftest"
TESTS_README_BACKLOG_MARKER = "there is no shared `zigux/tests/runtime_*` replay packet, `zigux/tests/phase9_build.zig`, `make -C zigux phase9*` route family, or dedicated shared `validate-phase9.py` visible on current `master`"

DOCS_README_PHASE9_NOTES_MARKER = "Phase 9 notes - `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`"
DOCS_README_TRACE_EVENTS_SAMPLE_MARKER = "`samples/zigux/runtime_trace_events.zig`"
DOCS_README_SELFTEST_HOOK_MARKER = "`.provides_selftest_hook = true`"
DOCS_README_LIFECYCLE_MARKER = "initialized, selftest_complete, and exited lifecycle tracking"
DOCS_README_UNREGISTERED_GATE_MARKER = "`samples/zigux/runtime_trace_events_unregistered_gate.zig`"
DOCS_README_EXIT_ROLLBACK_GUARD_MARKER = "`samples/zigux/runtime_trace_events_exit_rollback_guard.zig`"
DOCS_README_REENTRY_GATE_MARKER = "`samples/zigux/runtime_trace_events_registration_reentry_gate.zig`"
DOCS_README_FAIL_CLOSED_MARKER = "unregistered function-thread failures fail-closed"
DOCS_README_EXIT_ROLLBACK_COMPANION_MARKER = "failed-exit rollback explicit after reusable selftest replay"
DOCS_README_REENTRY_COMPANION_MARKER = "balanced function-thread registration reusable across the initialized and selftest_complete stages"
DOCS_README_BACKLOG_MARKER = "does not currently expose the broader shared runtime-loader packet"
DOCS_README_PHASE2_BOUNDARY_MARKER = "remain Phase 2 config-surface bridge references"
DOCS_README_PHASE3_BOUNDARY_MARKER = "remain Phase 3 export-boundary references rather than runtime-pilot evidence"

SCRIPTS_README_TRACE_EVENTS_SAMPLE_MARKER = "`samples/zigux/runtime_trace_events.zig`"
SCRIPTS_README_UNREGISTERED_GATE_MARKER = "`samples/zigux/runtime_trace_events_unregistered_gate.zig`"
SCRIPTS_README_EXIT_ROLLBACK_GUARD_MARKER = "`samples/zigux/runtime_trace_events_exit_rollback_guard.zig`"
SCRIPTS_README_REENTRY_GATE_MARKER = "`samples/zigux/runtime_trace_events_registration_reentry_gate.zig`"
SCRIPTS_README_SELFTEST_HOOK_MARKER = "`.provides_selftest_hook = true`"
SCRIPTS_README_LIFECYCLE_MARKER = "initialized, selftest_complete, and exited lifecycle tracking"
SCRIPTS_README_FAIL_CLOSED_MARKER = "unregistered function-thread failures fail-closed"
SCRIPTS_README_EXIT_ROLLBACK_COMPANION_MARKER = "failed-exit rollback explicit after reusable selftest replay together with later post-exit invalid-lifecycle rejections"
SCRIPTS_README_REENTRY_COMPANION_MARKER = "keeps balanced function-thread registration reusable before and after selftest"
SCRIPTS_README_BACKLOG_MARKER = "current `master` still does not materialize `zigux/tests/phase9_build.zig`"
SCRIPTS_README_BOUNDARY_SELF_TEST_MARKER = "`python3 scripts/zigux/check-phase9-review-checklist-phase-boundaries.py --self-test`"
SCRIPTS_README_PACKET_SELF_TEST_MARKER = "`python3 scripts/zigux/check-phase9-trace-events-runtime-packet.py --self-test`"
SCRIPTS_README_BOUNDARY_LIVE_MARKER = "`python3 scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`"
SCRIPTS_README_PACKET_LIVE_MARKER = "`python3 scripts/zigux/check-phase9-trace-events-runtime-packet.py`"
SCRIPTS_README_FREEZE_BOUNDARY_MARKER = "keep the freeze-map boundary explicit too: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only anchors through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` rather than Phase 9 runtime-substrate readiness cues"
SCRIPTS_README_MAKEFILE_BOUNDARY_MARKER = "keep `zigux/Makefile` explicit only as a readable non-owner surface whose live body still lacks dedicated `phase9-*` runtime-pilot routes"

SAMPLES_README_TRACE_EVENTS_SAMPLE_MARKER = "`samples/zigux/runtime_trace_events.zig`"
SAMPLES_README_SELFTEST_HOOK_MARKER = "`.provides_selftest_hook = true`"
SAMPLES_README_LIFECYCLE_MARKER = "initialized, selftest_complete, and exited lifecycle tracking"
SAMPLES_README_BACKLOG_MARKER = "does not currently expose the broader shared runtime-loader packet"
SAMPLES_README_UNREGISTERED_GATE_MARKER = "`samples/zigux/runtime_trace_events_unregistered_gate.zig`"
SAMPLES_README_REENTRY_GATE_MARKER = "`samples/zigux/runtime_trace_events_registration_reentry_gate.zig`"
SAMPLES_README_REENTRY_COMPANION_MARKER = "balanced function-thread registration reusable before and after selftest"
SAMPLES_README_REENTRY_DETAIL_MARKER = "balanced registration re-entry companion across the initialized and selftest_complete stages"
SAMPLES_README_EXIT_ROLLBACK_GUARD_DETAIL_MARKER = "`samples/zigux/runtime_trace_events_exit_rollback_guard.zig` keeps failed-exit rollback explicit after reusable selftest replay"
SAMPLES_README_POST_EXIT_REJECTION_MARKER = "post-exit invalid-lifecycle rejections"
SAMPLES_README_SUMMARY_STABILITY_MARKER = "initialized-before/after, selftest_complete-before/after, and exited-before/after summary-stability checks"

TRACE_EVENTS_SAMPLE_MARKER = "`samples/zigux/runtime_trace_events.zig`"
UNREGISTERED_GATE_SAMPLE_MARKER = "`samples/zigux/runtime_trace_events_unregistered_gate.zig`"
REENTRY_GATE_SAMPLE_MARKER = "`samples/zigux/runtime_trace_events_registration_reentry_gate.zig`"
SELFTEST_HOOK_MARKER = "`.provides_selftest_hook = true`"
ABSENT_SHARED_LOADER_MARKER = "does not currently expose the broader shared runtime-loader packet"

MODULE_SLICE_PHASE_BOUNDARY_HEADING = "Keep earlier-phase references in their own lanes:"
MODULE_SLICE_LIFECYCLE_MARKER = "initialized, selftest_complete, and exited sample-local lifecycle tracking"
MODULE_SLICE_PHASE2_BOUNDARY_MARKER = "remain Phase 2 references"
MODULE_SLICE_PHASE3_BOUNDARY_MARKER = "remain Phase 3 export-boundary references."

MAKEFILE_FORBIDDEN_ROUTE_FIXTURES = ["phase9-test", "phase9-runtime-trace-events-sample-tests", "phase9"]

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
    TESTS_README_EXIT_ROLLBACK_GUARD_MARKER,
    TESTS_README_REENTRY_GATE_MARKER,
    TESTS_README_SELFTEST_HOOK_MARKER,
    TESTS_README_LIFECYCLE_MARKER,
    TESTS_README_FAIL_CLOSED_MARKER,
    TESTS_README_EXIT_ROLLBACK_COMPANION_MARKER,
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
    DOCS_README_EXIT_ROLLBACK_GUARD_MARKER,
    DOCS_README_REENTRY_GATE_MARKER,
    DOCS_README_FAIL_CLOSED_MARKER,
    DOCS_README_EXIT_ROLLBACK_COMPANION_MARKER,
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
    SCRIPTS_README_EXIT_ROLLBACK_GUARD_MARKER,
    SCRIPTS_README_REENTRY_GATE_MARKER,
    SCRIPTS_README_SELFTEST_HOOK_MARKER,
    SCRIPTS_README_LIFECYCLE_MARKER,
    SCRIPTS_README_FAIL_CLOSED_MARKER,
    SCRIPTS_README_EXIT_ROLLBACK_COMPANION_MARKER,
    SCRIPTS_README_REENTRY_COMPANION_MARKER,
    SCRIPTS_README_BACKLOG_MARKER,
    SCRIPTS_README_MAKEFILE_BOUNDARY_MARKER,
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
    SAMPLES_README_EXIT_ROLLBACK_GUARD_DETAIL_MARKER,
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

REQUIRED_MARKERS = {
    DOCS_README_PATH: DOCS_README_REQUIRED_MARKERS,
    REVIEW_CHECKLIST_PATH: CHECKLIST_REQUIRED_MARKERS,
    LANE_SEQUENCING_PATH: LANE_SEQUENCING_REQUIRED_MARKERS,
    MODULE_SLICE_PATH: MODULE_SLICE_REQUIRED_MARKERS,
    TESTS_README_PATH: TESTS_README_REQUIRED_MARKERS,
    SCRIPTS_README_PATH: SCRIPTS_README_REQUIRED_MARKERS,
    SAMPLES_README_PATH: SAMPLES_README_REQUIRED_MARKERS,
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def find_makefile_phase9_routes(text: str) -> list[str]:
    routes: list[str] = []
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith(".PHONY:"):
            continue
        if stripped.startswith("phase9") and ":" in stripped:
            routes.append(stripped.split(":", 1)[0])
    return routes


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path in [*REQUIRED_MARKERS, MAKEFILE_PATH]:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")
    if failures:
        return failures

    for rel_path, markers in REQUIRED_MARKERS.items():
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                failures.append(f"missing_marker:{rel_path}:{marker}")

    makefile = read_text(root, MAKEFILE_PATH)
    for route in find_makefile_phase9_routes(makefile):
        failures.append(f"unexpected_phase9_route:{MAKEFILE_PATH}:{route}")

    return failures


def build_fixture_text(rel_path: str) -> str:
    if rel_path == MAKEFILE_PATH:
        return """PYTHON ?= python3
ZIG ?= zig
ZIGUX_ROOT := ..

.PHONY: phase8-test phase10-test phase12-test

phase8-test:
\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase8_build.zig --summary all

phase10-test:
\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase10_build.zig --summary all

phase12-test:
\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase12_build.zig --summary all
"""
    return "# fixture\n\n" + "\n".join(REQUIRED_MARKERS[rel_path]) + "\n"


def seed_fixture_tree(base: Path) -> None:
    for rel_path in [*REQUIRED_MARKERS, MAKEFILE_PATH]:
        write_text(base / rel_path, build_fixture_text(rel_path))


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase9-review-checklist-boundaries-"))
    try:
        seed_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        for rel_path, markers in REQUIRED_MARKERS.items():
            for marker in markers:
                seed_fixture_tree(base)
                current = read_text(base, rel_path)
                write_text(base / rel_path, current.replace(marker, ""))
                expect_failure(base, f"missing_marker:{rel_path}:{marker}")

        for route in MAKEFILE_FORBIDDEN_ROUTE_FIXTURES:
            seed_fixture_tree(base)
            current = read_text(base, MAKEFILE_PATH)
            write_text(base / MAKEFILE_PATH, current + f"\n{route}:\n\t@true\n")
            expect_failure(base, f"unexpected_phase9_route:{MAKEFILE_PATH}:{route}")

        for rel_path in [*REQUIRED_MARKERS, MAKEFILE_PATH]:
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
    print(f"PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_FORBIDDEN_MAKEFILE_ROUTE_COUNT={len(MAKEFILE_FORBIDDEN_ROUTE_FIXTURES)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 9 review checklist, docs-root summary, lane-sequencing summary, trace-events module-slice note, tests-root guide, scripts-root reminder, samples-root reminder, and live Makefile posture all keep the surviving trace-events runtime packet, backlog posture, older runtime-loader-survey historical-only status, older Phase 2 versus Phase 3 non-owner boundaries, and the no-Phase-9-make-route policy explicit."
    )
    parser.add_argument("--repo-root", type=Path, default=ROOT, help="repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test and exit")
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
    print(f"PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_FORBIDDEN_MAKEFILE_ROUTE_COUNT={len(MAKEFILE_FORBIDDEN_ROUTE_FIXTURES)}")
    print("PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
