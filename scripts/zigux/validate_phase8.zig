const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE8_VALIDATION=pass";
pub const self_test_pass_marker = "PHASE8_SELF_TEST=pass";

const CHECKERS = [_][]const u8{
    "TESTS_ALIGNMENT_CHECKER",
    "HELP_KALLSYMS_PACKET_CHECKER",
    "HELP_KALLSYMS_BUILD_SHARD_CHECKER",
    "PERF_BUFFER_POLL_GATE_CHECKER",
    "LIBBPF_SHARD_ROUTES_CHECKER",
    "LIBBPF_SEGMENT_GATE_CHECKER",
    "EXEC_CMD_PACKET_CHECKER",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_checkers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_checkers_path);
    const text_checkers = try guard.readUtf8File(io, allocator, text_checkers_path);
    defer allocator.free(text_checkers);
    for (CHECKERS) |marker| try guard.requireMarker(text_checkers, marker);
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
