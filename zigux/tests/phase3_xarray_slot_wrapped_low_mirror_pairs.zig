const std = @import("std");
const testing = std.testing;

const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn wrappedLowSourceBase() usize {
    return @as(usize, 1) << (@bitSizeOf(usize) - 1);
}

fn wrappedRawForRejectedSource(source: usize) usize {
    return (source *% 2) +% xa_value.value_tag_mask;
}

test "wrapped-low rejected sources mirror accepted low constructors exactly" {
    const base = wrappedLowSourceBase();

    inline for (0..5) |offset| {
        const source = base + offset;
        const mirrored = try xarray_slot_view.fromValue(offset);
        const wrapped_raw = wrappedRawForRejectedSource(source);
        const wrapped_slot = xarray_slot_view.fromRaw(wrapped_raw);

        try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(source));
        try testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(source));
        try testing.expectEqual(mirrored.rawValue(), wrapped_raw);
        try testing.expectEqual(mirrored.rawValue(), wrapped_slot.rawValue());
        try testing.expectEqual(mirrored.kind(), wrapped_slot.kind());
        try testing.expectEqual(mirrored.value(), wrapped_slot.value());
        try testing.expectEqual(@as(?isize, null), wrapped_slot.errorCode());
        try testing.expectEqual(@as(?usize, null), wrapped_slot.pointerValue());
        try testing.expect(wrapped_slot.isValue());
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(wrapped_raw));
    }
}

test "wrapped-low mirror raws stay on the low odd ladder and decode as their offsets" {
    const base = wrappedLowSourceBase();
    const expected_raws = [_]usize{ 1, 3, 5, 7, 9 };

    inline for (expected_raws, 0..) |expected_raw, offset| {
        const source = base + offset;
        const wrapped_raw = wrappedRawForRejectedSource(source);
        const wrapped_slot = xarray_slot_view.fromRaw(wrapped_raw);

        try testing.expectEqual(expected_raw, wrapped_raw);
        try testing.expectEqual(@as(usize, offset), wrapped_slot.value().?);
        if (offset != 0) {
            try testing.expectEqual(expected_raws[offset - 1] + 2, expected_raw);
        }
    }
}

test "wrapped-low source offsets advance one decoded value per two raw steps" {
    const base = wrappedLowSourceBase();

    inline for (0..4) |offset| {
        const current_source = base + offset;
        const next_source = base + offset + 1;
        const current_raw = wrappedRawForRejectedSource(current_source);
        const next_raw = wrappedRawForRejectedSource(next_source);
        const current_slot = xarray_slot_view.fromRaw(current_raw);
        const next_slot = xarray_slot_view.fromRaw(next_raw);

        try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(current_source));
        try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(next_source));
        try testing.expectEqual(current_raw + 2, next_raw);
        try testing.expectEqual(current_slot.value().? + 1, next_slot.value().?);
    }
}
