const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE9_FREEZE_MAP_BOUNDARY_CHECK=pass";

const LANE_SEQUENCING_PATH = [_][]const u8{
    "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md",
};

const DOCS_README_PATH = [_][]const u8{
    "Documentation/zigux/README.md",
};

const SCRIPTS_README_PATH = [_][]const u8{
    "scripts/zigux/README.md",
};

const LANE_FREEZE_MAP_MARKER = [_][]const u8{
    "keep `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` framed as freeze-map study-only anchors",
};

const LANE_PHASE15_MARKER = [_][]const u8{
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
};

const DOCS_FREEZE_MAP_MARKER = [_][]const u8{
    "`kernel/workqueue.c` plus `kernel/trace/ring_buffer.c` framed only through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` instead of as runtime-pilot bridge-readiness cues",
};

const SCRIPTS_FREEZE_MAP_MARKER = [_][]const u8{
    "keep the freeze-map boundary explicit too: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only anchors through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` rather than Phase 9 runtime-substrate readiness cues",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (LANE_SEQUENCING_PATH) |marker| try guard.requireMarker(text, marker);
    for (DOCS_README_PATH) |marker| try guard.requireMarker(text, marker);
    for (SCRIPTS_README_PATH) |marker| try guard.requireMarker(text, marker);
    for (LANE_FREEZE_MAP_MARKER) |marker| try guard.requireMarker(text, marker);
    for (LANE_PHASE15_MARKER) |marker| try guard.requireMarker(text, marker);
    for (DOCS_FREEZE_MAP_MARKER) |marker| try guard.requireMarker(text, marker);
    for (SCRIPTS_FREEZE_MAP_MARKER) |marker| try guard.requireMarker(text, marker);
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
