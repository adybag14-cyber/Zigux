const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const ExpectedSlot = struct {
    raw: usize,
    kind: xarray_slot_view.SlotKind,
    value: ?usize = null,
    error_code: ?isize = null,
    pointer_value: ?usize = null,
};

fn expectSlot(expected: ExpectedSlot) !void {
    const slot = xarray_slot_view.fromRaw(expected.raw);

    try testing.expectEqual(expected.raw, slot.rawValue());
    try testing.expectEqual(expected.kind, slot.kind());
    try testing.expectEqual(expected.value, slot.value());
    try testing.expectEqual(expected.error_code, slot.errorCode());
    try testing.expectEqual(expected.pointer_value, slot.pointerValue());
}

test "inline-limit raw window stays partitioned across value gap and err lanes" {
    const inline_before = xa_value.safe_inline_limit - 1;
    const inline_top = xa_value.safe_inline_limit;

    const expected = [_]ExpectedSlot{
        .{
            .raw = try xa_value.makeValue(inline_before),
            .kind = .value,
            .value = inline_before,
        },
        .{
            .raw = err_ptr.err_floor - 3,
            .kind = .pointer,
            .pointer_value = err_ptr.err_floor - 3,
        },
        .{
            .raw = try xa_value.makeValue(inline_top),
            .kind = .value,
            .value = inline_top,
        },
        .{
            .raw = err_ptr.err_floor - 1,
            .kind = .pointer,
            .pointer_value = err_ptr.err_floor - 1,
        },
        .{
            .raw = err_ptr.err_floor,
            .kind = .err,
            .error_code = -@as(isize, @intCast(err_ptr.max_errno)),
        },
        .{
            .raw = err_ptr.err_floor + 1,
            .kind = .err,
            .error_code = -@as(isize, @intCast(err_ptr.max_errno - 1)),
        },
    };

    for (expected) |entry| {
        try expectSlot(entry);
    }
}

test "constructor outputs align with the inline ceiling and first err raws" {
    const inline_before = try xarray_slot_view.fromValue(xa_value.safe_inline_limit - 1);
    const inline_top = try xarray_slot_view.fromValue(xa_value.safe_inline_limit);
    const err_floor_slot = xarray_slot_view.fromErrorCode(-@as(isize, @intCast(err_ptr.max_errno)));
    const next_err_slot = xarray_slot_view.fromErrorCode(-@as(isize, @intCast(err_ptr.max_errno - 1)));

    try testing.expectEqual(err_ptr.err_floor - 4, inline_before.rawValue());
    try testing.expectEqual(err_ptr.err_floor - 2, inline_top.rawValue());
    try testing.expectEqual(err_ptr.err_floor, err_floor_slot.rawValue());
    try testing.expectEqual(err_ptr.err_floor + 1, next_err_slot.rawValue());

    try testing.expectEqual(@as(?usize, xa_value.safe_inline_limit - 1), inline_before.value());
    try testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), inline_top.value());
    try testing.expectEqual(@as(?isize, -4095), err_floor_slot.errorCode());
    try testing.expectEqual(@as(?isize, -4094), next_err_slot.errorCode());
}

test "first rejected inline preimage lands directly on the err floor" {
    const overlapping_value = xa_value.safe_inline_limit + 1;
    const overlapping_raw = (overlapping_value << 1) | xa_value.value_tag_mask;
    const slot = xarray_slot_view.fromRaw(overlapping_raw);

    try testing.expectError(
        error.ValueWouldOverlapErrPtr,
        xarray_slot_view.fromValue(overlapping_value),
    );
    try testing.expectEqual(err_ptr.err_floor, overlapping_raw);
    try testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
    try testing.expectEqual(@as(?isize, -4095), slot.errorCode());
    try testing.expectEqual(@as(?usize, null), slot.value());
    try testing.expectEqual(@as(?usize, null), slot.pointerValue());
}
