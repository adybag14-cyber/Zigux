const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

test "cutoff seam keeps all four adjacent raw lanes explicit" {
    const accepted_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const gap_raw = err_ptr.err_floor - 1;
    const tagged_err_raw = err_ptr.err_floor;
    const even_err_raw = err_ptr.err_floor + 1;

    const accepted_slot = xarray_slot_view.fromRaw(accepted_raw);
    const gap_slot = xarray_slot_view.fromRaw(gap_raw);
    const tagged_err_slot = xarray_slot_view.fromRaw(tagged_err_raw);
    const even_err_slot = xarray_slot_view.fromRaw(even_err_raw);

    try std.testing.expectEqual(err_ptr.err_floor - 2, accepted_raw);
    try std.testing.expectEqual(accepted_raw + 1, gap_raw);
    try std.testing.expectEqual(gap_raw + 1, tagged_err_raw);
    try std.testing.expectEqual(tagged_err_raw + 1, even_err_raw);

    try std.testing.expectEqual(xarray_slot_view.SlotKind.value, accepted_slot.kind());
    try std.testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), accepted_slot.value());
    try std.testing.expectEqual(@as(?isize, null), accepted_slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), accepted_slot.pointerValue());

    try std.testing.expectEqual(xarray_slot_view.SlotKind.pointer, gap_slot.kind());
    try std.testing.expectEqual(@as(?usize, null), gap_slot.value());
    try std.testing.expectEqual(@as(?isize, null), gap_slot.errorCode());
    try std.testing.expectEqual(@as(?usize, gap_raw), gap_slot.pointerValue());

    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, tagged_err_slot.kind());
    try std.testing.expectEqual(@as(?usize, null), tagged_err_slot.value());
    try std.testing.expectEqual(@as(?isize, -4095), tagged_err_slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), tagged_err_slot.pointerValue());

    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, even_err_slot.kind());
    try std.testing.expectEqual(@as(?usize, null), even_err_slot.value());
    try std.testing.expectEqual(@as(?isize, -4094), even_err_slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), even_err_slot.pointerValue());
}

test "cutoff seam helper classifiers stay aligned across the boundary" {
    const accepted_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const gap_raw = err_ptr.err_floor - 1;
    const tagged_err_raw = err_ptr.err_floor;
    const even_err_raw = err_ptr.err_floor + 1;

    try std.testing.expect(xa_value.isValue(accepted_raw));
    try std.testing.expect(!err_ptr.isErrValue(accepted_raw));
    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(accepted_raw));

    try std.testing.expect(!xa_value.isValue(gap_raw));
    try std.testing.expect(!err_ptr.isErrValue(gap_raw));
    try std.testing.expect(!xarray_slot_view.isTaggedInternalEntry(gap_raw));

    try std.testing.expect(!xa_value.isValue(tagged_err_raw));
    try std.testing.expect(err_ptr.isErrValue(tagged_err_raw));
    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(tagged_err_raw));

    try std.testing.expect(!xa_value.isValue(even_err_raw));
    try std.testing.expect(err_ptr.isErrValue(even_err_raw));
    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(even_err_raw));
}
