const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE9_FREEZE_MAP_STUDY_BOUNDARIES_SELF_TEST=pass";

const ROADMAP_STUDY_ONLY_ANCHORS = [_][]const u8{
    "kernel/workqueue.c",
    "kernel/trace/ring_buffer.c",
};

const PHASE9_SHARED_VALIDATOR_MARKERS = [_][]const u8{
    "scripts\zigux/validate_phase9.zig",
    "zig run validate_phase9.zig --self-test",
    "zig run validate_phase9.zig",
};

const STALE_PHASE9_VALIDATOR_DENIAL = [_][]const u8{
    "there is still no dedicated shared `validate-phase9.py` rerun path",
};

const CURRENT_PHASE9_MAKE_ROUTES = [_][]const u8{
    "phase9-runtime-atomic64-test",
    "phase9-runtime-bitmap-test",
    "phase9-runtime-loader-shared-test",
    "phase9-runtime-loader-command-env-boundary-guard-test",
    "phase9-runtime-trace-events-test",
    "phase9-runtime-kretprobe-test",
    "phase9-first-loadable-runtime-module-parity-test",
    "phase9-test",
};

const FORBIDDEN_PHASE9_MAKE_ROUTES = [_][]const u8{
    "phase9",
    "phase9-validate",
    "phase9-runtime-trace-events-sample-tests",
};

const PATH_REQUIREMENTS = [_][]const u8{
    "# Zigux Freeze Map",
    "`kernel/workqueue.c`",
    "`kernel/trace/ring_buffer.c`",
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "`Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`",
    "`Documentation/zigux/README.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`scripts/zigux/README.md`",
    "`samples/zigux/README.md`",
    "`zigux/tests/README.md`",
    "`scripts/zigux/check_phase9_review_checklist_phase_boundaries.zig`",
    "`scripts/zigux/check_phase9_trace_events_runtime_packet.zig`",
    "`scripts/zigux/check_phase9_freeze_map_study_boundaries.zig`",
    "`samples/zigux/runtime_trace_events.zig`",
    "`samples/zigux/runtime_trace_events_unregistered_gate.zig`",
    "`samples/zigux/runtime_trace_events_exit_rollback_guard.zig`",
    "`samples/zigux/runtime_trace_events_registration_reentry_gate.zig`",
    "`samples/zigux/runtime_trace_events_reinit_rollback_guard.zig`",
    "`samples/zigux/runtime_trace_events_reinit_reexit_guard.zig`",
    "`Documentation/zigux/phase9-runtime-loader-gap-survey.md`",
    "`zigux/tests/runtime_loader_gap_manifest.json`",
    "`zigux/tests/runtime_loader_gap_survey.zig`",
    "`zigux/tests/runtime_loader_allocator_init_flow.zig`",
    "`zigux/tests/phase9_build.zig`",
    "`zigux/kernel/runtime_loader.zig`",
    "`zigux/kernel/runtime_loader_contract.zig`",
    "`zigux/kernel/runtime_loader_command_env_boundary_guard.zig`",
    "`samples/zigux/runtime_bitmap_loader.zig`",
    "`samples/zigux/runtime_trace_events_loader.zig`",
    "`zigux/Makefile` explicit only as a readable non-owner surface whose live body now exposes bounded `phase9-runtime-atomic64-test`, `phase9-runtime-bitmap-test`, `phase9-runtime-loader-shared-test`, `phase9-runtime-loader-command-env-boundary-guard-test`, `phase9-runtime-trace-events-test`, `phase9-runtime-kretprobe-test`, and `phase9-test` routes",
    "# Phase 15 Study-Only Anchor Accounting",
    "PHASE15_STATUS=study_only_accounting_slice_landed",
    "PHASE15_PROVENANCE_MODE=dated_master_readback",
    "`kernel/workqueue.c`",
    "`kernel/trace/ring_buffer.c`",
    "`study_only`",
    "tracked outside the freeze-in-C scorecard",
    "this note is an inventory and handoff surface, not an approval record",
    "if the study-only anchor set changes in `Documentation/zigux/freeze-map.md`, this note must change with it",
    "the freeze-map governance note, the parity scorecard, the handoff-next-steps survey, and the shared-summary gap note",
    "boundary-study target first, not a rewrite target",
    "remain future-only and not current product claims",
    "no Architecture Council approval is currently recorded for a deep-core status change",
    "a direct Zigux bridge for `kernel/workqueue.c`",
    "a direct Zigux bridge for `kernel/trace/ring_buffer.c`",
    "any future status-bucket change for either anchor must update the freeze map, the Phase 15 governance note, the parity scorecard, and this study-only accounting note together",
    "if a shared reminder surface summarizes the study-only freeze-map anchors, does it route that summary back through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` so `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay explicit as study-only boundary context rather than runtime-substrate or bridge-readiness evidence?",
    "Phase 9 notes - `Documentation/zigux/freeze-map.md` - `Documentation/zigux/phase15-study-only-anchor-accounting.md` - `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` - `Documentation/zigux/review-checklist.md` - `Documentation/zigux/README.md` - `scripts/zigux/README.md` - `samples/zigux/README.md` - `zigux/tests/README.md` - `scripts/zigux/check_phase9_review_checklist_phase_boundaries.zig` - `scripts/zigux/check_phase9_trace_events_runtime_packet.zig` - `scripts/zigux/check_phase9_freeze_map_study_boundaries.zig` keep the shared Phase 9 reminder packet honest by routing any study-only freeze-map summary back through the dedicated accounting note, keeping the returned loader shard and the bounded `zigux/tests/phase9_build.zig` rerun bundle explicit as shared-owner evidence, and not treating `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` as runtime-substrate readiness evidence.",
    "keep the freeze-map boundary explicit here too: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only anchors through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` rather than Phase 9 runtime-substrate readiness cues, and any shared reminder surface that summarizes them must route back through those two owner notes.",
    "keep the narrow trace-events packet distinct too: `samples/zigux/runtime_trace_events.zig`, `samples/zigux/runtime_trace_events_unregistered_gate.zig`, `samples/zigux/runtime_trace_events_exit_rollback_guard.zig`, and `samples/zigux/runtime_trace_events_registration_reentry_gate.zig` remain the current shipped runtime-pilot proof, while the study-only anchors stay non-owner governance context only.",
    "keep the returned shared runtime-loader allocator/init-flow and command/environment boundary packet explicit as neighboring shared-owner evidence through `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`, the bounded `zigux/tests/phase9_build.zig` `phase9-runtime-loader-shared-tests` and `phase9-runtime-loader-command-env-boundary-guard-tests` shards, and the separate returned `samples/zigux/runtime_bitmap_loader.zig` scaffold without implying that blocked publication, install-root, or module-metadata surfaces are complete.",
    "keep the freeze-map study-only anchors explicit through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md`: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain cautionary non-owner context rather than proof of runtime-substrate or bridge readiness",
    "keep the freeze-map boundary explicit too: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only anchors through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` rather than Phase 9 runtime-substrate readiness cues",
    "Keep `samples/zigux/runtime_trace_events_reinit_rollback_guard.zig` explicit as the rejected re-init rollback companion for initialized, selftest-complete, and exited lifecycle checkpoints in the same direct runtime packet.",
    "Keep `samples/zigux/runtime_trace_events_reinit_reexit_guard.zig` explicit as the paired rejected re-init plus rejected re-exit rollback companion after initialized direct activity and selftest-ready replay in the same direct runtime packet.",
    "Current `master` also keeps a narrower returned runtime kretprobe sample-side packet explicit through `samples/zigux/runtime_kretprobe.zig`, `samples/zigux/runtime_kretprobe_loader.zig`, `samples/zigux/runtime_kretprobe_initialized_snapshot_guard.zig`, `samples/zigux/runtime_kretprobe_registration_reentry_gate.zig`, `zigux/tests/runtime_kretprobe_module.zig`, `zigux/tests/runtime_kretprobe_survey.zig`, `zigux/tests/runtime_first_loadable_parity_behavior.zig`, and the dedicated `phase9-runtime-kretprobe-sample-tests`, `phase9-runtime-kretprobe-loader-tests`, `phase9-runtime-kretprobe-initialized-snapshot-guard-tests`, `phase9-runtime-kretprobe-registration-reentry-gate-tests`, `phase9-runtime-kretprobe-survey-tests`, `phase9-runtime-kretprobe-module-tests`, `phase9-runtime-kretprobe-tests`, and `phase9-first-loadable-runtime-module-parity-behavior-tests` routes in `zigux/tests/phase9_build.zig`.",
    "Keep `samples/zigux/runtime_bitmap_direct_init_contract.zig` explicit as the returned direct-init normalization companion proof for the same runtime bitmap starter, covering unsorted duplicate input collapse, nth-set ordering, formatted sparse-summary stability, and lifecycle-summary stability through selftest and exit.",
    "Keep that bitmap packet framed as a separate Phase 9 runtime reminder rather than as proof that the broader shared runtime-loader packet returned or as evidence that a fifth approved Phase 5 sample family landed here.",
    "Keep the current bounded Phase 9 reminder packet explicit through `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-study-only-anchor-accounting.md`, `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `samples/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/check_phase9_review_checklist_phase_boundaries.zig`, `scripts/zigux/check_phase9_trace_events_runtime_packet.zig`, and `scripts/zigux/check_phase9_freeze_map_study_boundaries.zig`.",
    "keep the narrow trace-events packet distinct too: `samples/zigux/runtime_trace_events.zig`, `samples/zigux/runtime_trace_events_unregistered_gate.zig`, `samples/zigux/runtime_trace_events_exit_rollback_guard.zig`, `samples/zigux/runtime_trace_events_registration_reentry_gate.zig`, `samples/zigux/runtime_trace_events_reinit_rollback_guard.zig`, `samples/zigux/runtime_trace_events_reinit_reexit_guard.zig`, `zigux/tests/runtime_trace_events_manifest.json`, and `zigux/tests/runtime_trace_events_survey.zig` remain the current shipped runtime-pilot proof rather than a claim that broader runtime-loader or publication boundaries are solved",
    "keep the returned shared runtime-loader allocator/init-flow and command/environment boundary packet explicit as neighboring shared-owner evidence through `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`, the bounded `zigux/tests/phase9_build.zig` `phase9-runtime-loader-allocator-init-flow-tests`, `phase9-runtime-loader-shared-tests`, and `phase9-runtime-loader-command-env-boundary-guard-tests` routes, and the separate returned `samples/zigux/runtime_bitmap_loader.zig` scaffold without implying that blocked publication, install-root, or module-metadata surfaces are complete",
    "keep the returned runtime kretprobe pilot packet distinct from those shared loader and bitmap reminders too: `samples/zigux/runtime_kretprobe.zig`, `samples/zigux/runtime_kretprobe_loader.zig`, `samples/zigux/runtime_kretprobe_initialized_snapshot_guard.zig`, `samples/zigux/runtime_kretprobe_registration_reentry_gate.zig`, `zigux/tests/runtime_kretprobe_survey.zig`, `zigux/tests/runtime_kretprobe_module.zig`, `zigux/tests/runtime_first_loadable_parity_behavior.zig`, and the bounded `zigux/tests/phase9_build.zig` `phase9-runtime-kretprobe-sample-tests`, `phase9-runtime-kretprobe-loader-tests`, `phase9-runtime-kretprobe-initialized-snapshot-guard-tests`, `phase9-runtime-kretprobe-registration-reentry-gate-tests`, `phase9-runtime-kretprobe-survey-tests`, `phase9-runtime-kretprobe-module-tests`, `phase9-runtime-kretprobe-tests`, and `phase9-first-loadable-runtime-module-parity-behavior-tests` routes are current family-local pilot evidence, but they still must not be used to imply that the broader shared runtime-loader packet, blocked publication boundaries, or install-root surfaces are complete",
    "without implying any Architecture Council approval for a freeze-map status change",
    "zig run scripts/zigux/check_phase9_review_checklist_phase_boundaries.zig -- --self-test",
    "zig run scripts/zigux/check_phase9_review_checklist_phase_boundaries.zig --",
    "zig run scripts/zigux/check_phase9_freeze_map_study_boundaries.zig -- --self-test",
    "zig run scripts/zigux/check_phase9_freeze_map_study_boundaries.zig --",
    "zig run scripts/zigux/check_phase9_trace_events_runtime_packet.zig -- --self-test",
    "zig run scripts/zigux/check_phase9_trace_events_runtime_packet.zig --",
    "zig build phase9-runtime-loader-command-env-boundary-guard-tests --build-file zigux/tests/phase9_build.zig",
    "zig build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig",
    "zig test samples/zigux/runtime_trace_events.zig",
    "zig test zigux/tests/runtime_trace_events_survey.zig",
};

const FREEZE_MAP_PATH = [_][]const u8{
    "Documentation/zigux/freeze-map.md",
};

const STUDY_ONLY_ACCOUNTING_PATH = [_][]const u8{
    "Documentation/zigux/phase15-study-only-anchor-accounting.md",
};

const REVIEW_CHECKLIST_PATH = [_][]const u8{
    "Documentation/zigux/review-checklist.md",
};

const DOCS_README_PATH = [_][]const u8{
    "Documentation/zigux/README.md",
};

const LANE_SEQUENCING_PATH = [_][]const u8{
    "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md",
};

const SCRIPTS_README_PATH = [_][]const u8{
    "scripts/zigux/README.md",
};

const SAMPLES_README_PATH = [_][]const u8{
    "samples/zigux/README.md",
};

const TESTS_README_PATH = [_][]const u8{
    "zigux/tests/README.md",
};

const MAKEFILE_PATH = [_][]const u8{
    "zigux/Makefile",
};

const WORKFLOW_PATH = [_][]const u8{
    ".github/workflows/zigux-bootstrap.yml",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (ROADMAP_STUDY_ONLY_ANCHORS) |marker| try guard.requireMarker(text, marker);
    for (PHASE9_SHARED_VALIDATOR_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (STALE_PHASE9_VALIDATOR_DENIAL) |marker| try guard.requireMarker(text, marker);
    for (CURRENT_PHASE9_MAKE_ROUTES) |marker| try guard.requireMarker(text, marker);
    for (FORBIDDEN_PHASE9_MAKE_ROUTES) |marker| try guard.requireMarker(text, marker);
    for (PATH_REQUIREMENTS) |marker| try guard.requireMarker(text, marker);
    for (FREEZE_MAP_PATH) |marker| try guard.requireMarker(text, marker);
    for (STUDY_ONLY_ACCOUNTING_PATH) |marker| try guard.requireMarker(text, marker);
    for (REVIEW_CHECKLIST_PATH) |marker| try guard.requireMarker(text, marker);
    for (DOCS_README_PATH) |marker| try guard.requireMarker(text, marker);
    for (LANE_SEQUENCING_PATH) |marker| try guard.requireMarker(text, marker);
    for (SCRIPTS_README_PATH) |marker| try guard.requireMarker(text, marker);
    for (SAMPLES_README_PATH) |marker| try guard.requireMarker(text, marker);
    for (TESTS_README_PATH) |marker| try guard.requireMarker(text, marker);
    for (MAKEFILE_PATH) |marker| try guard.requireMarker(text, marker);
    for (WORKFLOW_PATH) |marker| try guard.requireMarker(text, marker);
}

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();
    const io = std.Io.Threaded.init(allocator, .{});
    defer io.deinit();
    const args = try std.process.argsAlloc(allocator);
    defer std.process.argsFree(allocator, args);

    var self_test = false;
    for (args[1..]) |arg| {
        if (std.mem.eql(u8, arg, "--self-test")) self_test = true;
    }

    if (self_test) {
        try checkText("");
        try guard.printLine(io, "{s}", .{pass_marker});
        return;
    }

    const root = try guard.repoRootFromScript(allocator);
    defer allocator.free(root);
    const workflow_rel = ".github/workflows/zigux-bootstrap.yml";
    const workflow_path = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ root, workflow_rel });
    defer allocator.free(workflow_path);
    const text = try guard.readUtf8File(io, allocator, workflow_path);
    defer allocator.free(text);
    try checkText(text);
    try guard.printLine(io, "{s}", .{pass_marker});
}
