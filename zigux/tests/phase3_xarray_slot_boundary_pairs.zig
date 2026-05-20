const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const Case = struct {
    name: []const u8,
    raw: usize,
    kind: xarray_slot_view.SlotKind,
};

fn rebuild(slot: xarray_slot_view.SlotView) !xarray_slot_view.SlotView {
    return switch (slot.kind()) {
        .null => xarray_slot_view.nullSlot(),
        .value => try xarray_slot_view.fromValue(slot.value().?),
        .pointer => xarray_slot_view.fromPointer(slot.pointerValue().?),
        .err => xarray_slot_view.fromErrorCode(slot.errorCode().?),
    };
}

fn expectDecodedShape(case: Case, slot: xarray_slot_view.SlotView) !void {
    try testing.expectEqual(case.kind, slot.kind());
    try testing.expectEqual(case.raw, slot.rawValue());

    switch (case.kind) {
        .null => {
            try testing.expectEqual(@as(?usize, null), slot.value());
            try testing.expectEqual(@as(?isize, null), slot.errorCode());
            try testing.expectEqual(@as(?usize, null), slot.pointerValue());
        },
        .value => {
            try testing.expect(slot.value() != null);
            try testing.expectEqual(@as(?isize, null), slot.errorCode());
            try testing.expectEqual(@as(?usize, null), slot.pointerValue());
        },
        .pointer => {
            try testing.expectEqual(@as(?usize, null), slot.value());
            try testing.expectEqual(@as(?isize, null), slot.errorCode());
            try testing.expectEqual(@as(?usize, case.raw), slot.pointerValue());
        },
        .err => {
            try testing.expectEqual(@as(?usize, null), slot.value());
            try testing.expect(slot.errorCode() != null);
            try testing.expectEqual(@as(?usize, null), slot.pointerValue());
        },
    }
}

test "low-end adjacent xarray-slot pairs keep their lane boundaries explicit" {
    const cases = [_]Case{
        .{ .name = "null", .raw = 0, .kind = .null },
        .{ .name = "inline_zero", .raw = try xa_value.makeValue(0), .kind = .value },
        .{ .name = "pointer_two", .raw = 2, .kind = .pointer },
        .{ .name = "inline_one", .raw = try xa_value.makeValue(1), .kind = .value },
    };

    for (cases, 0..) |case, index| {
        const slot = xarray_slot_view.fromRaw(case.raw);
        try expectDecodedShape(case, slot);
        const rebuilt = try rebuild(slot);
        try expectDecodedShape(case, rebuilt);

        if (index != 0) {
            try testing.expectEqual(cases[index - 1].raw + 1, case.raw);
            try testing.expect(cases[index - 1].kind != case.kind);
        }
    }

    try testing.expectEqualStrings("null", cases[0].name);
    try testing.expectEqualStrings("inline_zero", cases[1].name);
    try testing.expectEqualStrings("pointer_two", cases[2].name);
    try testing.expectEqualStrings("inline_one", cases[3].name);
}

test "high-end adjacent xarray-slot pairs keep the safe-inline gap and err floor explicit" {
    const cases = [_]Case{
        .{ .name = "inline_limit", .raw = try xa_value.makeValue(xa_value.safe_inline_limit), .kind = .value },
        .{ .name = "gap_before_err_floor", .raw = err_ptr.err_floor - 1, .kind = .pointer },
        .{ .name = "err_floor", .raw = err_ptr.err_floor, .kind = .err },
        .{ .name = "err_floor_plus_one", .raw = err_ptr.err_floor + 1, .kind = .err },
    };

    for (cases, 0..) |case, index| {
        const slot = xarray_slot_view.fromRaw(case.raw);
        try expectDecodedShape(case, slot);
        const rebuilt = try rebuild(slot);
        try expectDecodedShape(case, rebuilt);

        if (index != 0) {
            try testing.expectEqual(cases[index - 1].raw + 1, case.raw);
        }
    }

    try testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), xarray_slot_view.fromRaw(cases[0].raw).value());
    try testing.expectEqual(@as(?isize, -4095), xarray_slot_view.fromRaw(cases[2].raw).errorCode());
    try testing.expectEqual(@as(?isize, -4094), xarray_slot_view.fromRaw(cases[3].raw).errorCode());
    try testing.expectEqual(xarray_slot_view.SlotKind.pointer, xarray_slot_view.fromRaw(cases[1].raw).kind());
}
