const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE2_FIXDEP_WORKFLOW_ORDER=pass";
pub const self_test_pass_marker = "PHASE2_FIXDEP_WORKFLOW_ORDER_SELF_TEST=pass";

const REQUIRED_FIXDEP_STEPS = [_][]const u8{
    "Self-test current Phase 2 fixdep gate checkerzig run scripts\\zigux/check_phase2_fixdep_gate.zig -- --self-test",
    "Check current Phase 2 fixdep gate packetzig run scripts\\zigux/check_phase2_fixdep_gate.zig",
    "Self-test current fixdep parity checkerzig run scripts\\zigux/check_fixdep_diff.zig -- --self-test",
    "Check current fixdep parity packetzig run scripts\\zigux/check_fixdep_diff.zig",
    "Run current Phase 2 fixdep unit testszig test scripts/zigux/fixdep.zig",
    "Run current Phase 2 fixdep make wrappermake -C zigux phase2-fixdep",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_fixdep_steps_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_required_fixdep_steps_path);
    const text_required_fixdep_steps = try guard.readUtf8File(io, allocator, text_required_fixdep_steps_path);
    defer allocator.free(text_required_fixdep_steps);
    for (REQUIRED_FIXDEP_STEPS) |marker| try guard.requireMarker(text_required_fixdep_steps, marker);
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
