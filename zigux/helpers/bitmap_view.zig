const std = @import("std");
const binding = @import("bitmap_cpumask_binding");

pub const Word = usize;
pub const bits_per_word: u32 = @intCast(@bitSizeOf(Word));

pub fn wordCount(nbits: u32) u32 {
    if (nbits == 0) return 0;

    const word_bits = @as(u64, bits_per_word);
    const numerator = @as(u64, nbits) + word_bits - 1;
    return @intCast(numerator / word_bits);
}

pub fn lastWordMask(nbits: u32) Word {
    if (nbits == 0) return 0;
    const remainder = nbits % bits_per_word;
    if (remainder == 0) return ~@as(Word, 0);
    return ~@as(Word, 0) >> @intCast(bits_per_word - remainder);
}

pub fn viewFromWords(backing: []const Word, nbits: u32) binding.BitmapView {
    std.debug.assert(backing.len == wordCount(nbits));
    return binding.initBitmapView(
        if (backing.len == 0) 0 else @intFromPtr(backing.ptr),
        nbits,
        @intCast(backing.len),
    );
}

pub fn isValid(view: binding.BitmapView) bool {
    const expected = wordCount(view.nbits);
    if (view.word_count != expected) return false;
    return expected == 0 or view.words_addr != 0;
}

fn words(view: binding.BitmapView) []const Word {
    std.debug.assert(view.word_count != 0);
    const ptr: [*]const Word = @ptrFromInt(view.words_addr);
    return ptr[0..view.word_count];
}

pub fn testBit(view: binding.BitmapView, bit: u32) bool {
    if (!isValid(view) or bit >= view.nbits or view.word_count == 0) return false;
    const slice = words(view);
    const word_index = bit / bits_per_word;
    const bit_index = bit % bits_per_word;
    return ((slice[word_index] >> @intCast(bit_index)) & 1) != 0;
}

pub fn firstSet(view: binding.BitmapView) u32 {
    if (!isValid(view)) return 0;
    if (view.word_count == 0) return view.nbits;

    for (words(view), 0..) |raw_word, index| {
        const masked = if (index + 1 == view.word_count)
            raw_word & lastWordMask(view.nbits)
        else
            raw_word;
        if (masked != 0) {
            const offset: u32 = @intCast(@ctz(masked));
            return @intCast(index * bits_per_word + offset);
        }
    }

    return view.nbits;
}

pub fn firstZero(view: binding.BitmapView) u32 {
    if (!isValid(view)) return 0;
    if (view.word_count == 0) return view.nbits;

    for (words(view), 0..) |raw_word, index| {
        var masked = ~raw_word;
        if (index + 1 == view.word_count) masked &= lastWordMask(view.nbits);
        if (masked != 0) {
            const offset: u32 = @intCast(@ctz(masked));
            return @intCast(index * bits_per_word + offset);
        }
    }

    return view.nbits;
}

pub fn weight(view: binding.BitmapView) u32 {
    if (!isValid(view) or view.word_count == 0) return 0;

    var total: u32 = 0;
    for (words(view), 0..) |raw_word, index| {
        const masked = if (index + 1 == view.word_count)
            raw_word & lastWordMask(view.nbits)
        else
            raw_word;
        total += @intCast(@popCount(masked));
    }
    return total;
}

pub fn summarize(view: binding.BitmapView) binding.BitmapSummary {
    if (!isValid(view)) return binding.initBitmapSummary(0, 0, 0);
    return binding.initBitmapSummary(firstSet(view), firstZero(view), weight(view));
}

test "bitmap view helpers stay bounded and predictable" {
    var backing = [_]Word{
        (@as(Word, 1) << 1) | (@as(Word, 1) << 3) | (@as(Word, 1) << 5),
        (@as(Word, 1) << 2),
    };
    const view = viewFromWords(backing[0..], bits_per_word + 6);
    const summary = summarize(view);

    try std.testing.expect(isValid(view));
    try std.testing.expectEqual(@as(u32, 2), wordCount(bits_per_word + 6));
    try std.testing.expectEqual(@as(u32, 1), firstSet(view));
    try std.testing.expectEqual(@as(u32, 0), firstZero(view));
    try std.testing.expectEqual(@as(u32, 4), weight(view));
    try std.testing.expect(testBit(view, bits_per_word + 2));
    try std.testing.expect(!testBit(view, 4));
    try std.testing.expect(!testBit(view, bits_per_word + 5));
    try std.testing.expectEqual(@as(u32, 1), summary.first_set);
    try std.testing.expectEqual(@as(u32, 0), summary.first_zero);
    try std.testing.expectEqual(@as(u32, 4), summary.weight);
}

test "bitmap helpers keep an all-clear bounded window distinct from the empty sentinel" {
    var backing = [_]Word{0};
    const view = viewFromWords(backing[0..], 16);
    const summary = summarize(view);

    try std.testing.expect(isValid(view));
    try std.testing.expect(!testBit(view, 0));
    try std.testing.expect(!testBit(view, 15));
    try std.testing.expectEqual(@as(u32, 16), firstSet(view));
    try std.testing.expectEqual(@as(u32, 0), firstZero(view));
    try std.testing.expectEqual(@as(u32, 0), weight(view));
    try std.testing.expectEqual(@as(u32, 16), summary.first_set);
    try std.testing.expectEqual(@as(u32, 0), summary.first_zero);
    try std.testing.expectEqual(@as(u32, 0), summary.weight);
}

test "bitmap tail masking keeps a full bounded bitmap from leaking zero bits" {
    var backing = [_]Word{
        ~@as(Word, 0),
        lastWordMask(bits_per_word + 11),
    };
    const view = viewFromWords(backing[0..], bits_per_word + 11);
    const summary = summarize(view);

    try std.testing.expect(isValid(view));
    try std.testing.expect(testBit(view, bits_per_word + 10));
    try std.testing.expect(!testBit(view, bits_per_word + 11));
    try std.testing.expectEqual(@as(u32, 0), firstSet(view));
    try std.testing.expectEqual(bits_per_word + 11, firstZero(view));
    try std.testing.expectEqual(bits_per_word + 11, weight(view));
    try std.testing.expectEqual(@as(u32, 0), summary.first_set);
    try std.testing.expectEqual(bits_per_word + 11, summary.first_zero);
    try std.testing.expectEqual(bits_per_word + 11, summary.weight);
}

test "bitmap tail masking ignores out-of-range set bits in the last word" {
    var backing = [_]Word{
        0,
        @as(Word, 1) << (11 + 3),
    };
    const view = viewFromWords(backing[0..], bits_per_word + 11);
    const summary = summarize(view);

    try std.testing.expect(isValid(view));
    try std.testing.expect(!testBit(view, bits_per_word + 10));
    try std.testing.expect(!testBit(view, bits_per_word + 11));
    try std.testing.expectEqual(bits_per_word + 11, firstSet(view));
    try std.testing.expectEqual(@as(u32, 0), firstZero(view));
    try std.testing.expectEqual(@as(u32, 0), weight(view));
    try std.testing.expectEqual(bits_per_word + 11, summary.first_set);
    try std.testing.expectEqual(@as(u32, 0), summary.first_zero);
    try std.testing.expectEqual(@as(u32, 0), summary.weight);
}

test "bitmap exact-word windows keep full-word masks explicit" {
    var backing = [_]Word{
        ~@as(Word, 0),
        (@as(Word, 1) << 5),
    };
    const view = viewFromWords(backing[0..], bits_per_word * 2);
    const summary = summarize(view);

    try std.testing.expect(isValid(view));
    try std.testing.expectEqual(~@as(Word, 0), lastWordMask(bits_per_word * 2));
    try std.testing.expect(testBit(view, bits_per_word + 5));
    try std.testing.expect(!testBit(view, bits_per_word + 6));
    try std.testing.expectEqual(@as(u32, 0), firstSet(view));
    try std.testing.expectEqual(bits_per_word, firstZero(view));
    try std.testing.expectEqual(bits_per_word + 1, weight(view));
    try std.testing.expectEqual(@as(u32, 0), summary.first_set);
    try std.testing.expectEqual(bits_per_word, summary.first_zero);
    try std.testing.expectEqual(bits_per_word + 1, summary.weight);
}

test "bitmap word counts stay predictable for large bounded windows" {
    const max_nbits = std.math.maxInt(u32);
    const expected: u32 = @intCast((@as(u64, max_nbits) + @as(u64, bits_per_word) - 1) / @as(u64, bits_per_word));
    const near_max_nbits = max_nbits - (bits_per_word - 1);
    const near_expected: u32 = @intCast((@as(u64, near_max_nbits) + @as(u64, bits_per_word) - 1) / @as(u64, bits_per_word));
    const invalid = binding.initBitmapView(1, max_nbits, expected - 1);
    const summary = summarize(invalid);

    try std.testing.expectEqual(expected, wordCount(max_nbits));
    try std.testing.expectEqual(near_expected, wordCount(near_max_nbits));
    try std.testing.expect(!isValid(invalid));
    try std.testing.expect(!testBit(invalid, 0));
    try std.testing.expectEqual(@as(u32, 0), firstSet(invalid));
    try std.testing.expectEqual(@as(u32, 0), firstZero(invalid));
    try std.testing.expectEqual(@as(u32, 0), weight(invalid));
    try std.testing.expectEqual(@as(u32, 0), summary.first_set);
    try std.testing.expectEqual(@as(u32, 0), summary.first_zero);
    try std.testing.expectEqual(@as(u32, 0), summary.weight);
}

test "bitmap validity rejects non-empty views without backing storage" {
    const invalid = binding.initBitmapView(0, 1, 1);
    const summary = summarize(invalid);

    try std.testing.expect(!isValid(invalid));
    try std.testing.expect(!testBit(invalid, 0));
    try std.testing.expectEqual(@as(u32, 0), firstSet(invalid));
    try std.testing.expectEqual(@as(u32, 0), firstZero(invalid));
    try std.testing.expectEqual(@as(u32, 0), weight(invalid));
    try std.testing.expectEqual(@as(u32, 0), summary.first_set);
    try std.testing.expectEqual(@as(u32, 0), summary.first_zero);
    try std.testing.expectEqual(@as(u32, 0), summary.weight);
}

test "bitmap validity rejects malformed word counts and closes helpers" {
    const invalid = binding.initBitmapView(0, bits_per_word + 1, 1);
    const summary = summarize(invalid);

    try std.testing.expect(!isValid(invalid));
    try std.testing.expect(!testBit(invalid, 0));
    try std.testing.expectEqual(@as(u32, 0), firstSet(invalid));
    try std.testing.expectEqual(@as(u32, 0), firstZero(invalid));
    try std.testing.expectEqual(@as(u32, 0), weight(invalid));
    try std.testing.expectEqual(@as(u32, 0), summary.first_set);
    try std.testing.expectEqual(@as(u32, 0), summary.first_zero);
    try std.testing.expectEqual(@as(u32, 0), summary.weight);
}

test "bitmap validity rejects zero-bit stray storage and closes helpers" {
    const invalid = binding.initBitmapView(1, 0, 1);
    const summary = summarize(invalid);

    try std.testing.expect(!isValid(invalid));
    try std.testing.expect(!testBit(invalid, 0));
    try std.testing.expectEqual(@as(u32, 0), firstSet(invalid));
    try std.testing.expectEqual(@as(u32, 0), firstZero(invalid));
    try std.testing.expectEqual(@as(u32, 0), weight(invalid));
    try std.testing.expectEqual(@as(u32, 0), summary.first_set);
    try std.testing.expectEqual(@as(u32, 0), summary.first_zero);
    try std.testing.expectEqual(@as(u32, 0), summary.weight);
}

test "bitmap empty sentinels stay stable even with a stray non-zero address" {
    const empty = binding.initBitmapView(1, 0, 0);
    const summary = summarize(empty);

    try std.testing.expect(isValid(empty));
    try std.testing.expect(!testBit(empty, 0));
    try std.testing.expectEqual(@as(u32, 0), firstSet(empty));
    try std.testing.expectEqual(@as(u32, 0), firstZero(empty));
    try std.testing.expectEqual(@as(u32, 0), weight(empty));
    try std.testing.expectEqual(@as(u32, 0), summary.first_set);
    try std.testing.expectEqual(@as(u32, 0), summary.first_zero);
    try std.testing.expectEqual(@as(u32, 0), summary.weight);
}

test "bitmap summaries keep reserved bytes zero for valid and invalid views" {
    var backing = [_]Word{
        (@as(Word, 1) << 1) | (@as(Word, 1) << 3),
    };
    const valid = summarize(viewFromWords(backing[0..], 8));
    const invalid = summarize(binding.initBitmapView(0, bits_per_word + 1, 1));

    try std.testing.expectEqual(@as(u32, 1), valid.first_set);
    try std.testing.expectEqual(@as(u32, 0), valid.first_zero);
    try std.testing.expectEqual(@as(u32, 2), valid.weight);
    try std.testing.expectEqual(@as(u32, 0), valid.reserved);

    try std.testing.expectEqual(@as(u32, 0), invalid.first_set);
    try std.testing.expectEqual(@as(u32, 0), invalid.first_zero);
    try std.testing.expectEqual(@as(u32, 0), invalid.weight);
    try std.testing.expectEqual(@as(u32, 0), invalid.reserved);
}

test "bitmap view empty sentinel behavior stays explicit" {
    const empty = viewFromWords(&.{}, 0);
    const summary = summarize(empty);

    try std.testing.expect(isValid(empty));
    try std.testing.expectEqual(@as(u32, 0), firstSet(empty));
    try std.testing.expectEqual(@as(u32, 0), firstZero(empty));
    try std.testing.expectEqual(@as(u32, 0), weight(empty));
    try std.testing.expectEqual(@as(u32, 0), summary.weight);
}
