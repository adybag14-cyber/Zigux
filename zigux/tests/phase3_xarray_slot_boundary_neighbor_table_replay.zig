const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;

const BoundaryNeighbor = struct {
    name: []const u8,
    raw: usize,
    kind: SlotKind,
    tagged: bool,
    value: ?usize = null,
    error_code: ?isize = null,
    pointer: ?usize = null,
};

fn expectNeighbor(row: BoundaryNeighbor) !void {
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
    try std.testing.expectEqual(row.error_code, slot.errorCode());
    try std.testing.expectEqual(row.pointer, slot.pointerValue());
}

test "boundary neighbor table keeps xarray slot lane edges explicit" {
    const rows = [_]BoundaryNeighbor{
        .{
            .name = "null raw",
            .raw = 0,
            .kind = .null,
            .tagged = false,
        },
        .{
            .name = "first inline value",
            .raw = try xa_value.makeValue(0),
            .kind = .value,
            .tagged = true,
            .value = 0,
        },
        .{
            .name = "small pointer gap",
            .raw = 2,
            .kind = .pointer,
            .tagged = false,
            .pointer = 2,
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
            .name = "err floor",
            .raw = err_ptr.err_floor,
            .kind = .err,
            .tagged = true,
            .error_code = -@as(isize, @intCast(err_ptr.max_errno)),
        },
        .{
            .name = "err floor neighbor",
            .raw = err_ptr.fromErrorCode(-4094),
            .kind = .err,
            .tagged = true,
            .error_code = -4094,
        },
        .{
            .name = "middle errno",
            .raw = err_ptr.fromErrorCode(-512),
            .kind = .err,
            .tagged = true,
            .error_code = -512,
        },
        .{
            .name = "top errno",
            .raw = err_ptr.fromErrorCode(-1),
            .kind = .err,
            .tagged = true,
            .error_code = -1,
        },
    };

    for (rows) |row| {
        try expectNeighbor(row);
    }
}

test "first rejected inline alias lands on the err floor neighbor contract" {
    const rejected_value = xa_value.safe_inline_limit + 1;
    const alias_raw = (rejected_value << 1) | xa_value.value_tag_mask;
    const alias_slot = xarray_slot_view.fromRaw(alias_raw);

    try std.testing.expect(!xa_value.canRepresent(rejected_value));
    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(rejected_value));
    try std.testing.expectEqual(err_ptr.err_floor, alias_raw);
    try std.testing.expectEqual(SlotKind.err, alias_slot.kind());
    try std.testing.expect(alias_slot.isErr());
    try std.testing.expect(alias_slot.isTaggedEntry());
    try std.testing.expectEqual(@as(?isize, -4095), alias_slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), alias_slot.value());
    try std.testing.expectEqual(@as(?usize, null), alias_slot.pointerValue());
}

test "public constructors match the same boundary neighbor table" {
    const constructors = [_]BoundaryNeighbor{
        .{
            .name = "constructor null",
            .raw = xarray_slot_view.nullSlot().rawValue(),
            .kind = .null,
            .tagged = false,
        },
        .{
            .name = "constructor highest inline value",
            .raw = (try xarray_slot_view.fromValue(xa_value.safe_inline_limit)).rawValue(),
            .kind = .value,
            .tagged = true,
            .value = xa_value.safe_inline_limit,
        },
        .{
            .name = "constructor pointer",
            .raw = xarray_slot_view.fromPointer(err_ptr.err_floor - 1).rawValue(),
            .kind = .pointer,
            .tagged = false,
            .pointer = err_ptr.err_floor - 1,
        },
        .{
            .name = "constructor err floor",
            .raw = xarray_slot_view.fromErrorCode(-4095).rawValue(),
            .kind = .err,
            .tagged = true,
            .error_code = -4095,
        },
        .{
            .name = "constructor top errno",
            .raw = xarray_slot_view.fromErrorCode(-1).rawValue(),
            .kind = .err,
            .tagged = true,
            .error_code = -1,
        },
    };

    for (constructors) |row| {
        try expectNeighbor(row);
    }
}
