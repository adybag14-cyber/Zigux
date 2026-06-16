// Ported from check-phase1-bitmap-review-packet.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE1_BITMAP_REVIEW_PACKET_SELF_TEST=pass";

const BITMAP_HELPER = "tools/lib/bitmap.zig";

const BITMAP_REL = "tools/lib/bitmap.zig";

const CLOSURE_REL = "Documentation/zigux/phase1-closure.md";

const FIXTURE_REL = "zigux/tests/fixtures/phase1_helpers.json";

const MANIFEST_REL = "zigux/tests/fixtures/phase1_helper_manifest.json";

const REQUIRED_CLOSURE_MARKERS = [_][]const u8{
    "PHASE1_BITMAP_DIRECT_REVIEW=helper-local bitmap direct anchors stay explicit",
    "PHASE1_BITMAP_UNIT_REVIEW=bitmap multiword-tail xorBits behavior still lets callers clamp",
    "PHASE1_BITMAP_EMPTY_UNIT_REVIEW=bitmap_scnprintf leaves a non-empty caller buffer untouched",
    "PHASE1_BITMAP_FINAL_PARTIAL_WORD_REVIEW=helper-local bitmap final partial-word proof stays explicit",
    "PHASE1_BITMAP_LINUX_ALIAS_REVIEW=helper-local bitmap Linux-style alias proof stays explicit",
};

const REQUIRED_FIXTURE_KEYS = [_][]const u8{
    "weight",
    "scnprintf",
    "truncated_scnprintf_len",
    "truncated_scnprintf",
    "terminator_only_scnprintf_len",
    "terminator_only_nul",
    "zero_length_scnprintf_len",
    "alloc_words",
    "zalloc_words",
    "zalloc_values",
    "copy_values",
    "copy_clear_tail_values",
    "copy_and_extend_values",
    "complement_values",
    "and_result",
    "and_values",
    "andnot_result",
    "andnot_values",
    "or_values",
    "xor_values",
    "partial_xor_nbits",
    "partial_xor_masked_values",
    "equal",
    "intersects",
    "subset",
    "range_after_set",
    "range_after_clear",
    "full_after_fill",
    "empty_after_zero",
};

const REQUIRED_MANIFEST_FIELDS = [_]struct { key: []const u8, expected: []const u8 }{
    .{ .key = "first_word_boundary_anchor", .expected = "test \"bitmap range helpers preserve edges across whole-word spans\"" },
    .{ .key = "final_partial_word_anchor", .expected = "test \"bitmap range helpers preserve edges across whole-word spans\"" },
    .{ .key = "fill_tail_clamp_anchor", .expected = "test \"bitmap full empty and weight ignore out-of-range tail bits\"" },
    .{ .key = "equal_fast_path_anchor", .expected = "test \"bitmap equal fast path ignores storage beyond an exact word boundary\"" },
    .{ .key = "predicate_tail_mask_anchor", .expected = "test \"bitmap tail-masked helpers ignore out-of-range differences\"" },
    .{ .key = "or_window_anchor", .expected = "test \"bitmap or keeps caller-selected bit window\"" },
    .{ .key = "or_multiword_tail_anchor", .expected = "test \"bitmap or across a multiword tail still lets callers clamp the last word\"" },
    .{ .key = "weighted_tail_count_anchor", .expected = "test \"bitmap weighted or and xor clamp counts to the declared tail window\"" },
    .{ .key = "scnprintf_cross_word_anchor", .expected = "test \"bitmap scnprintf keeps contiguous ranges merged across word boundaries\"" },
    .{ .key = "empty_buffer_anchor", .expected = "test \"bitmap scnprintf leaves the caller buffer untouched for an empty bitmap\"" },
    .{ .key = "copy_raw_alias_anchor", .expected = "test \"bitmap copy alias preserves raw source words without tail clearing\"" },
    .{ .key = "zero_bit_noop_anchor", .expected = "test \"bitmap zero-bit logical helpers stay explicit\"" },
    .{ .key = "zero_bit_binary_identity_anchor", .expected = "test \"bitmap zero-bit logical helpers stay explicit\"" },
    .{ .key = "linux_alias_anchor", .expected = "test \"bitmap Linux-style aliases mirror copy logical range and format helpers\"" },
};

const REQUIRED_HELPER_TESTS = [_][]const u8{
    "test \"bitmap range helpers preserve edges across whole-word spans\"",
    "test \"bitmap copy alias preserves raw source words without tail clearing\"",
    "test \"bitmap copy aliases preserve tail clearing and extension semantics\"",
    "test \"bitmap copy and extend handles zero and aligned counts\"",
    "test \"bitmap copy helpers keep zero-sized destination views untouched\"",
    "test \"bitmap zero-bit logical helpers stay explicit\"",
    "test \"bitmap equal fast path ignores storage beyond an exact word boundary\"",
    "test \"bitmap tail-masked helpers ignore out-of-range differences\"",
    "test \"bitmap full empty and weight ignore out-of-range tail bits\"",
    "test \"bitmap xor keeps caller-selected bit window\"",
    "test \"bitmap xor across a multiword tail still lets callers clamp the last word\"",
    "test \"bitmap or keeps caller-selected bit window\"",
    "test \"bitmap or across a multiword tail still lets callers clamp the last word\"",
    "test \"bitmap weighted or and xor clamp counts to the declared tail window\"",
    "test \"bitmap weighted and andnot clamp counts to the declared tail window\"",
    "test \"bitmap complement clamps partial tails and leaves zero-sized caller views untouched\"",
    "test \"bitmap scnprintf keeps contiguous ranges merged across word boundaries\"",
    "test \"bitmap scnprintf handles terminator-only and zero-length caller views\"",
    "test \"bitmap scnprintf leaves the caller buffer untouched for an empty bitmap\"",
    "test \"bitmap Linux-style aliases mirror copy logical range and format helpers\"",
    "test \"bitmap Linux-style aliases mirror size state and allocation helpers\"",
    "test \"bitmap allocation helpers size zero fill and reset optionals\"",
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

    const bitmap_text = blk: {
        const full_path = try guard.joinPath(allocator, root, BITMAP_REL);
        defer allocator.free(full_path);
        break :blk guard.readUtf8File(io, allocator, full_path) catch |err| switch (err) {
            guard.GuardError.IOError => {
                try guard.appendMissingFileIssue(allocator, &failures, BITMAP_REL);
                return failures;
            },
            else => return err,
        };
    };
    defer allocator.free(bitmap_text);

    for (REQUIRED_HELPER_TESTS) |marker| {
        const needle = try std.fmt.allocPrint(allocator, "{s} {{", .{marker});
        defer allocator.free(needle);
        const label = try std.fmt.allocPrint(allocator, "{s}:{s}", .{ BITMAP_REL, marker });
        defer allocator.free(label);
        try guard.appendExactOccurrenceIssue(allocator, &failures, bitmap_text, label, needle);
    }

    const manifest_text = blk: {
        const full_path = try guard.joinPath(allocator, root, MANIFEST_REL);
        defer allocator.free(full_path);
        break :blk guard.readUtf8File(io, allocator, full_path) catch |err| switch (err) {
            guard.GuardError.IOError => {
                try guard.appendMissingFileIssue(allocator, &failures, MANIFEST_REL);
                return failures;
            },
            else => return err,
        };
    };
    defer allocator.free(manifest_text);

    const fixture_text = blk: {
        const full_path = try guard.joinPath(allocator, root, FIXTURE_REL);
        defer allocator.free(full_path);
        break :blk guard.readUtf8File(io, allocator, full_path) catch |err| switch (err) {
            guard.GuardError.IOError => {
                try guard.appendMissingFileIssue(allocator, &failures, FIXTURE_REL);
                return failures;
            },
            else => return err,
        };
    };
    defer allocator.free(fixture_text);

    const closure_text = blk: {
        const full_path = try guard.joinPath(allocator, root, CLOSURE_REL);
        defer allocator.free(full_path);
        break :blk guard.readUtf8File(io, allocator, full_path) catch |err| switch (err) {
            guard.GuardError.IOError => {
                try guard.appendMissingFileIssue(allocator, &failures, CLOSURE_REL);
                return failures;
            },
            else => return err,
        };
    };
    defer allocator.free(closure_text);

    const manifest_parsed = try guard.parseJsonValue(allocator, manifest_text);
    defer manifest_parsed.deinit();
    const fixture_parsed = try guard.parseJsonValue(allocator, fixture_text);
    defer fixture_parsed.deinit();

    if (manifest_parsed.value == .object) {
        const helpers = manifest_parsed.value.object.get("helpers");
        var has_bitmap_helper = false;
        if (helpers) |value| {
            if (value == .array) {
                for (value.array.items) |item| {
                    if (item == .string and std.mem.eql(u8, item.string, BITMAP_HELPER)) has_bitmap_helper = true;
                }
            }
        }
        if (!has_bitmap_helper) {
            const issue = try std.fmt.allocPrint(allocator, "{s}:helpers:missing:{s}", .{ MANIFEST_REL, BITMAP_HELPER });
            try failures.append(allocator, issue);
        }

        const review_root = guard.nestedJsonValue(manifest_parsed.value, &[_][]const u8{"review_anchors"});
        const bitmap_anchors = if (review_root) |value| guard.nestedJsonValue(value, &[_][]const u8{BITMAP_HELPER}) else null;
        if (bitmap_anchors == null or bitmap_anchors.? != .object) {
            const issue = try std.fmt.allocPrint(allocator, "{s}:review_anchors:{s}:missing", .{ MANIFEST_REL, BITMAP_HELPER });
            try failures.append(allocator, issue);
        } else {
            const anchors_object = bitmap_anchors.?.object;
            const helper_tests = anchors_object.get("helper_test_anchors");
            if (helper_tests == null or helper_tests.? != .array) {
                const issue = try std.fmt.allocPrint(allocator, "{s}:helper_test_anchors:missing", .{MANIFEST_REL});
                try failures.append(allocator, issue);
            } else {
                for (REQUIRED_HELPER_TESTS) |marker| {
                    var found = false;
                    for (helper_tests.?.array.items) |item| {
                        if (item == .string and std.mem.eql(u8, item.string, marker)) found = true;
                    }
                    if (!found) {
                        const issue = try std.fmt.allocPrint(allocator, "{s}:helper_test_anchors:missing:{s}", .{ MANIFEST_REL, marker });
                        try failures.append(allocator, issue);
                    }
                }
            }
            for (REQUIRED_MANIFEST_FIELDS) |field| {
                const actual = anchors_object.get(field.key);
                const ok = if (actual) |value| value == .string and std.mem.eql(u8, value.string, field.expected) else false;
                if (!ok) {
                    const issue = try std.fmt.allocPrint(allocator, "{s}:{s}:drift", .{ MANIFEST_REL, field.key });
                    try failures.append(allocator, issue);
                }
            }
        }
    }

    if (fixture_parsed.value == .object) {
        const bitmap_fixture = guard.nestedJsonValue(fixture_parsed.value, &[_][]const u8{"bitmap"});
        if (bitmap_fixture == null or bitmap_fixture.? != .object) {
            const issue = try std.fmt.allocPrint(allocator, "{s}:bitmap:missing", .{FIXTURE_REL});
            try failures.append(allocator, issue);
        } else {
            const bitmap_object = bitmap_fixture.?.object;
            for (REQUIRED_FIXTURE_KEYS) |key| {
                if (bitmap_object.get(key) == null) {
                    const issue = try std.fmt.allocPrint(allocator, "{s}:bitmap:{s}:missing", .{ FIXTURE_REL, key });
                    try failures.append(allocator, issue);
                }
            }
        }
    }

    for (REQUIRED_CLOSURE_MARKERS) |marker| {
        const label = try std.fmt.allocPrint(allocator, "{s}:{s}", .{ CLOSURE_REL, marker });
        defer allocator.free(label);
        try guard.appendExactOccurrenceIssue(allocator, &failures, closure_text, label, marker);
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
        for (REQUIRED_CLOSURE_MARKERS) |marker| {
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
    try guard.printLine(io, "PHASE1_BITMAP_REVIEW_PACKET_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
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
        try guard.printLine(io, "PHASE1_BITMAP_REVIEW_PACKET_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE1_BITMAP_REVIEW_PACKET_FIXTURE_KEY_COUNT={d}", .{@as(usize, REQUIRED_FIXTURE_KEYS.len)});
    try guard.printLine(io, "PHASE1_BITMAP_REVIEW_PACKET_HELPER_TEST_COUNT={d}", .{@as(usize, REQUIRED_HELPER_TESTS.len)});
    std.process.exit(0);
}
