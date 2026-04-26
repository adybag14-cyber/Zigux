const std = @import("std");

const SummaryExpectation = struct {
    first_set: u32,
    first_zero: u32,
    weight: u32,
};

const RangeOp = struct {
    start: u32,
    len: u32,
};

const DiffCase = struct {
    name: []const u8,
    init_bits: []const u32,
    set_ranges: []const RangeOp,
    clear_ranges: []const RangeOp,
    expected_summary: SummaryExpectation,
    must_be_set: []const u32,
    must_be_clear: []const u32,
};

const CopyCase = struct {
    name: []const u8,
    source_set_len: u32,
    copy_nbits: u32,
    expected_summary: SummaryExpectation,
    must_be_set: []const u32,
    must_be_clear: []const u32,
};

const BitmapHarness = struct {
    const Self = @This();
    const Word = usize;
    const bits_per_long: u32 = @intCast(@bitSizeOf(Word));
    pub const bitmap_nbits: u32 = 1024;
    const word_count: usize = bitmap_nbits / bits_per_long;

    words: [word_count]Word = [_]Word{0} ** word_count,

    fn validateRange(start: u32, len: u32) !void {
        if (len == 0) return;
        if (start >= bitmap_nbits) return error.BitRangeOutOfBounds;
        if (len > bitmap_nbits - start) return error.BitRangeOutOfBounds;
    }

    fn assignBit(self: *Self, bit: u32, value: bool) void {
        const word_index: usize = @intCast(bit / bits_per_long);
        const bit_index: u6 = @intCast(bit % bits_per_long);
        const mask: Word = @as(Word, 1) << bit_index;
        if (value) {
            self.words[word_index] |= mask;
        } else {
            self.words[word_index] &= ~mask;
        }
    }

    fn initWithSetBits(self: *Self, bits: []const u32) !void {
        @memset(self.words[0..], 0);
        for (bits) |bit| {
            if (bit >= bitmap_nbits) return error.BitRangeOutOfBounds;
            self.assignBit(bit, true);
        }
    }

    fn setRange(self: *Self, start: u32, len: u32) !void {
        try validateRange(start, len);
        var bit = start;
        while (bit < start + len) : (bit += 1) {
            self.assignBit(bit, true);
        }
    }

    fn clearRange(self: *Self, start: u32, len: u32) !void {
        try validateRange(start, len);
        var bit = start;
        while (bit < start + len) : (bit += 1) {
            self.assignBit(bit, false);
        }
    }

    fn fill(self: *Self) void {
        @memset(self.words[0..], ~@as(Word, 0));
    }

    fn copyFrom(self: *Self, other: *const Self, nbits: u32) !void {
        if (nbits > bitmap_nbits) return error.BitRangeOutOfBounds;

        if (nbits == 0) {
            @memset(self.words[0..], 0);
            return;
        }

        const full_words: usize = @intCast(nbits / bits_per_long);
        const tail_bits = nbits % bits_per_long;

        var index: usize = 0;
        while (index < full_words) : (index += 1) {
            self.words[index] = other.words[index];
        }

        if (tail_bits != 0) {
            const mask: Word = (~@as(Word, 0)) >> @intCast(bits_per_long - tail_bits);
            self.words[full_words] = other.words[full_words] & mask;
            index = full_words + 1;
        } else {
            index = full_words;
        }

        while (index < self.words.len) : (index += 1) {
            self.words[index] = 0;
        }
    }

    fn isSet(self: *const Self, bit: u32) bool {
        if (bit >= bitmap_nbits) return false;

        const word_index: usize = @intCast(bit / bits_per_long);
        const bit_index: u6 = @intCast(bit % bits_per_long);
        return ((self.words[word_index] >> bit_index) & 1) != 0;
    }

    fn firstSet(self: *const Self) u32 {
        for (self.words, 0..) |word, index| {
            if (word != 0) {
                const offset: u32 = @intCast(@ctz(word));
                return @intCast(index * bits_per_long + offset);
            }
        }

        return bitmap_nbits;
    }

    fn firstZero(self: *const Self) u32 {
        for (self.words, 0..) |word, index| {
            const inverted = ~word;
            if (inverted != 0) {
                const offset: u32 = @intCast(@ctz(inverted));
                return @intCast(index * bits_per_long + offset);
            }
        }

        return bitmap_nbits;
    }

    fn weight(self: *const Self) u32 {
        var total: u32 = 0;
        for (self.words) |word| {
            total += @intCast(@popCount(word));
        }
        return total;
    }

    fn summary(self: *const Self) SummaryExpectation {
        return .{
            .first_set = self.firstSet(),
            .first_zero = self.firstZero(),
            .weight = self.weight(),
        };
    }
};

fn expectSummary(summary: SummaryExpectation, expected: SummaryExpectation) !void {
    try std.testing.expectEqual(expected.first_set, summary.first_set);
    try std.testing.expectEqual(expected.first_zero, summary.first_zero);
    try std.testing.expectEqual(expected.weight, summary.weight);
}

fn expectCase(case: DiffCase) !void {
    var bitmap = BitmapHarness{};
    try bitmap.initWithSetBits(case.init_bits);
    try std.testing.expect(case.name.len != 0);

    for (case.set_ranges) |op| {
        try bitmap.setRange(op.start, op.len);
    }
    for (case.clear_ranges) |op| {
        try bitmap.clearRange(op.start, op.len);
    }

    try expectSummary(bitmap.summary(), case.expected_summary);

    for (case.must_be_set) |bit| {
        try std.testing.expect(bitmap.isSet(bit));
    }
    for (case.must_be_clear) |bit| {
        try std.testing.expect(!bitmap.isSet(bit));
    }
}

fn expectCopyCase(case: CopyCase) !void {
    var source = BitmapHarness{};
    try source.initWithSetBits(&.{});
    try source.setRange(0, case.source_set_len);

    var destination = BitmapHarness{};
    destination.fill();
    try destination.copyFrom(&source, case.copy_nbits);
    try std.testing.expect(case.name.len != 0);

    try expectSummary(destination.summary(), case.expected_summary);

    for (case.must_be_set) |bit| {
        try std.testing.expect(destination.isSet(bit));
    }
    for (case.must_be_clear) |bit| {
        try std.testing.expect(!destination.isSet(bit));
    }
}

test "bitmap diff gate replays bounded lib/test_bitmap.c range expectations" {
    const cases = [_]DiffCase{
        .{
            .name = "test_fill_set single-word starter",
            .init_bits = &.{},
            .set_ranges = &.{.{ .start = 0, .len = 9 }},
            .clear_ranges = &.{},
            .expected_summary = .{ .first_set = 0, .first_zero = 9, .weight = 9 },
            .must_be_set = &.{ 0, 8 },
            .must_be_clear = &.{ 9, 10, BitmapHarness.bitmap_nbits - 1 },
        },
        .{
            .name = "test_zero_clear cross-boundary cutout",
            .init_bits = &.{},
            .set_ranges = &.{.{ .start = 0, .len = BitmapHarness.bitmap_nbits }},
            .clear_ranges = &.{.{ .start = 79, .len = 19 }},
            .expected_summary = .{
                .first_set = 0,
                .first_zero = 79,
                .weight = BitmapHarness.bitmap_nbits - 19,
            },
            .must_be_set = &.{ 0, 78, 98, BitmapHarness.bitmap_nbits - 1 },
            .must_be_clear = &.{ 79, 97 },
        },
        .{
            .name = "test_find_nth_bit starter population",
            .init_bits = &.{ 10, 20, 30, 40, 50, 60, 80, 123 },
            .set_ranges = &.{},
            .clear_ranges = &.{},
            .expected_summary = .{ .first_set = 10, .first_zero = 0, .weight = 8 },
            .must_be_set = &.{ 10, 80, 123 },
            .must_be_clear = &.{ 0, 79, 124 },
        },
    };

    for (cases) |case| {
        try expectCase(case);
    }
}

test "bitmap diff gate records exact bounded copy checks" {
    const cases = [_]CopyCase{
        .{
            .name = "test_copy partial-word tail clearing at 109 bits",
            .source_set_len = 109,
            .copy_nbits = 109,
            .expected_summary = .{ .first_set = 0, .first_zero = 109, .weight = 109 },
            .must_be_set = &.{108},
            .must_be_clear = &.{ 109, BitmapHarness.bitmap_nbits - 1 },
        },
        .{
            .name = "test_copy aligned tail clearing at 97 bits",
            .source_set_len = 109,
            .copy_nbits = 97,
            .expected_summary = .{ .first_set = 0, .first_zero = 97, .weight = 97 },
            .must_be_set = &.{96},
            .must_be_clear = &.{ 97, 108, BitmapHarness.bitmap_nbits - 1 },
        },
        .{
            .name = "test_zero_nbits zero-length copy clears destination",
            .source_set_len = 109,
            .copy_nbits = 0,
            .expected_summary = .{
                .first_set = BitmapHarness.bitmap_nbits,
                .first_zero = 0,
                .weight = 0,
            },
            .must_be_set = &.{},
            .must_be_clear = &.{ 0, 96, BitmapHarness.bitmap_nbits - 1 },
        },
    };

    for (cases) |case| {
        try expectCopyCase(case);
    }
}
