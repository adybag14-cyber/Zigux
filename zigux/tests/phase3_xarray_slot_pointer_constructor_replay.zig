const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;

fn expectPointerConstructor(raw: usize) !void {
    const constructed = xarray_slot_view.fromPointer(raw);
    const decoded = xarray_slot_view.fromRaw(raw);

    try std.testing.expectEqual(SlotKind.pointer, constructed.kind());
    try std.testing.expectEqual(SlotKind.pointer, decoded.kind());
    try std.testing.expectEqual(raw, constructed.rawValue());
    try std.testing.expectEqual(raw, constructed.pointerValue().?);
    try std.testing.expectEqual(@as(?usize, raw), decoded.pointerValue());
    try std.testing.expectEqual(@as(?usize, null), constructed.value());
    try std.testing.expectEqual(@as(?isize, null), constructed.errorCode());
    try std.testing.expect(!xarray_slot_view.isTaggedInternalEntry(raw));
}

fn expectTaggedRaw(raw: usize, kind: SlotKind) !void {
    const slot = xarray_slot_view.fromRaw(raw);

    try std.testing.expectEqual(kind, slot.kind());
    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
    try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
}

test "fromPointer admits only non-null untagged slot representatives" {
    const admitted = [_]usize{
        2,
        0x1000,
        err_ptr.err_floor - 3,
        err_ptr.err_floor - 1,
    };

    for (admitted) |raw| {
        try std.testing.expect(raw != 0);
        try expectPointerConstructor(raw);
    }
}

test "raw neighbors around admitted pointer slots stay in their own lanes" {
    try std.testing.expectEqual(SlotKind.null, xarray_slot_view.fromRaw(0).kind());
    try expectTaggedRaw(try xa_value.makeValue(0), .value);
    try expectPointerConstructor(try xa_value.makeValue(0) + 1);

    try expectTaggedRaw(err_ptr.err_floor - 2, .value);
    try expectPointerConstructor(err_ptr.err_floor - 1);
    try expectTaggedRaw(err_ptr.err_floor, .err);
    try expectTaggedRaw(err_ptr.fromErrorCode(-1), .err);
}
