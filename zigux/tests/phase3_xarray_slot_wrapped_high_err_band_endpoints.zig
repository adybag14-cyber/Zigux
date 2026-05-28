const std = @import("std");

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn wrappedHighCutoverBase() usize {
    return (@as(usize, 1) << (@bitSizeOf(usize) - 1)) + (xa_value.safe_inline_limit - 1);
}

fn projectedRaw(source_value: usize) usize {
    return (source_value << 1) | xa_value.value_tag_mask;
}

fn firstWrappedHighErrSource() usize {
    return wrappedHighCutoverBase() + 2;
}

test "wrapped-high err band starts at the first reachable odd err alias" {
    const source = firstWrappedHighErrSource();
    const previous_source = source - 1;

    const first_err_raw = projectedRaw(source);
    const previous_raw = projectedRaw(previous_source);

    const first_err_alias = xarray_slot_view.fromRaw(first_err_raw);
    const previous_alias = xarray_slot_view.fromRaw(previous_raw);
    const first_err_constructor = xarray_slot_view.fromErrorCode(-@as(isize, @intCast(err_ptr.max_errno)));

    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(source));
    try std.testing.expectEqual(err_ptr.err_floor, first_err_raw);
    try std.testing.expectEqual(err_ptr.err_floor - 2, previous_raw);
    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, first_err_alias.kind());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.value, previous_alias.kind());
    try std.testing.expectEqual(first_err_constructor.rawValue(), first_err_raw);
    try std.testing.expectEqual(@as(?isize, -4095), first_err_alias.errorCode());
    try std.testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), previous_alias.value());
    try std.testing.expect((first_err_raw & xa_value.value_tag_mask) == xa_value.value_tag_mask);
}

test "wrapped-high err band ends at the top odd err alias when the source reaches usize max" {
    const source = std.math.maxInt(usize);
    const previous_source = source - 1;

    const top_err_raw = projectedRaw(source);
    const previous_top_err_raw = projectedRaw(previous_source);

    const top_err_alias = xarray_slot_view.fromRaw(top_err_raw);
    const previous_top_err_alias = xarray_slot_view.fromRaw(previous_top_err_raw);
    const top_err_constructor = xarray_slot_view.fromErrorCode(-1);
    const previous_top_err_constructor = xarray_slot_view.fromErrorCode(-3);

    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(previous_source));
    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(source));
    try std.testing.expectEqual(std.math.maxInt(usize), top_err_raw);
    try std.testing.expectEqual(top_err_constructor.rawValue(), top_err_raw);
    try std.testing.expectEqual(previous_top_err_constructor.rawValue(), previous_top_err_raw);
    try std.testing.expectEqual(@as(?isize, -1), top_err_alias.errorCode());
    try std.testing.expectEqual(@as(?isize, -3), previous_top_err_alias.errorCode());
    try std.testing.expectEqual(@as(usize, 2), top_err_raw - previous_top_err_raw);
    try std.testing.expect((top_err_raw & xa_value.value_tag_mask) == xa_value.value_tag_mask);
}

test "wrapped-high err sources cover exactly the reachable odd err aliases" {
    const first_source = firstWrappedHighErrSource();
    const last_source = std.math.maxInt(usize);
    const source_count = last_source - first_source + 1;

    const first_raw = projectedRaw(first_source);
    const last_raw = projectedRaw(last_source);
    const odd_err_count = ((last_raw - first_raw) / 2) + 1;

    try std.testing.expectEqual(err_ptr.err_floor, first_raw);
    try std.testing.expectEqual(std.math.maxInt(usize), last_raw);
    try std.testing.expectEqual(@as(usize, (err_ptr.max_errno + 1) / 2), source_count);
    try std.testing.expectEqual(source_count, odd_err_count);
    try std.testing.expectEqual(@as(usize, err_ptr.max_errno - 1), last_raw - first_raw);
}
