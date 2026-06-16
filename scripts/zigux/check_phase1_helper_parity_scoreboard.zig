// Ported from check-phase1-helper-parity-scoreboard.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE1_HELPER_PARITY_SCOREBOARD_SELF_TEST=pass";

const DIRECT_CHECKER_REL = "scripts\\zigux/check_phase1_direct_helper_parity.zig";

const EXPECTED_DIRECT_CHECKER_MARKERS = [_][]const u8{
    "PHASE1_DIRECT_HELPER_PARITY=pass",
    "EXPECTED_DIRECT_HELPERS",
    "EXPECTED_MANIFEST_KEYS",
    "SOURCE_MARKERS",
};

const EXPECTED_DIRECT_HELPERS = [_][]const u8{
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
};

const EXPECTED_FIXTURE_SECTION = [_]struct { label: []const u8, marker: []const u8 }{
    .{ .label = "tools/lib/bitmap.zig", .marker = "bitmap" },
    .{ .label = "tools/lib/find_bit.zig", .marker = "find_bit" },
    .{ .label = "tools/lib/rbtree.zig", .marker = "rbtree" },
    .{ .label = "tools/lib/string.zig", .marker = "string" },
};

const EXPECTED_PARITY_CHECKER_MARKERS = [_][]const u8{
    "PHASE1_PARITY=pass",
    "PHASE1_PARITY_HELPER_COUNT=",
    "PHASE1_PARITY_DIRECT_REVIEW_HELPER_COUNT=",
    "PHASE1_PARITY_BLOCKER_IDS=",
    "EXPECTED_DIRECT_REVIEW_ANCHOR_EXACT_FIELDS",
    "EXPECTED_DIRECT_REVIEW_ANCHOR_SUBSET_FIELDS",
};

const EXPECTED_PARKED_HELPERS = [_][]const u8{
    "tools/lib/argv_split.zig",
    "tools/lib/cmdline.zig",
    "tools/lib/ctype.zig",
    "tools/lib/hweight.zig",
    "tools/lib/list_sort.zig",
    "tools/lib/slab.zig",
    "tools/lib/str_error_r.zig",
    "tools/lib/vsprintf.zig",
    "tools/lib/zalloc.zig",
};

const EXPECTED_PARKED_REVIEW_FIELDS = [_][]const u8{
    "helper_test_anchors",
    "next_safe_step_note",
};

const EXPECTED_REVIEW_FIXTURE_FIELDS_ENTRIES = [_]struct { file: []const u8, marker: []const u8 }{
    .{ .file = "tools/lib/bitmap.zig", .marker = "parity_fixture_keys" },
    .{ .file = "tools/lib/bitmap.zig", .marker = "shared_logical_fixture_keys" },
    .{ .file = "tools/lib/bitmap.zig", .marker = "shared_range_fixture_keys" },
    .{ .file = "tools/lib/bitmap.zig", .marker = "partial_xor_review_fields" },
    .{ .file = "tools/lib/find_bit.zig", .marker = "tail_clamp_fixture_keys" },
    .{ .file = "tools/lib/find_bit.zig", .marker = "tail_inclusive_boundary_fixture_keys" },
    .{ .file = "tools/lib/rbtree.zig", .marker = "parity_fixture_keys" },
    .{ .file = "tools/lib/rbtree.zig", .marker = "cached_leftmost_fixture_keys" },
    .{ .file = "tools/lib/rbtree.zig", .marker = "cached_root_transition_fixture_keys" },
    .{ .file = "tools/lib/string.zig", .marker = "parity_fixture_keys" },
};

const FIXTURE_REL = "zigux/tests/fixtures/phase1_helpers.json";

const MANIFEST_REL = "zigux/tests/fixtures/phase1_helper_manifest.json";

const PARITY_CHECKER_REL = "scripts\\zigux/check_phase1_parity.zig";

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
        const relative_path = "zigux/tests/fixtures/phase1_helper_manifest.json";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    if (failures.items.len > 0) return failures;

    {
        const relative_path = "zigux/tests/fixtures/phase1_helper_manifest.json";
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
        for (EXPECTED_PARITY_CHECKER_MARKERS) |marker| {
            if (std.mem.indexOf(u8, text, marker) == null) {
                const issue = try std.fmt.allocPrint(allocator, "missing_marker:{s}", .{marker});
                try failures.append(allocator, issue);
            }
        }
    }

    {
        const relative_path = "zigux/tests/fixtures/phase1_helper_manifest.json";
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
        for (EXPECTED_DIRECT_CHECKER_MARKERS) |marker| {
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
        const relative_path = "zigux/tests/fixtures/phase1_helper_manifest.json";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        var content = std.ArrayList(u8).empty;
        defer content.deinit(allocator);
        for (EXPECTED_PARITY_CHECKER_MARKERS) |marker| {
            try content.appendSlice(allocator, marker);
            try content.append(allocator, '\n');
        }
        try guard.writeUtf8File(io, full_path, content.items);
    }
    {
        const relative_path = "zigux/tests/fixtures/phase1_helper_manifest.json";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        var content = std.ArrayList(u8).empty;
        defer content.deinit(allocator);
        for (EXPECTED_DIRECT_CHECKER_MARKERS) |marker| {
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
    try guard.printLine(io, "PHASE1_HELPER_PARITY_SCOREBOARD_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
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
        try guard.printLine(io, "PHASE1_HELPER_PARITY_SCOREBOARD_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE1_HELPER_PARITY_SCOREBOARD_DIRECT_HELPER_COUNT={d}", .{@as(usize, EXPECTED_DIRECT_HELPERS.len)});
    try guard.printLine(io, "PHASE1_HELPER_PARITY_SCOREBOARD_PARKED_HELPER_COUNT={d}", .{@as(usize, EXPECTED_PARKED_HELPERS.len)});
    std.process.exit(0);
}
