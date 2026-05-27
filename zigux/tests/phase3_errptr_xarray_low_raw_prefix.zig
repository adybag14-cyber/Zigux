const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const PrefixCase = struct {
    raw: usize,
    kind: xarray_slot_view.SlotKind,
    decoded_value: ?usize = null,
    pointer_raw: ?usize = null,
    tagged: bool,
};

fn expectPrefixCase(case: PrefixCase) !void {
    const slot = xarray_slot_view.fromRaw(case.raw);

    try testing.expectEqual(case.raw, slot.rawValue());
    try testing.expectEqual(case.kind, slot.kind());
    try testing.expectEqual(case.decoded_value, slot.value());
    try testing.expectEqual(@as(?isize, null), slot.errorCode());
    try testing.expectEqual(case.pointer_raw, slot.pointerValue());
    try testing.expectEqual(false, err_ptr.isErrValue(case.raw));
    try testing.expectEqual(case.kind == .value, xa_value.isValue(case.raw));
    try testing.expectEqual(case.tagged, xarray_slot_view.isTaggedInternalEntry(case.raw));
}

test "low raw prefix keeps zero null odd raws as values and positive even raws as pointers" {
    const cases = [_]PrefixCase{
        .{ .raw = 0, .kind = .null, .tagged = false },
        .{ .raw = 1, .kind = .value, .decoded_value = 0, .tagged = true },
        .{ .raw = 2, .kind = .pointer, .pointer_raw = 2, .tagged = false },
        .{ .raw = 3, .kind = .value, .decoded_value = 1, .tagged = true },
        .{ .raw = 4, .kind = .pointer, .pointer_raw = 4, .tagged = false },
        .{ .raw = 5, .kind = .value, .decoded_value = 2, .tagged = true },
        .{ .raw = 6, .kind = .pointer, .pointer_raw = 6, .tagged = false },
        .{ .raw = 7, .kind = .value, .decoded_value = 3, .tagged = true },
        .{ .raw = 8, .kind = .pointer, .pointer_raw = 8, .tagged = false },
        .{ .raw = 9, .kind = .value, .decoded_value = 4, .tagged = true },
    };

    for (cases) |case| {
        try expectPrefixCase(case);
    }
}

test "small value constructors land on the odd raw ladder and their next raws stay pointer like" {
    const inline_values = [_]usize{ 0, 1, 2, 3, 4 };

    for (inline_values) |value| {
        const value_slot = try xarray_slot_view.fromValue(value);
        const pointer_raw = value_slot.rawValue() + 1;
        const pointer_slot = xarray_slot_view.fromRaw(pointer_raw);

        try testing.expectEqual((value << 1) | xa_value.value_tag_mask, value_slot.rawValue());
        try testing.expectEqual(@as(?usize, value), value_slot.value());
        try testing.expectEqual(xarray_slot_view.SlotKind.pointer, pointer_slot.kind());
        try testing.expectEqual(@as(?usize, pointer_raw), pointer_slot.pointerValue());
        try testing.expect(!xarray_slot_view.isTaggedInternalEntry(pointer_raw));
        try testing.expect(pointer_raw < err_ptr.err_floor);
    }
}

test "low raw prefix constructors and rereads agree on null value and pointer lanes" {
    const null_slot = xarray_slot_view.nullSlot();
    const value_slot = try xarray_slot_view.fromValue(4);
    const pointer_slot = xarray_slot_view.fromPointer(8);

    try testing.expectEqual(@as(usize, 0), null_slot.rawValue());
    try testing.expectEqual(xarray_slot_view.SlotKind.null, null_slot.kind());

    try testing.expectEqual(@as(usize, 9), value_slot.rawValue());
    try testing.expectEqual(xarray_slot_view.fromRaw(9).kind(), value_slot.kind());
    try testing.expectEqual(xarray_slot_view.fromRaw(9).value(), value_slot.value());

    try testing.expectEqual(@as(usize, 8), pointer_slot.rawValue());
    try testing.expectEqual(xarray_slot_view.fromRaw(8).kind(), pointer_slot.kind());
    try testing.expectEqual(xarray_slot_view.fromRaw(8).pointerValue(), pointer_slot.pointerValue());
}
