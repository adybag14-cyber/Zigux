const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE12_VIRTIO_NET_THROUGHPUT_PARITY_PACKET_SELF_TEST=pass";

const REQUIRED_FILES = [_][]const u8{
    "DOC_PATH",
    "DRIVER_PATH",
    "TEST_PATH",
    "MANIFEST_PATH",
    "BUILD_PATH",
    "MAKEFILE_PATH",
    "WORKFLOW_PATH",
    "CHECKER_PATH",
};

const DOC_MARKERS = [_][]const u8{
    "This note records one bounded Validation and Perf packet for the current Phase 12 `virtio_net` throughput-parity replay.",
    "`drivers/net/virtio_net_throughput_parity.zig`",
    "`zigux/tests/phase12_virtio_net_throughput_parity.zig`",
    "`zigux/tests/fixtures/phase12_virtio_net_throughput_parity_manifest.json`",
    "`scripts/zigux/check_phase12_virtio_net_throughput_parity_packet.zig`",
    "`zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/phase12_build.zig --summary all`",
    "`make -C zigux phase12-virtio-net-throughput-parity-test`",
    "It does not claim live transport execution, measured wire throughput, DMA-safe receive ownership, or interrupt-backed completion evidence.",
};

const DRIVER_MARKERS = [_][]const u8{
    "pub const ThroughputParityStatus = enum {",
    "needs_post_reset_probe_replay,",
    "pub const ThroughputParitySummary = struct {",
    "receive_refill_ready: bool,",
    "transmit_recycle_ready: bool,",
    "throughput_ratio_pct: u8,",
    "pub fn summarizeThroughputParity(request: ThroughputParityRequest) !ThroughputParitySummary {",
    "test \"summarizeThroughputParity keeps post reset replay explicit after receive refill when transmit never stopped\" {",
};

const TEST_MARKERS = [_][]const u8{
    "test \"phase12 throughput parity gate counts preexisting free descriptors toward stopped-queue wake readiness\" {",
    "test \"phase12 throughput parity gate keeps queue-restore precedence explicit\" {",
    "summary.free_transmit_descriptors_after_recycle",
    "summary.queue_pair_ratio_pct",
};

const BUILD_MARKERS = [_][]const u8{
    "../../drivers/net/virtio_net_throughput_parity.zig",
    "\"phase12_virtio_net_throughput_parity.zig\"",
    "\"phase12-virtio-net-throughput-parity-tests\"",
    "throughput_parity_step = b.step(",
    "\"phase12-virtio-net-throughput-parity\"",
    "throughput_parity_step.dependOn(&throughput_parity_tests.step);",
};

const MAKEFILE_MARKERS = [_][]const u8{
    "phase12-validate:",
    "phase12-virtio-net-throughput-parity-test:",
    "$(ZIG) build phase12-virtio-net-throughput-parity --build-file zigux/tests/phase12_build.zig --summary all",
};

const WORKFLOW_MARKERS = [_][]const u8{
    "Run current Phase 12 throughput-parity anchor",
};

const EXPECTED_MANIFEST_FIELDS = [_][]const u8{
    "lane_key",
    "P12-L04",
    "phase",
    "Phase 12",
    "slug",
    "phase12-virtio-net-throughput-parity-packet",
    "anchor",
    "drivers/net/virtio_net.c",
    "status",
    "throughput_parity_helper_present_direct_checker_and_isolated_route_guard_present",
    "scope",
    "review-only virtio_net throughput parity helper evidence plus the direct ",
    "isolated-route guard around the dedicated throughput replay",
    "next_safe_step",
    "keep future same-lane follow-through narrowed to measured transport ",
    "throughput replay or runtime completion only if this helper-local packet ",
    "drifts on master",
};

const DOC_PATH = [_][]const u8{
    "Documentation/zigux/phase12-virtio-net-throughput-parity-slice.md",
};

const DRIVER_PATH = [_][]const u8{
    "drivers/net/virtio_net_throughput_parity.zig",
};

const TEST_PATH = [_][]const u8{
    "zigux/tests/phase12_virtio_net_throughput_parity.zig",
};

const MANIFEST_PATH = [_][]const u8{
    "zigux/tests/fixtures/phase12_virtio_net_throughput_parity_manifest.json",
};

const BUILD_PATH = [_][]const u8{
    "zigux/tests/phase12_build.zig",
};

const MAKEFILE_PATH = [_][]const u8{
    "zigux/Makefile",
};

const WORKFLOW_PATH = [_][]const u8{
    ".github/workflows/zigux-bootstrap.yml",
};

const CHECKER_PATH = [_][]const u8{
    "scripts/zigux/check_phase12_virtio_net_throughput_parity_packet.zig",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_FILES) |marker| try guard.requireMarker(text, marker);
    for (DOC_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (DRIVER_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (TEST_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (BUILD_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MAKEFILE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (WORKFLOW_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_MANIFEST_FIELDS) |marker| try guard.requireMarker(text, marker);
    for (DOC_PATH) |marker| try guard.requireMarker(text, marker);
    for (DRIVER_PATH) |marker| try guard.requireMarker(text, marker);
    for (TEST_PATH) |marker| try guard.requireMarker(text, marker);
    for (MANIFEST_PATH) |marker| try guard.requireMarker(text, marker);
    for (BUILD_PATH) |marker| try guard.requireMarker(text, marker);
    for (MAKEFILE_PATH) |marker| try guard.requireMarker(text, marker);
    for (WORKFLOW_PATH) |marker| try guard.requireMarker(text, marker);
    for (CHECKER_PATH) |marker| try guard.requireMarker(text, marker);
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
