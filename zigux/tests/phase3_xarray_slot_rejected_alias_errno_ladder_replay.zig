const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const AliasCase = struct {
    rejected_offset: usize,
    errno: isize,
};

const alias_cases = [_]AliasCase{
    .{ .rejected_offset = 1, .errno = -4095 },
    .{ .rejected_offset = 2, .errno = -4093 },
    .{ .rejected_offset = 7, .errno = -4083 },
    .{ .rejected_offset = 64, .errno = -3969 },
    .{ .rejected_offset = 512, .errno = -3073 },
    .{ .rejected_offset = 2048, .errno = -1 },
};

fn rejectedAliasValue(offset: usize) usize {
    return xa_value.safe_inline_limit + offset;
}

fn rejectedAliasRaw(offset: usize) usize {
    return err_ptr.err_floor + ((offset - 1) * 2);
}

test "rejected inline aliases map onto the odd err_ptr errno ladder" {
    for (alias_cases) |case| {
        const value = rejectedAliasValue(case.rejected_offset);
        const raw = rejectedAliasRaw(case.rejected_offset);
        const slot = xarray_slot_view.fromRaw(raw);

        try testing.expect(!xa_value.canRepresent(value));
        try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(value));
        try testing.expectEqual(err_ptr.fromErrorCode(case.errno), raw);
        try testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
        try testing.expect(slot.isErr());
        try testing.expect(slot.isTaggedEntry());
        try testing.expectEqual(@as(?isize, case.errno), slot.errorCode());
    }
}

test "rejected alias slots keep value and pointer accessors closed" {
    for (alias_cases) |case| {
        const raw = rejectedAliasRaw(case.rejected_offset);
        const slot = xarray_slot_view.fromRaw(raw);

        try testing.expect(!slot.isNull());
        try testing.expect(!slot.isValue());
        try testing.expect(!slot.isPointer());
        try testing.expectEqual(@as(?usize, null), slot.value());
        try testing.expectEqual(@as(?usize, null), slot.pointerValue());
        try testing.expectEqual(raw, slot.rawValue());
    }
}

test "top rejected alias lands exactly on the top err_ptr code" {
    const top_rejected_value = rejectedAliasValue(2048);
    const top_alias_raw = rejectedAliasRaw(2048);
    const top_slot = xarray_slot_view.fromRaw(top_alias_raw);

    try testing.expect(!xa_value.canRepresent(top_rejected_value));
    try testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(top_rejected_value));
    try testing.expectEqual(err_ptr.fromErrorCode(-1), top_alias_raw);
    try testing.expectEqual(@as(?isize, -1), top_slot.errorCode());
    try testing.expectEqual(xarray_slot_view.fromErrorCode(-1).rawValue(), top_slot.rawValue());
}
