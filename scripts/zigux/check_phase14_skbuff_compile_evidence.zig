const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE14_SKBUFF_COMPILE_EVIDENCE_SELF_TEST=pass";

const EXPECTED_NOTE_MARKERS = [_][]const u8{
    "PHASE14_LANE_KEY=P14-L11",
    "PHASE14_BLOCKED_GAP=phase14-skbuff-live-ownership-blocker",
    "current `master` still ships the bounded skbuff anchor packet files `zigux/tests/phase14_skbuff_bridge.zig`, `zigux/tests/phase14_build.zig`, and `net/core/skbuff_bridge.zig`",
    "`full_bundle_only`",
    "`phase14-skbuff-bridge-tests`",
    "`zig build test --build-file zigux/tests/phase14_build.zig --summary all`",
    "`make -C zigux phase14-test`",
    "keeps the skbuff shard out of `phase14-smoke`",
};

const FORBIDDEN_NOTE_MARKERS = [_][]const u8{
    "PHASE14_BLOCKED_GAP=phase14-skbuff-anchor-packet-missing",
    "no longer exposes the earlier `P14-L11` skbuff anchor packet files",
    "must not be treated as live compile evidence on current `master`",
    "anchor packet is absent",
};

const EXPECTED_BUILD_MARKERS = [_][]const u8{
    ".root_source_file = b.path(\"../../net/core/skbuff_bridge.zig\")",
    "phase14_skbuff_bridge_module.addImport(\"skbuff_bridge\", skbuff_bridge_module);",
    ".name = \"phase14-skbuff-bridge-tests\"",
    "test_step.dependOn(&run_phase14_skbuff_bridge_tests.step);",
};

const FORBIDDEN_BUILD_MARKERS = [_][]const u8{
    "smoke_step.dependOn(&run_phase14_skbuff_bridge_tests.step);",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (EXPECTED_NOTE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (FORBIDDEN_NOTE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_BUILD_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (FORBIDDEN_BUILD_MARKERS) |marker| try guard.requireMarker(text, marker);
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
