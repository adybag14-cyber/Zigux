const std = @import("std");
const testing = std.testing;

const ida_slot_view = @import("ida_slot_view");

fn bitMask(bit_index: usize) usize {
    return @as(usize, 1) << @intCast(bit_index);
}

test "ida slot view keeps empty slots explicit" {
    const slot = ida_slot_view.emptySlot();

    try testing.expect(slot.isEmpty());
    try testing.expect(!slot.isInlineBits());
    try testing.expect(!slot.isBitmapPointer());
    try testing.expectEqual(@as(?usize, null), slot.inlineMask());
}

test "ida slot view keeps inline mask lanes bounded to the helper-local packet" {
    const slot = try ida_slot_view.fromInlineMask(bitMask(0) | bitMask(5) | bitMask(11));

    try testing.expect(slot.isInlineBits());
    try testing.expectEqual(@as(?usize, 3), slot.inlineBitCount());
    try testing.expectEqual(@as(?usize, 0), slot.firstInlineBit());
    try testing.expectEqual(@as(?usize, 5), slot.nextInlineBit(1));
    try testing.expectEqual(@as(?usize, 11), slot.nextInlineBit(6));
    try testing.expectEqual(@as(?bool, true), slot.containsInlineBit(11));
    try testing.expectEqual(@as(?bool, false), slot.containsInlineBit(10));
}

test "ida slot view keeps bitmap pointers distinct from inline bit lanes" {
    const slot = ida_slot_view.fromBitmapPointer(0x2000);

    try testing.expect(slot.isBitmapPointer());
    try testing.expect(!slot.isInlineBits());
    try testing.expectEqual(@as(?usize, 0x2000), slot.bitmapPointer());
}

test "ida slot view keeps impossible err-tagged raws visible as defensive drift" {
    const slot = ida_slot_view.fromUnexpectedError(-1);

    try testing.expect(slot.isUnexpectedErr());
    try testing.expect(!slot.isInlineBits());
    try testing.expect(!slot.isBitmapPointer());
    try testing.expectEqual(@as(?isize, -1), slot.unexpectedErrorCode());
}

test "ida inline constructor rejects empty masks and the pointer tag bit" {
    try testing.expectError(error.EmptyInlineMask, ida_slot_view.fromInlineMask(0));
    try testing.expectError(
        error.InlineMaskWouldUsePointerTagBit,
        ida_slot_view.fromInlineMask(@as(usize, 1) << @intCast(ida_slot_view.inline_bit_capacity)),
    );
}
