const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE7_ARGV_SPLIT_NEXT_STEP=pass";
pub const self_test_pass_marker = "PHASE7_ARGV_SPLIT_NEXT_STEP_SELF_TEST=pass";

const EXPECTED_NEXT_BOUNDED_STEP = [_][]const u8{
    "Keep same-lane follow-through limited to the returned fixture-backed helper-local survey-manifest-checker truthfulness packet, starting with exact `next_bounded_step` enforcement inside `scripts\\zigux/check_phase7_argv_split_packet.zig` before widening into any new vector-backed replay proof.",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_expected_next_bounded_step_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_expected_next_bounded_step_path);
    const text_expected_next_bounded_step = try guard.readUtf8File(io, allocator, text_expected_next_bounded_step_path);
    defer allocator.free(text_expected_next_bounded_step);
    for (EXPECTED_NEXT_BOUNDED_STEP) |marker| try guard.requireMarker(text_expected_next_bounded_step, marker);
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
