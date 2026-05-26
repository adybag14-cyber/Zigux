const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const Case = struct {
    name: []const u8,
    slot: xarray_slot_view.SlotView,
    expected_kind: xarray_slot_view.SlotKind,
    expected_tagged: bool,
    expected_ok: bool,
    expected_value: ?usize = null,
    expected_error: ?isize = null,
    expected_pointer: ?usize = null,
};

fn expectCase(case: Case) !void {
    const raw = case.slot.rawValue();

    try testing.expectEqual(case.expected_kind, case.slot.kind());
    try testing.expectEqual(case.expected_tagged, xarray_slot_view.isTaggedInternalEntry(raw));
    try testing.expectEqual(case.expected_ok, err_ptr.isOkValue(raw));
    try testing.expectEqual(!case.expected_ok, err_ptr.isErrValue(raw));
    try testing.expectEqual(case.expected_value, case.slot.value());
    try testing.expectEqual(case.expected_error, case.slot.errorCode());
    try testing.expectEqual(case.expected_pointer, case.slot.pointerValue());
    try testing.expectEqual(case.expected_kind == .value, xa_value.isValue(raw));
}

test "tagged lane replay keeps constructor outputs partitioned across the four slot kinds" {
    const null_slot = xarray_slot_view.nullSlot();
    const pointer_slot = xarray_slot_view.fromPointer(err_ptr.err_floor - 1);
    const inline_zero = try xarray_slot_view.fromValue(0);
    const inline_limit = try xarray_slot_view.fromValue(xa_value.safe_inline_limit);
    const err_floor_slot = xarray_slot_view.fromErrorCode(-@as(isize, @intCast(err_ptr.max_errno)));
    const err_top_slot = xarray_slot_view.fromErrorCode(-1);

    const cases = [_]Case{
        .{
            .name = "null",
            .slot = null_slot,
            .expected_kind = .null,
            .expected_tagged = false,
            .expected_ok = true,
        },
        .{
            .name = "pointer_gap",
            .slot = pointer_slot,
            .expected_kind = .pointer,
            .expected_tagged = false,
            .expected_ok = true,
            .expected_pointer = err_ptr.err_floor - 1,
        },
        .{
            .name = "inline_zero",
            .slot = inline_zero,
            .expected_kind = .value,
            .expected_tagged = true,
            .expected_ok = true,
            .expected_value = 0,
        },
        .{
            .name = "inline_limit",
            .slot = inline_limit,
            .expected_kind = .value,
            .expected_tagged = true,
            .expected_ok = true,
            .expected_value = xa_value.safe_inline_limit,
        },
        .{
            .name = "err_floor",
            .slot = err_floor_slot,
            .expected_kind = .err,
            .expected_tagged = true,
            .expected_ok = false,
            .expected_error = -4095,
        },
        .{
            .name = "err_top",
            .slot = err_top_slot,
            .expected_kind = .err,
            .expected_tagged = true,
            .expected_ok = false,
            .expected_error = -1,
        },
    };

    for (cases) |case| {
        _ = case.name;
        try expectCase(case);
    }
}

test "tagged lane replay keeps rejected inline values on the err side of the partition" {
    const overlapping_value = xa_value.safe_inline_limit + 1;
    const raw = (overlapping_value << 1) | xa_value.value_tag_mask;
    const slot = xarray_slot_view.fromRaw(raw);

    try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(overlapping_value));
    try testing.expectEqual(err_ptr.err_floor, raw);
    try testing.expect(err_ptr.isErrValue(raw));
    try testing.expect(!err_ptr.isOkValue(raw));
    try testing.expect(!xa_value.isValue(raw));
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
    try testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
    try testing.expectEqual(@as(?isize, -4095), slot.errorCode());
}

test "tagged lane replay keeps the last ok raw pair split between pointer and value lanes" {
    const pointer_raw = err_ptr.err_floor - 1;
    const value_raw = err_ptr.err_floor - 2;

    const pointer_slot = xarray_slot_view.fromRaw(pointer_raw);
    const value_slot = xarray_slot_view.fromRaw(value_raw);

    try testing.expect(err_ptr.isOkValue(pointer_raw));
    try testing.expect(!err_ptr.isErrValue(pointer_raw));
    try testing.expect(!xa_value.isValue(pointer_raw));
    try testing.expect(!xarray_slot_view.isTaggedInternalEntry(pointer_raw));
    try testing.expectEqual(xarray_slot_view.SlotKind.pointer, pointer_slot.kind());
    try testing.expectEqual(@as(?usize, pointer_raw), pointer_slot.pointerValue());

    try testing.expect(err_ptr.isOkValue(value_raw));
    try testing.expect(!err_ptr.isErrValue(value_raw));
    try testing.expect(xa_value.isValue(value_raw));
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(value_raw));
    try testing.expectEqual(xarray_slot_view.SlotKind.value, value_slot.kind());
    try testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), value_slot.value());
}
