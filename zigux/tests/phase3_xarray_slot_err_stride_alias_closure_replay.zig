const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const AliasCase = struct {
    rejected_value: usize,
    error_code: isize,
};

fn rejectedAliasRaw(value: usize) usize {
    return (value << 1) | xa_value.value_tag_mask;
}

fn expectErrSlot(raw: usize, code: isize, tagged: bool) !void {
    const slot = xarray_slot_view.fromRaw(raw);

    try testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
    try testing.expect(slot.isErr());
    try testing.expect(!slot.isValue());
    try testing.expect(!slot.isPointer());
    try testing.expectEqual(raw, slot.rawValue());
    try testing.expectEqual(@as(?isize, code), slot.errorCode());
    try testing.expectEqual(@as(?usize, null), slot.value());
    try testing.expectEqual(@as(?usize, null), slot.pointerValue());
    try testing.expectEqual(tagged, slot.isTaggedEntry());
}

test "rejected inline aliases stride through odd err_ptr slots without becoming values" {
    const cases = [_]AliasCase{
        .{
            .rejected_value = xa_value.safe_inline_limit + 1,
            .error_code = -4095,
        },
        .{
            .rejected_value = xa_value.safe_inline_limit + 64,
            .error_code = -3969,
        },
        .{
            .rejected_value = xa_value.safe_inline_limit + 1024,
            .error_code = -2049,
        },
        .{
            .rejected_value = xa_value.safe_inline_limit + 2048,
            .error_code = -1,
        },
    };

    for (cases) |case| {
        const raw = rejectedAliasRaw(case.rejected_value);

        try testing.expect(!xa_value.canRepresent(case.rejected_value));
        try testing.expectEqual(err_ptr.fromErrorCode(case.error_code), raw);
        try testing.expect(!xa_value.isValue(raw));
        try expectErrSlot(raw, case.error_code, true);
    }
}

test "even err_ptr slots between rejected aliases stay errors without value tags" {
    const even_errs = [_]isize{ -4094, -3968, -2048, -2 };

    for (even_errs) |code| {
        const raw = err_ptr.fromErrorCode(code);

        try testing.expect((raw & xa_value.value_tag_mask) == 0);
        try testing.expect(err_ptr.isErrValue(raw));
        try testing.expect(!xa_value.isValue(raw));
        try expectErrSlot(raw, code, true);
    }
}

test "the one raw gap before the first rejected alias remains pointer-like" {
    const gap_raw = err_ptr.err_floor - 1;
    const first_alias_raw = rejectedAliasRaw(xa_value.safe_inline_limit + 1);
    const gap_slot = xarray_slot_view.fromRaw(gap_raw);

    try testing.expectEqual(gap_raw + 1, first_alias_raw);
    try testing.expect(err_ptr.isOkValue(gap_raw));
    try testing.expect(!xarray_slot_view.isTaggedInternalEntry(gap_raw));
    try testing.expectEqual(xarray_slot_view.SlotKind.pointer, gap_slot.kind());
    try testing.expectEqual(@as(?usize, gap_raw), gap_slot.pointerValue());
    try testing.expectEqual(@as(?usize, null), gap_slot.value());
    try testing.expectEqual(@as(?isize, null), gap_slot.errorCode());
}
