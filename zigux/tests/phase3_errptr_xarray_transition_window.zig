const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const Case = struct {
    name: []const u8,
    raw: usize,
    expected_kind: xarray_slot_view.SlotKind,
    expected_value: ?usize = null,
    expected_error: ?isize = null,
    expected_pointer: ?usize = null,
};

fn expectCase(case: Case) !void {
    const slot = xarray_slot_view.fromRaw(case.raw);

    try testing.expectEqual(case.expected_kind, slot.kind());
    try testing.expectEqual(case.raw, slot.rawValue());
    try testing.expectEqual(case.expected_value, slot.value());
    try testing.expectEqual(case.expected_error, slot.errorCode());
    try testing.expectEqual(case.expected_pointer, slot.pointerValue());
}

test "transition window classifies the inline ceiling pointer gap and err floor exactly once each" {
    const last_inline_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const cases = [_]Case{
        .{
            .name = "inline_limit_minus_one",
            .raw = try xa_value.makeValue(xa_value.safe_inline_limit - 1),
            .expected_kind = .value,
            .expected_value = xa_value.safe_inline_limit - 1,
        },
        .{
            .name = "inline_limit",
            .raw = last_inline_raw,
            .expected_kind = .value,
            .expected_value = xa_value.safe_inline_limit,
        },
        .{
            .name = "pointer_gap",
            .raw = err_ptr.err_floor - 1,
            .expected_kind = .pointer,
            .expected_pointer = err_ptr.err_floor - 1,
        },
        .{
            .name = "err_floor",
            .raw = err_ptr.err_floor,
            .expected_kind = .err,
            .expected_error = -4095,
        },
        .{
            .name = "err_floor_plus_one",
            .raw = err_ptr.err_floor + 1,
            .expected_kind = .err,
            .expected_error = -4094,
        },
    };

    for (cases) |case| {
        try expectCase(case);
    }
}

test "the transition window is contiguous across the last xa_value pointer gap and first err_ptr" {
    const last_inline_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const pointer_gap_raw = err_ptr.err_floor - 1;
    const first_err_raw = err_ptr.err_floor;

    try testing.expectEqual(last_inline_raw + 1, pointer_gap_raw);
    try testing.expectEqual(pointer_gap_raw + 1, first_err_raw);

    try testing.expect(xa_value.isValue(last_inline_raw));
    try testing.expect(!err_ptr.isErrValue(last_inline_raw));

    try testing.expect(!xa_value.isValue(pointer_gap_raw));
    try testing.expect(!err_ptr.isErrValue(pointer_gap_raw));

    try testing.expect(!xa_value.isValue(first_err_raw));
    try testing.expect(err_ptr.isErrValue(first_err_raw));
}

test "constructor and raw rereads agree at the exact lane boundaries" {
    const value_slot = try xarray_slot_view.fromValue(xa_value.safe_inline_limit);
    const pointer_slot = xarray_slot_view.fromPointer(err_ptr.err_floor - 1);
    const err_slot = xarray_slot_view.fromErrorCode(-4095);

    try testing.expectEqual(value_slot.rawValue(), (try xa_value.makeValue(xa_value.safe_inline_limit)));
    try testing.expectEqual(pointer_slot.rawValue(), err_ptr.err_floor - 1);
    try testing.expectEqual(err_slot.rawValue(), err_ptr.err_floor);

    try testing.expectEqual(value_slot.kind(), xarray_slot_view.fromRaw(value_slot.rawValue()).kind());
    try testing.expectEqual(pointer_slot.kind(), xarray_slot_view.fromRaw(pointer_slot.rawValue()).kind());
    try testing.expectEqual(err_slot.kind(), xarray_slot_view.fromRaw(err_slot.rawValue()).kind());
}
