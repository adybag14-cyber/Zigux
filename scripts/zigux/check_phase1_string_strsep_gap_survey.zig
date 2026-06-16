// Ported from check-phase1-string-strsep-gap-survey.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE1_STRING_STRSEP_SURVEY_SELF_TEST=pass";

const STRING_HELPER_REL = "tools/lib/string.zig";

const STRSEP_SYMBOL = "pub fn strsep(cursor: *?[]u8, delimiters: []const u8) ?[]u8 {";

const STRSEP_TESTS = [_][]const u8{
    "test \"strsep splits mutable C strings and preserves empty tokens\"",
    "test \"strsep respects C-string delimiter and source boundaries\"",
    "test \"strsep with an empty delimiter set returns the remaining C string once\"",
};

const SURVEY_MARKERS = [_][]const u8{
    "`PHASE1_STRING_STRSEP_SURVEY_STATUS=packet-gap-recorded`",
    "`PHASE1_STRING_STRSEP_ROADMAP_SCOPE=tools/lib/string.zig host-side helper`",
    "`PHASE1_STRING_STRSEP_LEDGER_SCOPE=Phase 1 helper train`",
    "`PHASE1_STRING_STRSEP_SOURCE_HELPER=pub fn strsep(cursor: *?[]u8, delimiters: []const u8) ?[]u8 {`",
    "`PHASE1_STRING_STRSEP_REVIEW_PACKET_GAP=scripts\\zigux/check_phase1_string_review_packet.zig does not yet list the strsep symbol or its three direct helper tests in EXPECTED_STRING_SOURCE_SYMBOLS or EXPECTED_HELPER_TEST_ANCHORS`",
    "`PHASE1_STRING_STRSEP_NEXT_STEP=when the string review packet reopens, add strsep to the existing packet checker and manifest review anchors, then retire or narrow this gap survey`",
};

const SURVEY_REL = "Documentation/zigux/phase1-string-strsep-gap-survey.md";

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
        const relative_path = "Documentation/zigux/phase1-string-strsep-gap-survey.md";
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
        for (SURVEY_MARKERS) |marker| {
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
        const relative_path = "Documentation/zigux/phase1-string-strsep-gap-survey.md";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        var content = std.ArrayList(u8).empty;
        defer content.deinit(allocator);
        for (SURVEY_MARKERS) |marker| {
            try content.appendSlice(allocator, marker);
            try content.append(allocator, '\n');
        }
        try guard.writeUtf8File(io, full_path, content.items);
    }
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
    try guard.printLine(io, "PHASE1_STRING_STRSEP_SURVEY_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
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
        try guard.printLine(io, "PHASE1_STRING_STRSEP_SURVEY_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    std.process.exit(0);
}
