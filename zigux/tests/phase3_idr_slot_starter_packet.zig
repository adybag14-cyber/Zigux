const std = @import("std");
const testing = std.testing;

const idr_slot_view = @import("idr_slot_view");

test "idr slot view keeps null and pointer slots explicit" {
    const null_slot = idr_slot_view.nullSlot();
    const pointer_slot = idr_slot_view.fromPointer(0x1000);

    try testing.expect(null_slot.isNull());
    try testing.expect(!null_slot.isPointer());
    try testing.expectEqual(@as(?usize, null), null_slot.pointerValue());

    try testing.expect(pointer_slot.isPointer());
    try testing.expect(!pointer_slot.isSibling());
    try testing.expect(!pointer_slot.isRetry());
    try testing.expect(!pointer_slot.isZero());
    try testing.expect(!pointer_slot.isErr());
    try testing.expectEqual(@as(?usize, 0x1000), pointer_slot.pointerValue());
}

test "idr slot view keeps sibling entries in a bounded internal lane" {
    const slot = try idr_slot_view.fromSibling(29);

    try testing.expect(slot.isSibling());
    try testing.expect(!slot.isPointer());
    try testing.expect(!slot.isRetry());
    try testing.expect(!slot.isZero());
    try testing.expect(!slot.isErr());
    try testing.expectEqual(@as(?usize, 29), slot.siblingOffset());
    try testing.expectEqual(@as(?usize, 29), slot.internalValue());
}

test "idr slot view keeps retry and zero sentinels separate from sibling entries" {
    const retry = idr_slot_view.retryEntry();
    const zero = idr_slot_view.zeroEntry();

    try testing.expect(retry.isRetry());
    try testing.expect(!retry.isSibling());
    try testing.expectEqual(@as(?usize, idr_slot_view.retry_internal_value), retry.internalValue());

    try testing.expect(zero.isZero());
    try testing.expect(!zero.isSibling());
    try testing.expectEqual(@as(?usize, idr_slot_view.zero_internal_value), zero.internalValue());
}

test "idr slot view preserves xarray-style negative internal errnos" {
    const slot = idr_slot_view.fromErrorCode(-11);

    try testing.expect(slot.isErr());
    try testing.expect(!slot.isPointer());
    try testing.expect(!slot.isSibling());
    try testing.expect(!slot.isRetry());
    try testing.expect(!slot.isZero());
    try testing.expectEqual(@as(?isize, -11), slot.errorCode());
}

test "bounded sibling constructor still rejects offsets beyond the shared xarray window" {
    try testing.expectError(
        error.OffsetOutOfRange,
        idr_slot_view.fromSibling(idr_slot_view.sibling_max_offset + 1),
    );
}
