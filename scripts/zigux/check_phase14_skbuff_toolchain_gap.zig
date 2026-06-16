const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE14_SKBUFF_TOOLCHAIN_GAP_SELF_TEST=pass";

const ABSENT_PACKET_PATHS = [_][]const u8{
    "Pathzigux/tests/phase14_skbuff_bridge.zig",
    "Pathzigux/tests/phase14_build.zig",
    "Pathnet/core/skbuff_bridge.zig",
    "Pathzigux/tests/phase14_skbuff_bridge_manifest.json",
};

const REQUIRED_SURVEY_MARKERS = [_][]const u8{
    "- `PHASE14_LANE_KEY=P14-L11`",
    "- `PHASE14_BLOCKED_GAP=phase14-skbuff-anchor-packet-missing`",
    "- current `master` no longer exposes `zigux/tests/phase14_skbuff_bridge.zig`",
    "- current `master` no longer exposes `zigux/tests/phase14_build.zig`",
    "- current `master` no longer exposes `net/core/skbuff_bridge.zig`",
    "- current `master` no longer exposes `zigux/tests/phase14_skbuff_bridge_manifest.json`",
    "- the previous `full_bundle_only` compile path",
    "is archival only and must not be treated as live compile evidence on current `master`",
};

const REQUIRED_GAP_NOTE_MARKERS = [_][]const u8{
    "- `PHASE14_SKBUFF_TOOLCHAIN_GAP=present`",
    "- `PHASE14_SKBUFF_TOOLCHAIN_GAP_KIND=anchor_packet_absent_under_attached_toolchain_policy`",
    "- `PHASE14_SKBUFF_TOOLCHAIN_GAP_SCOPE=skbuff_packet_truthfulness_only`",
    "- `PHASE14_SKBUFF_TOOLCHAIN_GAP_STATUS_BUCKET=study_only`",
    "- `PHASE14_SKBUFF_TOOLCHAIN_GAP_OWNER=Repo Tooling Pod`",
    "there is no livenskbuff-local packet to compile on current `master`.",
    "`scripts/zigux/check_phase14_skbuff_toolchain_gap.zig` keeps this gap note and",
    "restore a bounded skbuff anchor packet first",
};

const FORBIDDEN_GAP_NOTE_MARKERS = [_][]const u8{
    "phase14-skbuff-bridge-tests",
    "make -C zigux phase14-test",
    "zig build test --build-file zigux/tests/phase14_build.zig --summary all",
};

const MARKER = [_][]const u8{
    "PHASE14_CHECK_PACKET=skbuff_toolchain_gap",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (ABSENT_PACKET_PATHS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_SURVEY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_GAP_NOTE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (FORBIDDEN_GAP_NOTE_MARKERS) |marker| try guard.requireMarker(text, marker);
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
