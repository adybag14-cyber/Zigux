const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;

fn uncheckedTaggedRaw(value: usize) usize {
    return (value << 1) | xa_value.value_tag_mask;
}

fn expectRejected(value: usize) !void {
    try std.testing.expect(!xa_value.canRepresent(value));
    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(value));
    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(value));
}

fn expectRawSlot(raw: usize, kind: SlotKind, payload_value: ?usize, errno: ?isize) !void {
    const slot = xarray_slot_view.fromRaw(raw);

    try std.testing.expectEqual(kind, slot.kind());
    try std.testing.expectEqual(raw, slot.rawValue());
    try std.testing.expectEqual(payload_value, slot.value());
    try std.testing.expectEqual(errno, slot.errorCode());

    if (kind == .pointer) {
        try std.testing.expectEqual(@as(?usize, raw), slot.pointerValue());
    } else {
        try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
    }
}

test "oversized inline values reject before shifted raws can wrap low" {
    const values = [_]usize{
        @as(usize, 1) << (@bitSizeOf(usize) - 1),
        std.math.maxInt(usize) - 1,
        std.math.maxInt(usize),
    };

    for (values) |value| {
        try expectRejected(value);
    }

    try expectRawSlot(uncheckedTaggedRaw(values[0]), .value, 0, null);
    try expectRawSlot(uncheckedTaggedRaw(values[1]), .err, null, -3);
    try expectRawSlot(uncheckedTaggedRaw(values[2]), .err, null, -1);
}

test "accepted ceiling and first rejected floor remain the only legal cutover" {
    const accepted = xa_value.safe_inline_limit;
    const rejected = accepted + 1;

    const accepted_slot = try xarray_slot_view.fromValue(accepted);
    try std.testing.expectEqual(SlotKind.value, accepted_slot.kind());
    try std.testing.expectEqual(err_ptr.err_floor - 2, accepted_slot.rawValue());
    try std.testing.expectEqual(@as(?usize, accepted), accepted_slot.value());

    try expectRejected(rejected);
    try expectRawSlot(uncheckedTaggedRaw(rejected), .err, null, -4095);
    try std.testing.expectEqual(err_ptr.err_floor, uncheckedTaggedRaw(rejected));
}

test "oversized rejection does not change raw decoder precedence" {
    const rejected_values = [_]usize{
        xa_value.safe_inline_limit + 1,
        xa_value.safe_inline_limit + 2,
        std.math.maxInt(usize),
    };

    for (rejected_values) |value| {
        try expectRejected(value);
    }

    try expectRawSlot(err_ptr.err_floor - 1, .pointer, null, null);
    try expectRawSlot(err_ptr.err_floor, .err, null, -4095);
    try expectRawSlot(err_ptr.fromErrorCode(-1), .err, null, -1);
}
