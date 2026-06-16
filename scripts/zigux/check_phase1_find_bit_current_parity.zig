// Ported from check-phase1-find-bit-current-parity.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE1_FIND_BIT_CURRENT_PARITY_SELF_TEST=pass";

const BUILD_MARKERS = [_][]const u8{
    "const find_bit_module = b.createModule(.{",
    ".root_source_file = b.path(\"../../tools/lib/find_bit.zig\"),",
    "root_module.addImport(\"find_bit\", find_bit_module);",
    "const phase1_helpers = b.step(",
    "\"phase1-helpers\",",
};

const BUILD_REL = "zigux/tests/phase1_helpers_build.zig";

const EXPECTED_PARITY_KEYS = [_][]const u8{
    "bits_per_long",
    "first",
    "next_after_6",
    "next_after_word",
    "first_zero",
    "next_zero",
    "first_and",
    "next_and",
    "last",
};

const FIXTURE_REL = "zigux/tests/fixtures/phase1_helpers.json";

const HELPER_ANCHORS = [_][]const u8{
    "test \"find first and next set bits across words, with andnot gaps explicit\"",
    "test \"single-word next scans honor start masks\"",
    "test \"tail-word next set scans skip earlier in-range matches before clamping\"",
    "test \"tail-word next zero and shared scans skip earlier in-range matches before clamping\"",
    "test \"find last bit clamps tail words to nbits\"",
    "test \"low-level underscore aliases mirror the primary find helpers, including andnot\"",
    "test \"Linux-style aliases mirror the primary find helpers, including andnot\"",
};

const HELPER_REL = "tools/lib/find_bit.zig";

const MANIFEST_REL = "zigux/tests/fixtures/phase1_helper_manifest.json";

const NEXT_SAFE_STEP = "If this helper lane reopens, keep find_bit parked unless a fresh reread finds drift in the manifest-backed same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, getValue8(), findLastBit(), underscore-alias, Linux-style alias coverage including the shipped andnot scan entry points, or tail-word skip anchors, or committed shared replay drift in the live `bits_per_long`, `first`, `next_after_6`, `next_after_word`, `first_zero`, `next_zero`, `first_and`, `next_and`, or `last` fixture keys; do not reopen older saved validator cues or neighboring helper families.";

const REPLAY_MARKERS = [_][]const u8{
    "const nbits = fixture.find_bit.bits_per_long * 2 + 8;",
    "try std.testing.expectEqual(fixture.find_bit.first, find_bit.findFirstBit(&bitmap_a, nbits));",
    "try std.testing.expectEqual(fixture.find_bit.next_after_6, find_bit.findNextBit(&bitmap_a, nbits, 6));",
    "try std.testing.expectEqual(fixture.find_bit.next_after_word, find_bit.findNextBit(&bitmap_a, nbits, fixture.find_bit.bits_per_long));",
    "try std.testing.expectEqual(fixture.find_bit.first_zero, find_bit.findFirstZeroBit(&bitmap_b, nbits));",
    "try std.testing.expectEqual(fixture.find_bit.next_zero, find_bit.findNextZeroBit(&bitmap_b, nbits, fixture.find_bit.bits_per_long));",
    "try std.testing.expectEqual(fixture.find_bit.first_and, find_bit.findFirstAndBit(&bitmap_a, &bitmap_and, nbits));",
    "try std.testing.expectEqual(fixture.find_bit.next_and, find_bit.findNextAndBit(&bitmap_a, &bitmap_and, nbits, fixture.find_bit.bits_per_long));",
    "try std.testing.expectEqual(fixture.find_bit.last, find_bit.findLastBit(&bitmap_a, nbits));",
};

const REPLAY_REL = "zigux/tests/phase1_helpers.zig";

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
        const relative_path = "zigux/tests/phase1_helpers_build.zig";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
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
        const relative_path = "zigux/tests/phase1_helpers.zig";
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
        for (REPLAY_MARKERS) |marker| {
            const count = guard.countOccurrences(text, marker);
            if (count != 1) {
                const issue = try std.fmt.allocPrint(allocator, "{s}:expected_once:actual_count={d}:{s}", .{ relative_path, count, marker });
                try failures.append(allocator, issue);
            }
        }
    }

    {
        const relative_path = "zigux/tests/phase1_helpers_build.zig";
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
        for (BUILD_MARKERS) |marker| {
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
        const relative_path = "zigux/tests/phase1_helpers.zig";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        var content = std.ArrayList(u8).empty;
        defer content.deinit(allocator);
        for (REPLAY_MARKERS) |marker| {
            try content.appendSlice(allocator, marker);
            try content.append(allocator, '\n');
        }
        try guard.writeUtf8File(io, full_path, content.items);
    }
    {
        const relative_path = "zigux/tests/phase1_helpers_build.zig";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        var content = std.ArrayList(u8).empty;
        defer content.deinit(allocator);
        for (BUILD_MARKERS) |marker| {
            try content.appendSlice(allocator, marker);
            try content.append(allocator, '\n');
        }
        try guard.writeUtf8File(io, full_path, content.items);
    }
    {
        const relative_path = "zigux/tests/fixtures/phase1_helper_manifest.json";
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
    try guard.printLine(io, "PHASE1_FIND_BIT_CURRENT_PARITY_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
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
        try guard.printLine(io, "PHASE1_FIND_BIT_CURRENT_PARITY_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    std.process.exit(0);
}
