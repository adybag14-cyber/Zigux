const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const ExpectedKind = enum {
    null,
    value,
    err,
    pointer,
};

const Case = struct {
    name: []const u8,
    raw: usize,
    kind: ExpectedKind,
    decoded_value: ?usize = null,
    decoded_error: ?isize = null,
    pointer_raw: ?usize = null,
};

fn expectCase(case: Case) !void {
    const slot = xarray_slot_view.fromRaw(case.raw);

    try testing.expectEqual(case.raw, slot.rawValue());
    try testing.expectEqual(case.decoded_value, slot.value());
    try testing.expectEqual(case.decoded_error, slot.errorCode());
    try testing.expectEqual(case.pointer_raw, slot.pointerValue());

    switch (case.kind) {
        .null => {
            try testing.expect(slot.isNull());
            try testing.expect(!slot.isValue());
            try testing.expect(!slot.isErr());
            try testing.expect(!slot.isPointer());
            try testing.expect(!err_ptr.isErrValue(case.raw));
            try testing.expect(!xa_value.isValue(case.raw));
            try testing.expect(!xarray_slot_view.isTaggedInternalEntry(case.raw));
        },
        .value => {
            try testing.expect(!slot.isNull());
            try testing.expect(slot.isValue());
            try testing.expect(!slot.isErr());
            try testing.expect(!slot.isPointer());
            try testing.expect(!err_ptr.isErrValue(case.raw));
            try testing.expect(xa_value.isValue(case.raw));
            try testing.expectEqual(case.decoded_value.?, xa_value.toValue(case.raw));
            try testing.expect(xarray_slot_view.isTaggedInternalEntry(case.raw));
        },
        .err => {
            try testing.expect(!slot.isNull());
            try testing.expect(!slot.isValue());
            try testing.expect(slot.isErr());
            try testing.expect(!slot.isPointer());
            try testing.expect(err_ptr.isErrValue(case.raw));
            try testing.expect(!xa_value.isValue(case.raw));
            try testing.expectEqual(case.decoded_error.?, err_ptr.toErrorCode(case.raw));
            try testing.expect(xarray_slot_view.isTaggedInternalEntry(case.raw));
        },
        .pointer => {
            try testing.expect(!slot.isNull());
            try testing.expect(!slot.isValue());
            try testing.expect(!slot.isErr());
            try testing.expect(slot.isPointer());
            try testing.expect(!err_ptr.isErrValue(case.raw));
            try testing.expect(!xa_value.isValue(case.raw));
            try testing.expect(!xarray_slot_view.isTaggedInternalEntry(case.raw));
        },
    }
}

test "exact err_ptr/xarray dump cases keep the expected classification matrix" {
    const inline_limit = try xa_value.makeValue(xa_value.safe_inline_limit);

    const cases = [_]Case{
        .{ .name = "null", .raw = 0, .kind = .null },
        .{ .name = "pointer_like", .raw = 64, .kind = .pointer, .pointer_raw = 64 },
        .{
            .name = "inline_small",
            .raw = try xa_value.makeValue(29),
            .kind = .value,
            .decoded_value = 29,
        },
        .{
            .name = "inline_limit",
            .raw = inline_limit,
            .kind = .value,
            .decoded_value = xa_value.safe_inline_limit,
        },
        .{
            .name = "gap_before_err_floor",
            .raw = err_ptr.err_floor - 1,
            .kind = .pointer,
            .pointer_raw = err_ptr.err_floor - 1,
        },
        .{
            .name = "err_enomem",
            .raw = err_ptr.fromErrorCode(-12),
            .kind = .err,
            .decoded_error = -12,
        },
        .{
            .name = "err_max",
            .raw = err_ptr.fromErrorCode(-4095),
            .kind = .err,
            .decoded_error = -4095,
        },
    };

    for (cases) |case| {
        try expectCase(case);
    }
}

test "dump-case matrix keeps the safe inline limit two steps below the err floor" {
    const raw = try xa_value.makeValue(xa_value.safe_inline_limit);

    try testing.expectEqual(err_ptr.err_floor - 2, raw);
    try testing.expect(raw < err_ptr.err_floor);
    try testing.expectEqual(@as(usize, xa_value.safe_inline_limit), xa_value.toValue(raw));
}

test "dump-case matrix keeps the first rejected inline value parked on the err floor" {
    const overlapping_value = xa_value.safe_inline_limit + 1;
    const raw = (overlapping_value << 1) | xa_value.value_tag_mask;
    const slot = xarray_slot_view.fromRaw(raw);

    try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(overlapping_value));
    try testing.expectEqual(err_ptr.err_floor, raw);
    try testing.expect(slot.isErr());
    try testing.expectEqual(@as(?isize, -4095), slot.errorCode());
    try testing.expect(!slot.isValue());
}
