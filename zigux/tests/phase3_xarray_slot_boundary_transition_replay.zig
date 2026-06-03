const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;

const BoundaryCase = struct {
    label: []const u8,
    raw: usize,
    kind: SlotKind,
    value: ?usize = null,
    error_code: ?isize = null,
    pointer: ?usize = null,
    tagged: bool,
};

fn expectBoundaryCase(case: BoundaryCase) !void {
    const slot = xarray_slot_view.fromRaw(case.raw);

    try std.testing.expectEqual(case.raw, slot.rawValue());
    try std.testing.expectEqual(case.kind, slot.kind());
    try std.testing.expectEqual(case.value, slot.value());
    try std.testing.expectEqual(case.error_code, slot.errorCode());
    try std.testing.expectEqual(case.pointer, slot.pointerValue());
    try std.testing.expectEqual(case.tagged, xarray_slot_view.isTaggedInternalEntry(case.raw));
}

test "slot boundary transitions stay stable around the inline value ceiling" {
    const highest_value_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const rejected_alias_raw = ((xa_value.safe_inline_limit + 1) << 1) | xa_value.value_tag_mask;

    try std.testing.expectEqual(err_ptr.err_floor - 2, highest_value_raw);
    try std.testing.expectEqual(err_ptr.err_floor, rejected_alias_raw);
    try std.testing.expectEqual(err_ptr.err_floor - 1, highest_value_raw + 1);

    const cases = [_]BoundaryCase{
        .{
            .label = "highest inline xa_value",
            .raw = highest_value_raw,
            .kind = .value,
            .value = xa_value.safe_inline_limit,
            .tagged = true,
        },
        .{
            .label = "odd pointer-like gap below err floor",
            .raw = err_ptr.err_floor - 1,
            .kind = .pointer,
            .pointer = err_ptr.err_floor - 1,
            .tagged = false,
        },
        .{
            .label = "rejected xa_value alias at err floor",
            .raw = rejected_alias_raw,
            .kind = .err,
            .error_code = -4095,
            .tagged = true,
        },
        .{
            .label = "next errno after floor",
            .raw = err_ptr.err_floor + 1,
            .kind = .err,
            .error_code = -4094,
            .tagged = true,
        },
    };

    for (cases) |case| {
        try std.testing.expect(case.label.len > 0);
        try expectBoundaryCase(case);
    }

    try std.testing.expectError(
        error.ValueWouldOverlapErrPtr,
        xa_value.makeValue(xa_value.safe_inline_limit + 1),
    );
}

test "constructor and raw views agree across neighboring boundary lanes" {
    const value_slot = try xarray_slot_view.fromValue(xa_value.safe_inline_limit);
    const pointer_slot = xarray_slot_view.fromPointer(err_ptr.err_floor - 1);
    const err_floor_slot = xarray_slot_view.fromErrorCode(-4095);
    const next_err_slot = xarray_slot_view.fromErrorCode(-4094);

    try std.testing.expectEqual(xarray_slot_view.fromRaw(value_slot.rawValue()).kind(), value_slot.kind());
    try std.testing.expectEqual(xarray_slot_view.fromRaw(pointer_slot.rawValue()).kind(), pointer_slot.kind());
    try std.testing.expectEqual(xarray_slot_view.fromRaw(err_floor_slot.rawValue()).kind(), err_floor_slot.kind());
    try std.testing.expectEqual(xarray_slot_view.fromRaw(next_err_slot.rawValue()).kind(), next_err_slot.kind());

    try std.testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), value_slot.value());
    try std.testing.expectEqual(@as(?usize, err_ptr.err_floor - 1), pointer_slot.pointerValue());
    try std.testing.expectEqual(@as(?isize, -4095), err_floor_slot.errorCode());
    try std.testing.expectEqual(@as(?isize, -4094), next_err_slot.errorCode());
}
