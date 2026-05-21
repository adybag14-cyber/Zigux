const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn expectTaggedOddNeighborPair(odd_code: isize) !void {
    const odd_raw = err_ptr.fromErrorCode(odd_code);
    const even_raw = err_ptr.fromErrorCode(odd_code + 1);
    const odd_slot = xarray_slot_view.fromRaw(odd_raw);
    const even_slot = xarray_slot_view.fromRaw(even_raw);
    const rejected_payload = odd_raw >> 1;

    try testing.expect((odd_raw & xa_value.value_tag_mask) == xa_value.value_tag_mask);
    try testing.expect((even_raw & xa_value.value_tag_mask) == 0);
    try testing.expectEqual(odd_raw + 1, even_raw);

    try testing.expect(odd_slot.isErr());
    try testing.expect(even_slot.isErr());
    try testing.expect(!odd_slot.isValue());
    try testing.expect(!even_slot.isValue());
    try testing.expect(!odd_slot.isPointer());
    try testing.expect(!even_slot.isPointer());
    try testing.expectEqual(@as(?isize, odd_code), odd_slot.errorCode());
    try testing.expectEqual(@as(?isize, odd_code + 1), even_slot.errorCode());
    try testing.expectEqual(@as(?usize, null), odd_slot.value());
    try testing.expectEqual(@as(?usize, null), even_slot.value());
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(odd_raw));
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(even_raw));

    try testing.expectEqual(odd_raw, xarray_slot_view.fromErrorCode(odd_code).rawValue());
    try testing.expectEqual(even_raw, xarray_slot_view.fromErrorCode(odd_code + 1).rawValue());
    try testing.expectEqual(odd_raw, (rejected_payload << 1) | xa_value.value_tag_mask);
    try testing.expect(!xa_value.canRepresent(rejected_payload));
    try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(rejected_payload));
}

test "representative tagged odd err_ptr raws stay adjacent to even err neighbors" {
    const odd_codes = [_]isize{ -4095, -2049, -3 };

    for (odd_codes) |odd_code| {
        try expectTaggedOddNeighborPair(odd_code);
    }
}

test "top tagged odd err_ptr raw still rebuilds the rejected xa_value payload" {
    const top_raw = err_ptr.fromErrorCode(-1);
    const top_slot = xarray_slot_view.fromRaw(top_raw);
    const neighbor_raw = err_ptr.fromErrorCode(-2);
    const rejected_payload = top_raw >> 1;

    try testing.expect((top_raw & xa_value.value_tag_mask) == xa_value.value_tag_mask);
    try testing.expectEqual(neighbor_raw + 1, top_raw);
    try testing.expect(top_slot.isErr());
    try testing.expect(!top_slot.isValue());
    try testing.expect(!top_slot.isPointer());
    try testing.expectEqual(@as(?isize, -1), top_slot.errorCode());
    try testing.expectEqual(@as(?usize, null), top_slot.value());
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(top_raw));

    try testing.expectEqual(top_raw, xarray_slot_view.fromErrorCode(-1).rawValue());
    try testing.expectEqual(top_raw, (rejected_payload << 1) | xa_value.value_tag_mask);
    try testing.expect(!xa_value.canRepresent(rejected_payload));
    try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(rejected_payload));
}
