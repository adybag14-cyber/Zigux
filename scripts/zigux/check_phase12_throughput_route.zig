const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE12_THROUGHPUT_ROUTE_SELF_TEST=pass";

const REQUIRED_FILES = [_][]const u8{
    "MAKEFILE_PATH",
    "BUILD_PATH",
    "WORKFLOW_PATH",
};

const REQUIRED_MARKERS = [_][]const u8{
    "phase12-virtio-net-throughput-parity-test:",
    "cd $(ZIGUX_ROOT) && $(ZIG) build phase12-virtio-net-throughput-parity --build-file zigux/tests/phase12_build.zig --summary all",
    "\"phase12_virtio_net_throughput_parity.zig\"",
    "\"phase12-virtio-net-throughput-parity-tests\"",
    "\"phase12-virtio-net-throughput-parity\"",
    "smoke_step.dependOn(&run_virtio_net_throughput_parity_tests.step);",
    "test_step.dependOn(&run_virtio_net_throughput_parity_tests.step);",
    "throughput_parity_step.dependOn(&run_virtio_net_throughput_parity_tests.step);",
    "throughput-parity, and survey-gate smoke tests",
    "throughput-parity, and survey-gate tests",
    "throughput-parity replay in isolation",
    "- name: Run current Phase 12 throughput-parity anchor",
    "run: zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/build.zig",
    "- name: Run current Phase 12 aggregate route",
    "run: make -C zigux phase12",
};

const FORBIDDEN_MARKERS = [_][]const u8{
    "\"phase12_virtio_net.zig\"",
    "\"phase12_virtio_net_syntax_lab.zig\"",
    "\"phase12-virtio-net-tests\"",
    "\"phase12-virtio-net-syntax-lab-tests\"",
};

const MAKEFILE_PATH = [_][]const u8{
    "zigux/Makefile",
};

const BUILD_PATH = [_][]const u8{
    "zigux/tests/phase12_build.zig",
};

const WORKFLOW_PATH = [_][]const u8{
    ".github/workflows/zigux-bootstrap.yml",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_FILES) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MAKEFILE_PATH) |marker| try guard.requireMarker(text, marker);
    for (BUILD_PATH) |marker| try guard.requireMarker(text, marker);
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
