const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn expectSlot(
    raw: usize,
    expected_kind: xarray_slot_view.SlotKind,
    expected_value: ?usize,
    expected_error: ?isize,
) !void {
    const slot = xarray_slot_view.fromRaw(raw);

    try testing.expectEqual(expected_kind, slot.kind());
    try testing.expectEqual(raw, slot.rawValue());
    try testing.expectEqual(expected_value, slot.value());
    try testing.expectEqual(expected_error, slot.errorCode());

    switch (expected_kind) {
        .null => {
            try testing.expect(slot.isNull());
            try testing.expect(!slot.isValue());
            try testing.expect(!slot.isErr());
            try testing.expect(!slot.isPointer());
            try testing.expectEqual(@as(?usize, null), slot.pointerValue());
            try testing.expect(!xarray_slot_view.isTaggedInternalEntry(raw));
        },
        .value => {
            try testing.expect(!slot.isNull());
            try testing.expect(slot.isValue());
            try testing.expect(!slot.isErr());
            try testing.expect(!slot.isPointer());
            try testing.expectEqual(@as(?usize, null), slot.pointerValue());
            try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
        },
        .err => {
            try testing.expect(!slot.isNull());
            try testing.expect(!slot.isValue());
            try testing.expect(slot.isErr());
            try testing.expect(!slot.isPointer());
            try testing.expectEqual(@as(?usize, null), slot.pointerValue());
            try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
        },
        .pointer => {
            try testing.expect(!slot.isNull());
            try testing.expect(!slot.isValue());
            try testing.expect(!slot.isErr());
            try testing.expect(slot.isPointer());
            try testing.expectEqual(@as(?usize, raw), slot.pointerValue());
            try testing.expect(!xarray_slot_view.isTaggedInternalEntry(raw));
        },
    }
}

fn rejectedInlineRaw(value: usize) usize {
    return (value << 1) | xa_value.value_tag_mask;
}

test "cutoff seam arithmetic stays exact at the value and err boundary" {
    const accepted_limit_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const first_rejected_value = xa_value.safe_inline_limit + 1;
    const second_rejected_value = xa_value.safe_inline_limit + 2;

    try testing.expectEqual(err_ptr.err_floor - 2, accepted_limit_raw);
    try testing.expectEqual(err_ptr.err_floor, rejectedInlineRaw(first_rejected_value));
    try testing.expectEqual(err_ptr.err_floor + 2, rejectedInlineRaw(second_rejected_value));
    try testing.expectEqual(@as(isize, -4095), err_ptr.toErrorCode(err_ptr.err_floor));
    try testing.expectEqual(@as(isize, -4093), err_ptr.toErrorCode(err_ptr.err_floor + 2));
}

test "cutoff window keeps accepted values, the pointer gap, and opening err raws distinct" {
    const accepted_before = try xa_value.makeValue(xa_value.safe_inline_limit - 1);
    const accepted_limit = try xa_value.makeValue(xa_value.safe_inline_limit);
    const gap_before_err = err_ptr.err_floor - 1;

    try expectSlot(accepted_before, .value, xa_value.safe_inline_limit - 1, null);
    try expectSlot(accepted_limit, .value, xa_value.safe_inline_limit, null);
    try expectSlot(gap_before_err, .pointer, null, null);
    try expectSlot(err_ptr.err_floor, .err, null, -4095);
    try expectSlot(err_ptr.err_floor + 1, .err, null, -4094);
    try expectSlot(err_ptr.err_floor + 2, .err, null, -4093);
}

test "rejected inline values stay in the err lane even when the low tag bit is set" {
    const first_rejected_raw = rejectedInlineRaw(xa_value.safe_inline_limit + 1);
    const second_rejected_raw = rejectedInlineRaw(xa_value.safe_inline_limit + 2);
    const top_tagged_err_raw = err_ptr.fromErrorCode(-1);

    try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(xa_value.safe_inline_limit + 1));
    try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(xa_value.safe_inline_limit + 2));

    for ([_]usize{ first_rejected_raw, second_rejected_raw, top_tagged_err_raw }) |raw| {
        try testing.expect((raw & xa_value.value_tag_mask) == xa_value.value_tag_mask);
        try testing.expect(err_ptr.isErrValue(raw));
        try testing.expect(!xa_value.isValue(raw));
        try expectSlot(raw, .err, null, err_ptr.toErrorCode(raw));
    }
}
