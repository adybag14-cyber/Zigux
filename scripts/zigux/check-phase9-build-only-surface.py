#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / "Documentation/zigux/README.md").exists() and (candidate / "zigux/Makefile").exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()

FREEZE_MAP_PATH = "Documentation/zigux/freeze-map.md"
PHASE9_LANE_SEQUENCING_PATH = "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md"
PHASE9_GAP_SURVEY_NOTE_PATH = "Documentation/zigux/phase9-runtime-loader-gap-survey.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
README_PATH = "Documentation/zigux/README.md"
SCRIPTS_README_PATH = "scripts/zigux/README.md"
TESTS_README_PATH = "zigux/tests/README.md"
MAKEFILE_PATH = "zigux/Makefile"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"
PHASE9_BUILD_PATH = "zigux/tests/phase9_build.zig"
RUNTIME_LOADER_PATH = "zigux/kernel/runtime_loader.zig"
RUNTIME_LOADER_CONTRACT_PATH = "zigux/kernel/runtime_loader_contract.zig"
ALLOCATOR_INIT_FLOW_PATH = "zigux/tests/runtime_loader_allocator_init_flow.zig"
RUNTIME_LOADER_SELFTEST_COMPLETE_EXIT_PARITY_PATH = "zigux/tests/runtime_loader_selftest_complete_exit_parity.zig"
LOADER_GAP_MANIFEST_PATH = "zigux/tests/runtime_loader_gap_manifest.json"
LOADER_GAP_SURVEY_PATH = "zigux/tests/runtime_loader_gap_survey.zig"
RUNTIME_LOADER_LIFECYCLE_BOUNDARY_GUARD_PATH = "zigux/tests/runtime_loader_lifecycle_boundary_guard.zig"
TRACE_EVENTS_SUBSTRATE_DRIFT_PATH = "zigux/tests/runtime_trace_events_loader_substrate_drift.zig"

FREEZE_MAP_TRACE_BOUNDARY_MARKER = (
    "the shared Phase 9 runtime-loader packet stays review-only beside `kernel/workqueue.c` and `kernel/trace/ring_buffer.c`"
)
PREPARED_STATE_LANDED_MARKER = (
    "direct readback now also shows `zigux/tests/runtime_loader_allocator_init_flow.zig` already keeps the prepared-plan drift replay explicit across rejected `requestRuntimeLoad()` calls"
)
PREPARED_STATE_EXPLICIT_ASSERTION_MARKER = """request.plan.module_name = \"runtime_trace_events_drift\";
    try std.testing.expectError(error.PreparedPlanDrift, request.requestRuntimeLoad());
    try expectPreparedPlanDriftKeepsPreparedState(request, stable_plan);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(request, .prepared, request.plan));
    try std.testing.expectEqualStrings(stable_plan.module_name, request.prepared_plan.module_name);"""
PREPARED_STATE_ALLOCATOR_HANDOFF_EXPLICIT_ASSERTION_MARKER = """request.plan.allocator_handoff = .arena;
    try std.testing.expectError(error.PreparedPlanDrift, request.requestRuntimeLoad());
    try expectPreparedPlanDriftKeepsPreparedState(request, stable_plan);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(request, .prepared, request.plan));
    try std.testing.expectEqual(runtime_loader.AllocatorHandoff.caller_provided, request.prepared_plan.allocator_handoff);"""
GAP_SURVEY_DRIFT_MARKER = (
    "direct readback now also shows `scripts/zigux/README.md` and `zigux/tests/README.md` both keep `zigux/tests/runtime_loader_gap_survey.zig` explicit beside the shared loader-facing packet, so the remaining shared reminder follow-through has narrowed back to reviewer-facing truthfulness around the still-blocked module-metadata and depmod-publication boundary instead of loader-gap inventory sync"
)
GAP_SURVEY_NEXT_STEP_MARKER = (
    "If the shared reminder packet already defers correctly to this note, refresh the smallest shipped shared summary that still undercounts the live shared loader packet or drifts around the blocked module-metadata and depmod-publication boundary and the stale repo-root loader inventory, starting with `Documentation/zigux/README.md`, then `zigux/tests/README.md`, while keeping `scripts/zigux/README.md` parked unless a later reread shows it reclaiming family-local owner-map detail again."
)
PHASE9_GAP_SURVEY_NOTE_TRACE_EVENTS_PROOF_MARKER = "`zigux/tests/runtime_trace_events_loader_substrate_drift.zig`"
DEP_MOD_BOUNDARY_MARKER = (
    "the shared module-metadata and depmod-publication boundary is still blocked in the live loader packet: `.modinfo`, `MODULE_ALIAS()`, `modules.alias`, `modules.order`, `modules.builtin`, module install-root, `Module.symvers`, and `depmod` script, manifest, or alias publication state remain review-only boundary references rather than shipped publication surfaces"
)
DOCS_ROOT_DEPMOD_BOUNDARY_MARKER = (
    "`.modinfo`, `MODULE_ALIAS()`, `modules.alias`, `modules.order`, `modules.builtin`, module install-root, and `depmod` script or manifest state stay blocked review-only boundaries"
)
DOCS_ROOT_SELFTEST_COMPLETE_EXIT_PARITY_MARKER = "`zigux/tests/runtime_loader_selftest_complete_exit_parity.zig`"
DOCS_ROOT_LIFECYCLE_BOUNDARY_GUARD_MARKER = "`zigux/tests/runtime_loader_lifecycle_boundary_guard.zig`"
DOCS_ROOT_TRACE_EVENTS_SUBSTRATE_DRIFT_MARKER = "`zigux/tests/runtime_trace_events_loader_substrate_drift.zig`"
REVIEW_CHECKLIST_TRACE_EVENTS_LOADER_MARKER = (
    "with `samples/zigux/runtime_trace_events_loader.zig` kept explicit as a shipped shared-loader scaffold while `samples/zigux/runtime_trace_events.zig` plus `zigux/tests/runtime_trace_events_manifest.json` remain the sample-only blocked pilot boundary for live runtime substrate and tracepoint-registration execution"
)
REVIEW_CHECKLIST_DEPMOD_BOUNDARY_MARKER = (
    "the shared module-metadata and depmod-publication boundary still blocked in the live loader packet so `.modinfo`, `MODULE_ALIAS()`, `modules.alias`, `modules.order`, `modules.builtin`, module install-root, and `depmod` script or manifest state remain review-only boundary references rather than shipped publication surfaces"
)
REVIEW_CHECKLIST_PHASE8_BOUNDARY_MARKER = (
    "while the older Phase 8 command and environment control cues stay with `tools/lib/subcmd/exec-cmd.zig` and `tools/lib/subcmd/help.zig`"
)
PHASE9_LANE_SEQUENCING_PHASE8_BOUNDARY_MARKER = (
    "`tools/lib/subcmd/exec-cmd.zig` and `tools/lib/subcmd/help.zig` remain earlier-phase command and environment cue owners"
)
PHASE9_LANE_SEQUENCING_LIFECYCLE_BOUNDARY_MARKER = (
    "`zigux/tests/runtime_loader_lifecycle_boundary_guard.zig` keeps the shared request-state and registration-boundary guard explicit"
)
PHASE9_LANE_SEQUENCING_TRACE_EVENTS_SHARED_ROUTE_MARKER = (
    "`zigux/tests/runtime_trace_events_loader_substrate_drift.zig` now rides the same `phase9-runtime-loader-shared-tests` bundle while staying trace-events-local for pilot-family ownership"
)
PHASE9_LANE_SEQUENCING_DEPMOD_ALIASES_BOUNDARY_MARKER = (
    "direct readback now also shows `zigux/kernel/runtime_loader_contract.zig` keeps `depmod_aliases` outside the shared `LoadPlan` beside `depmod_script` and `depmod_manifest`, so the shared owner-map note should keep depmod alias publication state parked with that same blocked module-metadata boundary instead of implying alias publication has moved into the shipped loader packet"
)
PHASE9_LANE_SEQUENCING_SHARED_OWNER_MAP_SOURCE_MARKER = (
    "The family-local manifests under `zigux/tests/runtime_*_manifest.json` are the source of truth for these lane labels, and their shared-owner-map references should point back to `P9-L11` when the broader loader-facing packet stays healthy."
)
PHASE9_LANE_SEQUENCING_ATOMIC64_OWNER_SPLIT_MARKER = (
    "the current atomic64 follow-through is the manifest-backed survey-versus-module-slice packet tracked in `P9-L04`, with the shared loader-facing owner map staying adjacent through `P9-L11`"
)
PHASE9_LANE_SEQUENCING_BITMAP_OWNER_SPLIT_MARKER = (
    "Keep bitmap-local proof there while `P9-L11` owns the shared loader-facing reminder packet."
)
LANE_NOTE_BITMAP_TOP_BIT_SPLIT_MARKER = (
    "`Documentation/zigux/review-checklist.md` now keeps the shared-loader split visible by naming the shipped `phase9-runtime-bitmap-top-bit-tests` step beside `samples/zigux/runtime_bitmap_top_bit_contract.zig`, while the bitmap-local `zig build phase9-runtime-bitmap-tests --build-file zigux/tests/phase9_build.zig` replay stays with the family packet instead of being flattened into shared loader evidence, and it remains the reviewer-facing surface that also restates the older command and environment ownership boundaries, while the shared `python3 scripts/zigux/check-phase9-build-only-surface.py --self-test` hook stays part of the same loader-owned validation packet"
)
PHASE9_GAP_SURVEY_NOTE_STATUS_MARKER = "PHASE9_SLICE=runtime-loader-gap-survey"
PHASE9_GAP_SURVEY_NOTE_ROUTE_MARKER = "`make -C zigux phase9-runtime-loader-shared-tests`"
PHASE9_GAP_SURVEY_NOTE_BOUNDARY_MARKER = "`depmod` script or manifest state"
LOADER_GAP_MANIFEST_NOTE_SURFACE_MARKER = '"surface": "Documentation/zigux/phase9-runtime-loader-gap-survey.md"'
LOADER_GAP_MANIFEST_ROUTE_MARKER = '"current_honest_gate": "make -C zigux phase9-runtime-loader-shared-tests"'
LOADER_GAP_MANIFEST_BOUNDARY_MARKER = '"id": "runtime-loader-publication-metadata"'
LOADER_GAP_MANIFEST_CHECKLIST_BOUNDARY_FLAG_MARKER = '"review_checklist_cross_phase_non_owner_boundary_present": false'
LOADER_GAP_MANIFEST_CHECKLIST_REMINDER_GAP_MARKER = '"id": "runtime-loader-checklist-cross-phase-non-owner-reminder"'
PHASE9_TRACE_EVENTS_SUBSTRATE_DRIFT_BUILD_MARKER = "\"phase9-runtime-trace-events-loader-substrate-drift-tests\""
PHASE9_TRACE_EVENTS_SUBSTRATE_DRIFT_MAKE_MARKER = (
    "$(ZIG) build phase9-runtime-trace-events-loader-substrate-drift-tests --build-file zigux/tests/phase9_build.zig"
)
TRACE_EVENTS_SUBSTRATE_DRIFT_PREPARED_PLAN_MARKER = "error.PreparedPlanDrift"
TRACE_EVENTS_SUBSTRATE_DRIFT_SELFTEST_HOOK_EXPLICIT_MARKER = (
    "try std.testing.expect(!runtime_loader.keepsSelftestHookEvidenceConsistent(shared_request.plan));"
)
RUNTIME_LOADER_CONTRACT_TEST_MARKER = (
    'test "shared runtime loader contract keeps registration-summary, publication, and depmod surfaces outside the request contract"'
)
RUNTIME_LOADER_CONTRACT_MODINFO_MARKER = '"modinfo"'
RUNTIME_LOADER_CONTRACT_MODULE_ALIAS_MARKER = '"module_alias"'
RUNTIME_LOADER_CONTRACT_MODULES_ALIAS_PATH_MARKER = '"modules_alias_path"'
RUNTIME_LOADER_CONTRACT_MODULE_INSTALL_ROOT_MARKER = '"module_install_root"'
RUNTIME_LOADER_CONTRACT_MODULES_ORDER_PATH_MARKER = '"modules_order_path"'
RUNTIME_LOADER_CONTRACT_MODULES_BUILTIN_PATH_MARKER = '"modules_builtin_path"'
RUNTIME_LOADER_CONTRACT_MODULE_SYMVERS_PATH_MARKER = '"module_symvers_path"'
RUNTIME_LOADER_CONTRACT_DEPMOD_SCRIPT_MARKER = '"depmod_script"'
RUNTIME_LOADER_CONTRACT_DEPMOD_MANIFEST_MARKER = '"depmod_manifest"'
RUNTIME_LOADER_CONTRACT_DEPMOD_ALIASES_MARKER = '"depmod_aliases"'
RUNTIME_LOADER_LIFECYCLE_BOUNDARY_CHECKLIST_TEST_MARKER = (
    "phase 9 runtime loader lifecycle boundary guard keeps shared review-checklist boundary markers explicit"
)
ALLOCATOR_INIT_FLOW_LIFECYCLE_LABEL_FIELD_MARKER = "metadata_only_lifecycle_labels: []const []const u8,"
ALLOCATOR_INIT_FLOW_LIFECYCLE_LABEL_LEN_MARKER = (
    "try std.testing.expectEqual(@as(usize, 2), kretprobe.value.lifecycle_boundary_summary.metadata_only_lifecycle_labels.len);"
)
ALLOCATOR_INIT_FLOW_KRETPROBE_INIT_LABEL_MARKER = (
    '"zigux_runtime_kretprobe_init", kretprobe.value.lifecycle_boundary_summary.metadata_only_lifecycle_labels[0]'
)
ALLOCATOR_INIT_FLOW_KRETPROBE_EXIT_LABEL_MARKER = (
    '"zigux_runtime_kretprobe_exit", kretprobe.value.lifecycle_boundary_summary.metadata_only_lifecycle_labels[1]'
)
OWNER_MAP_MARKERS = [
    "- `P9-L04`: owns the current runtime atomic64 manifest-backed survey-versus-module-slice packet.",
    "- `P9-L08`: owns the current runtime bitmap manifest, survey note, module-slice note, focused top-bit companion replay, and survey gate packet.",
    "- `P9-L10`: owns the current runtime trace-events manifest, survey note, module-slice note, and survey-gate packet.",
    "- `P9-L13`: owns the current runtime kretprobe manifest-backed loader-plan, survey-gate lifecycle, and tracing proof follow-through.",
]

REQUIRED_FILES = [
    FREEZE_MAP_PATH,
    PHASE9_LANE_SEQUENCING_PATH,
    PHASE9_GAP_SURVEY_NOTE_PATH,
    REVIEW_CHECKLIST_PATH,
    README_PATH,
    SCRIPTS_README_PATH,
    TESTS_README_PATH,
    MAKEFILE_PATH,
    WORKFLOW_PATH,
    PHASE9_BUILD_PATH,
    RUNTIME_LOADER_PATH,
    RUNTIME_LOADER_CONTRACT_PATH,
    ALLOCATOR_INIT_FLOW_PATH,
    RUNTIME_LOADER_SELFTEST_COMPLETE_EXIT_PARITY_PATH,
    LOADER_GAP_MANIFEST_PATH,
    LOADER_GAP_SURVEY_PATH,
    RUNTIME_LOADER_LIFECYCLE_BOUNDARY_GUARD_PATH,
    TRACE_EVENTS_SUBSTRATE_DRIFT_PATH,
    "samples/zigux/runtime_atomic64_loader.zig",
    "samples/zigux/runtime_bitmap_loader.zig",
    "samples/zigux/runtime_bitmap_top_bit_contract.zig",
    "samples/zigux/runtime_trace_events_loader.zig",
    "samples/zigux/runtime_kretprobe_loader.zig",
]

FORBIDDEN_FILES = [
    "scripts/zigux/validate-phase9.py",
    "scripts/zigux/check-phase9-validation-flow.py",
    "scripts/zigux/check-phase9-runtime-loader-commit-alignment.py",
    "scripts/zigux/check-phase9-loader-substrate-plan.py",
]

REQUIRED_MARKERS = {
    FREEZE_MAP_PATH: [
        "kernel/workqueue.c",
        "kernel/trace/ring_buffer.c",
        FREEZE_MAP_TRACE_BOUNDARY_MARKER,
        "`scripts/zigux/check-phase9-build-only-surface.py`",
        "`zigux/tests/phase9_build.zig`",
        "`zigux/kernel/runtime_loader.zig`",
        "`zigux/kernel/runtime_loader_contract.zig`",
    ],
    PHASE9_LANE_SEQUENCING_PATH: [
        PREPARED_STATE_LANDED_MARKER,
        GAP_SURVEY_DRIFT_MARKER,
        GAP_SURVEY_NEXT_STEP_MARKER,
        DEP_MOD_BOUNDARY_MARKER,
        PHASE9_LANE_SEQUENCING_DEPMOD_ALIASES_BOUNDARY_MARKER,
        PHASE9_LANE_SEQUENCING_PHASE8_BOUNDARY_MARKER,
        PHASE9_LANE_SEQUENCING_LIFECYCLE_BOUNDARY_MARKER,
        PHASE9_LANE_SEQUENCING_TRACE_EVENTS_SHARED_ROUTE_MARKER,
        PHASE9_LANE_SEQUENCING_SHARED_OWNER_MAP_SOURCE_MARKER,
        PHASE9_LANE_SEQUENCING_ATOMIC64_OWNER_SPLIT_MARKER,
        PHASE9_LANE_SEQUENCING_BITMAP_OWNER_SPLIT_MARKER,
        LANE_NOTE_BITMAP_TOP_BIT_SPLIT_MARKER,
        *OWNER_MAP_MARKERS,
        "the shipped `scripts/zigux/check-phase9-build-only-surface.py` guard should still fail closed if this note regresses around either the shared owner split or the blocked module-metadata and depmod-publication boundary markers",
    ],
    PHASE9_GAP_SURVEY_NOTE_PATH: [
        PHASE9_GAP_SURVEY_NOTE_STATUS_MARKER,
        PHASE9_GAP_SURVEY_NOTE_ROUTE_MARKER,
        "There is no dedicated shared `validate-phase9.py`",
        "samples/zigux/runtime_kretprobe_loader.zig",
        PHASE9_GAP_SURVEY_NOTE_TRACE_EVENTS_PROOF_MARKER,
        PHASE9_GAP_SURVEY_NOTE_BOUNDARY_MARKER,
    ],
    REVIEW_CHECKLIST_PATH: [
        "`scripts/zigux/check-phase9-build-only-surface.py`",
        "`Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`",
        "without overstating missing shared-loader paths as shipped current-`master` evidence",
        "the owner of the exact shared-loader target list, convenience-target names, and repo-reality blocker posture",
        "workflow-backed `make -C zigux phase9` route",
        "no-dedicated-`validate-phase9.py` posture",
        REVIEW_CHECKLIST_TRACE_EVENTS_LOADER_MARKER,
        REVIEW_CHECKLIST_DEPMOD_BOUNDARY_MARKER,
        REVIEW_CHECKLIST_PHASE8_BOUNDARY_MARKER,
    ],
    README_PATH: [
        "`Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`",
        "`scripts/zigux/check-phase9-build-only-surface.py`",
        "`zigux/tests/phase9_build.zig`",
        "`zigux/kernel/runtime_loader.zig`",
        "`zigux/kernel/runtime_loader_contract.zig`",
        "`zigux/tests/runtime_loader_gap_manifest.json`",
        DOCS_ROOT_SELFTEST_COMPLETE_EXIT_PARITY_MARKER,
        DOCS_ROOT_LIFECYCLE_BOUNDARY_GUARD_MARKER,
        DOCS_ROOT_TRACE_EVENTS_SUBSTRATE_DRIFT_MARKER,
        "loader-gap survey note plus manifest-backed survey gate",
        "the shared Phase 9 packet is still review-first rather than loadable-runtime-complete",
        DOCS_ROOT_DEPMOD_BOUNDARY_MARKER,
    ],
    SCRIPTS_README_PATH: [
        "Phase 9 flow",
        "`Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` remains the shared owner map",
        "`Documentation/zigux/phase9-runtime-loader-gap-survey.md`",
        "`zigux/tests/runtime_loader_gap_manifest.json`",
        "`zigux/tests/runtime_loader_gap_survey.zig`",
        "there is no dedicated shared `validate-phase9.py`",
    ],
    TESTS_README_PATH: [
        "`zigux/tests/runtime_loader_allocator_init_flow.zig`",
        "`zigux/tests/runtime_loader_gap_manifest.json`",
        "`zigux/tests/runtime_loader_gap_survey.zig`",
        "loader-gap manifest-backed survey gate",
        "`zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`",
    ],
    MAKEFILE_PATH: [
        "PHONY += phase9-runtime-atomic64-test phase9-runtime-bitmap-top-bit-test phase9-runtime-trace-events-test phase9-runtime-kretprobe-test phase9-runtime-loader-shared-tests phase9-test phase9",
        "phase9-runtime-loader-shared-tests:",
        "$(ZIG) build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig",
        PHASE9_TRACE_EVENTS_SUBSTRATE_DRIFT_MAKE_MARKER,
        "phase9-test:",
        "$(PYTHON) scripts/zigux/check-phase9-build-only-surface.py",
        "phase9: phase9-test",
    ],
    WORKFLOW_PATH: [
        "Self-test Phase 9 build-only surface checker",
        "python3 scripts/zigux/check-phase9-build-only-surface.py --self-test",
        "Check Phase 9 build-only surface",
        "python3 scripts/zigux/check-phase9-build-only-surface.py",
        "Run Phase 9 runtime helper tests",
        "make -C zigux phase9",
    ],
    PHASE9_BUILD_PATH: [
        "\"phase9-runtime-loader-shared-tests\"",
        "runtime_loader_gap_survey.zig",
        "runtime_loader_shared_tests_step.dependOn(&run_runtime_loader_gap_survey_tests.step);",
        "runtime_loader_selftest_complete_exit_parity.zig",
        "runtime_loader_allocator_init_flow.zig",
        "runtime_loader_shared_tests_step.dependOn(&run_runtime_loader_selftest_complete_exit_parity_tests.step);",
        "runtime_loader_lifecycle_boundary_guard.zig",
        "runtime_loader_shared_tests_step.dependOn(&run_runtime_loader_lifecycle_boundary_guard_tests.step);",
        PHASE9_TRACE_EVENTS_SUBSTRATE_DRIFT_BUILD_MARKER,
        "runtime_trace_events_loader_substrate_drift.zig",
        "test_step.dependOn(&run_runtime_trace_events_loader_substrate_drift_tests.step);",
        "test_step.dependOn(&run_runtime_loader_gap_survey_tests.step);",
        "test_step.dependOn(&run_runtime_loader_selftest_complete_exit_parity_tests.step);",
        "test_step.dependOn(&run_runtime_loader_lifecycle_boundary_guard_tests.step);",
        "\"phase9-runtime-bitmap-top-bit-tests\"",
        "runtime_bitmap_top_bit_contract.zig",
    ],
    RUNTIME_LOADER_CONTRACT_PATH: [
        RUNTIME_LOADER_CONTRACT_TEST_MARKER,
        "keepsPublicationBoundaryExplicit()",
        "keepsDepmodBoundaryExplicit()",
        "keepsReviewOnlyControlBoundaryExplicit()",
        RUNTIME_LOADER_CONTRACT_MODINFO_MARKER,
        RUNTIME_LOADER_CONTRACT_MODULE_ALIAS_MARKER,
        RUNTIME_LOADER_CONTRACT_MODULES_ALIAS_PATH_MARKER,
        RUNTIME_LOADER_CONTRACT_MODULE_INSTALL_ROOT_MARKER,
        RUNTIME_LOADER_CONTRACT_MODULES_ORDER_PATH_MARKER,
        RUNTIME_LOADER_CONTRACT_MODULES_BUILTIN_PATH_MARKER,
        RUNTIME_LOADER_CONTRACT_MODULE_SYMVERS_PATH_MARKER,
        RUNTIME_LOADER_CONTRACT_DEPMOD_SCRIPT_MARKER,
        RUNTIME_LOADER_CONTRACT_DEPMOD_MANIFEST_MARKER,
        RUNTIME_LOADER_CONTRACT_DEPMOD_ALIASES_MARKER,
    ],
    ALLOCATOR_INIT_FLOW_PATH: [
        "phase 9 runtime loader allocator/init-flow replay covers all shipped runtime pilot handoffs",
        "phase 9 runtime loader allocator/init-flow replay rejects missing init, premature selftest, exited, duplicate-init, duplicate-selftest, and incomplete selftest evidence",
        "phase 9 runtime loader allocator/init-flow replay keeps prepared snapshots pinned when requestRuntimeLoad sees prepared-plan drift",
        "runtime_loader.keepsAllocatorInitFlowConsistent(",
        "request.plan.allocator_handoff = .arena;",
        PREPARED_STATE_EXPLICIT_ASSERTION_MARKER,
        PREPARED_STATE_ALLOCATOR_HANDOFF_EXPLICIT_ASSERTION_MARKER,
        ALLOCATOR_INIT_FLOW_LIFECYCLE_LABEL_FIELD_MARKER,
        ALLOCATOR_INIT_FLOW_LIFECYCLE_LABEL_LEN_MARKER,
        ALLOCATOR_INIT_FLOW_KRETPROBE_INIT_LABEL_MARKER,
        ALLOCATOR_INIT_FLOW_KRETPROBE_EXIT_LABEL_MARKER,
    ],
    RUNTIME_LOADER_SELFTEST_COMPLETE_EXIT_PARITY_PATH: [
        "phase 9 runtime loader keeps selftest-complete prepared snapshots stable even if later live state would look exited across all shipped pilot families",
        "runtime_loader.RequestState.waiting_on_runtime_substrate",
        "runtime_loader.RequestState.released_without_substrate",
        "runtime_loader.HandoffStage.selftest_complete",
        "runtime_loader.keepsSelftestHookEvidenceConsistent(pending)",
    ],
    LOADER_GAP_MANIFEST_PATH: [
        '"lane_key": "P9-L18"',
        LOADER_GAP_MANIFEST_NOTE_SURFACE_MARKER,
        '"surface": "zigux/tests/runtime_loader_gap_manifest.json"',
        LOADER_GAP_MANIFEST_ROUTE_MARKER,
        LOADER_GAP_MANIFEST_BOUNDARY_MARKER,
        LOADER_GAP_MANIFEST_CHECKLIST_BOUNDARY_FLAG_MARKER,
        LOADER_GAP_MANIFEST_CHECKLIST_REMINDER_GAP_MARKER,
    ],
    LOADER_GAP_SURVEY_PATH: [
        "phase 9 runtime loader gap survey keeps note and manifest aligned with the live shared packet",
        "phase 9 runtime loader gap survey keeps the shared replay routes and no-dedicated-validator boundary explicit",
        "phase 9 runtime loader gap survey keeps rollback, metadata-only trace-events evidence, and prepared-state drift proof explicit",
        "shared_runtime_loader_files_present",
        "shared_runtime_loader_contract_present",
        "shared_loader_shared_tests_route_present",
        "shared_phase9_bundle_route_present",
        "dedicated_validate_phase9_present",
    ],
    RUNTIME_LOADER_LIFECYCLE_BOUNDARY_GUARD_PATH: [
        "phase 9 runtime loader lifecycle boundary guard keeps manifest lifecycle summary aligned with the shared registration boundary",
        "phase 9 runtime loader lifecycle boundary guard keeps shared request states explicit in the shared facade",
        RUNTIME_LOADER_LIFECYCLE_BOUNDARY_CHECKLIST_TEST_MARKER,
        "error.OutstandingRegistrationForLoader",
        "releaseSharedWithoutSubstrate",
    ],
    TRACE_EVENTS_SUBSTRATE_DRIFT_PATH: [
        "phase 9 runtime trace-events loader rejects prepared shared runtime-substrate drift before any local runtime handoff",
        "phase 9 runtime trace-events loader rejects initialized-stage prepared shared runtime-substrate drift before any local runtime handoff",
        "phase 9 runtime trace-events loader rejects prepared shared selftest-hook drift before any local runtime handoff",
        "phase 9 runtime trace-events loader rejects initialized-stage prepared shared selftest-hook drift before any local runtime handoff",
        "shared_request.plan.requires_runtime_substrate = false;",
        "shared_request.plan.provides_selftest_hook = false;",
        TRACE_EVENTS_SUBSTRATE_DRIFT_PREPARED_PLAN_MARKER,
        TRACE_EVENTS_SUBSTRATE_DRIFT_SELFTEST_HOOK_EXPLICIT_MARKER,
    ],
}

FORBIDDEN_MARKERS = {
    MAKEFILE_PATH: ["phase9-validate:"],
    WORKFLOW_PATH: ["validate-phase9.py", "check-phase9-loader-substrate-plan.py"],
}

SELF_TEST_REMOVALS = [
    (FREEZE_MAP_PATH, "`scripts/zigux/check-phase9-build-only-surface.py`", 1),
    (PHASE9_LANE_SEQUENCING_PATH, PREPARED_STATE_LANDED_MARKER, 1),
    (PHASE9_LANE_SEQUENCING_PATH, DEP_MOD_BOUNDARY_MARKER, 1),
    (PHASE9_LANE_SEQUENCING_PATH, PHASE9_LANE_SEQUENCING_DEPMOD_ALIASES_BOUNDARY_MARKER, 1),
    (PHASE9_LANE_SEQUENCING_PATH, PHASE9_LANE_SEQUENCING_PHASE8_BOUNDARY_MARKER, 1),
    (PHASE9_LANE_SEQUENCING_PATH, PHASE9_LANE_SEQUENCING_LIFECYCLE_BOUNDARY_MARKER, 1),
    (PHASE9_LANE_SEQUENCING_PATH, PHASE9_LANE_SEQUENCING_TRACE_EVENTS_SHARED_ROUTE_MARKER, 1),
    (PHASE9_LANE_SEQUENCING_PATH, PHASE9_LANE_SEQUENCING_SHARED_OWNER_MAP_SOURCE_MARKER, 1),
    (PHASE9_LANE_SEQUENCING_PATH, PHASE9_LANE_SEQUENCING_ATOMIC64_OWNER_SPLIT_MARKER, 1),
    (PHASE9_LANE_SEQUENCING_PATH, PHASE9_LANE_SEQUENCING_BITMAP_OWNER_SPLIT_MARKER, 1),
    (PHASE9_LANE_SEQUENCING_PATH, GAP_SURVEY_DRIFT_MARKER, 1),
    (PHASE9_LANE_SEQUENCING_PATH, GAP_SURVEY_NEXT_STEP_MARKER, 1),
    (PHASE9_LANE_SEQUENCING_PATH, LANE_NOTE_BITMAP_TOP_BIT_SPLIT_MARKER, 1),
    (PHASE9_LANE_SEQUENCING_PATH, OWNER_MAP_MARKERS[0], 1),
    (PHASE9_LANE_SEQUENCING_PATH, OWNER_MAP_MARKERS[1], 1),
    (PHASE9_LANE_SEQUENCING_PATH, OWNER_MAP_MARKERS[2], 1),
    (PHASE9_LANE_SEQUENCING_PATH, OWNER_MAP_MARKERS[3], 1),
    (PHASE9_GAP_SURVEY_NOTE_PATH, PHASE9_GAP_SURVEY_NOTE_ROUTE_MARKER, 1),
    (PHASE9_GAP_SURVEY_NOTE_PATH, PHASE9_GAP_SURVEY_NOTE_TRACE_EVENTS_PROOF_MARKER, 1),
    (PHASE9_GAP_SURVEY_NOTE_PATH, PHASE9_GAP_SURVEY_NOTE_BOUNDARY_MARKER, 1),
    (LOADER_GAP_MANIFEST_PATH, LOADER_GAP_MANIFEST_ROUTE_MARKER, 1),
    (LOADER_GAP_MANIFEST_PATH, LOADER_GAP_MANIFEST_BOUNDARY_MARKER, 1),
    (LOADER_GAP_MANIFEST_PATH, LOADER_GAP_MANIFEST_CHECKLIST_BOUNDARY_FLAG_MARKER, 1),
    (LOADER_GAP_MANIFEST_PATH, LOADER_GAP_MANIFEST_CHECKLIST_REMINDER_GAP_MARKER, 1),
    (REVIEW_CHECKLIST_PATH, "the owner of the exact shared-loader target list, convenience-target names, and repo-reality blocker posture", 1),
    (REVIEW_CHECKLIST_PATH, "workflow-backed `make -C zigux phase9` route", 1),
    (REVIEW_CHECKLIST_PATH, "`Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`", 1),
    (REVIEW_CHECKLIST_PATH, "no-dedicated-`validate-phase9.py` posture", 1),
    (REVIEW_CHECKLIST_PATH, REVIEW_CHECKLIST_TRACE_EVENTS_LOADER_MARKER, 1),
    (REVIEW_CHECKLIST_PATH, REVIEW_CHECKLIST_DEPMOD_BOUNDARY_MARKER, 1),
    (REVIEW_CHECKLIST_PATH, REVIEW_CHECKLIST_PHASE8_BOUNDARY_MARKER, 1),
    (README_PATH, DOCS_ROOT_DEPMOD_BOUNDARY_MARKER, 1),
    (README_PATH, "`zigux/tests/runtime_loader_gap_manifest.json`", 1),
    (README_PATH, DOCS_ROOT_SELFTEST_COMPLETE_EXIT_PARITY_MARKER, 1),
    (README_PATH, DOCS_ROOT_LIFECYCLE_BOUNDARY_GUARD_MARKER, 1),
    (README_PATH, DOCS_ROOT_TRACE_EVENTS_SUBSTRATE_DRIFT_MARKER, 1),
    (README_PATH, "loader-gap survey note plus manifest-backed survey gate", 1),
    (SCRIPTS_README_PATH, "`Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` remains the shared owner map", 1),
    (TESTS_README_PATH, "`zigux/tests/runtime_loader_gap_manifest.json`", 1),
    (TESTS_README_PATH, "`zigux/tests/runtime_loader_gap_survey.zig`", 1),
    (TESTS_README_PATH, "loader-gap manifest-backed survey gate", 1),
    (RUNTIME_LOADER_CONTRACT_PATH, RUNTIME_LOADER_CONTRACT_TEST_MARKER, 1),
    (RUNTIME_LOADER_CONTRACT_PATH, RUNTIME_LOADER_CONTRACT_MODULE_SYMVERS_PATH_MARKER, 1),
    (RUNTIME_LOADER_CONTRACT_PATH, RUNTIME_LOADER_CONTRACT_DEPMOD_ALIASES_MARKER, 1),
    (MAKEFILE_PATH, "phase9-runtime-loader-shared-tests:", 1),
    (MAKEFILE_PATH, PHASE9_TRACE_EVENTS_SUBSTRATE_DRIFT_MAKE_MARKER, 1),
    (PHASE9_BUILD_PATH, "runtime_loader_gap_survey.zig", 1),
    (PHASE9_BUILD_PATH, "runtime_loader_shared_tests_step.dependOn(&run_runtime_loader_gap_survey_tests.step);", 1),
    (PHASE9_BUILD_PATH, "runtime_loader_selftest_complete_exit_parity.zig", 1),
    (PHASE9_BUILD_PATH, "runtime_trace_events_loader_substrate_drift.zig", 1),
    (PHASE9_BUILD_PATH, "test_step.dependOn(&run_runtime_trace_events_loader_substrate_drift_tests.step);", 1),
    (PHASE9_BUILD_PATH, "test_step.dependOn(&run_runtime_loader_gap_survey_tests.step);", 1),
    (PHASE9_BUILD_PATH, "runtime_loader_shared_tests_step.dependOn(&run_runtime_loader_selftest_complete_exit_parity_tests.step);", 1),
    (PHASE9_BUILD_PATH, "runtime_loader_shared_tests_step.dependOn(&run_runtime_loader_lifecycle_boundary_guard_tests.step);", 1),
    (PHASE9_BUILD_PATH, "test_step.dependOn(&run_runtime_loader_lifecycle_boundary_guard_tests.step);", 1),
    (RUNTIME_LOADER_SELFTEST_COMPLETE_EXIT_PARITY_PATH, "phase 9 runtime loader keeps selftest-complete prepared snapshots stable even if later live state would look exited across all shipped pilot families", 1),
    (RUNTIME_LOADER_LIFECYCLE_BOUNDARY_GUARD_PATH, "phase 9 runtime loader lifecycle boundary guard keeps manifest lifecycle summary aligned with the shared registration boundary", 1),
    (RUNTIME_LOADER_LIFECYCLE_BOUNDARY_GUARD_PATH, RUNTIME_LOADER_LIFECYCLE_BOUNDARY_CHECKLIST_TEST_MARKER, 1),
    (ALLOCATOR_INIT_FLOW_PATH, "phase 9 runtime loader allocator/init-flow replay covers all shipped runtime pilot handoffs", 1),
    (ALLOCATOR_INIT_FLOW_PATH, "request.plan.allocator_handoff = .arena;", 2),
    (ALLOCATOR_INIT_FLOW_PATH, PREPARED_STATE_EXPLICIT_ASSERTION_MARKER, 1),
    (ALLOCATOR_INIT_FLOW_PATH, PREPARED_STATE_ALLOCATOR_HANDOFF_EXPLICIT_ASSERTION_MARKER, 1),
    (ALLOCATOR_INIT_FLOW_PATH, ALLOCATOR_INIT_FLOW_LIFECYCLE_LABEL_FIELD_MARKER, 1),
    (ALLOCATOR_INIT_FLOW_PATH, ALLOCATOR_INIT_FLOW_LIFECYCLE_LABEL_LEN_MARKER, 1),
    (ALLOCATOR_INIT_FLOW_PATH, ALLOCATOR_INIT_FLOW_KRETPROBE_INIT_LABEL_MARKER, 1),
    (ALLOCATOR_INIT_FLOW_PATH, ALLOCATOR_INIT_FLOW_KRETPROBE_EXIT_LABEL_MARKER, 1),
    (LOADER_GAP_SURVEY_PATH, "shared_phase9_bundle_route_present", 1),
    (TRACE_EVENTS_SUBSTRATE_DRIFT_PATH, TRACE_EVENTS_SUBSTRATE_DRIFT_PREPARED_PLAN_MARKER, 1),
    (TRACE_EVENTS_SUBSTRATE_DRIFT_PATH, TRACE_EVENTS_SUBSTRATE_DRIFT_SELFTEST_HOOK_EXPLICIT_MARKER, 1),
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")
    for rel_path in FORBIDDEN_FILES:
        if (root / rel_path).exists():
            failures.append(f"unexpected_file:{rel_path}")
    if failures:
        return failures
    for rel_path, markers in REQUIRED_MARKERS.items():
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                failures.append(f"missing_marker:{rel_path}:{marker}")
    for rel_path, markers in FORBIDDEN_MARKERS.items():
        text = read_text(root, rel_path)
        for marker in markers:
            if marker in text:
                failures.append(f"forbidden_marker:{rel_path}:{marker}")
    return failures


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    for rel_path in REQUIRED_FILES:
        markers = REQUIRED_MARKERS.get(rel_path, [])
        title = Path(rel_path).name
        prefix = f"# {title}" if rel_path.endswith((".py", ".md", ".json")) else f"// {title}"
        write_text(root / rel_path, "\n".join([prefix, *markers, ""]))


def remove_once(root: Path, rel_path: str, marker: str, count: int) -> None:
    path = root / rel_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(marker, "", count), encoding="utf-8")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase9-build-only-surface-"))
    try:
        write_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")
        for rel_path, marker, count in SELF_TEST_REMOVALS:
            write_fixture_tree(base)
            remove_once(base, rel_path, marker, count)
            expect_failure(base, f"missing_marker:{rel_path}:{marker}")
        write_fixture_tree(base)
        write_text(base / "scripts/zigux/check-phase9-loader-substrate-plan.py", "# forbidden\n")
        expect_failure(base, "unexpected_file:scripts/zigux/check-phase9-loader-substrate-plan.py")
    finally:
        shutil.rmtree(base, ignore_errors=True)
    print("PHASE9_BUILD_ONLY_SURFACE_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the shared Phase 9 runtime-pilot build-only packet.")
    parser.add_argument("--repo-root", type=Path, default=ROOT, help="repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test and exit")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    failures = validate(args.repo_root)
    if failures:
        for failure in failures:
            print(f"PHASE9_BUILD_ONLY_SURFACE_ERROR={failure}")
        return 1
    print(f"PHASE9_BUILD_ONLY_SURFACE_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE9_BUILD_ONLY_SURFACE_REQUIRED_SURFACE_COUNT={len(REQUIRED_MARKERS)}")
    print("PHASE9_BUILD_ONLY_SURFACE=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
