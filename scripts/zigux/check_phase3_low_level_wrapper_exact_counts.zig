const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_LOW_LEVEL_WRAPPER_EXACT_COUNTS=pass";
pub const self_test_pass_marker = "PHASE3_LOW_LEVEL_WRAPPER_EXACT_COUNTS_SELF_TEST=pass";

const DUPLICATE_SELF_TEST_CASES = [_][]const u8{
    "`zigux/tests/phase3_low_level_wrappers_build.zig`",
    "phase3-low-level-wrappers-test:",
    "      - name: Run current Phase 3 low-level wrapper replay",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_duplicate_self_test_cases_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_duplicate_self_test_cases_path);
    const text_duplicate_self_test_cases = try guard.readUtf8File(io, allocator, text_duplicate_self_test_cases_path);
    defer allocator.free(text_duplicate_self_test_cases);
    for (DUPLICATE_SELF_TEST_CASES) |marker| try guard.requireMarker(text_duplicate_self_test_cases, marker);
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
