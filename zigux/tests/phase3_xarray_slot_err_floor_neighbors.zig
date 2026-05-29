const std = @import("std");

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const NeighborCase = struct {
    offset: usize,
    code: isize,
    has_value_tag_bit: bool,
};

fn expectErrNeighbor(case: NeighborCase) !void {
    const raw = err_ptr.err_floor + case.offset;
    const slot = xarray_slot_view.fromRaw(raw);

    try std.testing.expectEqual(err_ptr.fromErrorCode(case.code), raw);
    try std.testing.expectEqual(case.code, err_ptr.toErrorCode(raw));
    try std.testing.expectEqual(case.has_value_tag_bit, (raw & xa_value.value_tag_mask) != 0);
    try std.testing.expectEqual(false, xa_value.isValue(raw));
    try std.testing.expectEqual(true, err_ptr.isErrValue(raw));
    try std.testing.expectEqual(true, xarray_slot_view.isTaggedInternalEntry(raw));

    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
    try std.testing.expectEqual(raw, slot.rawValue());
    try std.testing.expectEqual(false, slot.isNull());
    try std.testing.expectEqual(false, slot.isValue());
    try std.testing.expectEqual(true, slot.isErr());
    try std.testing.expectEqual(false, slot.isPointer());
    try std.testing.expectEqual(@as(?usize, null), slot.value());
    try std.testing.expectEqual(@as(?isize, case.code), slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
}

test "err floor neighbors decode as a contiguous xarray err lane" {
    const cases = [_]NeighborCase{
        .{ .offset = 0, .code = -4095, .has_value_tag_bit = true },
        .{ .offset = 1, .code = -4094, .has_value_tag_bit = false },
        .{ .offset = 2, .code = -4093, .has_value_tag_bit = true },
        .{ .offset = 3, .code = -4092, .has_value_tag_bit = false },
        .{ .offset = 4, .code = -4091, .has_value_tag_bit = true },
        .{ .offset = 5, .code = -4090, .has_value_tag_bit = false },
    };

    for (cases) |case| {
        try expectErrNeighbor(case);
    }
}

test "err floor neighbors remain closed to constructors for other lanes" {
    const err_floor_value_source = xa_value.safe_inline_limit + 1;
    const next_odd_value_source = xa_value.safe_inline_limit + 2;

    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(err_floor_value_source));
    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(err_floor_value_source));
    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(next_odd_value_source));
    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(next_odd_value_source));

    try std.testing.expectEqual(err_ptr.err_floor, (err_floor_value_source << 1) | xa_value.value_tag_mask);
    try std.testing.expectEqual(err_ptr.err_floor + 2, (next_odd_value_source << 1) | xa_value.value_tag_mask);

    const even_err_neighbor = xarray_slot_view.fromRaw(err_ptr.err_floor + 1);
    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, even_err_neighbor.kind());
    try std.testing.expectEqual(@as(?usize, null), even_err_neighbor.pointerValue());
    try std.testing.expectEqual(@as(?usize, null), even_err_neighbor.value());
}
