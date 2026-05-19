const std = @import("std");

pub const chunk_size_bytes: usize = 128;
pub const word_bits: usize = @bitSizeOf(usize);
pub const bitmap_longs: usize = chunk_size_bytes / @sizeOf(usize);
pub const bitmap_bits: usize = bitmap_longs * word_bits;
pub const BitmapWords = [bitmap_longs]usize;

pub const BitmapView = struct {
    words: *const BitmapWords,

    pub fn rawWords(self: BitmapView) []const usize {
        return self.words[0..];
    }

    pub fn isSet(self: BitmapView, index: usize) bool {
        std.debug.assert(index < bitmap_bits);
        const word_index = index / word_bits;
        const bit_index = index % word_bits;
        return (self.words[word_index] & (@as(usize, 1) << @intCast(bit_index))) != 0;
    }

    pub fn isEmpty(self: BitmapView) bool {
        for (self.rawWords()) |word| {
            if (word != 0) {
                return false;
            }
        }
        return true;
    }

    pub fn isFull(self: BitmapView) bool {
        for (self.rawWords()) |word| {
            if (word != ~@as(usize, 0)) {
                return false;
            }
        }
        return true;
    }

    pub fn weight(self: BitmapView) usize {
        var total: usize = 0;
        for (self.rawWords()) |word| {
            total += @popCount(word);
        }
        return total;
    }

    pub fn firstSet(self: BitmapView) ?usize {
        for (self.rawWords(), 0..) |word, word_index| {
            if (word != 0) {
                return (word_index * word_bits) + @ctz(word);
            }
        }
        return null;
    }

    pub fn firstZero(self: BitmapView) ?usize {
        for (self.rawWords(), 0..) |word, word_index| {
            if (word != ~@as(usize, 0)) {
                return (word_index * word_bits) + @ctz(~word);
            }
        }
        return null;
    }
};

pub fn fromWords(words: *const BitmapWords) BitmapView {
    return .{ .words = words };
}

comptime {
    std.debug.assert(chunk_size_bytes == 128);
    std.debug.assert(bitmap_longs == chunk_size_bytes / @sizeOf(usize));
    std.debug.assert(bitmap_bits == chunk_size_bytes * 8);
}

test "ida bitmap constants keep the fixed chunk geometry" {
    try std.testing.expectEqual(@as(usize, 128), chunk_size_bytes);
    try std.testing.expectEqual(chunk_size_bytes / @sizeOf(usize), bitmap_longs);
    try std.testing.expectEqual(chunk_size_bytes * 8, bitmap_bits);
}

test "empty ida bitmap chunk stays empty and exposes the first zero bit" {
    const words = std.mem.zeroes(BitmapWords);
    const view = fromWords(&words);

    try std.testing.expect(view.isEmpty());
    try std.testing.expect(!view.isFull());
    try std.testing.expectEqual(@as(usize, 0), view.weight());
    try std.testing.expectEqual(@as(?usize, null), view.firstSet());
    try std.testing.expectEqual(@as(?usize, 0), view.firstZero());
}

test "ida bitmap chunk tracks sparse bits across word boundaries" {
    var words = std.mem.zeroes(BitmapWords);
    words[0] |= @as(usize, 1) << 5;
    words[1] |= @as(usize, 1) << 3;
    words[bitmap_longs - 1] |= @as(usize, 1) << @as(std.math.Log2Int(usize), @intCast(word_bits - 1));

    const view = fromWords(&words);

    try std.testing.expect(!view.isEmpty());
    try std.testing.expect(!view.isFull());
    try std.testing.expect(view.isSet(5));
    try std.testing.expect(view.isSet(word_bits + 3));
    try std.testing.expect(view.isSet(bitmap_bits - 1));
    try std.testing.expectEqual(@as(usize, 3), view.weight());
    try std.testing.expectEqual(@as(?usize, 5), view.firstSet());
    try std.testing.expectEqual(@as(?usize, 0), view.firstZero());
}

test "full ida bitmap chunk reports no zero bits left" {
    const words = [_]usize{~@as(usize, 0)} ** bitmap_longs;
    const view = fromWords(&words);

    try std.testing.expect(!view.isEmpty());
    try std.testing.expect(view.isFull());
    try std.testing.expectEqual(bitmap_bits, view.weight());
    try std.testing.expectEqual(@as(?usize, 0), view.firstSet());
    try std.testing.expectEqual(@as(?usize, null), view.firstZero());
}

test "first zero bit advances to the first clear position inside a used word" {
    var words = [_]usize{0} ** bitmap_longs;
    words[0] = (@as(usize, 1) << 0) | (@as(usize, 1) << 1) | (@as(usize, 1) << 3);
    words[1] = ~@as(usize, 0);

    const view = fromWords(&words);

    try std.testing.expectEqual(@as(?usize, 2), view.firstZero());
    try std.testing.expectEqual(@as(?usize, 0), view.firstSet());
    try std.testing.expectEqual(@as(usize, word_bits + 3), view.weight());
}
