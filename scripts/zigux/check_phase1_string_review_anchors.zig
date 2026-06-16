// Ported from check-phase1-string-review-anchors.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE1_STRING_REVIEW_ANCHORS_SELF_TEST=pass";

const MANIFEST = "zigux/tests/fixtures/phase1_helper_manifest.json";

const REQUIRED_FUNCTION_MARKERS = [_][]const u8{
    "pub fn strHasPrefix(str: []const u8, prefix: []const u8) usize {",
    "pub fn strHasSuffix(str: []const u8, suffix: []const u8) usize {",
    "pub fn sysfsMatchString(haystack: []const []const u8, needle: []const u8) ?usize {",
    "pub fn matchString(haystack: []const []const u8, needle: []const u8) ?usize {",
    "pub fn memparse(text: []const u8) MemparseResult {",
    "pub fn kbasename(path: []const u8) []const u8 {",
    "pub fn strnchr(buf: []const u8, count: usize, needle: u8) ?usize {",
    "pub fn strnlen(buf: []const u8, count: usize) usize {",
    "pub fn strnchrNul(buf: []const u8, count: usize, needle: u8) usize {",
};

const REQUIRED_TEST_MARKERS = [_][]const u8{
    "test \"strHasPrefix returns the matched prefix length with C-string semantics\" {",
    "test \"strHasSuffix returns the matched suffix length with C-string semantics\" {",
    "test \"strstarts mirrors the header-level prefix helper\" {",
    "test \"strEndsWith honors C-string boundaries\" {",
    "test \"sysfsStreq treats trailing newline and NUL as equivalent\" {",
    "test \"sysfs_streq mirrors sysfsStreq newline and NUL equivalence\" {",
    "test \"sysfsMatchString finds newline-aware matches and preserves first-match order\" {",
    "test \"sysfs_match_string mirrors sysfsMatchString for empty and matched lists\" {",
    "test \"matchString finds C-string matches and preserves first-match order\" {",
    "test \"match_string mirrors matchString for empty and matched lists\" {",
    "test \"memparse handles decimal hexadecimal octal and suffixes\" {",
    "test \"memparse keeps original rest when sign is not followed by digits\" {",
    "test \"memparse saturates signed overflow instead of trapping\" {",
    "test \"memparse clamps explicit positive signed overflow\" {",
    "test \"memparse keeps signed values and their trailing rest aligned\" {",
    "test \"memparse consumes suffix after saturation\" {",
    "test \"memparse applies suffixes before signed clamping\" {",
    "test \"kbasename returns the final path component with C-string semantics\" {",
    "test \"phase 1 string trim helpers stop at embedded NUL after trailing whitespace\" {",
    "test \"memchrInv follows the earliest dirty byte as long buffers change\" {",
    "test \"strchr mirrors full-length C-string searches\" {",
    "test \"strrchr finds the last in-range match with C-string semantics\" {",
    "test \"strpbrk finds the first accepted byte with C-string semantics\" {",
    "test \"strnchr honors count and C-string boundaries\" {",
    "test \"strnlen honors count and C-string boundaries\" {",
    "test \"strnchrNul returns the first match, NUL, or count boundary\" {",
};

const TARGET = "tools/lib/string.zig";

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
        for (REQUIRED_FUNCTION_MARKERS) |marker| {
            if (std.mem.indexOf(u8, text, marker) == null) {
                const issue = try std.fmt.allocPrint(allocator, "missing_marker:{s}", .{marker});
                try failures.append(allocator, issue);
            }
        }
    }

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
        for (REQUIRED_TEST_MARKERS) |marker| {
            if (std.mem.indexOf(u8, text, marker) == null) {
                const issue = try std.fmt.allocPrint(allocator, "missing_marker:{s}", .{marker});
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
        for (REQUIRED_FUNCTION_MARKERS) |marker| {
            try content.appendSlice(allocator, marker);
            try content.append(allocator, '\n');
        }
        try guard.writeUtf8File(io, full_path, content.items);
    }
    {
        const relative_path = "tools/lib/string.zig";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        var content = std.ArrayList(u8).empty;
        defer content.deinit(allocator);
        for (REQUIRED_TEST_MARKERS) |marker| {
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
    try guard.printLine(io, "PHASE1_STRING_REVIEW_ANCHORS_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
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
        try guard.printLine(io, "PHASE1_STRING_REVIEW_ANCHORS_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE1_STRING_REVIEW_ANCHORS_FUNCTION_MARKER_COUNT={d}", .{@as(usize, REQUIRED_FUNCTION_MARKERS.len)});
    try guard.printLine(io, "PHASE1_STRING_REVIEW_ANCHORS_TEST_MARKER_COUNT={d}", .{@as(usize, REQUIRED_TEST_MARKERS.len)});
    std.process.exit(0);
}
