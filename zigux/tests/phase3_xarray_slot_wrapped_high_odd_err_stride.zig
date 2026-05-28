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

test "wrapped-high source steps stay contiguous while odd raws cross from value to err lanes" {
    const base = wrappedHighCutoverBase();
    const cases = [_]struct {
        offset: usize,
        expected_raw: usize,
        expected_kind: xarray_slot_view.SlotKind,
        expected_value: ?usize,
        expected_error: ?isize,
    }{
        .{
            .offset = 0,
            .expected_raw = err_ptr.err_floor - 4,
            .expected_kind = .value,
            .expected_value = xa_value.safe_inline_limit - 1,
            .expected_error = null,
        },
        .{
            .offset = 1,
            .expected_raw = err_ptr.err_floor - 2,
            .expected_kind = .value,
            .expected_value = xa_value.safe_inline_limit,
            .expected_error = null,
        },
        .{
            .offset = 2,
            .expected_raw = err_ptr.err_floor,
            .expected_kind = .err,
            .expected_value = null,
            .expected_error = -4095,
        },
        .{
            .offset = 3,
            .expected_raw = err_ptr.err_floor + 2,
            .expected_kind = .err,
            .expected_value = null,
            .expected_error = -4093,
        },
    };

    inline for (cases) |case| {
        const source = base + case.offset;
        const raw = projectedRaw(source);
        const slot = xarray_slot_view.fromRaw(raw);

        try std.testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(source));
        try std.testing.expectEqual(case.expected_raw, raw);
        try std.testing.expectEqual(case.expected_kind, slot.kind());
        try std.testing.expectEqual(case.expected_value, slot.value());
        try std.testing.expectEqual(case.expected_error, slot.errorCode());
        try std.testing.expect((raw & xa_value.value_tag_mask) == xa_value.value_tag_mask);
        try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
    }

    try std.testing.expectEqual(@as(usize, 1), (base + 1) - base);
    try std.testing.expectEqual(@as(usize, 1), (base + 2) - (base + 1));
    try std.testing.expectEqual(@as(usize, 1), (base + 3) - (base + 2));
    try std.testing.expectEqual(@as(usize, 2), cases[1].expected_raw - cases[0].expected_raw);
    try std.testing.expectEqual(@as(usize, 2), cases[2].expected_raw - cases[1].expected_raw);
    try std.testing.expectEqual(@as(usize, 2), cases[3].expected_raw - cases[2].expected_raw);
}

test "wrapped-high cutover skips the pointer gap and even err raws" {
    const base = wrappedHighCutoverBase();
    const top_value_raw = projectedRaw(base + 1);
    const first_err_raw = projectedRaw(base + 2);
    const second_err_raw = projectedRaw(base + 3);

    const pointer_gap_raw = top_value_raw + 1;
    const even_err_raw = first_err_raw + 1;

    const pointer_gap_slot = xarray_slot_view.fromRaw(pointer_gap_raw);
    const first_err_slot = xarray_slot_view.fromRaw(first_err_raw);
    const even_err_slot = xarray_slot_view.fromRaw(even_err_raw);
    const second_err_slot = xarray_slot_view.fromRaw(second_err_raw);

    try std.testing.expectEqual(err_ptr.err_floor - 2, top_value_raw);
    try std.testing.expectEqual(err_ptr.err_floor - 1, pointer_gap_raw);
    try std.testing.expectEqual(err_ptr.err_floor, first_err_raw);
    try std.testing.expectEqual(err_ptr.err_floor + 1, even_err_raw);
    try std.testing.expectEqual(err_ptr.err_floor + 2, second_err_raw);

    try std.testing.expectEqual(xarray_slot_view.SlotKind.pointer, pointer_gap_slot.kind());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, first_err_slot.kind());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, even_err_slot.kind());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, second_err_slot.kind());

    try std.testing.expectEqual(@as(?usize, pointer_gap_raw), pointer_gap_slot.pointerValue());
    try std.testing.expectEqual(@as(?isize, -4095), first_err_slot.errorCode());
    try std.testing.expectEqual(@as(?isize, -4094), even_err_slot.errorCode());
    try std.testing.expectEqual(@as(?isize, -4093), second_err_slot.errorCode());

    try std.testing.expect(!xarray_slot_view.isTaggedInternalEntry(pointer_gap_raw));
    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(first_err_raw));
    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(even_err_raw));
    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(second_err_raw));
}

test "wrapped-high err aliases stay aligned with odd err_ptr constructors only" {
    const base = wrappedHighCutoverBase();
    const first_err_raw = projectedRaw(base + 2);
    const second_err_raw = projectedRaw(base + 3);
    const even_err_raw = first_err_raw + 1;

    const first_err_slot = xarray_slot_view.fromErrorCode(-@as(isize, @intCast(err_ptr.max_errno)));
    const second_err_slot = xarray_slot_view.fromErrorCode(-4093);
    const even_err_slot = xarray_slot_view.fromErrorCode(-4094);

    try std.testing.expectEqual(first_err_slot.rawValue(), first_err_raw);
    try std.testing.expectEqual(second_err_slot.rawValue(), second_err_raw);
    try std.testing.expectEqual(even_err_slot.rawValue(), even_err_raw);

    try std.testing.expectEqual(@as(usize, 2), second_err_raw - first_err_raw);
    try std.testing.expectEqual(@as(usize, 1), even_err_raw - first_err_raw);
    try std.testing.expect((first_err_raw & xa_value.value_tag_mask) == xa_value.value_tag_mask);
    try std.testing.expect((second_err_raw & xa_value.value_tag_mask) == xa_value.value_tag_mask);
    try std.testing.expect((even_err_raw & xa_value.value_tag_mask) == 0);
}
