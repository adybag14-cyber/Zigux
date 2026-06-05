const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");

pub const SlotKind = enum {
    null,
    value,
    err,
    pointer,
};

pub const SlotView = struct {
    raw: usize,

    pub fn kind(self: SlotView) SlotKind {
        if (self.raw == 0) {
            return .null;
        }
        if (err_ptr.isErrValue(self.raw)) {
            return .err;
        }
        if (xa_value.isValue(self.raw)) {
            return .value;
        }
        return .pointer;
    }

    pub fn rawValue(self: SlotView) usize {
        return self.raw;
    }

    pub fn isNull(self: SlotView) bool {
        return self.kind() == .null;
    }

    pub fn isValue(self: SlotView) bool {
        return self.kind() == .value;
    }

    pub fn isErr(self: SlotView) bool {
        return self.kind() == .err;
    }

    pub fn isPointer(self: SlotView) bool {
        return self.kind() == .pointer;
    }

    pub fn isTaggedEntry(self: SlotView) bool {
        return isTaggedInternalEntry(self.raw);
    }

    pub fn value(self: SlotView) ?usize {
        if (!self.isValue()) {
            return null;
        }
        return xa_value.toValue(self.raw);
    }

    pub fn errorCode(self: SlotView) ?isize {
        if (!self.isErr()) {
            return null;
        }
        return err_ptr.toErrorCode(self.raw);
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

pub fn fromValue(value: usize) xa_value.MakeValueError!SlotView {
    return .{ .raw = try xa_value.makeValue(value) };
}

pub fn fromErrorCode(code: isize) SlotView {
    return .{ .raw = err_ptr.fromErrorCode(code) };
}

pub fn fromPointer(pointer: usize) SlotView {
    std.debug.assert(pointer != 0);
    std.debug.assert(!isTaggedInternalEntry(pointer));
    return .{ .raw = pointer };
}

pub fn isTaggedInternalEntry(raw: usize) bool {
    return err_ptr.isErrValue(raw) or xa_value.isValue(raw);
}

test "err floor stays in the err lane even with the xa_value low tag bit set" {
    const slot = fromRaw(err_ptr.err_floor);

    try std.testing.expect(!slot.isNull());
    try std.testing.expect(!slot.isValue());
    try std.testing.expect(slot.isErr());
    try std.testing.expect(!slot.isPointer());
    try std.testing.expectEqual(@as(?isize, -4095), slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), slot.value());
    try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
    try std.testing.expect(isTaggedInternalEntry(err_ptr.err_floor));
}

test "gap below err floor stays pointer-like and leaves tagged decoders closed" {
    const raw = err_ptr.err_floor - 1;
    const slot = fromRaw(raw);

    try std.testing.expect(!slot.isNull());
    try std.testing.expect(!slot.isValue());
    try std.testing.expect(!slot.isErr());
    try std.testing.expect(slot.isPointer());
    try std.testing.expectEqual(@as(?isize, null), slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), slot.value());
    try std.testing.expectEqual(@as(?usize, raw), slot.pointerValue());
    try std.testing.expect(!isTaggedInternalEntry(raw));
}

test "inline zero stays a tagged value and keeps other decoders closed" {
    const raw = try xa_value.makeValue(0);
    const slot = fromRaw(raw);

    try std.testing.expect(!slot.isNull());
    try std.testing.expect(slot.isValue());
    try std.testing.expect(!slot.isErr());
    try std.testing.expect(!slot.isPointer());
    try std.testing.expectEqual(@as(?usize, 0), slot.value());
    try std.testing.expectEqual(@as(?isize, null), slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
    try std.testing.expect(isTaggedInternalEntry(raw));
}

test "top err_ptr encoding stays tagged and keeps value and pointer decoders closed" {
    const raw = err_ptr.fromErrorCode(-1);
    const slot = fromRaw(raw);

    try std.testing.expect(!slot.isNull());
    try std.testing.expect(!slot.isValue());
    try std.testing.expect(slot.isErr());
    try std.testing.expect(!slot.isPointer());
    try std.testing.expectEqual(@as(?usize, null), slot.value());
    try std.testing.expectEqual(@as(?isize, -1), slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
    try std.testing.expect(isTaggedInternalEntry(raw));
}

test "constructor helpers keep each xarray slot lane explicit" {
    const null_slot = nullSlot();
    const value_slot = try fromValue(29);
    const err_slot = fromErrorCode(-22);
    const pointer_slot = fromPointer(0x1000);

    try std.testing.expectEqual(SlotKind.null, null_slot.kind());
    try std.testing.expectEqual(@as(usize, 0), null_slot.rawValue());

    try std.testing.expectEqual(SlotKind.value, value_slot.kind());
    try std.testing.expectEqual(try xa_value.makeValue(29), value_slot.rawValue());
    try std.testing.expectEqual(@as(?usize, 29), value_slot.value());

    try std.testing.expectEqual(SlotKind.err, err_slot.kind());
    try std.testing.expectEqual(err_ptr.fromErrorCode(-22), err_slot.rawValue());
    try std.testing.expectEqual(@as(?isize, -22), err_slot.errorCode());

    try std.testing.expectEqual(SlotKind.pointer, pointer_slot.kind());
    try std.testing.expectEqual(@as(usize, 0x1000), pointer_slot.rawValue());
    try std.testing.expectEqual(@as(?usize, 0x1000), pointer_slot.pointerValue());
}

test "value constructor still rejects entries that would overlap err_ptr space" {
    try std.testing.expectError(
        error.ValueWouldOverlapErrPtr,
        fromValue(xa_value.safe_inline_limit + 1),
    );
}

test "slot-level tagged entry query matches raw xarray helper state" {
    const null_slot = nullSlot();
    const value_slot = try fromValue(29);
    const pointer_slot = fromRaw(err_ptr.err_floor - 1);
    const err_floor_slot = fromRaw(err_ptr.err_floor);
    const top_err_slot = fromErrorCode(-1);

    try std.testing.expectEqual(isTaggedInternalEntry(null_slot.rawValue()), null_slot.isTaggedEntry());
    try std.testing.expectEqual(isTaggedInternalEntry(value_slot.rawValue()), value_slot.isTaggedEntry());
    try std.testing.expectEqual(isTaggedInternalEntry(pointer_slot.rawValue()), pointer_slot.isTaggedEntry());
    try std.testing.expectEqual(isTaggedInternalEntry(err_floor_slot.rawValue()), err_floor_slot.isTaggedEntry());
    try std.testing.expectEqual(isTaggedInternalEntry(top_err_slot.rawValue()), top_err_slot.isTaggedEntry());

    try std.testing.expect(!null_slot.isTaggedEntry());
    try std.testing.expect(value_slot.isTaggedEntry());
    try std.testing.expect(!pointer_slot.isTaggedEntry());
    try std.testing.expect(err_floor_slot.isTaggedEntry());
    try std.testing.expect(top_err_slot.isTaggedEntry());
}

test "rejected value aliases keep err_ptr precedence and signed payloads" {
    const rejected_values = [_]usize{
        xa_value.safe_inline_limit + 1,
        xa_value.safe_inline_limit + 2,
        xa_value.safe_inline_limit + 127,
        (std.math.maxInt(usize) >> 1),
    };

    for (rejected_values) |value| {
        const raw = (value << 1) | xa_value.value_tag_mask;
        const slot = fromRaw(raw);
        const expected_code = err_ptr.toErrorCode(raw);

        try std.testing.expect(!xa_value.canRepresent(value));
        try std.testing.expect((raw & xa_value.value_tag_mask) == xa_value.value_tag_mask);
        try std.testing.expect(err_ptr.isErrValue(raw));
        try std.testing.expect(!xa_value.isValue(raw));
        try std.testing.expectEqual(SlotKind.err, slot.kind());
        try std.testing.expect(slot.isTaggedEntry());
        try std.testing.expectEqual(raw, slot.rawValue());
        try std.testing.expectEqual(@as(?isize, expected_code), slot.errorCode());
        try std.testing.expectEqual(@as(?usize, null), slot.value());
        try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
    }
}
