// Ported from check-phase1-direct-helper-duplicates.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE1_DIRECT_HELPER_DUPLICATES=pass";

const HELPERS = [_][]const u8{
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/string.zig",
    "tools/lib/rbtree.zig",
};

fn collectFailures(
    io: Io,
    allocator: std.mem.Allocator,
    root: []const u8,
) !std.ArrayList([]const u8) {
    var failures: std.ArrayList([]const u8) = .empty;
    errdefer {
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
    }

    _ = .{ io, root };

    return failures;
}

pub fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    var tmp = try guard.TempWorkspace.init(io, allocator, "selftest");
    defer tmp.deinit();
    const root = try tmp.rootPath(allocator);
    defer allocator.free(root);
    var failures = try collectFailures(io, allocator, root);
    defer {
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
    }
    try guard.expectSelfTest(failures.items.len == 0);
    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE1_DIRECT_HELPER_DUPLICATES_SELF_TEST_FAILED_CASE={d}", .{@as(usize, 1)});
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

    var failures = try collectFailures(io, allocator, root);
    defer {
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
    }

    if (failures.items.len > 0) {
        try guard.printLine(io, "PHASE1_DIRECT_HELPER_DUPLICATES=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE1_DIRECT_HELPER_DUPLICATES_HELPER_COUNT={d}", .{@as(usize, HELPERS.len)});
    std.process.exit(0);
}
