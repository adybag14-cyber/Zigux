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

test "wrapped-high rejected sources collapse onto the current value and err constructor quartet" {
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
        const rejected_source = base + case.offset;
        const aliased_raw = projectedRaw(rejected_source);
        const aliased_slot = xarray_slot_view.fromRaw(aliased_raw);

        try std.testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(rejected_source));
        try std.testing.expectEqual(case.expected_raw, aliased_raw);
        try std.testing.expectEqual(case.expected_kind, aliased_slot.kind());
        try std.testing.expectEqual(case.expected_value, aliased_slot.value());
        try std.testing.expectEqual(case.expected_error, aliased_slot.errorCode());
        try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(aliased_raw));

        switch (case.expected_kind) {
            .value => {
                const constructor_slot = try xarray_slot_view.fromValue(case.expected_value.?);
                try std.testing.expectEqual(constructor_slot.rawValue(), aliased_raw);
            },
            .err => {
                const constructor_slot = xarray_slot_view.fromErrorCode(case.expected_error.?);
                try std.testing.expectEqual(constructor_slot.rawValue(), aliased_raw);
            },
            else => unreachable,
        }
    }
}

test "wrapped-high provenance keeps the pointer gap and first even err raw outside the rejected-source alias set" {
    const base = wrappedHighCutoverBase();

    const highest_value_alias_raw = projectedRaw(base + 1);
    const pointer_gap_raw = highest_value_alias_raw + 1;
    const first_odd_err_alias_raw = projectedRaw(base + 2);
    const first_even_err_raw = first_odd_err_alias_raw + 1;
    const second_odd_err_alias_raw = projectedRaw(base + 3);

    const pointer_gap = xarray_slot_view.fromPointer(pointer_gap_raw);
    const even_err = xarray_slot_view.fromErrorCode(-4094);

    try std.testing.expectEqual(err_ptr.err_floor - 2, highest_value_alias_raw);
    try std.testing.expectEqual(err_ptr.err_floor - 1, pointer_gap_raw);
    try std.testing.expectEqual(err_ptr.err_floor, first_odd_err_alias_raw);
    try std.testing.expectEqual(err_ptr.err_floor + 1, first_even_err_raw);
    try std.testing.expectEqual(err_ptr.err_floor + 2, second_odd_err_alias_raw);

    try std.testing.expectEqual(pointer_gap_raw, pointer_gap.rawValue());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.pointer, pointer_gap.kind());
    try std.testing.expectEqual(first_even_err_raw, even_err.rawValue());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, even_err.kind());

    try std.testing.expect(!xarray_slot_view.isTaggedInternalEntry(pointer_gap_raw));
    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(first_even_err_raw));
    try std.testing.expect(pointer_gap_raw != projectedRaw(base + 1));
    try std.testing.expect(pointer_gap_raw != projectedRaw(base + 2));
    try std.testing.expect(first_even_err_raw != projectedRaw(base + 2));
    try std.testing.expect(first_even_err_raw != projectedRaw(base + 3));
}

test "wrapped-high provenance keeps source steps contiguous while aliased raws advance in constructor-sized strides" {
    const base = wrappedHighCutoverBase();

    const first_source = base;
    const second_source = base + 1;
    const third_source = base + 2;
    const fourth_source = base + 3;

    const first_raw = projectedRaw(first_source);
    const second_raw = projectedRaw(second_source);
    const third_raw = projectedRaw(third_source);
    const fourth_raw = projectedRaw(fourth_source);

    try std.testing.expectEqual(@as(usize, 1), second_source - first_source);
    try std.testing.expectEqual(@as(usize, 1), third_source - second_source);
    try std.testing.expectEqual(@as(usize, 1), fourth_source - third_source);

    try std.testing.expectEqual(@as(usize, 2), second_raw - first_raw);
    try std.testing.expectEqual(@as(usize, 2), third_raw - second_raw);
    try std.testing.expectEqual(@as(usize, 2), fourth_raw - third_raw);

    try std.testing.expectEqual((try xarray_slot_view.fromValue(xa_value.safe_inline_limit - 1)).rawValue(), first_raw);
    try std.testing.expectEqual((try xarray_slot_view.fromValue(xa_value.safe_inline_limit)).rawValue(), second_raw);
    try std.testing.expectEqual(xarray_slot_view.fromErrorCode(-4095).rawValue(), third_raw);
    try std.testing.expectEqual(xarray_slot_view.fromErrorCode(-4093).rawValue(), fourth_raw);
}
