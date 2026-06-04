const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;

const RawCase = struct {
    name: []const u8,
    raw: usize,
    kind: SlotKind,
    value: ?usize = null,
    err: ?isize = null,
    pointer: ?usize = null,
    tagged_internal: bool,
};

fn expectRawCase(case: RawCase) !void {
    const slot = xarray_slot_view.fromRaw(case.raw);

    errdefer std.debug.print("raw constructor case failed: {s}\n", .{case.name});

    try std.testing.expectEqual(case.raw, slot.rawValue());
    try std.testing.expectEqual(case.kind, slot.kind());
    try std.testing.expectEqual(case.kind == .null, slot.isNull());
    try std.testing.expectEqual(case.kind == .value, slot.isValue());
    try std.testing.expectEqual(case.kind == .err, slot.isErr());
    try std.testing.expectEqual(case.kind == .pointer, slot.isPointer());
    try std.testing.expectEqual(case.value, slot.value());
    try std.testing.expectEqual(case.err, slot.errorCode());
    try std.testing.expectEqual(case.pointer, slot.pointerValue());
    try std.testing.expectEqual(case.tagged_internal, xarray_slot_view.isTaggedInternalEntry(case.raw));
}

test "raw constructor keeps boundary lanes mutually exclusive" {
    const inline_zero = try xa_value.makeValue(0);
    const inline_high = try xa_value.makeValue(xa_value.safe_inline_limit);
    const err_floor_gap = err_ptr.err_floor - 1;
    const err_floor = err_ptr.err_floor;
    const top_err = err_ptr.fromErrorCode(-1);

    const cases = [_]RawCase{
        .{
            .name = "null slot",
            .raw = 0,
            .kind = .null,
            .tagged_internal = false,
        },
        .{
            .name = "inline zero",
            .raw = inline_zero,
            .kind = .value,
            .value = 0,
            .tagged_internal = true,
        },
        .{
            .name = "highest inline value",
            .raw = inline_high,
            .kind = .value,
            .value = xa_value.safe_inline_limit,
            .tagged_internal = true,
        },
        .{
            .name = "pointer-like even raw",
            .raw = 0x1000,
            .kind = .pointer,
            .pointer = 0x1000,
            .tagged_internal = false,
        },
        .{
            .name = "odd raw below err floor",
            .raw = 0x1001,
            .kind = .value,
            .value = 0x800,
            .tagged_internal = true,
        },
        .{
            .name = "gap immediately below err floor",
            .raw = err_floor_gap,
            .kind = .pointer,
            .pointer = err_floor_gap,
            .tagged_internal = false,
        },
        .{
            .name = "err floor",
            .raw = err_floor,
            .kind = .err,
            .err = -4095,
            .tagged_internal = true,
        },
        .{
            .name = "top err",
            .raw = top_err,
            .kind = .err,
            .err = -1,
            .tagged_internal = true,
        },
    };

    for (cases) |case| {
        try expectRawCase(case);
    }
}

test "public constructors match raw constructor representatives" {
    const value_slot = try xarray_slot_view.fromValue(0x2a);
    const raw_value_slot = xarray_slot_view.fromRaw(try xa_value.makeValue(0x2a));
    const err_slot = xarray_slot_view.fromErrorCode(-12);
    const raw_err_slot = xarray_slot_view.fromRaw(err_ptr.fromErrorCode(-12));
    const pointer_slot = xarray_slot_view.fromPointer(0x2000);
    const raw_pointer_slot = xarray_slot_view.fromRaw(0x2000);

    try std.testing.expectEqual(raw_value_slot.rawValue(), value_slot.rawValue());
    try std.testing.expectEqual(raw_value_slot.kind(), value_slot.kind());
    try std.testing.expectEqual(raw_value_slot.value(), value_slot.value());

    try std.testing.expectEqual(raw_err_slot.rawValue(), err_slot.rawValue());
    try std.testing.expectEqual(raw_err_slot.kind(), err_slot.kind());
    try std.testing.expectEqual(raw_err_slot.errorCode(), err_slot.errorCode());

    try std.testing.expectEqual(raw_pointer_slot.rawValue(), pointer_slot.rawValue());
    try std.testing.expectEqual(raw_pointer_slot.kind(), pointer_slot.kind());
    try std.testing.expectEqual(raw_pointer_slot.pointerValue(), pointer_slot.pointerValue());
}
