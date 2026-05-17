const std = @import("std");
const testing = std.testing;

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

pub fn isTaggedInternalEntry(raw: usize) bool {
    return err_ptr.isErrValue(raw) or xa_value.isValue(raw);
}

test "xarray slot view keeps null slots explicit" {
    const slot = fromRaw(0);

    try testing.expect(slot.isNull());
    try testing.expect(!slot.isValue());
    try testing.expect(!slot.isErr());
    try testing.expect(!slot.isPointer());
    try testing.expectEqual(@as(?usize, null), slot.value());
    try testing.expectEqual(@as(?isize, null), slot.errorCode());
    try testing.expectEqual(@as(?usize, null), slot.pointerValue());
}

test "xarray slot view keeps xa_value entries out of the err_ptr band" {
    const raw = try xa_value.makeValue(29);
    const slot = fromRaw(raw);

    try testing.expect(slot.isValue());
    try testing.expect(!slot.isErr());
    try testing.expect(!slot.isPointer());
    try testing.expectEqual(@as(?usize, 29), slot.value());
    try testing.expectEqual(@as(?isize, null), slot.errorCode());
    try testing.expect(xa_value.isValue(raw));
    try testing.expect(isTaggedInternalEntry(raw));
}

test "xarray slot view preserves err_ptr encodings as tagged error entries" {
    const raw = err_ptr.fromErrorCode(-22);
    const slot = fromRaw(raw);

    try testing.expect(slot.isErr());
    try testing.expect(!slot.isValue());
    try testing.expect(!slot.isPointer());
    try testing.expectEqual(@as(?isize, -22), slot.errorCode());
    try testing.expectEqual(@as(?usize, null), slot.pointerValue());
    try testing.expect(isTaggedInternalEntry(raw));
}

test "xarray slot view keeps ordinary pointer-like slots separate from tagged entries" {
    const raw: usize = 0x1000;
    const slot = fromRaw(raw);

    try testing.expect(slot.isPointer());
    try testing.expect(!slot.isValue());
    try testing.expect(!slot.isErr());
    try testing.expectEqual(@as(?usize, raw), slot.pointerValue());
    try testing.expect(!isTaggedInternalEntry(raw));
}

test "safe inline limit still lands in the tagged-value lane" {
    const raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const slot = fromRaw(raw);

    try testing.expect(slot.isValue());
    try testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), slot.value());
    try testing.expect(raw < err_ptr.err_floor);
}

test "inline zero stays tagged without looking like a null slot" {
    const raw = try xa_value.makeValue(0);
    const slot = fromRaw(raw);

    try testing.expect(!slot.isNull());
    try testing.expect(slot.isValue());
    try testing.expect(!slot.isErr());
    try testing.expect(!slot.isPointer());
    try testing.expectEqual(@as(?usize, 0), slot.value());
    try testing.expect(isTaggedInternalEntry(raw));
}

test "gap before err floor still classifies as pointer-like" {
    const raw = err_ptr.err_floor - 1;
    const slot = fromRaw(raw);

    try testing.expect(!slot.isNull());
    try testing.expect(!slot.isValue());
    try testing.expect(!slot.isErr());
    try testing.expect(slot.isPointer());
    try testing.expectEqual(@as(?usize, raw), slot.pointerValue());
    try testing.expect(!isTaggedInternalEntry(raw));
}

test "top err_ptr encoding stays tagged and never falls back to pointer-like" {
    const raw = err_ptr.fromErrorCode(-1);
    const slot = fromRaw(raw);

    try testing.expect(!slot.isNull());
    try testing.expect(!slot.isValue());
    try testing.expect(slot.isErr());
    try testing.expect(!slot.isPointer());
    try testing.expectEqual(@as(?isize, -1), slot.errorCode());
    try testing.expect(isTaggedInternalEntry(raw));
}
