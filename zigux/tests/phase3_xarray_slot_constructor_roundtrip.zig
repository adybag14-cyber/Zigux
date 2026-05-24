const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const ConstructorCase = struct {
    name: []const u8,
    slot: xarray_slot_view.SlotView,
    kind: xarray_slot_view.SlotKind,
    value: ?usize,
    error_code: ?isize,
    pointer: ?usize,
    tagged_internal: bool,
};

fn expectCase(expected: ConstructorCase) !void {
    try testing.expectEqual(expected.kind, expected.slot.kind());
    try testing.expectEqual(expected.value, expected.slot.value());
    try testing.expectEqual(expected.error_code, expected.slot.errorCode());
    try testing.expectEqual(expected.pointer, expected.slot.pointerValue());
    try testing.expectEqual(expected.tagged_internal, xarray_slot_view.isTaggedInternalEntry(expected.slot.rawValue()));
    try testing.expectEqual(expected.kind == .null, expected.slot.isNull());
    try testing.expectEqual(expected.kind == .value, expected.slot.isValue());
    try testing.expectEqual(expected.kind == .err, expected.slot.isErr());
    try testing.expectEqual(expected.kind == .pointer, expected.slot.isPointer());
}

fn buildCases() ![7]ConstructorCase {
    return .{
        .{
            .name = "null",
            .slot = xarray_slot_view.nullSlot(),
            .kind = .null,
            .value = null,
            .error_code = null,
            .pointer = null,
            .tagged_internal = false,
        },
        .{
            .name = "inline_zero",
            .slot = try xarray_slot_view.fromValue(0),
            .kind = .value,
            .value = 0,
            .error_code = null,
            .pointer = null,
            .tagged_internal = true,
        },
        .{
            .name = "inline_limit",
            .slot = try xarray_slot_view.fromValue(xa_value.safe_inline_limit),
            .kind = .value,
            .value = xa_value.safe_inline_limit,
            .error_code = null,
            .pointer = null,
            .tagged_internal = true,
        },
        .{
            .name = "gap_pointer",
            .slot = xarray_slot_view.fromPointer(err_ptr.err_floor - 1),
            .kind = .pointer,
            .value = null,
            .error_code = null,
            .pointer = err_ptr.err_floor - 1,
            .tagged_internal = false,
        },
        .{
            .name = "plain_pointer",
            .slot = xarray_slot_view.fromPointer(0x1000),
            .kind = .pointer,
            .value = null,
            .error_code = null,
            .pointer = 0x1000,
            .tagged_internal = false,
        },
        .{
            .name = "err_floor",
            .slot = xarray_slot_view.fromErrorCode(-4095),
            .kind = .err,
            .value = null,
            .error_code = -4095,
            .pointer = null,
            .tagged_internal = true,
        },
        .{
            .name = "err_top",
            .slot = xarray_slot_view.fromErrorCode(-1),
            .kind = .err,
            .value = null,
            .error_code = -1,
            .pointer = null,
            .tagged_internal = true,
        },
    };
}

test "constructor round-trip keeps xarray-slot decoders aligned" {
    const cases = try buildCases();

    for (cases) |expected| {
        try expectCase(expected);
    }
}

test "constructor case counts stay stable across slot lanes" {
    const cases = try buildCases();
    var null_count: usize = 0;
    var value_count: usize = 0;
    var pointer_count: usize = 0;
    var err_count: usize = 0;
    var tagged_internal_count: usize = 0;

    for (cases) |expected| {
        switch (expected.kind) {
            .null => null_count += 1,
            .value => value_count += 1,
            .pointer => pointer_count += 1,
            .err => err_count += 1,
        }
        if (expected.tagged_internal) {
            tagged_internal_count += 1;
        }
    }

    try testing.expectEqual(@as(usize, 1), null_count);
    try testing.expectEqual(@as(usize, 2), value_count);
    try testing.expectEqual(@as(usize, 2), pointer_count);
    try testing.expectEqual(@as(usize, 2), err_count);
    try testing.expectEqual(@as(usize, 4), tagged_internal_count);
}

test "constructor seam ordering stays value then pointer gap then err floor" {
    const inline_limit = try xarray_slot_view.fromValue(xa_value.safe_inline_limit);
    const gap_pointer = xarray_slot_view.fromPointer(err_ptr.err_floor - 1);
    const err_floor = xarray_slot_view.fromErrorCode(-4095);

    try testing.expectEqual(@as(usize, err_ptr.err_floor - 2), inline_limit.rawValue());
    try testing.expectEqual(@as(usize, err_ptr.err_floor - 1), gap_pointer.rawValue());
    try testing.expectEqual(@as(usize, err_ptr.err_floor), err_floor.rawValue());

    try testing.expectEqual(xarray_slot_view.SlotKind.value, inline_limit.kind());
    try testing.expectEqual(xarray_slot_view.SlotKind.pointer, gap_pointer.kind());
    try testing.expectEqual(xarray_slot_view.SlotKind.err, err_floor.kind());

    try testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), inline_limit.value());
    try testing.expectEqual(@as(?usize, err_ptr.err_floor - 1), gap_pointer.pointerValue());
    try testing.expectEqual(@as(?isize, -4095), err_floor.errorCode());
}
