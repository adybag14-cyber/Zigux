const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const PointerCase = struct {
    raw: usize,
};

fn expectPointerAdmission(case: PointerCase) !void {
    const slot = xarray_slot_view.fromPointer(case.raw);

    try std.testing.expectEqual(xarray_slot_view.SlotKind.pointer, slot.kind());
    try std.testing.expectEqual(case.raw, slot.rawValue());
    try std.testing.expect(!slot.isNull());
    try std.testing.expect(!slot.isValue());
    try std.testing.expect(!slot.isErr());
    try std.testing.expect(slot.isPointer());
    try std.testing.expectEqual(@as(?usize, case.raw), slot.pointerValue());
    try std.testing.expectEqual(@as(?usize, null), slot.value());
    try std.testing.expectEqual(@as(?isize, null), slot.errorCode());
    try std.testing.expect(!xarray_slot_view.isTaggedInternalEntry(case.raw));
    try std.testing.expect(!err_ptr.isErrValue(case.raw));
    try std.testing.expect(!xa_value.isValue(case.raw));
}

test "pointer constructor admits only untagged non-null slot raws" {
    const cases = [_]PointerCase{
        .{ .raw = 0x2 },
        .{ .raw = 0x1000 },
        .{ .raw = err_ptr.err_floor - 3 },
        .{ .raw = err_ptr.err_floor - 1 },
    };

    for (cases) |case| {
        try expectPointerAdmission(case);
    }
}

test "internal xarray entries stay outside pointer admission" {
    const internal = [_]usize{
        try xa_value.makeValue(0),
        try xa_value.makeValue(1),
        try xa_value.makeValue(xa_value.safe_inline_limit),
        err_ptr.err_floor - 4,
        err_ptr.err_floor - 2,
        err_ptr.err_floor,
        err_ptr.fromErrorCode(-22),
        err_ptr.fromErrorCode(-1),
    };

    for (internal) |raw| {
        const slot = xarray_slot_view.fromRaw(raw);

        try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
        try std.testing.expect(!slot.isPointer());
        try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
    }
}

test "null remains its own xarray slot lane" {
    const null_slot = xarray_slot_view.nullSlot();

    try std.testing.expectEqual(xarray_slot_view.SlotKind.null, null_slot.kind());
    try std.testing.expectEqual(@as(usize, 0), null_slot.rawValue());
    try std.testing.expect(null_slot.isNull());
    try std.testing.expect(!null_slot.isPointer());
    try std.testing.expect(!xarray_slot_view.isTaggedInternalEntry(0));
}
