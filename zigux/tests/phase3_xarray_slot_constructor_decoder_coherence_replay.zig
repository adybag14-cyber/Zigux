const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;
const SlotView = xarray_slot_view.SlotView;

fn expectLane(
    slot: SlotView,
    expected_kind: SlotKind,
    expected_value: ?usize,
    expected_error: ?isize,
    expected_pointer: ?usize,
) !void {
    try std.testing.expectEqual(expected_kind, slot.kind());
    try std.testing.expectEqual(expected_kind == .null, slot.isNull());
    try std.testing.expectEqual(expected_kind == .value, slot.isValue());
    try std.testing.expectEqual(expected_kind == .err, slot.isErr());
    try std.testing.expectEqual(expected_kind == .pointer, slot.isPointer());
    try std.testing.expectEqual(expected_value, slot.value());
    try std.testing.expectEqual(expected_error, slot.errorCode());
    try std.testing.expectEqual(expected_pointer, slot.pointerValue());
}

test "public constructors round trip through raw xarray slot decoding" {
    const value_cases = [_]usize{
        0,
        1,
        29,
        xa_value.safe_inline_limit,
    };

    for (value_cases) |value| {
        const constructed = try xarray_slot_view.fromValue(value);
        const decoded = xarray_slot_view.fromRaw(constructed.rawValue());

        try std.testing.expectEqual(try xa_value.makeValue(value), constructed.rawValue());
        try std.testing.expectEqual(constructed.rawValue(), decoded.rawValue());
        try expectLane(constructed, .value, value, null, null);
        try expectLane(decoded, .value, value, null, null);
        try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(decoded.rawValue()));
    }

    const err_cases = [_]isize{
        -1,
        -22,
        -@as(isize, @intCast(err_ptr.max_errno)),
    };

    for (err_cases) |code| {
        const constructed = xarray_slot_view.fromErrorCode(code);
        const decoded = xarray_slot_view.fromRaw(constructed.rawValue());

        try std.testing.expectEqual(err_ptr.fromErrorCode(code), constructed.rawValue());
        try std.testing.expectEqual(constructed.rawValue(), decoded.rawValue());
        try expectLane(constructed, .err, null, code, null);
        try expectLane(decoded, .err, null, code, null);
        try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(decoded.rawValue()));
    }

    const pointer_cases = [_]usize{
        2,
        0x1000,
        err_ptr.err_floor - 1,
    };

    for (pointer_cases) |raw| {
        const constructed = xarray_slot_view.fromPointer(raw);
        const decoded = xarray_slot_view.fromRaw(raw);

        try std.testing.expectEqual(raw, constructed.rawValue());
        try std.testing.expectEqual(raw, decoded.rawValue());
        try expectLane(constructed, .pointer, null, null, raw);
        try expectLane(decoded, .pointer, null, null, raw);
        try std.testing.expect(!xarray_slot_view.isTaggedInternalEntry(raw));
    }
}

test "null constructor and raw zero keep every payload accessor closed" {
    const constructed = xarray_slot_view.nullSlot();
    const decoded = xarray_slot_view.fromRaw(0);

    try std.testing.expectEqual(constructed.rawValue(), decoded.rawValue());
    try expectLane(constructed, .null, null, null, null);
    try expectLane(decoded, .null, null, null, null);
    try std.testing.expect(!xarray_slot_view.isTaggedInternalEntry(decoded.rawValue()));
}
