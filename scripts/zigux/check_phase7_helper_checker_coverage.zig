const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE7_HELPER_CHECKER_COVERAGE=pass";
pub const self_test_pass_marker = "PHASE7_HELPER_CHECKER_COVERAGE_SELF_TEST=pass";

const CHECKER_EXPECTATIONS = [_][]const u8{
    "(scripts\\zigux/check_phase7_cmdline_packet.zig",
    "--self-testPHASE7_CMDLINE_PACKET_SELF_TEST=passPHASE7_CMDLINE_PACKET=passEXPECTED_MANIFEST_LANE_KEY = \"P7-L08\"EXPECTED_MANIFEST_ANCHOR = \"lib/cmdline.c\"",
    ")",
    "(scripts\\zigux/check_phase7_argv_split_packet.zig",
    "--self-testPHASE7_ARGV_SPLIT_PACKET_SELF_TEST=passPHASE7_ARGV_SPLIT_PACKET=passEXPECTED_MANIFEST_LANE_KEY = \"P7-L09\"EXPECTED_MANIFEST_ANCHOR = \"lib/argv_split.c\"",
    ")",
    "(scripts\\zigux/check_phase7_rbtree_parity.zig",
    "--self-testPHASE7_RBTREE_PARITY_SELF_TEST=passPHASE7_RBTREE_PARITY=passEXPECTED_MANIFEST_LANE_KEY = \"P7-L13\"EXPECTED_MANIFEST_ANCHOR = \"lib/rbtree.c\"",
    ")",
    "(scripts\\zigux/check_phase7_string_helpers_format_boundary_packet.zig",
    "--self-testPHASE7_STRING_HELPERS_FORMAT_BOUNDARY_PACKET_SELF_TEST=passPHASE7_STRING_HELPERS_FORMAT_BOUNDARY_PACKET=passCurrent `master` also still ships no standalone broad `*format*` Phase 5 reference sample here.",
    ")",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_checker_expectations_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_checker_expectations_path);
    const text_checker_expectations = try guard.readUtf8File(io, allocator, text_checker_expectations_path);
    defer allocator.free(text_checker_expectations);
    for (CHECKER_EXPECTATIONS) |marker| try guard.requireMarker(text_checker_expectations, marker);
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
