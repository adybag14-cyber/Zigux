const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const Row = struct {
    label: []const u8,
    raw: usize,
    expected_code: isize,
    low_bit_set: bool,
    rejected_value_source: ?usize,
};

fn expectErrParityRow(row: Row) !void {
    const slot = xarray_slot_view.fromRaw(row.raw);

    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
    try std.testing.expect(slot.isErr());
    try std.testing.expect(!slot.isNull());
    try std.testing.expect(!slot.isValue());
    try std.testing.expect(!slot.isPointer());
    try std.testing.expect(slot.isTaggedEntry());
    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(row.raw));
    try std.testing.expect(err_ptr.isErrValue(row.raw));
    try std.testing.expect(!err_ptr.isOkValue(row.raw));
    try std.testing.expectEqual(row.low_bit_set, (row.raw & xa_value.value_tag_mask) == xa_value.value_tag_mask);
    try std.testing.expect(!xa_value.isValue(row.raw));
    try std.testing.expectEqual(@as(?isize, row.expected_code), slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), slot.value());
    try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());

    if (row.rejected_value_source) |source| {
        try std.testing.expect(!xa_value.canRepresent(source));
        try std.testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(source));
        try std.testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(source));
        try std.testing.expectEqual(row.raw, (source << 1) | xa_value.value_tag_mask);
    }
}

test "err band parity stays error-first through xarray slot decoding" {
    const rejected_floor = xa_value.safe_inline_limit + 1;
    const rejected_floor_plus_one = rejected_floor + 1;
    const rejected_top_minus_one = (err_ptr.fromErrorCode(-3) >> 1);
    const rejected_top = (err_ptr.fromErrorCode(-1) >> 1);

    const rows = [_]Row{
        .{
            .label = "first-rejected-odd",
            .raw = err_ptr.err_floor,
            .expected_code = -4095,
            .low_bit_set = true,
            .rejected_value_source = rejected_floor,
        },
        .{
            .label = "even-error-neighbor",
            .raw = err_ptr.err_floor + 1,
            .expected_code = -4094,
            .low_bit_set = false,
            .rejected_value_source = null,
        },
        .{
            .label = "second-rejected-odd",
            .raw = err_ptr.err_floor + 2,
            .expected_code = -4093,
            .low_bit_set = true,
            .rejected_value_source = rejected_floor_plus_one,
        },
        .{
            .label = "second-even-error-neighbor",
            .raw = err_ptr.err_floor + 3,
            .expected_code = -4092,
            .low_bit_set = false,
            .rejected_value_source = null,
        },
        .{
            .label = "interior-even",
            .raw = err_ptr.fromErrorCode(-128),
            .expected_code = -128,
            .low_bit_set = false,
            .rejected_value_source = null,
        },
        .{
            .label = "interior-odd",
            .raw = err_ptr.fromErrorCode(-127),
            .expected_code = -127,
            .low_bit_set = true,
            .rejected_value_source = null,
        },
        .{
            .label = "near-top-odd-alias",
            .raw = err_ptr.fromErrorCode(-3),
            .expected_code = -3,
            .low_bit_set = true,
            .rejected_value_source = rejected_top_minus_one,
        },
        .{
            .label = "near-top-even-neighbor",
            .raw = err_ptr.fromErrorCode(-2),
            .expected_code = -2,
            .low_bit_set = false,
            .rejected_value_source = null,
        },
        .{
            .label = "top-odd-alias",
            .raw = err_ptr.fromErrorCode(-1),
            .expected_code = -1,
            .low_bit_set = true,
            .rejected_value_source = rejected_top,
        },
    };

    for (rows) |row| {
        try std.testing.expect(row.label.len > 0);
        try expectErrParityRow(row);
    }
}

test "non-error parity neighbors remain outside the err precedence band" {
    const high_value_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const pointer_gap_raw = err_ptr.err_floor - 1;
    const first_value_raw = try xa_value.makeValue(0);
    const low_pointer_raw: usize = 2;

    const high_value = xarray_slot_view.fromRaw(high_value_raw);
    const pointer_gap = xarray_slot_view.fromRaw(pointer_gap_raw);
    const first_value = xarray_slot_view.fromRaw(first_value_raw);
    const low_pointer = xarray_slot_view.fromRaw(low_pointer_raw);

    try std.testing.expectEqual(err_ptr.err_floor - 2, high_value.rawValue());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.value, high_value.kind());
    try std.testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), high_value.value());
    try std.testing.expectEqual(@as(?isize, null), high_value.errorCode());

    try std.testing.expectEqual(xarray_slot_view.SlotKind.pointer, pointer_gap.kind());
    try std.testing.expectEqual(@as(?usize, pointer_gap_raw), pointer_gap.pointerValue());
    try std.testing.expectEqual(@as(?isize, null), pointer_gap.errorCode());
    try std.testing.expect(!xarray_slot_view.isTaggedInternalEntry(pointer_gap_raw));

    try std.testing.expectEqual(xarray_slot_view.SlotKind.value, first_value.kind());
    try std.testing.expectEqual(@as(?usize, 0), first_value.value());
    try std.testing.expect(!err_ptr.isErrValue(first_value_raw));

    try std.testing.expectEqual(xarray_slot_view.SlotKind.pointer, low_pointer.kind());
    try std.testing.expectEqual(@as(?usize, low_pointer_raw), low_pointer.pointerValue());
    try std.testing.expect(!xa_value.isValue(low_pointer_raw));
    try std.testing.expect(!err_ptr.isErrValue(low_pointer_raw));
}
