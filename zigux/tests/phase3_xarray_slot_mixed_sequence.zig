const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const ExpectedCase = struct {
    name: []const u8,
    raw: usize,
    kind: xarray_slot_view.SlotKind,
    value: ?usize,
    error_code: ?isize,
    pointer: ?usize,
    tagged_internal: bool,
};

fn expectCase(expected: ExpectedCase) !void {
    const slot = xarray_slot_view.fromRaw(expected.raw);

    try testing.expectEqual(expected.kind, slot.kind());
    try testing.expectEqual(expected.value, slot.value());
    try testing.expectEqual(expected.error_code, slot.errorCode());
    try testing.expectEqual(expected.pointer, slot.pointerValue());
    try testing.expectEqual(expected.tagged_internal, xarray_slot_view.isTaggedInternalEntry(expected.raw));
    try testing.expectEqual(expected.kind == .null, slot.isNull());
    try testing.expectEqual(expected.kind == .value, slot.isValue());
    try testing.expectEqual(expected.kind == .err, slot.isErr());
    try testing.expectEqual(expected.kind == .pointer, slot.isPointer());
}

fn buildCases() ![8]ExpectedCase {
    return .{
        .{
            .name = "null",
            .raw = 0,
            .kind = .null,
            .value = null,
            .error_code = null,
            .pointer = null,
            .tagged_internal = false,
        },
        .{
            .name = "inline_zero",
            .raw = try xa_value.makeValue(0),
            .kind = .value,
            .value = 0,
            .error_code = null,
            .pointer = null,
            .tagged_internal = true,
        },
        .{
            .name = "inline_limit",
            .raw = try xa_value.makeValue(xa_value.safe_inline_limit),
            .kind = .value,
            .value = xa_value.safe_inline_limit,
            .error_code = null,
            .pointer = null,
            .tagged_internal = true,
        },
        .{
            .name = "plain_pointer",
            .raw = 0x1000,
            .kind = .pointer,
            .value = null,
            .error_code = null,
            .pointer = 0x1000,
            .tagged_internal = false,
        },
        .{
            .name = "gap_before_err_floor",
            .raw = err_ptr.err_floor - 1,
            .kind = .pointer,
            .value = null,
            .error_code = null,
            .pointer = err_ptr.err_floor - 1,
            .tagged_internal = false,
        },
        .{
            .name = "err_floor",
            .raw = err_ptr.err_floor,
            .kind = .err,
            .value = null,
            .error_code = -4095,
            .pointer = null,
            .tagged_internal = true,
        },
        .{
            .name = "err_enomem",
            .raw = err_ptr.fromErrorCode(-12),
            .kind = .err,
            .value = null,
            .error_code = -12,
            .pointer = null,
            .tagged_internal = true,
        },
        .{
            .name = "err_top",
            .raw = err_ptr.fromErrorCode(-1),
            .kind = .err,
            .value = null,
            .error_code = -1,
            .pointer = null,
            .tagged_internal = true,
        },
    };
}

test "mixed xarray-slot sequence keeps lane ownership and decoders aligned" {
    const cases = try buildCases();

    for (cases) |expected| {
        try expectCase(expected);
    }
}

test "mixed sequence summary counts stay stable across null, value, pointer, and err lanes" {
    const cases = try buildCases();
    var null_count: usize = 0;
    var value_count: usize = 0;
    var pointer_count: usize = 0;
    var err_count: usize = 0;
    var tagged_internal_count: usize = 0;

    for (cases) |expected| {
        switch (expected.kind) {
            .null => null_count += 1,
            .value => value_count += 1,
            .pointer => pointer_count += 1,
            .err => err_count += 1,
        }
        if (expected.tagged_internal) {
            tagged_internal_count += 1;
        }
    }

    try testing.expectEqual(@as(usize, 1), null_count);
    try testing.expectEqual(@as(usize, 2), value_count);
    try testing.expectEqual(@as(usize, 2), pointer_count);
    try testing.expectEqual(@as(usize, 3), err_count);
    try testing.expectEqual(@as(usize, 5), tagged_internal_count);
}

test "mixed sequence preserves the seam ordering from tagged value to pointer gap to err_ptr" {
    const inline_limit_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const seam = [_]ExpectedCase{
        .{
            .name = "inline_limit",
            .raw = inline_limit_raw,
            .kind = .value,
            .value = xa_value.safe_inline_limit,
            .error_code = null,
            .pointer = null,
            .tagged_internal = true,
        },
        .{
            .name = "gap_before_err_floor",
            .raw = err_ptr.err_floor - 1,
            .kind = .pointer,
            .value = null,
            .error_code = null,
            .pointer = err_ptr.err_floor - 1,
            .tagged_internal = false,
        },
        .{
            .name = "err_floor",
            .raw = err_ptr.err_floor,
            .kind = .err,
            .value = null,
            .error_code = -4095,
            .pointer = null,
            .tagged_internal = true,
        },
    };

    for (seam) |expected| {
        try expectCase(expected);
    }

    try testing.expectEqual(err_ptr.err_floor - 2, inline_limit_raw);
}
