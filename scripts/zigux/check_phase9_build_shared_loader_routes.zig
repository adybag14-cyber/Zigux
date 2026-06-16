const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE9_BUILD_SHARED_LOADER_ROUTES_SELF_TEST=pass";

const REQUIRED_MARKERS = [_][]const u8{
    "const runtime_loader_kernel_tests = b.addTest(.{",
    "        .name = \"phase9-runtime-loader-kernel-tests\",",
    "const runtime_loader_allocator_init_flow_tests = b.addTest(.{",
    "        .name = \"phase9-runtime-loader-allocator-init-flow-tests\",",
    "const runtime_loader_contract_tests = b.addTest(.{",
    "        .name = \"phase9-runtime-loader-contract-tests\",",
    "const runtime_loader_command_env_boundary_guard_tests = b.addTest(.{",
    "        .name = \"phase9-runtime-loader-command-env-boundary-guard-tests\",",
    "const runtime_trace_events_loader_substrate_drift_tests = b.addTest(.{",
    "        .name = \"phase9-runtime-trace-events-loader-substrate-drift-tests\",",
    "const runtime_kretprobe_loader_tests = b.addTest(.{",
    "        .name = \"phase9-runtime-kretprobe-loader-tests\",",
    "    const run_runtime_loader_kernel_tests = b.addRunArtifact(runtime_loader_kernel_tests);",
    "    const run_runtime_loader_allocator_init_flow_tests = b.addRunArtifact(",
    "        runtime_loader_allocator_init_flow_tests,",
    "    const run_runtime_loader_contract_tests = b.addRunArtifact(runtime_loader_contract_tests);",
    "    const run_runtime_kretprobe_loader_tests = b.addRunArtifact(",
    "        runtime_kretprobe_loader_tests,",
    "const phase9_runtime_loader_kernel = b.step(",
    "        \"phase9-runtime-loader-kernel-tests\",",
    "    phase9_runtime_loader_kernel.dependOn(&run_runtime_loader_kernel_tests.step);",
    "    const phase9_runtime_loader_contract = b.step(",
    "        \"phase9-runtime-loader-contract-tests\",",
    "    phase9_runtime_loader_contract.dependOn(&run_runtime_loader_contract_tests.step);",
    "const phase9_runtime_loader_shared = b.step(",
    "        \"phase9-runtime-loader-shared-tests\",",
    "    phase9_runtime_loader_shared.dependOn(&run_runtime_loader_kernel_tests.step);",
    "    phase9_runtime_loader_shared.dependOn(&run_runtime_loader_allocator_init_flow_tests.step);",
    "    phase9_runtime_loader_shared.dependOn(&run_runtime_loader_contract_tests.step);",
    "    phase9_runtime_loader_shared.dependOn(",
    "        &run_runtime_loader_command_env_boundary_guard_tests.step,",
    "        &run_runtime_trace_events_loader_substrate_drift_tests.step,",
    "    phase9_runtime_loader_shared.dependOn(&run_runtime_bitmap_loader_tests.step);",
    "    phase9_runtime_loader_shared.dependOn(&run_runtime_kretprobe_loader_tests.step);",
    "    const phase9_first_loadable_runtime_module_parity = b.step(",
    "        \"phase9-first-loadable-runtime-module-parity-survey-tests\",",
};

const EXACT_ONCE_MARKERS = [_][]const u8{
    "        .name = \"phase9-runtime-loader-kernel-tests\",",
    "        .name = \"phase9-runtime-loader-allocator-init-flow-tests\",",
    "        .name = \"phase9-runtime-loader-contract-tests\",",
    "        .name = \"phase9-runtime-loader-command-env-boundary-guard-tests\",",
    "        .name = \"phase9-runtime-trace-events-loader-substrate-drift-tests\",",
    "        .name = \"phase9-runtime-kretprobe-loader-tests\",",
    "    const run_runtime_loader_allocator_init_flow_tests = b.addRunArtifact(",
    "        runtime_loader_allocator_init_flow_tests,",
    "    const run_runtime_kretprobe_loader_tests = b.addRunArtifact(",
    "        runtime_kretprobe_loader_tests,",
    "        \"phase9-runtime-loader-kernel-tests\",",
    "        \"phase9-runtime-loader-contract-tests\",",
    "        \"phase9-runtime-loader-shared-tests\",",
    "        \"phase9-first-loadable-runtime-module-parity-survey-tests\",",
};

const PHASE9_BUILD_PATH = [_][]const u8{
    "zigux/tests/phase9_build.zig",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (EXACT_ONCE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (PHASE9_BUILD_PATH) |marker| try guard.requireMarker(text, marker);
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
