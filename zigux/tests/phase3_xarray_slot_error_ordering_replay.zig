const std = @import("std");
const err_ptr = @import("err_ptr");
const slot_view = @import("xarray_slot_view");

const ErrorRow = struct {
    code: isize,
    label: []const u8,
};

const ordered_errors = [_]ErrorRow{
    .{ .code = -4095, .label = "floor" },
    .{ .code = -2048, .label = "lower-interior" },
    .{ .code = -1024, .label = "middle" },
    .{ .code = -512, .label = "upper-interior" },
    .{ .code = -22, .label = "einval" },
    .{ .code = -1, .label = "top" },
};

fn expectErrorSlot(row: ErrorRow) !slot_view.SlotView {
    try std.testing.expect(row.label.len != 0);

    const raw = err_ptr.fromErrorCode(row.code);
    const slot = slot_view.fromRaw(raw);

    try std.testing.expect(slot.isErr());
    try std.testing.expect(!slot.isNull());
    try std.testing.expect(!slot.isValue());
    try std.testing.expect(!slot.isPointer());
    try std.testing.expect(slot.isTaggedEntry());
    try std.testing.expect(slot_view.isTaggedInternalEntry(raw));
    try std.testing.expect(err_ptr.isErrValue(raw));
    try std.testing.expectEqual(row.code, err_ptr.toErrorCode(raw));
    try std.testing.expectEqual(@as(?isize, row.code), slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), slot.value());
    try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());

    return slot;
}

test "err_ptr raw ordering follows signed errno ordering through xarray slots" {
    var previous_raw: usize = 0;
    var previous_code: isize = -@as(isize, @intCast(err_ptr.max_errno)) - 1;

    for (ordered_errors, 0..) |row, index| {
        const slot = try expectErrorSlot(row);
        const raw = slot.rawValue();

        if (index == 0) {
            try std.testing.expectEqual(err_ptr.err_floor, raw);
        } else {
            try std.testing.expect(raw > previous_raw);
            try std.testing.expect(row.code > previous_code);
        }

        previous_raw = raw;
        previous_code = row.code;
    }

    try std.testing.expectEqual(err_ptr.fromErrorCode(-1), previous_raw);
    try std.testing.expectEqual(@as(isize, -1), previous_code);
}

test "neighboring non-error boundary values do not enter the ordered err lane" {
    const before_floor = slot_view.fromRaw(err_ptr.err_floor - 1);
    const null_slot = slot_view.nullSlot();
    const low_value = try slot_view.fromValue(0);
    const pointer_slot = slot_view.fromPointer(0x2000);

    try std.testing.expect(before_floor.isPointer());
    try std.testing.expect(!before_floor.isErr());
    try std.testing.expectEqual(@as(?usize, err_ptr.err_floor - 1), before_floor.pointerValue());

    try std.testing.expect(null_slot.isNull());
    try std.testing.expect(!null_slot.isErr());
    try std.testing.expect(!null_slot.isTaggedEntry());

    try std.testing.expect(low_value.isValue());
    try std.testing.expect(!low_value.isErr());
    try std.testing.expectEqual(@as(?usize, 0), low_value.value());

    try std.testing.expect(pointer_slot.isPointer());
    try std.testing.expect(!pointer_slot.isErr());
    try std.testing.expectEqual(@as(?usize, 0x2000), pointer_slot.pointerValue());
}
