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
    fill_prefixes: []const u32,
    zero_prefixes: []const u32,
    expected_summary: SummaryExpectation,
    must_be_set: []const u32,
    must_be_clear: []const u32,
};

const CopyCase = struct {
    name: []const u8,
    source_set_len: u32,
    copy_nbits: u32,
    destination_fill: bool,
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

    words: [word_count]Word = std.mem.zeroes([word_count]Word),

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

    fn roundedPrefixLen(nbits: u32) !u32 {
        if (nbits > bitmap_nbits) return error.BitRangeOutOfBounds;
        if (nbits == 0) return 0;

        const words = (nbits + bits_per_long - 1) / bits_per_long;
        return @min(bitmap_nbits, words * bits_per_long);
    }

    fn fillPrefix(self: *Self, nbits: u32) !void {
        try self.setRange(0, try roundedPrefixLen(nbits));
    }

    fn zeroPrefix(self: *Self, nbits: u32) !void {
        try self.clearRange(0, try roundedPrefixLen(nbits));
    }

    fn copyFrom(self: *Self, other: *const Self, nbits: u32) !void {
        if (nbits > bitmap_nbits) return error.BitRangeOutOfBounds;
        if (nbits == 0) return;

        const full_words: usize = @intCast(nbits / bits_per_long);
        const tail_bits = nbits % bits_per_long;

        var index: usize = 0;
        while (index < full_words) : (index += 1) {
            self.words[index] = other.words[index];
        }

        if (tail_bits != 0) {
            const mask: Word = (~@as(Word, 0)) >> @intCast(bits_per_long - tail_bits);
            self.words[full_words] = other.words[full_words] & mask;
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

    fn findNthSet(self: *const Self, nbits: u32, nth: u32) !u32 {
        if (nbits > bitmap_nbits) return error.BitRangeOutOfBounds;

        var seen: u32 = 0;
        var bit: u32 = 0;
        while (bit < nbits) : (bit += 1) {
            if (!self.isSet(bit)) continue;
            if (seen == nth) return bit;
            seen += 1;
        }

        return nbits;
    }

    fn summary(self: *const Self) SummaryExpectation {
        return .{
            .first_set = self.firstSet(),
            .first_zero = self.firstZero(),
            .weight = self.weight(),
        };
    }
};

const ThresholdReplaySummary = struct {
    iterations: usize,
    checksum: u64,
    final_first_set: u32,
    final_first_zero: u32,
    final_weight: u32,
};

fn mixThresholdChecksum(checksum: *u64, value: anytype) void {
    checksum.* = checksum.* *% 0x9e3779b185ebca87 +% @as(u64, @intCast(value));
}

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
    for (case.fill_prefixes) |nbits| {
        try bitmap.fillPrefix(nbits);
    }
    for (case.zero_prefixes) |nbits| {
        try bitmap.zeroPrefix(nbits);
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
    if (case.destination_fill) {
        destination.fill();
    }
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

fn expectNthCase(bits: []const u32, nbits: u32, expected: []const u32) !void {
    var bitmap = BitmapHarness{};
    try bitmap.initWithSetBits(bits);

    for (expected, 0..) |bit, nth| {
        try std.testing.expectEqual(bit, try bitmap.findNthSet(nbits, @intCast(nth)));
    }
    try std.testing.expectEqual(nbits, try bitmap.findNthSet(nbits, @intCast(expected.len)));
}

// Keep one deterministic batch available so a future bitmap threshold lane can
// benchmark the exact current rollback gate instead of a looser synthetic loop.
pub fn runThresholdReplay(iterations: usize) !ThresholdReplaySummary {
    var bitmap = BitmapHarness{};
    var source = BitmapHarness{};
    var destination = BitmapHarness{};
    var checksum: u64 = 0;

    var iteration: usize = 0;
    while (iteration < iterations) : (iteration += 1) {
        try bitmap.initWithSetBits(&.{});
        try bitmap.setRange(0, 9);
        const range_summary = bitmap.summary();
        mixThresholdChecksum(&checksum, range_summary.first_set);
        mixThresholdChecksum(&checksum, range_summary.first_zero);
        mixThresholdChecksum(&checksum, range_summary.weight);

        try bitmap.fillPrefix(35);
        const fill_summary = bitmap.summary();
        mixThresholdChecksum(&checksum, fill_summary.first_zero);
        mixThresholdChecksum(&checksum, fill_summary.weight);

        bitmap.fill();
        try bitmap.zeroPrefix(115);
        const zero_summary = bitmap.summary();
        mixThresholdChecksum(&checksum, zero_summary.first_set);
        mixThresholdChecksum(&checksum, zero_summary.weight);

        try source.initWithSetBits(&.{});
        try source.setRange(0, 109);
        destination.fill();
        try destination.copyFrom(&source, 97);
        const copy_summary = destination.summary();
        mixThresholdChecksum(&checksum, copy_summary.first_zero);
        mixThresholdChecksum(&checksum, copy_summary.weight);
    }

    const final_summary = destination.summary();
    return .{
        .iterations = iterations,
        .checksum = checksum,
        .final_first_set = final_summary.first_set,
        .final_first_zero = final_summary.first_zero,
        .final_weight = final_summary.weight,
    };
}

test "bitmap diff gate replays bounded lib/test_bitmap.c range expectations" {
    const cases = [_]DiffCase{
        .{
            .name = "test_fill_set single-word starter",
            .init_bits = &.{},
            .set_ranges = &.{.{ .start = 0, .len = 9 }},
            .clear_ranges = &.{},
            .fill_prefixes = &.{},
            .zero_prefixes = &.{},
            .expected_summary = .{ .first_set = 0, .first_zero = 9, .weight = 9 },
            .must_be_set = &.{ 0, 8 },
            .must_be_clear = &.{ 9, 10, BitmapHarness.bitmap_nbits - 1 },
        },
        .{
            .name = "test_fill_set bitmap_fill rounds 35 bits to one full word",
            .init_bits = &.{},
            .set_ranges = &.{.{ .start = 0, .len = 9 }},
            .clear_ranges = &.{},
            .fill_prefixes = &.{35},
            .zero_prefixes = &.{},
            .expected_summary = .{ .first_set = 0, .first_zero = 64, .weight = 64 },
            .must_be_set = &.{ 8, 63 },
            .must_be_clear = &.{ 64, BitmapHarness.bitmap_nbits - 1 },
        },
        .{
            .name = "test_fill_set cross-boundary extension after rounded prefix",
            .init_bits = &.{},
            .set_ranges = &.{ .{ .start = 0, .len = 64 }, .{ .start = 79, .len = 19 } },
            .clear_ranges = &.{},
            .fill_prefixes = &.{},
            .zero_prefixes = &.{},
            .expected_summary = .{ .first_set = 0, .first_zero = 64, .weight = 83 },
            .must_be_set = &.{ 63, 79, 97 },
            .must_be_clear = &.{ 64, 78, 98 },
        },
        .{
            .name = "test_fill_set bitmap_fill rounds 115 bits to two full words",
            .init_bits = &.{},
            .set_ranges = &.{ .{ .start = 0, .len = 64 }, .{ .start = 79, .len = 19 } },
            .clear_ranges = &.{},
            .fill_prefixes = &.{115},
            .zero_prefixes = &.{},
            .expected_summary = .{ .first_set = 0, .first_zero = 128, .weight = 128 },
            .must_be_set = &.{ 97, 127 },
            .must_be_clear = &.{ 128, BitmapHarness.bitmap_nbits - 1 },
        },
        .{
            .name = "test_zero_clear single-word starter",
            .init_bits = &.{},
            .set_ranges = &.{.{ .start = 0, .len = BitmapHarness.bitmap_nbits }},
            .clear_ranges = &.{.{ .start = 0, .len = 9 }},
            .fill_prefixes = &.{},
            .zero_prefixes = &.{},
            .expected_summary = .{
                .first_set = 9,
                .first_zero = 0,
                .weight = BitmapHarness.bitmap_nbits - 9,
            },
            .must_be_set = &.{ 9, BitmapHarness.bitmap_nbits - 1 },
            .must_be_clear = &.{ 0, 8 },
        },
        .{
            .name = "test_zero_clear bitmap_zero rounds 35 bits to one full word",
            .init_bits = &.{},
            .set_ranges = &.{.{ .start = 0, .len = BitmapHarness.bitmap_nbits }},
            .clear_ranges = &.{},
            .fill_prefixes = &.{},
            .zero_prefixes = &.{35},
            .expected_summary = .{
                .first_set = 64,
                .first_zero = 0,
                .weight = BitmapHarness.bitmap_nbits - 64,
            },
            .must_be_set = &.{ 64, BitmapHarness.bitmap_nbits - 1 },
            .must_be_clear = &.{ 0, 63 },
        },
        .{
            .name = "test_zero_clear cross-boundary cutout after rounded prefix",
            .init_bits = &.{},
            .set_ranges = &.{.{ .start = 64, .len = BitmapHarness.bitmap_nbits - 64 }},
            .clear_ranges = &.{.{ .start = 79, .len = 19 }},
            .fill_prefixes = &.{},
            .zero_prefixes = &.{},
            .expected_summary = .{
                .first_set = 64,
                .first_zero = 0,
                .weight = BitmapHarness.bitmap_nbits - 64 - 19,
            },
            .must_be_set = &.{ 64, 78, 98, BitmapHarness.bitmap_nbits - 1 },
            .must_be_clear = &.{ 0, 63, 79, 97 },
        },
        .{
            .name = "test_zero_clear bitmap_zero rounds 115 bits to two full words",
            .init_bits = &.{},
            .set_ranges = &.{.{ .start = 0, .len = BitmapHarness.bitmap_nbits }},
            .clear_ranges = &.{},
            .fill_prefixes = &.{},
            .zero_prefixes = &.{115},
            .expected_summary = .{
                .first_set = 128,
                .first_zero = 0,
                .weight = BitmapHarness.bitmap_nbits - 128,
            },
            .must_be_set = &.{ 128, BitmapHarness.bitmap_nbits - 1 },
            .must_be_clear = &.{ 0, 127 },
        },
        .{
            .name = "test_find_nth_bit starter population",
            .init_bits = &.{ 10, 20, 30, 40, 50, 60, 80, 123 },
            .set_ranges = &.{},
            .clear_ranges = &.{},
            .fill_prefixes = &.{},
            .zero_prefixes = &.{},
            .expected_summary = .{ .first_set = 10, .first_zero = 0, .weight = 8 },
            .must_be_set = &.{ 10, 80, 123 },
            .must_be_clear = &.{ 0, 79, 124 },
        },
    };

    for (cases) |case| {
        try expectCase(case);
    }
}

test "bitmap diff gate records exact bounded find_nth_bit checks" {
    const starter_bits = [_]u32{ 10, 20, 30, 40, 50, 60, 80, 123 };
    try expectNthCase(&starter_bits, 64 * 3, &starter_bits);
    try expectNthCase(&starter_bits, 64 * 3 - 1, &starter_bits);
}

test "bitmap diff gate records exact bounded copy checks" {
    const cases = [_]CopyCase{
        .{
            .name = "test_copy zeroed destination preserves 0-18 inside 23-bit window",
            .source_set_len = 19,
            .copy_nbits = 23,
            .destination_fill = false,
            .expected_summary = .{
                .first_set = 0,
                .first_zero = 19,
                .weight = 19,
            },
            .must_be_set = &.{ 0, 18 },
            .must_be_clear = &.{ 19, 22, 23, BitmapHarness.bitmap_nbits - 1 },
        },
        .{
            .name = "test_copy filled destination clears first-word tail after 23-bit copy",
            .source_set_len = 19,
            .copy_nbits = 23,
            .destination_fill = true,
            .expected_summary = .{
                .first_set = 0,
                .first_zero = 19,
                .weight = 19 + (BitmapHarness.bitmap_nbits - 64),
            },
            .must_be_set = &.{ 0, 18, 64, BitmapHarness.bitmap_nbits - 1 },
            .must_be_clear = &.{ 19, 22, 23, 63 },
        },
        .{
            .name = "test_copy partial-word tail clearing at 109 bits",
            .source_set_len = 109,
            .copy_nbits = 109,
            .destination_fill = true,
            .expected_summary = .{
                .first_set = 0,
                .first_zero = 109,
                .weight = 109 + (BitmapHarness.bitmap_nbits - 128),
            },
            .must_be_set = &.{ 108, 128, BitmapHarness.bitmap_nbits - 1 },
            .must_be_clear = &.{ 109, 127 },
        },
        .{
            .name = "test_copy aligned tail clearing at 97 bits",
            .source_set_len = 109,
            .copy_nbits = 97,
            .destination_fill = true,
            .expected_summary = .{
                .first_set = 0,
                .first_zero = 97,
                .weight = 97 + (BitmapHarness.bitmap_nbits - 128),
            },
            .must_be_set = &.{ 96, 128, BitmapHarness.bitmap_nbits - 1 },
            .must_be_clear = &.{ 97, 127 },
        },
        .{
            .name = "test_zero_nbits zero-length copy leaves destination unchanged",
            .source_set_len = 109,
            .copy_nbits = 0,
            .destination_fill = true,
            .expected_summary = .{
                .first_set = 0,
                .first_zero = BitmapHarness.bitmap_nbits,
                .weight = BitmapHarness.bitmap_nbits,
            },
            .must_be_set = &.{ 0, 96, BitmapHarness.bitmap_nbits - 1 },
            .must_be_clear = &.{},
        },
    };

    for (cases) |case| {
        try expectCopyCase(case);
    }
}

test "bitmap diff gate keeps a deterministic threshold replay batch ready for future perf baselines" {
    const single = try runThresholdReplay(1);
    const repeated = try runThresholdReplay(4);

    try std.testing.expectEqual(@as(usize, 1), single.iterations);
    try std.testing.expectEqual(@as(usize, 4), repeated.iterations);
    try std.testing.expectEqual(@as(u32, 0), single.final_first_set);
    try std.testing.expectEqual(@as(u32, 97), single.final_first_zero);
    try std.testing.expectEqual(@as(u32, 993), single.final_weight);
    try std.testing.expect(single.checksum != 0);
    try std.testing.expect(repeated.checksum != 0);
    try std.testing.expect(repeated.checksum != single.checksum);
    try std.testing.expectEqualDeep(repeated, try runThresholdReplay(4));
}
