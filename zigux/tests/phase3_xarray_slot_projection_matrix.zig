const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const MatrixCase = struct {
    raw: usize,
    kind: xarray_slot_view.SlotKind,
    value: ?usize = null,
    code: ?isize = null,
    pointer: ?usize = null,
};

fn expectCase(case: MatrixCase) !void {
    const slot = xarray_slot_view.fromRaw(case.raw);

    try testing.expectEqual(case.kind, slot.kind());
    try testing.expectEqual(case.raw, slot.rawValue());
    try testing.expectEqual(case.value, slot.value());
    try testing.expectEqual(case.code, slot.errorCode());
    try testing.expectEqual(case.pointer, slot.pointerValue());

    switch (case.kind) {
        .null => {
            try testing.expect(slot.isNull());
            try testing.expect(!xarray_slot_view.isTaggedInternalEntry(case.raw));
        },
        .value => {
            try testing.expect(slot.isValue());
            try testing.expect(xarray_slot_view.isTaggedInternalEntry(case.raw));
            try testing.expectEqual(case.raw, try xa_value.makeValue(case.value.?));
        },
        .err => {
            try testing.expect(slot.isErr());
            try testing.expect(xarray_slot_view.isTaggedInternalEntry(case.raw));
            try testing.expectEqual(case.raw, err_ptr.fromErrorCode(case.code.?));
        },
        .pointer => {
            try testing.expect(slot.isPointer());
            try testing.expect(!xarray_slot_view.isTaggedInternalEntry(case.raw));
        },
    }
}

test "projection matrix holds across low cutoff and top raws" {
    const cases = [_]MatrixCase{
        .{ .raw = 0, .kind = .null },
        .{ .raw = 1, .kind = .value, .value = 0 },
        .{ .raw = 2, .kind = .pointer, .pointer = 2 },
        .{ .raw = 3, .kind = .value, .value = 1 },
        .{ .raw = err_ptr.err_floor - 3, .kind = .pointer, .pointer = err_ptr.err_floor - 3 },
        .{ .raw = err_ptr.err_floor - 2, .kind = .value, .value = xa_value.safe_inline_limit },
        .{ .raw = err_ptr.err_floor - 1, .kind = .pointer, .pointer = err_ptr.err_floor - 1 },
        .{ .raw = err_ptr.err_floor, .kind = .err, .code = -4095 },
        .{ .raw = err_ptr.err_floor + 1, .kind = .err, .code = -4094 },
        .{ .raw = err_ptr.fromErrorCode(-2), .kind = .err, .code = -2 },
        .{ .raw = err_ptr.fromErrorCode(-1), .kind = .err, .code = -1 },
    };

    for (cases) |case| {
        try expectCase(case);
    }
}

test "mid-value projection keeps value-pointer-value ordering" {
    const mid_value = xa_value.safe_inline_limit / 2;
    const lower_raw = try xa_value.makeValue(mid_value);
    const separator_raw = lower_raw + 1;
    const upper_raw = try xa_value.makeValue(mid_value + 1);

    try testing.expectEqual(lower_raw + 1, separator_raw);
    try testing.expectEqual(separator_raw + 1, upper_raw);
    try testing.expect(separator_raw < err_ptr.err_floor);

    try expectCase(.{ .raw = lower_raw, .kind = .value, .value = mid_value });
    try expectCase(.{ .raw = separator_raw, .kind = .pointer, .pointer = separator_raw });
    try expectCase(.{ .raw = upper_raw, .kind = .value, .value = mid_value + 1 });
}

test "mid-err projection keeps even and odd raws inside the err lane" {
    const even_raw = err_ptr.fromErrorCode(-2048);
    const odd_raw = err_ptr.fromErrorCode(-2047);

    try testing.expectEqual(even_raw + 1, odd_raw);
    try testing.expect((even_raw & xa_value.value_tag_mask) == 0);
    try testing.expect((odd_raw & xa_value.value_tag_mask) == xa_value.value_tag_mask);

    try expectCase(.{ .raw = even_raw, .kind = .err, .code = -2048 });
    try expectCase(.{ .raw = odd_raw, .kind = .err, .code = -2047 });

    const rejected_payload = odd_raw >> 1;
    try testing.expect(!xa_value.canRepresent(rejected_payload));
    try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(rejected_payload));
}
