const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;

const AliasCase = struct {
    offset: usize,
    expected_code: isize,
};

fn rawRejectedValue(offset: usize) usize {
    const rejected_value = xa_value.safe_inline_limit + offset;
    return (rejected_value << 1) | xa_value.value_tag_mask;
}

fn expectRejectedAlias(case: AliasCase) !void {
    const value = xa_value.safe_inline_limit + case.offset;
    const raw = rawRejectedValue(case.offset);
    const slot = xarray_slot_view.fromRaw(raw);

    try std.testing.expect(!xa_value.canRepresent(value));
    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(value));
    try std.testing.expectEqual(err_ptr.err_floor + ((case.offset - 1) * 2), raw);
    try std.testing.expect(err_ptr.isErrValue(raw));
    try std.testing.expect(!xa_value.isValue(raw));

    try std.testing.expectEqual(SlotKind.err, slot.kind());
    try std.testing.expect(!slot.isNull());
    try std.testing.expect(!slot.isValue());
    try std.testing.expect(slot.isErr());
    try std.testing.expect(!slot.isPointer());
    try std.testing.expectEqual(@as(?isize, case.expected_code), slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), slot.value());
    try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
}

test "rejected inline value stride stays in the err_ptr lane" {
    const cases = [_]AliasCase{
        .{ .offset = 1, .expected_code = -4095 },
        .{ .offset = 2, .expected_code = -4093 },
        .{ .offset = 16, .expected_code = -4065 },
        .{ .offset = 2048, .expected_code = -1 },
    };

    for (cases) |case| {
        try expectRejectedAlias(case);
    }
}

test "accepted inline ceiling and adjacent pointer gap bracket the alias stride" {
    const accepted_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const accepted_slot = xarray_slot_view.fromRaw(accepted_raw);
    const pointer_gap_raw = err_ptr.err_floor - 1;
    const pointer_gap_slot = xarray_slot_view.fromRaw(pointer_gap_raw);
    const first_alias_slot = xarray_slot_view.fromRaw(rawRejectedValue(1));

    try std.testing.expectEqual(err_ptr.err_floor - 2, accepted_raw);
    try std.testing.expectEqual(SlotKind.value, accepted_slot.kind());
    try std.testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), accepted_slot.value());
    try std.testing.expectEqual(@as(?isize, null), accepted_slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), accepted_slot.pointerValue());

    try std.testing.expectEqual(SlotKind.pointer, pointer_gap_slot.kind());
    try std.testing.expectEqual(@as(?usize, pointer_gap_raw), pointer_gap_slot.pointerValue());
    try std.testing.expectEqual(@as(?usize, null), pointer_gap_slot.value());
    try std.testing.expectEqual(@as(?isize, null), pointer_gap_slot.errorCode());

    try std.testing.expectEqual(SlotKind.err, first_alias_slot.kind());
    try std.testing.expectEqual(@as(?isize, -4095), first_alias_slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), first_alias_slot.value());
    try std.testing.expectEqual(@as(?usize, null), first_alias_slot.pointerValue());
}

test "even err_ptr raws are errors despite not matching the xa_value tag bit" {
    const raw = err_ptr.fromErrorCode(-4094);
    const slot = xarray_slot_view.fromRaw(raw);

    try std.testing.expect((raw & xa_value.value_tag_mask) == 0);
    try std.testing.expect(err_ptr.isErrValue(raw));
    try std.testing.expect(!xa_value.isValue(raw));
    try std.testing.expectEqual(SlotKind.err, slot.kind());
    try std.testing.expectEqual(@as(?isize, -4094), slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), slot.value());
    try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
}
