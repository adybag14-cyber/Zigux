const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const AliasCase = struct {
    rejected_value: usize,
    error_code: isize,
};

fn assertRejectedAlias(case: AliasCase) !void {
    const raw = (case.rejected_value << 1) | xa_value.value_tag_mask;
    const slot = xarray_slot_view.fromRaw(raw);

    try std.testing.expect(!xa_value.canRepresent(case.rejected_value));
    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(case.rejected_value));
    try std.testing.expectEqual(err_ptr.fromErrorCode(case.error_code), raw);
    try std.testing.expect((raw & xa_value.value_tag_mask) == xa_value.value_tag_mask);
    try std.testing.expect(err_ptr.isErrValue(raw));
    try std.testing.expect(!xa_value.isValue(raw));

    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
    try std.testing.expect(slot.isErr());
    try std.testing.expect(!slot.isValue());
    try std.testing.expect(!slot.isPointer());
    try std.testing.expectEqual(@as(?usize, null), slot.value());
    try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
    try std.testing.expectEqual(@as(?isize, case.error_code), slot.errorCode());
    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
}

test "rejected inline aliases decode through the err_ptr lane" {
    const cases = [_]AliasCase{
        .{
            .rejected_value = xa_value.safe_inline_limit + 1,
            .error_code = -@as(isize, @intCast(err_ptr.max_errno)),
        },
        .{
            .rejected_value = xa_value.safe_inline_limit + 2,
            .error_code = -@as(isize, @intCast(err_ptr.max_errno - 2)),
        },
        .{
            .rejected_value = (err_ptr.fromErrorCode(-257) >> 1),
            .error_code = -257,
        },
        .{
            .rejected_value = (err_ptr.fromErrorCode(-1) >> 1),
            .error_code = -1,
        },
    };

    for (cases) |case| {
        try assertRejectedAlias(case);
    }
}

test "constructor and raw decoding stay split across the alias boundary" {
    const accepted = try xarray_slot_view.fromValue(xa_value.safe_inline_limit);
    const rejected_raw = ((xa_value.safe_inline_limit + 1) << 1) | xa_value.value_tag_mask;
    const rejected = xarray_slot_view.fromRaw(rejected_raw);
    const gap = xarray_slot_view.fromRaw(err_ptr.err_floor - 1);

    try std.testing.expectEqual(xarray_slot_view.SlotKind.value, accepted.kind());
    try std.testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), accepted.value());
    try std.testing.expectEqual(@as(?isize, null), accepted.errorCode());
    try std.testing.expectEqual(err_ptr.err_floor - 2, accepted.rawValue());

    try std.testing.expectError(
        error.ValueWouldOverlapErrPtr,
        xarray_slot_view.fromValue(xa_value.safe_inline_limit + 1),
    );
    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, rejected.kind());
    try std.testing.expectEqual(@as(?isize, -@as(isize, @intCast(err_ptr.max_errno))), rejected.errorCode());
    try std.testing.expectEqual(err_ptr.err_floor, rejected.rawValue());

    try std.testing.expectEqual(xarray_slot_view.SlotKind.pointer, gap.kind());
    try std.testing.expectEqual(@as(?usize, err_ptr.err_floor - 1), gap.pointerValue());
    try std.testing.expectEqual(@as(?usize, null), gap.value());
    try std.testing.expectEqual(@as(?isize, null), gap.errorCode());
    try std.testing.expect(!xarray_slot_view.isTaggedInternalEntry(gap.rawValue()));
}
