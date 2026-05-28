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

test "wrapped-high cutover ladder lands on alternating odd raws across value and err lanes" {
    const base = wrappedHighCutoverBase();
    const cases = [_]struct {
        offset: usize,
        expected_raw: usize,
        expected_kind: xarray_slot_view.SlotKind,
        expected_value: ?usize,
    }{
        .{
            .offset = 0,
            .expected_raw = err_ptr.err_floor - 4,
            .expected_kind = .value,
            .expected_value = xa_value.safe_inline_limit - 1,
        },
        .{
            .offset = 1,
            .expected_raw = err_ptr.err_floor - 2,
            .expected_kind = .value,
            .expected_value = xa_value.safe_inline_limit,
        },
        .{
            .offset = 2,
            .expected_raw = err_ptr.err_floor,
            .expected_kind = .err,
            .expected_value = null,
        },
        .{
            .offset = 3,
            .expected_raw = err_ptr.err_floor + 2,
            .expected_kind = .err,
            .expected_value = null,
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
        try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
    }

    try std.testing.expectEqual(@as(usize, 2), cases[1].expected_raw - cases[0].expected_raw);
    try std.testing.expectEqual(@as(usize, 2), cases[2].expected_raw - cases[1].expected_raw);
    try std.testing.expectEqual(@as(usize, 2), cases[3].expected_raw - cases[2].expected_raw);
}

test "skipped raws around the cutover keep the pointer to err split explicit" {
    const first_skipped = err_ptr.err_floor - 3;
    const second_skipped = err_ptr.err_floor - 1;
    const third_skipped = err_ptr.err_floor + 1;

    const first_slot = xarray_slot_view.fromRaw(first_skipped);
    const second_slot = xarray_slot_view.fromRaw(second_skipped);
    const third_slot = xarray_slot_view.fromRaw(third_skipped);

    try std.testing.expectEqual(xarray_slot_view.SlotKind.pointer, first_slot.kind());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.pointer, second_slot.kind());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, third_slot.kind());

    try std.testing.expectEqual(@as(?usize, first_skipped), first_slot.pointerValue());
    try std.testing.expectEqual(@as(?usize, second_skipped), second_slot.pointerValue());
    try std.testing.expectEqual(@as(?isize, err_ptr.toErrorCode(third_skipped)), third_slot.errorCode());

    try std.testing.expect(!xarray_slot_view.isTaggedInternalEntry(first_skipped));
    try std.testing.expect(!xarray_slot_view.isTaggedInternalEntry(second_skipped));
    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(third_skipped));
}

test "cutover ladder aliases stay aligned with accepted top values and odd err constructors" {
    const base = wrappedHighCutoverBase();

    const wrapped_top_minus_one_raw = projectedRaw(base);
    const wrapped_top_raw = projectedRaw(base + 1);
    const wrapped_first_err_raw = projectedRaw(base + 2);
    const wrapped_second_err_raw = projectedRaw(base + 3);

    const top_minus_one_slot = try xarray_slot_view.fromValue(xa_value.safe_inline_limit - 1);
    const top_slot = try xarray_slot_view.fromValue(xa_value.safe_inline_limit);
    const first_err_slot = xarray_slot_view.fromErrorCode(-@as(isize, @intCast(err_ptr.max_errno)));
    const second_err_slot = xarray_slot_view.fromRaw(wrapped_second_err_raw);

    try std.testing.expectEqual(top_minus_one_slot.rawValue(), wrapped_top_minus_one_raw);
    try std.testing.expectEqual(top_slot.rawValue(), wrapped_top_raw);
    try std.testing.expectEqual(first_err_slot.rawValue(), wrapped_first_err_raw);
    try std.testing.expectEqual(err_ptr.toErrorCode(wrapped_second_err_raw), second_err_slot.errorCode().?);
    try std.testing.expectEqual(@as(isize, -4093), second_err_slot.errorCode().?);
    try std.testing.expectEqual(err_ptr.fromErrorCode(-4093), wrapped_second_err_raw);
}
