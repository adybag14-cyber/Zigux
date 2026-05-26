const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const Case = struct {
    raw: usize,
    expected_kind: xarray_slot_view.SlotKind,
    expected_tagged: bool,
    expected_value: ?usize = null,
    expected_error: ?isize = null,
    expected_pointer: ?usize = null,
};

fn expectCase(case: Case) !void {
    const slot = xarray_slot_view.fromRaw(case.raw);

    try testing.expectEqual(case.expected_kind, slot.kind());
    try testing.expectEqual(case.raw, slot.rawValue());
    try testing.expectEqual(case.expected_tagged, xarray_slot_view.isTaggedInternalEntry(case.raw));
    try testing.expectEqual(case.expected_value, slot.value());
    try testing.expectEqual(case.expected_error, slot.errorCode());
    try testing.expectEqual(case.expected_pointer, slot.pointerValue());
}

test "contiguous interleave window alternates value and pointer lanes until the err floor takes over" {
    const cases = [_]Case{
        .{
            .raw = err_ptr.err_floor - 6,
            .expected_kind = .value,
            .expected_tagged = true,
            .expected_value = xa_value.safe_inline_limit - 2,
        },
        .{
            .raw = err_ptr.err_floor - 5,
            .expected_kind = .pointer,
            .expected_tagged = false,
            .expected_pointer = err_ptr.err_floor - 5,
        },
        .{
            .raw = err_ptr.err_floor - 4,
            .expected_kind = .value,
            .expected_tagged = true,
            .expected_value = xa_value.safe_inline_limit - 1,
        },
        .{
            .raw = err_ptr.err_floor - 3,
            .expected_kind = .pointer,
            .expected_tagged = false,
            .expected_pointer = err_ptr.err_floor - 3,
        },
        .{
            .raw = err_ptr.err_floor - 2,
            .expected_kind = .value,
            .expected_tagged = true,
            .expected_value = xa_value.safe_inline_limit,
        },
        .{
            .raw = err_ptr.err_floor - 1,
            .expected_kind = .pointer,
            .expected_tagged = false,
            .expected_pointer = err_ptr.err_floor - 1,
        },
        .{
            .raw = err_ptr.err_floor,
            .expected_kind = .err,
            .expected_tagged = true,
            .expected_error = -4095,
        },
        .{
            .raw = err_ptr.err_floor + 1,
            .expected_kind = .err,
            .expected_tagged = true,
            .expected_error = -4094,
        },
        .{
            .raw = err_ptr.err_floor + 2,
            .expected_kind = .err,
            .expected_tagged = true,
            .expected_error = -4093,
        },
    };

    for (cases, 0..) |case, index| {
        try expectCase(case);
        if (index != 0) {
            try testing.expectEqual(cases[index - 1].raw + 1, case.raw);
        }
    }
}

test "every other raw below the seam stays decodable as the descending inline tail" {
    const oldest_value_raw = err_ptr.err_floor - 6;
    const middle_value_raw = err_ptr.err_floor - 4;
    const newest_value_raw = err_ptr.err_floor - 2;

    try testing.expectEqual(try xa_value.makeValue(xa_value.safe_inline_limit - 2), oldest_value_raw);
    try testing.expectEqual(try xa_value.makeValue(xa_value.safe_inline_limit - 1), middle_value_raw);
    try testing.expectEqual(try xa_value.makeValue(xa_value.safe_inline_limit), newest_value_raw);

    try testing.expectEqual(@as(usize, 2), middle_value_raw - oldest_value_raw);
    try testing.expectEqual(@as(usize, 2), newest_value_raw - middle_value_raw);

    try testing.expectEqual(xa_value.safe_inline_limit - 2, xa_value.toValue(oldest_value_raw));
    try testing.expectEqual(xa_value.safe_inline_limit - 1, xa_value.toValue(middle_value_raw));
    try testing.expectEqual(xa_value.safe_inline_limit, xa_value.toValue(newest_value_raw));

    try testing.expectEqual(xarray_slot_view.SlotKind.pointer, xarray_slot_view.fromRaw(oldest_value_raw + 1).kind());
    try testing.expectEqual(xarray_slot_view.SlotKind.pointer, xarray_slot_view.fromRaw(middle_value_raw + 1).kind());
    try testing.expectEqual(xarray_slot_view.SlotKind.pointer, xarray_slot_view.fromRaw(newest_value_raw + 1).kind());
}

test "constructor outputs and raw rereads agree across the interleave seam" {
    const value_slots = [_]xarray_slot_view.SlotView{
        try xarray_slot_view.fromValue(xa_value.safe_inline_limit - 2),
        try xarray_slot_view.fromValue(xa_value.safe_inline_limit - 1),
        try xarray_slot_view.fromValue(xa_value.safe_inline_limit),
    };
    const pointer_slots = [_]xarray_slot_view.SlotView{
        xarray_slot_view.fromPointer(err_ptr.err_floor - 5),
        xarray_slot_view.fromPointer(err_ptr.err_floor - 3),
        xarray_slot_view.fromPointer(err_ptr.err_floor - 1),
    };
    const err_slots = [_]xarray_slot_view.SlotView{
        xarray_slot_view.fromErrorCode(-4095),
        xarray_slot_view.fromErrorCode(-4094),
        xarray_slot_view.fromErrorCode(-4093),
    };

    for (value_slots) |slot| {
        const reread = xarray_slot_view.fromRaw(slot.rawValue());
        try testing.expectEqual(xarray_slot_view.SlotKind.value, reread.kind());
        try testing.expectEqual(slot.value(), reread.value());
    }

    for (pointer_slots) |slot| {
        const reread = xarray_slot_view.fromRaw(slot.rawValue());
        try testing.expectEqual(xarray_slot_view.SlotKind.pointer, reread.kind());
        try testing.expectEqual(slot.pointerValue(), reread.pointerValue());
    }

    for (err_slots) |slot| {
        const reread = xarray_slot_view.fromRaw(slot.rawValue());
        try testing.expectEqual(xarray_slot_view.SlotKind.err, reread.kind());
        try testing.expectEqual(slot.errorCode(), reread.errorCode());
    }
}
