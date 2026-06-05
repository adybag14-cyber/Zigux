const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;
const SlotView = xarray_slot_view.SlotView;

const TransitionCase = struct {
    name: []const u8,
    raw: usize,
    kind: SlotKind,
    value: ?usize,
    error_code: ?isize,
    pointer: ?usize,
    tagged: bool,
    ok_value: bool,
    xa_value_raw: bool,
};

fn expectTransition(case: TransitionCase) !void {
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
    try std.testing.expectEqual(case.tagged, slot.isTaggedEntry());
    try std.testing.expectEqual(case.tagged, xarray_slot_view.isTaggedInternalEntry(case.raw));
    try std.testing.expectEqual(case.ok_value, err_ptr.isOkValue(case.raw));
    try std.testing.expectEqual(case.xa_value_raw, xa_value.isValue(case.raw));
}

test "raw classification transitions follow null err value pointer precedence" {
    const inline_tail_raw = try xa_value.makeValue(xa_value.safe_inline_limit);

    const cases = [_]TransitionCase{
        .{
            .name = "zero remains the only null slot",
            .raw = 0,
            .kind = .null,
            .value = null,
            .error_code = null,
            .pointer = null,
            .tagged = false,
            .ok_value = true,
            .xa_value_raw = false,
        },
        .{
            .name = "low odd raw becomes an xa_value",
            .raw = try xa_value.makeValue(0),
            .kind = .value,
            .value = 0,
            .error_code = null,
            .pointer = null,
            .tagged = true,
            .ok_value = true,
            .xa_value_raw = true,
        },
        .{
            .name = "even nonzero raw stays pointer-like",
            .raw = 2,
            .kind = .pointer,
            .value = null,
            .error_code = null,
            .pointer = 2,
            .tagged = false,
            .ok_value = true,
            .xa_value_raw = false,
        },
        .{
            .name = "highest inline value remains value before the pointer gap",
            .raw = inline_tail_raw,
            .kind = .value,
            .value = xa_value.safe_inline_limit,
            .error_code = null,
            .pointer = null,
            .tagged = true,
            .ok_value = true,
            .xa_value_raw = true,
        },
        .{
            .name = "last raw before err_ptr floor is pointer-like",
            .raw = err_ptr.err_floor - 1,
            .kind = .pointer,
            .value = null,
            .error_code = null,
            .pointer = err_ptr.err_floor - 1,
            .tagged = false,
            .ok_value = true,
            .xa_value_raw = false,
        },
        .{
            .name = "err_ptr floor wins before xa_value can decode the low tag",
            .raw = err_ptr.err_floor,
            .kind = .err,
            .value = null,
            .error_code = -4095,
            .pointer = null,
            .tagged = true,
            .ok_value = false,
            .xa_value_raw = false,
        },
        .{
            .name = "interior errno stays in the err lane",
            .raw = err_ptr.fromErrorCode(-512),
            .kind = .err,
            .value = null,
            .error_code = -512,
            .pointer = null,
            .tagged = true,
            .ok_value = false,
            .xa_value_raw = false,
        },
        .{
            .name = "top errno keeps err precedence over low-bit value shape",
            .raw = err_ptr.fromErrorCode(-1),
            .kind = .err,
            .value = null,
            .error_code = -1,
            .pointer = null,
            .tagged = true,
            .ok_value = false,
            .xa_value_raw = false,
        },
    };

    for (cases) |case| {
        errdefer std.debug.print("failed transition case: {s}\n", .{case.name});
        try expectTransition(case);
    }
}

test "constructor outputs land on the same precedence table as raw slots" {
    const constructed = [_]SlotView{
        xarray_slot_view.nullSlot(),
        try xarray_slot_view.fromValue(1),
        xarray_slot_view.fromPointer(0x2000),
        xarray_slot_view.fromErrorCode(-34),
    };
    const expected = [_]SlotKind{ .null, .value, .pointer, .err };

    for (constructed, expected) |slot, kind| {
        try std.testing.expectEqual(kind, slot.kind());
        try expectTransition(.{
            .name = "constructor raw follows table",
            .raw = slot.rawValue(),
            .kind = kind,
            .value = slot.value(),
            .error_code = slot.errorCode(),
            .pointer = slot.pointerValue(),
            .tagged = slot.isTaggedEntry(),
            .ok_value = err_ptr.isOkValue(slot.rawValue()),
            .xa_value_raw = xa_value.isValue(slot.rawValue()),
        });
    }
}

test "first rejected inline alias transitions directly into err_ptr space" {
    const rejected_value = xa_value.safe_inline_limit + 1;
    const rejected_raw = (rejected_value << 1) | xa_value.value_tag_mask;
    const slot = xarray_slot_view.fromRaw(rejected_raw);

    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(rejected_value));
    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(rejected_value));
    try std.testing.expectEqual(err_ptr.err_floor, rejected_raw);
    try std.testing.expectEqual(SlotKind.err, slot.kind());
    try std.testing.expectEqual(@as(?isize, -4095), slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), slot.value());
    try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
    try std.testing.expect(!xa_value.isValue(rejected_raw));
    try std.testing.expect(err_ptr.isErrValue(rejected_raw));
}
