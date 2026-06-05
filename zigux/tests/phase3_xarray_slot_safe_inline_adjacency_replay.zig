const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn expectSlot(
    raw: usize,
    kind: xarray_slot_view.SlotKind,
    value: ?usize,
    error_code: ?isize,
    pointer: ?usize,
    tagged: bool,
) !void {
    const slot = xarray_slot_view.fromRaw(raw);

    try testing.expectEqual(kind, slot.kind());
    try testing.expectEqual(raw, slot.rawValue());
    try testing.expectEqual(value, slot.value());
    try testing.expectEqual(error_code, slot.errorCode());
    try testing.expectEqual(pointer, slot.pointerValue());
    try testing.expectEqual(tagged, slot.isTaggedEntry());
    try testing.expectEqual(tagged, xarray_slot_view.isTaggedInternalEntry(raw));
}

test "safe inline limit, pointer gap, and err floor stay adjacent but disjoint" {
    const inline_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const gap_raw = err_ptr.err_floor - 1;
    const floor_raw = err_ptr.fromErrorCode(-@as(isize, @intCast(err_ptr.max_errno)));

    try testing.expectEqual(err_ptr.err_floor - 2, inline_raw);
    try testing.expectEqual(inline_raw + 1, gap_raw);
    try testing.expectEqual(gap_raw + 1, floor_raw);

    try expectSlot(
        inline_raw,
        .value,
        xa_value.safe_inline_limit,
        null,
        null,
        true,
    );
    try expectSlot(gap_raw, .pointer, null, null, gap_raw, false);
    try expectSlot(floor_raw, .err, null, -4095, null, true);
}

test "public constructors agree with raw adjacency at the safe inline edge" {
    const value_slot = try xarray_slot_view.fromValue(xa_value.safe_inline_limit);
    const gap_slot = xarray_slot_view.fromPointer(err_ptr.err_floor - 1);
    const err_slot = xarray_slot_view.fromErrorCode(-4095);

    try testing.expectEqual(err_ptr.err_floor - 2, value_slot.rawValue());
    try testing.expectEqual(err_ptr.err_floor - 1, gap_slot.rawValue());
    try testing.expectEqual(err_ptr.err_floor, err_slot.rawValue());

    try testing.expectEqual(xarray_slot_view.SlotKind.value, value_slot.kind());
    try testing.expectEqual(xarray_slot_view.SlotKind.pointer, gap_slot.kind());
    try testing.expectEqual(xarray_slot_view.SlotKind.err, err_slot.kind());

    try testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), value_slot.value());
    try testing.expectEqual(@as(?usize, err_ptr.err_floor - 1), gap_slot.pointerValue());
    try testing.expectEqual(@as(?isize, -4095), err_slot.errorCode());

    try testing.expectError(
        error.ValueWouldOverlapErrPtr,
        xarray_slot_view.fromValue(xa_value.safe_inline_limit + 1),
    );
}
