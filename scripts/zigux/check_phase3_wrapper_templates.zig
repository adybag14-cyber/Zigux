const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_WRAPPER_TEMPLATES_CHECK=pass";
pub const self_test_pass_marker = "PHASE3_WRAPPER_TEMPLATES_CHECK_SELF_TEST=pass";

const SCALAR_MARKERS = [_][]const u8{
    "from phase3_check_lib import run_from_wrapper",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_scalar_markers_path = try guard.joinPath(allocator, root, "scripts/zigux/check_phase3_wrapper_templates.zig");
    defer allocator.free(text_scalar_markers_path);
    const text_scalar_markers = try guard.readUtf8File(io, allocator, text_scalar_markers_path);
    defer allocator.free(text_scalar_markers);
    for (SCALAR_MARKERS) |marker| try guard.requireMarker(text_scalar_markers, marker);
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    try checkRepo(io, allocator, try guard.defaultRepoRoot(allocator));
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);

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
