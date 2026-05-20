const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn expectErrSlot(raw: usize, expected_code: isize) !void {
    const slot = xarray_slot_view.fromRaw(raw);

    try testing.expect(slot.isErr());
    try testing.expect(!slot.isNull());
    try testing.expect(!slot.isValue());
    try testing.expect(!slot.isPointer());
    try testing.expectEqual(@as(?isize, expected_code), slot.errorCode());
    try testing.expectEqual(@as(?usize, null), slot.value());
    try testing.expectEqual(@as(?usize, null), slot.pointerValue());
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
}

test "interior odd rejected-alias raws stay bracketed by adjacent even err_ptr raws" {
    const odd_codes = [_]isize{ -4093, -2047, -3 };

    for (odd_codes) |odd_code| {
        const odd_raw = err_ptr.fromErrorCode(odd_code);
        const lower_even_raw = odd_raw - 1;
        const upper_even_raw = odd_raw + 1;

        try testing.expectEqual(@as(usize, 1), odd_raw & xa_value.value_tag_mask);
        try testing.expectEqual(@as(usize, 0), lower_even_raw & xa_value.value_tag_mask);
        try testing.expectEqual(@as(usize, 0), upper_even_raw & xa_value.value_tag_mask);

        try testing.expectEqual(odd_raw, lower_even_raw + 1);
        try testing.expectEqual(upper_even_raw, odd_raw + 1);

        try expectErrSlot(lower_even_raw, odd_code - 1);
        try expectErrSlot(odd_raw, odd_code);
        try expectErrSlot(upper_even_raw, odd_code + 1);

        try testing.expect(!xa_value.isValue(lower_even_raw));
        try testing.expect(!xa_value.isValue(odd_raw));
        try testing.expect(!xa_value.isValue(upper_even_raw));
    }
}

test "interior even err_ptr raws stay bracketed by consecutive odd rejected aliases" {
    const even_codes = [_]isize{ -4094, -2048, -2 };

    for (even_codes) |even_code| {
        const even_raw = err_ptr.fromErrorCode(even_code);
        const lower_odd_raw = even_raw - 1;
        const upper_odd_raw = even_raw + 1;

        try testing.expectEqual(@as(usize, 0), even_raw & xa_value.value_tag_mask);
        try testing.expectEqual(@as(usize, 1), lower_odd_raw & xa_value.value_tag_mask);
        try testing.expectEqual(@as(usize, 1), upper_odd_raw & xa_value.value_tag_mask);

        try testing.expectEqual(even_raw, lower_odd_raw + 1);
        try testing.expectEqual(upper_odd_raw, even_raw + 1);

        try expectErrSlot(lower_odd_raw, even_code - 1);
        try expectErrSlot(even_raw, even_code);
        try expectErrSlot(upper_odd_raw, even_code + 1);

        try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(lower_odd_raw >> 1));
        try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(upper_odd_raw >> 1));
    }
}

test "err_ptr band endpoints keep the one-sided neighbor braid intact" {
    const floor_odd_raw = err_ptr.err_floor;
    const floor_upper_even_raw = floor_odd_raw + 1;
    const top_lower_even_raw = err_ptr.fromErrorCode(-2);
    const top_odd_raw = err_ptr.fromErrorCode(-1);

    try testing.expectEqual(@as(usize, 1), floor_odd_raw & xa_value.value_tag_mask);
    try testing.expectEqual(@as(usize, 0), floor_upper_even_raw & xa_value.value_tag_mask);
    try testing.expectEqual(@as(usize, 0), top_lower_even_raw & xa_value.value_tag_mask);
    try testing.expectEqual(@as(usize, 1), top_odd_raw & xa_value.value_tag_mask);

    try expectErrSlot(floor_odd_raw, -4095);
    try expectErrSlot(floor_upper_even_raw, -4094);
    try expectErrSlot(top_lower_even_raw, -2);
    try expectErrSlot(top_odd_raw, -1);

    try testing.expectEqual(floor_odd_raw + 1, floor_upper_even_raw);
    try testing.expectEqual(top_lower_even_raw + 1, top_odd_raw);
    try testing.expectEqual(std.math.maxInt(usize), top_odd_raw);
    try testing.expect(!xa_value.isValue(floor_upper_even_raw));
    try testing.expect(!xa_value.isValue(top_lower_even_raw));
}
