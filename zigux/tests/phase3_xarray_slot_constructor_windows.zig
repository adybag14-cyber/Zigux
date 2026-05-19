const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;
const SlotView = xarray_slot_view.SlotView;

const ConstructorCase = struct {
    slot: SlotView,
    expected_raw: usize,
    expected_kind: SlotKind,
    expected_value: ?usize = null,
    expected_error: ?isize = null,
    expected_pointer: ?usize = null,
};

fn rebuildThroughConstructors(slot: SlotView) !SlotView {
    return switch (slot.kind()) {
        .null => xarray_slot_view.nullSlot(),
        .value => try xarray_slot_view.fromValue(slot.value().?),
        .err => xarray_slot_view.fromErrorCode(slot.errorCode().?),
        .pointer => xarray_slot_view.fromPointer(slot.pointerValue().?),
    };
}

fn expectConstructorCase(case: ConstructorCase) !void {
    try testing.expectEqual(case.expected_kind, case.slot.kind());
    try testing.expectEqual(case.expected_raw, case.slot.rawValue());
    try testing.expectEqual(case.expected_value, case.slot.value());
    try testing.expectEqual(case.expected_error, case.slot.errorCode());
    try testing.expectEqual(case.expected_pointer, case.slot.pointerValue());

    const decoded = xarray_slot_view.fromRaw(case.slot.rawValue());
    try testing.expectEqual(case.expected_kind, decoded.kind());
    try testing.expectEqual(case.expected_raw, decoded.rawValue());
    try testing.expectEqual(case.expected_value, decoded.value());
    try testing.expectEqual(case.expected_error, decoded.errorCode());
    try testing.expectEqual(case.expected_pointer, decoded.pointerValue());

    const rebuilt = try rebuildThroughConstructors(decoded);
    try testing.expectEqual(case.expected_kind, rebuilt.kind());
    try testing.expectEqual(case.expected_raw, rebuilt.rawValue());
    try testing.expectEqual(case.expected_value, rebuilt.value());
    try testing.expectEqual(case.expected_error, rebuilt.errorCode());
    try testing.expectEqual(case.expected_pointer, rebuilt.pointerValue());
}

test "constructor-first low cutoff window stays contiguous through decode and rebuild" {
    const cases = [_]ConstructorCase{
        .{ .slot = xarray_slot_view.nullSlot(), .expected_raw = 0, .expected_kind = .null },
        .{ .slot = try xarray_slot_view.fromValue(0), .expected_raw = 1, .expected_kind = .value, .expected_value = 0 },
        .{ .slot = xarray_slot_view.fromPointer(2), .expected_raw = 2, .expected_kind = .pointer, .expected_pointer = 2 },
        .{ .slot = try xarray_slot_view.fromValue(1), .expected_raw = 3, .expected_kind = .value, .expected_value = 1 },
        .{ .slot = xarray_slot_view.fromPointer(4), .expected_raw = 4, .expected_kind = .pointer, .expected_pointer = 4 },
        .{ .slot = try xarray_slot_view.fromValue(2), .expected_raw = 5, .expected_kind = .value, .expected_value = 2 },
    };

    for (cases, 0..) |case, index| {
        try expectConstructorCase(case);
        try testing.expectEqual(index, case.expected_raw);
    }
}

test "constructor-first high cutoff window stays ordered through decode and rebuild" {
    const safe_limit_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const err_floor = err_ptr.err_floor;
    const cases = [_]ConstructorCase{
        .{
            .slot = try xarray_slot_view.fromValue(xa_value.safe_inline_limit),
            .expected_raw = safe_limit_raw,
            .expected_kind = .value,
            .expected_value = xa_value.safe_inline_limit,
        },
        .{
            .slot = xarray_slot_view.fromPointer(err_floor - 1),
            .expected_raw = err_floor - 1,
            .expected_kind = .pointer,
            .expected_pointer = err_floor - 1,
        },
        .{
            .slot = xarray_slot_view.fromErrorCode(-4095),
            .expected_raw = err_floor,
            .expected_kind = .err,
            .expected_error = -4095,
        },
        .{
            .slot = xarray_slot_view.fromErrorCode(-4094),
            .expected_raw = err_floor + 1,
            .expected_kind = .err,
            .expected_error = -4094,
        },
        .{
            .slot = xarray_slot_view.fromErrorCode(-1),
            .expected_raw = err_ptr.fromErrorCode(-1),
            .expected_kind = .err,
            .expected_error = -1,
        },
    };

    try testing.expectEqual(err_floor - 2, safe_limit_raw);

    for (cases) |case| {
        try expectConstructorCase(case);
    }

    try testing.expectEqual(cases[0].expected_raw + 1, cases[1].expected_raw);
    try testing.expectEqual(cases[1].expected_raw + 1, cases[2].expected_raw);
    try testing.expectEqual(cases[2].expected_raw + 1, cases[3].expected_raw);
}
