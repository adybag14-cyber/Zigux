const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;

const ErrCodeCase = struct {
    label: []const u8,
    code: isize,
};

fn rawRejectedValueAlias(code: isize) usize {
    const distance_from_floor: usize = @intCast(code + @as(isize, @intCast(err_ptr.max_errno)));
    const rejected_value = xa_value.safe_inline_limit + 1 + (distance_from_floor / 2);
    return (rejected_value << 1) | xa_value.value_tag_mask;
}

fn expectErrSlot(label: []const u8, raw: usize, code: isize) !void {
    const slot = xarray_slot_view.fromRaw(raw);

    try std.testing.expectEqual(err_ptr.fromErrorCode(code), raw);
    try std.testing.expectEqual(SlotKind.err, slot.kind());
    try std.testing.expect(slot.isErr());
    try std.testing.expect(slot.isTaggedEntry());
    try std.testing.expectEqual(@as(?isize, code), slot.errorCode());
    try std.testing.expectEqual(@as(isize, code), err_ptr.toErrorCode(slot.rawValue()));
    try std.testing.expectEqual(@as(?usize, null), slot.value());
    try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());

    errdefer std.debug.print("failed err sign-table expectation: {s}\n", .{label});
}

test "direct err_ptr raws preserve signed errno values through xarray slots" {
    const cases = [_]ErrCodeCase{
        .{ .label = "floor errno", .code = -4095 },
        .{ .label = "near floor errno", .code = -4094 },
        .{ .label = "mid errno", .code = -2048 },
        .{ .label = "common invalid argument errno", .code = -22 },
        .{ .label = "top errno", .code = -1 },
    };

    for (cases) |case| {
        try expectErrSlot(case.label, err_ptr.fromErrorCode(case.code), case.code);
    }
}

test "rejected xa_value aliases decode to the same signed odd errno values" {
    const cases = [_]ErrCodeCase{
        .{ .label = "first rejected value alias", .code = -4095 },
        .{ .label = "early odd alias", .code = -4093 },
        .{ .label = "middle odd alias", .code = -2047 },
        .{ .label = "near top odd alias", .code = -257 },
        .{ .label = "top odd alias", .code = -1 },
    };

    for (cases) |case| {
        const raw = rawRejectedValueAlias(case.code);

        try std.testing.expect((raw & xa_value.value_tag_mask) == xa_value.value_tag_mask);
        try std.testing.expectError(
            error.ValueWouldOverlapErrPtr,
            xa_value.makeValue((raw - xa_value.value_tag_mask) >> 1),
        );
        try expectErrSlot(case.label, raw, case.code);
    }
}

test "signed errno accessor stays closed around accepted values and pointer gaps" {
    const accepted_tail_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const pointer_gap_raw = err_ptr.err_floor - 1;
    const null_slot = xarray_slot_view.nullSlot();
    const accepted_tail_slot = xarray_slot_view.fromRaw(accepted_tail_raw);
    const pointer_gap_slot = xarray_slot_view.fromRaw(pointer_gap_raw);
    const aligned_pointer_slot = xarray_slot_view.fromPointer(0x8000);

    try std.testing.expectEqual(@as(?isize, null), null_slot.errorCode());
    try std.testing.expectEqual(@as(?isize, null), accepted_tail_slot.errorCode());
    try std.testing.expectEqual(@as(?isize, null), pointer_gap_slot.errorCode());
    try std.testing.expectEqual(@as(?isize, null), aligned_pointer_slot.errorCode());

    try std.testing.expectEqual(SlotKind.value, accepted_tail_slot.kind());
    try std.testing.expectEqual(SlotKind.pointer, pointer_gap_slot.kind());
    try std.testing.expectEqual(SlotKind.pointer, aligned_pointer_slot.kind());
    try std.testing.expectEqual(@as(?isize, -4095), xarray_slot_view.fromRaw(err_ptr.err_floor).errorCode());
}
