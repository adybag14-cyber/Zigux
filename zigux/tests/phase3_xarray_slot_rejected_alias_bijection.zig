const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn aliasableErrRawCount() usize {
    return (err_ptr.max_errno + 1) / 2;
}

test "rejected inline payloads enumerate the odd err_ptr alias band exactly once" {
    var expected_payload = xa_value.safe_inline_limit + 1;
    var alias_count: usize = 0;
    var code = -@as(isize, @intCast(err_ptr.max_errno));

    while (code <= -1) : (code += 1) {
        const raw = err_ptr.fromErrorCode(code);
        const slot = xarray_slot_view.fromRaw(raw);

        try std.testing.expect(slot.isErr());
        try std.testing.expectEqual(raw, slot.rawValue());
        try std.testing.expectEqual(@as(?isize, code), slot.errorCode());

        if ((raw & xa_value.value_tag_mask) == 0) {
            try std.testing.expect(!xa_value.isValue(raw));
            continue;
        }

        try std.testing.expectEqual(expected_payload, raw >> 1);
        try std.testing.expectEqual(raw, (expected_payload << 1) | xa_value.value_tag_mask);
        try std.testing.expect(!xa_value.canRepresent(expected_payload));
        try std.testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(expected_payload));

        alias_count += 1;
        expected_payload += 1;
    }

    try std.testing.expectEqual(aliasableErrRawCount(), alias_count);
    try std.testing.expectEqual(std.math.maxInt(usize) >> 1, expected_payload - 1);
}

test "odd err_ptr alias band endpoints match the first and last rejected payloads" {
    const first_rejected_payload = xa_value.safe_inline_limit + 1;
    const last_rejected_payload = std.math.maxInt(usize) >> 1;

    const first_raw = err_ptr.err_floor;
    const last_raw = err_ptr.fromErrorCode(-1);

    try std.testing.expectEqual(first_raw, (first_rejected_payload << 1) | xa_value.value_tag_mask);
    try std.testing.expectEqual(last_raw, (last_rejected_payload << 1) | xa_value.value_tag_mask);

    const first_slot = xarray_slot_view.fromRaw(first_raw);
    const last_slot = xarray_slot_view.fromRaw(last_raw);

    try std.testing.expect(first_slot.isErr());
    try std.testing.expect(last_slot.isErr());
    try std.testing.expectEqual(@as(?isize, -@as(isize, @intCast(err_ptr.max_errno))), first_slot.errorCode());
    try std.testing.expectEqual(@as(?isize, -1), last_slot.errorCode());

    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(first_rejected_payload));
    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(last_rejected_payload));
}

test "every odd err_ptr alias raw sits between non-xa_value neighbors" {
    var code = -@as(isize, @intCast(err_ptr.max_errno));

    while (code <= -1) : (code += 1) {
        const raw = err_ptr.fromErrorCode(code);
        if ((raw & xa_value.value_tag_mask) == 0) {
            continue;
        }

        if (raw > err_ptr.err_floor) {
            try std.testing.expect(!xa_value.isValue(raw - 1));
        }
        if (raw < err_ptr.fromErrorCode(-1)) {
            try std.testing.expect(!xa_value.isValue(raw + 1));
        }
    }
}
