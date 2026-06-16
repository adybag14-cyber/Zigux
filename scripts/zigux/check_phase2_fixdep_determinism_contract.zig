const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE2_FIXDEP_DETERMINISM_CONTRACT=pass";
pub const self_test_pass_marker = "PHASE2_FIXDEP_DETERMINISM_CONTRACT_SELF_TEST=pass";

const REQUIRED_EXACT_LINES = [_][]const u8{
    "compare_returncode(f\"{case['name']} Zig\", expected_exit_code, zig_result.returncode)",
    "compare_returncode(f\"{case['name']} Zig repeat\", zig_result.returncode, zig_repeat_result.returncode)",
    "diff_text(expected_stdout, zig_actual)",
    "diff_text(expected_stdout, zig_repeat)",
    "diff_text(zig_actual, zig_repeat)",
    "diff_text(expected_stderr_path, zig_actual_stderr)",
    "diff_text(expected_stderr_path, zig_repeat_stderr)",
    "diff_text(zig_actual_stderr, zig_repeat_stderr)",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_exact_lines_path = try guard.joinPath(allocator, root, "scripts\zigux/check_fixdep_diff.zig");
    defer allocator.free(text_required_exact_lines_path);
    const text_required_exact_lines = try guard.readUtf8File(io, allocator, text_required_exact_lines_path);
    defer allocator.free(text_required_exact_lines);
    for (REQUIRED_EXACT_LINES) |marker| try guard.requireExactLineCount(text_required_exact_lines, marker, 1);
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
