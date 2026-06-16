// Ported from check-phase1-string-strlcat-anchors.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE1_STRING_STRLCAT_ANCHORS_SELF_TEST=pass";

const REQUIRED_SYMBOLS = [_][]const u8{
    "pub fn strlcat(dest: []u8, src: []const u8) usize {",
    "const src_len = cStringLen(src);",
    "const dest_len = strnlen(dest, dest.len);",
    "return dest.len + src_len;",
    "const copy_len = @min(src_len, dest.len - dest_len - 1);",
    "dest[dest_len + copy_len] = 0;",
    "return dest_len + src_len;",
};

const REQUIRED_TEST_ANCHORS = [_][]const u8{
    "test \"strlcat appends within the destination size and reports the attempted length\"",
    "test \"strlcat truncates with a terminator and keeps the full attempted length\"",
    "test \"strlcat treats an unterminated destination as full\"",
    "test \"strlcat handles a zero-length destination buffer\"",
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
        const relative_path = STRING_HELPER_REL;
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            try guard.appendMissingFileIssue(allocator, &failures, relative_path);
            return failures;
        }
        const text = try guard.readUtf8File(io, allocator, full_path);
        defer allocator.free(text);
        for (REQUIRED_SYMBOLS) |symbol| {
            const count = guard.countOccurrences(text, symbol);
            if (count != 1) {
                const issue = try std.fmt.allocPrint(allocator, "string_strlcat_symbol:{s}:expected=1:actual={d}", .{ symbol, count });
                try failures.append(allocator, issue);
            }
        }
        for (REQUIRED_TEST_ANCHORS) |anchor| {
            const count = guard.countOccurrences(text, anchor);
            if (count != 1) {
                const issue = try std.fmt.allocPrint(allocator, "string_strlcat_anchor:{s}:expected=1:actual={d}", .{ anchor, count });
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
        try guard.writeUtf8File(io, full_path, "\n");
    }
    var failures = try collectFailures(io, allocator, root);
    defer {
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
    }
    try guard.expectSelfTest(failures.items.len == 0);
    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE1_STRING_STRLCAT_ANCHORS_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
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
        try guard.printLine(io, "PHASE1_STRING_STRLCAT_ANCHORS_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    std.process.exit(0);
}
