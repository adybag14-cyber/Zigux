const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");

fn retagRejectedValue(value: usize) usize {
    return (value << 1) | xa_value.value_tag_mask;
}

test "accepted xa_value range stops exactly at the err_ptr cutoff strip" {
    const first_raw = try xa_value.makeValue(0);
    const last_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const separator_raw = last_raw + 1;

    try testing.expectEqual(@as(usize, 1), first_raw);
    try testing.expectEqual(err_ptr.err_floor - 2, last_raw);
    try testing.expectEqual(err_ptr.err_floor - 1, separator_raw);
    try testing.expect(xa_value.isValue(first_raw));
    try testing.expect(xa_value.isValue(last_raw));
    try testing.expect(!xa_value.isValue(separator_raw));
    try testing.expect(!err_ptr.isErrValue(separator_raw));
    try testing.expectEqual(err_ptr.err_floor, separator_raw + 1);
}

test "err_ptr band keeps the expected total and parity counts" {
    var total_count: usize = 0;
    var odd_count: usize = 0;
    var even_count: usize = 0;
    var raw = err_ptr.err_floor;

    while (true) {
        try testing.expect(err_ptr.isErrValue(raw));

        const code = err_ptr.toErrorCode(raw);
        try testing.expect(code <= -1);
        try testing.expect(code >= -@as(isize, @intCast(err_ptr.max_errno)));

        total_count += 1;
        if ((raw & xa_value.value_tag_mask) == xa_value.value_tag_mask) {
            odd_count += 1;
        } else {
            even_count += 1;
        }

        if (raw == std.math.maxInt(usize)) {
            break;
        }
        raw += 1;
    }

    try testing.expectEqual(err_ptr.max_errno, total_count);
    try testing.expectEqual((err_ptr.max_errno + 1) / 2, odd_count);
    try testing.expectEqual(err_ptr.max_errno / 2, even_count);
    try testing.expectEqual(@as(isize, -4095), err_ptr.toErrorCode(err_ptr.err_floor));
    try testing.expectEqual(@as(isize, -1), err_ptr.toErrorCode(std.math.maxInt(usize)));
}

test "rejected inline payloads start and end with the odd err_ptr ladder" {
    const first_rejected_value = xa_value.safe_inline_limit + 1;
    const first_raw = retagRejectedValue(first_rejected_value);
    const second_raw = retagRejectedValue(first_rejected_value + 1);
    const top_raw = err_ptr.fromErrorCode(-1);
    const top_rejected_value = top_raw >> 1;

    try testing.expect(!xa_value.canRepresent(first_rejected_value));
    try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(first_rejected_value));
    try testing.expectEqual(err_ptr.err_floor, first_raw);
    try testing.expectEqual(err_ptr.err_floor + 2, second_raw);
    try testing.expectEqual(err_ptr.fromErrorCode(-1), top_raw);
    try testing.expectEqual(top_raw, retagRejectedValue(top_rejected_value));
    try testing.expect(!xa_value.canRepresent(top_rejected_value));
    try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(top_rejected_value));
}
