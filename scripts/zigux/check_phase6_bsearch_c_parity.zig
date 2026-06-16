const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE6_BSEARCH_C_PARITY=pass";
pub const self_test_pass_marker = "PHASE6_BSEARCH_C_PARITY_SELF_TEST=pass";

const REQUIRED_OUTPUT_LINES = [_][]const u8{
    "descending-hit\t34\t2",
    "descending-miss\t20\tnull",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_output_lines_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/phase6_bsearch_c_harness.c");
    defer allocator.free(text_required_output_lines_path);
    const text_required_output_lines = try guard.readUtf8File(io, allocator, text_required_output_lines_path);
    defer allocator.free(text_required_output_lines);
    for (REQUIRED_OUTPUT_LINES) |marker| try guard.requireExactLineCount(text_required_output_lines, marker, 1);
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
