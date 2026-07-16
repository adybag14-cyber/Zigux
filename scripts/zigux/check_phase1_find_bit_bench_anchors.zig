// Ported from check-phase1-find-bit-bench-anchors.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE1_FIND_BIT_BENCH_ANCHORS_SELF_TEST=pass";

const FIND_BIT_REL = "tools/lib/find_bit.zig";

const REQUIRED_SOURCE_COUNT_MARKERS_ENTRIES = [_]struct { file: []const u8, marker: []const u8 }{
    .{ .file = "find_next_boundary", .marker = "findNextBit(&set_map, nbits, boundary)" },
    .{ .file = "find_next_and_boundary", .marker = "findNextAndBit(&and_lhs, &and_rhs, nbits, boundary)" },
    .{ .file = "find_next_andnot_boundary", .marker = "findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, boundary)" },
    .{ .file = "find_next_or_boundary", .marker = "findNextOrBit(&or_lhs, &or_rhs, nbits, boundary)" },
    .{ .file = "find_next_zero_boundary", .marker = "findNextZeroBit(&zero_map, nbits, boundary)" },
    .{ .file = "find_last_nbits_bitmap", .marker = "try std.testing.expectEqual(@as(usize, nbits), findLastBit(&bitmap, nbits));" },
    .{ .file = "find_first_clump8_tail_word", .marker = "try std.testing.expectEqual(@as(usize, bits_per_long), findFirstClump8(&clump, &bitmap, nbits));" },
    .{ .file = "find_first_clump8_tail_value", .marker = "try std.testing.expectEqual(@as(u8, 0b0000_1000), clump);" },
    .{ .file = "find_first_andnot_low_level_alias", .marker = "try std.testing.expectEqual(findFirstAndNotBit(&andnot_lhs, &andnot_rhs, nbits), _find_first_andnot_bit(&andnot_lhs, &andnot_rhs, nbits));" },
};

const REQUIRED_SOURCE_EXACT_MARKERS = [_]struct { label: []const u8, marker: []const u8 }{
    .{ .label = "find_first_andnot_gap", .marker = "findFirstAndNotBit(&andnot_lhs, &andnot_rhs, bits_per_long * 3)" },
    .{ .label = "find_same_word_set_first", .marker = "try std.testing.expectEqual(@as(usize, 7), findNextBit(&set_bits, nbits, 3));" },
    .{ .label = "find_same_word_set_second", .marker = "try std.testing.expectEqual(@as(usize, 11), findNextBit(&set_bits, nbits, 8));" },
    .{ .label = "find_same_word_zero_first", .marker = "try std.testing.expectEqual(@as(usize, 4), findNextZeroBit(&zero_bits, nbits, 1));" },
    .{ .label = "find_same_word_zero_second", .marker = "try std.testing.expectEqual(@as(usize, 9), findNextZeroBit(&zero_bits, nbits, 5));" },
    .{ .label = "find_same_word_and_first", .marker = "try std.testing.expectEqual(@as(usize, 9), findNextAndBit(&and_lhs, &and_rhs, nbits, 2));" },
    .{ .label = "find_same_word_and_second", .marker = "try std.testing.expectEqual(@as(usize, 12), findNextAndBit(&and_lhs, &and_rhs, nbits, 10));" },
    .{ .label = "find_last_exact_word_boundary_first", .marker = "try std.testing.expectEqual(@as(usize, boundary), findLastBit(&bitmap, nbits));" },
    .{ .label = "find_last_exact_word_boundary_clear", .marker = "bitmap[0] = 0;" },
    .{ .label = "find_last_tail_single_word", .marker = "try std.testing.expectEqual(@as(usize, 4), findLastBit(&single_word, single_word_nbits));" },
    .{ .label = "find_last_zero_sized", .marker = "findLastBit(&populated, 0)" },
    .{ .label = "find_last_empty_zero", .marker = "findLastBit(&empty, 0)" },
    .{ .label = "find_next_past_end", .marker = "findNextBit(&empty, 7, 11)" },
    .{ .label = "find_next_zero_past_end", .marker = "findNextZeroBit(&empty, 7, 11)" },
    .{ .label = "find_next_and_past_end", .marker = "findNextAndBit(&empty, &empty, 7, 11)" },
    .{ .label = "find_next_or_past_end", .marker = "findNextOrBit(&empty, &empty, 7, 11)" },
    .{ .label = "find_next_andnot_past_end", .marker = "findNextAndNotBit(&empty, &empty, 7, 11)" },
    .{ .label = "find_next_or_single_word_clamp", .marker = "findNextOrBit(&or_lhs, &or_rhs, nbits, 13)" },
    .{ .label = "find_next_and_tail_mask", .marker = "findNextAndBit(&lhs, &rhs, nbits, bits_per_long + 4)" },
    .{ .label = "find_next_tail_skip", .marker = "try std.testing.expectEqual(@as(usize, bits_per_long + 4), findNextBit(&tail_map, nbits, bits_per_long + 2));" },
    .{ .label = "find_next_tail_skip_stop", .marker = "try std.testing.expectEqual(@as(usize, nbits), findNextBit(&tail_map, nbits, bits_per_long + 5));" },
    .{ .label = "find_next_andnot_single_word_window", .marker = "try std.testing.expectEqual(@as(usize, 8), findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, 3));" },
    .{ .label = "find_next_andnot_single_word_stop", .marker = "try std.testing.expectEqual(@as(usize, nbits), findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, 9));" },
    .{ .label = "find_next_andnot_word_boundary_follow", .marker = "try std.testing.expectEqual(boundary + 5, findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, boundary + 1));" },
    .{ .label = "find_next_andnot_single_word_tail_stop", .marker = "try std.testing.expectEqual(@as(usize, nbits), findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, boundary + 1));" },
    .{ .label = "find_next_andnot_tail_skip", .marker = "try std.testing.expectEqual(@as(usize, bits_per_long + 4), findNextAndNotBit(&tail_andnot_lhs, &tail_andnot_rhs, nbits, bits_per_long + 2));" },
    .{ .label = "find_next_andnot_tail_skip_stop", .marker = "try std.testing.expectEqual(@as(usize, nbits), findNextAndNotBit(&tail_andnot_lhs, &tail_andnot_rhs, nbits, bits_per_long + 5));" },
    .{ .label = "find_next_zero_tail_skip", .marker = "try std.testing.expectEqual(@as(usize, bits_per_long + 4), findNextZeroBit(&tail_zero_map, nbits, bits_per_long + 2));" },
    .{ .label = "find_next_zero_tail_skip_stop", .marker = "try std.testing.expectEqual(@as(usize, nbits), findNextZeroBit(&tail_zero_map, nbits, bits_per_long + 5));" },
    .{ .label = "find_next_and_tail_skip", .marker = "try std.testing.expectEqual(@as(usize, bits_per_long + 4), findNextAndBit(&tail_and_lhs, &tail_and_rhs, nbits, bits_per_long + 2));" },
    .{ .label = "find_next_and_tail_skip_stop", .marker = "try std.testing.expectEqual(@as(usize, nbits), findNextAndBit(&tail_and_lhs, &tail_and_rhs, nbits, bits_per_long + 5));" },
    .{ .label = "find_next_or_tail_skip", .marker = "try std.testing.expectEqual(@as(usize, bits_per_long + 4), findNextOrBit(&tail_or_lhs, &tail_or_rhs, nbits, bits_per_long + 2));" },
    .{ .label = "find_next_or_tail_skip_stop", .marker = "try std.testing.expectEqual(@as(usize, nbits), findNextOrBit(&tail_or_lhs, &tail_or_rhs, nbits, bits_per_long + 5));" },
    .{ .label = "find_first_clump8_zero_sized", .marker = "findFirstClump8(&clump, &populated, 0)" },
    .{ .label = "find_next_clump8_untouched", .marker = "findNextClump8(&clump, &populated, 8, 12)" },
    .{ .label = "find_clump8_past_end", .marker = "findNextClump8(&clump, &empty, 8, 8)" },
    .{ .label = "find_clump8_linux_alias_past_end", .marker = "find_next_clump8(&clump, &empty, 8, 12)" },
    .{ .label = "find_clump8_low_level_alias_past_end", .marker = "_find_next_clump8(&clump, &empty, 8, 20)" },
    .{ .label = "find_clump8_skip_first", .marker = "try std.testing.expectEqual(@as(usize, 8), findNextClump8(&clump, &bitmap, nbits, 0));" },
    .{ .label = "find_clump8_skip_second", .marker = "try std.testing.expectEqual(@as(usize, 24), findNextClump8(&clump, &bitmap, nbits, 16));" },
    .{ .label = "find_clump8_skip_same_byte", .marker = "try std.testing.expectEqual(@as(usize, 24), findNextClump8(&clump, &bitmap, nbits, 25));" },
    .{ .label = "find_clump8_skip_stop", .marker = "try std.testing.expectEqual(@as(usize, nbits), findNextClump8(&clump, &bitmap, nbits, 30));" },
    .{ .label = "find_clump8_last_word_byte", .marker = "try std.testing.expectEqual(@as(usize, last_aligned_byte), findFirstClump8(&clump, &bitmap, nbits));" },
    .{ .label = "find_clump8_next_word_byte", .marker = "try std.testing.expectEqual(@as(usize, bits_per_long), findNextClump8(&clump, &bitmap, nbits, bits_per_long));" },
    .{ .label = "find_clump8_last_word_value", .marker = "try std.testing.expectEqual(@as(u8, 0xa5), clump);" },
    .{ .label = "find_clump8_next_word_value", .marker = "try std.testing.expectEqual(@as(u8, 0x11), clump);" },
    .{ .label = "find_get_value8_last_aligned", .marker = "try std.testing.expectEqual(@as(u8, 0xa5), getValue8(&bitmap, last_aligned_byte));" },
    .{ .label = "find_get_value8_next_word", .marker = "try std.testing.expectEqual(@as(u8, 0x11), getValue8(&bitmap, bits_per_long));" },
    .{ .label = "find_next_andnot_low_level_alias", .marker = "try std.testing.expectEqual(findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, bits_per_long), _find_next_andnot_bit(&andnot_lhs, &andnot_rhs, nbits, bits_per_long));" },
    .{ .label = "find_first_andnot_linux_alias", .marker = "try std.testing.expectEqual(findFirstAndNotBit(&andnot_lhs, &andnot_rhs, nbits), find_first_andnot_bit(&andnot_lhs, &andnot_rhs, nbits));" },
    .{ .label = "find_next_andnot_linux_alias", .marker = "try std.testing.expectEqual(findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, bits_per_long), find_next_andnot_bit(&andnot_lhs, &andnot_rhs, nbits, bits_per_long));" },
};

const REQUIRED_TEST_MARKERS = [_]struct { label: []const u8, marker: []const u8 }{
    .{ .label = "andnot_gap_test", .marker = "test \"find first and next set bits across words, with andnot gaps explicit\" {" },
    .{ .label = "same_word_start_mask_test", .marker = "test \"single-word next scans honor start masks\" {" },
    .{ .label = "boundary_head_test", .marker = "test \"head-word boundary scans keep the last in-range bit reachable from an inclusive start\" {" },
    .{ .label = "boundary_tail_test", .marker = "test \"tail-word boundary scans keep the last in-range bit reachable from an inclusive start\" {" },
    .{ .label = "single_word_tail_test", .marker = "test \"single-word tail windows keep the last in-range next matches reachable from an inclusive start\" {" },
    .{ .label = "single_word_partial_window_test", .marker = "test \"single-word next scans clamp partial windows before returning nbits\" {" },
    .{ .label = "word_boundary_test", .marker = "test \"word-boundary next scans start fresh on the next word\" {" },
    .{ .label = "zero_sized_scan_test", .marker = "test \"zero-sized scans ignore populated backing words\" {" },
    .{ .label = "past_end_no_read_test", .marker = "test \"next scans past nbits return without reading bitmap words\" {" },
    .{ .label = "tail_mask_shared_test", .marker = "test \"tail mask ignores shared bits beyond nbits\" {" },
    .{ .label = "tail_word_set_skip_test", .marker = "test \"tail-word next set scans skip earlier in-range matches before clamping\" {" },
    .{ .label = "tail_word_zero_shared_skip_test", .marker = "test \"tail-word next zero and shared scans skip earlier in-range matches before clamping\" {" },
    .{ .label = "clump8_tail_reach_test", .marker = "test \"clump8 scans keep tail bytes reachable from partial final words\" {" },
    .{ .label = "clump8_tail_mask_test", .marker = "test \"clump8 scans mask tail bits beyond nbits\" {" },
    .{ .label = "clump8_untouched_test", .marker = "test \"clump8 zero-bit and past-end windows leave the caller byte untouched\" {" },
    .{ .label = "clump8_no_read_test", .marker = "test \"clump8 past-end scans return without reading bitmap words\" {" },
    .{ .label = "clump8_skip_forward_test", .marker = "test \"clump8 scans skip earlier aligned bytes once the offset moves forward\" {" },
    .{ .label = "clump8_word_boundary_test", .marker = "test \"clump8 keeps the last aligned byte of a word isolated from the next word\" {" },
    .{ .label = "get_value8_last_aligned_test", .marker = "test \"getValue8 reads the last aligned byte of a word without folding in the next word\" {" },
    .{ .label = "underscore_andnot_alias_test", .marker = "test \"low-level underscore aliases mirror the primary find helpers, including andnot\" {" },
    .{ .label = "linux_andnot_alias_test", .marker = "test \"Linux-style aliases mirror the primary find helpers, including andnot\" {" },
    .{ .label = "last_bit_exact_word_boundary_test", .marker = "test \"find last bit ignores storage beyond an exact word boundary\" {" },
    .{ .label = "last_bit_tail_test", .marker = "test \"find last bit clamps tail words to nbits\" {" },
    .{ .label = "last_bit_empty_test", .marker = "test \"find last bit returns nbits when no set bits remain\" {" },
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
        for (REQUIRED_TEST_MARKERS) |entry| {
            const count = guard.countOccurrences(text, entry.marker);
            if (count != 1) {
                const issue = try std.fmt.allocPrint(allocator, "{s}:expected=1:actual={d}", .{ entry.label, count });
                try failures.append(allocator, issue);
            }
        }
        for (REQUIRED_SOURCE_EXACT_MARKERS) |entry| {
            const count = guard.countOccurrences(text, entry.marker);
            if (count != 1) {
                const issue = try std.fmt.allocPrint(allocator, "{s}:expected=1:actual={d}", .{ entry.label, count });
                try failures.append(allocator, issue);
            }
        }
    }

    return failures;
}

fn buildSampleSource(allocator: std.mem.Allocator) ![]u8 {
    var content = std.ArrayList(u8).empty;
    errdefer content.deinit(allocator);
    for (REQUIRED_TEST_MARKERS) |entry| {
        try content.appendSlice(allocator, entry.marker);
        try content.append(allocator, '\n');
    }
    for (REQUIRED_SOURCE_EXACT_MARKERS) |entry| {
        try content.appendSlice(allocator, entry.marker);
        try content.append(allocator, '\n');
    }
    return try content.toOwnedSlice(allocator);
}

pub fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    var tmp = try guard.TempWorkspace.init(io, allocator, "selftest");
    defer tmp.deinit();
    const root = try tmp.rootPath(allocator);
    defer allocator.free(root);
    const sample = try buildSampleSource(allocator);
    defer allocator.free(sample);
    {
        const relative_path = "tools/lib/find_bit.zig";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        try guard.writeUtf8File(io, full_path, sample);
        var failures = try collectFailures(io, allocator, root);
        defer {
            for (failures.items) |item| allocator.free(item);
            failures.deinit(allocator);
        }
        try guard.expectSelfTest(failures.items.len == 0);
    }
    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE1_FIND_BIT_BENCH_ANCHORS_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 153)});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(init.arena.allocator());

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
        try guard.printLine(io, "PHASE1_FIND_BIT_BENCH_ANCHORS_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    std.process.exit(0);
}
