const std = @import("std");

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn wrappedHighSourceBase() usize {
    return (@as(usize, 1) << (@bitSizeOf(usize) - 1)) + (xa_value.safe_inline_limit - 3);
}

fn projectedRaw(source_value: usize) usize {
    return (source_value << 1) | xa_value.value_tag_mask;
}

test "wrapped-high rejected sources still decode as the top tagged value ladder" {
    const base = wrappedHighSourceBase();
    const cases = [_]struct {
        offset: usize,
        expected_raw: usize,
        expected_value: usize,
    }{
        .{ .offset = 0, .expected_raw = err_ptr.err_floor - 8, .expected_value = xa_value.safe_inline_limit - 3 },
        .{ .offset = 1, .expected_raw = err_ptr.err_floor - 6, .expected_value = xa_value.safe_inline_limit - 2 },
        .{ .offset = 2, .expected_raw = err_ptr.err_floor - 4, .expected_value = xa_value.safe_inline_limit - 1 },
        .{ .offset = 3, .expected_raw = err_ptr.err_floor - 2, .expected_value = xa_value.safe_inline_limit },
    };

    inline for (cases) |case| {
        const source = base + case.offset;
        const raw = projectedRaw(source);
        const slot = xarray_slot_view.fromRaw(raw);

        try std.testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(source));
        try std.testing.expectEqual(case.expected_raw, raw);
        try std.testing.expectEqual(xarray_slot_view.SlotKind.value, slot.kind());
        try std.testing.expectEqual(@as(?usize, case.expected_value), slot.value());
        try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
        try std.testing.expectEqual(@as(?isize, null), slot.errorCode());
        try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
    }
}

test "adjacent high even raws stay in the pointer lane beside wrapped-high aliases" {
    const base = wrappedHighSourceBase();

    inline for (0..4) |offset| {
        const source = base + offset;
        const value_raw = projectedRaw(source);
        const pointer_raw = value_raw + 1;
        const pointer_slot = xarray_slot_view.fromPointer(pointer_raw);
        const raw_slot = xarray_slot_view.fromRaw(pointer_raw);

        try std.testing.expectEqual(@as(usize, 1), pointer_raw - value_raw);
        try std.testing.expect(!xarray_slot_view.isTaggedInternalEntry(pointer_raw));
        try std.testing.expectEqual(xarray_slot_view.SlotKind.pointer, pointer_slot.kind());
        try std.testing.expectEqual(pointer_slot.kind(), raw_slot.kind());
        try std.testing.expectEqual(@as(?usize, pointer_raw), pointer_slot.pointerValue());
        try std.testing.expectEqual(@as(?usize, pointer_raw), raw_slot.pointerValue());
        try std.testing.expectEqual(@as(?usize, null), raw_slot.value());
        try std.testing.expectEqual(@as(?isize, null), raw_slot.errorCode());
    }
}

test "wrapped-high aliases and pointer neighbors alternate cleanly into err floor" {
    const base = wrappedHighSourceBase();

    inline for (0..4) |offset| {
        const source = base + offset;
        const value_raw = projectedRaw(source);
        const pointer_raw = value_raw + 1;
        const expected_value = (xa_value.safe_inline_limit - 3) + offset;
        const value_slot = xarray_slot_view.fromRaw(value_raw);
        const pointer_slot = xarray_slot_view.fromRaw(pointer_raw);

        try std.testing.expectEqual(xarray_slot_view.SlotKind.value, value_slot.kind());
        try std.testing.expectEqual(xarray_slot_view.SlotKind.pointer, pointer_slot.kind());
        try std.testing.expectEqual(@as(?usize, expected_value), value_slot.value());
        try std.testing.expectEqual(@as(?usize, pointer_raw), pointer_slot.pointerValue());
    }

    const top_value_raw = projectedRaw(base + 3);
    const top_pointer_raw = top_value_raw + 1;
    const err_raw = xarray_slot_view.fromErrorCode(-@as(isize, @intCast(err_ptr.max_errno))).rawValue();

    try std.testing.expectEqual(err_ptr.err_floor - 2, top_value_raw);
    try std.testing.expectEqual(err_ptr.err_floor - 1, top_pointer_raw);
    try std.testing.expectEqual(err_ptr.err_floor, err_raw);
    try std.testing.expectEqual(@as(usize, 1), top_pointer_raw - top_value_raw);
    try std.testing.expectEqual(@as(usize, 1), err_raw - top_pointer_raw);
    try std.testing.expect(!xarray_slot_view.fromRaw(top_pointer_raw).isErr());
    try std.testing.expect(xarray_slot_view.fromRaw(err_raw).isErr());
}
