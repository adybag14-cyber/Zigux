const std = @import("std");
const xa_value = @import("xa_value");
const err_ptr = @import("err_ptr");

test "phase3 xa_value safe inline limit remains the top representable tagged value" {
    const raw = try xa_value.makeValue(xa_value.safe_inline_limit);

    try std.testing.expect(xa_value.canRepresent(xa_value.safe_inline_limit));
    try std.testing.expect(xa_value.isValue(raw));
    try std.testing.expectEqual(xa_value.safe_inline_limit, xa_value.toValue(raw));
    try std.testing.expectEqual(err_ptr.err_floor, raw + 2);
}

test "phase3 xa_value rejects the first tagged value that would overlap err_ptr" {
    const first_overlapping_value = xa_value.safe_inline_limit + 1;
    const overlapping_raw = (first_overlapping_value << 1) | xa_value.value_tag_mask;

    try std.testing.expectError(
        error.ValueWouldOverlapErrPtr,
        xa_value.makeValue(first_overlapping_value),
    );
    try std.testing.expect(!xa_value.canRepresent(first_overlapping_value));
    try std.testing.expect(err_ptr.isErrValue(overlapping_raw));
    try std.testing.expect(!xa_value.isValue(overlapping_raw));
}
