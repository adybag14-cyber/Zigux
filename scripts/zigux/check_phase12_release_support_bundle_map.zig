const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "{CHECK_NAME}_SELF_TEST=pass";

const REQUIRED_FILES = [_][]const u8{
    "NOTE_PATH",
    "BUILD_ONLY_CHECKER_PATH",
    "BUILD_INVENTORY_CHECKER_PATH",
    "READINESS_CHECKER_PATH",
    "VALIDATOR_PATH",
    "WORKFLOW_PATH",
    "MAKEFILE_PATH",
    "BUILD_PATH",
};

const NOTE_MARKERS = [_][]const u8{
    "- lane owner: `pmo-release`",
    "- `scripts/zigux/check_build_only_phase12_surface.zig`",
    "- `scripts/zigux/check_phase12_build_inventory.zig`",
    "- `scripts/zigux/check_phase12_release_readiness_packet.zig`",
    "- `make -C zigux phase12-validate`",
    "- `make -C zigux phase12-smoke`",
    "- `make -C zigux phase12-test`",
    "- `make -C zigux phase12`",
    "- the shared smoke-and-test route is still the six-file `virtio_net` packet wired through `zigux/tests/phase12_build.zig`",
};

const WORKFLOW_MARKERS = [_][]const u8{
    "run: zig run scripts/zigux/check_build_only_phase12_surface.zig -- --self-test",
    "run: zig run scripts/zigux/check_phase12_build_inventory.zig -- --self-test",
    "run: zig run scripts/zigux/check_phase12_build_inventory.zig --",
    "run: zig run scripts/zigux/check_phase12_release_readiness_packet.zig -- --self-test",
    "run: zig run scripts/zigux/validate_phase12.zig",
    "run: make -C zigux phase12-smoke",
    "run: make -C zigux phase12-test",
    "run: make -C zigux phase12",
};

const MAKEFILE_MARKERS = [_][]const u8{
    "phase12-validate:",
    "phase12-smoke:",
    "phase12-test:",
    "phase12: phase12-validate phase12-smoke phase12-test",
};

const BUILD_MARKERS = [_][]const u8{
    "phase12_virtio_net_queue_resume.zig",
    "phase12_virtio_net_receive_refill_replay.zig",
    "phase12_virtio_net_transmit_recycle.zig",
    "phase12_virtio_net_post_reset_replay.zig",
    "phase12_virtio_net_throughput_parity.zig",
    "phase12_virtio_net_survey.zig",
};

const CHECK_NAME = [_][]const u8{
    "PHASE12_RELEASE_SUPPORT_BUNDLE_MAP",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_FILES) |marker| try guard.requireMarker(text, marker);
    for (NOTE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (WORKFLOW_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MAKEFILE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (BUILD_MARKERS) |marker| try guard.requireMarker(text, marker);
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
