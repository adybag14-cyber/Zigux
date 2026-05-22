const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xarray_slot_view = @import("xarray_slot_view");

test "every err_ptr code stays in the err lane across the full error band" {
    var previous_raw: ?usize = null;
    var odd_raws: usize = 0;
    var even_raws: usize = 0;

    var code: isize = -@as(isize, @intCast(err_ptr.max_errno));
    while (code <= -1) : (code += 1) {
        const raw = err_ptr.fromErrorCode(code);
        const slot = xarray_slot_view.fromRaw(raw);

        try testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
        try testing.expect(slot.isErr());
        try testing.expect(!slot.isNull());
        try testing.expect(!slot.isValue());
        try testing.expect(!slot.isPointer());
        try testing.expectEqual(raw, slot.rawValue());
        try testing.expectEqual(@as(?isize, code), slot.errorCode());
        try testing.expectEqual(@as(?usize, null), slot.value());
        try testing.expectEqual(@as(?usize, null), slot.pointerValue());
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));

        if ((raw & 1) == 0) {
            even_raws += 1;
        } else {
            odd_raws += 1;
        }

        if (previous_raw) |prev| {
            try testing.expectEqual(prev + 1, raw);
        } else {
            try testing.expectEqual(err_ptr.err_floor, raw);
        }
        previous_raw = raw;
    }

    try testing.expectEqual(@as(usize, 2048), odd_raws);
    try testing.expectEqual(@as(usize, 2047), even_raws);
    try testing.expectEqual(@as(usize, std.math.maxInt(usize)), previous_raw.?);
}

test "the full err band stays fenced off from the pointer gap on both ends" {
    const gap_raw = err_ptr.err_floor - 1;
    const floor_slot = xarray_slot_view.fromErrorCode(-4095);
    const top_slot = xarray_slot_view.fromErrorCode(-1);
    const gap_slot = xarray_slot_view.fromRaw(gap_raw);

    try testing.expectEqual(err_ptr.err_floor, gap_raw + 1);
    try testing.expectEqual(std.math.maxInt(usize), top_slot.rawValue());

    try testing.expectEqual(xarray_slot_view.SlotKind.pointer, gap_slot.kind());
    try testing.expect(gap_slot.isPointer());
    try testing.expectEqual(@as(?usize, gap_raw), gap_slot.pointerValue());
    try testing.expectEqual(@as(?isize, null), gap_slot.errorCode());
    try testing.expect(!xarray_slot_view.isTaggedInternalEntry(gap_raw));

    try testing.expectEqual(xarray_slot_view.SlotKind.err, floor_slot.kind());
    try testing.expectEqual(@as(?isize, -4095), floor_slot.errorCode());
    try testing.expectEqual(xarray_slot_view.SlotKind.err, top_slot.kind());
    try testing.expectEqual(@as(?isize, -1), top_slot.errorCode());
}
