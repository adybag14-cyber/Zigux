const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn expectClosedInactiveAccessors(slot: xarray_slot_view.SlotView, kind: xarray_slot_view.SlotKind) !void {
    try testing.expectEqual(kind, slot.kind());

    switch (kind) {
        .null => {
            try testing.expectEqual(@as(?usize, null), slot.value());
            try testing.expectEqual(@as(?isize, null), slot.errorCode());
            try testing.expectEqual(@as(?usize, null), slot.pointerValue());
        },
        .value => {
            try testing.expect(slot.value() != null);
            try testing.expectEqual(@as(?isize, null), slot.errorCode());
            try testing.expectEqual(@as(?usize, null), slot.pointerValue());
        },
        .pointer => {
            try testing.expectEqual(@as(?usize, null), slot.value());
            try testing.expectEqual(@as(?isize, null), slot.errorCode());
            try testing.expect(slot.pointerValue() != null);
        },
        .err => {
            try testing.expectEqual(@as(?usize, null), slot.value());
            try testing.expect(slot.errorCode() != null);
            try testing.expectEqual(@as(?usize, null), slot.pointerValue());
        },
    }
}

test "low value-shaped raws stay value while high value-shaped raws stay err" {
    const low_payloads = [_]usize{ 0, 1, 29, xa_value.safe_inline_limit };

    for (low_payloads) |payload| {
        const raw = try xa_value.makeValue(payload);
        const slot = xarray_slot_view.fromRaw(raw);

        try testing.expectEqual(@as(usize, 1), raw & xa_value.value_tag_mask);
        try testing.expect(raw < err_ptr.err_floor);
        try testing.expect(xa_value.isValue(raw));
        try testing.expect(!err_ptr.isErrValue(raw));
        try expectClosedInactiveAccessors(slot, .value);
        try testing.expectEqual(@as(?usize, payload), slot.value());
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
    }

    const high_codes = [_]isize{ -4095, -4094, -3, -1 };

    for (high_codes) |code| {
        const raw = err_ptr.fromErrorCode(code);
        const slot = xarray_slot_view.fromRaw(raw);

        try testing.expect(raw >= err_ptr.err_floor);
        try testing.expect(err_ptr.isErrValue(raw));
        try testing.expect(!xa_value.isValue(raw));
        try expectClosedInactiveAccessors(slot, .err);
        try testing.expectEqual(@as(?isize, code), slot.errorCode());
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
    }
}

test "single pointer gap separates highest value raw from err floor raw" {
    const value_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const gap_raw = err_ptr.err_floor - 1;
    const err_raw = err_ptr.err_floor;

    try testing.expectEqual(value_raw + 1, gap_raw);
    try testing.expectEqual(gap_raw + 1, err_raw);

    const value_slot = xarray_slot_view.fromRaw(value_raw);
    const gap_slot = xarray_slot_view.fromRaw(gap_raw);
    const err_slot = xarray_slot_view.fromRaw(err_raw);

    try expectClosedInactiveAccessors(value_slot, .value);
    try expectClosedInactiveAccessors(gap_slot, .pointer);
    try expectClosedInactiveAccessors(err_slot, .err);

    try testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), value_slot.value());
    try testing.expectEqual(@as(?usize, gap_raw), gap_slot.pointerValue());
    try testing.expectEqual(@as(?isize, -@as(isize, @intCast(err_ptr.max_errno))), err_slot.errorCode());
    try testing.expect(!xarray_slot_view.isTaggedInternalEntry(gap_raw));
}

test "rejected value payloads decode through err_ptr instead of xa_value" {
    const rejected_payloads = [_]usize{
        xa_value.safe_inline_limit + 1,
        xa_value.safe_inline_limit + 2,
        err_ptr.fromErrorCode(-1) >> 1,
    };
    const expected_codes = [_]isize{ -4095, -4093, -1 };

    for (rejected_payloads, expected_codes) |payload, expected_code| {
        const raw = (payload << 1) | xa_value.value_tag_mask;
        const slot = xarray_slot_view.fromRaw(raw);

        try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(payload));
        try testing.expectEqual(@as(usize, 1), raw & xa_value.value_tag_mask);
        try testing.expect(err_ptr.isErrValue(raw));
        try testing.expect(!xa_value.isValue(raw));
        try expectClosedInactiveAccessors(slot, .err);
        try testing.expectEqual(@as(?isize, expected_code), slot.errorCode());
    }
}
