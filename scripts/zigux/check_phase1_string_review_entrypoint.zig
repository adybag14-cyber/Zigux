// Ported from check-phase1-string-review-entrypoint.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE1_STRING_REVIEW_ENTRYPOINT_SELF_TEST=pass";

const CHECKER_REL = "scripts/zigux/check_phase1_string_review_packet.zig";

fn checkerPath(allocator: std.mem.Allocator, root: []const u8) ![]const u8 {
    return guard.joinPath(allocator, root, CHECKER_REL);
}

fn runChecker(
    io: Io,
    allocator: std.mem.Allocator,
    root: []const u8,
    zig_path: []const u8,
    passthrough: []const []const u8,
) !guard.ProcessOutput {
    var argv = std.ArrayList([]const u8).empty;
    defer argv.deinit(allocator);
    try argv.append(allocator, zig_path);
    try argv.append(allocator, "run");
    const checker = try checkerPath(allocator, root);
    defer allocator.free(checker);
    try argv.append(allocator, checker);
    try argv.append(allocator, "--");
    try argv.append(allocator, "--root");
    try argv.append(allocator, root);
    for (passthrough) |arg| try argv.append(allocator, arg);
    return guard.runProcessCapture(io, allocator, argv.items, root);
}

pub fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    _ = .{ io, allocator };
    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE1_STRING_REVIEW_ENTRYPOINT_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);

    var explicit_root: ?[]const u8 = null;
    var self_test = false;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root") or std.mem.eql(u8, arg, "--repo-root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
    }

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    const root = if (explicit_root) |value| value else try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);

    const checker = try checkerPath(allocator, root);
    defer allocator.free(checker);
    if (!guard.pathExists(io, checker)) {
        try guard.printLine(io, "missing_checker:{s}", .{checker});
        std.process.exit(1);
    }

    const zig_path = guard.findZigExecutable(io, allocator, root, null) catch {
        try guard.printLine(io, "missing_zig_executable", .{});
        std.process.exit(1);
    };
    defer allocator.free(zig_path);

    const result = try runChecker(io, allocator, root, zig_path, &.{});
    defer {
        allocator.free(result.stdout);
        allocator.free(result.stderr);
    }
    if (result.stdout.len > 0) {
        var buffer: [4096]u8 = undefined;
        var writer = Io.File.stdout().writer(io, &buffer);
        try writer.interface.writeAll(result.stdout);
        try writer.interface.flush();
    }
    if (result.stderr.len > 0) {
        var buffer: [4096]u8 = undefined;
        var writer = Io.File.stderr().writer(io, &buffer);
        try writer.interface.writeAll(result.stderr);
        try writer.interface.flush();
    }
    std.process.exit(result.exit_code);
}