const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const RejectedPointerCase = struct {
    name: []const u8,
    raw: usize,
    expected_kind: xarray_slot_view.SlotKind,
    expected_error: ?isize = null,
    expected_value: ?usize = null,
};

fn expectRejectedPointerCase(case: RejectedPointerCase) !void {
    try std.testing.expect(
        xarray_slot_view.isTaggedInternalEntry(case.raw),
    );

    const slot = xarray_slot_view.fromRaw(case.raw);
    try std.testing.expectEqual(case.expected_kind, slot.kind());
    try std.testing.expectEqual(case.expected_error, slot.errorCode());
    try std.testing.expectEqual(case.expected_value, slot.value());
    try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
    try std.testing.expect(
        case.name.len != 0,
    );
}

test "pointer constructor rejection inputs decode as internal tagged slots" {
    const cases = [_]RejectedPointerCase{
        .{
            .name = "inline zero xa_value tag",
            .raw = try xa_value.makeValue(0),
            .expected_kind = .value,
            .expected_value = 0,
        },
        .{
            .name = "highest accepted xa_value tag",
            .raw = try xa_value.makeValue(xa_value.safe_inline_limit),
            .expected_kind = .value,
            .expected_value = xa_value.safe_inline_limit,
        },
        .{
            .name = "err_ptr floor tag",
            .raw = err_ptr.err_floor,
            .expected_kind = .err,
            .expected_error = -4095,
        },
        .{
            .name = "top err_ptr tag",
            .raw = err_ptr.fromErrorCode(-1),
            .expected_kind = .err,
            .expected_error = -1,
        },
    };

    for (cases) |case| {
        try expectRejectedPointerCase(case);
    }
}

test "pointer constructor accepted neighbors stay outside internal tag space" {
    const accepted_pointer_raws = [_]usize{
        0x2,
        0x1000,
        err_ptr.err_floor - 1,
    };

    for (accepted_pointer_raws) |raw| {
        try std.testing.expect(!xarray_slot_view.isTaggedInternalEntry(raw));
        const slot = xarray_slot_view.fromPointer(raw);
        try std.testing.expectEqual(xarray_slot_view.SlotKind.pointer, slot.kind());
        try std.testing.expectEqual(raw, slot.rawValue());
        try std.testing.expectEqual(@as(?usize, raw), slot.pointerValue());
        try std.testing.expectEqual(@as(?usize, null), slot.value());
        try std.testing.expectEqual(@as(?isize, null), slot.errorCode());
    }
}

test "first rejected xa_value alias is not pointer-admissible" {
    const overlapping_value = xa_value.safe_inline_limit + 1;
    const overlapping_raw = (overlapping_value << 1) | xa_value.value_tag_mask;

    try std.testing.expectEqual(err_ptr.err_floor, overlapping_raw);
    try std.testing.expectError(
        error.ValueWouldOverlapErrPtr,
        xa_value.makeValue(overlapping_value),
    );
    try expectRejectedPointerCase(.{
        .name = "first rejected xa_value aliases err floor",
        .raw = overlapping_raw,
        .expected_kind = .err,
        .expected_error = -4095,
    });
}
