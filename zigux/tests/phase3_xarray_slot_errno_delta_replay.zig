const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const slot_view = @import("xarray_slot_view");

const ErrnoDeltaRow = struct {
    code: isize,
    expected_delta: usize,
};

const errno_delta_rows = [_]ErrnoDeltaRow{
    .{ .code = -4095, .expected_delta = 0 },
    .{ .code = -4094, .expected_delta = 1 },
    .{ .code = -2048, .expected_delta = 2047 },
    .{ .code = -1024, .expected_delta = 3071 },
    .{ .code = -512, .expected_delta = 3583 },
    .{ .code = -22, .expected_delta = 4073 },
    .{ .code = -1, .expected_delta = 4094 },
};

fn expectErrnoDelta(row: ErrnoDeltaRow) !void {
    const raw = err_ptr.fromErrorCode(row.code);
    const slot = slot_view.fromRaw(raw);
    const calculated_delta = raw - err_ptr.err_floor;
    const formula_delta: usize = @intCast(@as(isize, @intCast(err_ptr.max_errno)) + row.code);

    try std.testing.expectEqual(row.expected_delta, calculated_delta);
    try std.testing.expectEqual(formula_delta, calculated_delta);
    try std.testing.expectEqual(err_ptr.err_floor + row.expected_delta, raw);
    try std.testing.expect(slot.isErr());
    try std.testing.expect(slot.isTaggedEntry());
    try std.testing.expect(!slot.isValue());
    try std.testing.expect(!slot.isPointer());
    try std.testing.expectEqual(@as(?isize, row.code), slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), slot.value());
    try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
}

test "err_ptr errno deltas survive xarray slot projection" {
    for (errno_delta_rows) |row| {
        try expectErrnoDelta(row);
    }
}

test "adjacent raw errno deltas map to adjacent signed error codes" {
    for (errno_delta_rows[0 .. errno_delta_rows.len - 1]) |row| {
        const raw = err_ptr.fromErrorCode(row.code);
        const next_raw = raw + 1;
        const next_slot = slot_view.fromRaw(next_raw);

        try std.testing.expect(next_slot.isErr());
        try std.testing.expectEqual(row.expected_delta + 1, next_raw - err_ptr.err_floor);
        try std.testing.expectEqual(@as(?isize, row.code + 1), next_slot.errorCode());
        try std.testing.expectEqual(@as(?usize, null), next_slot.value());
        try std.testing.expectEqual(@as(?usize, null), next_slot.pointerValue());
    }
}

test "rejected xa_value aliases land at deterministic errno deltas" {
    const AliasRow = struct {
        inline_offset: usize,
        expected_code: isize,
        expected_delta: usize,
    };
    const alias_rows = [_]AliasRow{
        .{ .inline_offset = 0, .expected_code = -4095, .expected_delta = 0 },
        .{ .inline_offset = 1, .expected_code = -4093, .expected_delta = 2 },
        .{ .inline_offset = 16, .expected_code = -4063, .expected_delta = 32 },
        .{ .inline_offset = 64, .expected_code = -3967, .expected_delta = 128 },
    };

    for (alias_rows) |row| {
        const rejected_value = xa_value.safe_inline_limit + 1 + row.inline_offset;
        const raw = (rejected_value << 1) | xa_value.value_tag_mask;
        const slot = slot_view.fromRaw(raw);

        try std.testing.expect(!xa_value.canRepresent(rejected_value));
        try std.testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(rejected_value));
        try std.testing.expectEqual(err_ptr.err_floor + row.expected_delta, raw);
        try std.testing.expectEqual(row.expected_code, err_ptr.toErrorCode(raw));
        try std.testing.expect(slot.isErr());
        try std.testing.expect(slot.isTaggedEntry());
        try std.testing.expect(!slot.isValue());
        try std.testing.expect(!slot.isPointer());
        try std.testing.expectEqual(@as(?isize, row.expected_code), slot.errorCode());
        try std.testing.expectEqual(@as(?usize, null), slot.value());
        try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
    }
}
