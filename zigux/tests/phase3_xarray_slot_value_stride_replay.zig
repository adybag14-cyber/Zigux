const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;

fn expectAcceptedValue(value: usize) !void {
    const raw = try xa_value.makeValue(value);
    const from_value = try xarray_slot_view.fromValue(value);
    const from_raw = xarray_slot_view.fromRaw(raw);

    try std.testing.expect(xa_value.canRepresent(value));
    try std.testing.expectEqual((value << 1) | xa_value.value_tag_mask, raw);
    try std.testing.expectEqual(raw, from_value.rawValue());
    try std.testing.expectEqual(raw, from_raw.rawValue());
    try std.testing.expectEqual(SlotKind.value, from_value.kind());
    try std.testing.expectEqual(SlotKind.value, from_raw.kind());
    try std.testing.expectEqual(@as(?usize, value), from_value.value());
    try std.testing.expectEqual(@as(?usize, value), from_raw.value());
    try std.testing.expectEqual(@as(?isize, null), from_raw.errorCode());
    try std.testing.expectEqual(@as(?usize, null), from_raw.pointerValue());
    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
    try std.testing.expect(from_raw.isTaggedEntry());
}

fn expectPointerNeighbor(raw: usize) !void {
    const slot = xarray_slot_view.fromRaw(raw);

    try std.testing.expect(raw != 0);
    try std.testing.expect(!err_ptr.isErrValue(raw));
    try std.testing.expect(!xa_value.isValue(raw));
    try std.testing.expectEqual(SlotKind.pointer, slot.kind());
    try std.testing.expectEqual(@as(?usize, raw), slot.pointerValue());
    try std.testing.expectEqual(@as(?usize, null), slot.value());
    try std.testing.expectEqual(@as(?isize, null), slot.errorCode());
    try std.testing.expect(!xarray_slot_view.isTaggedInternalEntry(raw));
    try std.testing.expect(!slot.isTaggedEntry());
}

test "accepted inline values advance by the Linux xa_value raw stride" {
    const values = [_]usize{
        0,
        1,
        2,
        7,
        31,
        255,
        xa_value.safe_inline_limit - 2,
        xa_value.safe_inline_limit - 1,
        xa_value.safe_inline_limit,
    };

    var previous_raw: ?usize = null;
    var previous_value: ?usize = null;

    for (values) |value| {
        const raw = try xa_value.makeValue(value);

        try expectAcceptedValue(value);
        if (previous_raw) |prev_raw| {
            const prev_value = previous_value.?;
            try std.testing.expectEqual((value - prev_value) * 2, raw - prev_raw);
        }

        previous_raw = raw;
        previous_value = value;
    }
}

test "even raws beside accepted inline values remain pointer-like" {
    const values = [_]usize{
        1,
        2,
        8,
        64,
        xa_value.safe_inline_limit - 2,
        xa_value.safe_inline_limit - 1,
    };

    for (values) |value| {
        const raw = try xa_value.makeValue(value);

        try expectAcceptedValue(value);
        try expectPointerNeighbor(raw - 1);
        try expectPointerNeighbor(raw + 1);
    }

    try expectAcceptedValue(xa_value.safe_inline_limit);
    try expectPointerNeighbor((try xa_value.makeValue(xa_value.safe_inline_limit)) + 1);
}

test "accepted value ceiling stays one stride below err_ptr floor" {
    const ceiling_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const first_rejected_value = xa_value.safe_inline_limit + 1;
    const rejected_raw = (first_rejected_value << 1) | xa_value.value_tag_mask;

    try expectAcceptedValue(xa_value.safe_inline_limit);
    try std.testing.expectEqual(err_ptr.err_floor - 2, ceiling_raw);
    try std.testing.expectEqual(err_ptr.err_floor, rejected_raw);
    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(first_rejected_value));
    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(first_rejected_value));
    try std.testing.expectEqual(SlotKind.pointer, xarray_slot_view.fromRaw(ceiling_raw + 1).kind());
    try std.testing.expectEqual(SlotKind.err, xarray_slot_view.fromRaw(rejected_raw).kind());
}
