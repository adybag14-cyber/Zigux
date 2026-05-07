const std = @import("std");

const bitmap_diff_source = @embedFile("bitmap_diff.zig");

const SummaryExpectation = struct {
    first_set: u32,
    first_zero: u32,
    weight: u32,
};

const RangeOp = struct {
    start: u32,
    len: u32,
};

const DestinationInit = union(enum) {
    zero,
    fill,
    prefix_set: u32,
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
    destination_init: DestinationInit,
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
        const rounded = ((nbits + bits_per_long - 1) / bits_per_long) * bits_per_long;
        return @min(bitmap_nbits, rounded);
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
        const words_to_copy = full_words + @intFromBool(tail_bits != 0);

        var index: usize = 0;
        while (index < words_to_copy) : (index += 1) {
            self.words[index] = other.words[index];
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
    final_nth_seven: u32,
};

const BitmapDiffGovernance = struct {
    owner: []const u8,
    rollback_owner: []const u8,
    fallback_anchor: []const u8,
    threshold_posture: []const u8,
};

pub const bitmap_diff_governance = BitmapDiffGovernance{
    .owner = "Shared Subsystems Pod",
    .rollback_owner = "Shared Subsystems Pod",
    .fallback_anchor = "lib/test_bitmap.c",
    .threshold_posture = "threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks",
};

const exp1_find_nth_bits = [_]u32{
    0, 65, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141,
    142, 143, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221,
    222, 223, 256, 258, 260, 262, 264, 266, 268, 270, 272, 274, 276, 278, 280, 282,
    284, 286, 321, 323, 325, 327, 329, 331, 333, 335, 337, 339, 341, 343, 345, 347,
    349, 351, 384, 388, 392, 396, 400, 404, 408, 412, 449, 453, 457, 461, 465, 469,
    473, 477, 512, 513, 514, 515, 516, 517, 518, 519, 520, 521, 522, 523, 524, 525,
    526, 527, 528, 529, 530, 531, 532, 533, 534, 535, 536, 537, 538, 539, 540, 541,
    542, 543, 577, 578, 579, 580, 581, 582, 583, 584, 585, 586, 587, 588, 589, 590,
    591, 592, 593, 594, 595, 596, 597, 598, 599, 600, 601, 602, 603, 604, 605, 606,
    607, 640, 644, 648, 652, 656, 660, 664, 668, 672, 673, 676, 677, 680, 681, 684,
    685, 688, 689, 692, 693, 696, 697, 700, 701, 704, 705, 706, 708, 709, 710, 712,
    713, 714, 716, 717, 718, 720, 721, 722, 724, 725, 726, 728, 729, 730, 732, 733,
    734, 736, 737, 738, 739, 740, 741, 742, 743, 744, 745, 746, 747, 748, 749, 750,
    751, 752, 753, 754, 755, 756, 757, 758, 759, 760, 761, 762, 763, 764, 765, 766,
    767, 847, 927,
};

fn mixThresholdChecksum(checksum: *u64, value: anytype) void {
    checksum.* = checksum.* *% 0x9e3779b185ebca87 +% @as(u64, @intCast(value));
}

fn expectMarker(haystack: []const u8, marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, marker) != null);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var start: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, start, needle)) |index| {
        count += 1;
        start = index + needle.len;
    }
    return count;
}

fn expectSourceCaseGroupCardinality(
    group_header: []const u8,
    next_header: []const u8,
    expected_case_count: usize,
) !void {
    const section_start = std.mem.indexOf(u8, bitmap_diff_source, group_header) orelse
        return error.MissingBitmapCaseGroupHeader;
    const section_end = std.mem.indexOfPos(u8, bitmap_diff_source, section_start, next_header) orelse
        return error.MissingBitmapCaseGroupBoundary;
    const section = bitmap_diff_source[section_start..section_end];
    try std.testing.expectEqual(expected_case_count, countOccurrences(section, ".name = "));
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
    switch (case.destination_init) {
        .zero => try destination.initWithSetBits(&.{}),
        .fill => destination.fill(),
        .prefix_set => |nbits| {
            try destination.initWithSetBits(&.{});
            try destination.setRange(0, nbits);
        },
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

pub fn runThresholdReplay(iterations: usize) !ThresholdReplaySummary {
    if (iterations == 0) return error.EmptyThresholdReplayBatch;

    var bitmap = BitmapHarness{};
    var source = BitmapHarness{};
    var destination = BitmapHarness{};
    var short_source = BitmapHarness{};
    var short_destination = BitmapHarness{};
    var nth_probe = BitmapHarness{};
    var checksum: u64 = 0;

    const starter_bits = [_]u32{ 10, 20, 30, 40, 50, 60, 80, 123 };
    const nth_limit = BitmapHarness.bits_per_long * 3;

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

        try short_source.initWithSetBits(&.{});
        try short_source.setRange(0, 19);
        try short_destination.initWithSetBits(&.{});
        try short_destination.setRange(0, 23);
        try short_destination.copyFrom(&short_source, 23);
        const short_copy_summary = short_destination.summary();
        mixThresholdChecksum(&checksum, short_copy_summary.first_zero);
        mixThresholdChecksum(&checksum, short_copy_summary.weight);

        try nth_probe.initWithSetBits(&starter_bits);
        const nth_seven = try nth_probe.findNthSet(nth_limit, 7);
        const nth_end = try nth_probe.findNthSet(nth_limit, 8);
        mixThresholdChecksum(&checksum, nth_seven);
        mixThresholdChecksum(&checksum, nth_end);
    }

    const final_summary = destination.summary();
    return .{
        .iterations = iterations,
        .checksum = checksum,
        .final_first_set = final_summary.first_set,
        .final_first_zero = final_summary.first_zero,
        .final_weight = final_summary.weight,
        .final_nth_seven = try nth_probe.findNthSet(nth_limit, 7),
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
            .name = "test_fill_set bitmap_fill rounds the 35-bit prefix up to one word",
            .init_bits = &.{},
            .set_ranges = &.{.{ .start = 0, .len = 9 }},
            .clear_ranges = &.{},
            .fill_prefixes = &.{35},
            .zero_prefixes = &.{},
            .expected_summary = .{ .first_set = 0, .first_zero = 64, .weight = 64 },
            .must_be_set = &.{ 8, 34, 63 },
            .must_be_clear = &.{ 64, 127, BitmapHarness.bitmap_nbits - 1 },
        },
        .{
            .name = "test_fill_set cross-boundary extension after exact prefix",
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
            .name = "test_fill_set bitmap_fill rounds the 115-bit prefix up to two words",
            .init_bits = &.{},
            .set_ranges = &.{ .{ .start = 0, .len = 64 }, .{ .start = 79, .len = 19 } },
            .clear_ranges = &.{},
            .fill_prefixes = &.{115},
            .zero_prefixes = &.{},
            .expected_summary = .{ .first_set = 0, .first_zero = 128, .weight = 128 },
            .must_be_set = &.{ 97, 114, 127 },
            .must_be_clear = &.{ 128, BitmapHarness.bitmap_nbits - 1 },
        },
        .{
            .name = "test_fill_set bitmap_fill reaches the full 1024-bit extent",
            .init_bits = &.{},
            .set_ranges = &.{},
            .clear_ranges = &.{},
            .fill_prefixes = &.{BitmapHarness.bitmap_nbits},
            .zero_prefixes = &.{},
            .expected_summary = .{
                .first_set = 0,
                .first_zero = BitmapHarness.bitmap_nbits,
                .weight = BitmapHarness.bitmap_nbits,
            },
            .must_be_set = &.{ 0, 127, BitmapHarness.bitmap_nbits - 1 },
            .must_be_clear = &.{},
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
            .name = "test_zero_clear bitmap_zero rounds the 35-bit prefix up to one word",
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
            .must_be_set = &.{ 64, 127, BitmapHarness.bitmap_nbits - 1 },
            .must_be_clear = &.{ 0, 63 },
        },
        .{
            .name = "test_zero_clear cross-boundary cutout after exact prefix",
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
            .name = "test_zero_clear bitmap_zero rounds the 115-bit prefix up to two words",
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
            .name = "test_zero_clear bitmap_zero reaches the empty 1024-bit extent",
            .init_bits = &.{},
            .set_ranges = &.{.{ .start = 0, .len = BitmapHarness.bitmap_nbits }},
            .clear_ranges = &.{},
            .fill_prefixes = &.{},
            .zero_prefixes = &.{BitmapHarness.bitmap_nbits},
            .expected_summary = .{
                .first_set = BitmapHarness.bitmap_nbits,
                .first_zero = 0,
                .weight = 0,
            },
            .must_be_set = &.{},
            .must_be_clear = &.{ 0, 127, BitmapHarness.bitmap_nbits - 1 },
        },
        .{
            .name = "test_zero_nbits zero-length range and prefix edits leave seeded bits unchanged",
            .init_bits = &.{ 5, 63, 80, 123 },
            .set_ranges = &.{ .{ .start = 5, .len = 0 }, .{ .start = 200, .len = 0 } },
            .clear_ranges = &.{ .{ .start = 63, .len = 0 }, .{ .start = 300, .len = 0 } },
            .fill_prefixes = &.{0},
            .zero_prefixes = &.{0},
            .expected_summary = .{ .first_set = 5, .first_zero = 0, .weight = 4 },
            .must_be_set = &.{ 5, 63, 80, 123 },
            .must_be_clear = &.{ 0, 4, 64, 124 },
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

test "bitmap diff gate replays exact bounded exp1 find_nth_bit enumeration" {
    try expectNthCase(&exp1_find_nth_bits, 64 * 15, &exp1_find_nth_bits);
}

test "bitmap diff gate records exact bounded copy checks" {
    const cases = [_]CopyCase{
        .{
            .name = "test_copy exact 23-bit replay from a cleared destination",
            .source_set_len = 19,
            .copy_nbits = 23,
            .destination_init = .zero,
            .expected_summary = .{
                .first_set = 0,
                .first_zero = 19,
                .weight = 19,
            },
            .must_be_set = &.{ 0, 18 },
            .must_be_clear = &.{ 19, 22, 23, BitmapHarness.bitmap_nbits - 1 },
        },
        .{
            .name = "test_copy exact 23-bit replay clears the stale tail in the destination word",
            .source_set_len = 19,
            .copy_nbits = 23,
            .destination_init = .{ .prefix_set = 23 },
            .expected_summary = .{
                .first_set = 0,
                .first_zero = 19,
                .weight = 19,
            },
            .must_be_set = &.{ 0, 18 },
            .must_be_clear = &.{ 19, 22, 23, BitmapHarness.bitmap_nbits - 1 },
        },
        .{
            .name = "test_copy exact 23-bit replay clears the first-word tail without dropping later filled words",
            .source_set_len = 19,
            .copy_nbits = 23,
            .destination_init = .fill,
            .expected_summary = .{
                .first_set = 0,
                .first_zero = 19,
                .weight = 19 + (BitmapHarness.bitmap_nbits - BitmapHarness.bits_per_long),
            },
            .must_be_set = &.{ 0, 18, 64, 127, BitmapHarness.bitmap_nbits - 1 },
            .must_be_clear = &.{ 19, 22, 23, 63 },
        },
        .{
            .name = "test_copy full-width replay from a cleared destination",
            .source_set_len = 109,
            .copy_nbits = BitmapHarness.bitmap_nbits,
            .destination_init = .zero,
            .expected_summary = .{
                .first_set = 0,
                .first_zero = 109,
                .weight = 109,
            },
            .must_be_set = &.{ 0, 108 },
            .must_be_clear = &.{ 109, 127, BitmapHarness.bitmap_nbits - 1 },
        },
        .{
            .name = "test_copy full-width replay clears a pre-filled destination",
            .source_set_len = 109,
            .copy_nbits = BitmapHarness.bitmap_nbits,
            .destination_init = .fill,
            .expected_summary = .{
                .first_set = 0,
                .first_zero = 109,
                .weight = 109,
            },
            .must_be_set = &.{ 0, 108 },
            .must_be_clear = &.{ 109, 127, BitmapHarness.bitmap_nbits - 1 },
        },
        .{
            .name = "test_copy partial-word tail clearing at 109 bits",
            .source_set_len = 109,
            .copy_nbits = 109,
            .destination_init = .fill,
            .expected_summary = .{
                .first_set = 0,
                .first_zero = 109,
                .weight = 109 + (BitmapHarness.bitmap_nbits - 128),
            },
            .must_be_set = &.{ 108, 128, BitmapHarness.bitmap_nbits - 1 },
            .must_be_clear = &.{ 109, 127 },
        },
        .{
            .name = "test_copy aligned 97-bit replay keeps the full second word before the filled tail resumes",
            .source_set_len = 109,
            .copy_nbits = 97,
            .destination_init = .fill,
            .expected_summary = .{
                .first_set = 0,
                .first_zero = 109,
                .weight = 109 + (BitmapHarness.bitmap_nbits - 128),
            },
            .must_be_set = &.{ 96, 108, 128, BitmapHarness.bitmap_nbits - 1 },
            .must_be_clear = &.{ 109, 127 },
        },
        .{
            .name = "test_zero_nbits zero-length copy leaves destination unchanged",
            .source_set_len = 109,
            .copy_nbits = 0,
            .destination_init = .fill,
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

test "bitmap diff gate rejects an empty threshold replay batch" {
    try std.testing.expectError(error.EmptyThresholdReplayBatch, runThresholdReplay(0));
}

test "bitmap diff gate keeps a deterministic threshold replay batch ready for future perf baselines" {
    const single = try runThresholdReplay(1);
    const repeated = try runThresholdReplay(4);

    try std.testing.expectEqual(@as(usize, 1), single.iterations);
    try std.testing.expectEqual(@as(usize, 4), repeated.iterations);
    try std.testing.expectEqual(@as(u32, 0), single.final_first_set);
    try std.testing.expectEqual(@as(u32, 109), single.final_first_zero);
    try std.testing.expectEqual(@as(u32, 1005), single.final_weight);
    try std.testing.expectEqual(@as(u32, 123), single.final_nth_seven);
    try std.testing.expectEqual(@as(u32, 0), repeated.final_first_set);
    try std.testing.expectEqual(@as(u32, 109), repeated.final_first_zero);
    try std.testing.expectEqual(@as(u32, 1005), repeated.final_weight);
    try std.testing.expectEqual(@as(u32, 123), repeated.final_nth_seven);
    try std.testing.expectEqual(@as(u64, 4641743358357118437), single.checksum);
    try std.testing.expectEqual(@as(u64, 15640590978236698512), repeated.checksum);
    try std.testing.expect(repeated.checksum != single.checksum);
    try std.testing.expectEqualDeep(repeated, try runThresholdReplay(4));
}

test "bitmap diff gate keeps rollback governance explicit" {
    try std.testing.expectEqualStrings("Shared Subsystems Pod", bitmap_diff_governance.owner);
    try std.testing.expectEqualStrings("Shared Subsystems Pod", bitmap_diff_governance.rollback_owner);
    try std.testing.expectEqualStrings("lib/test_bitmap.c", bitmap_diff_governance.fallback_anchor);
    try std.testing.expectEqualStrings(
        "threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks",
        bitmap_diff_governance.threshold_posture,
    );
    try expectMarker(bitmap_diff_source, "pub const bitmap_diff_governance = BitmapDiffGovernance{");
    try expectMarker(bitmap_diff_source, ".owner = \"Shared Subsystems Pod\",");
    try expectMarker(bitmap_diff_source, ".rollback_owner = \"Shared Subsystems Pod\",");
    try expectMarker(bitmap_diff_source, ".fallback_anchor = \"lib/test_bitmap.c\",");
    try expectMarker(
        bitmap_diff_source,
        ".threshold_posture = \"threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks\",",
    );
}

test "bitmap diff gate keeps the current bounded source inventory explicit" {
    try expectSourceCaseGroupCardinality(
        "const cases = [_]DiffCase{",
        "test \"bitmap diff gate records exact bounded find_nth_bit checks\"",
        12,
    );
    try expectSourceCaseGroupCardinality(
        "const cases = [_]CopyCase{",
        "test \"bitmap diff gate rejects an empty threshold replay batch\"",
        8,
    );
    try expectMarker(bitmap_diff_source, "const exp1_find_nth_bits = [_]u32{");
    try expectMarker(bitmap_diff_source, "test_fill_set bitmap_fill rounds the 35-bit prefix up to one word");
    try expectMarker(bitmap_diff_source, "test_fill_set bitmap_fill rounds the 115-bit prefix up to two words");
    try expectMarker(bitmap_diff_source, "test_fill_set bitmap_fill reaches the full 1024-bit extent");
    try expectMarker(bitmap_diff_source, "test_zero_clear bitmap_zero rounds the 35-bit prefix up to one word");
    try expectMarker(bitmap_diff_source, "test_zero_clear bitmap_zero rounds the 115-bit prefix up to two words");
    try expectMarker(bitmap_diff_source, "test_zero_clear bitmap_zero reaches the empty 1024-bit extent");
    try expectMarker(bitmap_diff_source, "test_zero_nbits zero-length range and prefix edits leave seeded bits unchanged");
    try expectMarker(bitmap_diff_source, "test_copy exact 23-bit replay clears the stale tail in the destination word");
    try expectMarker(bitmap_diff_source, "test_copy exact 23-bit replay clears the first-word tail without dropping later filled words");
    try expectMarker(bitmap_diff_source, "test_copy full-width replay from a cleared destination");
    try expectMarker(bitmap_diff_source, "test_copy full-width replay clears a pre-filled destination");
    try expectMarker(bitmap_diff_source, "test_zero_nbits zero-length copy leaves destination unchanged");
    try expectMarker(bitmap_diff_source, "bitmap diff gate replays exact bounded exp1 find_nth_bit enumeration");
    try expectMarker(bitmap_diff_source, "if (iterations == 0) return error.EmptyThresholdReplayBatch;");
    try expectMarker(bitmap_diff_source, "try std.testing.expectError(error.EmptyThresholdReplayBatch, runThresholdReplay(0));");
    try expectMarker(bitmap_diff_source, "try std.testing.expectEqual(@as(u64, 4641743358357118437), single.checksum);");
    try expectMarker(bitmap_diff_source, "try std.testing.expectEqual(@as(u64, 15640590978236698512), repeated.checksum);");
    try expectMarker(bitmap_diff_source, "try std.testing.expectEqual(@as(u32, 0), repeated.final_first_set);");
    try expectMarker(bitmap_diff_source, "try std.testing.expectEqual(@as(u32, 109), repeated.final_first_zero);");
    try expectMarker(bitmap_diff_source, "try std.testing.expectEqual(@as(u32, 1005), repeated.final_weight);");
    try expectMarker(bitmap_diff_source, "try std.testing.expectEqual(@as(u32, 123), repeated.final_nth_seven);");
    try expectMarker(bitmap_diff_source, "pub const bitmap_diff_governance = BitmapDiffGovernance{");
    try expectMarker(bitmap_diff_source, ".owner = \"Shared Subsystems Pod\",");
    try expectMarker(bitmap_diff_source, ".rollback_owner = \"Shared Subsystems Pod\",");
    try expectMarker(bitmap_diff_source, ".fallback_anchor = \"lib/test_bitmap.c\",");
    try expectMarker(bitmap_diff_source, ".threshold_posture = \"threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks\",");
    const replay_start = std.mem.indexOf(
        u8,
        bitmap_diff_source,
        "pub fn runThresholdReplay(iterations: usize) !ThresholdReplaySummary {",
    ) orelse return error.MissingThresholdReplayBody;
    const replay_end = std.mem.indexOfPos(
        u8,
        bitmap_diff_source,
        replay_start,
        "test \"bitmap diff gate replays bounded lib/test_bitmap.c range expectations\"",
    ) orelse return error.MissingThresholdReplayBoundary;
    const replay_body = bitmap_diff_source[replay_start..replay_end];
    try std.testing.expectEqual(@as(usize, 13), countOccurrences(replay_body, "mixThresholdChecksum(&checksum,"));
    try expectMarker(replay_body, "try bitmap.setRange(0, 9);");
    try expectMarker(replay_body, "try bitmap.fillPrefix(35);");
    try expectMarker(replay_body, "try bitmap.zeroPrefix(115);");
    try expectMarker(replay_body, "try destination.copyFrom(&source, 97);");
    try expectMarker(replay_body, "try short_destination.copyFrom(&short_source, 23);");
    try expectMarker(replay_body, "const nth_seven = try nth_probe.findNthSet(nth_limit, 7);");
    try expectMarker(replay_body, "const nth_end = try nth_probe.findNthSet(nth_limit, 8);");
}
