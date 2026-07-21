const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE2_FIXDEP_DETERMINISM_CONTRACT=pass";
pub const self_test_pass_marker = "PHASE2_FIXDEP_DETERMINISM_CONTRACT_SELF_TEST=pass";

const REQUIRED_EXACT_LINES = [_][]const u8{
    "if (zig_result.exit_code != case_item.expected_exit_code or zig_repeat.exit_code != zig_result.exit_code) {",
    "try guard.printLine(io, \"FIXDEP_CASE_EXIT_MISMATCH={s}:expected={d}:first={d}:repeat={d}\", .{ case_item.name, case_item.expected_exit_code, zig_result.exit_code, zig_repeat.exit_code });",
    "try diffText(io, allocator, root, zig, expected_stdout, actual_stdout_path);",
    "try diffText(io, allocator, root, zig, expected_stdout, repeat_stdout_path);",
    "try diffText(io, allocator, root, zig, actual_stdout_path, repeat_stdout_path);",
    "try diffText(io, allocator, root, zig, expected_stderr, actual_stderr_path);",
    "try diffText(io, allocator, root, zig, expected_stderr, repeat_stderr_path);",
    "try diffText(io, allocator, root, zig, actual_stderr_path, repeat_stderr_path);",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_exact_lines_path = try guard.joinPath(allocator, root, "scripts/zigux/check_fixdep_diff.zig");
    defer allocator.free(text_required_exact_lines_path);
    const text_required_exact_lines = try guard.readUtf8File(io, allocator, text_required_exact_lines_path);
    defer allocator.free(text_required_exact_lines);
    for (REQUIRED_EXACT_LINES) |marker| try guard.requireExactLineCount(text_required_exact_lines, marker, 1);
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
    const args = try init.minimal.args.toSlice(allocator);
    defer allocator.free(args);

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
        _ = try runSelfTest(io, allocator);
        return;
    }

    checkRepo(io, allocator, root) catch {
        std.process.exit(1);
    };
    try guard.printLine(io, "{s}", .{live_pass_marker});
}
