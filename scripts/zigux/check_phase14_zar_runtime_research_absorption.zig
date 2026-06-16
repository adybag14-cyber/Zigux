const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE14_ZAR_RUNTIME_RESEARCH_ABSORPTION_SELF_TEST=pass";

const NOTE_MARKERS = [_][]const u8{
    "`PHASE14_LANE_KEY=P14-L06`",
    "`PHASE14_SOURCE=ZAR-Zig-Agent-Runtime-main/docs/architecture.md`",
    "gateway and dispatcher layering maps only to review-boundary vocabulary",
    "bounded in-memory histories and compact retention map only to audit prompts for workqueue and ring-buffer study notes",
    "secret-store fallback reporting maps only to explicit stay-in-C and unsupported-backend wording",
    "bare-metal ABI lifecycle hooks map only to ABI-boundary review prompts",
    "does not add `kernel/workqueue_bridge.zig`, `kernel/trace/ring_buffer.zig`, `net/core/skbuff_bridge.zig`, or `kernel/rcu/tree_bridge.zig`",
    "does not change the freeze map, Architecture Council posture, or Phase 15 governance packet",
};

const ABSENT_CLAIMS = [_][]const u8{
    "PHASE14_STATUS=parity",
    "PHASE14_STATUS=implementation_ready",
    "workqueue parity is ready",
    "ring buffer parity is ready",
    "skbuff ownership transferred",
    "rcu tree ownership transferred",
};

const MARKER = [_][]const u8{
    "PHASE14_CHECK_PACKET=zar_runtime_research_absorption",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (NOTE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (ABSENT_CLAIMS) |marker| try guard.requireMarker(text, marker);
    for (MARKER) |marker| try guard.requireMarker(text, marker);
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
