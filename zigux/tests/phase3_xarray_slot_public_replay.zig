const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;
const SlotView = xarray_slot_view.SlotView;

const ReplayCase = struct {
    raw: usize,
    kind: SlotKind,
    decoded_value: ?usize = null,
    decoded_error: ?isize = null,
    pointer_raw: ?usize = null,
};

fn rebuild(slot: SlotView) !SlotView {
    return switch (slot.kind()) {
        .null => xarray_slot_view.nullSlot(),
        .value => try xarray_slot_view.fromValue(slot.value().?),
        .err => xarray_slot_view.fromErrorCode(slot.errorCode().?),
        .pointer => xarray_slot_view.fromPointer(slot.pointerValue().?),
    };
}

fn expectCase(case: ReplayCase) !void {
    const slot = xarray_slot_view.fromRaw(case.raw);
    try testing.expectEqual(case.kind, slot.kind());
    try testing.expectEqual(case.raw, slot.rawValue());
    try testing.expectEqual(case.decoded_value, slot.value());
    try testing.expectEqual(case.decoded_error, slot.errorCode());
    try testing.expectEqual(case.pointer_raw, slot.pointerValue());

    const rebuilt = try rebuild(slot);
    try testing.expectEqual(case.kind, rebuilt.kind());
    try testing.expectEqual(case.raw, rebuilt.rawValue());
    try testing.expectEqual(case.decoded_value, rebuilt.value());
    try testing.expectEqual(case.decoded_error, rebuilt.errorCode());
    try testing.expectEqual(case.pointer_raw, rebuilt.pointerValue());
}

test "public replay keeps the first low raw window in explicit lane order" {
    const cases = [_]ReplayCase{
        .{ .raw = 0, .kind = .null },
        .{ .raw = 1, .kind = .value, .decoded_value = 0 },
        .{ .raw = 2, .kind = .pointer, .pointer_raw = 2 },
        .{ .raw = 3, .kind = .value, .decoded_value = 1 },
        .{ .raw = 4, .kind = .pointer, .pointer_raw = 4 },
        .{ .raw = 5, .kind = .value, .decoded_value = 2 },
    };

    for (cases) |case| {
        try expectCase(case);
    }
}

test "public replay preserves the contiguous high boundary window around err_ptr floor" {
    const safe_limit_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const err_floor = err_ptr.err_floor;
    const cases = [_]ReplayCase{
        .{ .raw = safe_limit_raw, .kind = .value, .decoded_value = xa_value.safe_inline_limit },
        .{ .raw = err_floor - 1, .kind = .pointer, .pointer_raw = err_floor - 1 },
        .{ .raw = err_floor, .kind = .err, .decoded_error = -4095 },
        .{ .raw = err_floor + 1, .kind = .err, .decoded_error = -4094 },
    };

    try testing.expectEqual(err_floor - 2, safe_limit_raw);

    for (cases) |case| {
        try expectCase(case);
    }
}
