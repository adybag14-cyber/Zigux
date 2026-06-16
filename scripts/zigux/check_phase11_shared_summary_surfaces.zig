const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE11_SHARED_SUMMARY_SURFACES_SELF_TEST=pass";

const CONTRACT_REQUIRED_MARKERS = [_][]const u8{
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "still skip Phase 11",
    "next same-lane reminder follow-through",
};

const DOCS_README_FORBIDDEN_MARKERS = [_][]const u8{
    "Phase 11 notes",
    "phase11",
};

const REVIEW_CHECKLIST_REQUIRED_MARKERS = [_][]const u8{
    "shared Phase 11",
    "make -C zigux phase11-validate",
};

const SCRIPTS_README_FORBIDDEN_MARKERS = [_][]const u8{
    "phase11",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (CONTRACT_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (DOCS_README_FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REVIEW_CHECKLIST_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SCRIPTS_README_FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text, marker);
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
