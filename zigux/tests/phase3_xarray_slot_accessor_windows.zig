const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;
const SlotView = xarray_slot_view.SlotView;

const AccessorCase = struct {
    raw: usize,
    kind: SlotKind,
    tagged_internal: bool,
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

fn expectExclusiveAccessors(case: AccessorCase) !void {
    const slot = xarray_slot_view.fromRaw(case.raw);
    const values = [_]bool{
        slot.value() != null,
        slot.errorCode() != null,
        slot.pointerValue() != null,
    };
    var open_count: usize = 0;
    for (values) |open| {
        if (open) {
            open_count += 1;
        }
    }

    try testing.expectEqual(case.kind, slot.kind());
    try testing.expectEqual(case.raw, slot.rawValue());
    try testing.expectEqual(case.decoded_value, slot.value());
    try testing.expectEqual(case.decoded_error, slot.errorCode());
    try testing.expectEqual(case.pointer_raw, slot.pointerValue());
    try testing.expectEqual(case.tagged_internal, xarray_slot_view.isTaggedInternalEntry(case.raw));
    try testing.expectEqual(
        if (case.kind == .null) @as(usize, 0) else @as(usize, 1),
        open_count,
    );

    const rebuilt = try rebuild(slot);
    try testing.expectEqual(case.kind, rebuilt.kind());
    try testing.expectEqual(case.raw, rebuilt.rawValue());
    try testing.expectEqual(case.decoded_value, rebuilt.value());
    try testing.expectEqual(case.decoded_error, rebuilt.errorCode());
    try testing.expectEqual(case.pointer_raw, rebuilt.pointerValue());
}

test "low accessor window keeps exactly one decoded accessor open per raw lane" {
    const cases = [_]AccessorCase{
        .{ .raw = 0, .kind = .null, .tagged_internal = false },
        .{ .raw = 1, .kind = .value, .tagged_internal = true, .decoded_value = 0 },
        .{ .raw = 2, .kind = .pointer, .tagged_internal = false, .pointer_raw = 2 },
        .{ .raw = 3, .kind = .value, .tagged_internal = true, .decoded_value = 1 },
        .{ .raw = 4, .kind = .pointer, .tagged_internal = false, .pointer_raw = 4 },
        .{ .raw = 5, .kind = .value, .tagged_internal = true, .decoded_value = 2 },
    };

    for (cases, 0..) |case, index| {
        try expectExclusiveAccessors(case);
        try testing.expectEqual(index, case.raw);
    }
}

test "high accessor window keeps exactly one decoded accessor open per boundary lane" {
    const safe_limit_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const err_floor = err_ptr.err_floor;
    const cases = [_]AccessorCase{
        .{
            .raw = safe_limit_raw,
            .kind = .value,
            .tagged_internal = true,
            .decoded_value = xa_value.safe_inline_limit,
        },
        .{
            .raw = err_floor - 1,
            .kind = .pointer,
            .tagged_internal = false,
            .pointer_raw = err_floor - 1,
        },
        .{
            .raw = err_floor,
            .kind = .err,
            .tagged_internal = true,
            .decoded_error = -4095,
        },
        .{
            .raw = err_floor + 1,
            .kind = .err,
            .tagged_internal = true,
            .decoded_error = -4094,
        },
        .{
            .raw = err_ptr.fromErrorCode(-1),
            .kind = .err,
            .tagged_internal = true,
            .decoded_error = -1,
        },
    };

    try testing.expectEqual(err_floor - 2, safe_limit_raw);

    for (cases) |case| {
        try expectExclusiveAccessors(case);
    }

    try testing.expectEqual(cases[0].raw + 1, cases[1].raw);
    try testing.expectEqual(cases[1].raw + 1, cases[2].raw);
    try testing.expectEqual(cases[2].raw + 1, cases[3].raw);
}
