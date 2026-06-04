const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const Case = struct {
    name: []const u8,
    raw: usize,
    kind: xarray_slot_view.SlotKind,
    tagged_internal: bool,
    decoded_value: ?usize,
    decoded_error: ?isize,
    decoded_pointer: ?usize,
};

fn expectCase(case: Case) !void {
    const slot = xarray_slot_view.fromRaw(case.raw);

    try std.testing.expectEqual(case.raw, slot.rawValue());
    try std.testing.expectEqual(case.kind, slot.kind());
    try std.testing.expectEqual(case.tagged_internal, xarray_slot_view.isTaggedInternalEntry(case.raw));
    try std.testing.expectEqual(case.kind == .null, slot.isNull());
    try std.testing.expectEqual(case.kind == .value, slot.isValue());
    try std.testing.expectEqual(case.kind == .err, slot.isErr());
    try std.testing.expectEqual(case.kind == .pointer, slot.isPointer());
    try std.testing.expectEqual(case.decoded_value, slot.value());
    try std.testing.expectEqual(case.decoded_error, slot.errorCode());
    try std.testing.expectEqual(case.decoded_pointer, slot.pointerValue());
}

test "tagged-internal matrix keeps xarray slot lane ownership disjoint" {
    const high_value_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const cases = [_]Case{
        .{
            .name = "null-slot",
            .raw = 0,
            .kind = .null,
            .tagged_internal = false,
            .decoded_value = null,
            .decoded_error = null,
            .decoded_pointer = null,
        },
        .{
            .name = "inline-zero",
            .raw = try xa_value.makeValue(0),
            .kind = .value,
            .tagged_internal = true,
            .decoded_value = 0,
            .decoded_error = null,
            .decoded_pointer = null,
        },
        .{
            .name = "high-inline-value",
            .raw = high_value_raw,
            .kind = .value,
            .tagged_internal = true,
            .decoded_value = xa_value.safe_inline_limit,
            .decoded_error = null,
            .decoded_pointer = null,
        },
        .{
            .name = "ordinary-pointer",
            .raw = 0x1000,
            .kind = .pointer,
            .tagged_internal = false,
            .decoded_value = null,
            .decoded_error = null,
            .decoded_pointer = 0x1000,
        },
        .{
            .name = "odd-pointer-gap",
            .raw = err_ptr.err_floor - 1,
            .kind = .pointer,
            .tagged_internal = false,
            .decoded_value = null,
            .decoded_error = null,
            .decoded_pointer = err_ptr.err_floor - 1,
        },
        .{
            .name = "err-floor",
            .raw = err_ptr.err_floor,
            .kind = .err,
            .tagged_internal = true,
            .decoded_value = null,
            .decoded_error = -@as(isize, @intCast(err_ptr.max_errno)),
            .decoded_pointer = null,
        },
        .{
            .name = "middle-errno",
            .raw = err_ptr.fromErrorCode(-2048),
            .kind = .err,
            .tagged_internal = true,
            .decoded_value = null,
            .decoded_error = -2048,
            .decoded_pointer = null,
        },
        .{
            .name = "top-errno",
            .raw = err_ptr.fromErrorCode(-1),
            .kind = .err,
            .tagged_internal = true,
            .decoded_value = null,
            .decoded_error = -1,
            .decoded_pointer = null,
        },
    };

    for (cases) |case| {
        try std.testing.expect(case.name.len > 0);
        try expectCase(case);
    }
}

test "public constructors agree with tagged-internal classification" {
    const constructed_value = try xarray_slot_view.fromValue(17);
    const constructed_error = xarray_slot_view.fromErrorCode(-17);
    const constructed_pointer = xarray_slot_view.fromPointer(0x2000);

    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(constructed_value.rawValue()));
    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(constructed_error.rawValue()));
    try std.testing.expect(!xarray_slot_view.isTaggedInternalEntry(xarray_slot_view.nullSlot().rawValue()));
    try std.testing.expect(!xarray_slot_view.isTaggedInternalEntry(constructed_pointer.rawValue()));

    try std.testing.expectEqual(xarray_slot_view.SlotKind.value, constructed_value.kind());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, constructed_error.kind());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.null, xarray_slot_view.nullSlot().kind());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.pointer, constructed_pointer.kind());
}
