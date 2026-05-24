const std = @import("std");

pub const max_errno: usize = 4095;
pub const internal_entry_mask: usize = 0x3;
pub const internal_entry_tag: usize = 0x2;
pub const sibling_max_offset: usize = 62;
pub const retry_internal_value: usize = 256;
pub const zero_internal_value: usize = 257;

pub const SlotKind = enum {
    null,
    pointer,
    sibling,
    retry,
    zero,
    err,
    internal,
};

pub const MakeSiblingError = error{
    OffsetOutOfRange,
};

pub const SlotView = struct {
    raw: usize,

    pub fn kind(self: SlotView) SlotKind {
        if (self.raw == 0) {
            return .null;
        }
        if (!isInternalEntry(self.raw)) {
            return .pointer;
        }
        if (isRetryEntry(self.raw)) {
            return .retry;
        }
        if (isZeroEntry(self.raw)) {
            return .zero;
        }
        if (isErrEntry(self.raw)) {
            return .err;
        }
        if (isSiblingEntry(self.raw)) {
            return .sibling;
        }
        return .internal;
    }

    pub fn rawValue(self: SlotView) usize {
        return self.raw;
    }

    pub fn isNull(self: SlotView) bool {
        return self.kind() == .null;
    }

    pub fn isPointer(self: SlotView) bool {
        return self.kind() == .pointer;
    }

    pub fn isSibling(self: SlotView) bool {
        return self.kind() == .sibling;
    }

    pub fn isRetry(self: SlotView) bool {
        return self.kind() == .retry;
    }

    pub fn isZero(self: SlotView) bool {
        return self.kind() == .zero;
    }

    pub fn isErr(self: SlotView) bool {
        return self.kind() == .err;
    }

    pub fn isInternal(self: SlotView) bool {
        return self.kind() == .internal;
    }

    pub fn pointerValue(self: SlotView) ?usize {
        if (!self.isPointer()) {
            return null;
        }
        return self.raw;
    }

    pub fn siblingOffset(self: SlotView) ?usize {
        if (!self.isSibling()) {
            return null;
        }
        return toInternal(self.raw);
    }

    pub fn errorCode(self: SlotView) ?isize {
        if (!self.isErr()) {
            return null;
        }
        return toErrorCode(self.raw);
    }

    pub fn internalValue(self: SlotView) ?usize {
        if (!isInternalEntry(self.raw) or self.isErr()) {
            return null;
        }
        return toInternal(self.raw);
    }
};

pub fn fromRaw(raw: usize) SlotView {
    return .{ .raw = raw };
}

pub fn nullSlot() SlotView {
    return fromRaw(0);
}

pub fn fromPointer(pointer: usize) SlotView {
    std.debug.assert(pointer != 0);
    std.debug.assert(!isInternalEntry(pointer));
    return .{ .raw = pointer };
}

pub fn fromSibling(offset: usize) MakeSiblingError!SlotView {
    if (offset > sibling_max_offset) {
        return error.OffsetOutOfRange;
    }
    return .{ .raw = makeInternal(offset) };
}

pub fn retryEntry() SlotView {
    return .{ .raw = makeInternal(retry_internal_value) };
}

pub fn zeroEntry() SlotView {
    return .{ .raw = makeInternal(zero_internal_value) };
}

pub fn fromErrorCode(code: isize) SlotView {
    std.debug.assert(code <= -1);
    std.debug.assert(code >= -@as(isize, @intCast(max_errno)));
    return .{ .raw = @bitCast((code << 2) | internal_entry_tag) };
}

pub fn makeInternal(value: usize) usize {
    return (value << 2) | internal_entry_tag;
}

pub fn isInternalEntry(raw: usize) bool {
    return (raw & internal_entry_mask) == internal_entry_tag;
}

pub fn isSiblingEntry(raw: usize) bool {
    return isInternalEntry(raw) and !isErrEntry(raw) and toInternal(raw) <= sibling_max_offset;
}

pub fn isRetryEntry(raw: usize) bool {
    return isInternalEntry(raw) and !isErrEntry(raw) and toInternal(raw) == retry_internal_value;
}

pub fn isZeroEntry(raw: usize) bool {
    return isInternalEntry(raw) and !isErrEntry(raw) and toInternal(raw) == zero_internal_value;
}

pub fn isErrEntry(raw: usize) bool {
    return isInternalEntry(raw) and @as(isize, @bitCast(raw)) < 0;
}

pub fn toInternal(raw: usize) usize {
    std.debug.assert(isInternalEntry(raw));
    return raw >> 2;
}

pub fn toErrorCode(raw: usize) isize {
    std.debug.assert(isErrEntry(raw));
    return @as(isize, @bitCast(raw)) >> 2;
}

test "sibling entries stay inside the bounded low-tag internal lane" {
    const raw = makeInternal(29);
    const slot = fromRaw(raw);

    try std.testing.expect(slot.isSibling());
    try std.testing.expect(!slot.isPointer());
    try std.testing.expect(!slot.isRetry());
    try std.testing.expect(!slot.isZero());
    try std.testing.expect(!slot.isErr());
    try std.testing.expectEqual(@as(?usize, 29), slot.siblingOffset());
    try std.testing.expectEqual(@as(?usize, 29), slot.internalValue());
}

test "retry and zero entries stay distinct from sibling and pointer lanes" {
    const retry = retryEntry();
    const zero = zeroEntry();

    try std.testing.expect(retry.isRetry());
    try std.testing.expect(!retry.isSibling());
    try std.testing.expectEqual(@as(?usize, retry_internal_value), retry.internalValue());

    try std.testing.expect(zero.isZero());
    try std.testing.expect(!zero.isRetry());
    try std.testing.expectEqual(@as(?usize, zero_internal_value), zero.internalValue());
}

test "negative internal entries decode back to errno values" {
    const slot = fromErrorCode(-22);

    try std.testing.expect(slot.isErr());
    try std.testing.expect(!slot.isPointer());
    try std.testing.expect(!slot.isSibling());
    try std.testing.expectEqual(@as(?isize, -22), slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), slot.internalValue());
}

test "ordinary pointer-like entries stay outside the internal tag family" {
    const slot = fromPointer(0x1000);

    try std.testing.expect(slot.isPointer());
    try std.testing.expect(!slot.isSibling());
    try std.testing.expect(!slot.isRetry());
    try std.testing.expect(!slot.isZero());
    try std.testing.expect(!slot.isErr());
    try std.testing.expectEqual(@as(?usize, 0x1000), slot.pointerValue());
    try std.testing.expect(!isInternalEntry(0x1000));
}
