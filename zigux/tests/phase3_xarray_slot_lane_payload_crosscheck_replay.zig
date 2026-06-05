const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;

const ExpectedPayload = union(enum) {
    none,
    value: usize,
    err: isize,
    pointer: usize,
};

const Case = struct {
    name: []const u8,
    raw: usize,
    kind: SlotKind,
    payload: ExpectedPayload,
    tagged: bool,
};

fn expectSlot(case: Case) !void {
    const slot = xarray_slot_view.fromRaw(case.raw);

    try std.testing.expectEqual(case.raw, slot.rawValue());
    try std.testing.expectEqual(case.kind, slot.kind());
    try std.testing.expectEqual(case.kind == .null, slot.isNull());
    try std.testing.expectEqual(case.kind == .value, slot.isValue());
    try std.testing.expectEqual(case.kind == .err, slot.isErr());
    try std.testing.expectEqual(case.kind == .pointer, slot.isPointer());
    try std.testing.expectEqual(case.tagged, slot.isTaggedEntry());

    switch (case.payload) {
        .none => {
            try std.testing.expectEqual(@as(?usize, null), slot.value());
            try std.testing.expectEqual(@as(?isize, null), slot.errorCode());
            try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
        },
        .value => |payload| {
            try std.testing.expectEqual(@as(?usize, payload), slot.value());
            try std.testing.expectEqual(@as(?isize, null), slot.errorCode());
            try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
        },
        .err => |payload| {
            try std.testing.expectEqual(@as(?usize, null), slot.value());
            try std.testing.expectEqual(@as(?isize, payload), slot.errorCode());
            try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
        },
        .pointer => |payload| {
            try std.testing.expectEqual(@as(?usize, null), slot.value());
            try std.testing.expectEqual(@as(?isize, null), slot.errorCode());
            try std.testing.expectEqual(@as(?usize, payload), slot.pointerValue());
        },
    }
}

test "representative raw slots expose exactly their owning lane payload" {
    const inline_zero_raw = try xa_value.makeValue(0);
    const inline_mid_payload = @as(usize, 73);
    const inline_mid_raw = try xa_value.makeValue(inline_mid_payload);
    const inline_ceiling_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const pointer_gap_raw = err_ptr.err_floor - 1;
    const aligned_pointer_raw = @as(usize, 0x4000);
    const err_floor_raw = err_ptr.err_floor;
    const interior_err_raw = err_ptr.fromErrorCode(-123);
    const top_err_raw = err_ptr.fromErrorCode(-1);

    const cases = [_]Case{
        .{
            .name = "null raw",
            .raw = 0,
            .kind = .null,
            .payload = .none,
            .tagged = false,
        },
        .{
            .name = "inline zero",
            .raw = inline_zero_raw,
            .kind = .value,
            .payload = .{ .value = 0 },
            .tagged = true,
        },
        .{
            .name = "inline middle value",
            .raw = inline_mid_raw,
            .kind = .value,
            .payload = .{ .value = inline_mid_payload },
            .tagged = true,
        },
        .{
            .name = "inline ceiling value",
            .raw = inline_ceiling_raw,
            .kind = .value,
            .payload = .{ .value = xa_value.safe_inline_limit },
            .tagged = true,
        },
        .{
            .name = "gap below err floor",
            .raw = pointer_gap_raw,
            .kind = .pointer,
            .payload = .{ .pointer = pointer_gap_raw },
            .tagged = false,
        },
        .{
            .name = "aligned pointer",
            .raw = aligned_pointer_raw,
            .kind = .pointer,
            .payload = .{ .pointer = aligned_pointer_raw },
            .tagged = false,
        },
        .{
            .name = "err floor",
            .raw = err_floor_raw,
            .kind = .err,
            .payload = .{ .err = -@as(isize, @intCast(err_ptr.max_errno)) },
            .tagged = true,
        },
        .{
            .name = "interior errno",
            .raw = interior_err_raw,
            .kind = .err,
            .payload = .{ .err = -123 },
            .tagged = true,
        },
        .{
            .name = "top errno",
            .raw = top_err_raw,
            .kind = .err,
            .payload = .{ .err = -1 },
            .tagged = true,
        },
    };

    for (cases) |case| {
        errdefer std.debug.print("failed slot case: {s}\n", .{case.name});
        try expectSlot(case);
    }
}

test "public constructors agree with raw payload ownership" {
    const null_slot = xarray_slot_view.nullSlot();
    const value_slot = try xarray_slot_view.fromValue(73);
    const pointer_slot = xarray_slot_view.fromPointer(0x4000);
    const err_slot = xarray_slot_view.fromErrorCode(-123);

    try expectSlot(.{
        .name = "null constructor",
        .raw = null_slot.rawValue(),
        .kind = .null,
        .payload = .none,
        .tagged = false,
    });
    try expectSlot(.{
        .name = "value constructor",
        .raw = value_slot.rawValue(),
        .kind = .value,
        .payload = .{ .value = 73 },
        .tagged = true,
    });
    try expectSlot(.{
        .name = "pointer constructor",
        .raw = pointer_slot.rawValue(),
        .kind = .pointer,
        .payload = .{ .pointer = 0x4000 },
        .tagged = false,
    });
    try expectSlot(.{
        .name = "err constructor",
        .raw = err_slot.rawValue(),
        .kind = .err,
        .payload = .{ .err = -123 },
        .tagged = true,
    });
}

test "first rejected inline alias is owned by the err lane" {
    const rejected_payload = xa_value.safe_inline_limit + 1;
    const rejected_raw = (rejected_payload << 1) | xa_value.value_tag_mask;

    try std.testing.expectError(
        error.ValueWouldOverlapErrPtr,
        xarray_slot_view.fromValue(rejected_payload),
    );
    try std.testing.expectEqual(err_ptr.err_floor, rejected_raw);
    try expectSlot(.{
        .name = "first rejected inline alias",
        .raw = rejected_raw,
        .kind = .err,
        .payload = .{ .err = -@as(isize, @intCast(err_ptr.max_errno)) },
        .tagged = true,
    });
}
