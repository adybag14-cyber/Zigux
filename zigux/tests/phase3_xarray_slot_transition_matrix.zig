const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;

const Expectation = struct {
    raw: usize,
    kind: SlotKind,
    value: ?usize = null,
    error_code: ?isize = null,
    pointer: ?usize = null,
};

fn expectDecoded(expected: Expectation) !void {
    const slot = xarray_slot_view.fromRaw(expected.raw);

    try testing.expectEqual(expected.kind, slot.kind());
    try testing.expectEqual(expected.raw, slot.rawValue());
    try testing.expectEqual(expected.value, slot.value());
    try testing.expectEqual(expected.error_code, slot.errorCode());
    try testing.expectEqual(expected.pointer, slot.pointerValue());

    try testing.expectEqual(expected.kind == .null, slot.isNull());
    try testing.expectEqual(expected.kind == .value, slot.isValue());
    try testing.expectEqual(expected.kind == .err, slot.isErr());
    try testing.expectEqual(expected.kind == .pointer, slot.isPointer());
}

fn expectAdjacent(current: Expectation, next: Expectation) !void {
    try expectDecoded(current);
    try expectDecoded(next);
    try testing.expectEqual(current.raw + 1, next.raw);
}

test "low xarray-slot raws keep the null-value-pointer transition matrix explicit" {
    const matrix = [_]Expectation{
        .{ .raw = 0, .kind = .null },
        .{ .raw = 1, .kind = .value, .value = 0 },
        .{ .raw = 2, .kind = .pointer, .pointer = 2 },
        .{ .raw = 3, .kind = .value, .value = 1 },
        .{ .raw = 4, .kind = .pointer, .pointer = 4 },
        .{ .raw = 5, .kind = .value, .value = 2 },
    };

    for (matrix[0 .. matrix.len - 1], matrix[1..]) |current, next| {
        try expectAdjacent(current, next);
    }

    try testing.expectEqual(matrix[1].value.? + 1, matrix[3].value.?);
    try testing.expectEqual(matrix[3].value.? + 1, matrix[5].value.?);
}

test "cutoff adjacency keeps value-gap-err progression stable" {
    const safe_limit_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const matrix = [_]Expectation{
        .{ .raw = safe_limit_raw, .kind = .value, .value = xa_value.safe_inline_limit },
        .{ .raw = err_ptr.err_floor - 1, .kind = .pointer, .pointer = err_ptr.err_floor - 1 },
        .{ .raw = err_ptr.err_floor, .kind = .err, .error_code = -4095 },
        .{ .raw = err_ptr.err_floor + 1, .kind = .err, .error_code = -4094 },
    };

    try testing.expectEqual(err_ptr.err_floor - 2, safe_limit_raw);

    for (matrix[0 .. matrix.len - 1], matrix[1..]) |current, next| {
        try expectAdjacent(current, next);
    }

    try testing.expectEqual(matrix[2].error_code.? + 1, matrix[3].error_code.?);
}

test "top err raws stay contiguous and monotonic" {
    const next_to_top = xarray_slot_view.fromErrorCode(-2);
    const top = xarray_slot_view.fromErrorCode(-1);

    try testing.expectEqual(next_to_top.rawValue() + 1, top.rawValue());
    try testing.expectEqual(@as(?isize, -2), next_to_top.errorCode());
    try testing.expectEqual(@as(?isize, -1), top.errorCode());
    try testing.expect(next_to_top.isErr());
    try testing.expect(top.isErr());
    try testing.expectEqual(@as(?usize, null), next_to_top.value());
    try testing.expectEqual(@as(?usize, null), top.value());
    try testing.expectEqual(@as(?usize, null), next_to_top.pointerValue());
    try testing.expectEqual(@as(?usize, null), top.pointerValue());
}
