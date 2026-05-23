const std = @import("std");

pub const word_bits: usize = @bitSizeOf(usize);
pub const Word = usize;

fn wordIndex(bit_index: usize) usize {
    return bit_index / word_bits;
}

fn bitMask(bit_index: usize) Word {
    return @as(Word, 1) << @intCast(bit_index % word_bits);
}

fn tailMask(bit_len: usize) Word {
    const remainder = bit_len % word_bits;
    if (remainder == 0) return std.math.maxInt(Word);
    return (@as(Word, 1) << @intCast(remainder)) - 1;
}

pub const BitmapView = struct {
    words: []const Word,
    bit_len: usize,

    pub fn init(words: []const Word, bit_len: usize) BitmapView {
        std.debug.assert(words.len * word_bits >= bit_len);
        return .{
            .words = words,
            .bit_len = bit_len,
        };
    }

    pub fn activeWordLen(self: BitmapView) usize {
        if (self.bit_len == 0) return 0;
        return (self.bit_len + (word_bits - 1)) / word_bits;
    }

    pub fn validWordMask(self: BitmapView, word_index: usize) Word {
        std.debug.assert(word_index < self.activeWordLen());
        if (word_index + 1 == self.activeWordLen()) return tailMask(self.bit_len);
        return std.math.maxInt(Word);
    }

    pub fn maskedWord(self: BitmapView, word_index: usize) Word {
        return self.words[word_index] & self.validWordMask(word_index);
    }

    pub fn isSet(self: BitmapView, bit_index: usize) bool {
        std.debug.assert(bit_index < self.bit_len);
        return (self.words[wordIndex(bit_index)] & bitMask(bit_index)) != 0;
    }

    pub fn countSetBits(self: BitmapView) usize {
        if (self.bit_len == 0) return 0;

        var total: usize = 0;
        for (0..self.activeWordLen()) |index| {
            total += @popCount(self.maskedWord(index));
        }
        return total;
    }

    pub fn firstSetBit(self: BitmapView) ?usize {
        for (0..self.activeWordLen()) |index| {
            const masked = self.maskedWord(index);
            if (masked == 0) continue;

            const base = index * word_bits;
            return base + @ctz(masked);
        }
        return null;
    }

    pub fn firstClearBit(self: BitmapView) ?usize {
        if (self.bit_len == 0) return null;

        for (0..self.activeWordLen()) |index| {
            const masked = (~self.words[index]) & self.validWordMask(index);
            if (masked == 0) continue;

            const base = index * word_bits;
            const bit = base + @ctz(masked);
            if (bit < self.bit_len) return bit;
        }
        return null;
    }
};

test "bitmap view keeps an empty range trivial" {
    const words = [_]Word{0};
    const view = BitmapView.init(words[0..], 0);

    try std.testing.expectEqual(@as(usize, 0), view.countSetBits());
    try std.testing.expectEqual(@as(?usize, null), view.firstSetBit());
    try std.testing.expectEqual(@as(?usize, null), view.firstClearBit());
}

test "bitmap view reports set bits inside one word" {
    const words = [_]Word{bitMask(1) | bitMask(5) | bitMask(12)};
    const view = BitmapView.init(words[0..], 16);

    try std.testing.expect(view.isSet(1));
    try std.testing.expect(view.isSet(5));
    try std.testing.expect(!view.isSet(7));
    try std.testing.expectEqual(@as(usize, 3), view.countSetBits());
    try std.testing.expectEqual(@as(?usize, 1), view.firstSetBit());
    try std.testing.expectEqual(@as(?usize, 0), view.firstClearBit());
}

test "bitmap view ignores padding bits past the declared range" {
    const words = [_]Word{
        std.math.maxInt(Word),
        std.math.maxInt(Word),
    };
    const bit_len = word_bits + 5;
    const view = BitmapView.init(words[0..], bit_len);

    try std.testing.expectEqual(bit_len, view.countSetBits());
    try std.testing.expectEqual(@as(?usize, 0), view.firstSetBit());
    try std.testing.expectEqual(@as(?usize, null), view.firstClearBit());
}

test "bitmap view finds the first clear bit across word boundaries" {
    const words = [_]Word{
        std.math.maxInt(Word),
        bitMask(word_bits) | bitMask(word_bits + 1),
    };
    const bit_len = word_bits + 4;
    const view = BitmapView.init(words[0..], bit_len);

    try std.testing.expectEqual(@as(usize, word_bits + 2), view.firstClearBit().?);
}

test "bitmap view shares trailing word masking across count and discovery paths" {
    const words = [_]Word{
        std.math.maxInt(Word),
        bitMask(word_bits) | bitMask(word_bits + 2) | bitMask(word_bits + 5),
    };
    const bit_len = word_bits + 3;
    const view = BitmapView.init(words[0..], bit_len);

    try std.testing.expectEqual(@as(Word, 0b111), view.validWordMask(1));
    try std.testing.expectEqual(bitMask(word_bits) | bitMask(word_bits + 2), view.maskedWord(1));
    try std.testing.expectEqual(word_bits + 2, view.countSetBits());
    try std.testing.expectEqual(@as(?usize, 0), view.firstSetBit());
    try std.testing.expectEqual(@as(?usize, word_bits + 1), view.firstClearBit());
}
