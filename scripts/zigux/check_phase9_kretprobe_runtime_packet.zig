const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE9_KRETPROBE_RUNTIME_PACKET_SELF_TEST=pass";

const REQUIRED_FILES = [_][]const u8{
    "OWNERSHIP_MAP_PATH",
    "SAMPLE_PATH",
    "LOADER_PATH",
    "INITIALIZED_SNAPSHOT_GUARD_PATH",
    "REGISTRATION_REENTRY_GATE_PATH",
    "REINIT_REEXIT_GUARD_PATH",
    "SURVEY_PATH",
    "MODULE_PATH",
    "BUILD_PATH",
};

const FILE_MARKERS = [_][]const u8{
    "## Runtime Kretprobe Family Owner",
    "`samples/zigux/runtime_kretprobe.zig`",
    "`samples/zigux/runtime_kretprobe_loader.zig`",
    "`samples/zigux/runtime_kretprobe_initialized_snapshot_guard.zig`",
    "`samples/zigux/runtime_kretprobe_registration_reentry_gate.zig`",
    "`samples/zigux/runtime_kretprobe_reinit_reexit_guard.zig`",
    "`zigux/tests/runtime_kretprobe_survey.zig`",
    "`zigux/tests/runtime_kretprobe_module.zig`",
    "`zigux/tests/runtime_first_loadable_parity_behavior.zig`",
    "`scripts/zigux/check_phase9_kretprobe_runtime_packet.zig`",
    "bounded `phase9-runtime-kretprobe-sample-tests`",
    "bounded `phase9-runtime-kretprobe-loader-tests`",
    "bounded `phase9-runtime-kretprobe-initialized-snapshot-guard-tests`",
    "bounded `phase9-runtime-kretprobe-registration-reentry-gate-tests`",
    "bounded `phase9-runtime-kretprobe-reinit-reexit-guard-tests`",
    "bounded `phase9-runtime-kretprobe-survey-tests`",
    "bounded `phase9-runtime-kretprobe-module-tests`",
    "bounded `phase9-runtime-kretprobe-tests`",
    "bounded `phase9-first-loadable-runtime-module-parity-behavior-tests`",
    ".name = \"runtime_kretprobe\"",
    ".anchor = \"samples/kprobes/kretprobe_example.c\"",
    ".requires_runtime_substrate = true",
    ".provides_selftest_hook = true",
    "pub fn runSelftest(self: *Self) !SelftestSummary {",
    "pub fn exit(self: *Self) !void {",
    "test \"runtime kretprobe sample keeps selftest hook and return replay explicit\" {",
    "const runtime_loader = @import(\"runtime_loader\");",
    "pub const LoaderStage = enum(u8) {",
    "pub fn requestSharedRuntimeLoad(",
    "pub fn releaseSharedWithoutSubstrate(",
    "released_without_substrate",
    "waiting_on_runtime_substrate",
    "error.InvalidLoaderState",
    "test \"runtime kretprobe loader keeps initialized-stage shared contract plans explicit\" {",
    "test \"runtime kretprobe loader keeps initialized shared-request snapshots stable across later selftest activity\" {",
    "const RuntimeKretprobeSample = kretprobe.RuntimeKretprobeSample;",
    "test \"phase9 kretprobe sample keeps captured initialized snapshot replay explicit across later selftest and exit\" {",
    "test \"phase9 kretprobe sample keeps captured initialized direct-activity snapshot replay explicit across later selftest and exit\" {",
    "const RuntimeKretprobeSample = runtime_kretprobe_sample.RuntimeKretprobeSample;",
    "test \"runtime kretprobe registration reentry stays reusable before selftest\" {",
    "test \"runtime kretprobe registration reentry stays reusable after selftest\" {",
    "test \"runtime kretprobe registration reentry stays fail-closed after exit\" {",
    "const RuntimeKretprobeSample = kretprobe.RuntimeKretprobeSample;",
    "test \"phase9 kretprobe sample keeps paired rejected re-init and re-exit rollback explicit after initialized direct activity\" {",
    "test \"phase9 kretprobe sample keeps paired rejected re-init and re-exit rollback explicit after selftest-ready replay\" {",
    "test \"phase9 runtime kretprobe survey gate matches the roadmap-backed sample and module packet\" {",
    "try std.testing.expectEqualStrings(\"runtime_kretprobe\", descriptor.name);",
    "try std.testing.expectEqualStrings(\"samples/kprobes/kretprobe_example.c\", descriptor.anchor);",
    "try expectContains(phase9_build, \"\\\"phase9-runtime-kretprobe-tests\\\"\");",
    "phase9-first-loadable-runtime-module-parity-behavior-tests",
    "test \"phase9 runtime kretprobe survey keeps captured initialized snapshot replay explicit across later selftest and exit\" {",
    "test \"runtime kretprobe sample advertises the bounded pilot-module contract\" {",
    "test \"runtime kretprobe sample keeps selftest summary replay explicit at the module boundary\" {",
    "test \"runtime kretprobe sample keeps lifecycle snapshot replay explicit at the module boundary\" {",
    "test \"runtime kretprobe sample keeps initialized-stage exit replay explicit at the module boundary\" {",
    "test \"runtime kretprobe sample keeps rejected re-selftest rollback explicit at the module boundary\" {",
    "test \"runtime kretprobe sample keeps duplicate registration and failed exit rollback explicit at the module boundary\" {",
    ".name = \"phase9-runtime-kretprobe-sample-tests\"",
    ".name = \"phase9-runtime-kretprobe-loader-tests\"",
    ".name = \"phase9-runtime-kretprobe-initialized-snapshot-guard-tests\"",
    ".name = \"phase9-runtime-kretprobe-registration-reentry-gate-tests\"",
    ".name = \"phase9-runtime-kretprobe-reinit-reexit-guard-tests\"",
    ".name = \"phase9-runtime-kretprobe-survey-tests\"",
    ".name = \"phase9-runtime-kretprobe-module-tests\"",
    "\"phase9-runtime-kretprobe-tests\",",
    "\"Run the Phase 9 runtime kretprobe sample, loader, initialized-snapshot guard, registration-reentry gate, reinit-reexit guard, survey, and module lifecycle tests.\",",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_FILES) |marker| try guard.requireMarker(text, marker);
    for (FILE_MARKERS) |marker| try guard.requireMarker(text, marker);
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
