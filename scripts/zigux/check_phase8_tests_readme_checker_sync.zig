const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "CHECK_PHASE8_TESTS_README_CHECKER_SYNC=pass";
pub const self_test_pass_marker = "CHECK_PHASE8_TESTS_README_CHECKER_SYNC_SELF_TEST=pass";

const TESTS_README_PATH_NAME = [_][]const u8{
    "TESTS_README_PATH",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_tests_readme_path_name_path = try guard.joinPath(allocator, root, "scripts/zigux/validate_phase8.zig");
    defer allocator.free(text_tests_readme_path_name_path);
    const text_tests_readme_path_name = try guard.readUtf8File(io, allocator, text_tests_readme_path_name_path);
    defer allocator.free(text_tests_readme_path_name);
    for (TESTS_README_PATH_NAME) |marker| try guard.requireMarker(text_tests_readme_path_name, marker);
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
