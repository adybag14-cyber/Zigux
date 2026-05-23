const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn expectErrSlot(code: isize) !usize {
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
    try testing.expect(err_ptr.isErrValue(raw));
    try testing.expect(!xa_value.isValue(raw));

    return raw;
}

test "sparse interior err deltas preserve the same decoded code deltas" {
    const codes = [_]isize{ -4000, -3073, -2048, -1025, -33 };

    var raws: [codes.len]usize = undefined;
    for (codes, 0..) |code, index| {
        raws[index] = try expectErrSlot(code);
    }

    for (codes[0 .. codes.len - 1], codes[1..], 0..) |left_code, right_code, index| {
        const expected_delta: usize = @intCast(right_code - left_code);
        try testing.expect(expected_delta > 1);
        try testing.expectEqual(raws[index] + expected_delta, raws[index + 1]);
        try testing.expectEqual(expected_delta, raws[index + 1] - raws[index]);
    }
}

test "adding sparse interior raw deltas reconstructs the same err lane slots" {
    const steps = [_]struct { start: isize, delta: usize, target: isize }{
        .{ .start = -3073, .delta = 1025, .target = -2048 },
        .{ .start = -2048, .delta = 1023, .target = -1025 },
        .{ .start = -1025, .delta = 992, .target = -33 },
    };

    for (steps) |step| {
        const start_raw = try expectErrSlot(step.start);
        const target_raw = try expectErrSlot(step.target);
        const shifted_raw = start_raw + step.delta;
        const shifted_slot = xarray_slot_view.fromRaw(shifted_raw);

        try testing.expectEqual(step.delta, target_raw - start_raw);
        try testing.expectEqual(shifted_raw, target_raw);
        try testing.expectEqual(@as(?isize, step.target), shifted_slot.errorCode());
        try testing.expect(shifted_slot.isErr());
        try testing.expect(!shifted_slot.isValue());
        try testing.expect(!shifted_slot.isPointer());
    }
}
