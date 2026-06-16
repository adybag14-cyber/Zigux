// Ported from check-phase1-string-shared-surfaces.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE1_STRING_SHARED_SURFACES_SELF_TEST=pass";

const EXPECTED_HELPERS_MARKERS = [_][]const u8{
    "try std.testing.expectEqual(fixture.string.strtobool_y, try string.strtobool(\"y\"));",
    "try std.testing.expectEqual(fixture.string.strtobool_on, try string.strtobool(\"on\"));",
    "try std.testing.expectEqual(fixture.string.strtobool_zero, try string.strtobool(\"0\"));",
    "try std.testing.expectEqual(fixture.string.strtobool_off, try string.strtobool(\"off\"));",
    "try std.testing.expectEqual(fixture.string.strtobool_invalid, @as(u8, @intCast(@intFromError(error.Invalid))));",
    "try std.testing.expectEqual(fixture.string.strlcpy_len, string.strlcpy(copied[0..], \"hello\"));",
    "try std.testing.expectEqualStrings(fixture.string.strlcpy_buffer, copied[0 .. copied.len - 1]);",
    "try std.testing.expectEqualStrings(fixture.string.skip_spaces, string.skipSpaces(\" \\t hello\"));",
    "try std.testing.expectEqualStrings(fixture.string.trim_spaces, string.trimSpaces(trim_buf[0..]));",
    "try std.testing.expectEqualStrings(fixture.string.remove_spaces, string.removeSpaces(remove_buf[0..]));",
    "try std.testing.expectEqual(fixture.string.replace_char_end, string.replaceChar(replace_buf[0..], '-', '_'));",
    "try std.testing.expectEqualStrings(fixture.string.replace_char, replace_buf[0 .. replace_buf.len - 1]);",
    "try std.testing.expectEqual(fixture.string.replace_char_cstr_end, string.replaceChar(replace_cstr_buf[0..], '-', '_'));",
    "try std.testing.expectEqualSlices(u8, fixture.string.replace_char_cstr_bytes, replace_cstr_buf[0..]);",
    "try std.testing.expectEqual(@as(?usize, fixture.string.memchr_inv_index), string.memchrInv(&[_]u8{ 'x', 'x', 'x', 'x', 'y' }, 'x'));",
    "try std.testing.expectEqual(fixture.string.memchr_inv_none, string.memchrInv(&[_]u8{ 'x', 'x', 'x' }, 'x') == null);",
};

const EXPECTED_SMOKE_MARKERS = [_][]const u8{
    "try std.testing.expectEqual(@as(usize, 5), string.strlcat(appended[0..], \"all\"));",
    "try std.testing.expectEqual(@as(usize, 6), string.strlcat(truncated_append[0..], \"cdef\"));",
    "try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(&sysfs, \"auto\"));",
    "try std.testing.expect(string.sysfs_streq(\"auto\\n\", \"auto\"));",
    "try std.testing.expectEqual(@as(?usize, 1), string.matchString(&lookup, \"manual\"));",
    "try std.testing.expectEqual(@as(?usize, 3), string.match_string(&lookup, &lookup_cstr));",
    "try std.testing.expectEqual(@as(?usize, 1), string.strnchr(&counted, counted.len, 'b'));",
    "try std.testing.expectEqual(@as(usize, 2), string.strnchrNul(&counted, counted.len, 'z'));",
    "try std.testing.expectEqual(@as(usize, 1), string.strnchrnul(&counted, counted.len, 'b'));",
    "try std.testing.expectEqual(@as(usize, 4), string.strspn(\"abba!\", \"ab\"));",
    "try std.testing.expectEqual(@as(usize, 1), string.strchrNul(&terminator_clamped, 'z'));",
    "try std.testing.expectEqual(@as(usize, 1), string.strchrnul(&terminator_clamped, 'z'));",
};

const FIXTURE_REL = "zigux/tests/fixtures/phase1_helpers.json";

const HELPERS_REL = "zigux/tests/phase1_helpers.zig";

const SMOKE_REL = "zigux/tests/phase1_host_tools_smoke.zig";

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
        const relative_path = "zigux/tests/phase1_host_tools_smoke.zig";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    if (failures.items.len > 0) return failures;

    {
        const relative_path = "zigux/tests/phase1_host_tools_smoke.zig";
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
        for (EXPECTED_SMOKE_MARKERS) |marker| {
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
        const relative_path = "zigux/tests/phase1_host_tools_smoke.zig";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        var content = std.ArrayList(u8).empty;
        defer content.deinit(allocator);
        for (EXPECTED_SMOKE_MARKERS) |marker| {
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
    try guard.printLine(io, "PHASE1_STRING_SHARED_SURFACES_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
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
        try guard.printLine(io, "PHASE1_STRING_SHARED_SURFACES_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    std.process.exit(0);
}
