const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot = @import("xarray_slot_view");

const SlotKind = xarray_slot.SlotKind;
const SlotView = xarray_slot.SlotView;

const Case = struct {
    name: []const u8,
    slot: SlotView,
    kind: SlotKind,
    value: ?usize = null,
    pointer: ?usize = null,
    errno: ?isize = null,
};

fn expectClosed(case: Case) !void {
    const reread = xarray_slot.fromRaw(case.slot.rawValue());

    try std.testing.expectEqual(case.slot.rawValue(), reread.rawValue());
    try std.testing.expectEqual(case.kind, case.slot.kind());
    try std.testing.expectEqual(case.kind, reread.kind());
    try std.testing.expectEqual(case.value, reread.value());
    try std.testing.expectEqual(case.pointer, reread.pointerValue());
    try std.testing.expectEqual(case.errno, reread.errorCode());

    const payload_count: usize =
        @as(usize, if (reread.value() != null) 1 else 0) +
        @as(usize, if (reread.pointerValue() != null) 1 else 0) +
        @as(usize, if (reread.errorCode() != null) 1 else 0);

    switch (case.kind) {
        .null => try std.testing.expectEqual(@as(usize, 0), payload_count),
        .value, .pointer, .err => try std.testing.expectEqual(@as(usize, 1), payload_count),
    }
}

test "public constructors stay lane-closed after raw xarray reread" {
    const rows = [_]Case{
        .{
            .name = "null constructor",
            .slot = xarray_slot.nullSlot(),
            .kind = .null,
        },
        .{
            .name = "inline zero constructor",
            .slot = try xarray_slot.fromValue(0),
            .kind = .value,
            .value = 0,
        },
        .{
            .name = "safe inline ceiling constructor",
            .slot = try xarray_slot.fromValue(xa_value.safe_inline_limit),
            .kind = .value,
            .value = xa_value.safe_inline_limit,
        },
        .{
            .name = "ordinary pointer constructor",
            .slot = xarray_slot.fromPointer(0x1000),
            .kind = .pointer,
            .pointer = 0x1000,
        },
        .{
            .name = "last pointer gap constructor",
            .slot = xarray_slot.fromPointer(err_ptr.err_floor - 1),
            .kind = .pointer,
            .pointer = err_ptr.err_floor - 1,
        },
        .{
            .name = "err floor constructor",
            .slot = xarray_slot.fromErrorCode(-@as(isize, @intCast(err_ptr.max_errno))),
            .kind = .err,
            .errno = -@as(isize, @intCast(err_ptr.max_errno)),
        },
        .{
            .name = "interior errno constructor",
            .slot = xarray_slot.fromErrorCode(-512),
            .kind = .err,
            .errno = -512,
        },
        .{
            .name = "top errno constructor",
            .slot = xarray_slot.fromErrorCode(-1),
            .kind = .err,
            .errno = -1,
        },
    };

    for (rows) |row| {
        try std.testing.expect(row.name.len > 0);
        try expectClosed(row);
    }
}

test "constructor boundary keeps value pointer and error lanes adjacent but distinct" {
    const value_slot = try xarray_slot.fromValue(xa_value.safe_inline_limit);
    const pointer_slot = xarray_slot.fromPointer(err_ptr.err_floor - 1);
    const err_slot = xarray_slot.fromErrorCode(-@as(isize, @intCast(err_ptr.max_errno)));

    try std.testing.expectEqual(err_ptr.err_floor - 2, value_slot.rawValue());
    try std.testing.expectEqual(err_ptr.err_floor - 1, pointer_slot.rawValue());
    try std.testing.expectEqual(err_ptr.err_floor, err_slot.rawValue());

    try expectClosed(.{
        .name = "ceiling value",
        .slot = value_slot,
        .kind = .value,
        .value = xa_value.safe_inline_limit,
    });
    try expectClosed(.{
        .name = "gap pointer",
        .slot = pointer_slot,
        .kind = .pointer,
        .pointer = err_ptr.err_floor - 1,
    });
    try expectClosed(.{
        .name = "floor error",
        .slot = err_slot,
        .kind = .err,
        .errno = -@as(isize, @intCast(err_ptr.max_errno)),
    });
}

test "first rejected inline constructor alias remains an error raw" {
    const rejected_value = xa_value.safe_inline_limit + 1;
    const alias_raw = (rejected_value << 1) | xa_value.value_tag_mask;
    const alias_slot = xarray_slot.fromRaw(alias_raw);

    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot.fromValue(rejected_value));
    try std.testing.expectEqual(err_ptr.err_floor, alias_raw);
    try std.testing.expectEqual(SlotKind.err, alias_slot.kind());
    try std.testing.expectEqual(@as(?isize, -@as(isize, @intCast(err_ptr.max_errno))), alias_slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), alias_slot.value());
    try std.testing.expectEqual(@as(?usize, null), alias_slot.pointerValue());
}
