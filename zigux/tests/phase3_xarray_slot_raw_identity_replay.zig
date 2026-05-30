const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;

const ExpectedProjection = struct {
    name: []const u8,
    raw: usize,
    kind: SlotKind,
    value: ?usize = null,
    error_code: ?isize = null,
    pointer: ?usize = null,
};

fn expectRawIdentity(case: ExpectedProjection) !void {
    const slot = xarray_slot_view.fromRaw(case.raw);

    try std.testing.expectEqual(case.raw, slot.rawValue());
    try std.testing.expectEqual(case.kind, slot.kind());
    try std.testing.expectEqual(case.kind == .null, slot.isNull());
    try std.testing.expectEqual(case.kind == .value, slot.isValue());
    try std.testing.expectEqual(case.kind == .err, slot.isErr());
    try std.testing.expectEqual(case.kind == .pointer, slot.isPointer());
    try std.testing.expectEqual(case.value, slot.value());
    try std.testing.expectEqual(case.error_code, slot.errorCode());
    try std.testing.expectEqual(case.pointer, slot.pointerValue());
}

test "fromRaw preserves slot identity while optional decoders project one lane" {
    const cases = [_]ExpectedProjection{
        .{
            .name = "null raw stays zero with every payload decoder closed",
            .raw = 0,
            .kind = .null,
        },
        .{
            .name = "inline value preserves its tagged raw while projecting the payload",
            .raw = try xa_value.makeValue(73),
            .kind = .value,
            .value = 73,
        },
        .{
            .name = "even pointer gap preserves its exact non-tagged raw",
            .raw = err_ptr.err_floor - 1,
            .kind = .pointer,
            .pointer = err_ptr.err_floor - 1,
        },
        .{
            .name = "ordinary pointer raw is returned without normalization",
            .raw = 0x2000,
            .kind = .pointer,
            .pointer = 0x2000,
        },
        .{
            .name = "middle err_ptr raw preserves the encoded errno word",
            .raw = err_ptr.fromErrorCode(-517),
            .kind = .err,
            .error_code = -517,
        },
        .{
            .name = "rejected xa_value alias still preserves raw identity as err_ptr",
            .raw = ((xa_value.safe_inline_limit + 1) << 1) | xa_value.value_tag_mask,
            .kind = .err,
            .error_code = -4095,
        },
    };

    for (cases) |case| {
        errdefer std.debug.print("raw identity case failed: {s}\n", .{case.name});
        try expectRawIdentity(case);
    }
}

test "constructor and raw views agree on raw identity for each public lane" {
    const constructed = [_]xarray_slot_view.SlotView{
        xarray_slot_view.nullSlot(),
        try xarray_slot_view.fromValue(5),
        xarray_slot_view.fromErrorCode(-22),
        xarray_slot_view.fromPointer(0x4000),
    };

    for (constructed) |slot| {
        const raw_view = xarray_slot_view.fromRaw(slot.rawValue());

        try std.testing.expectEqual(slot.rawValue(), raw_view.rawValue());
        try std.testing.expectEqual(slot.kind(), raw_view.kind());
        try std.testing.expectEqual(slot.value(), raw_view.value());
        try std.testing.expectEqual(slot.errorCode(), raw_view.errorCode());
        try std.testing.expectEqual(slot.pointerValue(), raw_view.pointerValue());
    }
}
