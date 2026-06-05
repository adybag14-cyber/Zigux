const std = @import("std");

const fixture_bytes = @embedFile("fixtures/phase1_helpers.json");

const BitmapFixture = struct {
    weight: u8,
    scnprintf: []const u8,
    truncated_scnprintf_len: u8,
    truncated_scnprintf: []const u8,
    terminator_only_scnprintf_len: u8,
    terminator_only_nul: u8,
    zero_length_scnprintf_len: u8,
    alloc_words: u8,
    zalloc_words: u8,
    zalloc_values: []const u64,
    copy_values: []const u64,
    copy_clear_tail_values: []const u64,
    copy_and_extend_values: []const u64,
    complement_values: []const u64,
    and_result: bool,
    and_values: []const u64,
    andnot_result: bool,
    andnot_values: []const u64,
    or_values: []const u64,
    xor_values: []const u64,
    partial_xor_nbits: u8,
    partial_xor_masked_values: []const u64,
    equal: bool,
    intersects: bool,
    subset: bool,
    range_after_set: []const u64,
    range_after_clear: []const u64,
    full_after_fill: bool,
    empty_after_zero: bool,
};

const Fixture = struct {
    bitmap: BitmapFixture,
};

fn loadFixture() !std.json.Parsed(Fixture) {
    return std.json.parseFromSlice(Fixture, std.testing.allocator, fixture_bytes, .{
        .ignore_unknown_fields = true,
    });
}

fn expectSliceEqual(comptime T: type, expected: []const T, actual: []const T) !void {
    try std.testing.expectEqualSlices(T, expected, actual);
}

fn expectNeedleAfter(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierNeedle;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterNeedle;
    try std.testing.expect(earlier_index < later_index);
}

test "phase 1 bitmap fixture pins render and allocation counters" {
    var parsed = try loadFixture();
    defer parsed.deinit();
    const bitmap = parsed.value.bitmap;

    try std.testing.expectEqual(@as(u8, 5), bitmap.weight);
    try std.testing.expectEqualStrings("1-3,66-67", bitmap.scnprintf);
    try std.testing.expectEqual(@as(u8, 7), bitmap.truncated_scnprintf_len);
    try std.testing.expectEqualStrings("1-3,66-", bitmap.truncated_scnprintf);
    try std.testing.expectEqual(@as(u8, 0), bitmap.terminator_only_scnprintf_len);
    try std.testing.expectEqual(@as(u8, 0), bitmap.terminator_only_nul);
    try std.testing.expectEqual(@as(u8, 0), bitmap.zero_length_scnprintf_len);
    try std.testing.expectEqual(@as(u8, 3), bitmap.alloc_words);
    try std.testing.expectEqual(@as(u8, 3), bitmap.zalloc_words);
    try expectSliceEqual(u64, &.{ 0, 0, 0 }, bitmap.zalloc_values);
}

test "phase 1 bitmap fixture pins word-operation results" {
    var parsed = try loadFixture();
    defer parsed.deinit();
    const bitmap = parsed.value.bitmap;

    try expectSliceEqual(u64, &.{ std.math.maxInt(u64), std.math.maxInt(u64) }, bitmap.copy_values);
    try expectSliceEqual(u64, &.{ std.math.maxInt(u64), 31 }, bitmap.copy_clear_tail_values);
    try expectSliceEqual(u64, &.{ std.math.maxInt(u64), 31, 0 }, bitmap.copy_and_extend_values);
    try expectSliceEqual(u64, &.{ 18446744073709551605, 29 }, bitmap.complement_values);
    try std.testing.expect(bitmap.and_result);
    try expectSliceEqual(u64, &.{ 10, 0 }, bitmap.and_values);
    try std.testing.expect(bitmap.andnot_result);
    try expectSliceEqual(u64, &.{ 4, 0 }, bitmap.andnot_values);
    try expectSliceEqual(u64, &.{ 14, 0 }, bitmap.or_values);
    try expectSliceEqual(u64, &.{ 4, 0 }, bitmap.xor_values);
}

test "phase 1 bitmap fixture pins range and section boundaries" {
    var parsed = try loadFixture();
    defer parsed.deinit();
    const bitmap = parsed.value.bitmap;

    try std.testing.expectEqual(@as(u8, 4), bitmap.partial_xor_nbits);
    try expectSliceEqual(u64, &.{14}, bitmap.partial_xor_masked_values);
    try std.testing.expect(bitmap.equal);
    try std.testing.expect(bitmap.intersects);
    try std.testing.expect(bitmap.subset);
    try expectSliceEqual(u64, &.{ 14, 12, 0 }, bitmap.range_after_set);
    try expectSliceEqual(u64, &.{ 0, 0, 0 }, bitmap.range_after_clear);
    try std.testing.expect(bitmap.full_after_fill);
    try std.testing.expect(bitmap.empty_after_zero);

    try expectNeedleAfter(fixture_bytes, "\"find_bit\"", "\"bitmap\"");
    try expectNeedleAfter(fixture_bytes, "\"bitmap\"", "\"string\"");
    try std.testing.expectEqual(@as(usize, 1), std.mem.count(u8, fixture_bytes, "\"bitmap\""));
}
