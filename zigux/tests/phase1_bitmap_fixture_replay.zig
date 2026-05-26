const std = @import("std");
const bitmap = @import("bitmap");

const fixture_bytes = @embedFile("fixtures/phase1_helpers.json");

const Fixture = struct {
    bitmap: struct {
        truncated_scnprintf_len: usize,
        truncated_scnprintf: []const u8,
        terminator_only_scnprintf_len: usize,
        terminator_only_nul: u8,
        zero_length_scnprintf_len: usize,
        alloc_words: usize,
        zalloc_words: usize,
        zalloc_values: []const bitmap.Word,
        partial_xor_nbits: usize,
        partial_xor_masked_values: []const bitmap.Word,
    },
};

fn loadFixture() !std.json.Parsed(Fixture) {
    return std.json.parseFromSlice(Fixture, std.testing.allocator, fixture_bytes, .{
        .ignore_unknown_fields = true,
    });
}

test "phase1 bitmap fixture replay covers truncation allocation and partial-window xor keys" {
    var parsed = try loadFixture();
    defer parsed.deinit();
    const fixture = parsed.value;

    var map = [_]bitmap.Word{0};
    bitmap.setRange(&map, 1, 3);
    bitmap.setRange(&map, 7, 1);
    bitmap.setRange(&map, 10, 2);

    var truncated = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa };
    const truncated_len = bitmap.scnprintf(&map, 12, truncated[0 .. fixture.bitmap.truncated_scnprintf_len + 1]);
    try std.testing.expectEqual(fixture.bitmap.truncated_scnprintf_len, truncated_len);
    try std.testing.expectEqualStrings(
        fixture.bitmap.truncated_scnprintf,
        truncated[0..truncated_len],
    );
    try std.testing.expectEqual(@as(u8, 0), truncated[truncated_len]);

    var terminator_only = [_]u8{0xaa};
    const terminator_only_len = bitmap.scnprintf(&map, 12, terminator_only[0..1]);
    try std.testing.expectEqual(fixture.bitmap.terminator_only_scnprintf_len, terminator_only_len);
    try std.testing.expectEqual(fixture.bitmap.terminator_only_nul, terminator_only[0]);

    var zero_length_backing = [_]u8{0xbb};
    const zero_length_len = bitmap.scnprintf(&map, 12, zero_length_backing[0..0]);
    try std.testing.expectEqual(fixture.bitmap.zero_length_scnprintf_len, zero_length_len);
    try std.testing.expectEqual(@as(u8, 0xbb), zero_length_backing[0]);

    const allocator = std.testing.allocator;
    var allocated: ?[]bitmap.Word = try bitmap.bitmapAlloc(allocator, bitmap.bits_per_long + 5);
    defer bitmap.bitmapFree(allocator, &allocated);
    try std.testing.expectEqual(fixture.bitmap.alloc_words, allocated.?.len);

    var zeroed: ?[]bitmap.Word = try bitmap.bitmapZalloc(allocator, bitmap.bits_per_long + 5);
    defer bitmap.bitmapFree(allocator, &zeroed);
    try std.testing.expectEqual(fixture.bitmap.zalloc_words, zeroed.?.len);
    try std.testing.expectEqualSlices(bitmap.Word, fixture.bitmap.zalloc_values, zeroed.?);

    const lhs = [_]bitmap.Word{0b1_1111};
    const rhs = [_]bitmap.Word{0b1_0001};
    var dst = [_]bitmap.Word{0};
    bitmap.xorBits(&dst, &lhs, &rhs, fixture.bitmap.partial_xor_nbits);
    const masked = [_]bitmap.Word{dst[0] & bitmap.lastWordMask(fixture.bitmap.partial_xor_nbits)};
    try std.testing.expectEqualSlices(bitmap.Word, fixture.bitmap.partial_xor_masked_values, &masked);
}
