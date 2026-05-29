const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const LadderEntry = struct {
    code: isize,
    previous_raw: ?usize,
};

const constructor_ladder = [_]LadderEntry{
    .{ .code = -4095, .previous_raw = null },
    .{ .code = -2048, .previous_raw = err_ptr.fromErrorCode(-4095) },
    .{ .code = -1024, .previous_raw = err_ptr.fromErrorCode(-2048) },
    .{ .code = -512, .previous_raw = err_ptr.fromErrorCode(-1024) },
    .{ .code = -256, .previous_raw = err_ptr.fromErrorCode(-512) },
    .{ .code = -128, .previous_raw = err_ptr.fromErrorCode(-256) },
    .{ .code = -64, .previous_raw = err_ptr.fromErrorCode(-128) },
    .{ .code = -32, .previous_raw = err_ptr.fromErrorCode(-64) },
    .{ .code = -16, .previous_raw = err_ptr.fromErrorCode(-32) },
    .{ .code = -8, .previous_raw = err_ptr.fromErrorCode(-16) },
    .{ .code = -4, .previous_raw = err_ptr.fromErrorCode(-8) },
    .{ .code = -2, .previous_raw = err_ptr.fromErrorCode(-4) },
    .{ .code = -1, .previous_raw = err_ptr.fromErrorCode(-2) },
};

fn expectErrConstructorSlot(code: isize, previous_raw: ?usize) !void {
    const slot = xarray_slot_view.fromErrorCode(code);
    const raw = slot.rawValue();

    try std.testing.expectEqual(err_ptr.fromErrorCode(code), raw);
    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
    try std.testing.expect(slot.isErr());
    try std.testing.expect(!slot.isValue());
    try std.testing.expect(!slot.isPointer());
    try std.testing.expectEqual(@as(?isize, code), slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), slot.value());
    try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
    try std.testing.expect(err_ptr.isErrValue(raw));
    try std.testing.expect(!xa_value.isValue(raw));
    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));

    if (previous_raw) |previous| {
        try std.testing.expect(raw > previous);
    } else {
        try std.testing.expectEqual(err_ptr.err_floor, raw);
    }
}

test "err constructor code ladder remains ordered through xarray slot view" {
    for (constructor_ladder) |entry| {
        try expectErrConstructorSlot(entry.code, entry.previous_raw);
    }
}

test "raw and constructor entry points agree for errno ladder slots" {
    for (constructor_ladder) |entry| {
        const constructed = xarray_slot_view.fromErrorCode(entry.code);
        const raw_view = xarray_slot_view.fromRaw(constructed.rawValue());

        try std.testing.expectEqual(constructed.kind(), raw_view.kind());
        try std.testing.expectEqual(constructed.errorCode(), raw_view.errorCode());
        try std.testing.expectEqual(constructed.value(), raw_view.value());
        try std.testing.expectEqual(constructed.pointerValue(), raw_view.pointerValue());
    }
}
