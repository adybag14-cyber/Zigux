const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;

const Witness = struct {
    name: []const u8,
    raw: usize,
    kind: SlotKind,
    value: ?usize = null,
    errno: ?isize = null,
    pointer: ?usize = null,
    tagged: bool,
};

fn laneCount(slot: xarray_slot_view.SlotView) usize {
    return @intFromBool(slot.isNull()) +
        @intFromBool(slot.isValue()) +
        @intFromBool(slot.isErr()) +
        @intFromBool(slot.isPointer());
}

fn expectWitness(row: Witness) !void {
    const slot = xarray_slot_view.fromRaw(row.raw);

    try std.testing.expectEqual(row.kind, slot.kind());
    try std.testing.expectEqual(row.raw, slot.rawValue());
    try std.testing.expectEqual(@as(usize, 1), laneCount(slot));
    try std.testing.expectEqual(row.tagged, slot.isTaggedEntry());
    try std.testing.expectEqual(row.tagged, xarray_slot_view.isTaggedInternalEntry(row.raw));
    try std.testing.expectEqual(err_ptr.isErrValue(row.raw), slot.isErr());
    try std.testing.expectEqual(xa_value.isValue(row.raw), slot.isValue());
    try std.testing.expectEqual(row.value, slot.value());
    try std.testing.expectEqual(row.errno, slot.errorCode());
    try std.testing.expectEqual(row.pointer, slot.pointerValue());
}

test "mixed raw witness table keeps exactly one public xarray lane open" {
    const rows = [_]Witness{
        .{
            .name = "null",
            .raw = 0,
            .kind = .null,
            .tagged = false,
        },
        .{
            .name = "inline zero",
            .raw = try xa_value.makeValue(0),
            .kind = .value,
            .value = 0,
            .tagged = true,
        },
        .{
            .name = "inline mid",
            .raw = try xa_value.makeValue(313),
            .kind = .value,
            .value = 313,
            .tagged = true,
        },
        .{
            .name = "even pointer",
            .raw = 0x2000,
            .kind = .pointer,
            .pointer = 0x2000,
            .tagged = false,
        },
        .{
            .name = "near-floor pointer",
            .raw = err_ptr.err_floor - 1,
            .kind = .pointer,
            .pointer = err_ptr.err_floor - 1,
            .tagged = false,
        },
        .{
            .name = "err floor",
            .raw = err_ptr.err_floor,
            .kind = .err,
            .errno = -4095,
            .tagged = true,
        },
        .{
            .name = "interior errno",
            .raw = err_ptr.fromErrorCode(-313),
            .kind = .err,
            .errno = -313,
            .tagged = true,
        },
        .{
            .name = "top errno",
            .raw = err_ptr.fromErrorCode(-1),
            .kind = .err,
            .errno = -1,
            .tagged = true,
        },
    };

    for (rows) |row| {
        errdefer std.debug.print("failed witness row: {s}\n", .{row.name});
        try expectWitness(row);
    }
}

test "constructor witness rows match raw reread rows" {
    const value_slot = try xarray_slot_view.fromValue(313);
    const err_slot = xarray_slot_view.fromErrorCode(-313);
    const pointer_slot = xarray_slot_view.fromPointer(0x2000);

    try expectWitness(.{
        .name = "constructed value",
        .raw = value_slot.rawValue(),
        .kind = .value,
        .value = 313,
        .tagged = true,
    });
    try expectWitness(.{
        .name = "constructed errno",
        .raw = err_slot.rawValue(),
        .kind = .err,
        .errno = -313,
        .tagged = true,
    });
    try expectWitness(.{
        .name = "constructed pointer",
        .raw = pointer_slot.rawValue(),
        .kind = .pointer,
        .pointer = 0x2000,
        .tagged = false,
    });
}
