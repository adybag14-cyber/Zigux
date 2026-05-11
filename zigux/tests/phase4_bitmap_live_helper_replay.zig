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

test "phase4 bitmap live helper replay keeps zero-length and full-extent prefix edits explicit" {
    var bitmap = LiveBitmapHarness{};

    bitmap.initEmpty();
    bitmap.setRange(5, 1);
    bitmap.setRange(63, 1);
    bitmap.setRange(80, 1);
    bitmap.setRange(123, 1);
    const seeded = bitmap.words;

    bitmap.fillPrefix(0);
    try std.testing.expectEqualDeep(seeded, bitmap.words);
    bitmap.zeroPrefix(0);
    try std.testing.expectEqualDeep(seeded, bitmap.words);
    try std.testing.expectEqual(@as(usize, 5), bitmap.firstSet());
    try std.testing.expectEqual(@as(usize, 0), bitmap.firstZero());
    try std.testing.expectEqual(@as(usize, 4), bitmap.weight());

    bitmap.initEmpty();
    bitmap.fillPrefix(LiveBitmapHarness.bitmap_nbits);
    try std.testing.expectEqual(@as(usize, 0), bitmap.firstSet());
    try std.testing.expectEqual(@as(usize, LiveBitmapHarness.bitmap_nbits), bitmap.firstZero());
    try std.testing.expectEqual(@as(usize, LiveBitmapHarness.bitmap_nbits), bitmap.weight());
    try std.testing.expect(bitmap.isSet(0));
    try std.testing.expect(bitmap.isSet(127));
    try std.testing.expect(bitmap.isSet(LiveBitmapHarness.bitmap_nbits - 1));

    bitmap.zeroPrefix(LiveBitmapHarness.bitmap_nbits);
    try std.testing.expectEqual(@as(usize, LiveBitmapHarness.bitmap_nbits), bitmap.firstSet());
    try std.testing.expectEqual(@as(usize, 0), bitmap.firstZero());
    try std.testing.expectEqual(@as(usize, 0), bitmap.weight());
    try std.testing.expect(!bitmap.isSet(0));
    try std.testing.expect(!bitmap.isSet(127));
    try std.testing.expect(!bitmap.isSet(LiveBitmapHarness.bitmap_nbits - 1));
}

test "phase4 bitmap live helper replay keeps copy-tail clearing and extension explicit" {
    const count = live_bitmap.bits_per_long + 5;
    const size = live_bitmap.bits_per_long * 3;
    const src = [_]live_bitmap.Word{ ~@as(live_bitmap.Word, 0), ~@as(live_bitmap.Word, 0), ~@as(live_bitmap.Word, 0) };

    var cleared = [_]live_bitmap.Word{ 0, 0, 0 };
    live_bitmap.bitmap_copy_clear_tail(cleared[0..], src[0..], count);
    try std.testing.expectEqual(@as(live_bitmap.Word, ~@as(live_bitmap.Word, 0)), cleared[0]);
    try std.testing.expectEqual(live_bitmap.lastWordMask(count), cleared[1]);
    try std.testing.expectEqual(@as(live_bitmap.Word, 0), cleared[2]);

    var extended = [_]live_bitmap.Word{ ~@as(live_bitmap.Word, 0), ~@as(live_bitmap.Word, 0), ~@as(live_bitmap.Word, 0) };
    live_bitmap.bitmap_copy_and_extend(extended[0..], src[0..], count, size);
    try std.testing.expectEqual(@as(live_bitmap.Word, ~@as(live_bitmap.Word, 0)), extended[0]);
    try std.testing.expectEqual(live_bitmap.lastWordMask(count), extended[1]);
    try std.testing.expectEqual(@as(live_bitmap.Word, 0), extended[2]);

    var zero_copy = [_]live_bitmap.Word{
        0x55aa55aa55aa55aa,
        0x1122334455667788,
        0x99aabbccddeeff00,
    };
    const zero_before = zero_copy;
    live_bitmap.bitmap_copy_clear_tail(zero_copy[0..0], src[0..0], 0);
    try std.testing.expectEqualDeep(zero_before, zero_copy);
    live_bitmap.bitmap_copy_and_extend(zero_copy[0..0], src[0..0], 0, 0);
    try std.testing.expectEqualDeep(zero_before, zero_copy);
}
