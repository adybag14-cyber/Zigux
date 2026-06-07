const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const errno: isize = -415;
const next_errno: isize = -416;
const raw = err_ptr.fromErrorCode(errno);
const next_raw = err_ptr.fromErrorCode(next_errno);

test "errno 415 keeps xarray slot error decoding closed over adjacent lanes" {
    const slot = xarray_slot_view.fromRaw(raw);

    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
    try std.testing.expect(slot.isErr());
    try std.testing.expect(!slot.isNull());
    try std.testing.expect(!slot.isValue());
    try std.testing.expect(!slot.isPointer());
    try std.testing.expect(slot.isTaggedEntry());
    try std.testing.expectEqual(raw, slot.rawValue());
    try std.testing.expectEqual(@as(?isize, errno), slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), slot.value());
    try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
}

test "errno 415 raw equation stays between its errno neighbors" {
    const previous_errno_raw = err_ptr.fromErrorCode(errno + 1);

    try std.testing.expectEqual(@as(usize, 1), previous_errno_raw - raw);
    try std.testing.expectEqual(@as(usize, 1), raw - next_raw);
    try std.testing.expect(err_ptr.isErrValue(raw));
    try std.testing.expect(!err_ptr.isOkValue(raw));
    try std.testing.expectEqual(errno, err_ptr.toErrorCode(raw));
}

test "errno 415 adjacent raw lanes keep value and pointer decoders precise" {
    const even_before = raw - 1;
    const even_after = raw + 1;
    const even_before_slot = xarray_slot_view.fromRaw(even_before);
    const even_after_slot = xarray_slot_view.fromRaw(even_after);

    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, even_before_slot.kind());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, even_after_slot.kind());
    try std.testing.expect(!xa_value.isValue(raw));
    try std.testing.expect(!xa_value.isValue(even_before));
    try std.testing.expect(!xa_value.isValue(even_after));
    try std.testing.expectEqual(@as(?usize, null), even_before_slot.pointerValue());
    try std.testing.expectEqual(@as(?usize, null), even_after_slot.pointerValue());
}
