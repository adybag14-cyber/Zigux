const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const ExpectedKind = xarray_slot_view.SlotKind;

const Case = struct {
    name: []const u8,
    raw: usize,
    kind: ExpectedKind,
    decoded_value: ?usize = null,
    decoded_error: ?isize = null,
    pointer_raw: ?usize = null,
    tagged: bool,
};

fn expectCase(case: Case) !void {
    const slot = xarray_slot_view.fromRaw(case.raw);

    try testing.expectEqual(case.raw, slot.rawValue());
    try testing.expectEqual(case.kind, slot.kind());
    try testing.expectEqual(case.decoded_value, slot.value());
    try testing.expectEqual(case.decoded_error, slot.errorCode());
    try testing.expectEqual(case.pointer_raw, slot.pointerValue());
    try testing.expectEqual(case.kind == .err, err_ptr.isErrValue(case.raw));
    try testing.expectEqual(case.kind == .value, xa_value.isValue(case.raw));
    try testing.expectEqual(case.tagged, xarray_slot_view.isTaggedInternalEntry(case.raw));

    switch (case.kind) {
        .null => {
            try testing.expect(slot.isNull());
            try testing.expect(!slot.isValue());
            try testing.expect(!slot.isErr());
            try testing.expect(!slot.isPointer());
        },
        .value => {
            try testing.expect(!slot.isNull());
            try testing.expect(slot.isValue());
            try testing.expect(!slot.isErr());
            try testing.expect(!slot.isPointer());
            try testing.expectEqual(case.decoded_value.?, xa_value.toValue(case.raw));
        },
        .err => {
            try testing.expect(!slot.isNull());
            try testing.expect(!slot.isValue());
            try testing.expect(slot.isErr());
            try testing.expect(!slot.isPointer());
            try testing.expectEqual(case.decoded_error.?, err_ptr.toErrorCode(case.raw));
        },
        .pointer => {
            try testing.expect(!slot.isNull());
            try testing.expect(!slot.isValue());
            try testing.expect(!slot.isErr());
            try testing.expect(slot.isPointer());
        },
    }
}

test "predicate matrix keeps representative raw values on the expected classifier lanes" {
    const inline_zero = try xa_value.makeValue(0);
    const inline_small = try xa_value.makeValue(29);
    const inline_limit = try xa_value.makeValue(xa_value.safe_inline_limit);

    const cases = [_]Case{
        .{ .name = "null", .raw = 0, .kind = .null, .tagged = false },
        .{ .name = "pointer_like", .raw = 64, .kind = .pointer, .pointer_raw = 64, .tagged = false },
        .{ .name = "inline_zero", .raw = inline_zero, .kind = .value, .decoded_value = 0, .tagged = true },
        .{ .name = "inline_small", .raw = inline_small, .kind = .value, .decoded_value = 29, .tagged = true },
        .{
            .name = "inline_limit",
            .raw = inline_limit,
            .kind = .value,
            .decoded_value = xa_value.safe_inline_limit,
            .tagged = true,
        },
        .{
            .name = "gap_before_err_floor",
            .raw = err_ptr.err_floor - 1,
            .kind = .pointer,
            .pointer_raw = err_ptr.err_floor - 1,
            .tagged = false,
        },
        .{
            .name = "err_floor",
            .raw = err_ptr.err_floor,
            .kind = .err,
            .decoded_error = -4095,
            .tagged = true,
        },
        .{
            .name = "err_top",
            .raw = err_ptr.fromErrorCode(-1),
            .kind = .err,
            .decoded_error = -1,
            .tagged = true,
        },
    };

    for (cases) |case| {
        try expectCase(case);
    }
}

test "predicate matrix keeps the first rejected inline value parked on the err floor" {
    const overlapping_value = xa_value.safe_inline_limit + 1;
    const raw = (overlapping_value << 1) | xa_value.value_tag_mask;
    const slot = xarray_slot_view.fromRaw(raw);

    try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(overlapping_value));
    try testing.expectEqual(err_ptr.err_floor, raw);
    try testing.expect(err_ptr.isErrValue(raw));
    try testing.expect(!xa_value.isValue(raw));
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
    try testing.expectEqual(ExpectedKind.err, slot.kind());
    try testing.expectEqual(@as(?isize, -4095), slot.errorCode());
}

test "predicate matrix keeps the pointer gap below err floor out of both tagged lanes" {
    const raw = err_ptr.err_floor - 1;
    const slot = xarray_slot_view.fromRaw(raw);

    try testing.expect(!err_ptr.isErrValue(raw));
    try testing.expect(!xa_value.isValue(raw));
    try testing.expect(!xarray_slot_view.isTaggedInternalEntry(raw));
    try testing.expectEqual(ExpectedKind.pointer, slot.kind());
    try testing.expectEqual(@as(?usize, raw), slot.pointerValue());
}
