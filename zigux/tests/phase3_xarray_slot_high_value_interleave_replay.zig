const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn expectHighValueSlot(value: usize, expected_raw: usize) !void {
    const raw = try xa_value.makeValue(value);
    const slot = xarray_slot_view.fromRaw(raw);

    try testing.expectEqual(expected_raw, raw);
    try testing.expectEqual(expected_raw, slot.rawValue());
    try testing.expectEqual(xarray_slot_view.SlotKind.value, slot.kind());
    try testing.expect(slot.isTaggedEntry());
    try testing.expectEqual(@as(?usize, value), slot.value());
    try testing.expectEqual(@as(?isize, null), slot.errorCode());
    try testing.expectEqual(@as(?usize, null), slot.pointerValue());
}

fn expectPointerGap(raw: usize) !void {
    const slot = xarray_slot_view.fromRaw(raw);

    try testing.expectEqual(xarray_slot_view.SlotKind.pointer, slot.kind());
    try testing.expect(!slot.isTaggedEntry());
    try testing.expectEqual(@as(?usize, raw), slot.pointerValue());
    try testing.expectEqual(@as(?usize, null), slot.value());
    try testing.expectEqual(@as(?isize, null), slot.errorCode());
}

test "final accepted xa_values interleave with pointer-like raw gaps" {
    const values = [_]usize{
        xa_value.safe_inline_limit - 3,
        xa_value.safe_inline_limit - 2,
        xa_value.safe_inline_limit - 1,
        xa_value.safe_inline_limit,
    };
    const raws = [_]usize{
        err_ptr.err_floor - 8,
        err_ptr.err_floor - 6,
        err_ptr.err_floor - 4,
        err_ptr.err_floor - 2,
    };

    for (values, raws) |value, raw| {
        try expectHighValueSlot(value, raw);
        try expectPointerGap(raw + 1);
    }
}

test "first rejected high-window value lands on err_ptr floor" {
    const rejected = xa_value.safe_inline_limit + 1;
    const raw = (rejected << 1) | xa_value.value_tag_mask;
    const slot = xarray_slot_view.fromRaw(raw);

    try testing.expect(!xa_value.canRepresent(rejected));
    try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(rejected));
    try testing.expectEqual(err_ptr.err_floor, raw);
    try testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
    try testing.expect(slot.isTaggedEntry());
    try testing.expectEqual(@as(?isize, -4095), slot.errorCode());
    try testing.expectEqual(@as(?usize, null), slot.value());
    try testing.expectEqual(@as(?usize, null), slot.pointerValue());
}

test "high-window raw sequence has no hidden null slots" {
    const start = err_ptr.err_floor - 8;
    var offset: usize = 0;
    while (offset <= 8) : (offset += 1) {
        const raw = start + offset;
        const slot = xarray_slot_view.fromRaw(raw);

        try testing.expect(!slot.isNull());
        try testing.expectEqual(raw, slot.rawValue());
    }
}
