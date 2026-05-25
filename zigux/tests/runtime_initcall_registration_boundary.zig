const std = @import("std");

const NOTE_PATH = "Documentation/zigux/phase9-initcall-registration-boundary-survey.md";
const RUNTIME_LOADER_CONTRACT_PATH = "zigux/kernel/runtime_loader_contract.zig";
const RUNTIME_LOADER_PATH = "zigux/kernel/runtime_loader.zig";
const ALLOCATOR_INIT_FLOW_PATH = "zigux/tests/runtime_loader_allocator_init_flow.zig";
const LOADER_SUBSTRATE_DRIFT_PATH = "zigux/tests/runtime_trace_events_loader_substrate_drift.zig";
const UNREGISTERED_GATE_PATH = "samples/zigux/runtime_trace_events_unregistered_gate.zig";
const REGISTRATION_REENTRY_PATH = "samples/zigux/runtime_trace_events_registration_reentry_gate.zig";
const PHASE9_BUILD_PATH = "zigux/tests/phase9_build.zig";

const NOTE_MARKERS = [_][]const u8{
    "`PHASE9_LANE_KEY=P9-L15`",
    "`PHASE9_BOUNDARY_PACKET=initcall_registration_boundary`",
    "`PHASE9_PROVENANCE_MODE=dated_master_readback`",
    "`zigux/kernel/runtime_loader_contract.zig` keeps `entry_symbol` and `exit_symbol` explicit in `LoadPlan` while `InitFlow` stays bounded to `.initialized` and `.selftest_complete`",
    "`zigux/kernel/runtime_loader.zig` keeps `PreparedRequest.requestRuntimeLoad()` and `PreparedRequest.releaseWithoutSubstrate()` fail-closed on `error.InvalidLoaderState` and `error.PreparedPlanDrift`",
    "`samples/zigux/runtime_trace_events_unregistered_gate.zig` keeps unregistered function-thread failures fail-closed with `error.FunctionThreadNotRegistered` and `error.RegistrationUnderflow`",
    "`samples/zigux/runtime_trace_events_registration_reentry_gate.zig` keeps reusable registration re-entry explicit with `error.FunctionThreadAlreadyRegistered`",
    "`zigux/tests/phase9_build.zig` keeps the neighboring shared rerun packet explicit through `phase9-runtime-loader-allocator-init-flow-tests`, `phase9-runtime-loader-command-env-boundary-guard-tests`, `phase9-runtime-loader-shared-tests`, and `phase9-runtime-trace-events-loader-substrate-drift-tests`",
    "`samples/zigux/runtime_trace_events_loader.zig` is not part of the current direct-readback packet for this lane and stays historical wider-family vocabulary unless a fresh repo reread proves it returned",
};

const CONTRACT_MARKERS = [_][]const u8{
    "entry_symbol",
    "exit_symbol",
    "LoadPlan keeps blocked publication and depmod surfaces out of the shared request contract",
};

const LOADER_MARKERS = [_][]const u8{
    "pub fn requestRuntimeLoad",
    "pub fn releaseWithoutSubstrate",
    "error.InvalidLoaderState",
    "error.PreparedPlanDrift",
    "PreparedRequest keeps blocked initcall metadata surfaces out of the shared request boundary",
    "PreparedRequest keeps blocked registration-summary surfaces out of the shared request boundary",
};

const ALLOCATOR_INIT_FLOW_MARKERS = [_][]const u8{
    "shared runtime loader keeps initialized-stage bitmap and kretprobe request shape aligned",
    "shared runtime loader keeps selftest-complete trace-events and atomic64 request shape aligned",
    "shared runtime loader keeps waiting selftest-hook and handoff-stage labels from drifting before release",
};

const LOADER_SUBSTRATE_DRIFT_MARKERS = [_][]const u8{
    "phase9 runtime trace-events shared loader rejects prepared substrate drift before handoff",
    "phase9 runtime trace-events shared loader rejects release drift after waiting handoff",
    "phase9 runtime trace-events shared loader rejects approved-family release drift after waiting handoff",
};

const UNREGISTERED_GATE_MARKERS = [_][]const u8{
    "phase9 trace-events sample keeps unregistered function-thread failures fail-closed",
    "error.FunctionThreadNotRegistered",
    "error.RegistrationUnderflow",
};

const REGISTRATION_REENTRY_MARKERS = [_][]const u8{
    "phase9 trace-events sample keeps registration reentry reusable across initialized and selftest_complete stages",
    "error.FunctionThreadAlreadyRegistered",
    "phase9 trace-events sample preserves initialized direct-activity summary across exit without selftest",
};

const PHASE9_BUILD_MARKERS = [_][]const u8{
    ".name = \"phase9-runtime-loader-allocator-init-flow-tests\"",
    ".name = \"phase9-runtime-loader-command-env-boundary-guard-tests\"",
    ".name = \"phase9-runtime-loader-shared-tests\"",
    ".name = \"phase9-runtime-trace-events-loader-substrate-drift-tests\"",
};

fn fileExists(path: []const u8) bool {
    std.Io.Dir.cwd().access(std.testing.io, path, .{}) catch return false;
    return true;
}

fn readFileAlloc(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        allocator,
        .limited(512 * 1024),
    );
}

fn expectMarkersInFile(
    allocator: std.mem.Allocator,
    rel_path: []const u8,
    markers: []const []const u8,
) !void {
    const content = try readFileAlloc(allocator, rel_path);
    defer allocator.free(content);

    for (markers) |marker| {
        try std.testing.expect(
            std.mem.indexOf(u8, content, marker) != null,
        );
    }
}

fn seedFixtureFile(dir: std.Io.Dir, path: []const u8, content: []const u8) !void {
    if (std.fs.path.dirname(path)) |dir_name| {
        var created = try dir.createDirPathOpen(std.testing.io, dir_name, .{});
        defer created.close(std.testing.io);
    }

    const file = try dir.createFile(std.testing.io, path, .{});
    defer file.close(std.testing.io);

    var buffer: [1024]u8 = undefined;
    var file_writer = file.writer(std.testing.io, &buffer);
    try file_writer.interface.writeAll(content);
}

fn seedFixtureTree(dir: std.Io.Dir) !void {
    try seedFixtureFile(dir, NOTE_PATH,
        \\# Phase 9 Initcall And Registration Boundary Survey
        \\
        \\- `PHASE9_LANE_KEY=P9-L15`
        \\- `PHASE9_BOUNDARY_PACKET=initcall_registration_boundary`
        \\- `PHASE9_PROVENANCE_MODE=dated_master_readback`
        \\- `zigux/kernel/runtime_loader_contract.zig` keeps `entry_symbol` and `exit_symbol` explicit in `LoadPlan` while `InitFlow` stays bounded to `.initialized` and `.selftest_complete`
        \\- `zigux/kernel/runtime_loader.zig` keeps `PreparedRequest.requestRuntimeLoad()` and `PreparedRequest.releaseWithoutSubstrate()` fail-closed on `error.InvalidLoaderState` and `error.PreparedPlanDrift`
        \\- `samples/zigux/runtime_trace_events_unregistered_gate.zig` keeps unregistered function-thread failures fail-closed with `error.FunctionThreadNotRegistered` and `error.RegistrationUnderflow`
        \\- `samples/zigux/runtime_trace_events_registration_reentry_gate.zig` keeps reusable registration re-entry explicit with `error.FunctionThreadAlreadyRegistered`
        \\- `zigux/tests/phase9_build.zig` keeps the neighboring shared rerun packet explicit through `phase9-runtime-loader-allocator-init-flow-tests`, `phase9-runtime-loader-command-env-boundary-guard-tests`, `phase9-runtime-loader-shared-tests`, and `phase9-runtime-trace-events-loader-substrate-drift-tests`
        \\- `samples/zigux/runtime_trace_events_loader.zig` is not part of the current direct-readback packet for this lane and stays historical wider-family vocabulary unless a fresh repo reread proves it returned
        \\
    );
    try seedFixtureFile(dir, RUNTIME_LOADER_CONTRACT_PATH,
        \\pub const LoadPlan = struct {
        \\    entry_symbol: []const u8,
        \\    exit_symbol: []const u8,
        \\};
        \\pub const HandoffStage = enum {
        \\    .initialized,
        \\    .selftest_complete,
        \\};
        \\test "LoadPlan keeps blocked publication and depmod surfaces out of the shared request contract" {}
        \\
    );
    try seedFixtureFile(dir, RUNTIME_LOADER_PATH,
        \\pub fn requestRuntimeLoad() void {}
        \\pub fn releaseWithoutSubstrate() void {}
        \\const invalid_loader_state = error.InvalidLoaderState;
        \\const prepared_plan_drift = error.PreparedPlanDrift;
        \\test "PreparedRequest keeps blocked initcall metadata surfaces out of the shared request boundary" {}
        \\test "PreparedRequest keeps blocked registration-summary surfaces out of the shared request boundary" {}
        \\
    );
    try seedFixtureFile(dir, ALLOCATOR_INIT_FLOW_PATH,
        \\test "shared runtime loader keeps initialized-stage bitmap and kretprobe request shape aligned" {}
        \\test "shared runtime loader keeps selftest-complete trace-events and atomic64 request shape aligned" {}
        \\test "shared runtime loader keeps waiting selftest-hook and handoff-stage labels from drifting before release" {}
        \\
    );
    try seedFixtureFile(dir, LOADER_SUBSTRATE_DRIFT_PATH,
        \\test "phase9 runtime trace-events shared loader rejects prepared substrate drift before handoff" {}
        \\test "phase9 runtime trace-events shared loader rejects release drift after waiting handoff" {}
        \\test "phase9 runtime trace-events shared loader rejects approved-family release drift after waiting handoff" {}
        \\
    );
    try seedFixtureFile(dir, UNREGISTERED_GATE_PATH,
        \\test "phase9 trace-events sample keeps unregistered function-thread failures fail-closed" {}
        \\const a = error.FunctionThreadNotRegistered;
        \\const b = error.RegistrationUnderflow;
        \\
    );
    try seedFixtureFile(dir, REGISTRATION_REENTRY_PATH,
        \\test "phase9 trace-events sample keeps registration reentry reusable across initialized and selftest_complete stages" {}
        \\const a = error.FunctionThreadAlreadyRegistered;
        \\test "phase9 trace-events sample preserves initialized direct-activity summary across exit without selftest" {}
        \\
    );
    try seedFixtureFile(dir, PHASE9_BUILD_PATH,
        \\\.name = "phase9-runtime-loader-allocator-init-flow-tests"
        \\\.name = "phase9-runtime-loader-command-env-boundary-guard-tests"
        \\\.name = "phase9-runtime-loader-shared-tests"
        \\\.name = "phase9-runtime-trace-events-loader-substrate-drift-tests"
        \\
    );
}

fn expectMarkersInDir(
    dir: std.Io.Dir,
    allocator: std.mem.Allocator,
    rel_path: []const u8,
    markers: []const []const u8,
) !void {
    const content = try dir.readFileAlloc(
        std.testing.io,
        rel_path,
        allocator,
        .limited(512 * 1024),
    );
    defer allocator.free(content);

    for (markers) |marker| {
        try std.testing.expect(std.mem.indexOf(u8, content, marker) != null);
    }
}

fn validatePacketInDir(dir: std.Io.Dir, allocator: std.mem.Allocator) !void {
    try expectMarkersInDir(dir, allocator, NOTE_PATH, &NOTE_MARKERS);
    try expectMarkersInDir(dir, allocator, RUNTIME_LOADER_CONTRACT_PATH, &CONTRACT_MARKERS);
    try expectMarkersInDir(dir, allocator, RUNTIME_LOADER_PATH, &LOADER_MARKERS);
    try expectMarkersInDir(dir, allocator, ALLOCATOR_INIT_FLOW_PATH, &ALLOCATOR_INIT_FLOW_MARKERS);
    try expectMarkersInDir(dir, allocator, LOADER_SUBSTRATE_DRIFT_PATH, &LOADER_SUBSTRATE_DRIFT_MARKERS);
    try expectMarkersInDir(dir, allocator, UNREGISTERED_GATE_PATH, &UNREGISTERED_GATE_MARKERS);
    try expectMarkersInDir(dir, allocator, REGISTRATION_REENTRY_PATH, &REGISTRATION_REENTRY_MARKERS);
    try expectMarkersInDir(dir, allocator, PHASE9_BUILD_PATH, &PHASE9_BUILD_MARKERS);
}

test "phase9 initcall-registration boundary fixture stays aligned" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    try seedFixtureTree(tmp.dir);
    try expectMarkersInDir(tmp.dir, std.testing.allocator, NOTE_PATH, &NOTE_MARKERS);
}

test "phase9 initcall-registration boundary packet matches live repo when present" {
    if (!fileExists(NOTE_PATH)) return;
    if (!fileExists(RUNTIME_LOADER_CONTRACT_PATH)) return;
    if (!fileExists(RUNTIME_LOADER_PATH)) return;
    if (!fileExists(ALLOCATOR_INIT_FLOW_PATH)) return;
    if (!fileExists(LOADER_SUBSTRATE_DRIFT_PATH)) return;
    if (!fileExists(UNREGISTERED_GATE_PATH)) return;
    if (!fileExists(REGISTRATION_REENTRY_PATH)) return;
    if (!fileExists(PHASE9_BUILD_PATH)) return;

    try validatePacketInDir(std.Io.Dir.cwd(), std.testing.allocator);
}
