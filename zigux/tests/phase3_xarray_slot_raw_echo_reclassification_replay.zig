const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;

const RawEchoCase = struct {
    name: []const u8,
    raw: usize,
    kind: SlotKind,
    tagged: bool,
    value: ?usize,
    err: ?isize,
    pointer: ?usize,
};

fn expectRawEcho(case: RawEchoCase) !void {
    const first = xarray_slot_view.fromRaw(case.raw);
    const second = xarray_slot_view.fromRaw(first.rawValue());

    try testing.expectEqual(case.raw, first.rawValue());
    try testing.expectEqual(first.rawValue(), second.rawValue());
    try testing.expectEqual(case.kind, first.kind());
    try testing.expectEqual(first.kind(), second.kind());
    try testing.expectEqual(case.tagged, first.isTaggedEntry());
    try testing.expectEqual(first.isTaggedEntry(), second.isTaggedEntry());
    try testing.expectEqual(case.tagged, xarray_slot_view.isTaggedInternalEntry(case.raw));

    try testing.expectEqual(case.kind == .null, first.isNull());
    try testing.expectEqual(case.kind == .value, first.isValue());
    try testing.expectEqual(case.kind == .err, first.isErr());
    try testing.expectEqual(case.kind == .pointer, first.isPointer());

    try testing.expectEqual(case.value, first.value());
    try testing.expectEqual(case.err, first.errorCode());
    try testing.expectEqual(case.pointer, first.pointerValue());
    try testing.expectEqual(first.value(), second.value());
    try testing.expectEqual(first.errorCode(), second.errorCode());
    try testing.expectEqual(first.pointerValue(), second.pointerValue());
}

test "raw slot echo preserves lane classification and accessor closure" {
    const cases = [_]RawEchoCase{
        .{
            .name = "null",
            .raw = 0,
            .kind = .null,
            .tagged = false,
            .value = null,
            .err = null,
            .pointer = null,
        },
        .{
            .name = "inline-zero-value",
            .raw = try xa_value.makeValue(0),
            .kind = .value,
            .tagged = true,
            .value = 0,
            .err = null,
            .pointer = null,
        },
        .{
            .name = "safe-limit-value",
            .raw = try xa_value.makeValue(xa_value.safe_inline_limit),
            .kind = .value,
            .tagged = true,
            .value = xa_value.safe_inline_limit,
            .err = null,
            .pointer = null,
        },
        .{
            .name = "gap-below-err-floor",
            .raw = err_ptr.err_floor - 1,
            .kind = .pointer,
            .tagged = false,
            .value = null,
            .err = null,
            .pointer = err_ptr.err_floor - 1,
        },
        .{
            .name = "err-floor",
            .raw = err_ptr.err_floor,
            .kind = .err,
            .tagged = true,
            .value = null,
            .err = -@as(isize, @intCast(err_ptr.max_errno)),
            .pointer = null,
        },
        .{
            .name = "interior-errno",
            .raw = err_ptr.fromErrorCode(-512),
            .kind = .err,
            .tagged = true,
            .value = null,
            .err = -512,
            .pointer = null,
        },
        .{
            .name = "top-errno",
            .raw = err_ptr.fromErrorCode(-1),
            .kind = .err,
            .tagged = true,
            .value = null,
            .err = -1,
            .pointer = null,
        },
    };

    for (cases) |case| {
        try std.testing.expect(case.name.len > 0);
        try expectRawEcho(case);
    }
}

test "constructor raw echoes match direct reclassification lanes" {
    const constructors = [_]xarray_slot_view.SlotView{
        xarray_slot_view.nullSlot(),
        try xarray_slot_view.fromValue(73),
        xarray_slot_view.fromPointer(0x2000),
        xarray_slot_view.fromErrorCode(-73),
    };

    for (constructors) |slot| {
        const echoed = xarray_slot_view.fromRaw(slot.rawValue());

        try testing.expectEqual(slot.rawValue(), echoed.rawValue());
        try testing.expectEqual(slot.kind(), echoed.kind());
        try testing.expectEqual(slot.isTaggedEntry(), echoed.isTaggedEntry());
        try testing.expectEqual(slot.value(), echoed.value());
        try testing.expectEqual(slot.errorCode(), echoed.errorCode());
        try testing.expectEqual(slot.pointerValue(), echoed.pointerValue());
    }
}

test "first rejected inline alias reclassifies as the err floor" {
    const rejected_value = xa_value.safe_inline_limit + 1;
    const rejected_raw = (rejected_value << 1) | xa_value.value_tag_mask;
    const slot = xarray_slot_view.fromRaw(rejected_raw);

    try testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(rejected_value));
    try testing.expectEqual(err_ptr.err_floor, rejected_raw);
    try testing.expectEqual(SlotKind.err, slot.kind());
    try testing.expect(slot.isTaggedEntry());
    try testing.expectEqual(@as(?isize, -4095), slot.errorCode());
    try testing.expectEqual(@as(?usize, null), slot.value());
    try testing.expectEqual(@as(?usize, null), slot.pointerValue());
}
