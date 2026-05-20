const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const LaneCase = struct {
    raw: usize,
    kind: xarray_slot_view.SlotKind,
    payload: ?usize = null,
    code: ?isize = null,
    pointer: ?usize = null,
};

fn expectCase(case: LaneCase) !void {
    const slot = xarray_slot_view.fromRaw(case.raw);

    try testing.expectEqual(case.kind, slot.kind());
    try testing.expectEqual(case.raw, slot.rawValue());
    try testing.expectEqual(case.kind == .null, slot.isNull());
    try testing.expectEqual(case.kind == .value, slot.isValue());
    try testing.expectEqual(case.kind == .err, slot.isErr());
    try testing.expectEqual(case.kind == .pointer, slot.isPointer());
    try testing.expectEqual(case.payload, slot.value());
    try testing.expectEqual(case.code, slot.errorCode());
    try testing.expectEqual(case.pointer, slot.pointerValue());
    try testing.expectEqual(
        case.kind == .value or case.kind == .err,
        xarray_slot_view.isTaggedInternalEntry(case.raw),
    );
}

test "xarray-slot lane extrema stay explicit at both ends of each live lane" {
    const cases = [_]LaneCase{
        .{ .raw = 0, .kind = .null },
        .{ .raw = try xa_value.makeValue(0), .kind = .value, .payload = 0 },
        .{ .raw = try xa_value.makeValue(xa_value.safe_inline_limit), .kind = .value, .payload = xa_value.safe_inline_limit },
        .{ .raw = 2, .kind = .pointer, .pointer = 2 },
        .{ .raw = err_ptr.err_floor - 1, .kind = .pointer, .pointer = err_ptr.err_floor - 1 },
        .{ .raw = err_ptr.err_floor, .kind = .err, .code = -4095 },
        .{ .raw = err_ptr.fromErrorCode(-1), .kind = .err, .code = -1 },
    };

    for (cases) |case| {
        try expectCase(case);
    }
}

test "constructor rebuilds preserve the chosen lane extrema without raw drift" {
    const cases = [_]LaneCase{
        .{ .raw = 0, .kind = .null },
        .{ .raw = try xa_value.makeValue(0), .kind = .value, .payload = 0 },
        .{ .raw = try xa_value.makeValue(xa_value.safe_inline_limit), .kind = .value, .payload = xa_value.safe_inline_limit },
        .{ .raw = 2, .kind = .pointer, .pointer = 2 },
        .{ .raw = err_ptr.err_floor - 1, .kind = .pointer, .pointer = err_ptr.err_floor - 1 },
        .{ .raw = err_ptr.err_floor, .kind = .err, .code = -4095 },
        .{ .raw = err_ptr.fromErrorCode(-1), .kind = .err, .code = -1 },
    };

    for (cases) |case| {
        const rebuilt = switch (case.kind) {
            .null => xarray_slot_view.nullSlot(),
            .value => try xarray_slot_view.fromValue(case.payload.?),
            .pointer => xarray_slot_view.fromPointer(case.pointer.?),
            .err => xarray_slot_view.fromErrorCode(case.code.?),
        };

        try testing.expectEqual(case.raw, rebuilt.rawValue());
        try expectCase(.{
            .raw = rebuilt.rawValue(),
            .kind = case.kind,
            .payload = case.payload,
            .code = case.code,
            .pointer = case.pointer,
        });
    }
}

test "highest inline value stays separate from the first err-lane raw" {
    const highest_value = try xarray_slot_view.fromValue(xa_value.safe_inline_limit);
    const first_err = xarray_slot_view.fromErrorCode(-4095);

    try testing.expectEqual(err_ptr.err_floor - 2, highest_value.rawValue());
    try testing.expectEqual(err_ptr.err_floor, first_err.rawValue());
    try testing.expectEqual(@as(usize, 2), first_err.rawValue() - highest_value.rawValue());
    try testing.expectError(
        error.ValueWouldOverlapErrPtr,
        xarray_slot_view.fromValue(xa_value.safe_inline_limit + 1),
    );
}
