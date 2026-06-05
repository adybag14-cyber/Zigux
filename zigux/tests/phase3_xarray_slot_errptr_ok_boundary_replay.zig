const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;

const BoundaryCase = struct {
    name: []const u8,
    raw: usize,
    kind: SlotKind,
    value: ?usize = null,
    err: ?isize = null,
    pointer: ?usize = null,
};

fn expectOkBoundary(case: BoundaryCase) !void {
    const slot = xarray_slot_view.fromRaw(case.raw);
    const ok_value = err_ptr.isOkValue(case.raw);

    errdefer std.debug.print("err_ptr ok boundary case failed: {s}\n", .{case.name});

    try std.testing.expectEqual(case.kind, slot.kind());
    try std.testing.expectEqual(case.kind != .err, ok_value);
    try std.testing.expectEqual(!ok_value, err_ptr.isErrValue(case.raw));
    try std.testing.expectEqual(case.kind == .err, slot.isErr());
    try std.testing.expectEqual(case.kind == .value, slot.isValue());
    try std.testing.expectEqual(case.kind == .pointer, slot.isPointer());
    try std.testing.expectEqual(case.kind == .null, slot.isNull());
    try std.testing.expectEqual(case.value, slot.value());
    try std.testing.expectEqual(case.err, slot.errorCode());
    try std.testing.expectEqual(case.pointer, slot.pointerValue());
}

test "err_ptr ok boundary matches xarray slot error decoding" {
    const inline_zero = try xa_value.makeValue(0);
    const inline_tail = try xa_value.makeValue(xa_value.safe_inline_limit);
    const pointer_gap = err_ptr.err_floor - 1;
    const err_floor = err_ptr.err_floor;
    const interior_err = err_floor + 2;
    const top_err = err_ptr.fromErrorCode(-1);

    const cases = [_]BoundaryCase{
        .{ .name = "null is ok but not a pointer", .raw = 0, .kind = .null },
        .{ .name = "inline zero is ok value", .raw = inline_zero, .kind = .value, .value = 0 },
        .{
            .name = "inline tail is ok value",
            .raw = inline_tail,
            .kind = .value,
            .value = xa_value.safe_inline_limit,
        },
        .{
            .name = "gap below err floor is ok pointer",
            .raw = pointer_gap,
            .kind = .pointer,
            .pointer = pointer_gap,
        },
        .{ .name = "err floor is not ok", .raw = err_floor, .kind = .err, .err = -4095 },
        .{ .name = "interior err raw is not ok", .raw = interior_err, .kind = .err, .err = -4093 },
        .{ .name = "top err raw is not ok", .raw = top_err, .kind = .err, .err = -1 },
    };

    for (cases) |case| {
        try expectOkBoundary(case);
    }
}

test "rejected inline aliases stay on the err side of the ok boundary" {
    const rejected_values = [_]usize{
        xa_value.safe_inline_limit + 1,
        xa_value.safe_inline_limit + 2,
        xa_value.safe_inline_limit + 128,
        xa_value.safe_inline_limit + 2047,
    };

    for (rejected_values) |value| {
        const raw = (value << 1) | xa_value.value_tag_mask;
        const slot = xarray_slot_view.fromRaw(raw);

        try std.testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(value));
        try std.testing.expect(!err_ptr.isOkValue(raw));
        try std.testing.expect(slot.isErr());
        try std.testing.expectEqual(@as(?usize, null), slot.value());
        try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
        try std.testing.expect(slot.errorCode().? <= -1);
        try std.testing.expect(slot.errorCode().? >= -@as(isize, @intCast(err_ptr.max_errno)));
        try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
    }
}
