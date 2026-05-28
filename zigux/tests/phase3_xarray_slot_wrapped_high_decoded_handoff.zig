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

test "wrapped-high decoded handoff keeps accepted top-value raws visible through rejected sources" {
    const base = wrappedHighCutoverBase();

    const accepted_top_minus_one = try xarray_slot_view.fromValue(xa_value.safe_inline_limit - 1);
    const accepted_top = try xarray_slot_view.fromValue(xa_value.safe_inline_limit);

    const rejected_source_minus_one = base;
    const rejected_source_top = base + 1;

    const rejected_alias_minus_one_raw = projectedRaw(rejected_source_minus_one);
    const rejected_alias_top_raw = projectedRaw(rejected_source_top);
    const rejected_alias_minus_one = xarray_slot_view.fromRaw(rejected_alias_minus_one_raw);
    const rejected_alias_top = xarray_slot_view.fromRaw(rejected_alias_top_raw);

    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(rejected_source_minus_one));
    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(rejected_source_top));

    try std.testing.expectEqual(accepted_top_minus_one.rawValue(), rejected_alias_minus_one_raw);
    try std.testing.expectEqual(accepted_top.rawValue(), rejected_alias_top_raw);
    try std.testing.expectEqual(xarray_slot_view.SlotKind.value, rejected_alias_minus_one.kind());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.value, rejected_alias_top.kind());
    try std.testing.expectEqual(@as(?usize, xa_value.safe_inline_limit - 1), rejected_alias_minus_one.value());
    try std.testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), rejected_alias_top.value());
    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(rejected_alias_minus_one_raw));
    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(rejected_alias_top_raw));
}

test "decoded handoff keeps the skipped pointer raws explicit on both sides of the err floor" {
    const base = wrappedHighCutoverBase();
    const top_value_raw = projectedRaw(base + 1);
    const first_err_raw = projectedRaw(base + 2);

    const high_pointer_gap_raw = top_value_raw + 1;
    const floor_pointer_gap_raw = first_err_raw - 1;

    const high_pointer_gap = xarray_slot_view.fromRaw(high_pointer_gap_raw);
    const floor_pointer_gap = xarray_slot_view.fromRaw(floor_pointer_gap_raw);

    try std.testing.expectEqual(err_ptr.err_floor - 2, top_value_raw);
    try std.testing.expectEqual(err_ptr.err_floor - 1, high_pointer_gap_raw);
    try std.testing.expectEqual(err_ptr.err_floor - 1, floor_pointer_gap_raw);
    try std.testing.expectEqual(err_ptr.err_floor, first_err_raw);

    try std.testing.expectEqual(xarray_slot_view.SlotKind.pointer, high_pointer_gap.kind());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.pointer, floor_pointer_gap.kind());
    try std.testing.expectEqual(@as(?usize, high_pointer_gap_raw), high_pointer_gap.pointerValue());
    try std.testing.expectEqual(@as(?usize, floor_pointer_gap_raw), floor_pointer_gap.pointerValue());
    try std.testing.expectEqual(@as(?usize, null), high_pointer_gap.value());
    try std.testing.expectEqual(@as(?isize, null), floor_pointer_gap.errorCode());
    try std.testing.expect(!xarray_slot_view.isTaggedInternalEntry(high_pointer_gap_raw));
}

test "wrapped-high decoded handoff reaches the first odd err aliases and skips the even err raw" {
    const base = wrappedHighCutoverBase();

    const first_err_raw = projectedRaw(base + 2);
    const next_odd_err_raw = projectedRaw(base + 3);
    const skipped_even_err_raw = first_err_raw + 1;

    const first_err_alias = xarray_slot_view.fromRaw(first_err_raw);
    const next_odd_err_alias = xarray_slot_view.fromRaw(next_odd_err_raw);
    const skipped_even_err = xarray_slot_view.fromRaw(skipped_even_err_raw);

    const first_err_constructor = xarray_slot_view.fromErrorCode(-@as(isize, @intCast(err_ptr.max_errno)));
    const next_odd_err_constructor = xarray_slot_view.fromErrorCode(-4093);
    const skipped_even_err_constructor = xarray_slot_view.fromErrorCode(-4094);

    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(base + 2));
    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(base + 3));

    try std.testing.expectEqual(first_err_constructor.rawValue(), first_err_raw);
    try std.testing.expectEqual(next_odd_err_constructor.rawValue(), next_odd_err_raw);
    try std.testing.expectEqual(skipped_even_err_constructor.rawValue(), skipped_even_err_raw);
    try std.testing.expectEqual(@as(isize, -4095), first_err_alias.errorCode().?);
    try std.testing.expectEqual(@as(isize, -4093), next_odd_err_alias.errorCode().?);
    try std.testing.expectEqual(@as(isize, -4094), skipped_even_err.errorCode().?);
    try std.testing.expectEqual(@as(usize, 2), next_odd_err_raw - first_err_raw);
    try std.testing.expectEqual(@as(usize, 1), skipped_even_err_raw - first_err_raw);
    try std.testing.expect((first_err_raw & xa_value.value_tag_mask) == xa_value.value_tag_mask);
    try std.testing.expect((next_odd_err_raw & xa_value.value_tag_mask) == xa_value.value_tag_mask);
    try std.testing.expect((skipped_even_err_raw & xa_value.value_tag_mask) == 0);
}
