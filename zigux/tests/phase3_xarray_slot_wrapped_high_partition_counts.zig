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

test "wrapped-high source partition keeps the two accepted aliases ahead of the odd err band" {
    const base = wrappedHighCutoverBase();

    const accepted_minus_one_source = base;
    const accepted_top_source = base + 1;
    const first_err_source = base + 2;

    const accepted_minus_one_alias = xarray_slot_view.fromRaw(projectedRaw(accepted_minus_one_source));
    const accepted_top_alias = xarray_slot_view.fromRaw(projectedRaw(accepted_top_source));
    const first_err_alias = xarray_slot_view.fromRaw(projectedRaw(first_err_source));

    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(accepted_minus_one_source));
    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(accepted_top_source));
    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(first_err_source));

    try std.testing.expectEqual(xarray_slot_view.SlotKind.value, accepted_minus_one_alias.kind());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.value, accepted_top_alias.kind());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, first_err_alias.kind());
    try std.testing.expectEqual(@as(?usize, xa_value.safe_inline_limit - 1), accepted_minus_one_alias.value());
    try std.testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), accepted_top_alias.value());
    try std.testing.expectEqual(@as(?isize, -4095), first_err_alias.errorCode());
}

test "wrapped-high source interval is exactly two accepted aliases plus the reachable odd err sources" {
    const first_source = wrappedHighCutoverBase();
    const first_err_source = first_source + 2;
    const last_source = std.math.maxInt(usize);

    const accepted_source_count: usize = 2;
    const odd_err_source_count = last_source - first_err_source + 1;
    const total_source_count = last_source - first_source + 1;

    try std.testing.expectEqual(@as(usize, (err_ptr.max_errno + 1) / 2), odd_err_source_count);
    try std.testing.expectEqual(accepted_source_count + odd_err_source_count, total_source_count);
    try std.testing.expectEqual(@as(usize, 2 + ((err_ptr.max_errno + 1) / 2)), total_source_count);
}

test "wrapped-high transition keeps one pointer gap between the accepted top raw and the first err alias" {
    const base = wrappedHighCutoverBase();

    const accepted_top_raw = projectedRaw(base + 1);
    const pointer_gap_raw = accepted_top_raw + 1;
    const first_err_raw = projectedRaw(base + 2);

    const accepted_top_alias = xarray_slot_view.fromRaw(accepted_top_raw);
    const pointer_gap = xarray_slot_view.fromRaw(pointer_gap_raw);
    const first_err_alias = xarray_slot_view.fromRaw(first_err_raw);

    try std.testing.expectEqual(err_ptr.err_floor - 2, accepted_top_raw);
    try std.testing.expectEqual(err_ptr.err_floor - 1, pointer_gap_raw);
    try std.testing.expectEqual(err_ptr.err_floor, first_err_raw);

    try std.testing.expectEqual(xarray_slot_view.SlotKind.value, accepted_top_alias.kind());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.pointer, pointer_gap.kind());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, first_err_alias.kind());
    try std.testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), accepted_top_alias.value());
    try std.testing.expectEqual(@as(?usize, pointer_gap_raw), pointer_gap.pointerValue());
    try std.testing.expectEqual(@as(?isize, -4095), first_err_alias.errorCode());
    try std.testing.expect(!xarray_slot_view.isTaggedInternalEntry(pointer_gap_raw));
}
