const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE10_SAMPLE_RUNTIME_SCOREBOARD_SELF_TEST=pass";

const SCOREBOARD_MARKERS = [_][]const u8{
    "PHASE10_SCOREBOARD_STATUS=active_shared_packet",
    "PHASE10_SCOREBOARD_SCOPE=sample-runtime-parity-notes-only",
    "PHASE10_SCOREBOARD_ROADMAP_ANCHORS=virtqueue-wrappers,mmio-wrappers,lab-only-driver-validation",
    "PHASE10_SCOREBOARD_RISKY_TRANSPORT=blocked_on_risky_transport",
    "PHASE10_SCOREBOARD_SHARED_VALIDATOR=scripts\zigux/validate_phase10.zig",
    "PHASE10_SCOREBOARD_SHARED_VALIDATOR_CHECK_COUNT=11",
    "PHASE10_SCOREBOARD_SELF_TEST_CASE_COUNT=35",
    "scripts/zigux/check_phase10_ring_manifest_destinations.zig",
    "zigux/tests/phase10_virtio_ring_manifest.json",
    "Documentation/zigux/phase10-closure-evidence.md",
    "zigux-alpha/PHASE10_CLOSURE_LEDGER.md",
    "zig run scripts/zigux/validate_phase10.zig -- --self-test",
    "zig run scripts/zigux/check_phase10_ring_manifest_destinations.zig -- --self-test",
    "zig run scripts/zigux/check_phase10_sample_runtime_scoreboard.zig -- --self-test",
    "zig run scripts/zigux/check_phase10_sample_runtime_scoreboard.zig --",
    "without claiming transport-backed queue discovery, IRQ delivery, DMA behavior, probe/remove lifecycle behavior, or risky dual-implementation parity",
};

const VALIDATOR_MARKERS = [_][]const u8{
    "scripts/zigux/check_phase10_ring_manifest_destinations.zig",
    "\"phase10-ring-manifest-destinations\"",
};

const SCOREBOARD_PATH = [_][]const u8{
    "Documentation/zigux/phase10-sample-runtime-parity-scoreboard.md",
};

const VALIDATOR_PATH = [_][]const u8{
    "scripts\zigux/validate_phase10.zig",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (SCOREBOARD_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (VALIDATOR_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SCOREBOARD_PATH) |marker| try guard.requireMarker(text, marker);
    for (VALIDATOR_PATH) |marker| try guard.requireMarker(text, marker);
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
