const testing = @import("std").testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const ExpectedRawSlot = struct {
    name: []const u8,
    raw: usize,
    kind: xarray_slot_view.SlotKind,
    value: ?usize = null,
    code: ?isize = null,
    pointer: ?usize = null,
    tagged: bool,
};

fn expectExclusion(sample: ExpectedRawSlot) !void {
    const slot = xarray_slot_view.fromRaw(sample.raw);

    try testing.expectEqual(sample.raw, slot.rawValue());
    try testing.expectEqual(sample.kind, slot.kind());
    try testing.expectEqual(sample.kind == .null, slot.isNull());
    try testing.expectEqual(sample.kind == .value, slot.isValue());
    try testing.expectEqual(sample.kind == .err, slot.isErr());
    try testing.expectEqual(sample.kind == .pointer, slot.isPointer());

    try testing.expectEqual(sample.value, slot.value());
    try testing.expectEqual(sample.code, slot.errorCode());
    try testing.expectEqual(sample.pointer, slot.pointerValue());
    try testing.expectEqual(sample.tagged, xarray_slot_view.isTaggedInternalEntry(sample.raw));
}

test "raw xarray slot decoders stay mutually exclusive across lane representatives" {
    const samples = [_]ExpectedRawSlot{
        .{ .name = "null", .raw = 0, .kind = .null, .tagged = false },
        .{ .name = "inline-zero", .raw = try xa_value.makeValue(0), .kind = .value, .value = 0, .tagged = true },
        .{ .name = "inline-one", .raw = try xa_value.makeValue(1), .kind = .value, .value = 1, .tagged = true },
        .{ .name = "inline-tail", .raw = try xa_value.makeValue(xa_value.safe_inline_limit), .kind = .value, .value = xa_value.safe_inline_limit, .tagged = true },
        .{ .name = "low-even-pointer", .raw = 2, .kind = .pointer, .pointer = 2, .tagged = false },
        .{ .name = "aligned-pointer", .raw = 0x1000, .kind = .pointer, .pointer = 0x1000, .tagged = false },
        .{ .name = "pre-err-gap", .raw = err_ptr.err_floor - 1, .kind = .pointer, .pointer = err_ptr.err_floor - 1, .tagged = false },
        .{ .name = "err-floor", .raw = err_ptr.err_floor, .kind = .err, .code = -4095, .tagged = true },
        .{ .name = "err-neighbor", .raw = err_ptr.err_floor + 1, .kind = .err, .code = -4094, .tagged = true },
        .{ .name = "err-top", .raw = err_ptr.fromErrorCode(-1), .kind = .err, .code = -1, .tagged = true },
    };

    for (samples) |sample| {
        try expectExclusion(sample);
    }
}

test "raw decoder predicates agree with helper-local tag predicates" {
    const raws = [_]usize{
        0,
        try xa_value.makeValue(0),
        try xa_value.makeValue(xa_value.safe_inline_limit),
        err_ptr.err_floor - 1,
        err_ptr.err_floor,
        err_ptr.err_floor + 1,
        err_ptr.fromErrorCode(-1),
    };

    for (raws) |raw| {
        const slot = xarray_slot_view.fromRaw(raw);

        try testing.expectEqual(err_ptr.isErrValue(raw), slot.isErr());
        try testing.expectEqual(xa_value.isValue(raw), slot.isValue());
        try testing.expectEqual(
            err_ptr.isErrValue(raw) or xa_value.isValue(raw),
            xarray_slot_view.isTaggedInternalEntry(raw),
        );
    }
}

test "pointer-like raws are the only nonzero slots with all typed decoders closed" {
    const pointers = [_]usize{ 2, 4, 0x1000, err_ptr.err_floor - 3, err_ptr.err_floor - 1 };

    for (pointers) |raw| {
        const slot = xarray_slot_view.fromRaw(raw);

        try testing.expect(raw != 0);
        try testing.expectEqual(xarray_slot_view.SlotKind.pointer, slot.kind());
        try testing.expectEqual(@as(?usize, null), slot.value());
        try testing.expectEqual(@as(?isize, null), slot.errorCode());
        try testing.expectEqual(@as(?usize, raw), slot.pointerValue());
        try testing.expect(!xarray_slot_view.isTaggedInternalEntry(raw));
    }
}
