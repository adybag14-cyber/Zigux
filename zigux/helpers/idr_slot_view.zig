const std = @import("std");
const xarray_slot_view = @import("xarray_slot_view");
const xa_value = @import("xa_value");

pub const SlotKind = enum {
    empty,
    internal_value,
    err,
    pointer,
};

pub const SlotView = struct {
    slot: xarray_slot_view.SlotView,

    pub fn kind(self: SlotView) SlotKind {
        return switch (self.slot.kind()) {
            .null => .empty,
            .value => .internal_value,
            .err => .err,
            .pointer => .pointer,
        };
    }

    pub fn rawValue(self: SlotView) usize {
        return self.slot.rawValue();
    }

    pub fn isEmpty(self: SlotView) bool {
        return self.kind() == .empty;
    }

    pub fn isInternalValue(self: SlotView) bool {
        return self.kind() == .internal_value;
    }

    pub fn isErr(self: SlotView) bool {
        return self.kind() == .err;
    }

    pub fn isPointer(self: SlotView) bool {
        return self.kind() == .pointer;
    }

    pub fn internalValue(self: SlotView) ?usize {
        if (!self.isInternalValue()) {
            return null;
        }
        return self.slot.value();
    }

    pub fn errorCode(self: SlotView) ?isize {
        return self.slot.errorCode();
    }

    pub fn pointerValue(self: SlotView) ?usize {
        return self.slot.pointerValue();
    }
};

pub fn fromRaw(raw: usize) SlotView {
    return .{ .slot = xarray_slot_view.fromRaw(raw) };
}

pub fn emptySlot() SlotView {
    return fromRaw(0);
}

pub fn fromInternalValue(value: usize) xa_value.MakeValueError!SlotView {
    return .{ .slot = try xarray_slot_view.fromValue(value) };
}

pub fn fromErrorCode(code: isize) SlotView {
    return .{ .slot = xarray_slot_view.fromErrorCode(code) };
}

pub fn fromPointer(pointer: usize) SlotView {
    return .{ .slot = xarray_slot_view.fromPointer(pointer) };
}

pub fn isTaggedInternalEntry(raw: usize) bool {
    return xarray_slot_view.isTaggedInternalEntry(raw);
}

test "empty slots stay distinct from pointer and internal lanes" {
    const slot = emptySlot();

    try std.testing.expect(slot.isEmpty());
    try std.testing.expect(!slot.isInternalValue());
    try std.testing.expect(!slot.isErr());
    try std.testing.expect(!slot.isPointer());
    try std.testing.expectEqual(@as(?usize, null), slot.internalValue());
    try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
}

test "pointer lanes stay publishable through the idr slot wrapper" {
    const raw: usize = 0x1000;
    const slot = fromPointer(raw);

    try std.testing.expect(slot.isPointer());
    try std.testing.expect(!slot.isInternalValue());
    try std.testing.expect(!slot.isErr());
    try std.testing.expectEqual(@as(?usize, raw), slot.pointerValue());
    try std.testing.expect(!isTaggedInternalEntry(raw));
}

test "xa_value-tagged entries stay internal instead of looking like mapped pointers" {
    const raw = try xarray_slot_view.fromValue(29);
    const slot = fromRaw(raw.rawValue());

    try std.testing.expect(!slot.isEmpty());
    try std.testing.expect(slot.isInternalValue());
    try std.testing.expect(!slot.isErr());
    try std.testing.expect(!slot.isPointer());
    try std.testing.expectEqual(@as(?usize, 29), slot.internalValue());
    try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
    try std.testing.expect(isTaggedInternalEntry(raw.rawValue()));
}

test "err_ptr encodings stay separated from pointer-backed idr entries" {
    const raw = xarray_slot_view.fromErrorCode(-22);
    const slot = fromRaw(raw.rawValue());

    try std.testing.expect(!slot.isEmpty());
    try std.testing.expect(!slot.isInternalValue());
    try std.testing.expect(slot.isErr());
    try std.testing.expect(!slot.isPointer());
    try std.testing.expectEqual(@as(?isize, -22), slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
    try std.testing.expect(isTaggedInternalEntry(raw.rawValue()));
}

test "internal value constructor preserves the overlap guard from xa_value" {
    try std.testing.expectError(
        error.ValueWouldOverlapErrPtr,
        fromInternalValue(xa_value.safe_inline_limit + 1),
    );
}
