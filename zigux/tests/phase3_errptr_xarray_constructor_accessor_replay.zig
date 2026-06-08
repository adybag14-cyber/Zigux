const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;

const SlotExpectation = struct {
    raw: usize,
    kind: SlotKind,
    value: ?usize,
    code: ?isize,
    pointer: ?usize,
    tagged: bool,
};

fn expectSlot(expected: SlotExpectation) !void {
    const slot = xarray_slot_view.fromRaw(expected.raw);

    try std.testing.expectEqual(expected.raw, slot.rawValue());
    try std.testing.expectEqual(expected.kind, slot.kind());
    try std.testing.expectEqual(expected.kind == .null, slot.isNull());
    try std.testing.expectEqual(expected.kind == .value, slot.isValue());
    try std.testing.expectEqual(expected.kind == .err, slot.isErr());
    try std.testing.expectEqual(expected.kind == .pointer, slot.isPointer());
    try std.testing.expectEqual(expected.value, slot.value());
    try std.testing.expectEqual(expected.code, slot.errorCode());
    try std.testing.expectEqual(expected.pointer, slot.pointerValue());
    try std.testing.expectEqual(expected.tagged, slot.isTaggedEntry());
    try std.testing.expectEqual(xarray_slot_view.isTaggedInternalEntry(expected.raw), slot.isTaggedEntry());
}

test "public constructors replay through optional accessors" {
    const null_slot = xarray_slot_view.nullSlot();
    const first_value = try xarray_slot_view.fromValue(0);
    const wide_value = try xarray_slot_view.fromValue(4095);
    const pointer_slot = xarray_slot_view.fromPointer(0x2000);
    const floor_err = xarray_slot_view.fromErrorCode(-@as(isize, @intCast(err_ptr.max_errno)));
    const middle_err = xarray_slot_view.fromErrorCode(-512);
    const top_err = xarray_slot_view.fromErrorCode(-1);

    try expectSlot(.{
        .raw = null_slot.rawValue(),
        .kind = .null,
        .value = null,
        .code = null,
        .pointer = null,
        .tagged = false,
    });
    try expectSlot(.{
        .raw = first_value.rawValue(),
        .kind = .value,
        .value = 0,
        .code = null,
        .pointer = null,
        .tagged = true,
    });
    try expectSlot(.{
        .raw = wide_value.rawValue(),
        .kind = .value,
        .value = 4095,
        .code = null,
        .pointer = null,
        .tagged = true,
    });
    try expectSlot(.{
        .raw = pointer_slot.rawValue(),
        .kind = .pointer,
        .value = null,
        .code = null,
        .pointer = 0x2000,
        .tagged = false,
    });
    try expectSlot(.{
        .raw = floor_err.rawValue(),
        .kind = .err,
        .value = null,
        .code = -@as(isize, @intCast(err_ptr.max_errno)),
        .pointer = null,
        .tagged = true,
    });
    try expectSlot(.{
        .raw = middle_err.rawValue(),
        .kind = .err,
        .value = null,
        .code = -512,
        .pointer = null,
        .tagged = true,
    });
    try expectSlot(.{
        .raw = top_err.rawValue(),
        .kind = .err,
        .value = null,
        .code = -1,
        .pointer = null,
        .tagged = true,
    });
}

test "boundary rows keep constructor accessors closed on neighboring lanes" {
    const last_inline = try xa_value.makeValue(xa_value.safe_inline_limit);
    const last_pointer = err_ptr.err_floor - 1;
    const first_error = err_ptr.err_floor;

    try expectSlot(.{
        .raw = last_inline,
        .kind = .value,
        .value = xa_value.safe_inline_limit,
        .code = null,
        .pointer = null,
        .tagged = true,
    });
    try expectSlot(.{
        .raw = last_pointer,
        .kind = .pointer,
        .value = null,
        .code = null,
        .pointer = last_pointer,
        .tagged = false,
    });
    try expectSlot(.{
        .raw = first_error,
        .kind = .err,
        .value = null,
        .code = -@as(isize, @intCast(err_ptr.max_errno)),
        .pointer = null,
        .tagged = true,
    });

    try std.testing.expectError(
        error.ValueWouldOverlapErrPtr,
        xarray_slot_view.fromValue(xa_value.safe_inline_limit + 1),
    );
}
