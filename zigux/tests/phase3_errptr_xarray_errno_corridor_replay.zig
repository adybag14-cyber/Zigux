const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const ErrnoCase = struct {
    name: []const u8,
    code: isize,
};

const common_errno_corridor = [_]ErrnoCase{
    .{ .name = "MAX_ERRNO floor", .code = -4095 },
    .{ .name = "EOPNOTSUPP", .code = -95 },
    .{ .name = "EOVERFLOW", .code = -75 },
    .{ .name = "EINVAL", .code = -22 },
    .{ .name = "ENOMEM", .code = -12 },
    .{ .name = "ENOENT", .code = -2 },
    .{ .name = "EPERM", .code = -1 },
};

test "common errno corridor decodes identically through err_ptr and xarray slots" {
    var previous_raw: usize = 0;

    for (common_errno_corridor, 0..) |row, index| {
        const raw = err_ptr.fromErrorCode(row.code);
        const slot = xarray_slot_view.fromErrorCode(row.code);

        try std.testing.expectEqual(raw, slot.rawValue());
        try std.testing.expectEqual(row.code, err_ptr.toErrorCode(raw));
        try std.testing.expectEqual(@as(?isize, row.code), slot.errorCode());
        try std.testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
        try std.testing.expect(slot.isErr());
        try std.testing.expect(slot.isTaggedEntry());
        try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));

        if (index == 0) {
            try std.testing.expectEqual(err_ptr.err_floor, raw);
        } else {
            try std.testing.expect(raw > previous_raw);
        }
        previous_raw = raw;
    }
}

test "errno raws stay out of xa_value even when the low tag bit is present" {
    for (common_errno_corridor) |row| {
        const raw = err_ptr.fromErrorCode(row.code);
        const low_tag_is_set = (raw & xa_value.value_tag_mask) == xa_value.value_tag_mask;
        const code_is_odd = @mod(-row.code, 2) == 1;

        try std.testing.expectEqual(code_is_odd, low_tag_is_set);
        try std.testing.expect(err_ptr.isErrValue(raw));
        try std.testing.expect(!xa_value.isValue(raw));
        try std.testing.expectEqual(@as(?usize, null), xarray_slot_view.fromRaw(raw).value());
    }
}

test "errno corridor keeps null value and pointer accessors closed" {
    for (common_errno_corridor) |row| {
        const slot = xarray_slot_view.fromErrorCode(row.code);

        try std.testing.expect(!slot.isNull());
        try std.testing.expect(!slot.isValue());
        try std.testing.expect(!slot.isPointer());
        try std.testing.expectEqual(@as(?usize, null), slot.value());
        try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
    }
}
