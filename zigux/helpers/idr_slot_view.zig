const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");

pub const SlotKind = enum {
    null,
    pointer,
    invalid,
};

pub const SlotView = struct {
    raw: usize,

    pub fn kind(self: SlotView) SlotKind {
        if (self.raw == 0) {
            return .null;
        }
        if (isDirectPointerEncoding(self.raw)) {
            return .pointer;
        }
        return .invalid;
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

    pub fn isInvalid(self: SlotView) bool {
        return self.kind() == .invalid;
    }

    pub fn pointerValue(self: SlotView) ?usize {
        if (!self.isPointer()) {
            return null;
        }
        return self.raw;
    }
};

pub fn fromRaw(raw: usize) SlotView {
    return .{ .raw = raw };
}

pub fn nullSlot() SlotView {
    return fromRaw(0);
}

pub fn fromPointer(pointer: usize) SlotView {
    std.debug.assert(isDirectPointerEncoding(pointer));
    return .{ .raw = pointer };
}

pub fn isDirectPointerEncoding(raw: usize) bool {
    if (raw == 0) {
        return false;
    }
    if ((raw & 0x3) != 0) {
        return false;
    }
    if (err_ptr.isErrValue(raw)) {
        return false;
    }
    if (xa_value.isValue(raw)) {
        return false;
    }
    return true;
}

test "null stays empty and keeps the pointer decoder closed" {
    const slot = nullSlot();

    try std.testing.expect(slot.isNull());
    try std.testing.expect(!slot.isPointer());
    try std.testing.expect(!slot.isInvalid());
    try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
}

test "aligned pointer round-trips through the direct IDR slot view" {
    const raw = @as(usize, 0x1000);
    const slot = fromPointer(raw);

    try std.testing.expect(!slot.isNull());
    try std.testing.expect(slot.isPointer());
    try std.testing.expect(!slot.isInvalid());
    try std.testing.expectEqual(raw, slot.rawValue());
    try std.testing.expectEqual(@as(?usize, raw), slot.pointerValue());
}

test "xa_value entries stay invalid for the direct IDR pointer contract" {
    const raw = try xa_value.makeValue(7);
    const slot = fromRaw(raw);

    try std.testing.expect(!slot.isNull());
    try std.testing.expect(!slot.isPointer());
    try std.testing.expect(slot.isInvalid());
    try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
}

test "err_ptr encodings stay invalid for the direct IDR pointer contract" {
    const raw = err_ptr.fromErrorCode(-2);
    const slot = fromRaw(raw);

    try std.testing.expect(!slot.isNull());
    try std.testing.expect(!slot.isPointer());
    try std.testing.expect(slot.isInvalid());
    try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
}

test "low-bit tagged pointer encodings stay invalid" {
    const raw = @as(usize, 0x1001);
    const slot = fromRaw(raw);

    try std.testing.expect(!slot.isNull());
    try std.testing.expect(!slot.isPointer());
    try std.testing.expect(slot.isInvalid());
    try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
}
