const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotExpectation = struct {
    slot: xarray_slot_view.SlotView,
    kind: xarray_slot_view.SlotKind,
    raw: usize,
    value: ?usize,
    error_code: ?isize,
    pointer: ?usize,
    tagged_internal: bool,
};

fn expectSlot(expected: SlotExpectation) !void {
    try std.testing.expectEqual(expected.kind, expected.slot.kind());
    try std.testing.expectEqual(expected.raw, expected.slot.rawValue());
    try std.testing.expectEqual(expected.kind == .null, expected.slot.isNull());
    try std.testing.expectEqual(expected.kind == .value, expected.slot.isValue());
    try std.testing.expectEqual(expected.kind == .err, expected.slot.isErr());
    try std.testing.expectEqual(expected.kind == .pointer, expected.slot.isPointer());
    try std.testing.expectEqual(expected.value, expected.slot.value());
    try std.testing.expectEqual(expected.error_code, expected.slot.errorCode());
    try std.testing.expectEqual(expected.pointer, expected.slot.pointerValue());
    try std.testing.expectEqual(expected.tagged_internal, xarray_slot_view.isTaggedInternalEntry(expected.raw));
}

test "xarray slot constructors preserve raw identity across public lanes" {
    const inline_zero = try xarray_slot_view.fromValue(0);
    const inline_top = try xarray_slot_view.fromValue(xa_value.safe_inline_limit);
    const err_floor = xarray_slot_view.fromErrorCode(-@as(isize, @intCast(err_ptr.max_errno)));
    const err_top = xarray_slot_view.fromErrorCode(-1);
    const pointer_low = xarray_slot_view.fromPointer(0x1000);
    const pointer_below_floor = xarray_slot_view.fromPointer(err_ptr.err_floor - 1);

    try expectSlot(.{
        .slot = xarray_slot_view.nullSlot(),
        .kind = .null,
        .raw = 0,
        .value = null,
        .error_code = null,
        .pointer = null,
        .tagged_internal = false,
    });
    try expectSlot(.{
        .slot = inline_zero,
        .kind = .value,
        .raw = xa_value.value_tag_mask,
        .value = 0,
        .error_code = null,
        .pointer = null,
        .tagged_internal = true,
    });
    try expectSlot(.{
        .slot = inline_top,
        .kind = .value,
        .raw = err_ptr.err_floor - 2,
        .value = xa_value.safe_inline_limit,
        .error_code = null,
        .pointer = null,
        .tagged_internal = true,
    });
    try expectSlot(.{
        .slot = err_floor,
        .kind = .err,
        .raw = err_ptr.err_floor,
        .value = null,
        .error_code = -@as(isize, @intCast(err_ptr.max_errno)),
        .pointer = null,
        .tagged_internal = true,
    });
    try expectSlot(.{
        .slot = err_top,
        .kind = .err,
        .raw = std.math.maxInt(usize),
        .value = null,
        .error_code = -1,
        .pointer = null,
        .tagged_internal = true,
    });
    try expectSlot(.{
        .slot = pointer_low,
        .kind = .pointer,
        .raw = 0x1000,
        .value = null,
        .error_code = null,
        .pointer = 0x1000,
        .tagged_internal = false,
    });
    try expectSlot(.{
        .slot = pointer_below_floor,
        .kind = .pointer,
        .raw = err_ptr.err_floor - 1,
        .value = null,
        .error_code = null,
        .pointer = err_ptr.err_floor - 1,
        .tagged_internal = false,
    });
}

test "value constructor rejects sources that would overlap the err_ptr lane" {
    try std.testing.expectError(
        error.ValueWouldOverlapErrPtr,
        xarray_slot_view.fromValue(xa_value.safe_inline_limit + 1),
    );
    try std.testing.expectError(
        error.ValueWouldOverlapErrPtr,
        xarray_slot_view.fromValue(std.math.maxInt(usize)),
    );
}
