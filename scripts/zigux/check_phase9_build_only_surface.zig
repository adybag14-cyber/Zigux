const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE9_BUILD_ONLY_SURFACE=pass";
pub const self_test_pass_marker = "PHASE9_BUILD_ONLY_SURFACE_SELF_TEST=pass";
pub const pass_marker = self_test_pass_marker;

const FileContract = struct { rel: []const u8, markers: []const []const u8 };

const markers_0 = [_][]const u8{
    "keep the returned shared runtime-loader allocator/init-flow and command/environment boundary packet explicit as neighboring shared-owner evidence through `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`",
    "`zigux/tests/runtime_loader_allocator_init_flow.zig`",
    "`zigux/kernel/runtime_loader.zig`",
    "`zigux/kernel/runtime_loader_contract.zig`",
    "the bounded `zigux/tests/phase9_build.zig` `phase9-runtime-loader-shared-tests` and `phase9-runtime-loader-command-env-boundary-guard-tests` shards",
    "`samples/zigux/runtime_bitmap_cold_stage_guard.zig`",
    "the runtime bitmap sample, cold-stage guard, survey, module, diff, loader, and top-bit companion packet members",
    "`phase9-runtime-bitmap-cold-stage-guard-tests` plus the aggregate `phase9-runtime-bitmap-tests` handle",
};

const markers_1 = [_][]const u8{
    "`samples/zigux/runtime_bitmap_direct_init_contract.zig`",
    "Keep the direct-init companion explicit when reminder text summarizes sample-local init normalization, unsorted duplicate input collapse, nth-set ordering, and formatted sparse-summary stability.",
    "`samples/zigux/runtime_bitmap_cold_stage_guard.zig`",
    "Keep `samples/zigux/runtime_bitmap_cold_stage_guard.zig` explicit as the returned cold-stage sample-root guard companion;",
    "`phase9-runtime-bitmap-cold-stage-guard-tests`",
    "`phase9-runtime-bitmap-tests`",
};

const markers_2 = [_][]const u8{
    "if the change touches the shared Phase 9 runtime-pilot packet",
    "`Documentation/zigux/phase9-runtime-loader-gap-survey.md`",
    "`zigux/tests/runtime_loader_gap_survey.zig`",
    "`zigux/tests/runtime_loader_allocator_init_flow.zig`",
    "`zigux/kernel/runtime_loader.zig`",
    "`zigux/kernel/runtime_loader_contract.zig`",
    "`samples/zigux/runtime_*_loader.zig`",
    "the returned shared runtime-loader allocator/init-flow packet remains neighboring shared-owner evidence",
};

const markers_3 = [_][]const u8{
    "The shared runtime-loader allocator/init-flow and command/environment boundary packet survives as a narrower shared-owner surface",
    "Trusted GitHub rereads on 2026-05-25 directly recover the still-live shared loader packet through `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`, the still-returned `samples/zigux/runtime_bitmap_loader.zig` scaffold, and the bounded `zigux/tests/phase9_build.zig` shard.",
    "`zigux/tests/phase9_build.zig` still exposes `phase9-runtime-loader-allocator-init-flow-tests`, `phase9-runtime-loader-shared-tests`, `phase9-runtime-loader-command-env-boundary-guard-tests`, and `phase9-runtime-trace-events-loader-substrate-drift-tests`",
    "`phase9-runtime-loader-command-env-boundary-guard-tests`",
    "`samples/zigux/runtime_bitmap_cold_stage_guard.zig`",
    "`zigux/tests/phase9_build.zig` keeps the returned bitmap packet inside the shared rerun bundle through `phase9-runtime-bitmap-tests` plus the dedicated `phase9-runtime-bitmap-cold-stage-guard-tests` route",
    "`scripts/zigux/README.md` now again carries a dedicated shared Phase 9 reminder section on current `master`, so keep counting it as active same-lane evidence beside the aligned docs-root and tests-root packet",
    "keep the Phase 8 command and environment ownership boundary explicit: deferred `command_name`, exec-path, `PERF_EXEC_PATH`, and `PATH` cues stay with `tools/lib/subcmd/exec-cmd.zig`, while `LINES` and `COLUMNS` stay with `tools/lib/subcmd/help.zig`",
    "current Phase 9 material still does not prove shipped runtime command or environment activation control; it proves only that the shared runtime-loader packet keeps those Phase 8 control surfaces out of the loader contract",
};

const markers_4 = [_][]const u8{
    "`samples/zigux/runtime_bitmap_cold_stage_guard.zig`",
    "Keep `samples/zigux/runtime_bitmap_cold_stage_guard.zig` explicit as the returned cold-stage selftest, exit, mutation, and source-lifecycle guard companion proof for the same runtime bitmap starter.",
    "`zigux/tests/runtime_bitmap_module.zig`",
    "`zigux/tests/runtime_bitmap_diff.zig`",
};

const markers_5 = [_][]const u8{
    "- `scripts\\zigux/validate_phase9.zig`, `scripts\\zigux/check_phase9_review_checklist_phase_boundaries.zig`, `scripts\\zigux/check_phase9_freeze_map_study_boundaries.zig`, `scripts\\zigux/check_phase9_trace_events_runtime_packet.zig`, `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/README.md`, `samples/zigux/README.md`, and `zigux/tests/README.md` keep the shipped shared Phase 9 reminder packet explicit from the scripts root",
    "zig run validate_phase9.zig --self-test",
    "zig run validate_phase9.zig --",
    "`zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`, the bounded `zigux/tests/phase9_build.zig` `phase9-runtime-loader-shared-tests` and `phase9-runtime-loader-command-env-boundary-guard-tests` shards, and the separate returned `samples/zigux/runtime_bitmap_loader.zig` scaffold keep the narrower shared runtime-loader allocator/init-flow and command/environment boundary packet explicit beside the still-blocked module-metadata and install-root surfaces",
    "keep `Documentation/zigux/phase9-runtime-loader-gap-survey.md`, `zigux/tests/runtime_loader_gap_manifest.json`, `zigux/tests/runtime_loader_gap_survey.zig`, and `samples/zigux/runtime_trace_events_loader.zig` framed as historical wider-family vocabulary until trusted direct rereads return them",
};

const markers_6 = [_][]const u8{
    "`samples/zigux/runtime_bitmap_cold_stage_guard.zig`",
    "keep the bounded runtime bitmap reminder packet distinct from that returned loader shard too",
    "keep the bounded Phase 9 build bundle explicit as rerun vocabulary only",
    "first-loadable parity-behavior handle",
};

const markers_7 = [_][]const u8{
    "const runtime_loader_allocator_init_flow_module = b.createModule(.{",
    ".root_source_file = b.path(\"runtime_loader_allocator_init_flow.zig\"),",
    "const runtime_loader_allocator_init_flow_tests = b.addTest(.{",
    "\"phase9-runtime-loader-allocator-init-flow-tests\",",
    "const phase9_runtime_loader_kernel = b.step(",
    "\"phase9-runtime-loader-kernel-tests\",",
    "phase9_runtime_loader_kernel.dependOn(&run_runtime_loader_kernel_tests.step);",
    "const phase9_runtime_loader_contract = b.step(",
    "\"phase9-runtime-loader-contract-tests\",",
    "phase9_runtime_loader_contract.dependOn(&run_runtime_loader_contract_tests.step);",
    "const runtime_loader_command_env_boundary_guard_module = b.createModule(.{",
    ".root_source_file = b.path(\"../kernel/runtime_loader_command_env_boundary_guard.zig\"),",
    "const runtime_loader_command_env_boundary_guard_tests = b.addTest(.{",
    "\"phase9-runtime-loader-command-env-boundary-guard-tests\",",
    "const runtime_bitmap_direct_init_contract_module = b.createModule(.{",
    ".root_source_file = b.path(\"../../samples/zigux/runtime_bitmap_direct_init_contract.zig\"),",
    "const runtime_bitmap_direct_init_contract_tests = b.addTest(.{",
    "\"phase9-runtime-bitmap-direct-init-contract-tests\",",
    "const runtime_bitmap_cold_stage_guard_module = b.createModule(.{",
    ".root_source_file = b.path(\"../../samples/zigux/runtime_bitmap_cold_stage_guard.zig\"),",
    "const runtime_bitmap_cold_stage_guard_tests = b.addTest(.{",
    "\"phase9-runtime-bitmap-cold-stage-guard-tests\",",
    "const phase9_runtime_bitmap_direct_init_contract = b.step(",
    "phase9_runtime_bitmap_direct_init_contract.dependOn(",
    "const phase9_runtime_bitmap_cold_stage_guard = b.step(",
    "phase9_runtime_bitmap_cold_stage_guard.dependOn(",
    "const phase9_runtime_loader_command_env_boundary_guard = b.step(",
    "phase9_runtime_loader_command_env_boundary_guard.dependOn(\n        &run_runtime_loader_command_env_boundary_guard_tests.step,\n    );",
    "const phase9_runtime_loader_shared = b.step(",
    "\"phase9-runtime-loader-shared-tests\",",
    "phase9_runtime_loader_shared.dependOn(&run_runtime_loader_kernel_tests.step);",
    "phase9_runtime_loader_shared.dependOn(&run_runtime_loader_contract_tests.step);",
    "phase9_runtime_loader_shared.dependOn(&run_runtime_loader_allocator_init_flow_tests.step);",
    "phase9_runtime_loader_shared.dependOn(\n        &run_runtime_loader_command_env_boundary_guard_tests.step,\n    );",
    "phase9_runtime_loader_shared.dependOn(&run_runtime_bitmap_loader_tests.step);",
    "phase9_runtime_bitmap.dependOn(&run_runtime_bitmap_direct_init_contract_tests.step);",
    "phase9_runtime_bitmap.dependOn(&run_runtime_bitmap_cold_stage_guard_tests.step);",
};

const markers_8 = [_][]const u8{
    "pub const PreparedRequest = struct {",
    "pub fn keepsAllocatorInitFlowConsistent(",
    "pub fn prepareRequest(plan: LoadPlan) !PreparedRequest {",
    "test \"prepareRequest enforces the bounded runtime loader contract\"",
    "test \"PreparedRequest.requestRuntimeLoad preserves the prepared snapshot on drift\"",
    "test \"releaseWithoutSubstrate preserves the waiting snapshot on drift\"",
};

const markers_9 = [_][]const u8{
    "test \"LoadPlan keeps blocked publication outputs and install-root surfaces out of the shared request contract\"",
    "\"modinfo\"",
    "\"module_alias\"",
    "\"modules_alias_path\"",
    "\"module_install_root\"",
    "\"modules_order_path\"",
    "\"modules_builtin_path\"",
    "\"module_symvers_path\"",
    "\"depmod_script\"",
    "\"depmod_manifest\"",
};

const markers_10 = [_][]const u8{
    "test \"shared runtime loader keeps initialized-stage bitmap and kretprobe request shape aligned\"",
    "test \"shared runtime loader keeps selftest-complete trace-events and atomic64 request shape aligned\"",
    "test \"shared runtime loader keeps rejected release-order transitions fail-closed across loader families\"",
};

const contracts = [_]FileContract{
    .{ .rel = "Documentation/zigux/README.md", .markers = &markers_0 },
    .{ .rel = "Documentation/zigux/phase9-runtime-bitmap-survey.md", .markers = &markers_1 },
    .{ .rel = "Documentation/zigux/review-checklist.md", .markers = &markers_2 },
    .{ .rel = "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md", .markers = &markers_3 },
    .{ .rel = "samples/zigux/README.md", .markers = &markers_4 },
    .{ .rel = "scripts/zigux/README.md", .markers = &markers_5 },
    .{ .rel = "zigux/tests/README.md", .markers = &markers_6 },
    .{ .rel = "zigux/tests/phase9_build.zig", .markers = &markers_7 },
    .{ .rel = "zigux/kernel/runtime_loader.zig", .markers = &markers_8 },
    .{ .rel = "zigux/kernel/runtime_loader_contract.zig", .markers = &markers_9 },
    .{ .rel = "zigux/tests/runtime_loader_allocator_init_flow.zig", .markers = &markers_10 },
};

const exact_markers_0 = [_][]const u8{
    "- `scripts\\zigux/validate_phase9.zig`, `scripts\\zigux/check_phase9_review_checklist_phase_boundaries.zig`, `scripts\\zigux/check_phase9_freeze_map_study_boundaries.zig`, `scripts\\zigux/check_phase9_trace_events_runtime_packet.zig`, `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/README.md`, `samples/zigux/README.md`, and `zigux/tests/README.md` keep the shipped shared Phase 9 reminder packet explicit from the scripts root",
};

const exact_contracts = [_]FileContract{
    .{ .rel = "scripts/zigux/README.md", .markers = &exact_markers_0 },
};

const forbidden_markers_0 = [_][]const u8{
    "blocked publication, install-root, or module-metadata boundaries are already solved",
};

const forbidden_markers_1 = [_][]const u8{
    "full publication completion",
};

const forbidden_contracts = [_]FileContract{
    .{ .rel = "Documentation/zigux/README.md", .markers = &forbidden_markers_0 },
    .{ .rel = "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md", .markers = &forbidden_markers_1 },
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for (contracts) |contract| {
        const file_path = try guard.joinPath(allocator, root, contract.rel);
        defer allocator.free(file_path);
        const text = try guard.readUtf8File(io, allocator, file_path);
        defer allocator.free(text);
        for (contract.markers) |marker| {
            guard.requireMarker(text, marker) catch |err| {
                try guard.printLine(io, "PHASE9_BUILD_ONLY_MISSING_MARKER_FILE={s}", .{contract.rel});
                try guard.printLine(io, "PHASE9_BUILD_ONLY_MISSING_MARKER_VALUE={s}", .{marker});
                return err;
            };
        }
    }
    for (exact_contracts) |contract| {
        const file_path = try guard.joinPath(allocator, root, contract.rel);
        defer allocator.free(file_path);
        const text = try guard.readUtf8File(io, allocator, file_path);
        defer allocator.free(text);
        for (contract.markers) |marker| try guard.requireExactLineCount(text, marker, 1);
    }
    for (forbidden_contracts) |contract| {
        const file_path = try guard.joinPath(allocator, root, contract.rel);
        defer allocator.free(file_path);
        const text = try guard.readUtf8File(io, allocator, file_path);
        defer allocator.free(text);
        for (contract.markers) |marker| try std.testing.expect(std.mem.indexOf(u8, text, marker) == null);
    }
}

fn emitCounts(io: Io) !void {
    try guard.printLine(io, "PHASE9_BUILD_ONLY_SURFACE_FILE_COUNT=11", .{});
    try guard.printLine(io, "PHASE9_BUILD_ONLY_SURFACE_MARKER_COUNT=100", .{});
    try guard.printLine(io, "PHASE9_BUILD_ONLY_SURFACE_EXACT_ONCE_MARKER_COUNT=1", .{});
    try guard.printLine(io, "PHASE9_BUILD_ONLY_SURFACE_FORBIDDEN_MARKER_COUNT=2", .{});
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    try checkRepo(io, allocator, root);
    try std.testing.expectEqual(@as(usize, 100), comptime blk: {
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
    try guard.printLine(io, "PHASE9_BUILD_ONLY_SURFACE_ROOT={s}", .{root});
    try guard.printLine(io, "PHASE9_BUILD_ONLY_SURFACE_FILES_CHECKED=11", .{});
    try emitCounts(io);
}

// Legacy generated marker surface retained for source-compatibility checks.
// const std = @import("std");
// const Io = std.Io;
// const guard = @import("zigux_guard.zig");
//
// pub const pass_marker = "PHASE9_BUILD_ONLY_SURFACE_SELF_TEST=pass";
//
// const REQUIRED_MARKERS = [_][]const u8{
//     "keep the returned shared runtime-loader allocator/init-flow and command/environment boundary packet explicit as neighboring shared-owner evidence through `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`",
//     "`zigux/tests/runtime_loader_allocator_init_flow.zig`",
//     "`zigux/kernel/runtime_loader.zig`",
//     "`zigux/kernel/runtime_loader_contract.zig`",
//     "the bounded `zigux/tests/phase9_build.zig` `phase9-runtime-loader-shared-tests` and `phase9-runtime-loader-command-env-boundary-guard-tests` shards",
//     "`samples/zigux/runtime_bitmap_cold_stage_guard.zig`",
//     "the runtime bitmap sample, cold-stage guard, survey, module, diff, loader, and top-bit companion packet members",
//     "`phase9-runtime-bitmap-cold-stage-guard-tests` plus the aggregate `phase9-runtime-bitmap-tests` handle",
//     "`samples/zigux/runtime_bitmap_direct_init_contract.zig`",
//     "Keep the direct-init companion explicit when reminder text summarizes sample-local init normalization, unsorted duplicate input collapse, nth-set ordering, and formatted sparse-summary stability.",
//     "`samples/zigux/runtime_bitmap_cold_stage_guard.zig`",
//     "Keep `samples/zigux/runtime_bitmap_cold_stage_guard.zig` explicit as the returned cold-stage sample-root guard companion;",
//     "`phase9-runtime-bitmap-cold-stage-guard-tests`",
//     "`phase9-runtime-bitmap-tests`",
//     "if the change touches the shared Phase 9 runtime-pilot packet",
//     "`Documentation/zigux/phase9-runtime-loader-gap-survey.md`",
//     "`zigux/tests/runtime_loader_gap_survey.zig`",
//     "`zigux/tests/runtime_loader_allocator_init_flow.zig`",
//     "`zigux/kernel/runtime_loader.zig`",
//     "`zigux/kernel/runtime_loader_contract.zig`",
//     "`samples/zigux/runtime_*_loader.zig`",
//     "the returned shared runtime-loader allocator/init-flow packet remains neighboring shared-owner evidence",
//     "The shared runtime-loader allocator/init-flow and command/environment boundary packet survives as a narrower shared-owner surface",
//     "Trusted GitHub rereads on 2026-05-25 directly recover the still-live shared loader packet through `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`, the still-returned `samples/zigux/runtime_bitmap_loader.zig` scaffold, and the bounded `zigux/tests/phase9_build.zig` shard.",
//     "`zigux/tests/phase9_build.zig` still exposes `phase9-runtime-loader-allocator-init-flow-tests`, `phase9-runtime-loader-shared-tests`, `phase9-runtime-loader-command-env-boundary-guard-tests`, and `phase9-runtime-trace-events-loader-substrate-drift-tests`",
//     "`phase9-runtime-loader-command-env-boundary-guard-tests`",
//     "`samples/zigux/runtime_bitmap_cold_stage_guard.zig`",
//     "`zigux/tests/phase9_build.zig` keeps the returned bitmap packet inside the shared rerun bundle through `phase9-runtime-bitmap-tests` plus the dedicated `phase9-runtime-bitmap-cold-stage-guard-tests` route",
//     "`scripts/zigux/README.md` now again carries a dedicated shared Phase 9 reminder section on current `master`, so keep counting it as active same-lane evidence beside the aligned docs-root and tests-root packet",
//     "keep the Phase 8 command and environment ownership boundary explicit: deferred `command_name`, exec-path, `PERF_EXEC_PATH`, and `PATH` cues stay with `tools/lib/subcmd/exec-cmd.zig`, while `LINES` and `COLUMNS` stay with `tools/lib/subcmd/help.zig`",
//     "current Phase 9 material still does not prove shipped runtime command or environment activation control; it proves only that the shared runtime-loader packet keeps those Phase 8 control surfaces out of the loader contract",
//     "`samples/zigux/runtime_bitmap_cold_stage_guard.zig`",
//     "Keep `samples/zigux/runtime_bitmap_cold_stage_guard.zig` explicit as the returned cold-stage selftest, exit, mutation, and source-lifecycle guard companion proof for the same runtime bitmap starter.",
//     "`zigux/tests/runtime_bitmap_module.zig`",
//     "`zigux/tests/runtime_bitmap_diff.zig`",
//     "- `scripts\zigux/validate_phase9.zig`, `scripts/zigux/check_phase9_review_checklist_phase_boundaries.zig`, `scripts/zigux/check_phase9_freeze_map_study_boundaries.zig`, `scripts/zigux/check_phase9_trace_events_runtime_packet.zig`, `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/README.md`, `samples/zigux/README.md`, and `zigux/tests/README.md` keep the shipped shared Phase 9 reminder packet explicit from the scripts root",
//     "zig run validate_phase9.zig --self-test",
//     "zig run validate_phase9.zig",
//     "`zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`, the bounded `zigux/tests/phase9_build.zig` `phase9-runtime-loader-shared-tests` and `phase9-runtime-loader-command-env-boundary-guard-tests` shards, and the separate returned `samples/zigux/runtime_bitmap_loader.zig` scaffold keep the narrower shared runtime-loader allocator/init-flow and command/environment boundary packet explicit beside the still-blocked module-metadata and install-root surfaces",
//     "keep `Documentation/zigux/phase9-runtime-loader-gap-survey.md`, `zigux/tests/runtime_loader_gap_manifest.json`, `zigux/tests/runtime_loader_gap_survey.zig`, and `samples/zigux/runtime_trace_events_loader.zig` framed as historical wider-family vocabulary until trusted direct rereads return them",
//     "`samples/zigux/runtime_bitmap_cold_stage_guard.zig`",
//     "keep the bounded runtime bitmap reminder packet distinct from that returned loader shard too",
//     "keep the bounded Phase 9 build bundle explicit as rerun vocabulary only",
//     "first-loadable parity-behavior handle",
//     "const runtime_loader_allocator_init_flow_module = b.createModule(.{",
//     ".root_source_file = b.path(\"runtime_loader_allocator_init_flow.zig\"),",
//     "const runtime_loader_allocator_init_flow_tests = b.addTest(.{",
//     "\"phase9-runtime-loader-allocator-init-flow-tests\",",
//     "const phase9_runtime_loader_kernel = b.step(",
//     "\"phase9-runtime-loader-kernel-tests\",",
//     "phase9_runtime_loader_kernel.dependOn(&run_runtime_loader_kernel_tests.step);",
//     "const phase9_runtime_loader_contract = b.step(",
//     "\"phase9-runtime-loader-contract-tests\",",
//     "phase9_runtime_loader_contract.dependOn(&run_runtime_loader_contract_tests.step);",
//     "const runtime_loader_command_env_boundary_guard_module = b.createModule(.{",
//     ".root_source_file = b.path(\"../kernel/runtime_loader_command_env_boundary_guard.zig\"),",
//     "const runtime_loader_command_env_boundary_guard_tests = b.addTest(.{",
//     "\"phase9-runtime-loader-command-env-boundary-guard-tests\",",
//     "const runtime_bitmap_direct_init_contract_module = b.createModule(.{",
//     ".root_source_file = b.path(\"../../samples/zigux/runtime_bitmap_direct_init_contract.zig\"),",
//     "const runtime_bitmap_direct_init_contract_tests = b.addTest(.{",
//     "\"phase9-runtime-bitmap-direct-init-contract-tests\",",
//     "const runtime_bitmap_cold_stage_guard_module = b.createModule(.{",
//     ".root_source_file = b.path(\"../../samples/zigux/runtime_bitmap_cold_stage_guard.zig\"),",
//     "const runtime_bitmap_cold_stage_guard_tests = b.addTest(.{",
//     "\"phase9-runtime-bitmap-cold-stage-guard-tests\",",
//     "const phase9_runtime_bitmap_direct_init_contract = b.step(",
//     "phase9_runtime_bitmap_direct_init_contract.dependOn(",
//     "const phase9_runtime_bitmap_cold_stage_guard = b.step(",
//     "phase9_runtime_bitmap_cold_stage_guard.dependOn(",
//     "const phase9_runtime_loader_command_env_boundary_guard = b.step(",
//     "phase9_runtime_loader_command_env_boundary_guard.dependOn(n        &run_runtime_loader_command_env_boundary_guard_tests.step,n    );",
//     "const phase9_runtime_loader_shared = b.step(",
//     "\"phase9-runtime-loader-shared-tests\",",
//     "phase9_runtime_loader_shared.dependOn(&run_runtime_loader_kernel_tests.step);",
//     "phase9_runtime_loader_shared.dependOn(&run_runtime_loader_contract_tests.step);",
//     "phase9_runtime_loader_shared.dependOn(&run_runtime_loader_allocator_init_flow_tests.step);",
//     "phase9_runtime_loader_shared.dependOn(n        &run_runtime_loader_command_env_boundary_guard_tests.step,n    );",
//     "phase9_runtime_loader_shared.dependOn(&run_runtime_bitmap_loader_tests.step);",
//     "phase9_runtime_bitmap.dependOn(&run_runtime_bitmap_direct_init_contract_tests.step);",
//     "phase9_runtime_bitmap.dependOn(&run_runtime_bitmap_cold_stage_guard_tests.step);",
//     "pub const PreparedRequest = struct {",
//     "pub fn keepsAllocatorInitFlowConsistent(",
//     "pub fn prepareRequest(plan: LoadPlan) !PreparedRequest {",
//     "test \"prepareRequest enforces the bounded runtime loader contract\"",
//     "test \"PreparedRequest.requestRuntimeLoad preserves the prepared snapshot on drift\"",
//     "test \"releaseWithoutSubstrate preserves the waiting snapshot on drift\"",
//     "test \"LoadPlan keeps blocked publication outputs and install-root surfaces out of the shared request contract\"",
//     "\"modinfo\"",
//     "\"module_alias\"",
//     "\"modules_alias_path\"",
//     "\"module_install_root\"",
//     "\"modules_order_path\"",
//     "\"modules_builtin_path\"",
//     "\"module_symvers_path\"",
//     "\"depmod_script\"",
//     "\"depmod_manifest\"",
//     "test \"shared runtime loader keeps initialized-stage bitmap and kretprobe request shape aligned\"",
//     "test \"shared runtime loader keeps selftest-complete trace-events and atomic64 request shape aligned\"",
//     "test \"shared runtime loader keeps rejected release-order transitions fail-closed across loader families\"",
// };
//
// const FORBIDDEN_MARKERS = [_][]const u8{
//     "blocked publication, install-root, or module-metadata boundaries are already solved",
//     "full publication completion",
// };
//
// const EXACT_ONCE_MARKERS = [_][]const u8{
//     "- `scripts\zigux/validate_phase9.zig`, `scripts/zigux/check_phase9_review_checklist_phase_boundaries.zig`, `scripts/zigux/check_phase9_freeze_map_study_boundaries.zig`, `scripts/zigux/check_phase9_trace_events_runtime_packet.zig`, `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/README.md`, `samples/zigux/README.md`, and `zigux/tests/README.md` keep the shipped shared Phase 9 reminder packet explicit from the scripts root",
// };
//
// const DOCS_README_PATH = [_][]const u8{
//     "Documentation/zigux/README.md",
// };
//
// const PHASE9_BITMAP_SURVEY_PATH = [_][]const u8{
//     "Documentation/zigux/phase9-runtime-bitmap-survey.md",
// };
//
// const REVIEW_CHECKLIST_PATH = [_][]const u8{
//     "Documentation/zigux/review-checklist.md",
// };
//
// const LANE_SEQUENCING_PATH = [_][]const u8{
//     "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md",
// };
//
// const SAMPLES_README_PATH = [_][]const u8{
//     "samples/zigux/README.md",
// };
//
// const SCRIPTS_README_PATH = [_][]const u8{
//     "scripts/zigux/README.md",
// };
//
// const TESTS_README_PATH = [_][]const u8{
//     "zigux/tests/README.md",
// };
//
// const PHASE9_BUILD_PATH = [_][]const u8{
//     "zigux/tests/phase9_build.zig",
// };
//
// const RUNTIME_LOADER_PATH = [_][]const u8{
//     "zigux/kernel/runtime_loader.zig",
// };
//
// const RUNTIME_LOADER_CONTRACT_PATH = [_][]const u8{
//     "zigux/kernel/runtime_loader_contract.zig",
// };
//
// const RUNTIME_LOADER_ALLOCATOR_INIT_FLOW_PATH = [_][]const u8{
//     "zigux/tests/runtime_loader_allocator_init_flow.zig",
// };
//
// pub fn checkText(text: []const u8) guard.GuardError!void {
//     for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (EXACT_ONCE_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (DOCS_README_PATH) |marker| try guard.requireMarker(text, marker);
//     for (PHASE9_BITMAP_SURVEY_PATH) |marker| try guard.requireMarker(text, marker);
//     for (REVIEW_CHECKLIST_PATH) |marker| try guard.requireMarker(text, marker);
//     for (LANE_SEQUENCING_PATH) |marker| try guard.requireMarker(text, marker);
//     for (SAMPLES_README_PATH) |marker| try guard.requireMarker(text, marker);
//     for (SCRIPTS_README_PATH) |marker| try guard.requireMarker(text, marker);
//     for (TESTS_README_PATH) |marker| try guard.requireMarker(text, marker);
//     for (PHASE9_BUILD_PATH) |marker| try guard.requireMarker(text, marker);
//     for (RUNTIME_LOADER_PATH) |marker| try guard.requireMarker(text, marker);
//     for (RUNTIME_LOADER_CONTRACT_PATH) |marker| try guard.requireMarker(text, marker);
//     for (RUNTIME_LOADER_ALLOCATOR_INIT_FLOW_PATH) |marker| try guard.requireMarker(text, marker);
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
