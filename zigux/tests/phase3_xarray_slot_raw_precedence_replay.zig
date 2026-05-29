const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;

const RawPrecedenceCase = struct {
    name: []const u8,
    raw: usize,
    kind: SlotKind,
    value: ?usize = null,
    error_code: ?isize = null,
    pointer: ?usize = null,
    tagged: bool,
};

fn expectRawPrecedence(case: RawPrecedenceCase) !void {
    const slot = xarray_slot_view.fromRaw(case.raw);

    try std.testing.expectEqual(case.kind, slot.kind());
    try std.testing.expectEqual(case.raw, slot.rawValue());
    try std.testing.expectEqual(case.kind == .null, slot.isNull());
    try std.testing.expectEqual(case.kind == .value, slot.isValue());
    try std.testing.expectEqual(case.kind == .err, slot.isErr());
    try std.testing.expectEqual(case.kind == .pointer, slot.isPointer());
    try std.testing.expectEqual(case.value, slot.value());
    try std.testing.expectEqual(case.error_code, slot.errorCode());
    try std.testing.expectEqual(case.pointer, slot.pointerValue());
    try std.testing.expectEqual(case.tagged, xarray_slot_view.isTaggedInternalEntry(case.raw));
}

test "raw slot precedence keeps null value pointer and err lanes disjoint" {
    const cases = [_]RawPrecedenceCase{
        .{
            .name = "null raw stays null before pointer fallback",
            .raw = 0,
            .kind = .null,
            .tagged = false,
        },
        .{
            .name = "inline zero uses the value lane",
            .raw = try xa_value.makeValue(0),
            .kind = .value,
            .value = 0,
            .tagged = true,
        },
        .{
            .name = "highest accepted inline value remains value before err floor",
            .raw = try xa_value.makeValue(xa_value.safe_inline_limit),
            .kind = .value,
            .value = xa_value.safe_inline_limit,
            .tagged = true,
        },
        .{
            .name = "even gap immediately below err floor falls through to pointer",
            .raw = err_ptr.err_floor - 1,
            .kind = .pointer,
            .pointer = err_ptr.err_floor - 1,
            .tagged = false,
        },
        .{
            .name = "ordinary aligned raw remains pointer-like",
            .raw = 0x1000,
            .kind = .pointer,
            .pointer = 0x1000,
            .tagged = false,
        },
        .{
            .name = "err floor wins over the xa_value low tag bit",
            .raw = err_ptr.err_floor,
            .kind = .err,
            .error_code = -4095,
            .tagged = true,
        },
        .{
            .name = "even errno raw is still an error despite lacking value tag",
            .raw = err_ptr.fromErrorCode(-2),
            .kind = .err,
            .error_code = -2,
            .tagged = true,
        },
        .{
            .name = "top errno raw stays error and closes value and pointer decoders",
            .raw = err_ptr.fromErrorCode(-1),
            .kind = .err,
            .error_code = -1,
            .tagged = true,
        },
    };

    for (cases) |case| {
        errdefer std.debug.print("raw precedence case failed: {s}\n", .{case.name});
        try expectRawPrecedence(case);
    }
}

test "rejected xa_value aliases decode through err_ptr before value" {
    const rejected_values = [_]usize{
        xa_value.safe_inline_limit + 1,
        xa_value.safe_inline_limit + 2,
        xa_value.safe_inline_limit + 17,
    };

    for (rejected_values) |value| {
        const raw = (value << 1) | xa_value.value_tag_mask;
        const slot = xarray_slot_view.fromRaw(raw);

        try std.testing.expect(!xa_value.canRepresent(value));
        try std.testing.expect(err_ptr.isErrValue(raw));
        try std.testing.expect(!xa_value.isValue(raw));
        try std.testing.expectEqual(SlotKind.err, slot.kind());
        try std.testing.expectEqual(err_ptr.toErrorCode(raw), slot.errorCode().?);
        try std.testing.expectEqual(@as(?usize, null), slot.value());
        try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
        try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
    }
}
