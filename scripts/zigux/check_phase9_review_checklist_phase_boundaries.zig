const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES=pass";
pub const self_test_pass_marker = "PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_SELF_TEST=pass";
pub const pass_marker = self_test_pass_marker;

const FileContract = struct { rel: []const u8, markers: []const []const u8 };
const RouteCommand = struct { route: []const u8, command: []const u8 };

const markers_0 = [_][]const u8{
    "if the change touches the shared Phase 9 runtime-pilot packet",
    "`Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`",
    "`scripts\\zigux/check_phase9_review_checklist_phase_boundaries.zig`",
    "`scripts\\zigux/check_phase9_trace_events_runtime_packet.zig`",
    "`scripts\\zigux/check_phase9_trace_events_direct_summary.zig`",
    "`scripts\\zigux/check_phase9_trace_events_summary_preservation.zig`",
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
    "`scripts/zigux/kconfig/conf_bridge.zig`",
    "`scripts/zigux/kconfig/confdata_bridge.zig`",
    "`rust/exports.c`",
    "`zigux/kernel/export_shim.zig`",
    "remain Phase 2 config-surface bridge references",
    "remain Phase 3 export-boundary references rather than runtime-pilot evidence",
};

const markers_1 = [_][]const u8{
    "Phase 9 notes - `Documentation/zigux/freeze-map.md` - `Documentation/zigux/phase15-study-only-anchor-accounting.md` - `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` - `Documentation/zigux/review-checklist.md` - `Documentation/zigux/README.md` - `scripts/zigux/README.md` - `samples/zigux/README.md` - `zigux/tests/README.md` - `scripts\\zigux/check_phase9_review_checklist_phase_boundaries.zig` - `scripts\\zigux/check_phase9_trace_events_runtime_packet.zig` - `scripts\\zigux/check_phase9_freeze_map_study_boundaries.zig` keep the shared Phase 9 reminder packet honest by routing any study-only freeze-map summary back through the dedicated accounting note, keeping the returned loader shard and the bounded `zigux/tests/phase9_build.zig` rerun bundle explicit as shared-owner evidence, and not treating `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` as runtime-substrate readiness evidence.",
    "keep the returned shared runtime-loader allocator/init-flow and command/environment boundary packet explicit as neighboring shared-owner evidence through `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`, the bounded `zigux/tests/phase9_build.zig` `phase9-runtime-loader-shared-tests` and `phase9-runtime-loader-command-env-boundary-guard-tests` shards, and the separate returned `samples/zigux/runtime_bitmap_loader.zig` scaffold without implying that blocked publication, install-root, or module-metadata surfaces are complete.",
    "keep the partial runtime bitmap reminder packet distinct from that returned loader shard too:",
};

const markers_2 = [_][]const u8{
    "Trusted mixed rereads on 2026-05-25 confirm four distinct current-master Phase 9 postures.",
    "The shared runtime-loader allocator/init-flow and command/environment boundary packet survives as a narrower shared-owner surface",
    "`zigux/tests/phase9_build.zig` still exposes `phase9-runtime-loader-allocator-init-flow-tests`, `phase9-runtime-loader-shared-tests`, `phase9-runtime-loader-command-env-boundary-guard-tests`, and `phase9-runtime-trace-events-loader-substrate-drift-tests`",
    "`zigux/kernel/runtime_loader_command_env_boundary_guard.zig`",
    "`phase9-runtime-loader-command-env-boundary-guard-tests`",
    "keep the Phase 8 command and environment ownership boundary explicit",
    "deferred `command_name`, exec-path, `PERF_EXEC_PATH`, and `PATH` cues stay with `tools/lib/subcmd/exec-cmd.zig`",
    "`LINES` and `COLUMNS` stay with `tools/lib/subcmd/help.zig`",
    "### 4. The runtime kretprobe side returns a family-local pilot packet, and shared reminder surfaces still need one-surface-at-a-time follow-through",
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
    "`scripts/zigux/kconfig/conf_bridge.zig`",
    "`scripts/zigux/kconfig/confdata_bridge.zig`",
    "`rust/exports.c`",
    "`zigux/kernel/export_shim.zig`",
    "remain Phase 2 config-surface bridge references",
    "remain Phase 3 export-boundary references rather than runtime-pilot evidence",
    "Treat stale shared-owner undercount or overclaim as the active blocker before reopening checker-local or runtime-behavior work.",
};

const markers_3 = [_][]const u8{
    "The adjacent shared build shard in `zigux/tests/phase9_build.zig` now names `phase9-runtime-trace-events-tests`, `phase9-runtime-trace-events-module-tests`, `phase9-runtime-loader-allocator-init-flow-tests`, `phase9-runtime-loader-command-env-boundary-guard-tests`, the dedicated `phase9-runtime-trace-events-loader-substrate-drift-tests` replay, the dedicated `phase9-runtime-trace-events-reinit-rollback-guard-tests` and `phase9-runtime-trace-events-reinit-reexit-guard-tests` replays, aggregate `phase9-runtime-loader-shared-tests`, and the broader `phase9-first-loadable-runtime-module-parity-survey-tests` route, but those rerun routes remain neighboring shared-owner evidence instead of expanding this module slice into returned family-local runtime-loader parity.",
    "Current `master` does now expose the shared loader-backed surfaces `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`, and the separate returned `samples/zigux/runtime_bitmap_loader.zig` scaffold through the adjacent `phase9-runtime-loader-shared-tests` shard plus the dedicated `phase9-runtime-trace-events-loader-substrate-drift-tests` replay in `zigux/tests/phase9_build.zig`, but those neighboring routes still stay shared-owner evidence rather than returned family-local trace-events proof.",
    "Current `master` still keeps the separate Phase 9 runtime bitmap reminder packet visible through `Documentation/zigux/phase9-runtime-bitmap-survey.md`",
    "`scripts/zigux/kconfig/conf_bridge.zig`",
    "`scripts/zigux/kconfig/confdata_bridge.zig`",
    "`rust/exports.c`",
    "`zigux/kernel/export_shim.zig`",
    "- `scripts/zigux/kconfig/conf_bridge.zig` and `scripts/zigux/kconfig/confdata_bridge.zig` remain Phase 2 config-surface bridge references.",
    "- `rust/exports.c` and `zigux/kernel/export_shim.zig` remain Phase 3 export-boundary references.",
    "- Those earlier-phase anchors stay adjacent context for the narrow trace-events packet rather than shared runtime-pilot evidence.",
};

const markers_4 = [_][]const u8{
    "`scripts/zigux/kconfig/conf_bridge.zig`",
    "`scripts/zigux/kconfig/confdata_bridge.zig`",
    "`rust/exports.c`",
    "`zigux/kernel/export_shim.zig`",
    "Keep the earlier non-owner boundary split explicit here too: `scripts/zigux/kconfig/conf_bridge.zig` and `scripts/zigux/kconfig/confdata_bridge.zig` remain Phase 2 config-surface bridge references, while `rust/exports.c` and `zigux/kernel/export_shim.zig` remain Phase 3 export-boundary references rather than runtime-pilot sample evidence.",
};

const markers_5 = [_][]const u8{
    "keep the returned shared runtime-loader allocator/init-flow and command/environment boundary packet explicit as neighboring shared-owner evidence through `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`, the bounded `zigux/tests/phase9_build.zig` `phase9-runtime-loader-allocator-init-flow-tests`, `phase9-runtime-loader-shared-tests`, and `phase9-runtime-loader-command-env-boundary-guard-tests` routes, and the separate returned `samples/zigux/runtime_bitmap_loader.zig` scaffold without implying that blocked publication, install-root, or module-metadata surfaces are complete",
    "keep the earlier non-owner boundary split explicit too: `tools/lib/subcmd/exec-cmd.zig` and `tools/lib/subcmd/help.zig` remain the command and environment owners, `scripts/zigux/kconfig/conf_bridge.zig` and `scripts/zigux/kconfig/confdata_bridge.zig` remain Phase 2 config-surface bridge references, and `rust/exports.c` plus `zigux/kernel/export_shim.zig` remain Phase 3 export-boundary references rather than runtime-pilot evidence.",
    "`scripts/zigux/kconfig/conf_bridge.zig`",
    "`scripts/zigux/kconfig/confdata_bridge.zig`",
    "`rust/exports.c`",
    "`zigux/kernel/export_shim.zig`",
    "remain Phase 2 config-surface bridge references",
    "remain Phase 3 export-boundary references rather than runtime-pilot evidence",
};

const markers_6 = [_][]const u8{
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

const markers_7 = [_][]const u8{
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

const contracts = [_]FileContract{
    .{ .rel = "Documentation/zigux/review-checklist.md", .markers = &markers_0 },
    .{ .rel = "Documentation/zigux/README.md", .markers = &markers_1 },
    .{ .rel = "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md", .markers = &markers_2 },
    .{ .rel = "Documentation/zigux/phase9-runtime-trace-events-module-slice.md", .markers = &markers_3 },
    .{ .rel = "samples/zigux/README.md", .markers = &markers_4 },
    .{ .rel = "zigux/tests/README.md", .markers = &markers_5 },
    .{ .rel = "zigux/kernel/runtime_loader_contract.zig", .markers = &markers_6 },
    .{ .rel = ".github/workflows/zigux-bootstrap.yml", .markers = &markers_7 },
};

const exact_markers_0 = [_][]const u8{
    "if the change touches the shared Phase 9 runtime-pilot packet",
    "keep that partial bitmap packet framed as a separate bounded Phase 9 runtime reminder rather than proof that the broader shared runtime-loader packet returned",
};

const exact_contracts = [_]FileContract{
    .{ .rel = "Documentation/zigux/review-checklist.md", .markers = &exact_markers_0 },
};

const required_routes = [_][]const u8{
    "phase9-runtime-atomic64-test",
    "phase9-runtime-bitmap-test",
    "phase9-runtime-loader-shared-test",
    "phase9-runtime-loader-command-env-boundary-guard-test",
    "phase9-runtime-trace-events-test",
    "phase9-runtime-kretprobe-test",
    "phase9-first-loadable-runtime-module-parity-test",
    "phase9-test",
};

const forbidden_routes = [_][]const u8{
    "phase9",
    "phase9-validate",
    "phase9-runtime-trace-events-sample-tests",
};

const route_commands = [_]RouteCommand{
    .{ .route = "phase9-runtime-atomic64-test", .command = "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase9-runtime-atomic64-tests --build-file zigux/tests/phase9_build.zig --summary all" },
    .{ .route = "phase9-runtime-bitmap-test", .command = "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase9-runtime-bitmap-tests --build-file zigux/tests/phase9_build.zig --summary all" },
    .{ .route = "phase9-runtime-loader-shared-test", .command = "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig --summary all" },
    .{ .route = "phase9-runtime-loader-command-env-boundary-guard-test", .command = "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase9-runtime-loader-command-env-boundary-guard-tests --build-file zigux/tests/phase9_build.zig --summary all" },
    .{ .route = "phase9-runtime-trace-events-test", .command = "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase9-runtime-trace-events-tests --build-file zigux/tests/phase9_build.zig --summary all" },
    .{ .route = "phase9-runtime-kretprobe-test", .command = "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase9-runtime-kretprobe-tests --build-file zigux/tests/phase9_build.zig --summary all" },
    .{ .route = "phase9-first-loadable-runtime-module-parity-test", .command = "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase9-first-loadable-runtime-module-parity-behavior-tests --build-file zigux/tests/phase9_build.zig --summary all" },
};

fn lineDefinesTarget(line_raw: []const u8, route: []const u8) bool {
    const line = std.mem.trimEnd(u8, line_raw, "\r");
    if (line.len == 0 or line[0] == ' ' or line[0] == '\t' or line[0] == '#') return false;
    const colon = std.mem.indexOfScalar(u8, line, ':') orelse return false;
    var targets = std.mem.tokenizeAny(u8, line[0..colon], " \t");
    while (targets.next()) |target| if (std.mem.eql(u8, target, route)) return true;
    return false;
}

fn targetSection(text: []const u8, route: []const u8) ?[]const u8 {
    var offset: usize = 0;
    var section_start: ?usize = null;
    while (offset <= text.len) {
        const line_end = std.mem.indexOfScalarPos(u8, text, offset, '\n') orelse text.len;
        const line = text[offset..line_end];
        if (lineDefinesTarget(line, route)) { section_start = offset; } else if (section_start != null) {
            const logical = std.mem.trimEnd(u8, line, "\r");
            if (logical.len != 0 and logical[0] != ' ' and logical[0] != '\t' and logical[0] != '#') {
                if (std.mem.indexOfScalar(u8, logical, ':') != null) return text[section_start.?..offset];
            }
        }
        if (line_end == text.len) break;
        offset = line_end + 1;
    }
    if (section_start) |start| return text[start..];
    return null;
}

fn checkMakefile(text: []const u8) !void {
    for (required_routes) |route| try std.testing.expect(targetSection(text, route) != null);
    for (forbidden_routes) |route| try std.testing.expect(targetSection(text, route) == null);
    for (route_commands) |item| {
        const section = targetSection(text, item.route) orelse return error.MissingMakeRoute;
        try guard.requireMarker(section, item.command);
    }
}

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for (contracts) |contract| {
        const file_path = try guard.joinPath(allocator, root, contract.rel);
        defer allocator.free(file_path);
        const text = try guard.readUtf8File(io, allocator, file_path);
        defer allocator.free(text);
        for (contract.markers) |marker| {
            guard.requireMarker(text, marker) catch |err| {
                try guard.printLine(io, "PHASE9_REVIEW_MISSING_MARKER_FILE={s}", .{contract.rel});
                try guard.printLine(io, "PHASE9_REVIEW_MISSING_MARKER_VALUE={s}", .{marker});
                return err;
            };
        }
    }
    for (exact_contracts) |contract| {
        const file_path = try guard.joinPath(allocator, root, contract.rel);
        defer allocator.free(file_path);
        const text = try guard.readUtf8File(io, allocator, file_path);
        defer allocator.free(text);
        for (contract.markers) |marker| try guard.requireExactCount(text, marker, 1);
    }
    const makefile_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(makefile_path);
    const makefile = try guard.readUtf8File(io, allocator, makefile_path);
    defer allocator.free(makefile);
    try checkMakefile(makefile);
}

fn emitCounts(io: Io) !void {
    try guard.printLine(io, "PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_FILE_COUNT=9", .{});
    try guard.printLine(io, "PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_MARKER_COUNT=111", .{});
    try guard.printLine(io, "PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_EXACT_ONCE_MARKER_COUNT=2", .{});
    try guard.printLine(io, "PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_REQUIRED_MAKEFILE_ROUTE_COUNT=8", .{});
    try guard.printLine(io, "PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_REQUIRED_MAKEFILE_COMMAND_COUNT=7", .{});
    try guard.printLine(io, "PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_FORBIDDEN_MAKEFILE_ROUTE_COUNT=3", .{});
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    try checkRepo(io, allocator, root);
    try std.testing.expectEqual(@as(usize, 111), comptime blk: {
        var total: usize = 0;
        for (contracts) |contract| total += contract.markers.len;
        break :blk total;
    });
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    try emitCounts(io);
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(init.arena.allocator());
    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) { self_test = true; continue; }
        if (std.mem.eql(u8, arg, "--root") or std.mem.eql(u8, arg, "--repo-root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1; explicit_root = args[index]; continue;
        }
        std.process.exit(2);
    }
    if (self_test) std.process.exit(try runSelfTest(io, allocator));
    const root = explicit_root orelse try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);
    checkRepo(io, allocator, root) catch std.process.exit(1);
    try guard.printLine(io, "{s}", .{live_pass_marker});
    try emitCounts(io);
}

// Legacy generated marker surface retained for source-compatibility checks.
// const std = @import("std");
// const Io = std.Io;
// const guard = @import("zigux_guard.zig");
//
// pub const pass_marker = "PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_SELF_TEST=pass";
//
// const REVIEW_CHECKLIST_REQUIRED_MARKERS = [_][]const u8{
//     "if the change touches the shared Phase 9 runtime-pilot packet",
//     "`Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`",
//     "`scripts/zigux/check_phase9_review_checklist_phase_boundaries.zig`",
//     "`scripts/zigux/check_phase9_trace_events_runtime_packet.zig`",
//     "`scripts/zigux/check_phase9_trace_events_direct_summary.zig`",
//     "`scripts/zigux/check_phase9_trace_events_summary_preservation.zig`",
//     "`samples/zigux/runtime_trace_events.zig`",
//     "`samples/zigux/runtime_trace_events_unregistered_gate.zig`",
//     "`samples/zigux/runtime_trace_events_exit_rollback_guard.zig`",
//     "`samples/zigux/runtime_trace_events_registration_reentry_gate.zig`",
//     "`samples/zigux/runtime_trace_events_reinit_rollback_guard.zig`",
//     "`samples/zigux/runtime_trace_events_reinit_reexit_guard.zig`",
//     ".provides_selftest_hook = true",
//     "initialized, selftest_complete, and exited lifecycle tracking",
//     "failed-exit rollback explicit after reusable selftest replay",
//     "balanced registration re-entry companion that keeps function-thread registration reusable before and after selftest",
//     "rejected re-init rollback companion that keeps initialized, selftest_complete, and exited summaries stable after rejected `init()` retries",
//     "paired rejected re-init plus rejected re-exit rollback companion that keeps initialized direct activity and selftest-ready replay explicit without drift",
//     "direct summary and summary-preservation checkers that keep the shipped trace-events packet replayable",
//     "`zigux/tests/runtime_loader_allocator_init_flow.zig`",
//     "`zigux/kernel/runtime_loader.zig`",
//     "`zigux/kernel/runtime_loader_contract.zig`",
//     "`zigux/kernel/runtime_loader_command_env_boundary_guard.zig`",
//     "`samples/zigux/runtime_*_loader.zig`",
//     "`phase9-runtime-loader-command-env-boundary-guard-tests`",
//     "the older `Documentation/zigux/phase9-runtime-loader-gap-survey.md`, `zigux/tests/runtime_loader_gap_survey.zig`, and `samples/zigux/runtime_trace_events_loader.zig` stay historical wider-family vocabulary",
//     "`zigux/tests/runtime_loader_gap_manifest.json` stays in that same historical wider-family bucket until the same kind of fresh shared-owner reread returns it",
//     "older blocked module-metadata and depmod-publication vocabulary such as `.modinfo`, `MODULE_ALIAS()`, `modules.alias`, `modules.order`, `modules.builtin`, `Module.symvers`, module install-root, and depmod script, manifest, or alias-output state stays historical blocked-boundary vocabulary until a fresh repo reread restores a current shared owner surface for that packet",
//     "the partial separate runtime bitmap reminder packet stays explicit in `samples/zigux/README.md`, `Documentation/zigux/README.md`, and `Documentation/zigux/review-checklist.md`",
//     "the shared `zigux/tests/phase9_build.zig` bundle now reruns that partial bitmap packet through `phase9-runtime-bitmap-cold-stage-guard-tests` plus the aggregate `phase9-runtime-bitmap-tests` handle",
//     "keep that partial bitmap packet framed as a separate bounded Phase 9 runtime reminder rather than proof that the broader shared runtime-loader packet returned",
//     "PHASE2_CONF_BRIDGE_MARKER",
//     "PHASE2_CONFDATA_BRIDGE_MARKER",
//     "PHASE3_EXPORTS_MARKER",
//     "PHASE3_EXPORT_SHIM_MARKER",
//     "PHASE2_BOUNDARY_MARKER",
//     "PHASE3_BOUNDARY_MARKER",
// };
//
// const DOCS_README_REQUIRED_MARKERS = [_][]const u8{
//     "Phase 9 notes - `Documentation/zigux/freeze-map.md` - `Documentation/zigux/phase15-study-only-anchor-accounting.md` - `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` - `Documentation/zigux/review-checklist.md` - `Documentation/zigux/README.md` - `scripts/zigux/README.md` - `samples/zigux/README.md` - `zigux/tests/README.md` - `scripts/zigux/check_phase9_review_checklist_phase_boundaries.zig` - `scripts/zigux/check_phase9_trace_events_runtime_packet.zig` - `scripts/zigux/check_phase9_freeze_map_study_boundaries.zig` keep the shared Phase 9 reminder packet honest by routing any study-only freeze-map summary back through the dedicated accounting note, keeping the returned loader shard and the bounded `zigux/tests/phase9_build.zig` rerun bundle explicit as shared-owner evidence, and not treating `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` as runtime-substrate readiness evidence.",
//     "keep the returned shared runtime-loader allocator/init-flow and command/environment boundary packet explicit as neighboring shared-owner evidence through `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`, the bounded `zigux/tests/phase9_build.zig` `phase9-runtime-loader-shared-tests` and `phase9-runtime-loader-command-env-boundary-guard-tests` shards, and the separate returned `samples/zigux/runtime_bitmap_loader.zig` scaffold without implying that blocked publication, install-root, or module-metadata surfaces are complete.",
//     "keep the partial runtime bitmap reminder packet distinct from that returned loader shard too:",
// };
//
// const LANE_SEQUENCING_REQUIRED_MARKERS = [_][]const u8{
//     "Trusted mixed rereads on 2026-05-25 confirm four distinct current-master Phase 9 postures.",
//     "The shared runtime-loader allocator/init-flow and command/environment boundary packet survives as a narrower shared-owner surface",
//     "`zigux/tests/phase9_build.zig` still exposes `phase9-runtime-loader-allocator-init-flow-tests`, `phase9-runtime-loader-shared-tests`, `phase9-runtime-loader-command-env-boundary-guard-tests`, and `phase9-runtime-trace-events-loader-substrate-drift-tests`",
//     "`zigux/kernel/runtime_loader_command_env_boundary_guard.zig`",
//     "`phase9-runtime-loader-command-env-boundary-guard-tests`",
//     "keep the Phase 8 command and environment ownership boundary explicit",
//     "deferred `command_name`, exec-path, `PERF_EXEC_PATH`, and `PATH` cues stay with `tools/lib/subcmd/exec-cmd.zig`",
//     "`LINES` and `COLUMNS` stay with `tools/lib/subcmd/help.zig`",
//     "`samples/zigux/runtime_kretprobe.zig`",
//     "`zigux/tests/runtime_kretprobe_module.zig`",
//     "`zigux/tests/runtime_first_loadable_parity_behavior.zig`",
//     "`phase9-runtime-kretprobe-sample-tests`",
//     "`phase9-runtime-kretprobe-module-tests`",
//     "`phase9-runtime-kretprobe-tests`",
//     "`phase9-first-loadable-runtime-module-parity-behavior-tests`",
//     "current `master` no longer supports treating kretprobe as absent from the cross-family parity surface",
//     "keep `modules.order`, `modules.builtin`, `Module.symvers`, and module install-root wording framed as blocked wider-family vocabulary too",
//     "keep blocked depmod script, depmod manifest, and depmod alias-output wording framed as historical wider-family vocabulary too until trusted direct rereads return a current shared owner surface for that publication packet",
//     "PHASE2_CONF_BRIDGE_MARKER",
//     "PHASE2_CONFDATA_BRIDGE_MARKER",
//     "PHASE3_EXPORTS_MARKER",
//     "PHASE3_EXPORT_SHIM_MARKER",
//     "PHASE2_BOUNDARY_MARKER",
//     "PHASE3_BOUNDARY_MARKER",
//     "Treat stale shared-owner undercount or overclaim as the active blocker before reopening checker-local or runtime-behavior work.",
// };
//
// const MODULE_SLICE_REQUIRED_MARKERS = [_][]const u8{
//     "The adjacent shared build shard in `zigux/tests/phase9_build.zig` now names `phase9-runtime-trace-events-tests`, `phase9-runtime-trace-events-module-tests`, `phase9-runtime-loader-allocator-init-flow-tests`, `phase9-runtime-loader-command-env-boundary-guard-tests`, the dedicated `phase9-runtime-trace-events-loader-substrate-drift-tests` replay, the dedicated `phase9-runtime-trace-events-reinit-rollback-guard-tests` and `phase9-runtime-trace-events-reinit-reexit-guard-tests` replays, aggregate `phase9-runtime-loader-shared-tests`, and the broader `phase9-first-loadable-runtime-module-parity-survey-tests` route, but those rerun routes remain neighboring shared-owner evidence instead of expanding this module slice into returned family-local runtime-loader parity.",
//     "Current `master` does now expose the shared loader-backed surfaces `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`, and the separate returned `samples/zigux/runtime_bitmap_loader.zig` scaffold through the adjacent `phase9-runtime-loader-shared-tests` shard plus the dedicated `phase9-runtime-trace-events-loader-substrate-drift-tests` replay in `zigux/tests/phase9_build.zig`, but those neighboring routes still stay shared-owner evidence rather than returned family-local trace-events proof.",
//     "Current `master` still keeps the separate Phase 9 runtime bitmap reminder packet visible through `Documentation/zigux/phase9-runtime-bitmap-survey.md`",
//     "PHASE2_CONF_BRIDGE_MARKER",
//     "PHASE2_CONFDATA_BRIDGE_MARKER",
//     "PHASE3_EXPORTS_MARKER",
//     "PHASE3_EXPORT_SHIM_MARKER",
//     "- `scripts/zigux/kconfig/conf_bridge.zig` and `scripts/zigux/kconfig/confdata_bridge.zig` remain Phase 2 config-surface bridge references.",
//     "- `rust/exports.c` and `zigux/kernel/export_shim.zig` remain Phase 3 export-boundary references.",
//     "- Those earlier-phase anchors stay adjacent context for the narrow trace-events packet rather than shared runtime-pilot evidence.",
// };
//
// const SAMPLES_README_REQUIRED_MARKERS = [_][]const u8{
//     "PHASE2_CONF_BRIDGE_MARKER",
//     "PHASE2_CONFDATA_BRIDGE_MARKER",
//     "PHASE3_EXPORTS_MARKER",
//     "PHASE3_EXPORT_SHIM_MARKER",
//     "Keep the earlier non-owner boundary split explicit here too: `scripts/zigux/kconfig/conf_bridge.zig` and `scripts/zigux/kconfig/confdata_bridge.zig` remain Phase 2 config-surface bridge references, while `rust/exports.c` and `zigux/kernel/export_shim.zig` remain Phase 3 export-boundary references rather than runtime-pilot sample evidence.",
// };
//
// const TESTS_README_REQUIRED_MARKERS = [_][]const u8{
//     "keep the returned shared runtime-loader allocator/init-flow and command/environment boundary packet explicit as neighboring shared-owner evidence through `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`, the bounded `zigux/tests/phase9_build.zig` `phase9-runtime-loader-allocator-init-flow-tests`, `phase9-runtime-loader-shared-tests`, and `phase9-runtime-loader-command-env-boundary-guard-tests` routes, and the separate returned `samples/zigux/runtime_bitmap_loader.zig` scaffold without implying that blocked publication, install-root, or module-metadata surfaces are complete",
//     "keep the earlier non-owner boundary split explicit too: `tools/lib/subcmd/exec-cmd.zig` and `tools/lib/subcmd/help.zig` remain the command and environment owners, `scripts/zigux/kconfig/conf_bridge.zig` and `scripts/zigux/kconfig/confdata_bridge.zig` remain Phase 2 config-surface bridge references, and `rust/exports.c` plus `zigux/kernel/export_shim.zig` remain Phase 3 export-boundary references rather than runtime-pilot evidence.",
//     "PHASE2_CONF_BRIDGE_MARKER",
//     "PHASE2_CONFDATA_BRIDGE_MARKER",
//     "PHASE3_EXPORTS_MARKER",
//     "PHASE3_EXPORT_SHIM_MARKER",
//     "PHASE2_BOUNDARY_MARKER",
//     "PHASE3_BOUNDARY_MARKER",
// };
//
// const WORKFLOW_REQUIRED_MARKERS = [_][]const u8{
//     "zig run scripts/zigux/check_phase9_review_checklist_phase_boundaries.zig -- --self-test",
//     "zig run scripts/zigux/check_phase9_review_checklist_phase_boundaries.zig --",
//     "zig run scripts/zigux/check_phase9_freeze_map_study_boundaries.zig -- --self-test",
//     "zig run scripts/zigux/check_phase9_freeze_map_study_boundaries.zig --",
//     "zig run scripts/zigux/check_phase9_trace_events_runtime_packet.zig -- --self-test",
//     "zig run scripts/zigux/check_phase9_trace_events_runtime_packet.zig --",
//     "zig run scripts/zigux/check_phase9_trace_events_direct_summary.zig -- --self-test",
//     "zig run scripts/zigux/check_phase9_trace_events_direct_summary.zig --",
//     "zig run scripts/zigux/check_phase9_trace_events_summary_preservation.zig -- --self-test",
//     "zig run scripts/zigux/check_phase9_trace_events_summary_preservation.zig --",
// };
//
// const CONTRACT_REQUIRED_MARKERS = [_][]const u8{
//     "test \"LoadPlan keeps blocked publication outputs and install-root surfaces out of the shared request contract\" {",
//     "const blocked_publication_fields = [_][]const u8{",
//     "\"modinfo\",",
//     "\"module_alias\",",
//     "\"modules_alias_path\",",
//     "\"module_install_root\",",
//     "\"modules_order_path\",",
//     "\"modules_builtin_path\",",
//     "\"module_symvers_path\",",
//     "\"depmod_script\",",
//     "\"depmod_manifest\",",
//     "try std.testing.expect(!@hasField(LoadPlan, field));",
// };
//
// const CURRENT_PHASE9_MAKE_ROUTES = [_][]const u8{
//     "phase9-runtime-atomic64-test",
//     "phase9-runtime-bitmap-test",
//     "phase9-runtime-loader-shared-test",
//     "phase9-runtime-loader-command-env-boundary-guard-test",
//     "phase9-runtime-trace-events-test",
//     "phase9-runtime-kretprobe-test",
//     "phase9-first-loadable-runtime-module-parity-test",
//     "phase9-test",
// };
//
// const FORBIDDEN_PHASE9_MAKE_ROUTES = [_][]const u8{
//     "phase9",
//     "phase9-validate",
//     "phase9-runtime-trace-events-sample-tests",
// };
//
// const EXACT_ONCE_MARKERS = [_][]const u8{
//     "if the change touches the shared Phase 9 runtime-pilot packet",
//     "keep that partial bitmap packet framed as a separate bounded Phase 9 runtime reminder rather than proof that the broader shared runtime-loader packet returned",
// };
//
// const REQUIRED_PHASE9_MAKE_COMMANDS = [_][]const u8{
//     "phase9-runtime-atomic64-test",
//     "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase9-runtime-atomic64-tests --build-file zigux/tests/phase9_build.zig --summary all",
//     "phase9-runtime-bitmap-test",
//     "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase9-runtime-bitmap-tests --build-file zigux/tests/phase9_build.zig --summary all",
//     "phase9-runtime-loader-shared-test",
//     "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig --summary all",
//     "phase9-runtime-loader-command-env-boundary-guard-test",
//     "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase9-runtime-loader-command-env-boundary-guard-tests --build-file zigux/tests/phase9_build.zig --summary all",
//     "phase9-runtime-trace-events-test",
//     "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase9-runtime-trace-events-tests --build-file zigux/tests/phase9_build.zig --summary all",
//     "phase9-runtime-kretprobe-test",
//     "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase9-runtime-kretprobe-tests --build-file zigux/tests/phase9_build.zig --summary all",
//     "phase9-first-loadable-runtime-module-parity-test",
//     "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase9-first-loadable-runtime-module-parity-behavior-tests --build-file zigux/tests/phase9_build.zig --summary all",
// };
//
// const REVIEW_CHECKLIST_PATH = [_][]const u8{
//     "Documentation/zigux/review-checklist.md",
// };
//
// const DOCS_README_PATH = [_][]const u8{
//     "Documentation/zigux/README.md",
// };
//
// const LANE_SEQUENCING_PATH = [_][]const u8{
//     "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md",
// };
//
// const MODULE_SLICE_PATH = [_][]const u8{
//     "Documentation/zigux/phase9-runtime-trace-events-module-slice.md",
// };
//
// const SCRIPTS_README_PATH = [_][]const u8{
//     "scripts/zigux/README.md",
// };
//
// const SAMPLES_README_PATH = [_][]const u8{
//     "samples/zigux/README.md",
// };
//
// const TESTS_README_PATH = [_][]const u8{
//     "zigux/tests/README.md",
// };
//
// const CONTRACT_PATH = [_][]const u8{
//     "zigux/kernel/runtime_loader_contract.zig",
// };
//
// const MAKEFILE_PATH = [_][]const u8{
//     "zigux/Makefile",
// };
//
// const WORKFLOW_PATH = [_][]const u8{
//     ".github/workflows/zigux-bootstrap.yml",
// };
//
// const PHASE2_CONF_BRIDGE_MARKER = [_][]const u8{
//     "`scripts/zigux/kconfig/conf_bridge.zig`",
// };
//
// const PHASE2_CONFDATA_BRIDGE_MARKER = [_][]const u8{
//     "`scripts/zigux/kconfig/confdata_bridge.zig`",
// };
//
// const PHASE3_EXPORTS_MARKER = [_][]const u8{
//     "`rust/exports.c`",
// };
//
// const PHASE3_EXPORT_SHIM_MARKER = [_][]const u8{
//     "`zigux/kernel/export_shim.zig`",
// };
//
// const PHASE2_BOUNDARY_MARKER = [_][]const u8{
//     "remain Phase 2 config-surface bridge references",
// };
//
// const PHASE3_BOUNDARY_MARKER = [_][]const u8{
//     "remain Phase 3 export-boundary references rather than runtime-pilot evidence",
// };
//
// pub fn checkText(text: []const u8) guard.GuardError!void {
//     for (REVIEW_CHECKLIST_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (DOCS_README_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (LANE_SEQUENCING_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (MODULE_SLICE_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (SAMPLES_README_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (TESTS_README_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (WORKFLOW_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (CONTRACT_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (CURRENT_PHASE9_MAKE_ROUTES) |marker| try guard.requireMarker(text, marker);
//     for (FORBIDDEN_PHASE9_MAKE_ROUTES) |marker| try guard.requireMarker(text, marker);
//     for (EXACT_ONCE_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_PHASE9_MAKE_COMMANDS) |marker| try guard.requireMarker(text, marker);
//     for (REVIEW_CHECKLIST_PATH) |marker| try guard.requireMarker(text, marker);
//     for (DOCS_README_PATH) |marker| try guard.requireMarker(text, marker);
//     for (LANE_SEQUENCING_PATH) |marker| try guard.requireMarker(text, marker);
//     for (MODULE_SLICE_PATH) |marker| try guard.requireMarker(text, marker);
//     for (SCRIPTS_README_PATH) |marker| try guard.requireMarker(text, marker);
//     for (SAMPLES_README_PATH) |marker| try guard.requireMarker(text, marker);
//     for (TESTS_README_PATH) |marker| try guard.requireMarker(text, marker);
//     for (CONTRACT_PATH) |marker| try guard.requireMarker(text, marker);
//     for (MAKEFILE_PATH) |marker| try guard.requireMarker(text, marker);
//     for (WORKFLOW_PATH) |marker| try guard.requireMarker(text, marker);
//     for (PHASE2_CONF_BRIDGE_MARKER) |marker| try guard.requireMarker(text, marker);
//     for (PHASE2_CONFDATA_BRIDGE_MARKER) |marker| try guard.requireMarker(text, marker);
//     for (PHASE3_EXPORTS_MARKER) |marker| try guard.requireMarker(text, marker);
//     for (PHASE3_EXPORT_SHIM_MARKER) |marker| try guard.requireMarker(text, marker);
//     for (PHASE2_BOUNDARY_MARKER) |marker| try guard.requireMarker(text, marker);
//     for (PHASE3_BOUNDARY_MARKER) |marker| try guard.requireMarker(text, marker);
// }
//
// pub fn main() !void {
//     var gpa = std.heap.GeneralPurposeAllocator(.{}){};
//     defer _ = gpa.deinit();
//     const allocator = gpa.allocator();
//     const io = std.Io.Threaded.init(allocator, .{});
//     defer io.deinit();
//     const args = try std.process.argsAlloc(allocator);
//     defer std.process.argsFree(allocator, args);
//
//     var self_test = false;
//     for (args[1..]) |arg| {
//         if (std.mem.eql(u8, arg, "--self-test")) self_test = true;
//     }
//
//     if (self_test) {
//         try checkText("");
//         try guard.printLine(io, "{s}", .{pass_marker});
//         return;
//     }
//
//     const root = try guard.repoRootFromScript(allocator);
//     defer allocator.free(root);
//     const workflow_rel = ".github/workflows/zigux-bootstrap.yml";
//     const workflow_path = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ root, workflow_rel });
//     defer allocator.free(workflow_path);
//     const text = try guard.readUtf8File(io, allocator, workflow_path);
//     defer allocator.free(text);
//     try checkText(text);
//     try guard.printLine(io, "{s}", .{pass_marker});
// }
//
