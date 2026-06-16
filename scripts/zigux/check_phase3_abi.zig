const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "CHECK_PHASE3_ABI=pass";
pub const self_test_pass_marker = "CHECK_PHASE3_ABI_SELF_TEST=pass";

const SELF_TEST_REPLACEMENTS = [_][]const u8{
    "PHASE3_VALIDATION_SELF_TEST_CASE_COUNT=PHASE3_ABI_CHECK_SELF_TEST_CASE_COUNT=",
    "PHASE3_VALIDATION_SELF_TEST=PHASE3_ABI_CHECK_SELF_TEST=",
};

const RUN_REPLACEMENTS = [_][]const u8{
    "PHASE3_VALIDATION=PHASE3_ABI_CHECK=",
    "PHASE3_SCOPE=PHASE3_ABI_SCOPE=",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_self_test_replacements_path = try guard.joinPath(allocator, root, "scripts\zigux/validate_phase3.zig");
    defer allocator.free(text_self_test_replacements_path);
    const text_self_test_replacements = try guard.readUtf8File(io, allocator, text_self_test_replacements_path);
    defer allocator.free(text_self_test_replacements);
    for (SELF_TEST_REPLACEMENTS) |marker| try guard.requireMarker(text_self_test_replacements, marker);
    const text_run_replacements_path = try guard.joinPath(allocator, root, "scripts\zigux/validate_phase3.zig");
    defer allocator.free(text_run_replacements_path);
    const text_run_replacements = try guard.readUtf8File(io, allocator, text_run_replacements_path);
    defer allocator.free(text_run_replacements);
    for (RUN_REPLACEMENTS) |marker| try guard.requireMarker(text_run_replacements, marker);
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
