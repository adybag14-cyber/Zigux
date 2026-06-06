const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;

const MirrorRow = struct {
    name: []const u8,
    raw: usize,
    kind: SlotKind,
    value: ?usize = null,
    error_code: ?isize = null,
    pointer: ?usize = null,
};

fn uncheckedInlineRaw(value: usize) usize {
    return (value << 1) | xa_value.value_tag_mask;
}

fn expectMirror(row: MirrorRow) !void {
    const slot = xarray_slot_view.fromRaw(row.raw);

    try std.testing.expectEqual(row.raw, slot.rawValue());
    try std.testing.expectEqual(row.kind, slot.kind());

    const expected_is_null = row.raw == 0;
    const expected_is_err = err_ptr.isErrValue(row.raw);
    const expected_is_value = xa_value.isValue(row.raw);
    const expected_is_pointer = !expected_is_null and !expected_is_err and !expected_is_value;
    const expected_is_tagged = expected_is_err or expected_is_value;

    try std.testing.expectEqual(expected_is_null, slot.isNull());
    try std.testing.expectEqual(expected_is_value, slot.isValue());
    try std.testing.expectEqual(expected_is_err, slot.isErr());
    try std.testing.expectEqual(expected_is_pointer, slot.isPointer());
    try std.testing.expectEqual(expected_is_tagged, slot.isTaggedEntry());
    try std.testing.expectEqual(expected_is_tagged, xarray_slot_view.isTaggedInternalEntry(row.raw));

    try std.testing.expectEqual(row.value, slot.value());
    try std.testing.expectEqual(row.error_code, slot.errorCode());
    try std.testing.expectEqual(row.pointer, slot.pointerValue());

    if (row.value) |value| {
        try std.testing.expectEqual(value, xa_value.toValue(row.raw));
    }
    if (row.error_code) |code| {
        try std.testing.expectEqual(code, err_ptr.toErrorCode(row.raw));
    }
    if (row.pointer) |pointer| {
        try std.testing.expectEqual(pointer, row.raw);
    }
}

test "raw slot predicates mirror helper predicates and optional accessors" {
    const inline_mid = @as(usize, 29);
    const rejected_first = xa_value.safe_inline_limit + 1;
    const rejected_next = xa_value.safe_inline_limit + 2;

    const rows = [_]MirrorRow{
        .{
            .name = "null",
            .raw = 0,
            .kind = .null,
        },
        .{
            .name = "inline zero",
            .raw = try xa_value.makeValue(0),
            .kind = .value,
            .value = 0,
        },
        .{
            .name = "inline middle",
            .raw = try xa_value.makeValue(inline_mid),
            .kind = .value,
            .value = inline_mid,
        },
        .{
            .name = "inline ceiling",
            .raw = try xa_value.makeValue(xa_value.safe_inline_limit),
            .kind = .value,
            .value = xa_value.safe_inline_limit,
        },
        .{
            .name = "ordinary pointer",
            .raw = 0x1000,
            .kind = .pointer,
            .pointer = 0x1000,
        },
        .{
            .name = "last pointer gap",
            .raw = err_ptr.err_floor - 1,
            .kind = .pointer,
            .pointer = err_ptr.err_floor - 1,
        },
        .{
            .name = "err floor",
            .raw = err_ptr.err_floor,
            .kind = .err,
            .error_code = -4095,
        },
        .{
            .name = "interior errno",
            .raw = err_ptr.fromErrorCode(-2048),
            .kind = .err,
            .error_code = -2048,
        },
        .{
            .name = "top errno",
            .raw = err_ptr.fromErrorCode(-1),
            .kind = .err,
            .error_code = -1,
        },
        .{
            .name = "first rejected inline alias",
            .raw = uncheckedInlineRaw(rejected_first),
            .kind = .err,
            .error_code = -4095,
        },
        .{
            .name = "next rejected inline alias",
            .raw = uncheckedInlineRaw(rejected_next),
            .kind = .err,
            .error_code = -4093,
        },
    };

    for (rows) |row| {
        errdefer std.debug.print("xarray mirror row failed: {s}\n", .{row.name});
        try expectMirror(row);
    }
}

test "public constructors project into the same mirror rows" {
    const constructed = [_]MirrorRow{
        .{
            .name = "constructed null",
            .raw = xarray_slot_view.nullSlot().rawValue(),
            .kind = .null,
        },
        .{
            .name = "constructed value",
            .raw = (try xarray_slot_view.fromValue(29)).rawValue(),
            .kind = .value,
            .value = 29,
        },
        .{
            .name = "constructed pointer",
            .raw = xarray_slot_view.fromPointer(0x2000).rawValue(),
            .kind = .pointer,
            .pointer = 0x2000,
        },
        .{
            .name = "constructed err",
            .raw = xarray_slot_view.fromErrorCode(-22).rawValue(),
            .kind = .err,
            .error_code = -22,
        },
    };

    for (constructed) |row| {
        errdefer std.debug.print("constructed xarray mirror row failed: {s}\n", .{row.name});
        try expectMirror(row);
    }
}
