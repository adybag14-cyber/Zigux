const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const ErrnoCase = struct {
    code: isize,
    has_value_tag_bit: bool,
};

const AdjacentErrnoPair = struct {
    higher_code: isize,
    lower_code: isize,
    higher_has_value_tag_bit: bool,
    lower_has_value_tag_bit: bool,
};

fn expectErrLane(case: ErrnoCase) !void {
    const raw = err_ptr.fromErrorCode(case.code);
    const slot = xarray_slot_view.fromRaw(raw);

    try std.testing.expectEqual(case.has_value_tag_bit, (raw & xa_value.value_tag_mask) == xa_value.value_tag_mask);
    try std.testing.expect(err_ptr.isErrValue(raw));
    try std.testing.expect(!err_ptr.isOkValue(raw));
    try std.testing.expect(!xa_value.isValue(raw));
    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));

    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
    try std.testing.expect(slot.isErr());
    try std.testing.expect(!slot.isValue());
    try std.testing.expect(!slot.isPointer());
    try std.testing.expect(slot.isTaggedEntry());
    try std.testing.expectEqual(@as(?isize, case.code), slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), slot.value());
    try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
}

test "odd and even errno raws both keep err_ptr priority over xa_value tagging" {
    const cases = [_]ErrnoCase{
        .{ .code = -1, .has_value_tag_bit = true },
        .{ .code = -2, .has_value_tag_bit = false },
        .{ .code = -13, .has_value_tag_bit = true },
        .{ .code = -14, .has_value_tag_bit = false },
        .{ .code = -4094, .has_value_tag_bit = false },
        .{ .code = -4095, .has_value_tag_bit = true },
    };

    for (cases) |case| {
        try expectErrLane(case);
    }
}

test "errno lsb flips raw adjacency without opening value or pointer accessors" {
    const pairs = [_]AdjacentErrnoPair{
        .{ .higher_code = -1, .lower_code = -2, .higher_has_value_tag_bit = true, .lower_has_value_tag_bit = false },
        .{ .higher_code = -13, .lower_code = -14, .higher_has_value_tag_bit = true, .lower_has_value_tag_bit = false },
        .{ .higher_code = -4094, .lower_code = -4095, .higher_has_value_tag_bit = false, .lower_has_value_tag_bit = true },
    };

    for (pairs) |pair| {
        const higher_raw = err_ptr.fromErrorCode(pair.higher_code);
        const lower_raw = err_ptr.fromErrorCode(pair.lower_code);
        const higher_slot = xarray_slot_view.fromRaw(higher_raw);
        const lower_slot = xarray_slot_view.fromRaw(lower_raw);

        try std.testing.expectEqual(@as(usize, 1), higher_raw - lower_raw);
        try std.testing.expectEqual(pair.higher_has_value_tag_bit, (higher_raw & xa_value.value_tag_mask) == xa_value.value_tag_mask);
        try std.testing.expectEqual(pair.lower_has_value_tag_bit, (lower_raw & xa_value.value_tag_mask) == xa_value.value_tag_mask);

        try std.testing.expectEqual(@as(?usize, null), higher_slot.value());
        try std.testing.expectEqual(@as(?usize, null), lower_slot.value());
        try std.testing.expectEqual(@as(?usize, null), higher_slot.pointerValue());
        try std.testing.expectEqual(@as(?usize, null), lower_slot.pointerValue());
        try std.testing.expectEqual(@as(?isize, pair.higher_code), higher_slot.errorCode());
        try std.testing.expectEqual(@as(?isize, pair.lower_code), lower_slot.errorCode());
    }
}
