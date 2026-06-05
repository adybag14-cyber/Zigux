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

const PayloadCase = struct {
    raw: usize,
    kind: SlotKind,
    payload: ExpectedPayload,
};

fn rejectedValueRaw(offset: usize) usize {
    return ((xa_value.safe_inline_limit + 1 + offset) << 1) | xa_value.value_tag_mask;
}

fn expectPayloadSentinel(case: PayloadCase) !void {
    const slot = xarray_slot_view.fromRaw(case.raw);

    try std.testing.expectEqual(case.raw, slot.rawValue());
    try std.testing.expectEqual(case.kind, slot.kind());

    switch (case.payload) {
        .none => {
            try std.testing.expectEqual(@as(?usize, null), slot.value());
            try std.testing.expectEqual(@as(?isize, null), slot.errorCode());
            try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
        },
        .value => |expected| {
            try std.testing.expectEqual(@as(?usize, expected), slot.value());
            try std.testing.expectEqual(@as(?isize, null), slot.errorCode());
            try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
        },
        .err => |expected| {
            try std.testing.expectEqual(@as(?usize, null), slot.value());
            try std.testing.expectEqual(@as(?isize, expected), slot.errorCode());
            try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
        },
        .pointer => |expected| {
            try std.testing.expectEqual(@as(?usize, null), slot.value());
            try std.testing.expectEqual(@as(?isize, null), slot.errorCode());
            try std.testing.expectEqual(@as(?usize, expected), slot.pointerValue());
        },
    }
}

test "null and low raw lanes expose only their owning optional payload" {
    const cases = [_]PayloadCase{
        .{ .raw = 0, .kind = .null, .payload = .none },
        .{ .raw = 1, .kind = .value, .payload = .{ .value = 0 } },
        .{ .raw = 2, .kind = .pointer, .payload = .{ .pointer = 2 } },
        .{ .raw = 3, .kind = .value, .payload = .{ .value = 1 } },
        .{ .raw = 4, .kind = .pointer, .payload = .{ .pointer = 4 } },
    };

    for (cases) |case| {
        try expectPayloadSentinel(case);
    }
}

test "inline ceiling and pointer gap keep payload sentinels disjoint" {
    const ceiling_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const cases = [_]PayloadCase{
        .{
            .raw = ceiling_raw,
            .kind = .value,
            .payload = .{ .value = xa_value.safe_inline_limit },
        },
        .{
            .raw = err_ptr.err_floor - 1,
            .kind = .pointer,
            .payload = .{ .pointer = err_ptr.err_floor - 1 },
        },
        .{
            .raw = err_ptr.err_floor,
            .kind = .err,
            .payload = .{ .err = -@as(isize, @intCast(err_ptr.max_errno)) },
        },
    };

    try std.testing.expectEqual(err_ptr.err_floor - 2, ceiling_raw);

    for (cases) |case| {
        try expectPayloadSentinel(case);
    }
}

test "rejected xa_value aliases expose err payloads, not value payloads" {
    const cases = [_]PayloadCase{
        .{
            .raw = rejectedValueRaw(0),
            .kind = .err,
            .payload = .{ .err = -@as(isize, @intCast(err_ptr.max_errno)) },
        },
        .{
            .raw = rejectedValueRaw(1),
            .kind = .err,
            .payload = .{ .err = -@as(isize, @intCast(err_ptr.max_errno - 2)) },
        },
        .{
            .raw = err_ptr.fromErrorCode(-1),
            .kind = .err,
            .payload = .{ .err = -1 },
        },
    };

    try std.testing.expectEqual(err_ptr.err_floor, rejectedValueRaw(0));
    try std.testing.expectEqual(err_ptr.err_floor + 2, rejectedValueRaw(1));

    for (cases) |case| {
        try std.testing.expect(err_ptr.isErrValue(case.raw));
        try std.testing.expect(!xa_value.isValue(case.raw));
        try expectPayloadSentinel(case);
    }
}

test "constructor-created slots preserve optional payload sentinels after raw replay" {
    const value_slot = try xarray_slot_view.fromValue(37);
    const pointer_slot = xarray_slot_view.fromPointer(0x1000);
    const err_slot = xarray_slot_view.fromErrorCode(-22);

    const cases = [_]PayloadCase{
        .{ .raw = xarray_slot_view.nullSlot().rawValue(), .kind = .null, .payload = .none },
        .{ .raw = value_slot.rawValue(), .kind = .value, .payload = .{ .value = 37 } },
        .{ .raw = pointer_slot.rawValue(), .kind = .pointer, .payload = .{ .pointer = 0x1000 } },
        .{ .raw = err_slot.rawValue(), .kind = .err, .payload = .{ .err = -22 } },
    };

    for (cases) |case| {
        try expectPayloadSentinel(case);
    }
}
