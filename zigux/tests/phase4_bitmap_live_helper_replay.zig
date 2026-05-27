const std = @import("std");
const bitmap_mod = @import("bitmap");
const find_bit = @import("find_bit");

const Word = bitmap_mod.Word;
const bitmap_nbits: usize = 1024;
const word_count: usize = bitmap_mod.bitsToWords(bitmap_nbits);

const LiveBitmap = struct {
    words: [word_count]Word = std.mem.zeroes([word_count]Word),

    fn fillExact(self: *LiveBitmap, nbits: usize) void {
        bitmap_mod.bitmap_fill(self.words[0..], nbits);
    }

    fn zeroRounded(self: *LiveBitmap, nbits: usize) void {
        bitmap_mod.bitmap_zero(self.words[0..], nbits);
    }

    fn copyClearTail(self: *LiveBitmap, other: *const LiveBitmap, nbits: usize) void {
        bitmap_mod.bitmap_copy_clear_tail(self.words[0..], other.words[0..], nbits);
    }

    fn firstSet(self: *const LiveBitmap) usize {
        return find_bit.findFirstBit(self.words[0..], bitmap_nbits);
    }

    fn firstZero(self: *const LiveBitmap) usize {
        return find_bit.findFirstZeroBit(self.words[0..], bitmap_nbits);
    }

    fn weight(self: *const LiveBitmap) usize {
        return bitmap_mod.bitmap_weight(self.words[0..], bitmap_nbits);
    }
};

test "phase4 bitmap live helper replay keeps fill exact and zero rounded" {
    var bitmap = LiveBitmap{};

    bitmap.fillExact(35);
    try std.testing.expectEqual(@as(usize, 35), bitmap.firstZero());
    try std.testing.expectEqual(@as(usize, 35), bitmap.weight());

    bitmap.fillExact(115);
    try std.testing.expectEqual(@as(usize, 115), bitmap.firstZero());
    try std.testing.expectEqual(@as(usize, 115), bitmap.weight());

    bitmap.fillExact(bitmap_nbits);
    bitmap.zeroRounded(35);
    try std.testing.expectEqual(@as(usize, 64), bitmap.firstSet());

    bitmap.fillExact(bitmap_nbits);
    bitmap.zeroRounded(115);
    try std.testing.expectEqual(@as(usize, 128), bitmap.firstSet());
}

test "phase4 bitmap live helper replay keeps copy-tail rollback explicit" {
    var source = LiveBitmap{};
    var bitmap = LiveBitmap{};

    source.fillExact(109);
    bitmap.fillExact(bitmap_nbits);
    bitmap.copyClearTail(&source, 97);

    try std.testing.expectEqual(@as(usize, 0), bitmap.firstSet());
    try std.testing.expectEqual(@as(usize, 97), bitmap.firstZero());
    try std.testing.expectEqual(@as(usize, 993), bitmap.weight());
}
