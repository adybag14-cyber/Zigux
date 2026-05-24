const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const RoundtripCase = struct {
    slot: xarray_slot_view.SlotView,
    kind: xarray_slot_view.SlotKind,
    raw: usize,
    tagged_internal: bool,
    value: ?usize,
    error_code: ?isize,
    pointer: ?usize,
};

fn buildRoundtripCases() ![7]RoundtripCase {
    return .{
        .{
            .slot = xarray_slot_view.nullSlot(),
            .kind = .null,
            .raw = 0,
            .tagged_internal = false,
            .value = null,
            .error_code = null,
            .pointer = null,
        },
        .{
            .slot = try xarray_slot_view.fromValue(0),
            .kind = .value,
            .raw = try xa_value.makeValue(0),
            .tagged_internal = true,
            .value = 0,
            .error_code = null,
            .pointer = null,
        },
        .{
            .slot = try xarray_slot_view.fromValue(xa_value.safe_inline_limit),
            .kind = .value,
            .raw = try xa_value.makeValue(xa_value.safe_inline_limit),
            .tagged_internal = true,
            .value = xa_value.safe_inline_limit,
            .error_code = null,
            .pointer = null,
        },
        .{
            .slot = xarray_slot_view.fromPointer(0x1000),
            .kind = .pointer,
            .raw = 0x1000,
            .tagged_internal = false,
            .value = null,
            .error_code = null,
            .pointer = 0x1000,
        },
        .{
            .slot = xarray_slot_view.fromRaw(err_ptr.err_floor - 1),
            .kind = .pointer,
            .raw = err_ptr.err_floor - 1,
            .tagged_internal = false,
            .value = null,
            .error_code = null,
            .pointer = err_ptr.err_floor - 1,
        },
        .{
            .slot = xarray_slot_view.fromErrorCode(-4095),
            .kind = .err,
            .raw = err_ptr.err_floor,
            .tagged_internal = true,
            .value = null,
            .error_code = -4095,
            .pointer = null,
        },
        .{
            .slot = xarray_slot_view.fromErrorCode(-1),
            .kind = .err,
            .raw = err_ptr.fromErrorCode(-1),
            .tagged_internal = true,
            .value = null,
            .error_code = -1,
            .pointer = null,
        },
    };
}

fn countOpenDecoders(slot: xarray_slot_view.SlotView) usize {
    var count: usize = 0;
    if (slot.value() != null) count += 1;
    if (slot.errorCode() != null) count += 1;
    if (slot.pointerValue() != null) count += 1;
    return count;
}

fn expectRoundtripCase(expected: RoundtripCase) !void {
    const bounced = xarray_slot_view.fromRaw(expected.slot.rawValue());

    try testing.expectEqual(expected.raw, expected.slot.rawValue());
    try testing.expectEqual(expected.kind, expected.slot.kind());
    try testing.expectEqual(expected.kind == .null, expected.slot.isNull());
    try testing.expectEqual(expected.kind == .value, expected.slot.isValue());
    try testing.expectEqual(expected.kind == .err, expected.slot.isErr());
    try testing.expectEqual(expected.kind == .pointer, expected.slot.isPointer());
    try testing.expectEqual(expected.tagged_internal, xarray_slot_view.isTaggedInternalEntry(expected.raw));
    try testing.expectEqual(expected.value, expected.slot.value());
    try testing.expectEqual(expected.error_code, expected.slot.errorCode());
    try testing.expectEqual(expected.pointer, expected.slot.pointerValue());

    try testing.expectEqual(expected.raw, bounced.rawValue());
    try testing.expectEqual(expected.kind, bounced.kind());
    try testing.expectEqual(expected.value, bounced.value());
    try testing.expectEqual(expected.error_code, bounced.errorCode());
    try testing.expectEqual(expected.pointer, bounced.pointerValue());
    try testing.expectEqual(countOpenDecoders(expected.slot), countOpenDecoders(bounced));
    if (expected.kind == .null) {
        try testing.expectEqual(@as(usize, 0), countOpenDecoders(expected.slot));
    } else {
        try testing.expectEqual(@as(usize, 1), countOpenDecoders(expected.slot));
    }
}

test "constructor-produced slots survive a raw roundtrip without changing lanes" {
    const cases = try buildRoundtripCases();

    for (cases) |expected| {
        try expectRoundtripCase(expected);
    }
}

test "constructor roundtrip keeps the inline-limit seam exact" {
    const inline_limit = try xarray_slot_view.fromValue(xa_value.safe_inline_limit);
    const gap = xarray_slot_view.fromRaw(err_ptr.err_floor - 1);
    const err_floor = xarray_slot_view.fromErrorCode(-4095);

    try testing.expectEqual(err_ptr.err_floor - 2, inline_limit.rawValue());
    try testing.expectEqual(@as(usize, 1), gap.rawValue() - inline_limit.rawValue());
    try testing.expectEqual(@as(usize, 1), err_floor.rawValue() - gap.rawValue());

    try testing.expectEqual(xarray_slot_view.SlotKind.value, xarray_slot_view.fromRaw(inline_limit.rawValue()).kind());
    try testing.expectEqual(xarray_slot_view.SlotKind.pointer, xarray_slot_view.fromRaw(gap.rawValue()).kind());
    try testing.expectEqual(xarray_slot_view.SlotKind.err, xarray_slot_view.fromRaw(err_floor.rawValue()).kind());

    try testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), xarray_slot_view.fromRaw(inline_limit.rawValue()).value());
    try testing.expectEqual(@as(?usize, err_ptr.err_floor - 1), xarray_slot_view.fromRaw(gap.rawValue()).pointerValue());
    try testing.expectEqual(@as(?isize, -4095), xarray_slot_view.fromRaw(err_floor.rawValue()).errorCode());
}

test "constructor roundtrip keeps lane counts and decoder openness stable" {
    const cases = try buildRoundtripCases();
    var null_count: usize = 0;
    var value_count: usize = 0;
    var pointer_count: usize = 0;
    var err_count: usize = 0;
    var tagged_internal_count: usize = 0;
    var open_decoder_count: usize = 0;

    for (cases) |expected| {
        const bounced = xarray_slot_view.fromRaw(expected.slot.rawValue());
        switch (bounced.kind()) {
            .null => null_count += 1,
            .value => value_count += 1,
            .pointer => pointer_count += 1,
            .err => err_count += 1,
        }
        if (xarray_slot_view.isTaggedInternalEntry(bounced.rawValue())) {
            tagged_internal_count += 1;
        }
        open_decoder_count += countOpenDecoders(bounced);
    }

    try testing.expectEqual(@as(usize, 1), null_count);
    try testing.expectEqual(@as(usize, 2), value_count);
    try testing.expectEqual(@as(usize, 2), pointer_count);
    try testing.expectEqual(@as(usize, 2), err_count);
    try testing.expectEqual(@as(usize, 4), tagged_internal_count);
    try testing.expectEqual(@as(usize, 6), open_decoder_count);
}
