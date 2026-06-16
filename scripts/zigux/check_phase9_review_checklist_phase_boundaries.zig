const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_SELF_TEST=pass";

const REVIEW_CHECKLIST_REQUIRED_MARKERS = [_][]const u8{
    "if the change touches the shared Phase 9 runtime-pilot packet",
    "`Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`",
    "`scripts/zigux/check_phase9_review_checklist_phase_boundaries.zig`",
    "`scripts/zigux/check_phase9_trace_events_runtime_packet.zig`",
    "`scripts/zigux/check_phase9_trace_events_direct_summary.zig`",
    "`scripts/zigux/check_phase9_trace_events_summary_preservation.zig`",
    "`samples/zigux/runtime_trace_events.zig`",
    "`samples/zigux/runtime_trace_events_unregistered_gate.zig`",
    "`samples/zigux/runtime_trace_events_exit_rollback_guard.zig`",
    "`samples/zigux/runtime_trace_events_registration_reentry_gate.zig`",
    "`samples/zigux/runtime_trace_events_reinit_rollback_guard.zig`",
    "`samples/zigux/runtime_trace_events_reinit_reexit_guard.zig`",
    ".provides_selftest_hook = true",
    "initialized, selftest_complete, and exited lifecycle tracking",
    "failed-exit rollback explicit after reusable selftest replay",
    "balanced registration re-entry companion that keeps function-thread registration reusable before and after selftest",
    "rejected re-init rollback companion that keeps initialized, selftest_complete, and exited summaries stable after rejected `init()` retries",
    "paired rejected re-init plus rejected re-exit rollback companion that keeps initialized direct activity and selftest-ready replay explicit without drift",
    "direct summary and summary-preservation checkers that keep the shipped trace-events packet replayable",
    "`zigux/tests/runtime_loader_allocator_init_flow.zig`",
    "`zigux/kernel/runtime_loader.zig`",
    "`zigux/kernel/runtime_loader_contract.zig`",
    "`zigux/kernel/runtime_loader_command_env_boundary_guard.zig`",
    "`samples/zigux/runtime_*_loader.zig`",
    "`phase9-runtime-loader-command-env-boundary-guard-tests`",
    "the older `Documentation/zigux/phase9-runtime-loader-gap-survey.md`, `zigux/tests/runtime_loader_gap_survey.zig`, and `samples/zigux/runtime_trace_events_loader.zig` stay historical wider-family vocabulary",
    "`zigux/tests/runtime_loader_gap_manifest.json` stays in that same historical wider-family bucket until the same kind of fresh shared-owner reread returns it",
    "older blocked module-metadata and depmod-publication vocabulary such as `.modinfo`, `MODULE_ALIAS()`, `modules.alias`, `modules.order`, `modules.builtin`, `Module.symvers`, module install-root, and depmod script, manifest, or alias-output state stays historical blocked-boundary vocabulary until a fresh repo reread restores a current shared owner surface for that packet",
    "the partial separate runtime bitmap reminder packet stays explicit in `samples/zigux/README.md`, `Documentation/zigux/README.md`, and `Documentation/zigux/review-checklist.md`",
    "the shared `zigux/tests/phase9_build.zig` bundle now reruns that partial bitmap packet through `phase9-runtime-bitmap-cold-stage-guard-tests` plus the aggregate `phase9-runtime-bitmap-tests` handle",
    "keep that partial bitmap packet framed as a separate bounded Phase 9 runtime reminder rather than proof that the broader shared runtime-loader packet returned",
    "PHASE2_CONF_BRIDGE_MARKER",
    "PHASE2_CONFDATA_BRIDGE_MARKER",
    "PHASE3_EXPORTS_MARKER",
    "PHASE3_EXPORT_SHIM_MARKER",
    "PHASE2_BOUNDARY_MARKER",
    "PHASE3_BOUNDARY_MARKER",
};

const DOCS_README_REQUIRED_MARKERS = [_][]const u8{
    "Phase 9 notes - `Documentation/zigux/freeze-map.md` - `Documentation/zigux/phase15-study-only-anchor-accounting.md` - `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` - `Documentation/zigux/review-checklist.md` - `Documentation/zigux/README.md` - `scripts/zigux/README.md` - `samples/zigux/README.md` - `zigux/tests/README.md` - `scripts/zigux/check_phase9_review_checklist_phase_boundaries.zig` - `scripts/zigux/check_phase9_trace_events_runtime_packet.zig` - `scripts/zigux/check_phase9_freeze_map_study_boundaries.zig` keep the shared Phase 9 reminder packet honest by routing any study-only freeze-map summary back through the dedicated accounting note, keeping the returned loader shard and the bounded `zigux/tests/phase9_build.zig` rerun bundle explicit as shared-owner evidence, and not treating `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` as runtime-substrate readiness evidence.",
    "keep the returned shared runtime-loader allocator/init-flow and command/environment boundary packet explicit as neighboring shared-owner evidence through `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`, the bounded `zigux/tests/phase9_build.zig` `phase9-runtime-loader-shared-tests` and `phase9-runtime-loader-command-env-boundary-guard-tests` shards, and the separate returned `samples/zigux/runtime_bitmap_loader.zig` scaffold without implying that blocked publication, install-root, or module-metadata surfaces are complete.",
    "keep the partial runtime bitmap reminder packet distinct from that returned loader shard too:",
};

const LANE_SEQUENCING_REQUIRED_MARKERS = [_][]const u8{
    "Trusted mixed rereads on 2026-05-25 confirm four distinct current-master Phase 9 postures.",
    "The shared runtime-loader allocator/init-flow and command/environment boundary packet survives as a narrower shared-owner surface",
    "`zigux/tests/phase9_build.zig` still exposes `phase9-runtime-loader-allocator-init-flow-tests`, `phase9-runtime-loader-shared-tests`, `phase9-runtime-loader-command-env-boundary-guard-tests`, and `phase9-runtime-trace-events-loader-substrate-drift-tests`",
    "`zigux/kernel/runtime_loader_command_env_boundary_guard.zig`",
    "`phase9-runtime-loader-command-env-boundary-guard-tests`",
    "keep the Phase 8 command and environment ownership boundary explicit",
    "deferred `command_name`, exec-path, `PERF_EXEC_PATH`, and `PATH` cues stay with `tools/lib/subcmd/exec-cmd.zig`",
    "`LINES` and `COLUMNS` stay with `tools/lib/subcmd/help.zig`",
    "`samples/zigux/runtime_kretprobe.zig`",
    "`zigux/tests/runtime_kretprobe_module.zig`",
    "`zigux/tests/runtime_first_loadable_parity_behavior.zig`",
    "`phase9-runtime-kretprobe-sample-tests`",
    "`phase9-runtime-kretprobe-module-tests`",
    "`phase9-runtime-kretprobe-tests`",
    "`phase9-first-loadable-runtime-module-parity-behavior-tests`",
    "current `master` no longer supports treating kretprobe as absent from the cross-family parity surface",
    "keep `modules.order`, `modules.builtin`, `Module.symvers`, and module install-root wording framed as blocked wider-family vocabulary too",
    "keep blocked depmod script, depmod manifest, and depmod alias-output wording framed as historical wider-family vocabulary too until trusted direct rereads return a current shared owner surface for that publication packet",
    "PHASE2_CONF_BRIDGE_MARKER",
    "PHASE2_CONFDATA_BRIDGE_MARKER",
    "PHASE3_EXPORTS_MARKER",
    "PHASE3_EXPORT_SHIM_MARKER",
    "PHASE2_BOUNDARY_MARKER",
    "PHASE3_BOUNDARY_MARKER",
    "Treat stale shared-owner undercount or overclaim as the active blocker before reopening checker-local or runtime-behavior work.",
};

const MODULE_SLICE_REQUIRED_MARKERS = [_][]const u8{
    "The adjacent shared build shard in `zigux/tests/phase9_build.zig` now names `phase9-runtime-trace-events-tests`, `phase9-runtime-trace-events-module-tests`, `phase9-runtime-loader-allocator-init-flow-tests`, `phase9-runtime-loader-command-env-boundary-guard-tests`, the dedicated `phase9-runtime-trace-events-loader-substrate-drift-tests` replay, the dedicated `phase9-runtime-trace-events-reinit-rollback-guard-tests` and `phase9-runtime-trace-events-reinit-reexit-guard-tests` replays, aggregate `phase9-runtime-loader-shared-tests`, and the broader `phase9-first-loadable-runtime-module-parity-survey-tests` route, but those rerun routes remain neighboring shared-owner evidence instead of expanding this module slice into returned family-local runtime-loader parity.",
    "Current `master` does now expose the shared loader-backed surfaces `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`, and the separate returned `samples/zigux/runtime_bitmap_loader.zig` scaffold through the adjacent `phase9-runtime-loader-shared-tests` shard plus the dedicated `phase9-runtime-trace-events-loader-substrate-drift-tests` replay in `zigux/tests/phase9_build.zig`, but those neighboring routes still stay shared-owner evidence rather than returned family-local trace-events proof.",
    "Current `master` still keeps the separate Phase 9 runtime bitmap reminder packet visible through `Documentation/zigux/phase9-runtime-bitmap-survey.md`",
    "PHASE2_CONF_BRIDGE_MARKER",
    "PHASE2_CONFDATA_BRIDGE_MARKER",
    "PHASE3_EXPORTS_MARKER",
    "PHASE3_EXPORT_SHIM_MARKER",
    "- `scripts/zigux/kconfig/conf_bridge.zig` and `scripts/zigux/kconfig/confdata_bridge.zig` remain Phase 2 config-surface bridge references.",
    "- `rust/exports.c` and `zigux/kernel/export_shim.zig` remain Phase 3 export-boundary references.",
    "- Those earlier-phase anchors stay adjacent context for the narrow trace-events packet rather than shared runtime-pilot evidence.",
};

const SAMPLES_README_REQUIRED_MARKERS = [_][]const u8{
    "PHASE2_CONF_BRIDGE_MARKER",
    "PHASE2_CONFDATA_BRIDGE_MARKER",
    "PHASE3_EXPORTS_MARKER",
    "PHASE3_EXPORT_SHIM_MARKER",
    "Keep the earlier non-owner boundary split explicit here too: `scripts/zigux/kconfig/conf_bridge.zig` and `scripts/zigux/kconfig/confdata_bridge.zig` remain Phase 2 config-surface bridge references, while `rust/exports.c` and `zigux/kernel/export_shim.zig` remain Phase 3 export-boundary references rather than runtime-pilot sample evidence.",
};

const TESTS_README_REQUIRED_MARKERS = [_][]const u8{
    "keep the returned shared runtime-loader allocator/init-flow and command/environment boundary packet explicit as neighboring shared-owner evidence through `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`, the bounded `zigux/tests/phase9_build.zig` `phase9-runtime-loader-allocator-init-flow-tests`, `phase9-runtime-loader-shared-tests`, and `phase9-runtime-loader-command-env-boundary-guard-tests` routes, and the separate returned `samples/zigux/runtime_bitmap_loader.zig` scaffold without implying that blocked publication, install-root, or module-metadata surfaces are complete",
    "keep the earlier non-owner boundary split explicit too: `tools/lib/subcmd/exec-cmd.zig` and `tools/lib/subcmd/help.zig` remain the command and environment owners, `scripts/zigux/kconfig/conf_bridge.zig` and `scripts/zigux/kconfig/confdata_bridge.zig` remain Phase 2 config-surface bridge references, and `rust/exports.c` plus `zigux/kernel/export_shim.zig` remain Phase 3 export-boundary references rather than runtime-pilot evidence.",
    "PHASE2_CONF_BRIDGE_MARKER",
    "PHASE2_CONFDATA_BRIDGE_MARKER",
    "PHASE3_EXPORTS_MARKER",
    "PHASE3_EXPORT_SHIM_MARKER",
    "PHASE2_BOUNDARY_MARKER",
    "PHASE3_BOUNDARY_MARKER",
};

const WORKFLOW_REQUIRED_MARKERS = [_][]const u8{
    "zig run scripts/zigux/check_phase9_review_checklist_phase_boundaries.zig -- --self-test",
    "zig run scripts/zigux/check_phase9_review_checklist_phase_boundaries.zig --",
    "zig run scripts/zigux/check_phase9_freeze_map_study_boundaries.zig -- --self-test",
    "zig run scripts/zigux/check_phase9_freeze_map_study_boundaries.zig --",
    "zig run scripts/zigux/check_phase9_trace_events_runtime_packet.zig -- --self-test",
    "zig run scripts/zigux/check_phase9_trace_events_runtime_packet.zig --",
    "zig run scripts/zigux/check_phase9_trace_events_direct_summary.zig -- --self-test",
    "zig run scripts/zigux/check_phase9_trace_events_direct_summary.zig --",
    "zig run scripts/zigux/check_phase9_trace_events_summary_preservation.zig -- --self-test",
    "zig run scripts/zigux/check_phase9_trace_events_summary_preservation.zig --",
};

const CONTRACT_REQUIRED_MARKERS = [_][]const u8{
    "test \"LoadPlan keeps blocked publication outputs and install-root surfaces out of the shared request contract\" {",
    "const blocked_publication_fields = [_][]const u8{",
    "\"modinfo\",",
    "\"module_alias\",",
    "\"modules_alias_path\",",
    "\"module_install_root\",",
    "\"modules_order_path\",",
    "\"modules_builtin_path\",",
    "\"module_symvers_path\",",
    "\"depmod_script\",",
    "\"depmod_manifest\",",
    "try std.testing.expect(!@hasField(LoadPlan, field));",
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

const EXACT_ONCE_MARKERS = [_][]const u8{
    "if the change touches the shared Phase 9 runtime-pilot packet",
    "keep that partial bitmap packet framed as a separate bounded Phase 9 runtime reminder rather than proof that the broader shared runtime-loader packet returned",
};

const REQUIRED_PHASE9_MAKE_COMMANDS = [_][]const u8{
    "phase9-runtime-atomic64-test",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase9-runtime-atomic64-tests --build-file zigux/tests/phase9_build.zig --summary all",
    "phase9-runtime-bitmap-test",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase9-runtime-bitmap-tests --build-file zigux/tests/phase9_build.zig --summary all",
    "phase9-runtime-loader-shared-test",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig --summary all",
    "phase9-runtime-loader-command-env-boundary-guard-test",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase9-runtime-loader-command-env-boundary-guard-tests --build-file zigux/tests/phase9_build.zig --summary all",
    "phase9-runtime-trace-events-test",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase9-runtime-trace-events-tests --build-file zigux/tests/phase9_build.zig --summary all",
    "phase9-runtime-kretprobe-test",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase9-runtime-kretprobe-tests --build-file zigux/tests/phase9_build.zig --summary all",
    "phase9-first-loadable-runtime-module-parity-test",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase9-first-loadable-runtime-module-parity-behavior-tests --build-file zigux/tests/phase9_build.zig --summary all",
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

const MODULE_SLICE_PATH = [_][]const u8{
    "Documentation/zigux/phase9-runtime-trace-events-module-slice.md",
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

const CONTRACT_PATH = [_][]const u8{
    "zigux/kernel/runtime_loader_contract.zig",
};

const MAKEFILE_PATH = [_][]const u8{
    "zigux/Makefile",
};

const WORKFLOW_PATH = [_][]const u8{
    ".github/workflows/zigux-bootstrap.yml",
};

const PHASE2_CONF_BRIDGE_MARKER = [_][]const u8{
    "`scripts/zigux/kconfig/conf_bridge.zig`",
};

const PHASE2_CONFDATA_BRIDGE_MARKER = [_][]const u8{
    "`scripts/zigux/kconfig/confdata_bridge.zig`",
};

const PHASE3_EXPORTS_MARKER = [_][]const u8{
    "`rust/exports.c`",
};

const PHASE3_EXPORT_SHIM_MARKER = [_][]const u8{
    "`zigux/kernel/export_shim.zig`",
};

const PHASE2_BOUNDARY_MARKER = [_][]const u8{
    "remain Phase 2 config-surface bridge references",
};

const PHASE3_BOUNDARY_MARKER = [_][]const u8{
    "remain Phase 3 export-boundary references rather than runtime-pilot evidence",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REVIEW_CHECKLIST_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (DOCS_README_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (LANE_SEQUENCING_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MODULE_SLICE_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SAMPLES_README_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (TESTS_README_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (WORKFLOW_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (CONTRACT_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (CURRENT_PHASE9_MAKE_ROUTES) |marker| try guard.requireMarker(text, marker);
    for (FORBIDDEN_PHASE9_MAKE_ROUTES) |marker| try guard.requireMarker(text, marker);
    for (EXACT_ONCE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_PHASE9_MAKE_COMMANDS) |marker| try guard.requireMarker(text, marker);
    for (REVIEW_CHECKLIST_PATH) |marker| try guard.requireMarker(text, marker);
    for (DOCS_README_PATH) |marker| try guard.requireMarker(text, marker);
    for (LANE_SEQUENCING_PATH) |marker| try guard.requireMarker(text, marker);
    for (MODULE_SLICE_PATH) |marker| try guard.requireMarker(text, marker);
    for (SCRIPTS_README_PATH) |marker| try guard.requireMarker(text, marker);
    for (SAMPLES_README_PATH) |marker| try guard.requireMarker(text, marker);
    for (TESTS_README_PATH) |marker| try guard.requireMarker(text, marker);
    for (CONTRACT_PATH) |marker| try guard.requireMarker(text, marker);
    for (MAKEFILE_PATH) |marker| try guard.requireMarker(text, marker);
    for (WORKFLOW_PATH) |marker| try guard.requireMarker(text, marker);
    for (PHASE2_CONF_BRIDGE_MARKER) |marker| try guard.requireMarker(text, marker);
    for (PHASE2_CONFDATA_BRIDGE_MARKER) |marker| try guard.requireMarker(text, marker);
    for (PHASE3_EXPORTS_MARKER) |marker| try guard.requireMarker(text, marker);
    for (PHASE3_EXPORT_SHIM_MARKER) |marker| try guard.requireMarker(text, marker);
    for (PHASE2_BOUNDARY_MARKER) |marker| try guard.requireMarker(text, marker);
    for (PHASE3_BOUNDARY_MARKER) |marker| try guard.requireMarker(text, marker);
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
