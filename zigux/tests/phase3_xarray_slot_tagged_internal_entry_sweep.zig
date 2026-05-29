const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const RawCase = struct {
    label: []const u8,
    raw: usize,
    kind: xarray_slot_view.SlotKind,
    tagged: bool,
    value: ?usize = null,
    error_code: ?isize = null,
    pointer: ?usize = null,
};

fn expectRawCase(case: RawCase) !void {
    const slot = xarray_slot_view.fromRaw(case.raw);

    errdefer std.debug.print("failed raw case: {s}\n", .{case.label});
    try std.testing.expectEqual(case.raw, slot.rawValue());
    try std.testing.expectEqual(case.kind, slot.kind());
    try std.testing.expectEqual(case.tagged, xarray_slot_view.isTaggedInternalEntry(case.raw));
    try std.testing.expectEqual(case.value, slot.value());
    try std.testing.expectEqual(case.error_code, slot.errorCode());
    try std.testing.expectEqual(case.pointer, slot.pointerValue());
}

test "tagged internal entry sweep keeps null value pointer and err lanes disjoint" {
    const highest_value_raw = try xa_value.makeValue(xa_value.safe_inline_limit);

    const cases = [_]RawCase{
        .{
            .label = "null slot is not tagged internal",
            .raw = 0,
            .kind = .null,
            .tagged = false,
        },
        .{
            .label = "inline zero is tagged value",
            .raw = try xa_value.makeValue(0),
            .kind = .value,
            .tagged = true,
            .value = 0,
        },
        .{
            .label = "highest inline value stays tagged below err floor",
            .raw = highest_value_raw,
            .kind = .value,
            .tagged = true,
            .value = xa_value.safe_inline_limit,
        },
        .{
            .label = "single pointer gap below err floor is not tagged",
            .raw = err_ptr.err_floor - 1,
            .kind = .pointer,
            .tagged = false,
            .pointer = err_ptr.err_floor - 1,
        },
        .{
            .label = "ordinary aligned pointer is not tagged",
            .raw = 0x1000,
            .kind = .pointer,
            .tagged = false,
            .pointer = 0x1000,
        },
        .{
            .label = "err floor is tagged err",
            .raw = err_ptr.err_floor,
            .kind = .err,
            .tagged = true,
            .error_code = -4095,
        },
        .{
            .label = "next err slot remains tagged err",
            .raw = err_ptr.err_floor + 1,
            .kind = .err,
            .tagged = true,
            .error_code = -4094,
        },
        .{
            .label = "top err slot remains tagged err",
            .raw = err_ptr.fromErrorCode(-1),
            .kind = .err,
            .tagged = true,
            .error_code = -1,
        },
    };

    for (cases) |case| {
        try expectRawCase(case);
    }
}

test "constructors land on the same tagged-entry decisions as raw decoding" {
    const value_slot = try xarray_slot_view.fromValue(xa_value.safe_inline_limit);
    const err_slot = xarray_slot_view.fromErrorCode(-4094);
    const pointer_slot = xarray_slot_view.fromPointer(err_ptr.err_floor - 1);

    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(value_slot.rawValue()));
    try std.testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), value_slot.value());

    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(err_slot.rawValue()));
    try std.testing.expectEqual(@as(?isize, -4094), err_slot.errorCode());

    try std.testing.expect(!xarray_slot_view.isTaggedInternalEntry(pointer_slot.rawValue()));
    try std.testing.expectEqual(@as(?usize, err_ptr.err_floor - 1), pointer_slot.pointerValue());
}
