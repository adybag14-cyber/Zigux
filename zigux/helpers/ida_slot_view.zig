const std = @import("std");
const xarray_slot_view = @import("xarray_slot_view");
const xa_value = @import("xa_value");

pub const inline_bit_capacity: usize = @bitSizeOf(usize) - 1;

pub const SlotKind = enum {
    empty,
    inline_bits,
    bitmap_pointer,
    unexpected_err,
};

pub const MakeInlineMaskError = error{
    EmptyInlineMask,
    InlineMaskWouldUsePointerTagBit,
    InlineMaskWouldOverlapErrPtr,
};

pub const SlotView = struct {
    slot: xarray_slot_view.SlotView,

    pub fn kind(self: SlotView) SlotKind {
        return switch (self.slot.kind()) {
            .null => .empty,
            .value => .inline_bits,
            .pointer => .bitmap_pointer,
            .err => .unexpected_err,
        };
    }

    pub fn rawValue(self: SlotView) usize {
        return self.slot.rawValue();
    }

    pub fn isEmpty(self: SlotView) bool {
        return self.kind() == .empty;
    }

    pub fn isInlineBits(self: SlotView) bool {
        return self.kind() == .inline_bits;
    }

    pub fn isBitmapPointer(self: SlotView) bool {
        return self.kind() == .bitmap_pointer;
    }

    pub fn isUnexpectedErr(self: SlotView) bool {
        return self.kind() == .unexpected_err;
    }

    pub fn inlineMask(self: SlotView) ?usize {
        return self.slot.value();
    }

    pub fn unexpectedErrorCode(self: SlotView) ?isize {
        return self.slot.errorCode();
    }

    pub fn bitmapPointer(self: SlotView) ?usize {
        return self.slot.pointerValue();
    }

    pub fn inlineBitCount(self: SlotView) ?usize {
        const mask = self.inlineMask() orelse return null;
        return @popCount(mask);
    }

    pub fn containsInlineBit(self: SlotView, bit_index: usize) ?bool {
        const mask = self.inlineMask() orelse return null;
        if (bit_index >= inline_bit_capacity) return false;
        return (mask & bitMask(bit_index)) != 0;
    }

    pub fn firstInlineBit(self: SlotView) ?usize {
        const mask = self.inlineMask() orelse return null;
        if (mask == 0) return null;
        return @ctz(mask);
    }

    pub fn nextInlineBit(self: SlotView, start_bit: usize) ?usize {
        const mask = self.inlineMask() orelse return null;
        if (start_bit >= inline_bit_capacity) return null;

        const remaining = mask & startMask(start_bit);
        if (remaining == 0) return null;
        return @ctz(remaining);
    }
};

fn bitMask(bit_index: usize) usize {
    return @as(usize, 1) << @intCast(bit_index);
}

fn startMask(bit_index: usize) usize {
    if (bit_index == 0) return std.math.maxInt(usize);
    return (~@as(usize, 0)) << @as(std.math.Log2Int(usize), @intCast(bit_index));
}

fn pointerTagBitClear(mask: usize) bool {
    return (mask >> inline_bit_capacity) == 0;
}

pub fn fromRaw(raw: usize) SlotView {
    return .{ .slot = xarray_slot_view.fromRaw(raw) };
}

pub fn emptySlot() SlotView {
    return fromRaw(0);
}

pub fn fromInlineMask(mask: usize) MakeInlineMaskError!SlotView {
    if (mask == 0) {
        return error.EmptyInlineMask;
    }
    if (!pointerTagBitClear(mask)) {
        return error.InlineMaskWouldUsePointerTagBit;
    }

    const raw = xa_value.makeValue(mask) catch {
        return error.InlineMaskWouldOverlapErrPtr;
    };
    return fromRaw(raw);
}

pub fn fromBitmapPointer(pointer: usize) SlotView {
    return .{ .slot = xarray_slot_view.fromPointer(pointer) };
}

pub fn fromUnexpectedError(code: isize) SlotView {
    return .{ .slot = xarray_slot_view.fromErrorCode(code) };
}

test "ida slot view keeps empty entries distinct from inline and pointer lanes" {
    const slot = emptySlot();

    try std.testing.expect(slot.isEmpty());
    try std.testing.expect(!slot.isInlineBits());
    try std.testing.expect(!slot.isBitmapPointer());
    try std.testing.expect(!slot.isUnexpectedErr());
    try std.testing.expectEqual(@as(?usize, null), slot.inlineMask());
    try std.testing.expectEqual(@as(?usize, null), slot.bitmapPointer());
}

test "ida slot view keeps inline masks explicit and walkable" {
    const slot = try fromInlineMask(bitMask(0) | bitMask(4) | bitMask(9));

    try std.testing.expect(slot.isInlineBits());
    try std.testing.expectEqual(@as(?usize, 3), slot.inlineBitCount());
    try std.testing.expectEqual(@as(?usize, 0), slot.firstInlineBit());
    try std.testing.expectEqual(@as(?usize, 4), slot.nextInlineBit(1));
    try std.testing.expectEqual(@as(?usize, 9), slot.nextInlineBit(5));
    try std.testing.expectEqual(@as(?bool, true), slot.containsInlineBit(4));
    try std.testing.expectEqual(@as(?bool, false), slot.containsInlineBit(7));
}

test "ida slot view keeps bitmap pointers distinct from tagged inline values" {
    const raw: usize = 0x4000;
    const slot = fromBitmapPointer(raw);

    try std.testing.expect(slot.isBitmapPointer());
    try std.testing.expect(!slot.isInlineBits());
    try std.testing.expectEqual(@as(?usize, raw), slot.bitmapPointer());
    try std.testing.expectEqual(@as(?usize, null), slot.inlineMask());
}

test "ida slot view keeps unexpected err_ptr encodings out of valid ida lanes" {
    const slot = fromUnexpectedError(-22);

    try std.testing.expect(slot.isUnexpectedErr());
    try std.testing.expect(!slot.isInlineBits());
    try std.testing.expect(!slot.isBitmapPointer());
    try std.testing.expectEqual(@as(?isize, -22), slot.unexpectedErrorCode());
}

test "ida inline constructor rejects empty and pointer-tag-overlapping masks" {
    try std.testing.expectError(error.EmptyInlineMask, fromInlineMask(0));
    try std.testing.expectError(
        error.InlineMaskWouldUsePointerTagBit,
        fromInlineMask(@as(usize, 1) << @intCast(inline_bit_capacity)),
    );
}
