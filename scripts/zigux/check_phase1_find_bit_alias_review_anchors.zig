// Ported from check-phase1-find-bit-alias-review-anchors.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE1_FIND_BIT_ALIAS_REVIEW_ANCHORS_SELF_TEST=pass";

const HELPER_REL = "tools/lib/find_bit.zig";

const REQUIRED_MARKERS = [_]struct { label: []const u8, marker: []const u8 }{
    .{ .label = "linux_alias_mirror_test", .marker = "test \"Linux-style aliases mirror the primary find helpers, including andnot\" {" },
    .{ .label = "linux_next_or_tail_alias_test", .marker = "test \"Linux-style next-or aliases clamp tail words and past-end starts\" {" },
    .{ .label = "linux_clump_tail_alias_test", .marker = "test \"Linux-style clump aliases mask tail bytes and preserve exhausted caller bytes\" {" },
    .{ .label = "linux_find_next_or_tail", .marker = "find_next_or_bit(&lhs, &rhs, nbits, bits_per_long + 2)" },
    .{ .label = "linux_find_next_or_past_end", .marker = "find_next_or_bit(&[_]Word{}, &[_]Word{}, 7, 7)" },
    .{ .label = "linux_underscore_next_or_past_end", .marker = "_find_next_or_bit(&[_]Word{}, &[_]Word{}, 7, 11)" },
    .{ .label = "linux_find_first_clump_tail", .marker = "try std.testing.expectEqual(@as(usize, bits_per_long), find_first_clump8(&clump, &bitmap, nbits));" },
    .{ .label = "linux_underscore_first_clump_tail", .marker = "try std.testing.expectEqual(@as(usize, bits_per_long), _find_first_clump8(&clump, &bitmap, nbits));" },
    .{ .label = "linux_find_next_clump_exhausted", .marker = "try std.testing.expectEqual(@as(usize, nbits), find_next_clump8(&clump, &bitmap, nbits, bits_per_long + 5));" },
    .{ .label = "linux_underscore_next_clump_exhausted", .marker = "try std.testing.expectEqual(@as(usize, nbits), _find_next_clump8(&clump, &bitmap, nbits, bits_per_long + 9));" },
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
        const relative_path = "tools/lib/find_bit.zig";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    if (failures.items.len > 0) return failures;

    {
        const relative_path = "tools/lib/find_bit.zig";
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
    }

    return failures;
}

pub fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    var tmp = try guard.TempWorkspace.init(io, allocator, "selftest");
    defer tmp.deinit();
    const root = try tmp.rootPath(allocator);
    defer allocator.free(root);
    {
        const relative_path = "tools/lib/find_bit.zig";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        var content = std.ArrayList(u8).empty;
        defer content.deinit(allocator);
        for (REQUIRED_MARKERS) |entry| {
            try content.appendSlice(allocator, entry.marker);
            try content.append(allocator, '\n');
        }
        try guard.writeUtf8File(io, full_path, content.items);
    }
    var failures = try collectFailures(io, allocator, root);
    defer {
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
    }
    try guard.expectSelfTest(failures.items.len == 0);
    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE1_FIND_BIT_ALIAS_REVIEW_ANCHORS_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
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
        try guard.printLine(io, "PHASE1_FIND_BIT_ALIAS_REVIEW_ANCHORS_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    std.process.exit(0);
}
