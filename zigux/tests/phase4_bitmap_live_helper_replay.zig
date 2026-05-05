const std = @import("std");
const live_bitmap = @import("bitmap");
const live_find_bit = @import("find_bit");

// Keep the synthetic rollback gate in bitmap_diff.zig paired with one
// helper-backed replay so the shipped bitmap helper semantics stay explicit.
const LiveBitmapHarness = struct {
    const Self = @This();
    pub const bitmap_nbits: usize = 1024;
    const word_count = live_bitmap.bitsToWords(bitmap_nbits);

    words: [word_count]live_bitmap.Word = std.mem.zeroes([word_count]live_bitmap.Word),

    fn initEmpty(self: *Self) void {
        @memset(self.words[0..], 0);
    }

    fn fillAll(self: *Self) void {
        live_bitmap.fill(self.words[0..], bitmap_nbits);
    }

    fn fillPrefix(self: *Self, nbits: usize) void {
        live_bitmap.fill(self.words[0..], nbits);
    }

    fn zeroPrefix(self: *Self, nbits: usize) void {
        live_bitmap.zero(self.words[0..], nbits);
    }

    fn setRange(self: *Self, start: usize, len: usize) void {
        live_bitmap.setRange(self.words[0..], start, len);
    }

    fn clearRange(self: *Self, start: usize, len: usize) void {
        live_bitmap.clearRange(self.words[0..], start, len);
    }

    fn firstSet(self: *const Self) usize {
        return live_find_bit.findFirstBit(self.words[0..], bitmap_nbits);
    }

    fn firstZero(self: *const Self) usize {
        return live_find_bit.findFirstZeroBit(self.words[0..], bitmap_nbits);
    }

    fn weight(self: *const Self) usize {
        return live_bitmap.weight(self.words[0..], bitmap_nbits);
    }

    fn isSet(self: *const Self, bit: usize) bool {
        const word_index = bit / live_bitmap.bits_per_long;
        const bit_index = @as(std.math.Log2Int(live_bitmap.Word), @intCast(bit % live_bitmap.bits_per_long));
        return ((self.words[word_index] >> bit_index) & 1) != 0;
    }
};

test "phase4 bitmap live helper replay keeps fill exact and zero rounded" {
    var bitmap = LiveBitmapHarness{};

    bitmap.initEmpty();
    bitmap.fillPrefix(35);
    try std.testing.expectEqual(@as(usize, 0), bitmap.firstSet());
    try std.testing.expectEqual(@as(usize, 35), bitmap.firstZero());
    try std.testing.expectEqual(@as(usize, 35), bitmap.weight());
    try std.testing.expect(bitmap.isSet(34));
    try std.testing.expect(!bitmap.isSet(35));
    try std.testing.expect(!bitmap.isSet(63));

    bitmap.fillAll();
    bitmap.zeroPrefix(35);
    try std.testing.expectEqual(@as(usize, 64), bitmap.firstSet());
    try std.testing.expectEqual(@as(usize, 0), bitmap.firstZero());
    try std.testing.expectEqual(@as(usize, LiveBitmapHarness.bitmap_nbits - 64), bitmap.weight());
    try std.testing.expect(!bitmap.isSet(63));
    try std.testing.expect(bitmap.isSet(64));

    bitmap.initEmpty();
    bitmap.setRange(0, 64);
    bitmap.setRange(79, 19);
    bitmap.fillPrefix(115);
    try std.testing.expectEqual(@as(usize, 0), bitmap.firstSet());
    try std.testing.expectEqual(@as(usize, 115), bitmap.firstZero());
    try std.testing.expectEqual(@as(usize, 115), bitmap.weight());
    try std.testing.expect(bitmap.isSet(114));
    try std.testing.expect(!bitmap.isSet(115));
    try std.testing.expect(!bitmap.isSet(127));

    bitmap.fillAll();
    bitmap.clearRange(79, 19);
    bitmap.zeroPrefix(115);
    try std.testing.expectEqual(@as(usize, 128), bitmap.firstSet());
    try std.testing.expectEqual(@as(usize, 0), bitmap.firstZero());
    try std.testing.expectEqual(@as(usize, LiveBitmapHarness.bitmap_nbits - 128), bitmap.weight());
    try std.testing.expect(!bitmap.isSet(127));
    try std.testing.expect(bitmap.isSet(128));
}
