const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;
const SlotView = xarray_slot_view.SlotView;

const ParityRow = struct {
    name: []const u8,
    constructed: SlotView,
    kind: SlotKind,
    tagged: bool,
    value: ?usize = null,
    error_code: ?isize = null,
    pointer: ?usize = null,
};

fn expectConstructedRawParity(row: ParityRow) !void {
    const raw_view = xarray_slot_view.fromRaw(row.constructed.rawValue());

    try std.testing.expectEqual(row.constructed.rawValue(), raw_view.rawValue());
    try std.testing.expectEqual(row.kind, row.constructed.kind());
    try std.testing.expectEqual(row.kind, raw_view.kind());
    try std.testing.expectEqual(row.kind == .null, raw_view.isNull());
    try std.testing.expectEqual(row.kind == .value, raw_view.isValue());
    try std.testing.expectEqual(row.kind == .err, raw_view.isErr());
    try std.testing.expectEqual(row.kind == .pointer, raw_view.isPointer());
    try std.testing.expectEqual(row.tagged, row.constructed.isTaggedEntry());
    try std.testing.expectEqual(row.tagged, raw_view.isTaggedEntry());
    try std.testing.expectEqual(row.value, row.constructed.value());
    try std.testing.expectEqual(row.value, raw_view.value());
    try std.testing.expectEqual(row.error_code, row.constructed.errorCode());
    try std.testing.expectEqual(row.error_code, raw_view.errorCode());
    try std.testing.expectEqual(row.pointer, row.constructed.pointerValue());
    try std.testing.expectEqual(row.pointer, raw_view.pointerValue());
}

test "xarray slot constructors reclassify identically through raw views" {
    const rows = [_]ParityRow{
        .{
            .name = "null constructor",
            .constructed = xarray_slot_view.nullSlot(),
            .kind = .null,
            .tagged = false,
        },
        .{
            .name = "inline zero constructor",
            .constructed = try xarray_slot_view.fromValue(0),
            .kind = .value,
            .tagged = true,
            .value = 0,
        },
        .{
            .name = "highest inline constructor",
            .constructed = try xarray_slot_view.fromValue(xa_value.safe_inline_limit),
            .kind = .value,
            .tagged = true,
            .value = xa_value.safe_inline_limit,
        },
        .{
            .name = "small pointer constructor",
            .constructed = xarray_slot_view.fromPointer(2),
            .kind = .pointer,
            .tagged = false,
            .pointer = 2,
        },
        .{
            .name = "last pointer before err floor",
            .constructed = xarray_slot_view.fromPointer(err_ptr.err_floor - 1),
            .kind = .pointer,
            .tagged = false,
            .pointer = err_ptr.err_floor - 1,
        },
        .{
            .name = "err floor constructor",
            .constructed = xarray_slot_view.fromErrorCode(-@as(isize, @intCast(err_ptr.max_errno))),
            .kind = .err,
            .tagged = true,
            .error_code = -@as(isize, @intCast(err_ptr.max_errno)),
        },
        .{
            .name = "interior errno constructor",
            .constructed = xarray_slot_view.fromErrorCode(-517),
            .kind = .err,
            .tagged = true,
            .error_code = -517,
        },
        .{
            .name = "top errno constructor",
            .constructed = xarray_slot_view.fromErrorCode(-1),
            .kind = .err,
            .tagged = true,
            .error_code = -1,
        },
    };

    for (rows) |row| {
        try expectConstructedRawParity(row);
    }
}

test "constructor raw parity preserves err_ptr and xa_value boundary equations" {
    const value_slot = try xarray_slot_view.fromValue(xa_value.safe_inline_limit);
    const pointer_slot = xarray_slot_view.fromPointer(err_ptr.err_floor - 1);
    const err_slot = xarray_slot_view.fromErrorCode(-@as(isize, @intCast(err_ptr.max_errno)));
    const rejected_raw = ((xa_value.safe_inline_limit + 1) << 1) | xa_value.value_tag_mask;

    try std.testing.expectEqual(err_ptr.err_floor - 2, value_slot.rawValue());
    try std.testing.expectEqual(err_ptr.err_floor - 1, pointer_slot.rawValue());
    try std.testing.expectEqual(err_ptr.err_floor, err_slot.rawValue());
    try std.testing.expectEqual(err_ptr.err_floor, rejected_raw);

    try std.testing.expectEqual(SlotKind.value, xarray_slot_view.fromRaw(value_slot.rawValue()).kind());
    try std.testing.expectEqual(SlotKind.pointer, xarray_slot_view.fromRaw(pointer_slot.rawValue()).kind());
    try std.testing.expectEqual(SlotKind.err, xarray_slot_view.fromRaw(err_slot.rawValue()).kind());
    try std.testing.expectEqual(SlotKind.err, xarray_slot_view.fromRaw(rejected_raw).kind());
}
