const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn oddAliasCount() usize {
    return (err_ptr.max_errno + 1) / 2;
}

fn evenErrCount() usize {
    return err_ptr.max_errno / 2;
}

test "err_ptr band splits into odd alias raws and even non-xa_value raws" {
    var odd_count: usize = 0;
    var even_count: usize = 0;
    var code = -@as(isize, @intCast(err_ptr.max_errno));

    while (code <= -1) : (code += 1) {
        const raw = err_ptr.fromErrorCode(code);
        const slot = xarray_slot_view.fromRaw(raw);

        try testing.expect(slot.isErr());
        try testing.expectEqual(@as(?isize, code), slot.errorCode());
        try testing.expectEqual(@as(?usize, null), slot.value());
        try testing.expectEqual(@as(?usize, null), slot.pointerValue());
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));

        if ((raw & xa_value.value_tag_mask) == 1) {
            const payload = raw >> 1;
            try testing.expectEqual((payload << 1) | xa_value.value_tag_mask, raw);
            try testing.expect(!xa_value.canRepresent(payload));
            try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(payload));
            odd_count += 1;
        } else {
            try testing.expect(!xa_value.isValue(raw));
            even_count += 1;
        }
    }

    try testing.expectEqual(oddAliasCount(), odd_count);
    try testing.expectEqual(evenErrCount(), even_count);
    try testing.expectEqual(err_ptr.max_errno, odd_count + even_count);
}

test "low, middle, and high err_ptr windows keep the same odd-even-odd cadence" {
    const starts = [_]isize{ -4095, -2049, -3 };

    for (starts) |start_code| {
        const lower = xarray_slot_view.fromErrorCode(start_code);
        const middle = xarray_slot_view.fromErrorCode(start_code + 1);
        const upper = xarray_slot_view.fromErrorCode(start_code + 2);

        try testing.expect(lower.isErr());
        try testing.expect(middle.isErr());
        try testing.expect(upper.isErr());

        try testing.expectEqual(@as(usize, 1), lower.rawValue() & xa_value.value_tag_mask);
        try testing.expectEqual(@as(usize, 0), middle.rawValue() & xa_value.value_tag_mask);
        try testing.expectEqual(@as(usize, 1), upper.rawValue() & xa_value.value_tag_mask);

        try testing.expectEqual(lower.rawValue() + 1, middle.rawValue());
        try testing.expectEqual(middle.rawValue() + 1, upper.rawValue());
        try testing.expectEqual(@as(?isize, start_code), lower.errorCode());
        try testing.expectEqual(@as(?isize, start_code + 1), middle.errorCode());
        try testing.expectEqual(@as(?isize, start_code + 2), upper.errorCode());

        try testing.expect(!xa_value.isValue(lower.rawValue()));
        try testing.expect(!xa_value.isValue(middle.rawValue()));
        try testing.expect(!xa_value.isValue(upper.rawValue()));
    }
}

test "err_ptr parity partition endpoints match the expected count formulas" {
    const first_odd = err_ptr.err_floor;
    const last_even = err_ptr.fromErrorCode(-2);
    const last_odd = err_ptr.fromErrorCode(-1);

    try testing.expectEqual(@as(usize, 1), first_odd & xa_value.value_tag_mask);
    try testing.expectEqual(@as(usize, 0), last_even & xa_value.value_tag_mask);
    try testing.expectEqual(@as(usize, 1), last_odd & xa_value.value_tag_mask);

    try testing.expectEqual(first_odd + ((oddAliasCount() - 1) * 2), last_odd);
    try testing.expectEqual(first_odd + ((evenErrCount() * 2) - 1), last_even);
    try testing.expectEqual(err_ptr.max_errno, oddAliasCount() + evenErrCount());
    try testing.expectEqual(std.math.maxInt(usize), last_odd);
}
