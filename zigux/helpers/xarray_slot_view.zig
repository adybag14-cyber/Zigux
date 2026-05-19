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

test "cutoff boundary keeps value, pointer-like gap, then err in order" {
    const value_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const gap_raw = err_ptr.err_floor - 1;
    const err_raw = err_ptr.err_floor;

    const value_slot = fromRaw(value_raw);
    const gap_slot = fromRaw(gap_raw);
    const err_slot = fromRaw(err_raw);

    try std.testing.expectEqual(err_ptr.err_floor - 2, value_raw);
    try std.testing.expectEqual(value_raw + 1, gap_raw);
    try std.testing.expectEqual(gap_raw + 1, err_raw);

    try std.testing.expect(value_slot.isValue());
    try std.testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), value_slot.value());
    try std.testing.expectEqual(@as(?isize, null), value_slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), value_slot.pointerValue());

    try std.testing.expect(gap_slot.isPointer());
    try std.testing.expectEqual(@as(?usize, gap_raw), gap_slot.pointerValue());
    try std.testing.expectEqual(@as(?usize, null), gap_slot.value());
    try std.testing.expectEqual(@as(?isize, null), gap_slot.errorCode());

    try std.testing.expect(err_slot.isErr());
    try std.testing.expectEqual(@as(?isize, -4095), err_slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), err_slot.value());
    try std.testing.expectEqual(@as(?usize, null), err_slot.pointerValue());
}

test "highest two tagged values stay packed below the final pointer gap" {
    const next_value_slot = try fromValue(xa_value.safe_inline_limit - 1);
    const top_value_slot = try fromValue(xa_value.safe_inline_limit);
    const gap_slot = fromPointer(err_ptr.err_floor - 1);
    const err_slot = fromErrorCode(-4095);

    const decoded_next = fromRaw(next_value_slot.rawValue());
    const decoded_top = fromRaw(top_value_slot.rawValue());
    const rebuilt_next = try fromValue(decoded_next.value().?);
    const rebuilt_top = try fromValue(decoded_top.value().?);

    try std.testing.expectEqual(err_ptr.err_floor - 4, next_value_slot.rawValue());
    try std.testing.expectEqual(next_value_slot.rawValue() + 2, top_value_slot.rawValue());
    try std.testing.expectEqual(top_value_slot.rawValue() + 1, gap_slot.rawValue());
    try std.testing.expectEqual(gap_slot.rawValue() + 1, err_slot.rawValue());

    try std.testing.expectEqual(SlotKind.value, decoded_next.kind());
    try std.testing.expectEqual(@as(?usize, xa_value.safe_inline_limit - 1), decoded_next.value());
    try std.testing.expectEqual(@as(?isize, null), decoded_next.errorCode());
    try std.testing.expectEqual(@as(?usize, null), decoded_next.pointerValue());
    try std.testing.expect(isTaggedInternalEntry(decoded_next.rawValue()));

    try std.testing.expectEqual(SlotKind.value, decoded_top.kind());
    try std.testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), decoded_top.value());
    try std.testing.expectEqual(@as(?isize, null), decoded_top.errorCode());
    try std.testing.expectEqual(@as(?usize, null), decoded_top.pointerValue());
    try std.testing.expect(isTaggedInternalEntry(decoded_top.rawValue()));

    try std.testing.expectEqual(decoded_next.rawValue(), rebuilt_next.rawValue());
    try std.testing.expectEqual(decoded_top.rawValue(), rebuilt_top.rawValue());
}

test "constructor helpers keep the cutoff boundary lanes distinct" {
    const value_slot = try fromValue(xa_value.safe_inline_limit);
    const gap_slot = fromPointer(err_ptr.err_floor - 1);
    const err_slot = fromErrorCode(-4095);

    try std.testing.expectEqual(err_ptr.err_floor - 2, value_slot.rawValue());
    try std.testing.expectEqual(value_slot.rawValue() + 1, gap_slot.rawValue());
    try std.testing.expectEqual(gap_slot.rawValue() + 1, err_slot.rawValue());

    try std.testing.expectEqual(SlotKind.value, value_slot.kind());
    try std.testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), value_slot.value());
    try std.testing.expectEqual(@as(?isize, null), value_slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), value_slot.pointerValue());

    try std.testing.expectEqual(SlotKind.pointer, gap_slot.kind());
    try std.testing.expectEqual(@as(?usize, err_ptr.err_floor - 1), gap_slot.pointerValue());
    try std.testing.expectEqual(@as(?usize, null), gap_slot.value());
    try std.testing.expectEqual(@as(?isize, null), gap_slot.errorCode());
    try std.testing.expect(!isTaggedInternalEntry(gap_slot.rawValue()));

    try std.testing.expectEqual(SlotKind.err, err_slot.kind());
    try std.testing.expectEqual(@as(?isize, -4095), err_slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), err_slot.value());
    try std.testing.expectEqual(@as(?usize, null), err_slot.pointerValue());
    try std.testing.expect(isTaggedInternalEntry(err_slot.rawValue()));
}

test "low boundary keeps null, inline zero, then pointer-like in order" {
    const null_raw: usize = 0;
    const value_raw = try xa_value.makeValue(0);
    const pointer_raw = value_raw + 1;

    const null_slot = fromRaw(null_raw);
    const value_slot = fromRaw(value_raw);
    const pointer_slot = fromRaw(pointer_raw);

    try std.testing.expectEqual(@as(usize, 1), value_raw);
    try std.testing.expectEqual(null_raw + 1, value_raw);
    try std.testing.expectEqual(value_raw + 1, pointer_raw);

    try std.testing.expect(null_slot.isNull());
    try std.testing.expectEqual(@as(?usize, null), null_slot.value());
    try std.testing.expectEqual(@as(?isize, null), null_slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), null_slot.pointerValue());

    try std.testing.expect(value_slot.isValue());
    try std.testing.expectEqual(@as(?usize, 0), value_slot.value());
    try std.testing.expectEqual(@as(?isize, null), value_slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), value_slot.pointerValue());
    try std.testing.expect(isTaggedInternalEntry(value_raw));

    try std.testing.expect(pointer_slot.isPointer());
    try std.testing.expectEqual(@as(?usize, pointer_raw), pointer_slot.pointerValue());
    try std.testing.expectEqual(@as(?usize, null), pointer_slot.value());
    try std.testing.expectEqual(@as(?isize, null), pointer_slot.errorCode());
    try std.testing.expect(!isTaggedInternalEntry(pointer_raw));
}

test "low-end raw cadence keeps alternating value tags and pointer gaps" {
    const raw_cases = [_]struct {
        raw: usize,
        kind: SlotKind,
        value: ?usize,
        pointer: ?usize,
    }{
        .{ .raw = 0, .kind = .null, .value = null, .pointer = null },
        .{ .raw = try xa_value.makeValue(0), .kind = .value, .value = 0, .pointer = null },
        .{ .raw = 2, .kind = .pointer, .value = null, .pointer = 2 },
        .{ .raw = try xa_value.makeValue(1), .kind = .value, .value = 1, .pointer = null },
        .{ .raw = 4, .kind = .pointer, .value = null, .pointer = 4 },
        .{ .raw = try xa_value.makeValue(2), .kind = .value, .value = 2, .pointer = null },
    };

    for (raw_cases, 0..) |case, index| {
        const slot = fromRaw(case.raw);

        try std.testing.expectEqual(case.kind, slot.kind());
        try std.testing.expectEqual(case.value, slot.value());
        try std.testing.expectEqual(@as(?isize, null), slot.errorCode());
        try std.testing.expectEqual(case.pointer, slot.pointerValue());
        try std.testing.expectEqual(case.kind == .value, isTaggedInternalEntry(case.raw));

        if (index > 0) {
            try std.testing.expectEqual(raw_cases[index - 1].raw + 1, case.raw);
        }
    }

    const first_positive_value = try fromValue(1);
    const second_pointer_gap = fromPointer(4);
    const second_positive_value = try fromValue(2);

    try std.testing.expectEqual(@as(usize, 3), first_positive_value.rawValue());
    try std.testing.expectEqual(@as(usize, 4), second_pointer_gap.rawValue());
    try std.testing.expectEqual(@as(usize, 5), second_positive_value.rawValue());
    try std.testing.expectEqual(@as(?usize, 1), first_positive_value.value());
    try std.testing.expectEqual(@as(?usize, 4), second_pointer_gap.pointerValue());
    try std.testing.expectEqual(@as(?usize, 2), second_positive_value.value());
}

test "constructor helpers keep the low boundary lanes distinct" {
    const null_slot = nullSlot();
    const value_slot = try fromValue(0);
    const pointer_slot = fromPointer(2);

    try std.testing.expectEqual(@as(usize, 0), null_slot.rawValue());
    try std.testing.expectEqual(@as(usize, 1), value_slot.rawValue());
    try std.testing.expectEqual(@as(usize, 2), pointer_slot.rawValue());

    try std.testing.expectEqual(null_slot.rawValue() + 1, value_slot.rawValue());
    try std.testing.expectEqual(value_slot.rawValue() + 1, pointer_slot.rawValue());

    try std.testing.expectEqual(SlotKind.null, null_slot.kind());
    try std.testing.expectEqual(@as(?usize, null), null_slot.value());
    try std.testing.expectEqual(@as(?isize, null), null_slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), null_slot.pointerValue());

    try std.testing.expectEqual(SlotKind.value, value_slot.kind());
    try std.testing.expectEqual(@as(?usize, 0), value_slot.value());
    try std.testing.expectEqual(@as(?isize, null), value_slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), value_slot.pointerValue());
    try std.testing.expect(isTaggedInternalEntry(value_slot.rawValue()));

    try std.testing.expectEqual(SlotKind.pointer, pointer_slot.kind());
    try std.testing.expectEqual(@as(?usize, 2), pointer_slot.pointerValue());
    try std.testing.expectEqual(@as(?usize, null), pointer_slot.value());
    try std.testing.expectEqual(@as(?isize, null), pointer_slot.errorCode());
    try std.testing.expect(!isTaggedInternalEntry(pointer_slot.rawValue()));
}

test "constructor tagging stays aligned at both slot cutoffs" {
    const low_null = nullSlot();
    const low_value = try fromValue(0);
    const low_pointer = fromPointer(2);
    const high_value = try fromValue(xa_value.safe_inline_limit);
    const high_pointer = fromPointer(err_ptr.err_floor - 1);
    const first_err = fromErrorCode(-4095);
    const top_err = fromErrorCode(-1);

    try std.testing.expectEqual(SlotKind.null, low_null.kind());
    try std.testing.expect(!isTaggedInternalEntry(low_null.rawValue()));

    try std.testing.expectEqual(SlotKind.value, low_value.kind());
    try std.testing.expect(isTaggedInternalEntry(low_value.rawValue()));
    try std.testing.expectEqual(@as(?usize, 0), low_value.value());

    try std.testing.expectEqual(SlotKind.pointer, low_pointer.kind());
    try std.testing.expect(!isTaggedInternalEntry(low_pointer.rawValue()));
    try std.testing.expectEqual(@as(?usize, 2), low_pointer.pointerValue());

    try std.testing.expectEqual(SlotKind.value, high_value.kind());
    try std.testing.expect(isTaggedInternalEntry(high_value.rawValue()));
    try std.testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), high_value.value());

    try std.testing.expectEqual(SlotKind.pointer, high_pointer.kind());
    try std.testing.expect(!isTaggedInternalEntry(high_pointer.rawValue()));
    try std.testing.expectEqual(@as(?usize, err_ptr.err_floor - 1), high_pointer.pointerValue());

    try std.testing.expectEqual(SlotKind.err, first_err.kind());
    try std.testing.expect(isTaggedInternalEntry(first_err.rawValue()));
    try std.testing.expectEqual(@as(?isize, -4095), first_err.errorCode());

    try std.testing.expectEqual(SlotKind.err, top_err.kind());
    try std.testing.expect(isTaggedInternalEntry(top_err.rawValue()));
    try std.testing.expectEqual(@as(?isize, -1), top_err.errorCode());
}

test "constructor accessors stay lane-specific at both slot cutoffs" {
    const low_null = nullSlot();
    const low_value = try fromValue(0);
    const low_pointer = fromPointer(2);
    const high_value = try fromValue(xa_value.safe_inline_limit);
    const high_pointer = fromPointer(err_ptr.err_floor - 1);
    const first_err = fromErrorCode(-4095);
    const top_err = fromErrorCode(-1);

    try std.testing.expectEqual(@as(?usize, null), low_null.value());
    try std.testing.expectEqual(@as(?isize, null), low_null.errorCode());
    try std.testing.expectEqual(@as(?usize, null), low_null.pointerValue());

    try std.testing.expectEqual(@as(?usize, 0), low_value.value());
    try std.testing.expectEqual(@as(?isize, null), low_value.errorCode());
    try std.testing.expectEqual(@as(?usize, null), low_value.pointerValue());

    try std.testing.expectEqual(@as(?usize, null), low_pointer.value());
    try std.testing.expectEqual(@as(?isize, null), low_pointer.errorCode());
    try std.testing.expectEqual(@as(?usize, 2), low_pointer.pointerValue());

    try std.testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), high_value.value());
    try std.testing.expectEqual(@as(?isize, null), high_value.errorCode());
    try std.testing.expectEqual(@as(?usize, null), high_value.pointerValue());

    try std.testing.expectEqual(@as(?usize, null), high_pointer.value());
    try std.testing.expectEqual(@as(?isize, null), high_pointer.errorCode());
    try std.testing.expectEqual(@as(?usize, err_ptr.err_floor - 1), high_pointer.pointerValue());

    try std.testing.expectEqual(@as(?usize, null), first_err.value());
    try std.testing.expectEqual(@as(?isize, -4095), first_err.errorCode());
    try std.testing.expectEqual(@as(?usize, null), first_err.pointerValue());

    try std.testing.expectEqual(@as(?usize, null), top_err.value());
    try std.testing.expectEqual(@as(?isize, -1), top_err.errorCode());
    try std.testing.expectEqual(@as(?usize, null), top_err.pointerValue());
}

test "constructor outputs round-trip through fromRaw at both slot cutoffs" {
    const cases = [_]struct {
        slot: SlotView,
        kind: SlotKind,
        value: ?usize,
        error_code: ?isize,
        pointer: ?usize,
    }{
        .{ .slot = nullSlot(), .kind = .null, .value = null, .error_code = null, .pointer = null },
        .{ .slot = try fromValue(0), .kind = .value, .value = 0, .error_code = null, .pointer = null },
        .{ .slot = fromPointer(2), .kind = .pointer, .value = null, .error_code = null, .pointer = 2 },
        .{
            .slot = try fromValue(xa_value.safe_inline_limit),
            .kind = .value,
            .value = xa_value.safe_inline_limit,
            .error_code = null,
            .pointer = null,
        },
        .{
            .slot = fromPointer(err_ptr.err_floor - 1),
            .kind = .pointer,
            .value = null,
            .error_code = null,
            .pointer = err_ptr.err_floor - 1,
        },
        .{ .slot = fromErrorCode(-4095), .kind = .err, .value = null, .error_code = -4095, .pointer = null },
        .{ .slot = fromErrorCode(-1), .kind = .err, .value = null, .error_code = -1, .pointer = null },
    };

    for (cases) |case| {
        const decoded = fromRaw(case.slot.rawValue());

        try std.testing.expectEqual(case.slot.rawValue(), decoded.rawValue());
        try std.testing.expectEqual(case.kind, decoded.kind());
        try std.testing.expectEqual(case.value, decoded.value());
        try std.testing.expectEqual(case.error_code, decoded.errorCode());
        try std.testing.expectEqual(case.pointer, decoded.pointerValue());
    }
}

test "decoded cutoff entries rebuild through public constructors without raw drift" {
    const cases = [_]struct {
        raw: usize,
        kind: SlotKind,
    }{
        .{ .raw = 0, .kind = .null },
        .{ .raw = try xa_value.makeValue(0), .kind = .value },
        .{ .raw = 2, .kind = .pointer },
        .{ .raw = try xa_value.makeValue(xa_value.safe_inline_limit), .kind = .value },
        .{ .raw = err_ptr.err_floor - 1, .kind = .pointer },
        .{ .raw = err_ptr.err_floor, .kind = .err },
        .{ .raw = err_ptr.fromErrorCode(-1), .kind = .err },
    };

    for (cases) |case| {
        const decoded = fromRaw(case.raw);
        const rebuilt = switch (case.kind) {
            .null => nullSlot(),
            .value => try fromValue(decoded.value().?),
            .err => fromErrorCode(decoded.errorCode().?),
            .pointer => fromPointer(decoded.pointerValue().?),
        };

        try std.testing.expectEqual(case.kind, decoded.kind());
        try std.testing.expectEqual(case.raw, rebuilt.rawValue());
        try std.testing.expectEqual(decoded.rawValue(), rebuilt.rawValue());
        try std.testing.expectEqual(decoded.kind(), rebuilt.kind());
    }
}

test "decoded cutoff entries keep payload accessors stable after reconstruction" {
    const cases = [_]struct {
        raw: usize,
        kind: SlotKind,
        value: ?usize,
        error_code: ?isize,
        pointer: ?usize,
    }{
        .{ .raw = 0, .kind = .null, .value = null, .error_code = null, .pointer = null },
        .{ .raw = try xa_value.makeValue(0), .kind = .value, .value = 0, .error_code = null, .pointer = null },
        .{ .raw = 2, .kind = .pointer, .value = null, .error_code = null, .pointer = 2 },
        .{
            .raw = try xa_value.makeValue(xa_value.safe_inline_limit),
            .kind = .value,
            .value = xa_value.safe_inline_limit,
            .error_code = null,
            .pointer = null,
        },
        .{
            .raw = err_ptr.err_floor - 1,
            .kind = .pointer,
            .value = null,
            .error_code = null,
            .pointer = err_ptr.err_floor - 1,
        },
        .{ .raw = err_ptr.err_floor, .kind = .err, .value = null, .error_code = -4095, .pointer = null },
        .{ .raw = err_ptr.fromErrorCode(-1), .kind = .err, .value = null, .error_code = -1, .pointer = null },
    };

    for (cases) |case| {
        const decoded = fromRaw(case.raw);
        const rebuilt = switch (decoded.kind()) {
            .null => nullSlot(),
            .value => try fromValue(decoded.value().?),
            .err => fromErrorCode(decoded.errorCode().?),
            .pointer => fromPointer(decoded.pointerValue().?),
        };
        const redecode = fromRaw(rebuilt.rawValue());

        try std.testing.expectEqual(case.kind, decoded.kind());
        try std.testing.expectEqual(case.value, decoded.value());
        try std.testing.expectEqual(case.error_code, decoded.errorCode());
        try std.testing.expectEqual(case.pointer, decoded.pointerValue());

        try std.testing.expectEqual(case.raw, rebuilt.rawValue());
        try std.testing.expectEqual(case.raw, redecode.rawValue());
        try std.testing.expectEqual(case.kind, redecode.kind());
        try std.testing.expectEqual(case.value, redecode.value());
        try std.testing.expectEqual(case.error_code, redecode.errorCode());
        try std.testing.expectEqual(case.pointer, redecode.pointerValue());
        try std.testing.expectEqual(isTaggedInternalEntry(case.raw), isTaggedInternalEntry(redecode.rawValue()));
    }
}

test "contiguous low and high boundary windows rebuild without lane drift" {
    const low_window = [_]struct {
        raw: usize,
        kind: SlotKind,
        value: ?usize,
        error_code: ?isize,
        pointer: ?usize,
    }{
        .{ .raw = 0, .kind = .null, .value = null, .error_code = null, .pointer = null },
        .{ .raw = 1, .kind = .value, .value = 0, .error_code = null, .pointer = null },
        .{ .raw = 2, .kind = .pointer, .value = null, .error_code = null, .pointer = 2 },
        .{ .raw = 3, .kind = .value, .value = 1, .error_code = null, .pointer = null },
        .{ .raw = 4, .kind = .pointer, .value = null, .error_code = null, .pointer = 4 },
        .{ .raw = 5, .kind = .value, .value = 2, .error_code = null, .pointer = null },
    };
    const high_window = [_]struct {
        raw: usize,
        kind: SlotKind,
        value: ?usize,
        error_code: ?isize,
        pointer: ?usize,
    }{
        .{
            .raw = err_ptr.err_floor - 2,
            .kind = .value,
            .value = xa_value.safe_inline_limit,
            .error_code = null,
            .pointer = null,
        },
        .{
            .raw = err_ptr.err_floor - 1,
            .kind = .pointer,
            .value = null,
            .error_code = null,
            .pointer = err_ptr.err_floor - 1,
        },
        .{ .raw = err_ptr.err_floor, .kind = .err, .value = null, .error_code = -4095, .pointer = null },
        .{ .raw = err_ptr.err_floor + 1, .kind = .err, .value = null, .error_code = -4094, .pointer = null },
    };

    for (low_window, 0..) |case, index| {
        const decoded = fromRaw(case.raw);
        const rebuilt = switch (decoded.kind()) {
            .null => nullSlot(),
            .value => try fromValue(decoded.value().?),
            .err => fromErrorCode(decoded.errorCode().?),
            .pointer => fromPointer(decoded.pointerValue().?),
        };
        const redecode = fromRaw(rebuilt.rawValue());

        try std.testing.expectEqual(case.kind, decoded.kind());
        try std.testing.expectEqual(case.value, decoded.value());
        try std.testing.expectEqual(case.error_code, decoded.errorCode());
        try std.testing.expectEqual(case.pointer, decoded.pointerValue());
        try std.testing.expectEqual(case.raw, rebuilt.rawValue());
        try std.testing.expectEqual(case.raw, redecode.rawValue());
        try std.testing.expectEqual(case.kind, redecode.kind());
        try std.testing.expectEqual(case.value, redecode.value());
        try std.testing.expectEqual(case.error_code, redecode.errorCode());
        try std.testing.expectEqual(case.pointer, redecode.pointerValue());
        try std.testing.expectEqual(isTaggedInternalEntry(case.raw), isTaggedInternalEntry(redecode.rawValue()));

        if (index > 0) {
            try std.testing.expectEqual(low_window[index - 1].raw + 1, case.raw);
        }
    }

    for (high_window, 0..) |case, index| {
        const decoded = fromRaw(case.raw);
        const rebuilt = switch (decoded.kind()) {
            .null => nullSlot(),
            .value => try fromValue(decoded.value().?),
            .err => fromErrorCode(decoded.errorCode().?),
            .pointer => fromPointer(decoded.pointerValue().?),
        };
        const redecode = fromRaw(rebuilt.rawValue());

        try std.testing.expectEqual(case.kind, decoded.kind());
        try std.testing.expectEqual(case.value, decoded.value());
        try std.testing.expectEqual(case.error_code, decoded.errorCode());
        try std.testing.expectEqual(case.pointer, decoded.pointerValue());
        try std.testing.expectEqual(case.raw, rebuilt.rawValue());
        try std.testing.expectEqual(case.raw, redecode.rawValue());
        try std.testing.expectEqual(case.kind, redecode.kind());
        try std.testing.expectEqual(case.value, redecode.value());
        try std.testing.expectEqual(case.error_code, redecode.errorCode());
        try std.testing.expectEqual(case.pointer, redecode.pointerValue());
        try std.testing.expectEqual(isTaggedInternalEntry(case.raw), isTaggedInternalEntry(redecode.rawValue()));

        if (index > 0) {
            try std.testing.expectEqual(high_window[index - 1].raw + 1, case.raw);
        }
    }
}

test "high-end raw cadence keeps alternating value tags and pointer gaps up to err floor" {
    const raw_cases = [_]struct {
        raw: usize,
        kind: SlotKind,
        value: ?usize,
        error_code: ?isize,
        pointer: ?usize,
    }{
        .{
            .raw = err_ptr.err_floor - 6,
            .kind = .value,
            .value = xa_value.safe_inline_limit - 2,
            .error_code = null,
            .pointer = null,
        },
        .{
            .raw = err_ptr.err_floor - 5,
            .kind = .pointer,
            .value = null,
            .error_code = null,
            .pointer = err_ptr.err_floor - 5,
        },
        .{
            .raw = err_ptr.err_floor - 4,
            .kind = .value,
            .value = xa_value.safe_inline_limit - 1,
            .error_code = null,
            .pointer = null,
        },
        .{
            .raw = err_ptr.err_floor - 3,
            .kind = .pointer,
            .value = null,
            .error_code = null,
            .pointer = err_ptr.err_floor - 3,
        },
        .{
            .raw = err_ptr.err_floor - 2,
            .kind = .value,
            .value = xa_value.safe_inline_limit,
            .error_code = null,
            .pointer = null,
        },
        .{
            .raw = err_ptr.err_floor - 1,
            .kind = .pointer,
            .value = null,
            .error_code = null,
            .pointer = err_ptr.err_floor - 1,
        },
        .{
            .raw = err_ptr.err_floor,
            .kind = .err,
            .value = null,
            .error_code = -4095,
            .pointer = null,
        },
    };

    for (raw_cases, 0..) |case, index| {
        const slot = fromRaw(case.raw);

        try std.testing.expectEqual(case.kind, slot.kind());
        try std.testing.expectEqual(case.value, slot.value());
        try std.testing.expectEqual(case.error_code, slot.errorCode());
        try std.testing.expectEqual(case.pointer, slot.pointerValue());

        if (index > 0) {
            try std.testing.expectEqual(raw_cases[index - 1].raw + 1, case.raw);
        }
    }

    const third_from_top_value = try fromValue(xa_value.safe_inline_limit - 2);
    const second_pointer_gap = fromPointer(err_ptr.err_floor - 3);
    const top_value = try fromValue(xa_value.safe_inline_limit);
    const final_pointer_gap = fromPointer(err_ptr.err_floor - 1);
    const first_err = fromErrorCode(-4095);

    try std.testing.expectEqual(@as(usize, err_ptr.err_floor - 6), third_from_top_value.rawValue());
    try std.testing.expectEqual(@as(usize, err_ptr.err_floor - 3), second_pointer_gap.rawValue());
    try std.testing.expectEqual(@as(usize, err_ptr.err_floor - 2), top_value.rawValue());
    try std.testing.expectEqual(@as(usize, err_ptr.err_floor - 1), final_pointer_gap.rawValue());
    try std.testing.expectEqual(@as(usize, err_ptr.err_floor), first_err.rawValue());
    try std.testing.expectEqual(@as(?usize, xa_value.safe_inline_limit - 2), third_from_top_value.value());
    try std.testing.expectEqual(@as(?usize, err_ptr.err_floor - 3), second_pointer_gap.pointerValue());
    try std.testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), top_value.value());
    try std.testing.expectEqual(@as(?usize, err_ptr.err_floor - 1), final_pointer_gap.pointerValue());
    try std.testing.expectEqual(@as(?isize, -4095), first_err.errorCode());
}

test "high-end cadence rebuilds through constructors without raw drift" {
    const raw_cases = [_]struct {
        raw: usize,
        kind: SlotKind,
        value: ?usize,
        error_code: ?isize,
        pointer: ?usize,
    }{
        .{
            .raw = err_ptr.err_floor - 6,
            .kind = .value,
            .value = xa_value.safe_inline_limit - 2,
            .error_code = null,
            .pointer = null,
        },
        .{
            .raw = err_ptr.err_floor - 5,
            .kind = .pointer,
            .value = null,
            .error_code = null,
            .pointer = err_ptr.err_floor - 5,
        },
        .{
            .raw = err_ptr.err_floor - 4,
            .kind = .value,
            .value = xa_value.safe_inline_limit - 1,
            .error_code = null,
            .pointer = null,
        },
        .{
            .raw = err_ptr.err_floor - 3,
            .kind = .pointer,
            .value = null,
            .error_code = null,
            .pointer = err_ptr.err_floor - 3,
        },
        .{
            .raw = err_ptr.err_floor - 2,
            .kind = .value,
            .value = xa_value.safe_inline_limit,
            .error_code = null,
            .pointer = null,
        },
        .{
            .raw = err_ptr.err_floor - 1,
            .kind = .pointer,
            .value = null,
            .error_code = null,
            .pointer = err_ptr.err_floor - 1,
        },
        .{
            .raw = err_ptr.err_floor,
            .kind = .err,
            .value = null,
            .error_code = -4095,
            .pointer = null,
        },
        .{
            .raw = err_ptr.err_floor + 1,
            .kind = .err,
            .value = null,
            .error_code = -4094,
            .pointer = null,
        },
    };

    for (raw_cases, 0..) |case, index| {
        const decoded = fromRaw(case.raw);
        const rebuilt = switch (decoded.kind()) {
            .null => nullSlot(),
            .value => try fromValue(decoded.value().?),
            .err => fromErrorCode(decoded.errorCode().?),
            .pointer => fromPointer(decoded.pointerValue().?),
        };
        const redecode = fromRaw(rebuilt.rawValue());

        try std.testing.expectEqual(case.kind, decoded.kind());
        try std.testing.expectEqual(case.value, decoded.value());
        try std.testing.expectEqual(case.error_code, decoded.errorCode());
        try std.testing.expectEqual(case.pointer, decoded.pointerValue());
        try std.testing.expectEqual(case.raw, rebuilt.rawValue());
        try std.testing.expectEqual(case.raw, redecode.rawValue());
        try std.testing.expectEqual(case.kind, redecode.kind());
        try std.testing.expectEqual(case.value, redecode.value());
        try std.testing.expectEqual(case.error_code, redecode.errorCode());
        try std.testing.expectEqual(case.pointer, redecode.pointerValue());
        try std.testing.expectEqual(isTaggedInternalEntry(case.raw), isTaggedInternalEntry(redecode.rawValue()));

        if (index > 0) {
            try std.testing.expectEqual(raw_cases[index - 1].raw + 1, case.raw);
        }
    }
}

test "constructor-built high window stays contiguous through fromRaw and rebuild" {
    const cases = [_]struct {
        slot: SlotView,
        raw: usize,
        kind: SlotKind,
        value: ?usize,
        error_code: ?isize,
        pointer: ?usize,
    }{
        .{
            .slot = try fromValue(xa_value.safe_inline_limit - 2),
            .raw = err_ptr.err_floor - 6,
            .kind = .value,
            .value = xa_value.safe_inline_limit - 2,
            .error_code = null,
            .pointer = null,
        },
        .{
            .slot = fromPointer(err_ptr.err_floor - 5),
            .raw = err_ptr.err_floor - 5,
            .kind = .pointer,
            .value = null,
            .error_code = null,
            .pointer = err_ptr.err_floor - 5,
        },
        .{
            .slot = try fromValue(xa_value.safe_inline_limit - 1),
            .raw = err_ptr.err_floor - 4,
            .kind = .value,
            .value = xa_value.safe_inline_limit - 1,
            .error_code = null,
            .pointer = null,
        },
        .{
            .slot = fromPointer(err_ptr.err_floor - 3),
            .raw = err_ptr.err_floor - 3,
            .kind = .pointer,
            .value = null,
            .error_code = null,
            .pointer = err_ptr.err_floor - 3,
        },
        .{
            .slot = try fromValue(xa_value.safe_inline_limit),
            .raw = err_ptr.err_floor - 2,
            .kind = .value,
            .value = xa_value.safe_inline_limit,
            .error_code = null,
            .pointer = null,
        },
        .{
            .slot = fromPointer(err_ptr.err_floor - 1),
            .raw = err_ptr.err_floor - 1,
            .kind = .pointer,
            .value = null,
            .error_code = null,
            .pointer = err_ptr.err_floor - 1,
        },
        .{
            .slot = fromErrorCode(-4095),
            .raw = err_ptr.err_floor,
            .kind = .err,
            .value = null,
            .error_code = -4095,
            .pointer = null,
        },
        .{
            .slot = fromErrorCode(-4094),
            .raw = err_ptr.err_floor + 1,
            .kind = .err,
            .value = null,
            .error_code = -4094,
            .pointer = null,
        },
    };

    for (cases, 0..) |case, index| {
        const decoded = fromRaw(case.slot.rawValue());
        const rebuilt = switch (case.kind) {
            .null => nullSlot(),
            .value => try fromValue(decoded.value().?),
            .err => fromErrorCode(decoded.errorCode().?),
            .pointer => fromPointer(decoded.pointerValue().?),
        };
        const redecode = fromRaw(rebuilt.rawValue());

        try std.testing.expectEqual(case.raw, case.slot.rawValue());
        try std.testing.expectEqual(case.kind, case.slot.kind());
        try std.testing.expectEqual(case.value, case.slot.value());
        try std.testing.expectEqual(case.error_code, case.slot.errorCode());
        try std.testing.expectEqual(case.pointer, case.slot.pointerValue());

        try std.testing.expectEqual(case.raw, decoded.rawValue());
        try std.testing.expectEqual(case.kind, decoded.kind());
        try std.testing.expectEqual(case.value, decoded.value());
        try std.testing.expectEqual(case.error_code, decoded.errorCode());
        try std.testing.expectEqual(case.pointer, decoded.pointerValue());

        try std.testing.expectEqual(case.raw, rebuilt.rawValue());
        try std.testing.expectEqual(case.raw, redecode.rawValue());
        try std.testing.expectEqual(case.kind, redecode.kind());
        try std.testing.expectEqual(case.value, redecode.value());
        try std.testing.expectEqual(case.error_code, redecode.errorCode());
        try std.testing.expectEqual(case.pointer, redecode.pointerValue());
        try std.testing.expectEqual(isTaggedInternalEntry(case.raw), isTaggedInternalEntry(redecode.rawValue()));

        if (index > 0) {
            try std.testing.expectEqual(cases[index - 1].raw + 1, case.raw);
        }
    }
}

test "err band stays contiguous after the pointer-like cutoff gap" {
    const gap_raw = err_ptr.err_floor - 1;
    const first_err_raw = err_ptr.err_floor;
    const second_err_raw = first_err_raw + 1;
    const top_err_raw = err_ptr.fromErrorCode(-1);

    const gap_slot = fromRaw(gap_raw);
    const first_err_slot = fromRaw(first_err_raw);
    const second_err_slot = fromRaw(second_err_raw);
    const top_err_slot = fromRaw(top_err_raw);

    try std.testing.expect(gap_slot.isPointer());
    try std.testing.expectEqual(@as(?usize, gap_raw), gap_slot.pointerValue());
    try std.testing.expectEqual(@as(?isize, null), gap_slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), gap_slot.value());

    try std.testing.expectEqual(gap_raw + 1, first_err_raw);
    try std.testing.expectEqual(first_err_raw + 1, second_err_raw);
    try std.testing.expectEqual(err_ptr.fromErrorCode(-4094), second_err_raw);

    try std.testing.expect(first_err_slot.isErr());
    try std.testing.expect(second_err_slot.isErr());
    try std.testing.expect(top_err_slot.isErr());

    try std.testing.expectEqual(@as(?isize, -4095), first_err_slot.errorCode());
    try std.testing.expectEqual(@as(?isize, -4094), second_err_slot.errorCode());
    try std.testing.expectEqual(@as(?isize, -1), top_err_slot.errorCode());

    try std.testing.expectEqual(@as(?usize, null), first_err_slot.pointerValue());
    try std.testing.expectEqual(@as(?usize, null), second_err_slot.pointerValue());
    try std.testing.expectEqual(@as(?usize, null), top_err_slot.pointerValue());
    try std.testing.expectEqual(@as(?usize, null), first_err_slot.value());
    try std.testing.expectEqual(@as(?usize, null), second_err_slot.value());
    try std.testing.expectEqual(@as(?usize, null), top_err_slot.value());

    try std.testing.expect(isTaggedInternalEntry(first_err_raw));
    try std.testing.expect(isTaggedInternalEntry(second_err_raw));
    try std.testing.expect(isTaggedInternalEntry(top_err_raw));
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
