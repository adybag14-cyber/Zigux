const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn firstRejectedPayload() usize {
    return xa_value.safe_inline_limit + 1;
}

fn lastRejectedPayload() usize {
    return std.math.maxInt(usize) >> 1;
}

fn aliasIndexFromRaw(raw: usize) usize {
    return (raw - err_ptr.err_floor) / 2;
}

fn expectedPayloadFromRaw(raw: usize) usize {
    return firstRejectedPayload() + aliasIndexFromRaw(raw);
}

fn expectedCodeFromPayload(payload: usize) isize {
    const index = payload - firstRejectedPayload();
    return -@as(isize, @intCast(err_ptr.max_errno)) + @as(isize, @intCast(index * 2));
}

test "odd rejected alias raws follow the closed-form raw-to-payload equation" {
    var code = -@as(isize, @intCast(err_ptr.max_errno));

    while (code <= -1) : (code += 1) {
        const raw = err_ptr.fromErrorCode(code);
        if ((raw & xa_value.value_tag_mask) == 0) {
            continue;
        }

        const payload = expectedPayloadFromRaw(raw);
        const slot = xarray_slot_view.fromRaw(raw);

        try std.testing.expect(slot.isErr());
        try std.testing.expectEqual(@as(?isize, code), slot.errorCode());
        try std.testing.expectEqual(raw, (payload << 1) | xa_value.value_tag_mask);
        try std.testing.expectEqual(payload, raw >> 1);
        try std.testing.expect(!xa_value.canRepresent(payload));
        try std.testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(payload));
    }
}

test "rejected payloads follow the inverse payload-to-error-code equation" {
    const samples = [_]usize{
        firstRejectedPayload(),
        firstRejectedPayload() + 1,
        firstRejectedPayload() + 17,
        firstRejectedPayload() + 511,
        lastRejectedPayload() - 1,
        lastRejectedPayload(),
    };

    for (samples) |payload| {
        const raw = (payload << 1) | xa_value.value_tag_mask;
        const expected_code = expectedCodeFromPayload(payload);
        const slot = xarray_slot_view.fromRaw(raw);
        const rebuilt = xarray_slot_view.fromErrorCode(expected_code);

        try std.testing.expect(slot.isErr());
        try std.testing.expectEqual(raw, rebuilt.rawValue());
        try std.testing.expectEqual(@as(?isize, expected_code), slot.errorCode());
        try std.testing.expectEqual(raw, err_ptr.fromErrorCode(expected_code));
        try std.testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(payload));
    }
}

test "the inverse equations meet exactly at the representable boundary" {
    const highest_inline = xa_value.safe_inline_limit;
    const first_rejected = firstRejectedPayload();

    const highest_inline_raw = try xa_value.makeValue(highest_inline);
    const first_rejected_raw = err_ptr.err_floor;

    try std.testing.expectEqual(err_ptr.err_floor - 2, highest_inline_raw);
    try std.testing.expectEqual(err_ptr.err_floor, first_rejected_raw);
    try std.testing.expectEqual(highest_inline + 1, first_rejected);
    try std.testing.expectEqual(@as(isize, -@as(isize, @intCast(err_ptr.max_errno))), expectedCodeFromPayload(first_rejected));
    try std.testing.expectEqual(first_rejected, expectedPayloadFromRaw(first_rejected_raw));
}
