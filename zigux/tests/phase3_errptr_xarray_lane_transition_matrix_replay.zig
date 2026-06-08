const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;

const LaneRow = struct {
    name: []const u8,
    raw: usize,
    kind: SlotKind,
    tagged: bool,
    value: ?usize = null,
    pointer: ?usize = null,
    errno: ?isize = null,
};

fn expectLane(row: LaneRow) !void {
    const slot = xarray_slot_view.fromRaw(row.raw);

    try std.testing.expectEqual(row.raw, slot.rawValue());
    try std.testing.expectEqual(row.kind, slot.kind());
    try std.testing.expectEqual(row.kind == .null, slot.isNull());
    try std.testing.expectEqual(row.kind == .value, slot.isValue());
    try std.testing.expectEqual(row.kind == .err, slot.isErr());
    try std.testing.expectEqual(row.kind == .pointer, slot.isPointer());
    try std.testing.expectEqual(row.tagged, slot.isTaggedEntry());
    try std.testing.expectEqual(row.tagged, xarray_slot_view.isTaggedInternalEntry(row.raw));
    try std.testing.expectEqual(row.value, slot.value());
    try std.testing.expectEqual(row.pointer, slot.pointerValue());
    try std.testing.expectEqual(row.errno, slot.errorCode());
}

test "phase3 errptr xarray lane transition matrix keeps adjacent raw lanes exclusive" {
    const rows = [_]LaneRow{
        .{
            .name = "null sentinel",
            .raw = 0,
            .kind = .null,
            .tagged = false,
        },
        .{
            .name = "inline zero",
            .raw = try xa_value.makeValue(0),
            .kind = .value,
            .tagged = true,
            .value = 0,
        },
        .{
            .name = "first even pointer lane",
            .raw = 2,
            .kind = .pointer,
            .tagged = false,
            .pointer = 2,
        },
        .{
            .name = "small inline value",
            .raw = try xa_value.makeValue(1),
            .kind = .value,
            .tagged = true,
            .value = 1,
        },
        .{
            .name = "highest inline value",
            .raw = try xa_value.makeValue(xa_value.safe_inline_limit),
            .kind = .value,
            .tagged = true,
            .value = xa_value.safe_inline_limit,
        },
        .{
            .name = "last pointer before err floor",
            .raw = err_ptr.err_floor - 1,
            .kind = .pointer,
            .tagged = false,
            .pointer = err_ptr.err_floor - 1,
        },
        .{
            .name = "first errno lane",
            .raw = err_ptr.err_floor,
            .kind = .err,
            .tagged = true,
            .errno = -@as(isize, @intCast(err_ptr.max_errno)),
        },
        .{
            .name = "middle odd errno lane",
            .raw = err_ptr.fromErrorCode(-255),
            .kind = .err,
            .tagged = true,
            .errno = -255,
        },
        .{
            .name = "top errno lane",
            .raw = err_ptr.fromErrorCode(-1),
            .kind = .err,
            .tagged = true,
            .errno = -1,
        },
    };

    for (rows) |row| {
        try expectLane(row);
    }
}

test "phase3 errptr xarray lane transition matrix preserves constructor raw rereads" {
    const value_slot = try xarray_slot_view.fromValue(xa_value.safe_inline_limit);
    const pointer_slot = xarray_slot_view.fromPointer(0x4000);
    const err_slot = xarray_slot_view.fromErrorCode(-255);

    try expectLane(.{
        .name = "value constructor reread",
        .raw = value_slot.rawValue(),
        .kind = .value,
        .tagged = true,
        .value = xa_value.safe_inline_limit,
    });
    try expectLane(.{
        .name = "pointer constructor reread",
        .raw = pointer_slot.rawValue(),
        .kind = .pointer,
        .tagged = false,
        .pointer = 0x4000,
    });
    try expectLane(.{
        .name = "errno constructor reread",
        .raw = err_slot.rawValue(),
        .kind = .err,
        .tagged = true,
        .errno = -255,
    });
}
