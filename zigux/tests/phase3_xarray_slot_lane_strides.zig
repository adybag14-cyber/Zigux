const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const ValueCase = struct {
    raw: usize,
    payload: usize,
};

const PointerCase = struct {
    raw: usize,
};

const ErrCase = struct {
    raw: usize,
    code: isize,
};

fn expectValueStride(window: []const ValueCase) !void {
    for (window, 0..) |case, index| {
        const slot = xarray_slot_view.fromRaw(case.raw);
        const rebuilt = try xarray_slot_view.fromValue(case.payload);

        try testing.expectEqual(xarray_slot_view.SlotKind.value, slot.kind());
        try testing.expect(slot.isValue());
        try testing.expectEqual(@as(?usize, case.payload), slot.value());
        try testing.expectEqual(case.raw, rebuilt.rawValue());

        if (index > 0) {
            const previous = window[index - 1];
            try testing.expectEqual(@as(usize, 2), case.raw - previous.raw);
            try testing.expectEqual(@as(usize, 1), case.payload - previous.payload);
        }
    }
}

fn expectPointerStride(window: []const PointerCase) !void {
    for (window, 0..) |case, index| {
        const slot = xarray_slot_view.fromRaw(case.raw);
        const rebuilt = xarray_slot_view.fromPointer(case.raw);

        try testing.expectEqual(xarray_slot_view.SlotKind.pointer, slot.kind());
        try testing.expect(slot.isPointer());
        try testing.expectEqual(@as(?usize, case.raw), slot.pointerValue());
        try testing.expectEqual(case.raw, rebuilt.rawValue());
        try testing.expect(!xarray_slot_view.isTaggedInternalEntry(case.raw));

        if (index > 0) {
            const previous = window[index - 1];
            try testing.expectEqual(@as(usize, 2), case.raw - previous.raw);
        }
    }
}

fn expectErrStride(window: []const ErrCase) !void {
    for (window, 0..) |case, index| {
        const slot = xarray_slot_view.fromRaw(case.raw);
        const rebuilt = xarray_slot_view.fromErrorCode(case.code);

        try testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
        try testing.expect(slot.isErr());
        try testing.expectEqual(@as(?isize, case.code), slot.errorCode());
        try testing.expectEqual(case.raw, rebuilt.rawValue());
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(case.raw));

        if (index > 0) {
            const previous = window[index - 1];
            try testing.expectEqual(@as(usize, 1), case.raw - previous.raw);
            try testing.expectEqual(@as(isize, 1), case.code - previous.code);
        }
    }
}

test "xarray-slot value lane keeps a two-raw stride and one-payload cadence" {
    const low_window = [_]ValueCase{
        .{ .raw = try xa_value.makeValue(0), .payload = 0 },
        .{ .raw = try xa_value.makeValue(1), .payload = 1 },
        .{ .raw = try xa_value.makeValue(2), .payload = 2 },
    };
    const high_window = [_]ValueCase{
        .{ .raw = try xa_value.makeValue(xa_value.safe_inline_limit - 2), .payload = xa_value.safe_inline_limit - 2 },
        .{ .raw = try xa_value.makeValue(xa_value.safe_inline_limit - 1), .payload = xa_value.safe_inline_limit - 1 },
        .{ .raw = try xa_value.makeValue(xa_value.safe_inline_limit), .payload = xa_value.safe_inline_limit },
    };

    try expectValueStride(low_window[0..]);
    try expectValueStride(high_window[0..]);
}

test "xarray-slot pointer lane keeps an even two-raw stride below the err floor" {
    const low_window = [_]PointerCase{
        .{ .raw = 2 },
        .{ .raw = 4 },
        .{ .raw = 6 },
    };
    const high_window = [_]PointerCase{
        .{ .raw = err_ptr.err_floor - 5 },
        .{ .raw = err_ptr.err_floor - 3 },
        .{ .raw = err_ptr.err_floor - 1 },
    };

    try expectPointerStride(low_window[0..]);
    try expectPointerStride(high_window[0..]);
}

test "xarray-slot err lane stays contiguous and rebuilds through error codes" {
    const err_window = [_]ErrCase{
        .{ .raw = err_ptr.err_floor, .code = -4095 },
        .{ .raw = err_ptr.err_floor + 1, .code = -4094 },
        .{ .raw = err_ptr.err_floor + 2, .code = -4093 },
    };

    try expectErrStride(err_window[0..]);
}
