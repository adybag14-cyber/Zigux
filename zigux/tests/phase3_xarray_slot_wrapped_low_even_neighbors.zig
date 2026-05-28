const std = @import("std");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn wrappedLowSourceBase() usize {
    return @as(usize, 1) << (@bitSizeOf(usize) - 1);
}

fn wrappedRawForRejectedSource(source: usize) usize {
    return (source *% 2) +% xa_value.value_tag_mask;
}

test "wrapped-low rejected sources still decode as low tagged value slots" {
    const base = wrappedLowSourceBase();
    const cases = [_]struct {
        offset: usize,
        expected_raw: usize,
    }{
        .{ .offset = 0, .expected_raw = 1 },
        .{ .offset = 1, .expected_raw = 3 },
        .{ .offset = 2, .expected_raw = 5 },
        .{ .offset = 3, .expected_raw = 7 },
    };

    try std.testing.expect(base > xa_value.safe_inline_limit);

    inline for (cases) |case| {
        const source = base + case.offset;
        const raw = wrappedRawForRejectedSource(source);
        const slot = xarray_slot_view.fromRaw(raw);

        try std.testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(source));
        try std.testing.expectEqual(case.expected_raw, raw);
        try std.testing.expect(slot.isValue());
        try std.testing.expect(!slot.isNull());
        try std.testing.expect(!slot.isErr());
        try std.testing.expect(!slot.isPointer());
        try std.testing.expectEqual(@as(?usize, case.offset), slot.value());
        try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
    }
}

test "adjacent low even raws stay null or pointer lanes beside wrapped-low values" {
    const cases = [_]struct {
        raw: usize,
        is_null: bool,
    }{
        .{ .raw = 0, .is_null = true },
        .{ .raw = 2, .is_null = false },
        .{ .raw = 4, .is_null = false },
        .{ .raw = 6, .is_null = false },
        .{ .raw = 8, .is_null = false },
    };

    inline for (cases) |case| {
        const slot = xarray_slot_view.fromRaw(case.raw);

        try std.testing.expect(!xarray_slot_view.isTaggedInternalEntry(case.raw));
        if (case.is_null) {
            try std.testing.expect(slot.isNull());
            try std.testing.expect(!slot.isPointer());
            try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
        } else {
            try std.testing.expect(!slot.isNull());
            try std.testing.expect(slot.isPointer());
            try std.testing.expectEqual(@as(?usize, case.raw), slot.pointerValue());
        }
        try std.testing.expect(!slot.isValue());
        try std.testing.expect(!slot.isErr());
        try std.testing.expectEqual(@as(?usize, null), slot.value());
        try std.testing.expectEqual(@as(?isize, null), slot.errorCode());
    }
}

test "wrapped-low tagged raws and low even neighbors alternate cleanly at the bottom edge" {
    const base = wrappedLowSourceBase();

    inline for (0..4) |offset| {
        const source = base + offset;
        const value_raw = wrappedRawForRejectedSource(source);
        const even_raw = value_raw + 1;
        const value_slot = xarray_slot_view.fromRaw(value_raw);
        const even_slot = xarray_slot_view.fromRaw(even_raw);

        try std.testing.expect(value_slot.isValue());
        try std.testing.expect(!even_slot.isValue());
        try std.testing.expect(!even_slot.isErr());
        if (even_raw == 0) {
            try std.testing.expect(even_slot.isNull());
        } else {
            try std.testing.expect(even_slot.isPointer());
        }
    }
}
