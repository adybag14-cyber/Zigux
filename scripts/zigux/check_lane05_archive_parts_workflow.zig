const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "LANE05_ARCHIVE_PARTS_WORKFLOW=pass";
pub const self_test_pass_marker = "LANE05_ARCHIVE_PARTS_WORKFLOW_SELF_TEST=pass";

const workflow_rel = ".github/workflows/zigux-bootstrap-archive-parts-packet.yml";
const workflow_markers = [_][]const u8{
    "name: zigux-bootstrap-archive-parts-packet",
    "branches: [ master ]",
    "- 'scripts/zigux/check_lane05_archive_parts_workflow.zig'",
    "- 'scripts/zigux/check_lane05_archive_parts_packet.zig'",
    "- name: Setup pinned Zig toolchain",
    "canonical_tag = \"upstream-64dfaa568db0\"",
    "zig test scripts/zigux/check_zig_toolchain.zig",
    "zig test scripts/zigux/check_lane05_archive_parts_packet.zig",
    "zig test scripts/zigux/check_lane05_archive_parts_workflow.zig",
    "zig run scripts/zigux/check_lane05_archive_parts_workflow.zig -- --self-test",
    "zig run scripts/zigux/check_lane05_archive_parts_workflow.zig",
    "zig run scripts/zigux/check_lane05_archive_parts_packet.zig -- --self-test",
    "zig run scripts/zigux/check_lane05_archive_parts_packet.zig -- --allow-missing",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const workflow_path = try guard.joinPath(allocator, root, workflow_rel);
    defer allocator.free(workflow_path);
    const workflow = try guard.readUtf8File(io, allocator, workflow_path);
    defer allocator.free(workflow);
    for (workflow_markers) |marker| try guard.requireMarker(workflow, marker);
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
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
        std.process.exit(2);
    }

    if (self_test) std.process.exit(try runSelfTest(io, allocator));

    const root = explicit_root orelse try guard.repoRootFromScript(allocator);
    defer if (explicit_root == null) allocator.free(root);
    checkRepo(io, allocator, root) catch std.process.exit(1);
    try guard.printLine(io, "{s}", .{live_pass_marker});
}
