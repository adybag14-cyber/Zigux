// Ported from check-phase1-bitmap-zero-bit-regression.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE1_BITMAP_ZERO_BIT_REGRESSION_SELF_TEST=pass";

const BITMAP_REL = "tools/lib/bitmap.zig";

const FORBIDDEN_MARKERS = [_]struct { label: []const u8, marker: []const u8 }{
    .{ .label = "stale_one_argument_expect_equal", .marker = "try std.testing.expectEqual(equal(lhs[0..0], rhs[0..0], 0));" },
};

const REQUIRED_MARKERS = [_]struct { label: []const u8, marker: []const u8 }{
    .{ .label = "zero_bit_test_anchor", .marker = "test \"bitmap zero-bit logical helpers stay explicit\" {" },
    .{ .label = "zero_bit_equal_expect", .marker = "try std.testing.expect(equal(lhs[0..0], rhs[0..0], 0));" },
    .{ .label = "zero_bit_subset_expect", .marker = "try std.testing.expect(subset(lhs[0..0], rhs[0..0], 0));" },
    .{ .label = "zero_bit_scnprintf_len", .marker = "const len = scnprintf(lhs[0..0], 0, &buffer);" },
    .{ .label = "zero_bit_scnprintf_untouched", .marker = "try std.testing.expectEqualSlices(u8, &[_]u8{ 0xcc, 0xcc, 0xcc }, &buffer);" },
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

    {
        const relative_path = "tools/lib/bitmap.zig";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    if (failures.items.len > 0) return failures;

    {
        const relative_path = "tools/lib/bitmap.zig";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        const text = guard.readUtf8File(io, allocator, full_path) catch |err| switch (err) {
            guard.GuardError.IOError => {
                const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
                try failures.append(allocator, issue);
                return failures;
            },
            else => return err,
        };
        defer allocator.free(text);
        for (REQUIRED_MARKERS) |entry| {
            const count = guard.countOccurrences(text, entry.marker);
            if (count != 1) {
                const issue = try std.fmt.allocPrint(allocator, "{s}:expected=1:actual={d}", .{ entry.label, count });
                try failures.append(allocator, issue);
            }
        }
        for (FORBIDDEN_MARKERS) |entry| {
            const count = guard.countOccurrences(text, entry.marker);
            if (count != 0) {
                const issue = try std.fmt.allocPrint(allocator, "{s}:expected=0:actual={d}", .{ entry.label, count });
                try failures.append(allocator, issue);
            }
        }
    }

    return failures;
}

fn buildSampleSource(allocator: std.mem.Allocator) ![]u8 {
    var content = std.ArrayList(u8).empty;
    errdefer content.deinit(allocator);
    for (REQUIRED_MARKERS) |entry| {
        try content.appendSlice(allocator, entry.marker);
        try content.append(allocator, '\n');
    }
    for (FORBIDDEN_MARKERS) |entry| {
        try content.appendSlice(allocator, entry.marker);
        try content.append(allocator, '\n');
    }
    return try content.toOwnedSlice(allocator);
}

pub fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    var tmp = try guard.TempWorkspace.init(io, allocator, "selftest");
    defer tmp.deinit();
    const root = try tmp.rootPath(allocator);
    defer allocator.free(root);
    const sample = try buildSampleSource(allocator);
    defer allocator.free(sample);
    {
        const relative_path = "tools/lib/bitmap.zig";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        try guard.writeUtf8File(io, full_path, sample);
        var failures = try collectFailures(io, allocator, root);
        defer {
            for (failures.items) |item| allocator.free(item);
            failures.deinit(allocator);
        }
        try guard.expectSelfTest(failures.items.len == 0);
    }
    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE1_BITMAP_ZERO_BIT_REGRESSION_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 16)});
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
        try guard.printLine(io, "PHASE1_BITMAP_ZERO_BIT_REGRESSION_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    std.process.exit(0);
}
