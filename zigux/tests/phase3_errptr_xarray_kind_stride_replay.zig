const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;

const SlotCase = struct {
    name: []const u8,
    raw: usize,
    kind: SlotKind,
    tagged: bool,
    value: ?usize = null,
    error_code: ?isize = null,
    pointer: ?usize = null,
};

fn expectSlot(case: SlotCase) !void {
    const slot = xarray_slot_view.fromRaw(case.raw);

    try std.testing.expectEqual(case.kind, slot.kind());
    try std.testing.expectEqual(case.raw, slot.rawValue());
    try std.testing.expectEqual(case.kind == .null, slot.isNull());
    try std.testing.expectEqual(case.kind == .value, slot.isValue());
    try std.testing.expectEqual(case.kind == .err, slot.isErr());
    try std.testing.expectEqual(case.kind == .pointer, slot.isPointer());
    try std.testing.expectEqual(case.tagged, slot.isTaggedEntry());
    try std.testing.expectEqual(case.tagged, xarray_slot_view.isTaggedInternalEntry(case.raw));
    try std.testing.expectEqual(case.value, slot.value());
    try std.testing.expectEqual(case.error_code, slot.errorCode());
    try std.testing.expectEqual(case.pointer, slot.pointerValue());
}

test "raw xarray slot kind stride keeps accessors closed by lane" {
    const inline_mid = xa_value.safe_inline_limit / 2;
    const inline_last = xa_value.safe_inline_limit;
    const value_below_floor = xa_value.safe_inline_limit - 1;
    const pointer_gap_near = err_ptr.err_floor - 1;
    const pointer_gap_stride = err_ptr.err_floor - 3;
    const err_interior = err_ptr.fromErrorCode(-2048);

    const cases = [_]SlotCase{
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
            .name = "inline middle",
            .raw = try xa_value.makeValue(inline_mid),
            .kind = .value,
            .tagged = true,
            .value = inline_mid,
        },
        .{
            .name = "inline limit",
            .raw = try xa_value.makeValue(inline_last),
            .kind = .value,
            .tagged = true,
            .value = inline_last,
        },
        .{
            .name = "value below floor",
            .raw = try xa_value.makeValue(value_below_floor),
            .kind = .value,
            .tagged = true,
            .value = value_below_floor,
        },
        .{
            .name = "near pointer gap",
            .raw = pointer_gap_near,
            .kind = .pointer,
            .tagged = false,
            .pointer = pointer_gap_near,
        },
        .{
            .name = "stride pointer gap",
            .raw = pointer_gap_stride,
            .kind = .pointer,
            .tagged = false,
            .pointer = pointer_gap_stride,
        },
        .{
            .name = "err floor",
            .raw = err_ptr.err_floor,
            .kind = .err,
            .tagged = true,
            .error_code = -4095,
        },
        .{
            .name = "interior errno",
            .raw = err_interior,
            .kind = .err,
            .tagged = true,
            .error_code = -2048,
        },
        .{
            .name = "top errno",
            .raw = err_ptr.fromErrorCode(-1),
            .kind = .err,
            .tagged = true,
            .error_code = -1,
        },
    };

    for (cases) |case| {
        errdefer std.debug.print("slot case failed: {s}\n", .{case.name});
        try expectSlot(case);
    }
}

test "rejected inline alias enters err lane before value decoding" {
    const rejected_inline = xa_value.safe_inline_limit + 1;
    const alias_raw = (rejected_inline << 1) | xa_value.value_tag_mask;
    const slot = xarray_slot_view.fromRaw(alias_raw);

    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(rejected_inline));
    try std.testing.expectEqual(err_ptr.err_floor, alias_raw);
    try std.testing.expectEqual(SlotKind.err, slot.kind());
    try std.testing.expect(slot.isTaggedEntry());
    try std.testing.expect(!slot.isValue());
    try std.testing.expect(!slot.isPointer());
    try std.testing.expectEqual(@as(?usize, null), slot.value());
    try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
    try std.testing.expectEqual(@as(?isize, -4095), slot.errorCode());
}
