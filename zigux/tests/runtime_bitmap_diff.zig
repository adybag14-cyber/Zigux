const std = @import("std");
const sample = @import("runtime_bitmap_sample");

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

fn expectCase(case: DiffCase) !void {
    var module = sample.RuntimeBitmapSample{};
    try module.initWithSetBits(case.init_bits);

    for (case.set_ranges) |op| {
        try module.setRange(op.start, op.len);
    }
    for (case.clear_ranges) |op| {
        try module.clearRange(op.start, op.len);
    }

    const summary = module.summary();
    try std.testing.expectEqual(case.expected_summary.first_set, summary.first_set);
    try std.testing.expectEqual(case.expected_summary.first_zero, summary.first_zero);
    try std.testing.expectEqual(case.expected_summary.weight, summary.weight);
    try std.testing.expectEqual(sample.RuntimeBitmapSample.bitmap_nbits, summary.nbits);

    for (case.must_be_set) |bit| {
        try std.testing.expect(module.isSet(bit));
    }
    for (case.must_be_clear) |bit| {
        try std.testing.expect(!module.isSet(bit));
    }
}

test "runtime bitmap diff gate replays bounded lib/test_bitmap.c expectations" {
    const cases = [_]DiffCase{
        .{
            .name = "test_fill_set single-word starter",
            .init_bits = &.{},
            .set_ranges = &.{.{ .start = 0, .len = 9 }},
            .clear_ranges = &.{},
            .expected_summary = .{ .first_set = 0, .first_zero = 9, .weight = 9 },
            .must_be_set = &.{ 0, 8 },
            .must_be_clear = &.{ 9, 10, sample.RuntimeBitmapSample.bitmap_nbits - 1 },
        },
        .{
            .name = "test_zero_clear cross-boundary cutout",
            .init_bits = &.{},
            .set_ranges = &.{.{ .start = 0, .len = sample.RuntimeBitmapSample.bitmap_nbits }},
            .clear_ranges = &.{.{ .start = 79, .len = 19 }},
            .expected_summary = .{
                .first_set = 0,
                .first_zero = 79,
                .weight = sample.RuntimeBitmapSample.bitmap_nbits - 19,
            },
            .must_be_set = &.{ 0, 78, 98, sample.RuntimeBitmapSample.bitmap_nbits - 1 },
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

test "runtime bitmap diff gate keeps copy parity and cleared tail semantics explicit" {
    var source = sample.RuntimeBitmapSample{};
    try source.initWithSetBits(&.{});
    try source.setRange(0, 109);

    var destination = sample.RuntimeBitmapSample{};
    try destination.initWithSetBits(&.{});
    try destination.setRange(0, sample.RuntimeBitmapSample.bitmap_nbits);
    try destination.copyFrom(&source);

    const summary = destination.summary();
    try std.testing.expectEqual(@as(u32, 0), summary.first_set);
    try std.testing.expectEqual(@as(u32, 109), summary.first_zero);
    try std.testing.expectEqual(@as(u32, 109), summary.weight);
    try std.testing.expect(destination.isSet(108));
    try std.testing.expect(!destination.isSet(109));
    try std.testing.expect(!destination.isSet(sample.RuntimeBitmapSample.bitmap_nbits - 1));
}
