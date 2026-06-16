const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE11_SCRIPTS_README_CONTRACT_SYNC_SELF_TEST=pass";

const DEFAULT_ROOT = [_][]const u8{
    "Path.resolve.parents[2]iflen>3elsePath.cwd",
};

const CONTRACT_SKIP_MARKERS = [_][]const u8{
    "broader contributor-facing summaries in `scripts/zigux/README.md` still skip that active packet",
    "no `Documentation/zigux/README.md` or `scripts/zigux/README.md` Phase 11 coverage on current `master`",
};

const SCRIPTS_README_ACTIVE_MARKERS = [_][]const u8{
    "scripts\zigux/validate_phase11.zig",
    "make -C zigux phase11-validate",
    "Documentation/zigux/phase11-shared-replay-contract.md",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (DEFAULT_ROOT) |marker| try guard.requireMarker(text, marker);
    for (CONTRACT_SKIP_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SCRIPTS_README_ACTIVE_MARKERS) |marker| try guard.requireMarker(text, marker);
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
