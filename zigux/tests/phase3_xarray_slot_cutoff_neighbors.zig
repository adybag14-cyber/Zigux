const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn expectValue(raw: usize, expected_value: usize) !void {
    const slot = xarray_slot_view.fromRaw(raw);

    try testing.expect(slot.isValue());
    try testing.expect(!slot.isErr());
    try testing.expect(!slot.isPointer());
    try testing.expectEqual(@as(?usize, expected_value), slot.value());
    try testing.expectEqual(@as(?isize, null), slot.errorCode());
    try testing.expectEqual(@as(?usize, null), slot.pointerValue());
}

fn expectPointer(raw: usize) !void {
    const slot = xarray_slot_view.fromRaw(raw);

    try testing.expect(!slot.isValue());
    try testing.expect(!slot.isErr());
    try testing.expect(slot.isPointer());
    try testing.expectEqual(@as(?usize, null), slot.value());
    try testing.expectEqual(@as(?isize, null), slot.errorCode());
    try testing.expectEqual(@as(?usize, raw), slot.pointerValue());
}

fn expectErr(raw: usize, expected_code: isize) !void {
    const slot = xarray_slot_view.fromRaw(raw);

    try testing.expect(!slot.isValue());
    try testing.expect(slot.isErr());
    try testing.expect(!slot.isPointer());
    try testing.expectEqual(@as(?usize, null), slot.value());
    try testing.expectEqual(@as(?isize, expected_code), slot.errorCode());
    try testing.expectEqual(@as(?usize, null), slot.pointerValue());
}

test "five consecutive cutoff neighbors keep the expected lane sequence" {
    const highest_value_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const pointer_gap_raw = err_ptr.err_floor - 1;
    const err_floor_raw = err_ptr.err_floor;
    const err_next_raw = err_floor_raw + 1;
    const err_after_raw = err_floor_raw + 2;

    try testing.expectEqual(err_ptr.err_floor - 2, highest_value_raw);
    try testing.expectEqual(@as(usize, 1), pointer_gap_raw - highest_value_raw);
    try testing.expectEqual(@as(usize, 1), err_floor_raw - pointer_gap_raw);
    try testing.expectEqual(@as(usize, 1), err_next_raw - err_floor_raw);
    try testing.expectEqual(@as(usize, 1), err_after_raw - err_next_raw);

    try expectValue(highest_value_raw, xa_value.safe_inline_limit);
    try expectPointer(pointer_gap_raw);
    try expectErr(err_floor_raw, -4095);
    try expectErr(err_next_raw, -4094);
    try expectErr(err_after_raw, -4093);
}

test "constructor helpers reproduce the cutoff neighborhood exactly" {
    const highest_value_slot = try xarray_slot_view.fromValue(xa_value.safe_inline_limit);
    const pointer_gap_slot = xarray_slot_view.fromPointer(err_ptr.err_floor - 1);
    const err_floor_slot = xarray_slot_view.fromErrorCode(-4095);
    const err_next_slot = xarray_slot_view.fromErrorCode(-4094);

    try testing.expectEqual(err_ptr.err_floor - 2, highest_value_slot.rawValue());
    try testing.expectEqual(err_ptr.err_floor - 1, pointer_gap_slot.rawValue());
    try testing.expectEqual(err_ptr.err_floor, err_floor_slot.rawValue());
    try testing.expectEqual(err_ptr.err_floor + 1, err_next_slot.rawValue());

    try testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), highest_value_slot.value());
    try testing.expectEqual(@as(?usize, err_ptr.err_floor - 1), pointer_gap_slot.pointerValue());
    try testing.expectEqual(@as(?isize, -4095), err_floor_slot.errorCode());
    try testing.expectEqual(@as(?isize, -4094), err_next_slot.errorCode());
}

test "cutoff equations keep value rejection and err decoding aligned" {
    const overlapping_value = xa_value.safe_inline_limit + 1;
    const overlapping_raw = (overlapping_value << 1) | xa_value.value_tag_mask;

    try testing.expectEqual(err_ptr.err_floor, overlapping_raw);
    try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(overlapping_value));
    try testing.expect(err_ptr.isErrValue(overlapping_raw));
    try testing.expect(!xa_value.isValue(overlapping_raw));
    try testing.expectEqual(@as(isize, -4095), err_ptr.toErrorCode(overlapping_raw));
    try testing.expectEqual(@as(isize, -4094), err_ptr.toErrorCode(overlapping_raw + 1));
    try testing.expectEqual(@as(isize, -4093), err_ptr.toErrorCode(overlapping_raw + 2));
}
