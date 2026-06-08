const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SpanRow = struct {
    code: isize,
    raw_offset_from_floor: usize,
};

fn expectErrSpanRow(row: SpanRow) !void {
    const raw = err_ptr.fromErrorCode(row.code);
    const slot = xarray_slot_view.fromRaw(raw);

    try std.testing.expectEqual(err_ptr.err_floor + row.raw_offset_from_floor, raw);
    try std.testing.expect(err_ptr.isErrValue(raw));
    try std.testing.expect(!err_ptr.isOkValue(raw));
    try std.testing.expect(!xa_value.isValue(raw));
    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));

    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
    try std.testing.expect(slot.isErr());
    try std.testing.expect(slot.isTaggedEntry());
    try std.testing.expectEqual(@as(?isize, row.code), slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), slot.value());
    try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
}

test "err_ptr errno span has one xarray error slot per Linux errno" {
    const top_raw = err_ptr.fromErrorCode(-1);
    const span_width = top_raw - err_ptr.err_floor + 1;

    try std.testing.expectEqual(err_ptr.max_errno, span_width);
    try std.testing.expectEqual(@as(usize, 0), err_ptr.fromErrorCode(-4095) - err_ptr.err_floor);
    try std.testing.expectEqual(@as(usize, 4094), top_raw - err_ptr.err_floor);

    const rows = [_]SpanRow{
        .{ .code = -4095, .raw_offset_from_floor = 0 },
        .{ .code = -4094, .raw_offset_from_floor = 1 },
        .{ .code = -2048, .raw_offset_from_floor = 2047 },
        .{ .code = -1024, .raw_offset_from_floor = 3071 },
        .{ .code = -2, .raw_offset_from_floor = 4093 },
        .{ .code = -1, .raw_offset_from_floor = 4094 },
    };

    for (rows) |row| {
        try expectErrSpanRow(row);
    }
}

test "constructor error slots replay the same errno span offsets" {
    const rows = [_]SpanRow{
        .{ .code = -4095, .raw_offset_from_floor = 0 },
        .{ .code = -2048, .raw_offset_from_floor = 2047 },
        .{ .code = -513, .raw_offset_from_floor = 3582 },
        .{ .code = -22, .raw_offset_from_floor = 4073 },
        .{ .code = -1, .raw_offset_from_floor = 4094 },
    };

    for (rows) |row| {
        const constructed = xarray_slot_view.fromErrorCode(row.code);
        const reread = xarray_slot_view.fromRaw(constructed.rawValue());

        try std.testing.expectEqual(err_ptr.err_floor + row.raw_offset_from_floor, constructed.rawValue());
        try std.testing.expectEqual(xarray_slot_view.SlotKind.err, constructed.kind());
        try std.testing.expectEqual(@as(?isize, row.code), constructed.errorCode());
        try std.testing.expectEqual(constructed.rawValue(), reread.rawValue());
        try std.testing.expectEqual(constructed.kind(), reread.kind());
        try std.testing.expectEqual(constructed.errorCode(), reread.errorCode());
        try std.testing.expectEqual(@as(?usize, null), reread.value());
        try std.testing.expectEqual(@as(?usize, null), reread.pointerValue());
    }
}
