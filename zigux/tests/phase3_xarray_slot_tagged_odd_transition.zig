const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn expectValueOdd(raw: usize, expected_value: usize) !void {
    const slot = xarray_slot_view.fromRaw(raw);

    try testing.expect((raw & xa_value.value_tag_mask) == xa_value.value_tag_mask);
    try testing.expect(slot.isValue());
    try testing.expect(!slot.isErr());
    try testing.expect(!slot.isPointer());
    try testing.expectEqual(@as(?usize, expected_value), slot.value());
    try testing.expectEqual(@as(?isize, null), slot.errorCode());
    try testing.expectEqual(raw, try xa_value.makeValue(expected_value));
}

fn expectErrOdd(raw: usize, expected_code: isize) !void {
    const slot = xarray_slot_view.fromRaw(raw);

    try testing.expect((raw & xa_value.value_tag_mask) == xa_value.value_tag_mask);
    try testing.expect(!slot.isValue());
    try testing.expect(slot.isErr());
    try testing.expect(!slot.isPointer());
    try testing.expectEqual(@as(?usize, null), slot.value());
    try testing.expectEqual(@as(?isize, expected_code), slot.errorCode());
    try testing.expectEqual(raw, xarray_slot_view.fromErrorCode(expected_code).rawValue());
}

test "tagged odd transition flips families exactly at the cutoff" {
    const accepted_top = try xa_value.makeValue(xa_value.safe_inline_limit);
    const first_rejected = err_ptr.err_floor;
    const gap = err_ptr.err_floor - 1;

    try testing.expectEqual(err_ptr.err_floor - 2, accepted_top);
    try testing.expectEqual(@as(usize, 2), first_rejected - accepted_top);
    try testing.expect((accepted_top & xa_value.value_tag_mask) == xa_value.value_tag_mask);
    try testing.expect((first_rejected & xa_value.value_tag_mask) == xa_value.value_tag_mask);

    try expectValueOdd(accepted_top, xa_value.safe_inline_limit);
    try testing.expect(xarray_slot_view.fromRaw(gap).isPointer());
    try expectErrOdd(first_rejected, -4095);
}

test "odd raw ladder stays contiguous while the lane flips once" {
    const accepted_top = try xa_value.makeValue(xa_value.safe_inline_limit);
    const accepted_prev = accepted_top - 2;
    const rejected_floor = err_ptr.err_floor;
    const rejected_next = rejected_floor + 2;
    const rejected_after = rejected_floor + 4;

    try testing.expectEqual(@as(usize, 2), accepted_top - accepted_prev);
    try testing.expectEqual(@as(usize, 2), rejected_floor - accepted_top);
    try testing.expectEqual(@as(usize, 2), rejected_next - rejected_floor);
    try testing.expectEqual(@as(usize, 2), rejected_after - rejected_next);

    try expectValueOdd(accepted_prev, xa_value.safe_inline_limit - 1);
    try expectValueOdd(accepted_top, xa_value.safe_inline_limit);
    try expectErrOdd(rejected_floor, -4095);
    try expectErrOdd(rejected_next, -4093);
    try expectErrOdd(rejected_after, -4091);
}

test "odd transition preserves raw-to-payload equations on both sides" {
    const accepted_low = try xa_value.makeValue(xa_value.safe_inline_limit - 2);
    const accepted_high = try xa_value.makeValue(xa_value.safe_inline_limit);
    const rejected_low = err_ptr.err_floor;
    const rejected_high = err_ptr.err_floor + 6;

    try testing.expectEqual(xa_value.safe_inline_limit - 2, accepted_low >> 1);
    try testing.expectEqual(xa_value.safe_inline_limit, accepted_high >> 1);
    try testing.expectEqual(@as(isize, -4095), err_ptr.toErrorCode(rejected_low));
    try testing.expectEqual(@as(isize, -4089), err_ptr.toErrorCode(rejected_high));

    try expectValueOdd(accepted_low, xa_value.safe_inline_limit - 2);
    try expectValueOdd(accepted_high, xa_value.safe_inline_limit);
    try expectErrOdd(rejected_low, -4095);
    try expectErrOdd(rejected_high, -4089);
}
