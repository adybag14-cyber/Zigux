const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE12_VIRTIO_NET_THROUGHPUT_ANCHOR_SELF_TEST=pass";

const REQUIRED_FILES = [_][]const u8{
    "Documentation/zigux/phase12-virtio-net-survey.md",
    "drivers/net/virtio_net_throughput_parity.zig",
    "zigux/tests/phase12_virtio_net_throughput_parity.zig",
    "zigux/tests/phase12_virtio_net_manifest.json",
    "zigux/tests/phase12_build.zig",
    "zigux/tests/build.zig",
    ".github/workflows/zigux-bootstrap.yml",
};

const SURVEY_MARKERS = [_][]const u8{
    "`PHASE12_STATUS=split-helper-packet-present-shared-build-sextet-throughput-review-only`",
    "drivers/net/virtio_net_throughput_parity.zig",
    "throughput helper remains review-only throughput-ratio checks",
    "explicit receive-refill and transmit-recycle readiness booleans",
};

const MANIFEST_MARKERS = [_][]const u8{
    "\"status\": \"throughput_parity_helper_present_review_only_runtime_completion_missing\"",
    "review-only throughput-ratio checks",
    "explicit receive-refill and transmit-recycle readiness booleans",
    "Measured transport throughput evidence",
};

const PHASE12_BUILD_MARKERS = [_][]const u8{
    "../../drivers/net/virtio_net_throughput_parity.zig",
    "\"phase12_virtio_net_throughput_parity.zig\"",
    "\"phase12-virtio-net-throughput-parity-tests\"",
    "smoke_step.dependOn(&run_virtio_net_throughput_parity_tests.step);",
    "test_step.dependOn(&run_virtio_net_throughput_parity_tests.step);",
};

const SHARED_BUILD_MARKERS = [_][]const u8{
    "../../drivers/net/virtio_net_throughput_parity.zig",
    "\"phase12_virtio_net_throughput_parity.zig\"",
    "\"phase12-virtio-net-throughput-parity\"",
    "const phase12_virtio_net_throughput_parity = addPhase12VirtioNetThroughputParity(",
    "phase12_step.dependOn(&phase12_virtio_net_throughput_parity.step);",
    "phase12_throughput_step.dependOn(&phase12_virtio_net_throughput_parity.step);",
};

const WORKFLOW_MARKERS = [_][]const u8{
    "- name: Run current Phase 12 throughput-parity anchor",
    "run: zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/build.zig",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_FILES) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MANIFEST_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (PHASE12_BUILD_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SHARED_BUILD_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (WORKFLOW_MARKERS) |marker| try guard.requireMarker(text, marker);
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
