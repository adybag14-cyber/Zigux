const std = @import("std");
const bitmap = @import("bitmap");

const fixture_bytes = @embedFile("fixtures/phase1_helpers.json");

const Fixture = struct {
    bitmap: struct {
        weight: usize,
        scnprintf: []const u8,
        truncated_scnprintf_len: usize,
        truncated_scnprintf: []const u8,
        terminator_only_scnprintf_len: usize,
        terminator_only_nul: u8,
        zero_length_scnprintf_len: usize,
        alloc_words: usize,
        zalloc_words: usize,
        zalloc_values: []const u64,
        copy_values: []const u64,
        copy_clear_tail_values: []const u64,
        copy_and_extend_values: []const u64,
        and_result: bool,
        and_values: []const u64,
        andnot_result: bool,
        andnot_values: []const u64,
        or_values: []const u64,
        xor_values: []const u64,
        partial_xor_nbits: usize,
        partial_xor_masked_values: []const u64,
        equal: bool,
        intersects: bool,
        subset: bool,
        range_after_set: []const u64,
        range_after_clear: []const u64,
        full_after_fill: bool,
        empty_after_zero: bool,
    },
};

fn loadFixture() !std.json.Parsed(Fixture) {
    return std.json.parseFromSlice(Fixture, std.testing.allocator, fixture_bytes, .{
        .ignore_unknown_fields = true,
    });
}

fn expectWordSliceMatchesFixture(actual: []const bitmap.Word, expected: []const u64) !void {
    try std.testing.expectEqual(expected.len, actual.len);
    for (expected, actual) |expected_word, actual_word| {
        try std.testing.expectEqual(
            @as(bitmap.Word, @intCast(expected_word)),
            actual_word,
        );
    }
}

test "phase1 bitmap fixture replay covers committed parity fields not exercised by the shared helper replay" {
    var parsed = try loadFixture();
    defer parsed.deinit();
    const fixture = parsed.value.bitmap;

    const allocator = std.testing.allocator;
    const nbits = bitmap.bits_per_long + 5;

    var allocated: ?[]bitmap.Word = try bitmap.bitmapAlloc(allocator, nbits);
    defer bitmap.bitmapFree(allocator, &allocated);
    try std.testing.expectEqual(fixture.alloc_words, allocated.?.len);

    var zeroed: ?[]bitmap.Word = try bitmap.bitmapZalloc(allocator, nbits);
    defer bitmap.bitmapFree(allocator, &zeroed);
    try std.testing.expectEqual(fixture.zalloc_words, zeroed.?.len);
    try expectWordSliceMatchesFixture(zeroed.?, fixture.zalloc_values);

    const copy_count = bitmap.bits_per_long + 33;
    const copy_src = [_]bitmap.Word{
        ~@as(bitmap.Word, 0),
        ~@as(bitmap.Word, 0),
        0,
    };
    var copy_dst = [_]bitmap.Word{ 0, 0, 0 };
    bitmap.copy(&copy_dst, copy_src[0..2], copy_count);
    try expectWordSliceMatchesFixture(copy_dst[0..2], fixture.copy_values);

    const tail_count = bitmap.bits_per_long + 5;
    var tail_dst = [_]bitmap.Word{ 0, 0 };
    bitmap.copyClearTail(&tail_dst, copy_src[0..2], tail_count);
    try expectWordSliceMatchesFixture(&tail_dst, fixture.copy_clear_tail_values);

    const extend_size = bitmap.bits_per_long * 3;
    var extend_dst = [_]bitmap.Word{
        ~@as(bitmap.Word, 0),
        ~@as(bitmap.Word, 0),
        ~@as(bitmap.Word, 0),
    };
    bitmap.copyAndExtend(&extend_dst, copy_src[0..2], tail_count, extend_size);
    try expectWordSliceMatchesFixture(&extend_dst, fixture.copy_and_extend_values);

    const lhs = [_]bitmap.Word{ 0b1110, 0 };
    const rhs = [_]bitmap.Word{ 0b1010, 0 };
    var logical_dst = [_]bitmap.Word{ 0, 0 };
    try std.testing.expectEqual(fixture.and_result, bitmap.andBits(&logical_dst, &lhs, &rhs, 8));
    try expectWordSliceMatchesFixture(&logical_dst, fixture.and_values);
    try std.testing.expectEqual(fixture.andnot_result, bitmap.andNotBits(&logical_dst, &lhs, &rhs, 8));
    try expectWordSliceMatchesFixture(&logical_dst, fixture.andnot_values);
    bitmap.orBits(&logical_dst, &lhs, &rhs, 8);
    try expectWordSliceMatchesFixture(&logical_dst, fixture.or_values);
    bitmap.xorBits(&logical_dst, &lhs, &rhs, 8);
    try expectWordSliceMatchesFixture(&logical_dst, fixture.xor_values);
    try std.testing.expectEqual(fixture.equal, bitmap.equal(&lhs, &[_]bitmap.Word{ 0b1110, 0 }, 8));
    try std.testing.expectEqual(fixture.intersects, bitmap.intersects(&lhs, &rhs, 8));
    try std.testing.expectEqual(fixture.subset, bitmap.subset(&rhs, &lhs, 8));

    const partial_lhs = [_]bitmap.Word{0b1_1111};
    const partial_rhs = [_]bitmap.Word{0b1_0001};
    var partial_dst = [_]bitmap.Word{0};
    bitmap.xorBits(&partial_dst, &partial_lhs, &partial_rhs, fixture.partial_xor_nbits);
    const partial_mask = bitmap.lastWordMask(fixture.partial_xor_nbits);
    try expectWordSliceMatchesFixture(
        &[_]bitmap.Word{partial_dst[0] & partial_mask},
        fixture.partial_xor_masked_values,
    );

    var range_map = [_]bitmap.Word{ 0, 0, 0 };
    bitmap.setRange(&range_map, 1, 3);
    bitmap.setRange(&range_map, 7, 1);
    bitmap.setRange(&range_map, 10, 2);
    try std.testing.expectEqual(fixture.weight, bitmap.weight(&range_map, 130));
    try expectWordSliceMatchesFixture(&range_map, fixture.range_after_set);

    var rendered: [32]u8 = undefined;
    const rendered_len = bitmap.scnprintf(&range_map, 130, &rendered);
    try std.testing.expectEqualStrings(fixture.scnprintf, rendered[0..rendered_len]);

    var truncated = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa };
    const truncated_len = bitmap.scnprintf(&range_map, 130, &truncated);
    try std.testing.expectEqual(fixture.truncated_scnprintf_len, truncated_len);
    try std.testing.expectEqualStrings(fixture.truncated_scnprintf, truncated[0..truncated_len]);

    var terminator_only = [_]u8{0xaa};
    const terminator_only_len = bitmap.scnprintf(&range_map, 130, terminator_only[0..1]);
    try std.testing.expectEqual(fixture.terminator_only_scnprintf_len, terminator_only_len);
    try std.testing.expectEqual(fixture.terminator_only_nul, terminator_only[0]);

    var zero_length_backing = [_]u8{0xbb};
    const zero_length_len = bitmap.scnprintf(&range_map, 130, zero_length_backing[0..0]);
    try std.testing.expectEqual(fixture.zero_length_scnprintf_len, zero_length_len);
    try std.testing.expectEqual(@as(u8, 0xbb), zero_length_backing[0]);

    bitmap.clearRange(&range_map, 1, 3);
    bitmap.clearRange(&range_map, 7, 1);
    bitmap.clearRange(&range_map, 10, 2);
    try expectWordSliceMatchesFixture(&range_map, fixture.range_after_clear);

    bitmap.fill(&range_map, 130);
    try std.testing.expectEqual(fixture.full_after_fill, bitmap.full(&range_map, 130));
    bitmap.zero(&range_map, 130);
    try std.testing.expectEqual(fixture.empty_after_zero, bitmap.empty(&range_map, 130));
}
