const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "{CHECK_NAME}_SELF_TEST=pass";

const REQUIRED_FILES = [_][]const u8{
    "DRIVER_PATH",
    "TEST_PATH",
    "BUILD_PATH",
    "INVENTORY_PATH",
    "DOC_PATH",
    "WORKFLOW_PATH",
};

const REQUIRED_MARKERS = [_][]const u8{
    "pub const ThroughputParityStatus = enum {",
    "pub fn summarizeThroughputParity(request: ThroughputParityRequest) !ThroughputParitySummary {",
    "expected_min_ratio_pct: u8 = 90,",
    "test \"summarizeThroughputParity counts preexisting free descriptors toward the stopped-queue wake gate\" {",
    "test \"summarizeThroughputParity rejects out-of-range target ratios\" {",
    "test \"phase12 throughput parity gate counts preexisting free descriptors toward stopped-queue wake readiness\" {",
    "test \"phase12 throughput parity gate keeps queue-restore precedence explicit\" {",
    "ThroughputParityStatus.parity_gate_ready,",
    "ThroughputParityStatus.needs_queue_restore,",
    ".root_source_file = b.path(\"../../drivers/net/virtio_net_throughput_parity.zig\"),",
    ".root_source_file = b.path(\"phase12_virtio_net_throughput_parity.zig\"),",
    ".name = \"phase12-virtio-net-throughput-parity-tests\",",
    "const throughput_parity_step = b.step(",
    "\"phase12-virtio-net-throughput-parity\",",
    "throughput_parity_step.dependOn(&throughput_parity_tests.step);",
    "\"phase12-virtio-net-throughput-parity-tests\"",
    "\"throughput_anchor_depend_steps\": [",
    "\"throughput_parity_tests\"",
    "\"path\": \"../../drivers/net/virtio_net_throughput_parity.zig\"",
    "\"path\": \"phase12_virtio_net_throughput_parity.zig\"",
    "\"step\": \"phase12-virtio-net-throughput-parity\"",
    "- driver shard: `drivers/net/virtio_net_throughput_parity.zig`",
    "- directly coupled replay: `zigux/tests/phase12_virtio_net_throughput_parity.zig`",
    "`make -C zigux phase12-virtio-net-throughput-parity-test`",
    "throughput-parity, and survey-gate sextet through shared `smoke` and shared `test`",
    "- name: Run current Phase 12 throughput-parity anchor",
    "run: zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/phase12_build.zig --summary all",
};

const CHECK_NAME = [_][]const u8{
    "PHASE12_THROUGHPUT_PARITY_PACKET",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_FILES) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (CHECK_NAME) |marker| try guard.requireMarker(text, marker);
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
