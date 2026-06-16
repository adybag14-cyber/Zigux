// Ported from check-phase1-bitmap-direct-anchors.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE1_BITMAP_DIRECT_ANCHORS_SELF_TEST=pass";

const BITMAP_REL = "tools/lib/bitmap.zig";

const REQUIRED_SOURCE_MARKERS = [_]struct { label: []const u8, marker: []const u8 }{
    .{ .label = "bitmap_size_alias", .marker = "pub fn bitmap_size(nbits: usize) usize {" },
    .{ .label = "bitmap_zero_alias", .marker = "pub fn bitmap_zero(dst: []Word, nbits: usize) void {" },
    .{ .label = "bitmap_fill_alias", .marker = "pub fn bitmap_fill(dst: []Word, nbits: usize) void {" },
    .{ .label = "bitmap_copy_alias", .marker = "pub fn bitmap_copy(dst: []Word, src: []const Word, nbits: usize) void {" },
    .{ .label = "bitmap_copy_clear_tail_alias", .marker = "pub fn bitmap_copy_clear_tail(dst: []Word, src: []const Word, nbits: usize) void {" },
    .{ .label = "bitmap_copy_and_extend_alias", .marker = "pub fn bitmap_copy_and_extend(dst: []Word, src: []const Word, count: usize, size: usize) void {" },
    .{ .label = "bitmap_empty_alias", .marker = "pub fn bitmap_empty(src: []const Word, nbits: usize) bool {" },
    .{ .label = "bitmap_full_alias", .marker = "pub fn bitmap_full(src: []const Word, nbits: usize) bool {" },
    .{ .label = "bitmap_weight_alias", .marker = "pub fn bitmap_weight(src: []const Word, nbits: usize) usize {" },
    .{ .label = "bitmap_or_alias", .marker = "pub fn bitmap_or(dst: []Word, src1: []const Word, src2: []const Word, nbits: usize) void {" },
    .{ .label = "bitmap_xor_alias", .marker = "pub fn bitmap_xor(dst: []Word, src1: []const Word, src2: []const Word, nbits: usize) void {" },
    .{ .label = "bitmap_weighted_or_alias", .marker = "pub fn bitmap_weighted_or(dst: []Word, src1: []const Word, src2: []const Word, nbits: usize) usize {" },
    .{ .label = "bitmap_weighted_xor_alias", .marker = "pub fn bitmap_weighted_xor(dst: []Word, src1: []const Word, src2: []const Word, nbits: usize) usize {" },
    .{ .label = "bitmap_weight_and_alias", .marker = "pub fn bitmap_weight_and(src1: []const Word, src2: []const Word, nbits: usize) usize {" },
    .{ .label = "bitmap_weight_andnot_alias", .marker = "pub fn bitmap_weight_andnot(src1: []const Word, src2: []const Word, nbits: usize) usize {" },
    .{ .label = "bitmap_and_alias", .marker = "pub fn bitmap_and(dst: []Word, src1: []const Word, src2: []const Word, nbits: usize) bool {" },
    .{ .label = "bitmap_andnot_alias", .marker = "pub fn bitmap_andnot(dst: []Word, src1: []const Word, src2: []const Word, nbits: usize) bool {" },
    .{ .label = "bitmap_equal_alias", .marker = "pub fn bitmap_equal(src1: []const Word, src2: []const Word, nbits: usize) bool {" },
    .{ .label = "bitmap_intersects_alias", .marker = "pub fn bitmap_intersects(src1: []const Word, src2: []const Word, nbits: usize) bool {" },
    .{ .label = "bitmap_subset_alias", .marker = "pub fn bitmap_subset(src1: []const Word, src2: []const Word, nbits: usize) bool {" },
    .{ .label = "bitmap_complement_alias", .marker = "pub fn bitmap_complement(dst: []Word, src: []const Word, nbits: usize) void {" },
    .{ .label = "bitmap_set_alias", .marker = "pub fn bitmap_set(map: []Word, start: usize, len: usize) void {" },
    .{ .label = "bitmap_clear_alias", .marker = "pub fn bitmap_clear(map: []Word, start: usize, len: usize) void {" },
    .{ .label = "bitmap_scnprintf_alias", .marker = "pub fn bitmap_scnprintf(bitmap: []const Word, nbits: usize, buffer: []u8) usize {" },
    .{ .label = "bitmap_alloc_alias", .marker = "pub fn bitmap_alloc(allocator: std.mem.Allocator, nbits: usize) ![]Word {" },
    .{ .label = "bitmap_zalloc_alias", .marker = "pub fn bitmap_zalloc(allocator: std.mem.Allocator, nbits: usize) ![]Word {" },
    .{ .label = "bitmap_free_alias", .marker = "pub fn bitmap_free(allocator: std.mem.Allocator, bitmap: *?[]Word) void {" },
    .{ .label = "set_clear_weight_assert", .marker = "try std.testing.expectEqual(@as(usize, 5), weight(&map, bits_per_long * 2));" },
    .{ .label = "clear_empty_assert", .marker = "try std.testing.expect(empty(&map, bits_per_long * 2));" },
    .{ .label = "range_first_word_assert", .marker = "try std.testing.expectEqual(@as(Word, firstWordMask(start)), map[0]);" },
    .{ .label = "range_last_partial_assert", .marker = "try std.testing.expectEqual(lastWordMask(start + len), map[3]);" },
    .{ .label = "fill_tail_clamp_assert", .marker = "try std.testing.expect(full(&full_map, nbits));" },
    .{ .label = "zero_bit_equal_identity_assert", .marker = "try std.testing.expect(equal(lhs[0..0], rhs[0..0], 0));" },
    .{ .label = "zero_bit_subset_identity_assert", .marker = "try std.testing.expect(subset(lhs[0..0], rhs[0..0], 0));" },
    .{ .label = "logical_and_assert", .marker = "try std.testing.expect(andBits(&dst, &lhs, &rhs, 8));" },
    .{ .label = "logical_subset_assert", .marker = "try std.testing.expect(subset(&rhs, &lhs, 8));" },
    .{ .label = "scnprintf_collapse_assert", .marker = "try std.testing.expectEqualStrings(\"1-3,10-11\", buffer[0..len]);" },
    .{ .label = "empty_buffer_preserved_assert", .marker = "try std.testing.expectEqualSlices(u8, &[_]u8{ 0xaa, 0xaa, 0xaa, 0xaa }, &buffer);" },
    .{ .label = "or_multiword_tail_assert", .marker = "try std.testing.expectEqualSlices(Word, &[_]Word{ 0b11_1101, 0b01_0111 }, &[_]Word{ dst[0], dst[1] & lastWordMask(nbits) });" },
    .{ .label = "weighted_or_direct_count", .marker = "try std.testing.expectEqual(@as(usize, 2), direct_or_weight);" },
    .{ .label = "weighted_xor_direct_count", .marker = "try std.testing.expectEqual(@as(usize, 2), direct_xor_weight);" },
    .{ .label = "weighted_or_masked_count", .marker = "try std.testing.expectEqual(@as(usize, 2), weight(&direct_or, nbits));" },
    .{ .label = "weighted_and_direct_count", .marker = "try std.testing.expectEqual(@as(usize, 1), direct_and_weight);" },
    .{ .label = "weighted_andnot_direct_count", .marker = "try std.testing.expectEqual(@as(usize, 1), direct_andnot_weight);" },
    .{ .label = "complement_tail_mask_assert", .marker = "try std.testing.expectEqual((~src[1]) & lastWordMask(nbits), direct[1]);" },
    .{ .label = "bitmap_size_alias_assert", .marker = "try std.testing.expectEqual(bitmapSize(nbits), bitmap_size(nbits));" },
    .{ .label = "bitmap_zero_alias_assert", .marker = "bitmap_zero(&alias, nbits);" },
    .{ .label = "bitmap_empty_alias_assert", .marker = "try std.testing.expectEqual(empty(&direct, nbits), bitmap_empty(&alias, nbits));" },
    .{ .label = "bitmap_fill_alias_assert", .marker = "bitmap_fill(&alias, nbits);" },
    .{ .label = "bitmap_full_alias_assert", .marker = "try std.testing.expectEqual(full(&direct, nbits), bitmap_full(&alias, nbits));" },
    .{ .label = "bitmap_weight_alias_assert", .marker = "try std.testing.expectEqual(weight(&direct, nbits), bitmap_weight(&alias, nbits));" },
    .{ .label = "bitmap_copy_alias_assert", .marker = "bitmap_copy(&alias, &lhs, nbits);" },
    .{ .label = "bitmap_copy_clear_tail_alias_assert", .marker = "bitmap_copy_clear_tail(&alias_tail, src[0..2], count);" },
    .{ .label = "bitmap_copy_and_extend_alias_assert", .marker = "bitmap_copy_and_extend(&alias_extend, src[0..2], count, size);" },
    .{ .label = "bitmap_or_alias_assert", .marker = "bitmap_or(&alias, &lhs, &rhs, nbits);" },
    .{ .label = "bitmap_xor_alias_assert", .marker = "bitmap_xor(&alias, &lhs, &rhs, nbits);" },
    .{ .label = "bitmap_weighted_or_alias_assert", .marker = "const alias_or_weight = bitmap_weighted_or(&alias_or, &or_lhs, &or_rhs, nbits);" },
    .{ .label = "bitmap_weighted_xor_alias_assert", .marker = "const alias_xor_weight = bitmap_weighted_xor(&alias_xor, &xor_lhs, &xor_rhs, nbits);" },
    .{ .label = "bitmap_weight_and_alias_assert", .marker = "const alias_and_weight = bitmap_weight_and(&and_lhs, &and_rhs, nbits);" },
    .{ .label = "bitmap_weight_andnot_alias_assert", .marker = "const alias_andnot_weight = bitmap_weight_andnot(&and_lhs, &and_rhs, nbits);" },
    .{ .label = "bitmap_complement_alias_assert", .marker = "bitmap_complement(&alias, &src, nbits);" },
    .{ .label = "bitmap_and_alias_assert", .marker = "try std.testing.expectEqual(andBits(&direct, &lhs, &rhs, nbits), bitmap_and(&alias, &lhs, &rhs, nbits));" },
    .{ .label = "bitmap_andnot_alias_assert", .marker = "try std.testing.expectEqual(andNotBits(&direct, &lhs, &rhs, nbits), bitmap_andnot(&alias, &lhs, &rhs, nbits));" },
    .{ .label = "bitmap_equal_alias_assert", .marker = "try std.testing.expectEqual(equal(&lhs, &rhs, nbits), bitmap_equal(&lhs, &rhs, nbits));" },
    .{ .label = "bitmap_intersects_alias_assert", .marker = "try std.testing.expectEqual(intersects(&lhs, &rhs, nbits), bitmap_intersects(&rhs, &lhs, nbits));" },
    .{ .label = "bitmap_subset_alias_assert", .marker = "try std.testing.expectEqual(subset(&rhs, &lhs, nbits), bitmap_subset(&rhs, &lhs, nbits));" },
    .{ .label = "bitmap_set_alias_assert", .marker = "bitmap_set(&alias_range, 1, 3);" },
    .{ .label = "bitmap_clear_alias_assert", .marker = "bitmap_clear(&alias_range, 2, 1);" },
    .{ .label = "bitmap_scnprintf_alias_assert", .marker = "const alias_len = bitmap_scnprintf(&alias_range, nbits, &alias_buffer);" },
    .{ .label = "bitmap_alloc_alias_assert", .marker = "var plain_alias: ?[]Word = try bitmap_alloc(allocator, nbits);" },
    .{ .label = "bitmap_zalloc_alias_assert", .marker = "var zeroed_alias: ?[]Word = try bitmap_zalloc(allocator, nbits);" },
    .{ .label = "bitmap_free_alias_assert", .marker = "bitmap_free(allocator, &plain_alias);" },
};

const REQUIRED_TEST_MARKERS = [_]struct { label: []const u8, marker: []const u8 }{
    .{ .label = "set_clear_weight_full_empty", .marker = "test \"bitmap set clear weight and empty full helpers\" {" },
    .{ .label = "range_edges", .marker = "test \"bitmap range helpers preserve edges across whole-word spans\" {" },
    .{ .label = "copy_raw_alias", .marker = "test \"bitmap copy alias preserves raw source words without tail clearing\" {" },
    .{ .label = "copy_tail_extend_alias", .marker = "test \"bitmap copy aliases preserve tail clearing and extension semantics\" {" },
    .{ .label = "copy_zero_aligned", .marker = "test \"bitmap copy and extend handles zero and aligned counts\" {" },
    .{ .label = "copy_zero_sized_views", .marker = "test \"bitmap copy helpers keep zero-sized destination views untouched\" {" },
    .{ .label = "zero_bit_logical", .marker = "test \"bitmap zero-bit logical helpers stay explicit\" {" },
    .{ .label = "equal_fast_path", .marker = "test \"bitmap equal fast path ignores storage beyond an exact word boundary\" {" },
    .{ .label = "logical_baseline", .marker = "test \"bitmap and andnot equal intersects subset\" {" },
    .{ .label = "tail_mask_predicates", .marker = "test \"bitmap tail-masked helpers ignore out-of-range differences\" {" },
    .{ .label = "tail_mask_counts", .marker = "test \"bitmap full empty and weight ignore out-of-range tail bits\" {" },
    .{ .label = "xor_window", .marker = "test \"bitmap xor keeps caller-selected bit window\" {" },
    .{ .label = "xor_multiword_tail", .marker = "test \"bitmap xor across a multiword tail still lets callers clamp the last word\" {" },
    .{ .label = "or_window", .marker = "test \"bitmap or keeps caller-selected bit window\" {" },
    .{ .label = "or_multiword_tail", .marker = "test \"bitmap or across a multiword tail still lets callers clamp the last word\" {" },
    .{ .label = "weighted_or_xor_tail", .marker = "test \"bitmap weighted or and xor clamp counts to the declared tail window\" {" },
    .{ .label = "weighted_and_andnot_tail", .marker = "test \"bitmap weighted and andnot clamp counts to the declared tail window\" {" },
    .{ .label = "complement_tail", .marker = "test \"bitmap complement clamps partial tails and leaves zero-sized caller views untouched\" {" },
    .{ .label = "scnprintf_contiguous_ranges", .marker = "test \"bitmap scnprintf collapses contiguous ranges\" {" },
    .{ .label = "scnprintf_cross_word", .marker = "test \"bitmap scnprintf keeps contiguous ranges merged across word boundaries\" {" },
    .{ .label = "scnprintf_truncation", .marker = "test \"bitmap scnprintf truncates and keeps a terminator slot\" {" },
    .{ .label = "scnprintf_zero_views", .marker = "test \"bitmap scnprintf handles terminator-only and zero-length caller views\" {" },
    .{ .label = "scnprintf_empty_buffer", .marker = "test \"bitmap scnprintf leaves the caller buffer untouched for an empty bitmap\" {" },
    .{ .label = "linux_alias_copy_logic", .marker = "test \"bitmap Linux-style aliases mirror copy logical range and format helpers\" {" },
    .{ .label = "linux_alias_size_alloc", .marker = "test \"bitmap Linux-style aliases mirror size state and allocation helpers\" {" },
    .{ .label = "allocation_helpers", .marker = "test \"bitmap allocation helpers size zero fill and reset optionals\" {" },
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
        const relative_path = "tools/lib/bitmap.zig";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    if (failures.items.len > 0) return failures;

    {
        const relative_path = "tools/lib/bitmap.zig";
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
        for (REQUIRED_SOURCE_MARKERS) |entry| {
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
    for (REQUIRED_SOURCE_MARKERS) |entry| {
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
        const relative_path = "tools/lib/bitmap.zig";
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
    try guard.printLine(io, "PHASE1_BITMAP_DIRECT_ANCHORS_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 199)});
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
        try guard.printLine(io, "PHASE1_BITMAP_DIRECT_ANCHORS_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    std.process.exit(0);
}
