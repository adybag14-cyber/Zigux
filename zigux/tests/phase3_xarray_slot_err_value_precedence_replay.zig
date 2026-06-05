const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const BoundaryCase = struct {
    label: []const u8,
    raw: usize,
    expected_kind: xarray_slot_view.SlotKind,
    expected_value: ?usize,
    expected_error: ?isize,
    expected_pointer: ?usize,
    expected_tagged: bool,
};

fn expectBoundary(case: BoundaryCase) !void {
    const slot = xarray_slot_view.fromRaw(case.raw);

    errdefer std.debug.print("failed xarray err/value boundary case: {s}\n", .{case.label});

    try std.testing.expectEqual(case.raw, slot.rawValue());
    try std.testing.expectEqual(case.expected_kind, slot.kind());
    try std.testing.expectEqual(case.expected_tagged, slot.isTaggedEntry());
    try std.testing.expectEqual(case.expected_tagged, xarray_slot_view.isTaggedInternalEntry(case.raw));
    try std.testing.expectEqual(case.expected_value, slot.value());
    try std.testing.expectEqual(case.expected_error, slot.errorCode());
    try std.testing.expectEqual(case.expected_pointer, slot.pointerValue());

    try std.testing.expectEqual(case.expected_kind == .value, xa_value.isValue(case.raw));
    try std.testing.expectEqual(case.expected_kind == .err, err_ptr.isErrValue(case.raw));
}

test "xarray slot keeps value lane closed at every err_ptr boundary" {
    const safe_tail_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const rejected_tail_value = xa_value.safe_inline_limit + 1;
    const rejected_tail_raw = (rejected_tail_value << 1) | xa_value.value_tag_mask;
    const errno_mid = -@as(isize, 2048);

    try std.testing.expectEqual(err_ptr.err_floor - 2, safe_tail_raw);
    try std.testing.expectEqual(err_ptr.err_floor, rejected_tail_raw);
    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(rejected_tail_value));

    const cases = [_]BoundaryCase{
        .{
            .label = "highest safe inline value",
            .raw = safe_tail_raw,
            .expected_kind = .value,
            .expected_value = xa_value.safe_inline_limit,
            .expected_error = null,
            .expected_pointer = null,
            .expected_tagged = true,
        },
        .{
            .label = "odd pointer gap below err floor",
            .raw = err_ptr.err_floor - 1,
            .expected_kind = .pointer,
            .expected_value = null,
            .expected_error = null,
            .expected_pointer = err_ptr.err_floor - 1,
            .expected_tagged = false,
        },
        .{
            .label = "rejected inline raw aliases err floor",
            .raw = rejected_tail_raw,
            .expected_kind = .err,
            .expected_value = null,
            .expected_error = -4095,
            .expected_pointer = null,
            .expected_tagged = true,
        },
        .{
            .label = "middle errno keeps low-bit precedence closed",
            .raw = err_ptr.fromErrorCode(errno_mid),
            .expected_kind = .err,
            .expected_value = null,
            .expected_error = errno_mid,
            .expected_pointer = null,
            .expected_tagged = true,
        },
        .{
            .label = "top errno has value tag bit but stays err",
            .raw = err_ptr.fromErrorCode(-1),
            .expected_kind = .err,
            .expected_value = null,
            .expected_error = -1,
            .expected_pointer = null,
            .expected_tagged = true,
        },
    };

    for (cases) |case| {
        try expectBoundary(case);
    }
}

test "constructor paths preserve the same err before value decoder ordering" {
    const value_slot = try xarray_slot_view.fromValue(xa_value.safe_inline_limit);
    const err_floor_slot = xarray_slot_view.fromErrorCode(-4095);
    const top_err_slot = xarray_slot_view.fromErrorCode(-1);

    try std.testing.expectEqual(xarray_slot_view.SlotKind.value, value_slot.kind());
    try std.testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), value_slot.value());
    try std.testing.expectEqual(@as(?isize, null), value_slot.errorCode());

    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, err_floor_slot.kind());
    try std.testing.expectEqual(@as(?usize, null), err_floor_slot.value());
    try std.testing.expectEqual(@as(?isize, -4095), err_floor_slot.errorCode());

    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, top_err_slot.kind());
    try std.testing.expectEqual(@as(?usize, null), top_err_slot.value());
    try std.testing.expectEqual(@as(?isize, -1), top_err_slot.errorCode());
}
