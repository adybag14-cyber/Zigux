const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;

fn expectSlot(
    raw: usize,
    expected_kind: SlotKind,
    expected_value: ?usize,
    expected_error: ?isize,
    expected_pointer: ?usize,
) !void {
    const slot = xarray_slot_view.fromRaw(raw);

    try std.testing.expectEqual(expected_kind, slot.kind());
    try std.testing.expectEqual(raw, slot.rawValue());
    try std.testing.expectEqual(expected_kind == .null, slot.isNull());
    try std.testing.expectEqual(expected_kind == .value, slot.isValue());
    try std.testing.expectEqual(expected_kind == .err, slot.isErr());
    try std.testing.expectEqual(expected_kind == .pointer, slot.isPointer());
    try std.testing.expectEqual(expected_value, slot.value());
    try std.testing.expectEqual(expected_error, slot.errorCode());
    try std.testing.expectEqual(expected_pointer, slot.pointerValue());
}

test "xarray slot error span keeps err_ptr precedence across representative errno raws" {
    const cases = [_]isize{
        -@as(isize, @intCast(err_ptr.max_errno)),
        -4094,
        -2048,
        -512,
        -22,
        -1,
    };

    for (cases) |code| {
        const raw = err_ptr.fromErrorCode(code);

        try expectSlot(raw, .err, null, code, null);
        try std.testing.expect(err_ptr.isErrValue(raw));
        try std.testing.expect(!xa_value.isValue(raw));
        try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
    }
}

test "xarray slot boundary span separates accepted values, pointer gaps, and rejected aliases" {
    const inline_zero = try xa_value.makeValue(0);
    const inline_top = try xa_value.makeValue(xa_value.safe_inline_limit);
    const pointer_gap = err_ptr.err_floor - 1;
    const rejected_floor_alias = (xa_value.safe_inline_limit + 1) << 1 | xa_value.value_tag_mask;
    const rejected_next_alias = (xa_value.safe_inline_limit + 2) << 1 | xa_value.value_tag_mask;

    try expectSlot(0, .null, null, null, null);
    try expectSlot(inline_zero, .value, 0, null, null);
    try expectSlot(inline_top, .value, xa_value.safe_inline_limit, null, null);
    try expectSlot(pointer_gap, .pointer, null, null, pointer_gap);
    try expectSlot(rejected_floor_alias, .err, null, -4095, null);
    try expectSlot(rejected_next_alias, .err, null, -4093, null);

    try std.testing.expectEqual(err_ptr.err_floor - 2, inline_top);
    try std.testing.expectEqual(err_ptr.err_floor, rejected_floor_alias);
    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(xa_value.safe_inline_limit + 1));
    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(xa_value.safe_inline_limit + 2));
}
