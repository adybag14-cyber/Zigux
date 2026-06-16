// Ported from check-phase1-string-search-anchors.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE1_STRING_SEARCH_ANCHORS_SELF_TEST=pass";

const EXPECTED_SEARCH_SYMBOLS = [_][]const u8{
    "pub fn strstr(buf: []const u8, needle: []const u8) ?usize {",
    "pub fn strnstr(buf: []const u8, needle: []const u8, count: usize) ?usize {",
    "pub fn strchr(buf: []const u8, needle: u8) ?usize {",
    "pub fn strrchr(buf: []const u8, needle: u8) ?usize {",
    "pub fn strpbrk(buf: []const u8, accept: []const u8) ?usize {",
    "pub fn strspn(buf: []const u8, accept: []const u8) usize {",
    "pub fn strcspn(buf: []const u8, reject: []const u8) usize {",
    "pub fn strnchr(buf: []const u8, count: usize, needle: u8) ?usize {",
    "pub fn strnchrNul(buf: []const u8, count: usize, needle: u8) usize {",
    "pub fn strnchrnul(buf: []const u8, count: usize, needle: u8) usize {",
    "pub fn strchrNul(buf: []const u8, needle: u8) usize {",
    "pub fn strchrnul(buf: []const u8, needle: u8) usize {",
};

const EXPECTED_SEARCH_TEST_ANCHORS = [_][]const u8{
    "test \"strstr mirrors full-length C-string substring searches\"",
    "test \"strnstr honors count and C-string boundaries\"",
    "test \"strchr mirrors full-length C-string searches\"",
    "test \"strrchr finds the last in-range match with C-string semantics\"",
    "test \"strchr and strrchr return the terminator index when searching for NUL\"",
    "test \"strpbrk finds the first accepted byte with C-string semantics\"",
    "test \"strspn counts the accepted prefix with C-string semantics\"",
    "test \"strcspn counts until the first rejected byte with C-string semantics\"",
    "test \"strnchr honors count and C-string boundaries\"",
    "test \"strnchr treats the NUL terminator as searchable within the count window\"",
    "test \"strnchrNul returns the first match, NUL, or count boundary\"",
    "test \"strchrNul and strchrnul return the first match or terminator boundary\"",
};

const SEARCH_REVIEW_MARKERS = [_][]const u8{
    "strstr(\"abc\", &[_]u8{ 'b', 0, 'x' })",
    "strnstr(&[_]u8{ 'a', 0, 'b', 'c' }, \"bc\", 4)",
    "strnchr(\"abc\", 3, 0)",
    "strnchrNul(&[_]u8{ 'a', 0, 'b' }, 3, 'z')",
    "strchrNul(&[_]u8{ 'a', 0, 'b' }, 'z')",
};

const STRING_HELPER_REL = "tools/lib/string.zig";

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
        const relative_path = "tools/lib/string.zig";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    if (failures.items.len > 0) return failures;

    {
        const relative_path = "tools/lib/string.zig";
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
        for (SEARCH_REVIEW_MARKERS) |marker| {
            const count = guard.countOccurrences(text, marker);
            if (count != 1) {
                const issue = try std.fmt.allocPrint(allocator, "{s}:expected_once:actual_count={d}:{s}", .{ relative_path, count, marker });
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
        const relative_path = "tools/lib/string.zig";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        var content = std.ArrayList(u8).empty;
        defer content.deinit(allocator);
        for (SEARCH_REVIEW_MARKERS) |marker| {
            try content.appendSlice(allocator, marker);
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
    try guard.printLine(io, "PHASE1_STRING_SEARCH_ANCHORS_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
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
        try guard.printLine(io, "PHASE1_STRING_SEARCH_ANCHORS_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    std.process.exit(0);
}
