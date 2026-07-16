const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "LANE05_ARCHIVE_PARTS_PACKET=pass";
pub const self_test_pass_marker = "LANE05_ARCHIVE_PARTS_PACKET_SELF_TEST=pass";

const WORKFLOW_REL = ".github/workflows/zigux-bootstrap.yml";

const WORKFLOW_MARKERS = [_][]const u8{
    "repo_archive_parts_dir=\"${repo_archive_path}.parts\"",
    "stage_pinned_zig_archive.zig",
    "--parts-dir \"$repo_archive_parts_dir\"",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const workflow_path = try guard.joinPath(allocator, root, WORKFLOW_REL);
    defer allocator.free(workflow_path);
    const workflow = try guard.readUtf8File(io, allocator, workflow_path);
    defer allocator.free(workflow);
    for (WORKFLOW_MARKERS) |marker| try guard.requireMarker(workflow, marker);
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    try checkRepo(io, allocator, root);
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(init.arena.allocator());

    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) self_test = true;
        if (std.mem.eql(u8, arg, "--root")) {
            index += 1;
            if (index >= args.len) std.process.exit(2);
            explicit_root = args[index];
        }
    }

    const root = explicit_root orelse try guard.repoRootFromScript(allocator);
    defer if (explicit_root == null) allocator.free(root);

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    checkRepo(io, allocator, root) catch {
        std.process.exit(1);
    };
    try guard.printLine(io, "{s}", .{live_pass_marker});
}
