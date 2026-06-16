// Ported from check-phase1-find-bit-clump.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE1_FIND_BIT_CLUMP_SELF_TEST=pass";

const MANIFEST = "zigux/tests/fixtures/phase1_helper_manifest.json";

const REQUIRED_ALIAS_EXPECTATIONS = [_]struct { label: []const u8, marker: []const u8 }{
    .{ .label = "underscore_first", .marker = "try std.testing.expectEqual(@as(usize, 0), _find_first_clump8(&clump, &clump_map, 8));" },
    .{ .label = "underscore_next", .marker = "try std.testing.expectEqual(@as(usize, 0), _find_next_clump8(&clump, &clump_map, 8, 0));" },
    .{ .label = "linux_first", .marker = "try std.testing.expectEqual(@as(usize, 0), find_first_clump8(&clump, &[_]Word{@as(Word, 1)}, 8));" },
    .{ .label = "linux_next", .marker = "try std.testing.expectEqual(@as(usize, 0), find_next_clump8(&clump, &[_]Word{@as(Word, 1)}, 8, 0));" },
};

const REQUIRED_FUNCTION_MARKERS = [_]struct { label: []const u8, marker: []const u8 }{
    .{ .label = "find_next_clump8", .marker = "pub fn findNextClump8(clump: *u8, addr: []const Word, nbits: usize, offset: usize) usize {" },
    .{ .label = "find_next_clump8_alias", .marker = "pub fn find_next_clump8(clump: *u8, addr: []const Word, nbits: usize, offset: usize) usize {" },
    .{ .label = "find_next_clump8_underscore", .marker = "pub fn _find_next_clump8(clump: *u8, addr: []const Word, nbits: usize, offset: usize) usize {" },
    .{ .label = "find_first_clump8", .marker = "pub fn findFirstClump8(clump: *u8, addr: []const Word, nbits: usize) usize {" },
    .{ .label = "find_first_clump8_alias", .marker = "pub fn find_first_clump8(clump: *u8, addr: []const Word, nbits: usize) usize {" },
    .{ .label = "find_first_clump8_underscore", .marker = "pub fn _find_first_clump8(clump: *u8, addr: []const Word, nbits: usize) usize {" },
};

const REQUIRED_MANIFEST_SUMMARY_FRAGMENTS = [_][]const u8{
    "clump8",
    "getValue8()",
    "findLastBit()",
};

const REQUIRED_TEST_MARKERS = [_]struct { label: []const u8, marker: []const u8 }{
    .{ .label = "byte_alignment", .marker = "test \"clump8 scans align to the containing byte and return its value\" {" },
    .{ .label = "tail_reachable", .marker = "test \"clump8 scans keep tail bytes reachable from partial final words\" {" },
    .{ .label = "tail_mask", .marker = "test \"clump8 scans mask tail bits beyond nbits\" {" },
    .{ .label = "no_match_preserves_byte", .marker = "test \"clump8 scans leave the caller byte untouched when no set bit remains\" {" },
};

const TARGET = "tools/lib/find_bit.zig";

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
        for (REQUIRED_FUNCTION_MARKERS) |entry| {
            const count = guard.countOccurrences(text, entry.marker);
            if (count != 1) {
                const issue = try std.fmt.allocPrint(allocator, "{s}:expected=1:actual={d}", .{ entry.label, count });
                try failures.append(allocator, issue);
            }
        }
        for (REQUIRED_TEST_MARKERS) |entry| {
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
        for (REQUIRED_FUNCTION_MARKERS) |entry| {
            try content.appendSlice(allocator, entry.marker);
            try content.append(allocator, '\n');
        }
        for (REQUIRED_TEST_MARKERS) |entry| {
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
    try guard.printLine(io, "PHASE1_FIND_BIT_CLUMP_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
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
        try guard.printLine(io, "PHASE1_FIND_BIT_CLUMP_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE1_FIND_BIT_CLUMP_FUNCTION_MARKER_COUNT={d}", .{@as(usize, REQUIRED_FUNCTION_MARKERS.len)});
    try guard.printLine(io, "PHASE1_FIND_BIT_CLUMP_TEST_MARKER_COUNT={d}", .{@as(usize, REQUIRED_TEST_MARKERS.len)});
    try guard.printLine(io, "PHASE1_FIND_BIT_CLUMP_ALIAS_MARKER_COUNT={d}", .{@as(usize, REQUIRED_ALIAS_EXPECTATIONS.len)});
    try guard.printLine(io, "PHASE1_FIND_BIT_CLUMP_MANIFEST_FRAGMENT_COUNT={d}", .{@as(usize, REQUIRED_MANIFEST_SUMMARY_FRAGMENTS.len)});
    std.process.exit(0);
}
